

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







def Pie_Generator(Sector, num_rings=3):
    # (Chart display options expander removed; always show labels and legend)
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
    provinces = sorted(df['Province'].dropna().unique())
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)
    years = sorted(pd.to_numeric(df['Year'], errors='coerce').dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", years)

    display_unit = st.sidebar.selectbox("Display unit", ["GJ","TJ","PJ"], index=["GJ","TJ","PJ"].index(base_unit))

    # Chart display options in a single expander (controls depend on label_mode)
    with st.sidebar.expander("Chart display options", expanded=False):
        label_mode = st.radio(
            "Label display mode",
            options=["Auto", "Manual"],
            index=0,
            help="Auto: show label inside slice if it fits; Manual: control label size, abbreviation, and other options"
        )
        if label_mode == "Auto":
            show_labels = st.checkbox("Show pie labels in chart", value=True)
            show_percent = st.checkbox("Show values as percent of total", value=False)
            min_pct_to_show_label = st.slider(
                "Show labels for slices ≥ this % of pie", min_value=0, max_value=20, value=3, step=1
            )
            auto_label_font_size = st.slider("Label font size", min_value=8, max_value=28, value=16)
            # In Auto mode, all other options are hidden
        else:
            label_font_size = st.slider("Label font size", min_value=8, max_value=28, value=16)
            show_labels = st.checkbox("Show pie labels in chart", value=True)
            show_percent = st.checkbox("Show values as percent of total", value=False)
            manual_min_pct_to_show_label = st.slider(
                "Show labels for slices ≥ this % of pie", min_value=0, max_value=20, value=0, step=1
            )
            adaptive_abbreviate = st.checkbox("Abbreviate labels with ellipsis if too long", value=False)
            max_label_length = st.slider("Max label length (chars, ellipsis after)", min_value=4, max_value=20, value=8)
            # Removed collapse_small and other_threshold controls
            label_orientation = st.selectbox(
                "Label orientation",
                options=["auto", "horizontal", "radial", "tangential"],
                index=0
            )
            show_data_table = st.checkbox("Show table of chart values below", value=False)

    # Convert to GJ and apply factor
    df['Energy_GJ'] = df[energy_col] * ({'GJ':1,'PJ':1e6}[base_unit])
    factor = {'GJ':1,'TJ':1e-3,'PJ':1e-6}[display_unit]
    df['Energy_display'] = df['Energy_GJ'] * factor

    if Sector == "All":
        if "All Canada" in selected_provinces:
            # Aggregate across all provinces, ignore province filter
            df_filtered = df[
                (df['Year'] == selected_year)
            ]
        else:
            df_filtered = df[
                df['Province'].isin(selected_provinces) &
                (df['Year'] == selected_year)
            ]
    else:
        if "All Canada" in selected_provinces:
            df_filtered = df[
                (df['Sector'].str.contains(Sector, case=False, na=False)) &
                (df['Year'] == selected_year)
            ]
        else:
            df_filtered = df[
                (df['Sector'].str.contains(Sector, case=False, na=False)) &
                df['Province'].isin(selected_provinces) &
                (df['Year'] == selected_year)
            ]

    # Group for sunburst: aggregate over the selected time range
    df_grouped_donut = df_filtered.groupby(['Tech_subsector', 'Carrier', 'Tech_name'])['Energy_display'].sum().reset_index()

    # --- Determine color_discrete_map for px.sunburst based on outermost ring ---
    # The sunburst path is set by path = base_path[:num_rings], so outermost is path[-1]
    def get_sunburst_color_map(path):
        """Return the appropriate color_discrete_map for px.sunburst given the path."""
        if not path:
            return {}
        outer = path[-1]
        if outer == 'Carrier':
            return carrier_colors
        elif outer == 'Tech_name':
            return carrier_tech_colors
        elif outer == 'Tech_subsector' or outer == 'Tech_subsector_display':
            return sector_activity_colors
        else:
            return {}

    # --- New: Pie label/legend logic depending on label_mode ---
    if label_mode == "Auto":
        # Compute slice percentage and determine labels (do not filter out small slices)
        df_grouped_donut['pct'] = df_grouped_donut['Energy_display'] / df_grouped_donut['Energy_display'].sum() * 100
        sunburst_label_col = 'Tech_subsector'
        base_path = [sunburst_label_col, 'Carrier', 'Tech_name']
        path = base_path[:num_rings]
        color_map = get_sunburst_color_map(path)
        fig_donut = px.sunburst(
            df_grouped_donut,
            path=path,
            values='Energy_display',
            color=path[-1],  # color by outermost ring
            color_discrete_map=color_map,
            title=f"{scenario} Transport Energy breakdown ({display_unit})",
        )
        fig_donut.update_layout(
            height=1080,
            title_x=0.5,
            title_xanchor='center',
            showlegend=True,
            uniformtext=dict(mode='show', minsize=1)
        )
        # --- Begin: Per-slice label display logic for sunburst ---
        for trace in fig_donut.data:
            values = trace.values if hasattr(trace, "values") else []
            labels = trace.labels if hasattr(trace, "labels") else []
            total = sum(values) if values is not None and len(values) > 0 else 0
            text_list = []
            for label, value in zip(labels, values):
                pct = (value / total * 100) if total > 0 else 0
                if show_labels and value > 0 and pct >= min_pct_to_show_label:
                    if show_percent:
                        text_list.append(f"{label}<br>{pct:.1f}%")
                    else:
                        text_list.append(f"{label}<br>{value:.0f} ({display_unit}/yr)")
                else:
                    text_list.append("")
            trace.text = text_list
            trace.texttemplate = "%{text}"
            trace.textinfo = "text"
            trace.insidetextorientation = "horizontal"
            trace.textfont = dict(size=auto_label_font_size)
        # --- End: Per-slice label display logic for sunburst ---
        show_data_table = False  # table option not shown in Auto mode
    else:
        # Manual mode: use all manual options and display logic
        def abbreviate_with_ellipsis(label, max_len):
            return label if len(label) <= max_len else label[:max_len - 1] + "…"

        if adaptive_abbreviate and 'Tech_subsector' in df_grouped_donut.columns:
            df_grouped_donut['Tech_subsector_display'] = df_grouped_donut['Tech_subsector'].astype(str).apply(
                lambda x: abbreviate_with_ellipsis(x, max_label_length)
            )
            sunburst_label_col = 'Tech_subsector_display'
        else:
            sunburst_label_col = 'Tech_subsector'

        base_path = [sunburst_label_col, 'Carrier', 'Tech_name']
        path = base_path[:num_rings]
        color_map = get_sunburst_color_map(path)
        fig_donut = px.sunburst(
            df_grouped_donut,
            path=path,
            values='Energy_display',
            color=path[-1],  # color by outermost ring
            color_discrete_map=color_map,
            title=f"{scenario} Transport Energy breakdown ({display_unit})",
        )
        fig_donut.update_layout(
            height=1080,
            title_x=0.5,
            title_xanchor='center',
            showlegend=True,
            uniformtext=dict(mode='show', minsize=1)
        )
        # --- Begin: Per-slice label display logic for sunburst, Manual mode ---
        total_energy = df_grouped_donut['Energy_display'].sum()
        for trace in fig_donut.data:
            values = trace.values if hasattr(trace, "values") else []
            labels = trace.labels if hasattr(trace, "labels") else []
            text_list = []
            for label, value in zip(labels, values):
                pct = (value / total_energy * 100) if total_energy > 0 else 0
                if show_labels and value > 0 and pct >= manual_min_pct_to_show_label:
                    if show_percent:
                        text_list.append(f"{label}<br>{pct:.1f}%")
                    else:
                        text_list.append(f"{label}<br>{value:.0f} ({display_unit}/yr)")
                else:
                    text_list.append("")
            trace.text = text_list
            trace.texttemplate = "%{text}"
            trace.textinfo = "text"
            trace.insidetextorientation = label_orientation if 'label_orientation' in locals() else "auto"
            trace.textfont = dict(size=label_font_size)
        # --- End: Per-slice label display logic for sunburst, Manual mode ---

    # if you used animation_frame, propagate title centering into each frame
    for frame in fig_donut.frames:
        # ensure frame.layout is a dict
        if frame.layout is None:
            frame.layout = {}
        frame.layout.update(
            title_text=fig_donut.layout.title.text,
            title_x=0.5,
            title_xanchor='center'
        )

    st.plotly_chart(fig_donut, use_container_width=True)

    if (label_mode == "Manual" and 'show_data_table' in locals() and show_data_table):
        st.subheader("Underlying values for chart")
        # Show only relevant columns
        show_cols = [sunburst_label_col, 'Carrier', 'Tech_name', 'Energy_display']
        st.dataframe(df_grouped_donut[show_cols])

    # Download button
    csv_bytes = df_grouped_donut.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download chart data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_transport_data_{display_unit}.csv",
        mime="text/csv"
    )

