import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from load_csv import load_csv
import os
from collections import defaultdict
from nzest_constants import (
    sector_activity_dict,
    carrier_dict,
    carrier_colors,
    sector_activity_colors,
    carrier_tech_colors,
    group_colors,
    stack_order,
)

# Define base directory for input CSV files, relative to this script's location
base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Input")

def Energy_Demand():
    # Apply basic styling to the Streamlit app (background and text color)
    st.markdown(
        """
        <style>
        .stApp { background-color: #fff; color: #222; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("NZEST Chart Generator")

    # Sidebar: Scenario selection radio buttons (no file uploader)
    scenario = st.sidebar.radio("Select Scenario", ["Status-Quo", "Net-Zero (beta)"])

    # Determine fallback CSV path based on selected scenario
    fallback = os.path.join(base_dir, 'SQ_Post_Process.csv') if scenario == 'Status-Quo' else os.path.join(base_dir, 'NZ_Post_Process.csv')

    # Load CSV if it exists; otherwise, show error and stop execution
    if os.path.exists(fallback):
        df = load_csv(fallback)
    else:
        st.error(f"No CSV for {scenario}.")
        st.stop()

    # For Net-Zero scenario, filter out placeholder sector entries ("-")
    if scenario.startswith("Net-Zero"):
        df = df[df['Sector'] != "-"]

    # Identify the energy data column and extract its base unit (e.g., GJ, TJ, PJ)
    energy_col = next(c for c in df.columns if c.startswith('Energy'))
    base_unit = energy_col.split('(')[1].split('/')[0]

    # Sidebar: Filters for sectors, provinces, and years
    st.sidebar.header("Filters")

    # List of unique sectors sorted alphabetically
    sectors = sorted(df['Sector'].dropna().unique())
    selected_sectors = st.sidebar.multiselect("Select Sectors", sectors, default=sectors)

    # List of unique provinces sorted alphabetically
    provinces = sorted(df['Province'].dropna().unique())

    # Add "All Canada" option at the top for province selection
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)

    # Determine min and max years available in data for slider range
    min_y = int(pd.to_numeric(df['Year'], errors='coerce').min())
    max_y = int(pd.to_numeric(df['Year'], errors='coerce').max())
    selected_years = st.sidebar.slider("Select Year Range", min_y, max_y, (min_y, max_y))

    # Sidebar: Grouping options for charting
    group_map = {
        "Carrier": "Carrier",
        "Carrier & Tech": "Tech_name",
        "Sub Sector": "Tech_subsector"
    }
    sel_label = st.sidebar.selectbox("Group by", list(group_map.keys()))
    dim_col = group_map[sel_label]

    # Sidebar: Unit display options with default set to base unit from data
    display_unit = st.sidebar.selectbox("Display unit", ["GJ","TJ","PJ"], index=["GJ","TJ","PJ"].index(base_unit))

    # Convert energy data to GJ for uniformity, then apply factor to convert to display unit
    df['Energy_GJ'] = df[energy_col] * ({'GJ':1,'PJ':1e6}[base_unit])
    factor = {'GJ':1,'TJ':1e-3,'PJ':1e-6}[display_unit]
    df['Energy_display'] = df['Energy_GJ'] * factor

    # Filter data based on selected sectors, provinces, and years
    # If "All Canada" selected, aggregate across all provinces
    if "All Canada" in selected_provinces:
        df_filtered = df[
            df['Sector'].isin(selected_sectors) &
            df['Year'].between(*selected_years)
        ]
    else:
        df_filtered = df[
            df['Sector'].isin(selected_sectors) &
            df['Province'].isin(selected_provinces) &
            df['Year'].between(*selected_years)
        ]

    # Group filtered data by year and selected dimension, summing energy values
    grouped = df_filtered.groupby(['Year', dim_col])['Energy_display'].sum().reset_index()

    # Extract sorted unique labels for the current grouping dimension
    label_options = sorted(grouped[dim_col].unique())

    # Sidebar: Chart display options inside an expander for better UI organization
    with st.sidebar.expander("Chart display options", expanded=False):
        # Option to show a vertical line marking 2022 cutoff between historical and model data
        show_cutoff_line = st.checkbox("Show 2022 data/model cutoff", value=False)

        # Toggle to show area/bar labels directly on the chart
        show_labels = st.checkbox("Show area/bar labels on chart", value=True)

        # Toggle to show or hide the legend on the chart
        show_legend = st.checkbox("Show legend", value=False)

        # Slider to adjust font size of labels on the chart
        label_font_size = st.slider("Label font size", min_value=16, max_value=34, value=24)

        # Label mode: Auto shows labels for large bands automatically, Manual allows selection
        label_mode = st.radio(
            "Label mode",
            options=["Auto", "Manual"],
            index=0,
            help="Auto: show labels for large bands automatically. Manual: select which categories to show labels for."
        )

        # If manual mode, allow user to pick which labels to show on the chart
        if label_mode == "Manual":
            show_label_for = st.multiselect(
                f"Show labels for {sel_label}s", label_options, default=label_options
            )
        else:
            show_label_for = label_options

        # Slider to adjust font size for axis tick labels
        tick_label_font_size = st.slider(
            "Axis tick label font size", min_value=16, max_value=34, value=24
        )

        # Option to show the underlying data table below the chart
        show_data_table = st.checkbox("Show table of chart values below", value=False)

        # --- Begin per-label color customization logic ---
        # Select default color mapping based on grouping selection
        if sel_label == "Carrier & Tech":
            default_map = carrier_tech_colors
        elif sel_label == "Sub Sector":
            default_map = sector_activity_colors
        elif sel_label == "Carrier":
            default_map = carrier_colors
        else:
            default_map = {}

        # Checkbox to enable manual selection of trace (fill) colors
        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)

        # Dictionary to hold final colors for each label
        label_colors = {}

        if show_trace_colors:
            st.markdown("**Pick a color for each label's area/trace:**")
            for label in label_options:
                # Use default color if available, else fallback to gray
                col = default_map.get(label, None)
                picked = st.color_picker(f"Trace color for {label}", col if col is not None else "#CCCCCC", key=f"color_{sel_label}_{label}")
                label_colors[label] = picked
        else:
            # Assign default colors where available; otherwise, leave unassigned for Plotly defaults
            for label in label_options:
                c = default_map.get(label, None)
                if c is not None:
                    label_colors[label] = c

        # --- Label text color customization ---
        # Checkbox to enable selection of label text colors (black or white)
        show_label_text_colors = st.checkbox("Select label text colors (black or white)", value=False)

        # Dictionary to hold text colors for each label
        label_text_colors = {}

        if show_label_text_colors:
            st.markdown("**Pick black or white for each label's text:**")
            for label in label_options:
                # Dropdown to select text color per label, defaulting to white
                txt_col = st.selectbox(
                    f"Text color for {label}",
                    options=["white", "black"],
                    index=0,
                    key=f"textcol_{sel_label}_{label}"
                )
                label_text_colors[label] = txt_col
        else:
            # Default all label text colors to white
            for label in label_options:
                label_text_colors[label] = "white"
        # --- End per-label color customization ---

    # Prepare y-axis label text including the selected display unit per year
    y_label = f"Energy demand ({display_unit}/yr)"

    # Create an area chart using Plotly Express with the grouped data
    fig = px.area(
        grouped, x='Year', y='Energy_display', color=dim_col,
        labels={'Energy_display': y_label, 'Year':'Year', dim_col:sel_label},
        title=f"{scenario} {y_label} by {sel_label}",
        category_orders={dim_col: stack_order},
        color_discrete_map=label_colors,
    )
    
    # Remove border lines and ensure each area is filled with its trace color
    fig.for_each_trace(
        lambda trace: trace.update(
            fillcolor=trace.line.color,
            line=dict(width=0)
        )
    )
    # Set figure height for better visibility
    fig.update_layout(height=1080)

    # Configure x-axis properties: linear ticks every 5 years with minor ticks every year
    fig.update_xaxes(
        tickmode='linear',
        dtick=5,
        showline=True,
        linewidth=2,
        linecolor='black',
        ticks='outside',
        ticklen=10,
        tickwidth=2,
        tickcolor='black',
        minor=dict(
            dtick=1,
            ticklen=5,
            tickwidth=2,
            tickcolor='black',
            showgrid=False
        ),
        mirror=True,
        tickfont=dict(size=tick_label_font_size),
        title_font=dict(size=tick_label_font_size)
    )

    # Configure y-axis properties: automatic ticks, grid lines, and styling
    fig.update_yaxes(
        tickmode='auto',
        showline=True,
        showgrid=True,
        gridcolor='lightgrey',
        gridwidth=1,
        linewidth=2,
        linecolor='black',
        ticks='outside',
        ticklen=10,
        tickwidth=2,
        tickcolor='black',
        minor=dict(
            ticklen=5,
            tickwidth=2,
            tickcolor='black',
            showgrid=True
        ),
        minor_gridcolor='lightgrey',
        minor_gridwidth=0.5,
        mirror=True,
        tickfont=dict(size=tick_label_font_size),
        title_font=dict(size=tick_label_font_size)
    )

    # Center the chart title and set its font size to match axis ticks
    fig.update_layout(
        title_x=0.5,
        title_xanchor='center',
        title_font=dict(size=tick_label_font_size)
    )

    # Set legend visibility based on sidebar checkbox
    fig.update_layout(showlegend=show_legend)

    # If enabled, add a vertical dashed line at year 2022 to indicate data/model cutoff
    if show_cutoff_line:
        fig.add_vline(
            x=2022,
            line_dash="dash",
            line_color="black",
            line_width=2,
            annotation_text="",
            annotation_position="top right",
            annotation_font_size=12
        )

    # Only add area/bar labels if user selected to show them
    if show_labels:
        # Define constants for label positioning and size threshold
        y_offset_abs  = 0.0         # Absolute vertical offset for labels
        offset_frac   = 0.2         # Fractional offset within band height for label position
        pixel_shift   = 0           # Pixel shift for label positioning
        min_height_ratio = 0.02     # Minimum relative band height (2%) to show label

        # Target year on x-axis to place labels (e.g., 2035)
        target_year = 2035

        # If no data traces exist, warn user and exit function early
        if not fig.data:
            st.warning("No data available for the current selection.")
            return

        # Extract x-axis values from first trace (all traces share same x)
        x_vals = list(fig.data[0].x)

        # Find index of target year; if not found, default to middle index
        idx = x_vals.index(target_year) if target_year in x_vals else len(x_vals) // 2
        x_pos = x_vals[idx]

        # Calculate total stacked height at target year across all traces
        total_stack_height = sum(trace.y[idx] for trace in fig.data)

        # Initialize list to keep track of cumulative stacked y-values for label positioning
        stacked_y = [0.0] * len(x_vals)

        # Determine label display mode: automatic or manual
        auto_show = label_mode == "Auto"
        manual_show = label_mode == "Manual"

        # Loop through each data trace to decide if label should be shown and add annotation
        for trace in fig.data:
            # Calculate top y-values of current band by adding current trace y to stacked_y
            y_top = [a + b for a, b in zip(stacked_y, trace.y)]

            # Height of current band at target year
            band_height = trace.y[idx]

            # Check if label should be shown based on mode and band height
            if (
                (auto_show and band_height / total_stack_height >= min_height_ratio)
                or (manual_show and trace.name in show_label_for)
            ):
                if band_height / total_stack_height >= min_height_ratio:
                    # Position label vertically near middle of band with some offset
                    y_mid = (stacked_y[idx] + y_top[idx]) / 2 + y_offset_abs + offset_frac * band_height
                    y_label = y_mid
                    yanchor = "middle"
                    font_color = label_text_colors.get(trace.name, "white")
                else:
                    # For smaller bands, position label just above top with smaller font color
                    y_label = y_top[idx] + 0.01 * total_stack_height  # 1% gap above band
                    yanchor = "bottom"
                    font_color = "#666"

                # Calculate slope of band at target year for label text angle
                window = 3  # years on each side of target for slope calculation
                start_year = target_year - window
                end_year = target_year + window
                try:
                    start_idx = x_vals.index(start_year)
                    end_idx = x_vals.index(end_year)
                    start_y = trace.y[start_idx]
                    end_y = trace.y[end_idx]
                    denom = (abs(start_y) + abs(end_y)) / 2
                    if denom != 0:
                        slope_ratio = (end_y - start_y) / denom
                    else:
                        slope_ratio = 0
                except ValueError:
                    # If start or end year not found, default slope to zero
                    slope_ratio = 0

                # Limit text angle between -12 and 0 degrees, inverse proportional to slope
                textangle = max(min(-slope_ratio * 12, 0), -12)

                # Add annotation (label) to figure at calculated position and angle
                fig.add_annotation(
                    x=x_pos,
                    y=y_label,
                    text=trace.name,
                    showarrow=False,
                    xanchor="left",
                    yanchor=yanchor,
                    font=dict(size=label_font_size, color=font_color),
                    yshift=pixel_shift,
                    textangle=textangle
                )

            # Update stacked_y to include current trace's values for next iteration
            stacked_y = y_top

    # Render the Plotly figure within the Streamlit app
    st.plotly_chart(fig, use_container_width=True)

    # If user opted to show data table, display the grouped data below the chart
    if 'show_data_table' in locals() and show_data_table:
        st.subheader("Underlying values for chart")
        st.dataframe(grouped)

    # Provide a download button in the sidebar to export chart data as CSV
    csv_bytes = grouped.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download chart data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_data_{display_unit}.csv",
        mime="text/csv"
    )
