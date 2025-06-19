

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

def Industry_Sector_Bar():
    st.markdown(
        """
        <style>
        .stApp { background-color: #fff; color: #222; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("NZEST Chart Generator - Industry")

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

    # Convert to GJ and apply factor
    df['Energy_GJ'] = df[energy_col] * ({'GJ':1,'PJ':1e6}[base_unit])
    factor = {'GJ':1,'TJ':1e-3,'PJ':1e-6}[display_unit]
    df['Energy_display'] = df['Energy_GJ'] * factor

    # Filter to Industry sector, with "All Canada" option
    if "All Canada" in selected_provinces:
        # Ignore province filter, aggregate across all provinces
        df_ind = df[
            (df['Sector'] == "Industry") &
            (df['Year'] == selected_year)
        ]
    else:
        df_ind = df[
            (df['Sector'] == "Industry") &
            df['Province'].isin(selected_provinces) &
            (df['Year'] == selected_year)
        ]

    # Sidebar: select one high-level industry category
    category_options = list(category_mapping.keys())
    selected_categories = st.sidebar.multiselect(
        "Select Industry Categories", category_options,
        default=[category_options[0]],
        max_selections=len(category_options)
    )
    # Filter to the selected categories using category_mapping
    # Flatten codes from all selected categories
    selected_codes = [code for cat in selected_categories for code in category_mapping[cat]]
    # Map codes to descriptive subsector names
    selected_subsectors = [sector_activity_dict[code] for code in selected_codes]
    df_ind = df_ind[df_ind['Tech_subsector'].isin(selected_subsectors)]

    # Group only by Tech_subsector and Carrier (remove Industry_group)
    grouped_ind = df_ind.groupby(['Tech_subsector','Carrier'])['Energy_display'].sum().reset_index()
    # Filter out small contributions (<5% of total category energy)
    total_energy = grouped_ind['Energy_display'].sum()
    grouped_ind = grouped_ind[grouped_ind['Energy_display'] >= 0.001 * total_energy]

    # Render the chart for the chosen high-level category
    y_label = f"Energy demand ({display_unit}/yr)"
    fossil_carriers = ["Coal", "HFO", "LFO",
                       "Diesel", "R-Diesel", "Gasoline", "Jet Fuel",
                       "Prop", "NG", "Plastics"]

    df_grp = grouped_ind.copy()

    # Chart display options in a single expander (moved after df_grp definition)
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
        label_options = sorted(df_grp['Carrier'].unique())
        if label_mode == "Manual":
            show_label_for = st.multiselect(
                "Show labels for Carriers", label_options, default=label_options
            )
        else:
            show_label_for = label_options
        # Add tick label font size slider at the end
        tick_label_font_size = st.slider("Axis tick label font size", min_value=8, max_value=28, value=12)

        # --- BEGIN: Per-label color logic for Industry_Sector_Bar ---
        import random
        def random_hex():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))

        # --- Trace (fill) colors toggle ---
        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)
        label_colors = {}
        default_map = carrier_colors
        if show_trace_colors:
            st.markdown("**Pick a color for each label's area/trace:**")
            for label in label_options:
                col = default_map.get(label, random_hex())
                picked = st.color_picker(f"Trace color for {label}", col, key=f"ind_bar_color_{label}")
                label_colors[label] = picked
        else:
            for label in label_options:
                label_colors[label] = default_map.get(label, random_hex())

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
                    key=f"ind_bar_textcol_{label}"
                )
                label_text_colors[label] = txt_col
        else:
            for label in label_options:
                label_text_colors[label] = "white"
        # --- END: Per-label color logic for Industry_Sector_Bar ---

    # Display combined header for multiple categories
    categories_label = ", ".join(selected_categories)
    st.subheader(f"{categories_label} — {selected_year}")
    fig = px.bar(
        df_grp,
        x='Tech_subsector',
        y='Energy_display',
        color='Carrier',
        text='Carrier',
        labels={
            'Energy_display': y_label,
            'Tech_subsector': 'Sub-sector',
            'Carrier': 'Carrier'
        },
        title=f"{categories_label} ({selected_year})",
        color_discrete_map=label_colors,
        category_orders={
            'Tech_subsector': sorted(df_grp['Tech_subsector'].unique()),
            'Carrier': stack_order
        }
    )
    # Compute stack heights for each x (subsector)
    stack_heights = defaultdict(float)
    for t in fig.data:
        for x, y in zip(t.x, t.y):
            stack_heights[str(x)] += y

    auto_show = label_mode == "Auto"
    manual_show = label_mode == "Manual"
    threshold = 0.05  # 10% of stack height

    for trace in fig.data:
        positions = []
        texts = []
        for x, y, t in zip(trace.x, trace.y, trace.text):
            stack = stack_heights[str(x)]
            rel = y / stack if stack > 0 else 0
            label_name = t if isinstance(t, str) else trace.name
            show = (
                (auto_show and rel >= threshold)
                or (manual_show and label_name in show_label_for)
            )
            if show:
                # If under 1 PJ/yr, always put label "outside"
                if y < 1:
                    positions.append("outside")
                else:
                    positions.append("inside" if rel >= threshold else "outside")
                texts.append(label_name)
            else:
                positions.append("none")
                texts.append(" ")  # keep hover active with a space
        trace.textposition = positions
        trace.text = texts
        trace.texttemplate = "%{text} %{y:.1f} (" + display_unit + "/yr)"
        trace.insidetextanchor = "middle"
        trace.textfont = dict(size=label_font_size, color=label_text_colors.get(trace.name, "white"))
        trace.hovertemplate = (
            "Sub-sector: %{x}<br>"
            f"{y_label}: "+"%{y:.1f}<br>"
            f"Carrier: {trace.name}<extra></extra>"
        )
    # Hide bar labels if show_labels is False
    if not show_labels:
        fig.update_traces(text="", textposition="none")
    fig.update_layout(
        height=800,
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
        tickformat=".1f",
        mirror=True,
        tickfont=dict(size=tick_label_font_size),
        title_font=dict(size=tick_label_font_size)
    )
    if show_decarb:
        decarb_grp = df_grp[df_grp['Carrier'].isin(fossil_carriers)] \
                    .groupby('Tech_subsector')['Energy_display'].sum().reset_index()
        fig.add_trace(go.Scatter(
            x=decarb_grp['Tech_subsector'],
            y=decarb_grp['Energy_display'],
            mode='markers+text',
            text=[f"{val:.1f} ({display_unit}/yr)" for val in decarb_grp['Energy_display']],
            textposition="middle right",
            textfont=dict(size=label_font_size, color="black"),
            marker=dict(symbol='triangle-down', size=20, color='black'),
            showlegend=False
        ))
    st.plotly_chart(fig, use_container_width=True)

    # Download chart data
    csv_bytes = grouped_ind.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download industry data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_industry_{selected_year}_{display_unit}.csv",
        mime="text/csv"
    )



