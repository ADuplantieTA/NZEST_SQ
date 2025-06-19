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
    tech_subsector_to_group,
)
base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Input")



def Grouped_Industry_Bar():
    import plotly.express as px
    st.markdown(
        """
        <style>
        .stApp { background-color: #fff; color: #222; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("NZEST Grouped Industry Bar Chart")

    scenario = st.sidebar.radio("Select Scenario", ["Status-Quo", "Net-Zero (beta)"])
    fallback = 'SQ_Post_Process.csv' if scenario == 'Status-Quo' else 'NZ_Post_Process.csv'
    csv_path = os.path.join(base_dir,fallback)
    if os.path.exists(csv_path):
        df = load_csv(csv_path)
    else:
        st.error(f"No CSV for {scenario}.")
        st.stop()
    if scenario.startswith("Net-Zero"):
        df = df[df['Sector'] != "-"]

    energy_col = next(c for c in df.columns if c.startswith('Energy'))
    base_unit = energy_col.split('(')[1].split('/')[0]
    df['Energy_GJ'] = df[energy_col] * ({'GJ': 1, 'PJ': 1e6}[base_unit])

    provinces = sorted(df['Province'].dropna().unique())
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)
    years = sorted(pd.to_numeric(df['Year'], errors='coerce').dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", years)
    display_unit = st.sidebar.selectbox("Display unit", ["GJ", "TJ", "PJ"], index=["GJ", "TJ", "PJ"].index(base_unit))
    factor = {'GJ': 1, 'TJ': 1e-3, 'PJ': 1e-6}[display_unit]
    df['Energy_display'] = df['Energy_GJ'] * factor

    # Use the explicit mapping for grouping
    manufacturing_codes = {k for k, v in tech_subsector_to_group.items() if v == "Manufacturing"}
    extractive_codes = {k for k, v in tech_subsector_to_group.items() if v == "Extractive Industry"}

    st.sidebar.header("Industry Comparison Bar")
    selectable_cats = list(category_mapping.keys())
    default_cat = "Cement" if "Cement" in selectable_cats else selectable_cats[0]
    selected_cat = st.sidebar.selectbox("Select specific industry to extract and compare", selectable_cats, index=selectable_cats.index(default_cat))
    selected_codes = category_mapping[selected_cat]

    # Filter year and province
    if "All Canada" in selected_provinces:
        df_year = df[df['Year'] == selected_year]
    else:
        df_year = df[(df['Year'] == selected_year) & (df['Province'].isin(selected_provinces))]

    # Determine if the selected sector is manufacturing or extractive using mapping
    selected_cat_codes = category_mapping[selected_cat]
    selected_cat_group = tech_subsector_to_group.get(selected_cat_codes[0], None)

    # Debug: warn if mapping is incomplete
    missing_in_mapping = [code for code in selected_cat_codes if code not in tech_subsector_to_group]
    if missing_in_mapping:
        st.warning(f"The following selected sector codes are missing from tech_subsector_to_group mapping: {missing_in_mapping}")

    df_codes_missing = set(df_year['Tech_subsector'].unique()) - set(tech_subsector_to_group.keys())
    if df_codes_missing:
        st.warning(f"The following Tech_subsector codes in your data are missing from tech_subsector_to_group: {sorted(df_codes_missing)}")

    # Assign group logic
    def assign_group(row):
        if row['Tech_subsector'] in selected_codes:
            return selected_cat
        elif selected_cat_group == "Manufacturing":
            if row['Tech_subsector'] in manufacturing_codes and row['Tech_subsector'] not in selected_codes:
                return "Manufacturing Other"
            elif row['Tech_subsector'] in extractive_codes:
                return "Extractive Industry"
        elif selected_cat_group == "Extractive Industry":
            if row['Tech_subsector'] in extractive_codes and row['Tech_subsector'] not in selected_codes:
                return "Extractive Industry Other"
            elif row['Tech_subsector'] in manufacturing_codes:
                return "Manufacturing"
        return None

    df_year = df_year.copy()
    df_year['Group'] = df_year.apply(assign_group, axis=1)

    # Only show three mutually exclusive bars
    if selected_cat_group == "Manufacturing":
        keep_groups = [selected_cat, "Manufacturing Other", "Extractive Industry"]
        group_order = [selected_cat, "Manufacturing Other", "Extractive Industry"]
    elif selected_cat_group == "Extractive Industry":
        keep_groups = [selected_cat, "Manufacturing", "Extractive Industry Other"]
        group_order = [selected_cat, "Manufacturing", "Extractive Industry Other"]
    else:
        # fallback: treat as manufacturing
        keep_groups = [selected_cat, "Manufacturing Other", "Extractive Industry"]
        group_order = [selected_cat, "Manufacturing Other", "Extractive Industry"]
    df_year = df_year[df_year['Group'].isin(keep_groups)]

    grouped = (
        df_year
        .groupby(['Group', 'Carrier'])['Energy_display']
        .sum()
        .reset_index()
    )

    # Set the carrier order for the chart
    if 'stack_order' in globals():
        this_carrier_order = stack_order
    else:
        this_carrier_order = sorted(df['Carrier'].dropna().unique())

    # Chart display options
    with st.sidebar.expander("Chart display options", expanded=False):
        show_legend = st.checkbox("Show legend", value=True)
        label_font_size = st.slider("Label font size", min_value=8, max_value=28, value=16)
        label_mode = st.radio(
            "Label mode",
            options=["Auto", "Manual"],
            index=0,
            help="Auto: show labels for large bars automatically. Manual: select which groups to show labels for."
        )
        # PATCH: Use carrier names for manual label selection
        carrier_options = list(this_carrier_order)
        if label_mode == "Manual":
            show_label_for = st.multiselect("Show labels for carriers", carrier_options, default=carrier_options)
        else:
            show_label_for = carrier_options
        tick_label_font_size = st.slider("Axis tick label font size", min_value=8, max_value=28, value=12)
        show_data_table = st.checkbox("Show table of chart values below", value=False)
        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)
        carrier_color_map = {}
        if show_trace_colors:
            carriers = sorted(df['Carrier'].dropna().unique())
            for label in carriers:
                col = carrier_colors.get(label, "#CCCCCC")
                picked = st.color_picker(f"Trace color for {label}", col, key=f"grouped_ind_bar_color_{label}")
                carrier_color_map[label] = picked
        else:
            for label in df['Carrier'].dropna().unique():
                carrier_color_map[label] = carrier_colors.get(label, "#CCCCCC")
        show_label_text_colors = st.checkbox("Select label text colors (black or white)", value=False)
        label_text_colors = {}
        if show_label_text_colors:
            st.markdown("**Pick black or white for each group label's text:**")
            for group in group_order:
                txt_col = st.selectbox(
                    f"Text color for {group}",
                    options=["white", "black"],
                    index=0,
                    key=f"grouped_ind_textcol_{group}"
                )
                label_text_colors[group] = txt_col
        else:
            for group in group_order:
                label_text_colors[group] = "white"

    y_label = f"Energy demand ({display_unit}/yr)"
    fig = px.bar(
        grouped,
        x='Group',
        y='Energy_display',
        color='Carrier',
        labels={'Energy_display': y_label, 'Group': 'Industry Group', 'Carrier': 'Carrier'},
        title=f"{scenario} Industry Demand by Group ({selected_year})",
        color_discrete_map=carrier_color_map,
        category_orders={'Group': group_order, 'Carrier': this_carrier_order}
    )
    fig.update_layout(
        height=900,
        showlegend=show_legend,
        title_x=0.5,
        title_font=dict(size=tick_label_font_size),
        xaxis_title="Industry Group",
        yaxis_title=y_label,
    )
    fig.update_xaxes(
        tickangle=-10,
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

    # Label logic
    auto_show = label_mode == "Auto"
    manual_show = label_mode == "Manual"
    bar_threshold = 0.05  # Only label if bar is >=5% of group stack
    from collections import defaultdict
    stack_heights = defaultdict(float)
    for t in fig.data:
        for x_val, y_val in zip(t.x, t.y):
            stack_heights[str(x_val)] += y_val
    for trace in fig.data:
        positions = []
        texts = []
        for x_val, y_val in zip(trace.x, trace.y):
            stack = stack_heights[str(x_val)]
            rel = y_val / stack if stack > 0 else 0
            group = x_val
            # PATCH: Label logic now checks carrier name against show_label_for
            is_label = (
                (auto_show and group in group_order and rel >= bar_threshold)
                or (manual_show and trace.name in show_label_for)
            )
            if is_label:
                if y_val < 1:
                    positions.append("outside")
                else:
                    positions.append("inside" if rel >= 0.10 else "outside")
                texts.append(trace.name)
            else:
                positions.append("none")
                texts.append(" ")
        trace.textposition = positions
        trace.text = texts
        trace.texttemplate = "%{text} %{y:.0f} (" + display_unit + "/yr)"
        trace.insidetextanchor = "middle"
        group_name = trace.x[0] if hasattr(trace, "x") and len(trace.x) > 0 else trace.name
        trace.textfont = dict(size=label_font_size, color=label_text_colors.get(group_name, "white"))
        trace.width = 0.54
        trace.hovertemplate = (
            "Group: %{x}<br>"
            f"{y_label}: "+"%{y:.3f}<br>"
            "Carrier: %{legendgroup}<extra></extra>"
        )

    st.plotly_chart(fig, use_container_width=True)

    if show_data_table:
        st.subheader("Underlying values for chart")
        st.dataframe(grouped.pivot(index='Carrier', columns='Group', values='Energy_display').reset_index())

    csv_bytes = grouped.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download grouped industry data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_grouped_industry_{selected_year}_{display_unit}.csv",
        mime="text/csv"
    )