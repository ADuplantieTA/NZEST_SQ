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


def Energy_Demand_Bar():
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
    provinces_with_all = ["All Canada"] + provinces
    selected_provinces = st.sidebar.multiselect("Select Provinces", provinces_with_all, default=provinces_with_all)
    years = sorted(pd.to_numeric(df['Year'], errors='coerce').dropna().unique())
    selected_years = st.sidebar.multiselect("Select up to 5 Years", options=years, default=years[:5], max_selections=5)
    # Toggle for decarbonisation marker
    # show_decarb = st.sidebar.checkbox("Show decarbonisation indicator", value=True)

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

    # Filter & group with "All Canada" option
    if "All Canada" in selected_provinces:
        # Ignore specific province filters and aggregate across all provinces
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
    grouped = df_filtered.groupby(['Year', dim_col])['Energy_display'].sum().reset_index()
    grouped['Year'] = grouped['Year'].astype(str)
    # Filter out categories representing <5% of total over the selected range
    total_by_cat = grouped.groupby(dim_col)['Energy_display'].sum()
    total_all = total_by_cat.sum()
    keep_cats = total_by_cat[total_by_cat / total_all >= 0.0001].index
    grouped = grouped[grouped[dim_col].isin(keep_cats)]

    # --- All chart display options and label selector in a single expander ---
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
        if not grouped.empty and dim_col in grouped.columns:
            label_options = sorted(grouped[dim_col].unique())
            if label_mode == "Manual":
                show_label_for = st.multiselect(
                    f"Show labels for {sel_label}s", label_options, default=label_options
                )
            else:
                show_label_for = label_options
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
        import random
        def random_hex():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))

        # --- Trace (fill) colors toggle ---
        show_trace_colors = st.checkbox("Select trace (fill) colors", value=False)
        label_colors = {}
        default_map = carrier_colors if sel_label == "Carrier" else carrier_colors
        if show_trace_colors and label_options:
            st.markdown("**Pick a color for each label's area/trace:**")
            for label in label_options:
                col = default_map.get(label, random_hex())
                picked = st.color_picker(f"Trace color for {label}", col, key=f"bar_color_{sel_label}_{label}")
                label_colors[label] = picked
        elif label_options:
            for label in label_options:
                label_colors[label] = default_map.get(label, random_hex())

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
                    key=f"bar_textcol_{sel_label}_{label}"
                )
                label_text_colors[label] = txt_col
        elif label_options:
            for label in label_options:
                label_text_colors[label] = "white"
        # --- END: Per-label color logic ---

    # Plot
    y_label = f"Energy demand ({display_unit}/yr)"
    fig = px.bar(
        grouped,
        x='Year',
        y='Energy_display',
        color=dim_col,
        text=dim_col,  # add this line
        labels={'Energy_display': y_label, 'Year':'Year', dim_col:sel_label},
        title=f"{scenario} {y_label} by {sel_label} for sectors: {', '.join(selected_sectors)}",
        category_orders={dim_col: stack_order},
        color_discrete_map=label_colors,
    )

    # Enforce white background, black fonts, and full numeric ticks
    fig.update_layout(template='plotly_white', font_color='black')
    fig.update_xaxes(tickfont=dict(color='black'), title_font=dict(color='black'), tickformat='.0f')
    fig.update_yaxes(tickfont=dict(color='black'), title_font=dict(color='black'), tickformat='.0f')

    # Enforce white background, black fonts, and full numeric ticks
    fig.update_layout(
        template='plotly_white',
        font_color='black'
    )
    fig.update_xaxes(
        tickfont=dict(color='black'),
        title_font=dict(color='black'),
        tickformat='.0f'
    )
    fig.update_yaxes(
        tickfont=dict(color='black'),
        title_font=dict(color='black'),
        tickformat='.0f'
    )

    # Compute stack heights for each x (Year) before the label loop
    from collections import defaultdict  # already imported at top; harmless re-import
    # Build total stack height per Year so we can compare each bar to its stack
    stack_heights = defaultdict(float)
    for t in fig.data:
        for x_val, y_val in zip(t.x, t.y):
            stack_heights[str(x_val)] += y_val

    threshold = 0.05        # bar must be ≥ 5 % of its stack to be considered
    inside_threshold = 0.10  # bar must be ≥ 10 % of its stack to keep the label *inside*

    auto_show = label_mode == "Auto"
    manual_show = label_mode == "Manual"
    for trace in fig.data:
        positions = []
        texts = []
        for x_val, y_val, t_text in zip(trace.x, trace.y, trace.text):
            stack = stack_heights[str(x_val)]
            rel = y_val / stack if stack > 0 else 0
            label_name = t_text if isinstance(t_text, str) else trace.name
            show = (
                (auto_show and rel >= threshold)
                or (manual_show and label_name in show_label_for)
            )
            if show:
                # If bar is < 1 (in displayed unit), force the label outside
                if y_val < 1:
                    positions.append("outside")
                else:
                    positions.append("inside" if rel >= inside_threshold else "outside")
                texts.append(label_name)
            else:
                positions.append("none")
                texts.append(" ")  # keep hover active with a space

        trace.textposition = positions
        trace.text = texts
        trace.texttemplate = "%{text} %{y:.0f} (" + display_unit + "/yr)"
        trace.insidetextanchor = "middle"
        trace.textfont = dict(size=label_font_size, color=label_text_colors.get(trace.name, "white"))
        # Force specific labels to black
        if trace.name in ["Jet Fuel", "Elec"]:
            trace.textfont['color'] = 'black'
        trace.width = 0.54
        trace.hovertemplate = (
            "Year: %{x}<br>"
            f"{y_label}: "+"%{y:.3f}<br>"
            f"{sel_label}: {trace.name}<extra></extra>"
        )

    # Hide bar labels if show_labels is False
    if not show_labels:
        fig.update_traces(text="", textposition="none")

    # (Removed redundant fillcolor/line update for bar chart)
    fig.update_layout(height=800)
    # Configure major and minor ticks on axes
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
        tickfont=dict(size=tick_label_font_size, color='black'),
        title_font=dict(size=tick_label_font_size, color='black'),
        tickformat=".0f"
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
        tickformat=".0f",
        minor=dict(
            ticklen=5,
            tickwidth=2,
            tickcolor='black',
            showgrid=False
        ),
        mirror=True,
        tickfont=dict(size=tick_label_font_size, color='black'),
        title_font=dict(size=tick_label_font_size, color='black')
    )

    # Center title and set font size to match tick_label_font_size
    fig.update_layout(
        title_x=0.5,
        title_xanchor='center',
        title_font=dict(size=tick_label_font_size)
    )

    # 1) Show/hide the legend as per sidebar
    fig.update_layout(showlegend=show_legend)

    if show_decarb:
        # Add decarbonisation indicator: sum of specific fossil carriers for each year
        fossil_carriers = ["Coal", "HFO", "LFO",
                           "Diesel", "R-Diesel", "Gasoline", "Jet Fuel",
                           "Prop", "NG", "Plastics"]
        decarb = grouped[grouped[dim_col].isin(fossil_carriers)] \
                  .groupby('Year')['Energy_display'].sum().reset_index()
        # Add marker trace for decarbonisation amount
        fig.add_trace(go.Scatter(
            x=decarb['Year'],
            y=decarb['Energy_display'],
            mode='markers+text',
            text=[f"{val:.1f} ({display_unit}/yr)" for val in decarb['Energy_display']],
            textposition="middle right",
            textfont=dict(size=label_font_size, color="black"),
            marker=dict(symbol='triangle-down', size=20, color='black'),
            name='To Decarbonise'
        ))
        # Enable legend to show the decarbonisation indicator
        fig.update_layout(showlegend=show_legend)

    # Slight right margin to avoid clipping the line
    fig.update_layout(margin=dict(r=20))

    # Prevent Plotly from shrinking outside labels
    fig.update_layout(
        uniformtext=dict(
            minsize=label_font_size,
            mode="show"  # keep text at least this size
        )
    )

    # Download button
    csv_bytes = grouped.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download chart data as CSV",
        data=csv_bytes,
        file_name=f"{scenario}_data_{display_unit}.csv",
        mime="text/csv"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    if show_data_table:
        st.subheader("Underlying values for chart")
        st.dataframe(grouped)