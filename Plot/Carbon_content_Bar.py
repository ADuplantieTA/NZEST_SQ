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

def Carbon_content_Bar():
    st.markdown(
        """
        <style>
        .stApp { background-color: #fff; color: #222; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("NZEST Carbon Content Chart")

    # Scenario toggle (no uploader)
    scenario = st.sidebar.radio("Select Scenario", ["Status-Quo", "Net-Zero (beta)"])
    fallback = 'SQ_Post_Process.csv' if scenario == 'Status-Quo' else 'NZ_Post_Process.csv'
    csv_path = os.path.join(base_dir, fallback)
    if os.path.exists(csv_path):
        df = load_csv(csv_path)
    else:
        st.error(f"No CSV for {scenario} at {csv_path}.")
        st.stop()
    # Filter out placeholder sector "-" for Net-Zero
    if scenario.startswith("Net-Zero"):
        df = df[df['Sector'] != "-"]

    # Filter out empty/null/zero carbon content
    df = df[df['Carbon Content MT c'].notna() & (df['Carbon Content MT c'] > 0)]

    # Sidebar filters
    st.sidebar.header("Filters")
    sectors = sorted(df['Sector'].dropna().unique())
    selected_sectors = st.sidebar.multiselect("Select Sectors", sectors, default=sectors)
    provinces = sorted(df['Province'].dropna().unique())
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)
    years = sorted(pd.to_numeric(df['Year'], errors='coerce').dropna().unique())
    selected_years = st.sidebar.multiselect("Select up to 5 Years", options=years, default=years[:5], max_selections=5)

    # Group-by toggle
    group_map = {
        "Carrier": "Carrier",
        "Carrier & Tech": "Tech_name",
        "Sub Sector": "Tech_subsector"
    }
    sel_label = st.sidebar.selectbox("Group by", list(group_map.keys()))
    dim_col = group_map[sel_label]

    # --- All chart display options and label selector in a single expander ---
    with st.sidebar.expander("Chart display options", expanded=False):
        show_labels = st.checkbox("Show bar labels on chart", value=True)
        show_legend = st.checkbox("Show legend", value=False)
        label_font_size = st.slider("Label font size", min_value=8, max_value=28, value=16)
        label_mode = st.radio(
            "Label mode",
            options=["Auto", "Manual"],
            index=0,
            help="Auto: show labels for large bars automatically. Manual: select which categories to show labels for."
        )
        if not df.empty:
            # Filter & group (for label options)
            if "All Canada" in selected_provinces:
                df_filtered_tmp = df[
                    df['Sector'].isin(selected_sectors) &
                    df['Year'].isin(selected_years)
                ]
            else:
                df_filtered_tmp = df[
                    df['Sector'].isin(selected_sectors) &
                    df['Province'].isin(selected_provinces) &
                    df['Year'].isin(selected_years)
                ]
            grouped_tmp = df_filtered_tmp.groupby(['Year', dim_col])['Carbon Content MT c'].sum().reset_index()
            grouped_tmp['Year'] = grouped_tmp['Year'].astype(str)
            total_by_cat_tmp = grouped_tmp.groupby(dim_col)['Carbon Content MT c'].sum()
            total_all_tmp = total_by_cat_tmp.sum()
            keep_cats_tmp = total_by_cat_tmp[total_by_cat_tmp / total_all_tmp >= 0.0001].index
            grouped_tmp = grouped_tmp[grouped_tmp[dim_col].isin(keep_cats_tmp)]
            if not grouped_tmp.empty and dim_col in grouped_tmp.columns:
                label_options = sorted(grouped_tmp[dim_col].unique())
                if label_mode == "Manual":
                    show_label_for = st.multiselect(
                        f"Show labels for {sel_label}s", label_options, default=label_options
                    )
                else:
                    show_label_for = label_options
            else:
                label_options, show_label_for = [], []
                st.warning("No categories available for label selection with current filters.")
        else:
            label_options, show_label_for = [], []
            st.warning("No categories available for label selection with current filters.")
        # Add tick label font size slider at the end
        tick_label_font_size = st.slider(
            "Axis tick label font size", min_value=16, max_value=34, value=24
        )
        # Add data table checkbox
        show_data_table = st.checkbox("Show table of chart values below", value=False)

        # --- BEGIN: Per-label color logic ---
        # --- Trace (fill) colors toggle ---
        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)
        label_colors = {}
        default_map = carrier_colors if sel_label == "Carrier" else carrier_colors
        if show_trace_colors and label_options:
            st.markdown("**Pick a color for each label's area/trace:**")
            for label in label_options:
                col = default_map.get(label, None)
                picked = st.color_picker(f"Trace color for {label}", col if col is not None else "#636efa", key=f"carbon_color_{sel_label}_{label}")
                label_colors[label] = picked
        elif label_options:
            for label in label_options:
                col = default_map.get(label, None)
                if col is not None:
                    label_colors[label] = col
                # If no color found, don't assign; let Plotly use its default

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
                    key=f"carbon_textcol_{sel_label}_{label}"
                )
                label_text_colors[label] = txt_col
        elif label_options:
            for label in label_options:
                label_text_colors[label] = "white"
        # --- END: Per-label color logic ---

    # Filter & group
    if "All Canada" in selected_provinces:
        df_filtered = df[
            df['Sector'].isin(selected_sectors) &
            df['Year'].isin(selected_years)
        ]
    else:
        df_filtered = df[
            df['Sector'].isin(selected_sectors) &
            df['Province'].isin(selected_provinces) &
            df['Year'].isin(selected_years)
        ]
    grouped = df_filtered.groupby(['Year', dim_col])['Carbon Content MT c'].sum().reset_index()
    grouped['Year'] = grouped['Year'].astype(str)
    # Filter out categories representing <5% of total for clarity
    total_by_cat = grouped.groupby(dim_col)['Carbon Content MT c'].sum()
    total_all = total_by_cat.sum()
    keep_cats = total_by_cat[total_by_cat / total_all >= 0.0001].index
    grouped = grouped[grouped[dim_col].isin(keep_cats)]

    # Plot
    y_label = "Carbon Content (MT C/yr)"
    fig = px.bar(
        grouped,
        x='Year',
        y='Carbon Content MT c',
        color=dim_col,
        text=dim_col,
        labels={'Carbon Content MT c': y_label, 'Year': 'Year', dim_col: sel_label},
        title=f"{scenario} {y_label} by {sel_label} for sectors: {', '.join(selected_sectors)}",
        color_discrete_map=label_colors,
        category_orders={dim_col: stack_order},
    )

    # Compute stack heights for each x (Year)
    from collections import defaultdict
    stack_heights = defaultdict(float)
    for t in fig.data:
        for x, y in zip(t.x, t.y):
            stack_heights[str(x)] += y
    threshold = 0.05  # 5% of stack at each x, matching Industry_Sector_Bar
    inside_threshold = 0.10  # need at least 10 % of the stack to keep the label inside

    auto_show = label_mode == "Auto"
    manual_show = label_mode == "Manual"
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
                min_abs_height = 1                      # absolute threshold (MT C/yr)
                min_px_height  = label_font_size * 0.03 # rough bar‑height (in data units) needed to fit the text

                # Decide where to place the label
                if y < min_abs_height or y < min_px_height:
                    # Bar too small (either in absolute terms or relative to chosen font) → put text above
                    positions.append("outside")
                else:
                    positions.append("inside" if rel >= inside_threshold else "outside")

                texts.append(label_name)
            else:
                positions.append("none")
                texts.append(" ")  # keep hover active with a space
        trace.textposition = positions
        trace.text = texts
        trace.texttemplate = "%{text} %{y:.1f} (MT C/yr)"
        trace.insidetextanchor = "middle"
        trace.textfont = dict(size=label_font_size, color=label_text_colors.get(trace.name, "white"))
        trace.width = 0.54
        # Set custom hovertemplate always
        trace.hovertemplate = (
            "Year: %{x}<br>"
            f"{y_label}: "+"%{y:.3f}<br>"
            f"{sel_label}: {trace.name}<extra></extra>"
        )

    if not show_labels:
        fig.update_traces(text="", textposition="none")

    # Do not set uniformtext or update textfont/textposition globally after the above per-trace logic.
    fig.update_layout(
        height=800,
        title_x=0.5,
        title_xanchor='center',
        title_font=dict(size=tick_label_font_size),
        showlegend=show_legend,
        margin=dict(r=20)
    )
    # Prevent Plotly from shrinking outside labels
    fig.update_layout(
        uniformtext=dict(
            minsize=label_font_size,
            mode="show"      # keep text at least `minsize`; never shrink
        )
    )
    fig.update_xaxes(
        type='category',
        categoryorder='array',
        categoryarray=list(grouped['Year']),
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
        mirror=True,
        tickfont=dict(size=tick_label_font_size),
        title_font=dict(size=tick_label_font_size)
    )

    # Download button for CSV
    csv_bytes = grouped.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download carbon content data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_carbon_content_{'_'.join(selected_sectors)}.csv",
        mime="text/csv"
    )

    st.plotly_chart(fig, use_container_width=True)
    if show_data_table:
        st.subheader("Underlying values for chart")
        st.dataframe(grouped)
