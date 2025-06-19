

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
ghg_data_path = os.path.join(base_dir, "GHG_Data.csv")

def GHG_Graph():
    st.markdown(
        """
        <style>
        .stApp { background-color: #fff; color: #222; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("NZEST Chart Generator")
    Path = ghg_data_path
    df_ghg = pd.read_csv(Path)
    df_ghg = df_ghg.melt(id_vars=['Sector', 'Sub-Sector', 'Use', 'Province']
                            ,value_vars=([str(year) for year in range(1990,2024)])
                            ,var_name= 'year'
                            ,value_name="GHG")
    # Ensure GHG values are numeric
    df_ghg['GHG'] = pd.to_numeric(df_ghg['GHG'], errors='coerce')
    
    # Sidebar filters
    st.sidebar.header("Filters")
    # Year range slider
    min_year = int(df_ghg['year'].min())
    max_year = int(df_ghg['year'].max())
    selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))
   
    # Province filter
    provinces = sorted(df_ghg['Province'].dropna().unique())
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)

    # Unit selector
    unit_map = {"MtCO₂e": "MtCO₂e", "GtCO₂e": "GtCO₂e"}
    unit_sel = st.sidebar.selectbox("Display unit", list(unit_map.keys()))
    # Grouping selector
    
    group_map = {"Sector": "Sector", "Sub-Sector": "Sub-Sector", "Use": "Use"}
    sel_label = st.sidebar.selectbox("Group by", list(group_map.keys()))
    dim_col = group_map[sel_label]

    # Chart display options in a single expander
    with st.sidebar.expander("Chart display options", expanded=False):
        show_labels = st.checkbox("Show area/bar labels on chart", value=True)
        show_legend = st.checkbox("Show legend", value=False)
        label_font_size = st.slider("Label font size", min_value=8, max_value=28, value=16)
        # Label mode and selector logic
        label_options = sorted(df_ghg[dim_col].dropna().unique())
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
            "Axis tick label font size", min_value=8, max_value=28, value=12
        )
        show_data_table = st.checkbox("Show table of chart values below", value=False)

        # --- BEGIN: Per-label color logic ---
        # Default color mapping for GHG categories (populate this dictionary as needed)
        label_colors_default = {
             "Buildings": "#9C1414",
             "Agric": "#aeaeae",
             "Energy Sector":"#18506B",
             "Ind Processes":"#747474",
             "Non Energy Ind": "#C56060",
             "Transport":"#ECC10B",
             "Waste": "#d1d1d1",
             "End use Combustion of Energy Carriers":"#225f99",
             "Production of Energy Carriers":"#c00000",
             "Non-Energy Emissions":"#78206e",
             "Electricity":"#FFBF00",
             "Oil and Gas":"#c00000",
                "Commercial": "#6C1D1D",
                "Residential": "#a64d79",
                "Air": "#167a0a",
                "Road": "#7ee183",
                "Off Road": "#1dce39",
                "Rail": "#219a2c",
                "Marine": "#20842e"
           
        }

        label_options = sorted(df_ghg[dim_col].dropna().unique())

        # --- Trace (fill) colors toggle ---
        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)
        label_colors = {}
        if show_trace_colors and label_options:
            st.markdown("**Pick a color for each label's area/trace:**")
            for label in label_options:
                col = label_colors_default.get(label, "#CCCCCC")
                picked = st.color_picker(f"Trace color for {label}", col, key=f"ghg_color_{sel_label}_{label}")
                label_colors[label] = picked
        elif label_options:
            for label in label_options:
                label_colors[label] = label_colors_default.get(label, "#CCCCCC")

        # --- Label text colors toggle ---
        show_label_text_colors = st.checkbox("Select label text colors (black or white)", value=False)
        label_text_colors = {}
        if show_label_text_colors and label_options:
            st.markdown("**Pick black or white for each label's text:**")
            for label in label_options:
                txt_col = st.selectbox(
                    f"Text color for {label}",
                    options=["white", "black"],
                    index=0,
                    key=f"ghg_textcol_{sel_label}_{label}"
                )
                label_text_colors[label] = txt_col
        elif label_options:
            for label in label_options:
                label_text_colors[label] = "white"
        # --- END: Per-label color logic ---

    # Dimension filter based on grouping
    dim_options = sorted(df_ghg[dim_col].dropna().unique())

    # Filter dataframe
    if "All Canada" in selected_provinces:
        # Ignore province filtering, aggregate across all provinces
        df_filtered = df_ghg[
            df_ghg['year'].astype(int).between(selected_years[0], selected_years[1])
        ]
    else:
        df_filtered = df_ghg[
            df_ghg['Province'].isin(selected_provinces) &
            df_ghg['year'].astype(int).between(selected_years[0], selected_years[1])
        ]
    # Aggregate
    grouped = df_filtered.groupby(['year', dim_col])['GHG'].sum().reset_index()
    grouped['year'] = grouped['year'].astype(int)

    # Convert from kilotonnes (kt) to Mt or Gt as selected
    # Data is in kilotonnes: 1 Mt = 1,000 kt; 1 Gt = 1,000,000 kt
    factor = {"MtCO₂e": 1e-3, "GtCO₂e": 1e-6}[unit_sel]
    grouped['GHG'] = grouped['GHG'] * factor

    # Plot
    y_label = f"GHG Emissions ({unit_sel}/yr)"
    fig = px.area(
        grouped,
        x='year',
        y='GHG',
        color=dim_col,
        labels={'GHG': y_label, 'year': 'Year', dim_col: sel_label},
        title=f"GHG Emissions by {sel_label}",
        color_discrete_map=label_colors,
    )
    # Apply styling similar to Energy Demand
    fig.for_each_trace(lambda trace: trace.update(fillcolor=trace.line.color, line=dict(width=0)))
    fig.update_layout(
        height=1080,
        title_x=0.5,
        title_xanchor='center',
        title_font=dict(size=tick_label_font_size),
        margin=dict(r=50),
    )
    fig.update_xaxes(
        tickmode='auto',
        showline=True,
        linewidth=2,
        linecolor='black',
        ticks='outside',
        ticklen=10,
        tickwidth=2,
        tickcolor='black',
        minor=dict(dtick=1, ticklen=5, tickwidth=2, tickcolor='black', showgrid=False),
        mirror=True,  # only left and bottom axes have ticks/lines
        tickfont=dict(size=tick_label_font_size),
        title_font=dict(size=tick_label_font_size)
    )
    fig.update_yaxes(
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
        minor=dict(ticklen=5, tickwidth=2, tickcolor='black', showgrid=True),
        minor_gridcolor='lightgrey',
        minor_gridwidth=0.5,
        mirror=True,  # only left and bottom axes have ticks/lines
        tickfont=dict(size=tick_label_font_size),
        title_font=dict(size=tick_label_font_size)
    )

    # Set legend visibility based on sidebar
    fig.update_layout(showlegend=show_legend)

    # Optional: Area label annotations
    if show_labels:
        y_offset_abs  = 0.0
        offset_frac   = 0.2
        pixel_shift   = 0
        min_height_ratio = 0.07  # 7% threshold

        # 3) Identify the x-position to place the label at the midpoint of the visible years
        if not fig.data:
            st.warning("No data available for the current selection.")
            return
        x_vals = list(fig.data[0].x)
        if not x_vals:
            st.warning("No x-values available for plotting.")
            return
        mid_idx = len(x_vals) // 2  # lower mid for even length, standard
        idx = mid_idx
        x_pos = x_vals[idx]

        # 4) Compute total stack height at target year
        total_stack_height = sum(trace.y[idx] for trace in fig.data)

        # 5) Loop through traces and annotate
        stacked_y = [0.0] * len(x_vals)

        auto_show = label_mode == "Auto"
        manual_show = label_mode == "Manual"
        for trace in fig.data:
            y_top = [a + b for a, b in zip(stacked_y, trace.y)]
            band_height = trace.y[idx]
            band_ratio = band_height / total_stack_height if total_stack_height != 0 else 0

            if (
                (auto_show and band_ratio >= min_height_ratio)
                or (manual_show and trace.name in show_label_for)
            ):
                if band_ratio >= min_height_ratio:
                    # Label inside the band (centered, color from label_text_colors)
                    y_mid = (stacked_y[idx] + y_top[idx]) / 2 + y_offset_abs + offset_frac * band_height
                    y_label = y_mid
                    yanchor = "middle"
                    font_color = label_text_colors.get(trace.name, "white")
                else:
                    # Label above the band (grey)
                    y_label = y_top[idx] + 0.01 * total_stack_height  # 1% of stack as gap
                    yanchor = "bottom"
                    font_color = "#666"

                # Slope/angle logic (unchanged)
                window = 3
                start_year = x_vals[idx] - window
                end_year = x_vals[idx] + window
                try:
                    start_idx = x_vals.index(start_year)
                    end_idx = x_vals.index(end_year)
                    start_y = trace.y[start_idx]
                    end_y = trace.y[end_idx]
                    denom = (abs(start_y) + abs(end_y)) / 2
                    slope_ratio = (end_y - start_y) / denom if denom != 0 else 0
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

    # Render plot and download
    st.plotly_chart(fig, use_container_width=True)
    if show_data_table:
        st.subheader("Underlying values for chart")
        st.dataframe(grouped)
    csv_bytes = grouped.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download GHG data as CSV",
        data=csv_bytes,
        file_name=f"GHG_Emissions_{sel_label}_{unit_sel}_{selected_years[0]}_{selected_years[1]}.csv",
        mime="text/csv"
    )