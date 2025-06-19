

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



def Multi_Sector_Bar():
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
    selected_sectors = st.sidebar.multiselect(
        "Select up to 3 Sectors", sectors, default=sectors[:2], max_selections=3
    )
    provinces = sorted(df['Province'].dropna().unique())
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)
    years = sorted(pd.to_numeric(df['Year'], errors='coerce').dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", years)

    display_unit = st.sidebar.selectbox("Display unit", ["GJ","TJ","PJ"], index=["GJ","TJ","PJ"].index(base_unit))

    # Convert to GJ and apply factor
    df['Energy_GJ'] = df[energy_col] * ({'GJ':1,'PJ':1e6}[base_unit])
    factor = {'GJ':1,'TJ':1e-3,'PJ':1e-6}[display_unit]
    df['Energy_display'] = df['Energy_GJ'] * factor

    # Filter & group by sector, sub-sector and carrier, with "All Canada" optiongroup_colors

    if "All Canada" in selected_provinces:
        # Ignore province filter, aggregate across all provinces
        df_filtered = df[
            df['Sector'].isin(selected_sectors) &
            (df['Year'] == selected_year)
        ]
    else:
        df_filtered = df[
            df['Sector'].isin(selected_sectors) &
            df['Province'].isin(selected_provinces) &
            (df['Year'] == selected_year)
        ]
    grouped = df_filtered.groupby(['Sector', 'Tech_subsector', 'Carrier'])['Energy_display'].sum().reset_index()

    # Chart display options in a single expander
    with st.sidebar.expander("Chart display options", expanded=False):
        show_labels = st.checkbox("Show area/bar labels on chart", value=True)
        show_legend = st.checkbox("Show legend", value=False)
        show_decarb = st.checkbox("Show decarbonisation indicator", value=True)
        label_font_size = st.slider("Label font size", min_value=8, max_value=28, value=16)
        label_mode = st.radio(
            "Label mode",
            options=["Auto", "Manual"],
            index=0,
            help="Auto: show labels for large bars automatically. Manual: select which categories to show labels for."
        )
        tick_label_font_size = st.slider("Axis tick label font size", min_value=8, max_value=28, value=12)

        # --- BEGIN: Per-trace color and text color logic for Multi_Sector_Bar ---
        import random
        def random_hex():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))

        # --- Trace (fill) colors toggle ---
        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)
        trace_label_colors = {}
        default_map = carrier_colors
        if show_trace_colors:
            st.markdown("**Pick a color for each label's area/trace:**")
            for s in selected_sectors[:2]:
                # Each chart has its own label set
                label_options = sorted(grouped[grouped['Sector'] == s]['Carrier'].unique())
                for label in label_options:
                    col = default_map.get(label, random_hex())
                    picked = st.color_picker(f"{s}: Trace color for {label}", col, key=f"multi_bar_color_{s}_{label}")
                    trace_label_colors[(s, label)] = picked
        else:
            for s in selected_sectors[:2]:
                label_options = sorted(grouped[grouped['Sector'] == s]['Carrier'].unique())
                for label in label_options:
                    trace_label_colors[(s, label)] = default_map.get(label, random_hex())

        # --- Label text colors toggle ---
        show_label_text_colors = st.checkbox("Select label text colors (black or white)", value=False)
        text_label_colors = {}
        if show_label_text_colors:
            st.markdown("**Pick black or white for each label's text:**")
            for s in selected_sectors[:2]:
                label_options = sorted(grouped[grouped['Sector'] == s]['Carrier'].unique())
                for label in label_options:
                    txt_col = st.selectbox(
                        f"{s}: Text color for {label}",
                        options=["white", "black"],
                        index=0,
                        key=f"multi_bar_textcol_{s}_{label}"
                    )
                    text_label_colors[(s, label)] = txt_col
        else:
            for s in selected_sectors[:2]:
                label_options = sorted(grouped[grouped['Sector'] == s]['Carrier'].unique())
                for label in label_options:
                    text_label_colors[(s, label)] = "white"
        # --- END: Per-trace color and text color logic for Multi_Sector_Bar ---

    # Create two columns for side-by-side charts
    cols = st.columns(2)
    y_label = f"Energy demand ({display_unit}/yr)"

    for idx, sec in enumerate(selected_sectors[:2]):
        df_sec = grouped[grouped['Sector'] == sec]
        if df_sec.empty:
            continue
        # Per-sector label options and label selection if manual
        label_options = sorted(df_sec['Carrier'].unique())
        if label_mode == "Manual":
            show_label_for = st.multiselect(
                f"Show labels for Carriers in {sec}", label_options, default=label_options, key=f"{sec}_labels"
            )
        else:
            show_label_for = label_options
        with cols[idx]:
            st.subheader(f"{sec} Sector — {selected_year}")
            fig = px.bar(
                df_sec,
                x='Tech_subsector',
                y='Energy_display',
                color='Carrier',
                text='Carrier',
                labels={
                    'Energy_display': y_label,
                    'Tech_subsector': 'Sub-sector',
                    'Carrier': 'Carrier'
                },
                title=f"{sec} Sector ({selected_year})",
                color_discrete_map={label: trace_label_colors[(sec, label)] for label in label_options},
                category_orders={
                    'Tech_subsector': sorted(df_sec['Tech_subsector'].unique()),
                    'Carrier': stack_order
                }
            )
            # Compute stack heights per x for this sector's chart
            x_vals = [str(x) for x in df_sec['Tech_subsector']]
            stack_heights = {str(x): 0 for x in x_vals}
            for t in fig.data:
                for x, y in zip(t.x, t.y):
                    stack_heights[str(x)] += y
            auto_show = label_mode == "Auto"
            manual_show = label_mode == "Manual"
            for trace in fig.data:
                positions = []
                texts = []
                for x, y, t_ in zip(trace.x, trace.y, trace.text):
                    stack = stack_heights[str(x)]
                    rel = y / stack if stack > 0 else 0
                    label_name = t_ if isinstance(t_, str) else trace.name
                    show = (
                        (auto_show and rel >= 0.1)
                        or (manual_show and label_name in show_label_for)
                    )
                    if show:
                        positions.append("inside" if rel >= 0.1 else "outside")
                        texts.append(label_name)
                    else:
                        positions.append("none")
                        texts.append(" ")  # keep hover active with a space
                trace.textposition = positions
                trace.text = texts
                trace.texttemplate = "%{text} %{y:.0f} (" + display_unit + "/yr)"
                trace.insidetextanchor = "middle"
                trace.textfont = dict(size=label_font_size, color=text_label_colors.get((sec, trace.name), "white"))
                trace.hovertemplate = (
                    "Sub-sector: %{x}<br>"
                    f"{y_label}: "+"%{y:.1f}<br>"
                    f"Carrier: {trace.name}<extra></extra>"
                )
            # Hide bar labels if show_labels is False
            if not show_labels:
                fig.update_traces(text="", textposition="none")
            fig.update_layout(
                height=500,
                showlegend=show_legend,
                margin=dict(r=20),
                title_font=dict(size=tick_label_font_size)
            )
            fig.update_xaxes(
                tickangle=-45,
                showline=True,
                linewidth=2,
                linecolor='black',
                ticks='outside',
                ticklen=10,
                tickwidth=2,
                tickcolor='black',
                tickfont=dict(size=tick_label_font_size),
                title_font=dict(size=tick_label_font_size)
            )
            fig.update_yaxes(
                showgrid=True,
                gridcolor='lightgrey',
                gridwidth=1,
                showline=True,
                linewidth=2,
                linecolor='black',
                ticks='outside',
                ticklen=10,
                tickwidth=2,
                tickcolor='black',
                mirror=True,
                tickfont=dict(size=tick_label_font_size),
                title_font=dict(size=tick_label_font_size)
            )
            if show_decarb:
                decarb_sec = df_sec[df_sec['Carrier'].isin(fossil_carriers)] \
                             .groupby('Tech_subsector')['Energy_display'].sum().reset_index()
                fig.add_trace(go.Scatter(
                    x=decarb_sec['Tech_subsector'],
                    y=decarb_sec['Energy_display'],
                    mode='markers+text',
                    text=[f"{val:.1f} ({display_unit}/yr)" for val in decarb_sec['Energy_display']],
                    textposition="middle right",
                    textfont=dict(size=12, color="black"),
                    marker=dict(symbol='triangle-down', size=20, color='black'),
                    showlegend=False
                ))
            st.plotly_chart(fig, use_container_width=True)

    # Download chart data
    csv_bytes = grouped.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download chart data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_multi_sector_{selected_year}_{display_unit}.csv",
        mime="text/csv"
    )