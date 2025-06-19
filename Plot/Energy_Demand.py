

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
    category_mapping,
    PAGES,
    fossil_carriers,
    group_order,
)
base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Input")

def Energy_Demand():
    st.markdown(
        """
        <style>
        .stApp { background-color: #fff; color: #222; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("NZEST Chart Generator")

    # Scenario toggle (no uploader)
    scenario = st.sidebar.radio("Select Scenario", ["Status-Quo", "Net-Zero (beta)"])
    fallback = os.path.join(base_dir, 'SQ_Post_Process.csv') if scenario == 'Status-Quo' else os.path.join(base_dir, 'NZ_Post_Process.csv')
    if os.path.exists(fallback):
        df = load_csv(fallback)
    else:
        st.error(f"No CSV for {scenario}.")
        st.stop()
    # Filter out placeholder sector "-" for Net-Zero
    if scenario.startswith("Net-Zero"):
        df = df[df['Sector'] != "-"]

    # Identify energy column and base unit
    energy_col = next(c for c in df.columns if c.startswith('Energy'))
    base_unit = energy_col.split('(')[1].split('/')[0]

    # Sidebar filters
    st.sidebar.header("Filters")
    sectors = sorted(df['Sector'].dropna().unique())
    selected_sectors = st.sidebar.multiselect("Select Sectors", sectors, default=sectors)
    provinces = sorted(df['Province'].dropna().unique())
    # Insert "All Canada" at the top of the provinces list
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)
    min_y = int(pd.to_numeric(df['Year'], errors='coerce').min())
    max_y = int(pd.to_numeric(df['Year'], errors='coerce').max())
    selected_years = st.sidebar.slider("Select Year Range", min_y, max_y, (min_y, max_y))

    # Group-by and unit toggle
    group_map = {
        "Carrier": "Carrier",
        "Carrier & Tech": "Tech_name",
        "Sub Sector": "Tech_subsector"
    }
    sel_label = st.sidebar.selectbox("Group by", list(group_map.keys()))
    dim_col = group_map[sel_label]
    display_unit = st.sidebar.selectbox("Display unit", ["GJ","TJ","PJ"], index=["GJ","TJ","PJ"].index(base_unit))


    # Convert to GJ and apply factor
    df['Energy_GJ'] = df[energy_col] * ({'GJ':1,'PJ':1e6}[base_unit])
    factor = {'GJ':1,'TJ':1e-3,'PJ':1e-6}[display_unit]
    df['Energy_display'] = df['Energy_GJ'] * factor

    # Filter & group, with "All Canada" option
    if "All Canada" in selected_provinces:
        # Ignore specific province filters and aggregate across all provinces
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
    grouped = df_filtered.groupby(['Year', dim_col])['Energy_display'].sum().reset_index()

    # Get label options for the current grouping
    label_options = sorted(grouped[dim_col].unique())

    # Chart display options in a single expander (now after grouping and label_options)
    with st.sidebar.expander("Chart display options", expanded=False):
        show_cutoff_line = st.checkbox("Show 2022 data/model cutoff", value=False)
        show_labels = st.checkbox("Show area/bar labels on chart", value=True)
        show_legend = st.checkbox("Show legend", value=False)
        label_font_size = st.slider("Label font size", min_value=16, max_value=34, value=24)
        label_mode = st.radio(
            "Label mode",
            options=["Auto", "Manual"],
            index=0,
            help="Auto: show labels for large bands automatically. Manual: select which categories to show labels for."
        )
        if label_mode == "Manual":
            show_label_for = st.multiselect(
                f"Show labels for {sel_label}s", label_options, default=label_options
            )
        else:
            show_label_for = label_options
        tick_label_font_size = st.slider(
            "Axis tick label font size", min_value=16, max_value=34, value=24
        )
        show_data_table = st.checkbox("Show table of chart values below", value=False)

        # --- BEGIN: New per-label color logic ---
        # Set default_map based on sel_label
        if sel_label == "Carrier & Tech":
            default_map = carrier_tech_colors
        elif sel_label == "Sub Sector":
            default_map = sector_activity_colors
        elif sel_label == "Carrier":
            default_map = carrier_colors
        else:
            default_map = {}

        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)
        label_colors = {}
        if show_trace_colors:
            st.markdown("**Pick a color for each label's area/trace:**")
            for label in label_options:
                col = default_map.get(label, None)
                picked = st.color_picker(f"Trace color for {label}", col if col is not None else "#CCCCCC", key=f"color_{sel_label}_{label}")
                label_colors[label] = picked
        else:
            for label in label_options:
                c = default_map.get(label, None)
                if c is not None:
                    label_colors[label] = c
                # If not in map, do not assign. Let Plotly use default color.

        # --- Label text colors toggle ---
        show_label_text_colors = st.checkbox("Select label text colors (black or white)", value=False)
        label_text_colors = {}
        if show_label_text_colors:
            st.markdown("**Pick black or white for each label's text:**")
            for label in label_options:
                txt_col = st.selectbox(
                    f"Text color for {label}",
                    options=["white", "black"],
                    index=0,
                    key=f"textcol_{sel_label}_{label}"
                )
                label_text_colors[label] = txt_col
        else:
            for label in label_options:
                label_text_colors[label] = "white"
        # --- END: New per-label color logic ---

    # Plot
    y_label = f"Energy demand ({display_unit}/yr)"
    fig = px.area(
        grouped, x='Year', y='Energy_display', color=dim_col,
        labels={'Energy_display': y_label, 'Year':'Year', dim_col:sel_label},
        title=f"{scenario} {y_label} by {sel_label}",
        category_orders={dim_col: stack_order},
        color_discrete_map=label_colors,
    )
    
    # Ensure each area has its fill color without border lines
    fig.for_each_trace(
        lambda trace: trace.update(
            fillcolor=trace.line.color,
            line=dict(width=0)
        )
    )
    fig.update_layout(height=1080)
    # Configure major and minor ticks on axes
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

    # Center title and set font size to match tick_label_font_size
    fig.update_layout(
        title_x=0.5,
        title_xanchor='center',
        title_font=dict(size=tick_label_font_size)
    )

    # Set legend visibility based on sidebar (after creating figure, before plotting)
    fig.update_layout(showlegend=show_legend)

    # Toggle to show historical/model cutoff
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

    # Only run area label annotation code block if show_labels is True
    if show_labels:
        y_offset_abs  = 0.0
        offset_frac   = 0.2
        pixel_shift   = 0
        min_height_ratio = 0.02  # 2% of total height at target year

        # 3) Identify the x-position to place the label
        target_year = 2035
        if not fig.data:
            st.warning("No data available for the current selection.")
            return
        x_vals = list(fig.data[0].x)
        idx = x_vals.index(target_year) if target_year in x_vals else len(x_vals) // 2
        x_pos = x_vals[idx]

        # 4) Compute total stack height at target year
        total_stack_height = sum(trace.y[idx] for trace in fig.data)

        # 5) Loop through traces and annotate if big enough
        stacked_y = [0.0] * len(x_vals)

        auto_show = label_mode == "Auto"
        manual_show = label_mode == "Manual"
        for trace in fig.data:
            y_top = [a + b for a, b in zip(stacked_y, trace.y)]
            band_height = trace.y[idx]
            if (
                (auto_show and band_height / total_stack_height >= min_height_ratio)
                or (manual_show and trace.name in show_label_for)
            ):
                if band_height / total_stack_height >= min_height_ratio:
                    y_mid = (stacked_y[idx] + y_top[idx]) / 2 + y_offset_abs + offset_frac * band_height
                    y_label = y_mid
                    yanchor = "middle"
                    font_color = label_text_colors.get(trace.name, "white")
                else:
                    y_label = y_top[idx] + 0.01 * total_stack_height  # 1% of stack as gap
                    yanchor = "bottom"
                    font_color = "#666"
                window = 3  # years on each side of target
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
                    slope_ratio = 0
                textangle = max(min(-slope_ratio * 12, 0), -12)
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
            stacked_y = y_top

    # Only render the chart once, at the end
    st.plotly_chart(fig, use_container_width=True)

    # Show data table if selected
    if 'show_data_table' in locals() and show_data_table:
        st.subheader("Underlying values for chart")
        st.dataframe(grouped)

    # Download button
    csv_bytes = grouped.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download chart data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_data_{display_unit}.csv",
        mime="text/csv"
    )
