import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Academic Command Center",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d2e 0%, #16192a 100%);
        border-right: 1px solid #2d3154;
    }

    /* KPI card style */
    .kpi-card {
        background: linear-gradient(135deg, #1e2235 0%, #252942 100%);
        border: 1px solid #3d4266;
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover { transform: translateY(-4px); }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #8891b4;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
    }
    .kpi-delta-good  { font-size: 13px; color: #4ade80; margin-top: 6px; }
    .kpi-delta-bad   { font-size: 13px; color: #f87171; margin-top: 6px; }
    .kpi-delta-neutral{ font-size: 13px; color: #94a3b8; margin-top: 6px; }

    /* Section header */
    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #c8ccf0;
        border-left: 4px solid #6366f1;
        padding-left: 12px;
        margin: 24px 0 16px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #1e2235;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #2d3154;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #8891b4;
        font-weight: 500;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #6366f1 !important;
        color: white !important;
    }

    /* Metric delta override */
    [data-testid="stMetricDelta"] { font-size: 13px !important; }

    /* Dataframe */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Select box */
    .stSelectbox > div > div {
        background: #1e2235;
        border: 1px solid #3d4266;
        border-radius: 10px;
        color: #c8ccf0;
    }

    /* Alert / info box */
    .stAlert { border-radius: 12px; }

    /* Hide Streamlit footer */
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Plotly dark theme helper ──────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#c8ccf0"),
    margin=dict(t=30, b=30, l=10, r=10),
    xaxis=dict(
        gridcolor="#2d3154", linecolor="#2d3154",
        tickfont=dict(color="#8891b4")
    ),
    yaxis=dict(
        gridcolor="#2d3154", linecolor="#2d3154",
        tickfont=dict(color="#8891b4")
    ),
    legend=dict(
        bgcolor="rgba(30,34,53,0.8)",
        bordercolor="#3d4266",
        borderwidth=1,
        font=dict(color="#c8ccf0")
    )
)

ACCENT_COLORS = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e", "#a78bfa"]

# ─── Google Sheet URL ──────────────────────────────────────────────────────────
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1IfhxtNcnHGr4ue1vYDngmRzUdJ02ucPIqjCVHbgL5j8/edit?usp=sharing"



# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Academic Hub")
    st.markdown("---")
    st.markdown("**Navigation**")
    selected_view = st.radio(
        label="View",
        options=["📊 Overview", "🔍 Explore Data", "📋 Records"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Filters**")
    sidebar_filter_placeholder = st.empty()
    st.markdown("---")
    st.info("📡 Data synced live from Google Sheets", icon="ℹ️")

# ─── Header ───────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.markdown("<div style='font-size:48px;padding-top:8px'>🏫</div>", unsafe_allow_html=True)
with col_title:
    st.markdown(
        "<h1 style='color:#ffffff;margin:0;font-size:28px;font-weight:800;"
        "letter-spacing:-0.5px'>University Academic & Attendance Command Center</h1>"
        "<p style='color:#8891b4;margin:4px 0 0;font-size:14px'>"
        "Real-time insights powered by Google Sheets integration</p>",
        unsafe_allow_html=True
    )
st.markdown("<hr style='border:1px solid #2d3154;margin:16px 0'>", unsafe_allow_html=True)

# ─── Data Load ────────────────────────────────────────────────────────────────
try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.spinner("🔄 Syncing live data stream..."):
        df = conn.read(spreadsheet=GOOGLE_SHEET_URL, ttl=60)

    # Clean columns
    df.columns = [col.strip() for col in df.columns]
    df['sgp']    = pd.to_numeric(df['sgp'],    errors='coerce')
    df['absent'] = pd.to_numeric(df['absent'], errors='coerce')
    if 'college' not in df.columns:
        df['college'] = 'N/A'
    df['college'] = df['college'].fillna('N/A').astype(str).str.strip()

    # ─── Aggregations ─────────────────────────────────────────────────────────
    dept_summary = df.groupby('programme').agg(
        total_students=('Name', 'count'),
        avg_sgpa      =('sgp',  'mean'),
        total_absences=('absent','sum')
    ).reset_index()

    college_summary = df.groupby('college').agg(
        total_students=('Name', 'count'),
        avg_sgpa      =('sgp',  'mean'),
        total_absences=('absent','sum')
    ).reset_index()

    global_avg_sgpa       = df['sgp'].mean()
    total_absences_logged = df['absent'].sum()
    total_students        = len(df)
    total_depts           = df['programme'].nunique()

    at_risk = df[df['sgp'] < 6.0]

    if not dept_summary.empty:
        top_dept_row      = dept_summary.loc[dept_summary['avg_sgpa'].idxmax()]
        worst_absent_row  = dept_summary.loc[dept_summary['total_absences'].idxmax()]
        top_dept          = top_dept_row['programme']
        top_dept_score    = f"{top_dept_row['avg_sgpa']:.2f}"
        worst_dept        = worst_absent_row['programme']
        worst_dept_days   = int(worst_absent_row['total_absences'])
    else:
        top_dept = worst_dept = "N/A"
        top_dept_score = "0.00"
        worst_dept_days = 0

    # ─── Sidebar dynamic filters ───────────────────────────────────────────────
    with sidebar_filter_placeholder.container():
        all_years    = ["All Years"]       + sorted(df['study year'].dropna().unique().tolist())
        all_depts    = ["All Departments"] + sorted(df['programme'].dropna().unique().tolist())
        all_colleges = ["All Colleges"]    + sorted(df['college'].dropna().unique().tolist())

        selected_year    = st.selectbox("Study Year",  all_years)
        selected_dept    = st.selectbox("Department",  all_depts)
        selected_college = st.selectbox("College",     all_colleges)

    filtered_df = df.copy()
    if selected_year != "All Years":
        filtered_df = filtered_df[filtered_df['study year'] == selected_year]
    if selected_dept != "All Departments":
        filtered_df = filtered_df[filtered_df['programme'] == selected_dept]
    if selected_college != "All Colleges":
        filtered_df = filtered_df[filtered_df['college'] == selected_college]

    # ─── KPI Row ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi_card(col, label, value, delta, delta_type="neutral"):
        delta_class = {"good": "kpi-delta-good", "bad": "kpi-delta-bad"}.get(delta_type, "kpi-delta-neutral")
        icon = {"good": "▲", "bad": "▼"}.get(delta_type, "•")
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_class}">{icon} {delta}</div>
        </div>""", unsafe_allow_html=True)

    kpi_card(k1, "🥇 Top Department",    top_dept,          f"SGPA {top_dept_score}",         "good")
    kpi_card(k2, "⚠️ Highest Absences",  worst_dept,        f"{worst_dept_days} days absent",  "bad")
    kpi_card(k3, "📚 College Avg SGPA",  f"{global_avg_sgpa:.2f}" if not pd.isna(global_avg_sgpa) else "N/A",
                                          "Overall benchmark",                                   "neutral")
    kpi_card(k4, "🏃 Total Absences",    f"{int(total_absences_logged)}" if not pd.isna(total_absences_logged) else "0",
                                          "All programs",                                         "bad")
    kpi_card(k5, "🚨 At-Risk Students",  len(at_risk),      "SGPA below 6.0",                  "bad")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Views ────────────────────────────────────────────────────────────────
    if selected_view == "📊 Overview":

        st.markdown('<div class="section-header">Visual Analytics</div>', unsafe_allow_html=True)

        # Row 1: Donut + Bar
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("##### Student Enrollment Distribution")
            fig_donut = px.pie(
                dept_summary,
                values='total_students',
                names='programme',
                hole=0.55,
                color_discrete_sequence=ACCENT_COLORS
            )
            fig_donut.update_traces(
                textposition='outside',
                textinfo='label+percent',
                textfont_size=12,
                marker=dict(line=dict(color='#0f1117', width=3))
            )
            fig_donut.add_annotation(
                text=f"<b>{total_students}</b><br>Students",
                x=0.5, y=0.5,
                font=dict(size=18, color="#ffffff"),
                showarrow=False
            )
            fig_donut.update_layout(**CHART_LAYOUT, showlegend=False)
            st.plotly_chart(fig_donut, use_container_width=True)

        with c2:
            st.markdown("##### Average SGPA by Department")
            sorted_dept = dept_summary.sort_values('avg_sgpa', ascending=True)
            fig_hbar = go.Figure(go.Bar(
                y=sorted_dept['programme'],
                x=sorted_dept['avg_sgpa'],
                orientation='h',
                marker=dict(
                    color=sorted_dept['avg_sgpa'],
                    colorscale=[[0, "#f43f5e"], [0.5, "#f59e0b"], [1, "#10b981"]],
                    line=dict(width=0)
                ),
                text=[f"{v:.2f}" for v in sorted_dept['avg_sgpa']],
                textposition='outside',
                textfont=dict(color="#c8ccf0", size=12)
            ))
            fig_hbar.add_vline(
                x=6.0,
                line_dash="dash",
                line_color="#f43f5e",
                annotation_text="Target 6.0",
                annotation_font_color="#f43f5e"
            )
            fig_hbar.update_layout(**CHART_LAYOUT, xaxis_title="Avg SGPA", yaxis_title="")
            st.plotly_chart(fig_hbar, use_container_width=True)

        # Row 2: Bubble chart + At-Risk table
        c3, c4 = st.columns([3, 2])

        with c3:
            st.markdown("##### Dept Performance vs Absence Bubble Chart")
            fig_bubble = px.scatter(
                dept_summary,
                x='avg_sgpa',
                y='total_absences',
                size='total_students',
                color='programme',
                hover_name='programme',
                size_max=60,
                color_discrete_sequence=ACCENT_COLORS,
                labels={
                    'avg_sgpa': 'Average SGPA',
                    'total_absences': 'Total Absences',
                    'total_students': 'Students'
                }
            )
            fig_bubble.add_vline(x=6.0, line_dash="dot", line_color="#f43f5e",
                                 annotation_text="SGPA Target", annotation_font_color="#f43f5e")
            fig_bubble.update_traces(marker=dict(opacity=0.85, line=dict(width=2, color='#0f1117')))
            fig_bubble.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig_bubble, use_container_width=True)

        with c4:
            st.markdown("##### 🚨 At-Risk Student List")
            if not at_risk.empty:
                display_cols = [c for c in ['Name', 'programme', 'college', 'sgp', 'absent'] if c in at_risk.columns]
                st.dataframe(
                    at_risk[display_cols]
                      .sort_values('sgp')
                      .rename(columns={'programme': 'Dept', 'college': 'College', 'sgp': 'SGPA', 'absent': 'Absences'}),
                    hide_index=True,
                    use_container_width=True,
                    height=350
                )
            else:
                st.success("No at-risk students! All SGPA ≥ 6.0")

        # Row 3: Grouped bar for SGPA + Absences together
        st.markdown("##### Department Comparison — SGPA vs Absence Load")
        fig_combo = go.Figure()
        fig_combo.add_trace(go.Bar(
            name='Avg SGPA',
            x=dept_summary['programme'],
            y=dept_summary['avg_sgpa'],
            marker_color='#6366f1',
            yaxis='y',
            offsetgroup=1
        ))
        fig_combo.add_trace(go.Bar(
            name='Total Absences',
            x=dept_summary['programme'],
            y=dept_summary['total_absences'],
            marker_color='#f43f5e',
            yaxis='y2',
            offsetgroup=2
        ))
        combo_layout = {k: v for k, v in CHART_LAYOUT.items() if k not in ('yaxis', 'xaxis', 'legend')}
        combo_layout.update(dict(
            barmode='group',
            xaxis=dict(gridcolor="#2d3154", linecolor="#2d3154", tickfont=dict(color="#8891b4")),
            yaxis=dict(title='Avg SGPA', gridcolor="#2d3154", tickfont=dict(color="#8891b4")),
            yaxis2=dict(title='Total Absences', overlaying='y', side='right',
                        gridcolor="#2d3154", tickfont=dict(color="#8891b4")),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                        bgcolor='rgba(30,34,53,0.8)', bordercolor='#3d4266', borderwidth=1,
                        font=dict(color='#c8ccf0'))
        ))
        fig_combo.update_layout(**combo_layout)
        st.plotly_chart(fig_combo, use_container_width=True)

        # Row 4: College-level charts
        st.markdown('<div class="section-header">College-wise Analytics</div>', unsafe_allow_html=True)
        c5, c6 = st.columns(2)

        with c5:
            st.markdown("##### Student Enrollment by College")
            fig_college_donut = px.pie(
                college_summary,
                values='total_students',
                names='college',
                hole=0.55,
                color_discrete_sequence=ACCENT_COLORS
            )
            fig_college_donut.update_traces(
                textposition='outside',
                textinfo='label+percent',
                textfont_size=12,
                marker=dict(line=dict(color='#0f1117', width=3))
            )
            fig_college_donut.update_layout(**CHART_LAYOUT, showlegend=False)
            st.plotly_chart(fig_college_donut, use_container_width=True)

        with c6:
            st.markdown("##### Average SGPA by College")
            sorted_college = college_summary.sort_values('avg_sgpa', ascending=True)
            fig_college_bar = go.Figure(go.Bar(
                y=sorted_college['college'],
                x=sorted_college['avg_sgpa'],
                orientation='h',
                marker=dict(
                    color=sorted_college['avg_sgpa'],
                    colorscale=[[0, "#f43f5e"], [0.5, "#f59e0b"], [1, "#10b981"]],
                    line=dict(width=0)
                ),
                text=[f"{v:.2f}" for v in sorted_college['avg_sgpa']],
                textposition='outside',
                textfont=dict(color="#c8ccf0", size=12)
            ))
            fig_college_bar.add_vline(
                x=6.0,
                line_dash="dash",
                line_color="#f43f5e",
                annotation_text="Target 6.0",
                annotation_font_color="#f43f5e"
            )
            fig_college_bar.update_layout(**CHART_LAYOUT, xaxis_title="Avg SGPA", yaxis_title="")
            st.plotly_chart(fig_college_bar, use_container_width=True)

        # Row 5: College SGPA Comparison grouped bar
        st.markdown("##### 🏛️ College SGPA Comparison")
        fig_college_compare = go.Figure()
        for i, row in college_summary.iterrows():
            fig_college_compare.add_trace(go.Bar(
                name=row['college'],
                x=[row['college']],
                y=[row['avg_sgpa']],
                marker_color=ACCENT_COLORS[i % len(ACCENT_COLORS)],
                text=[f"{row['avg_sgpa']:.2f}"],
                textposition='outside',
                textfont=dict(color="#c8ccf0", size=13)
            ))
        fig_college_compare.add_hline(
            y=6.0,
            line_dash="dash",
            line_color="#f43f5e",
            annotation_text="Min Target (6.0)",
            annotation_font_color="#f43f5e",
            annotation_position="top left"
        )
        fig_college_compare.add_hline(
            y=college_summary['avg_sgpa'].mean(),
            line_dash="dot",
            line_color="#f59e0b",
            annotation_text=f"Overall Avg ({college_summary['avg_sgpa'].mean():.2f})",
            annotation_font_color="#f59e0b",
            annotation_position="top right"
        )
        college_compare_layout = {k: v for k, v in CHART_LAYOUT.items() if k not in ('yaxis', 'xaxis', 'legend')}
        college_compare_layout.update(dict(
            barmode='group',
            showlegend=True,
            yaxis=dict(title="Avg SGPA", gridcolor="#2d3154", tickfont=dict(color="#8891b4"), range=[0, 10]),
            xaxis=dict(title="College", gridcolor="#2d3154", linecolor="#2d3154", tickfont=dict(color="#c8ccf0", size=13))
        ))
        fig_college_compare.update_layout(**college_compare_layout)
        st.plotly_chart(fig_college_compare, use_container_width=True)

    elif selected_view == "🔍 Explore Data":

        st.markdown('<div class="section-header">Targeted Search & Filter</div>', unsafe_allow_html=True)

        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("Filtered Students",   len(filtered_df))
        col_info2.metric("Filtered Avg SGPA",   f"{filtered_df['sgp'].mean():.2f}" if not filtered_df.empty else "—")
        col_info3.metric("Filtered Absences",   int(filtered_df['absent'].sum()) if not filtered_df.empty else 0)

        st.markdown("---")

        # SGPA histogram for filtered set
        if not filtered_df.empty:
            fig_hist = px.histogram(
                filtered_df,
                x='sgp',
                nbins=20,
                color_discrete_sequence=["#6366f1"],
                labels={'sgp': 'SGPA', 'count': 'Students'},
                title="SGPA Distribution (Filtered)"
            )
            fig_hist.add_vline(x=6.0, line_dash="dash", line_color="#f43f5e",
                               annotation_text="Min Target (6.0)", annotation_font_color="#f43f5e")
            fig_hist.update_layout(**CHART_LAYOUT, title_font_color="#c8ccf0")
            st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("##### Filtered Student Records")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=400)

    # ─── Records Tab ──────────────────────────────────────────────────────────
    elif selected_view == "📋 Records":

        st.markdown('<div class="section-header">Master Records & Department Rankings</div>', unsafe_allow_html=True)

        left, right = st.columns([1, 2])

        with left:
            st.markdown("##### Department Leaderboard")
            leaderboard = dept_summary[['programme', 'avg_sgpa', 'total_students', 'total_absences']] \
                .sort_values('avg_sgpa', ascending=False) \
                .reset_index(drop=True)
            leaderboard.index += 1
            st.dataframe(
                leaderboard.rename(columns={
                    'programme': 'Department',
                    'avg_sgpa': 'Avg SGPA',
                    'total_students': 'Students',
                    'total_absences': 'Absences'
                }),
                use_container_width=True,
                height=400
            )

        with right:
            st.markdown("##### Full Student Registry")
            search_col1, search_col2 = st.columns(2)
            with search_col1:
                search_name = st.text_input("🔍 Search by Name", placeholder="Type student name…")
            with search_col2:
                search_regno = st.text_input("🔢 Search by Redg. No", placeholder="Type redg. no…")

            display_df = df.copy()
            if search_name:
                display_df = display_df[display_df['Name'].str.contains(search_name, case=False, na=False)]
            if search_regno:
                regno_col = next((c for c in df.columns if 'redg' in c.lower()), None)
                if regno_col:
                    display_df = display_df[display_df[regno_col].astype(str).str.contains(search_regno, case=False, na=False)]
                else:
                    st.warning("⚠️ No redg. no column found in the sheet. Make sure a column with 'redg' in its name exists.")
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)

# ─── Error State ──────────────────────────────────────────────────────────────
except Exception as e:
    st.markdown("""
    <div style="background:#2d1b1b;border:1px solid #7f1d1d;border-radius:16px;padding:32px;text-align:center;margin-top:40px">
        <div style="font-size:48px">🔌</div>
        <h2 style="color:#fca5a5;margin:16px 0 8px">Connection Failed</h2>
        <p style="color:#f87171">Unable to reach the Google Sheet. Check your URL and connection settings.</p>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("🔍 Error Details"):
        st.code(str(e))