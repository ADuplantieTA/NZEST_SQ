

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


def Energy_Demand_Grouped():
    

    st.markdown(
        """
        <style>
        .stApp { background-color: #fff; color: #222; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("NZEST Chart Generator – Grouped Energy Demand")

    # Load scenario and data
    scenario = st.sidebar.radio("Select Scenario", ["Status-Quo", "Net-Zero (beta)"])
    fallback = os.path.join(base_dir, 'SQ_Post_Process.csv') if scenario == 'Status-Quo' else os.path.join(base_dir, 'NZ_Post_Process.csv')
    if os.path.exists(fallback):
        df = load_csv(fallback)
    else:
        st.error(f"No CSV for {scenario}.")
        st.stop()
    if scenario.startswith("Net-Zero"):
        df = df[df['Sector'] != "-"]

    # Identify energy column and convert to GJ
    energy_col = next(c for c in df.columns if c.startswith('Energy'))
    base_unit = energy_col.split('(')[1].split('/')[0]
    df['Energy_GJ'] = df[energy_col] * ({'GJ': 1, 'PJ': 1e6}[base_unit])

    # Sidebar filters
    st.sidebar.header("Filters")
    provinces = sorted(df['Province'].dropna().unique())
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)
    min_y = int(pd.to_numeric(df['Year'], errors='coerce').min())
    max_y = int(pd.to_numeric(df['Year'], errors='coerce').max())
    selected_years = st.sidebar.slider("Select Year Range", min_y, max_y, (min_y, max_y))
    display_unit = st.sidebar.selectbox("Display unit", ["GJ", "TJ", "PJ"], index=["GJ", "TJ", "PJ"].index(base_unit))
    factor = {'GJ': 1, 'TJ': 1e-3, 'PJ': 1e-6}[display_unit]
    df['Energy_display'] = df['Energy_GJ'] * factor

    # Group sectors as requested
    mapping = {
        "Transport":   "Transport",
        "Residential": "Building",
        "Commercial":  "Building",
        "Industry":    "Industry",
        "Agriculture": "Industry"
    }
    df['Group'] = df['Sector'].map(mapping).fillna("Other")

    # Filter rows by selection
    if "All Canada" in selected_provinces:
        df_filtered = df[df['Year'].between(*selected_years)]
    else:
        df_filtered = df[
            df['Year'].between(*selected_years) &
            df['Province'].isin(selected_provinces)
        ]
    grouped = (
        df_filtered
        .groupby(['Year', 'Group'])['Energy_display']
        .sum()
        .reset_index()
    )
    grouped = grouped[grouped['Group'].isin(["Transport", "Building", "Industry"])]
    label_options = ["Transport", "Building", "Industry"]

    # --- All chart display options and label selector in a single expander ---
    with st.sidebar.expander("Chart display options", expanded=False):
        show_cutoff_line = st.checkbox("Show 2022 data/model cutoff", value=False)
        show_labels = st.checkbox("Show area labels on chart", value=True)
        show_legend = st.checkbox("Show legend", value=False)
        label_font_size = st.slider("Label font size", min_value=8, max_value=28, value=16)
        label_mode = st.radio(
            "Label mode",
            options=["Auto", "Manual"],
            index=0,
            help="Auto: show labels for large bands automatically. Manual: select which categories to show labels for."
        )
        if label_mode == "Manual":
            show_label_for = st.multiselect(
                "Show labels for groups", label_options, default=label_options
            )
        else:
            show_label_for = label_options
        tick_label_font_size = st.slider(
            "Axis tick label font size", min_value=8, max_value=28, value=12
        )
        show_data_table = st.checkbox("Show table of chart values below", value=False)

        # --- Color pickers for each group ---
        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)
        group_color_map = {}
        if show_trace_colors:
            st.markdown("**Pick a color for each group:**")
            for label in label_options:
                col = group_colors.get(label, "#CCCCCC")
                picked = st.color_picker(f"Trace color for {label}", col, key=f"grouped_color_{label}")
                group_color_map[label] = picked
        else:
            for label in label_options:
                group_color_map[label] = group_colors.get(label, "#CCCCCC")

        # --- Label text color pickers ---
        show_label_text_colors = st.checkbox("Select label text colors (black or white)", value=False)
        label_text_colors = {}
        if show_label_text_colors:
            st.markdown("**Pick black or white for each label's text:**")
            for label in label_options:
                txt_col = st.selectbox(
                    f"Text color for {label}",
                    options=["white", "black"],
                    index=0,
                    key=f"grouped_textcol_{label}"
                )
                label_text_colors[label] = txt_col
        else:
            for label in label_options:
                label_text_colors[label] = "white"

    # --- Area chart ---
    y_label = f"Energy demand ({display_unit}/yr)"
    import plotly.express as px
    # Define explicit group order
    
    fig = px.area(
        grouped,
        x='Year',
        y='Energy_display',
        color='Group',
        labels={'Energy_display': y_label, 'Year': 'Year', 'Group': 'Category'},
        title=f"{scenario} Energy Demand by Category",
        color_discrete_map=group_color_map,
        category_orders={'Group': group_order}
    )

    # Remove area border lines
    fig.for_each_trace(
        lambda trace: trace.update(fillcolor=trace.line.color, line=dict(width=0))
    )
    fig.update_layout(height=1080)
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
    fig.update_layout(
        title_x=0.5,
        title_xanchor='center',
        title_font=dict(size=tick_label_font_size),
        showlegend=show_legend
    )
    if show_cutoff_line:
        fig.add_vline(
            x=2022,
            line_dash="dot",
            line_color="black",
            line_width=2,
            annotation_text="   Historical → Model",
            annotation_position="top right",
            annotation_font_size=12
        )

    # Label logic (inside/outside/none)
    if show_labels:
        y_offset_abs  = 0.0
        offset_frac   = 0.2
        pixel_shift   = 0
        min_height_ratio = 0.02  # 2% of total height at target year

        # Choose a mid/future year to place label
        target_year = 2035 if 2035 in list(grouped['Year'].unique()) else grouped['Year'].max()
        x_vals = list(fig.data[0].x) if fig.data else []
        if target_year in x_vals:
            idx = x_vals.index(target_year)
        else:
            idx = len(x_vals) // 2 if x_vals else 0
        x_pos = x_vals[idx] if x_vals else None
        total_stack_height = sum(trace.y[idx] for trace in fig.data) if fig.data else 0
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
                    y_label_pos = y_mid
                    yanchor = "middle"
                    font_color = label_text_colors.get(trace.name, "white")
                else:
                    y_label_pos = y_top[idx] + 0.01 * total_stack_height
                    yanchor = "bottom"
                    font_color = "#666"
                window = 3
                start_year = x_vals[idx] - window if x_vals else None
                end_year = x_vals[idx] + window if x_vals else None
                try:
                    start_idx = x_vals.index(start_year)
                    end_idx = x_vals.index(end_year)
                    start_y = trace.y[start_idx]
                    end_y = trace.y[end_idx]
                    denom = (abs(start_y) + abs(end_y)) / 2
                    slope_ratio = (end_y - start_y) / denom if denom != 0 else 0
                except Exception:
                    slope_ratio = 0
                textangle = max(min(-slope_ratio * 12, 0), -12)
                if x_pos is not None:
                    fig.add_annotation(
                        x=x_pos,
                        y=y_label_pos,
                        text=trace.name,
                        showarrow=False,
                        xanchor="left",
                        yanchor=yanchor,
                        font=dict(size=label_font_size, color=font_color),
                        yshift=pixel_shift,
                        textangle=textangle
                    )
            stacked_y = y_top

    st.plotly_chart(fig, use_container_width=True)

    if show_data_table:
        st.subheader("Underlying values for chart")
        st.dataframe(grouped.pivot(index='Year', columns='Group', values='Energy_display').reset_index())
    csv_bytes = grouped.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download grouped energy data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_energy_grouped_{selected_years[0]}_{selected_years[1]}_{display_unit}.csv",
        mime="text/csv"
    )