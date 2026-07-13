import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0d0f1e 0%, #111827 40%, #1a0a2e 100%);
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12102b 0%, #0e0c22 100%);
        border-right: 1px solid rgba(139,92,246,0.3);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 15px !important; font-weight: 600; }

    .kpi-card {
        background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(59,130,246,0.1) 100%);
        border: 1px solid rgba(139,92,246,0.4);
        border-radius: 18px;
        padding: 22px 18px;
        text-align: center;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        backdrop-filter: blur(8px);
    }
    .kpi-card:hover { transform: translateY(-5px); box-shadow: 0 12px 32px rgba(139,92,246,0.3); }
    .kpi-icon  { font-size: 26px; margin-bottom: 6px; }
    .kpi-label { font-size: 11px; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase; color: #a78bfa; margin-bottom: 10px; }
    .kpi-value { font-size: 30px; font-weight: 800; color: #ffffff; line-height: 1.1; }
    .kpi-delta-good    { font-size: 12px; color: #34d399; margin-top: 8px; font-weight: 600; }
    .kpi-delta-bad     { font-size: 12px; color: #f87171; margin-top: 8px; font-weight: 600; }
    .kpi-delta-neutral { font-size: 12px; color: #94a3b8; margin-top: 8px; font-weight: 600; }

    .section-header {
        font-size: 19px; font-weight: 800; color: #e2e8f0;
        border-left: 5px solid #8b5cf6; padding-left: 14px;
        margin: 28px 0 18px; letter-spacing: 0.3px;
    }
    h5, .element-container h5 {
        color: #c4b5fd !important; font-size: 15px !important;
        font-weight: 700 !important; letter-spacing: 0.4px; margin-bottom: 4px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(139,92,246,0.12); border-radius: 12px;
        padding: 4px; gap: 4px; border: 1px solid rgba(139,92,246,0.3);
    }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; color: #a78bfa; font-weight: 600; font-size: 14px; padding: 8px 22px; }
    .stTabs [aria-selected="true"] { background: #7c3aed !important; color: white !important; }
    .stDataFrame { border-radius: 14px; overflow: hidden; }
    .stSelectbox > div > div { background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.4); border-radius: 10px; color: #e2e8f0; font-weight: 600; }
    .stTextInput > div > div > input { background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.4); border-radius: 10px; color: #e2e8f0; font-size: 14px; }
    .stAlert { border-radius: 12px; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0d0f1e; }
    ::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 4px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Plotly theme ──────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0", size=13),
    margin=dict(t=40, b=40, l=10, r=10),
    xaxis=dict(gridcolor="rgba(139,92,246,0.15)", linecolor="rgba(139,92,246,0.2)", tickfont=dict(color="#c4b5fd", size=12)),
    yaxis=dict(gridcolor="rgba(139,92,246,0.15)", linecolor="rgba(139,92,246,0.2)", tickfont=dict(color="#c4b5fd", size=12)),
    legend=dict(bgcolor="rgba(13,15,30,0.8)", bordercolor="rgba(139,92,246,0.3)", borderwidth=1, font=dict(color="#e2e8f0", size=12))
)
ACCENT_COLORS = ["#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e", "#a78bfa", "#3b82f6", "#ec4899"]

def safe_layout(exclude=('xaxis','yaxis'), **extra):
    layout = {k: v for k, v in CHART_LAYOUT.items() if k not in exclude}
    layout.update(extra)
    return layout

# ─── Google Sheet URL ──────────────────────────────────────────────────────────
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1IfhxtNcnHGr4ue1vYDngmRzUdJ02ucPIqjCVHbgL5j8/edit?usp=sharing"

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:10px 0 6px'>"
        "<span style='font-size:42px'>🎓</span>"
        "<h2 style='color:#c4b5fd;margin:6px 0 2px;font-size:18px;font-weight:800'>Academic Hub</h2>"
        "<p style='color:#7c6fa0;font-size:12px;margin:0'>Powered by Google Sheets</p></div>",
        unsafe_allow_html=True
    )
    st.markdown("<hr style='border:1px solid rgba(139,92,246,0.3);margin:12px 0'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a78bfa;font-size:12px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px'>Navigation</p>", unsafe_allow_html=True)
    selected_view = st.radio(
        label="View",
        options=["📊 Overview", "📈 Overall Pass Rate", "🎓 Avg Campus CGPA", "📋 Records"],
        label_visibility="collapsed"
    )
    st.markdown("<hr style='border:1px solid rgba(139,92,246,0.3);margin:12px 0'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a78bfa;font-size:12px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px'>Filters</p>", unsafe_allow_html=True)
    sidebar_filter_placeholder = st.empty()
    st.markdown("<hr style='border:1px solid rgba(139,92,246,0.3);margin:12px 0'>", unsafe_allow_html=True)
    st.info("📡 Live sync every 60 seconds", icon="ℹ️")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='background:linear-gradient(90deg,rgba(139,92,246,0.2) 0%,rgba(59,130,246,0.1) 100%);"
    "border:1px solid rgba(139,92,246,0.35);border-radius:18px;padding:20px 28px;margin-bottom:20px'>"
    "<div style='display:flex;align-items:center;gap:16px'>"
    "<span style='font-size:46px'>🏫</span><div>"
    "<h1 style='color:#ffffff;margin:0;font-size:26px;font-weight:800;letter-spacing:-0.5px'>University Academic Command Center</h1>"
    "<p style='color:#a78bfa;margin:4px 0 0;font-size:14px;font-weight:500'>Real-time academic insights · Google Sheets integration</p>"
    "</div></div></div>",
    unsafe_allow_html=True
)

# ─── Data Load ────────────────────────────────────────────────────────────────
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    with st.spinner("🔄 Syncing live data..."):
        df = conn.read(spreadsheet=GOOGLE_SHEET_URL, ttl=60)

    df.columns = [col.strip() for col in df.columns]
    df['sgp'] = pd.to_numeric(df['sgp'], errors='coerce')
    if 'college' not in df.columns:
        df['college'] = 'N/A'
    df['college'] = df['college'].fillna('N/A').astype(str).str.strip()

    # ─── Aggregations ─────────────────────────────────────────────────────────
    dept_summary = df.groupby('programme').agg(
        total_students=('Name',  'count'),
        avg_sgpa      =('sgp',   'mean'),
        pass_count    =('sgp',   lambda x: (x >= 6.0).sum())
    ).reset_index()
    dept_summary['pass_rate'] = (dept_summary['pass_count'] / dept_summary['total_students'] * 100).round(1)

    college_summary = df.groupby('college').agg(
        total_students=('Name', 'count'),
        avg_sgpa      =('sgp',  'mean'),
        pass_count    =('sgp',  lambda x: (x >= 6.0).sum())
    ).reset_index()
    college_summary['pass_rate'] = (college_summary['pass_count'] / college_summary['total_students'] * 100).round(1)

    # Year-wise trend (for line chart)
    if 'study year' in df.columns:
        year_summary = df.groupby('study year').agg(
            avg_sgpa  =('sgp', 'mean'),
            pass_rate =('sgp', lambda x: round((x >= 6.0).sum() / len(x) * 100, 1)),
            total     =('Name','count')
        ).reset_index().sort_values('study year')
    else:
        year_summary = pd.DataFrame()

    total_students     = len(df)
    global_avg_cgpa    = df['sgp'].mean()
    overall_pass_count = int((df['sgp'] >= 6.0).sum())
    overall_pass_rate  = round(overall_pass_count / total_students * 100, 1) if total_students > 0 else 0
    at_risk            = df[df['sgp'] < 6.0]

    top_dept_row   = dept_summary.loc[dept_summary['avg_sgpa'].idxmax()] if not dept_summary.empty else None
    top_dept       = top_dept_row['programme'] if top_dept_row is not None else "N/A"
    top_dept_score = f"{top_dept_row['avg_sgpa']:.2f}" if top_dept_row is not None else "0.00"

    # ─── Sidebar filters (only Year + Department) ──────────────────────────────
    with sidebar_filter_placeholder.container():
        all_years = ["All Years"] + sorted(df['study year'].dropna().unique().tolist())
        all_depts = ["All Departments"] + sorted(df['programme'].dropna().unique().tolist())
        selected_year = st.selectbox("Study Year",  all_years)
        selected_dept = st.selectbox("Department",  all_depts)

    filtered_df = df.copy()
    if selected_year != "All Years":       filtered_df = filtered_df[filtered_df['study year'] == selected_year]
    if selected_dept != "All Departments": filtered_df = filtered_df[filtered_df['programme']  == selected_dept]

    # ─── KPI Row ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📌 Key Performance Indicators</div>', unsafe_allow_html=True)

    def kpi_card(col, icon, label, value, delta, delta_type="neutral"):
        delta_class = {"good": "kpi-delta-good", "bad": "kpi-delta-bad"}.get(delta_type, "kpi-delta-neutral")
        arrow = {"good": "▲", "bad": "▼"}.get(delta_type, "•")
        col.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_class}">{arrow} {delta}</div>
        </div>""", unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_card(k1, "🥇", "Top Department",    top_dept,                                                              f"SGPA {top_dept_score}",         "good")
    kpi_card(k2, "📈", "Overall Pass Rate", f"{overall_pass_rate}%",                                               f"{overall_pass_count} passed",   "good")
    kpi_card(k3, "🎓", "Avg Campus CGPA",   f"{global_avg_cgpa:.2f}" if not pd.isna(global_avg_cgpa) else "N/A",  "Across all programmes",          "neutral")
    kpi_card(k4, "👥", "Total Students",    total_students,                                                        f"{df['programme'].nunique()} depts", "neutral")
    kpi_card(k5, "🚨", "At-Risk Students",  len(at_risk),                                                          "SGPA below 6.0",                 "bad")
    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  OVERVIEW
    # ══════════════════════════════════════════════════════════════════════════
    if selected_view == "📊 Overview":
        st.markdown('<div class="section-header">📊 Department Analytics</div>', unsafe_allow_html=True)

        # Row 1 — Pie + Bar
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🥧 Student Enrollment by Department")
            fig_pie = px.pie(dept_summary, values='total_students', names='programme',
                             color_discrete_sequence=ACCENT_COLORS)
            fig_pie.update_traces(
                textposition='inside', textinfo='label+percent',
                textfont=dict(size=12, color="#ffffff"),
                marker=dict(line=dict(color='#0d0f1e', width=2))
            )
            fig_pie.update_layout(**CHART_LAYOUT, showlegend=True)
            st.plotly_chart(fig_pie, width='stretch', key="fig_pie")

        with c2:
            st.markdown("##### 📊 Average SGPA by Department")
            sorted_dept = dept_summary.sort_values('avg_sgpa', ascending=True)
            fig_hbar = go.Figure(go.Bar(
                y=sorted_dept['programme'], x=sorted_dept['avg_sgpa'], orientation='h',
                marker=dict(color=sorted_dept['avg_sgpa'],
                            colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"  {v:.2f}" for v in sorted_dept['avg_sgpa']],
                textposition='outside', textfont=dict(color="#e2e8f0", size=13)
            ))
            fig_hbar.add_vline(x=6.0, line_dash="dash", line_color="#f43f5e",
                               annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig_hbar.update_layout(**safe_layout(
                xaxis=dict(range=[0,10], title="Avg SGPA", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12)),
                yaxis=dict(title="", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
            ))
            st.plotly_chart(fig_hbar, width='stretch', key="fig_hbar")

        # Row 2 — Scatter (SGPA vs Students per dept) + College bar
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("##### 🔵 SGPA vs Student Count (Scatter)")
            fig_scatter = px.scatter(
                dept_summary, x='avg_sgpa', y='total_students',
                size='total_students', color='programme', text='programme',
                color_discrete_sequence=ACCENT_COLORS,
                labels={'avg_sgpa':'Avg SGPA','total_students':'No. of Students','programme':'Department'},
                size_max=50
            )
            fig_scatter.update_traces(textposition='top center', textfont=dict(color="#e2e8f0", size=11),
                                      marker=dict(opacity=0.85, line=dict(width=2, color='#0d0f1e')))
            fig_scatter.add_vline(x=6.0, line_dash="dot", line_color="#f43f5e",
                                  annotation_text="SGPA 6.0", annotation_font_color="#f43f5e")
            fig_scatter.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig_scatter, width='stretch', key="fig_scatter")

        with c4:
            st.markdown("##### 📊 College SGPA Comparison")
            fig_college_bar = go.Figure(go.Bar(
                x=college_summary['college'], y=college_summary['avg_sgpa'],
                marker=dict(color=ACCENT_COLORS[:len(college_summary)], line=dict(width=0)),
                text=[f"{v:.2f}" for v in college_summary['avg_sgpa']],
                textposition='outside', textfont=dict(color="#e2e8f0", size=13)
            ))
            fig_college_bar.add_hline(y=6.0, line_dash="dash", line_color="#f43f5e",
                                      annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig_college_bar.add_hline(y=college_summary['avg_sgpa'].mean(), line_dash="dot",
                                      line_color="#f59e0b",
                                      annotation_text=f"Avg {college_summary['avg_sgpa'].mean():.2f}",
                                      annotation_font_color="#f59e0b", annotation_position="top right")
            fig_college_bar.update_layout(**safe_layout(
                xaxis=dict(title="College", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12)),
                yaxis=dict(title="Avg SGPA", range=[0,10], gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
            ))
            st.plotly_chart(fig_college_bar, width='stretch', key="fig_college_bar")

        # Row 3 — Heatmap dept × college SGPA
        st.markdown('<div class="section-header">🗺️ SGPA Heatmap — Department vs College</div>', unsafe_allow_html=True)
        if 'college' in df.columns:
            heat_data = df.groupby(['programme','college'])['sgp'].mean().unstack(fill_value=0).round(2)
            fig_heat = go.Figure(go.Heatmap(
                z=heat_data.values,
                x=heat_data.columns.tolist(),
                y=heat_data.index.tolist(),
                colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]],
                text=heat_data.values.round(2),
                texttemplate="%{text}",
                textfont=dict(color="#ffffff", size=12),
                hovertemplate="Dept: %{y}<br>College: %{x}<br>Avg SGPA: %{z}<extra></extra>",
                showscale=True,
                colorbar=dict(tickfont=dict(color="#c4b5fd"), title=dict(text="SGPA", font=dict(color="#c4b5fd")))
            ))
            fig_heat.update_layout(**safe_layout(
                xaxis=dict(title="College", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12)),
                yaxis=dict(title="Department", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
            ))
            st.plotly_chart(fig_heat, width='stretch', key="fig_heat")

        # At-Risk table
        st.markdown('<div class="section-header">🚨 At-Risk Students (SGPA &lt; 6.0)</div>', unsafe_allow_html=True)
        if not at_risk.empty:
            display_cols = [c for c in ['Name','programme','college','sgp'] if c in at_risk.columns]
            st.dataframe(
                at_risk[display_cols].sort_values('sgp')
                  .rename(columns={'programme':'Department','college':'College','sgp':'SGPA'}),
                hide_index=True, width='stretch', height=280
            )
        else:
            st.success("🎉 No at-risk students! All students have SGPA ≥ 6.0")

    # ══════════════════════════════════════════════════════════════════════════
    #  OVERALL PASS RATE
    # ══════════════════════════════════════════════════════════════════════════
    elif selected_view == "📈 Overall Pass Rate":
        st.markdown('<div class="section-header">📈 Overall Pass Rate Analysis</div>', unsafe_allow_html=True)

        # Summary metric cards
        m1, m2, m3 = st.columns(3)
        kpi_card(m1, "📈", "Overall Pass Rate", f"{overall_pass_rate}%",    f"{overall_pass_count} students passed", "good")
        kpi_card(m2, "🚨", "Fail Rate",         f"{100-overall_pass_rate}%", f"{len(at_risk)} students below 6.0",   "bad")
        kpi_card(m3, "👥", "Total Evaluated",   total_students,              "All programmes",                        "neutral")
        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            # Bar — pass rate by department
            st.markdown("##### 📊 Pass Rate by Department (%)")
            sorted_pass = dept_summary.sort_values('pass_rate', ascending=True)
            fig_pass_bar = go.Figure(go.Bar(
                y=sorted_pass['programme'], x=sorted_pass['pass_rate'], orientation='h',
                marker=dict(color=sorted_pass['pass_rate'],
                            colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"  {v:.1f}%" for v in sorted_pass['pass_rate']],
                textposition='outside', textfont=dict(color="#e2e8f0", size=13)
            ))
            fig_pass_bar.add_vline(x=75, line_dash="dash", line_color="#f59e0b",
                                   annotation_text="Target 75%", annotation_font_color="#f59e0b")
            fig_pass_bar.update_layout(**safe_layout(
                xaxis=dict(range=[0,110], title="Pass Rate (%)", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12)),
                yaxis=dict(title="", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
            ))
            st.plotly_chart(fig_pass_bar, width='stretch', key="fig_pass_bar")

        with c2:
            # Pie — pass vs fail overall
            st.markdown("##### 🥧 Pass vs Fail Distribution")
            fig_pf_pie = px.pie(
                values=[overall_pass_count, len(at_risk)],
                names=["Passed (≥6.0)", "Failed (<6.0)"],
                color_discrete_sequence=["#10b981", "#f43f5e"]
            )
            fig_pf_pie.update_traces(
                textposition='inside', textinfo='label+percent+value',
                textfont=dict(size=13, color="#ffffff"),
                marker=dict(line=dict(color='#0d0f1e', width=2))
            )
            fig_pf_pie.update_layout(**CHART_LAYOUT, showlegend=True)
            st.plotly_chart(fig_pf_pie, width='stretch', key="fig_pf_pie")

        # Bar — pass rate by year
        if not year_summary.empty:
            st.markdown("##### 📊 Pass Rate by Study Year")
            fig_year_pass = go.Figure(go.Bar(
                x=year_summary['study year'].astype(str), y=year_summary['pass_rate'],
                marker=dict(
                    color=year_summary['pass_rate'],
                    colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)
                ),
                text=[f"{v}%" for v in year_summary['pass_rate']],
                textposition='outside', textfont=dict(color="#e2e8f0", size=13)
            ))
            fig_year_pass.add_hline(y=75, line_dash="dash", line_color="#f59e0b",
                                    annotation_text="Target 75%", annotation_font_color="#f59e0b")
            fig_year_pass.update_layout(**safe_layout(
                xaxis=dict(title="Study Year", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12)),
                yaxis=dict(title="Pass Rate (%)", range=[0,110], gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
            ))
            st.plotly_chart(fig_year_pass, width='stretch', key="fig_year_pass")

        # Bar — pass rate by college
        st.markdown("##### 📊 Pass Rate by College (%)")
        sorted_cpass = college_summary.sort_values('pass_rate', ascending=True)
        fig_cpass = go.Figure(go.Bar(
            y=sorted_cpass['college'], x=sorted_cpass['pass_rate'], orientation='h',
            marker=dict(color=sorted_cpass['pass_rate'],
                        colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
            text=[f"  {v:.1f}%" for v in sorted_cpass['pass_rate']],
            textposition='outside', textfont=dict(color="#e2e8f0", size=13)
        ))
        fig_cpass.add_vline(x=75, line_dash="dash", line_color="#f59e0b",
                            annotation_text="Target 75%", annotation_font_color="#f59e0b")
        fig_cpass.update_layout(**safe_layout(
            xaxis=dict(range=[0,110], title="Pass Rate (%)", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12)),
            yaxis=dict(title="", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
        ))
        st.plotly_chart(fig_cpass, width='stretch', key="fig_cpass")

    # ══════════════════════════════════════════════════════════════════════════
    #  AVG CAMPUS CGPA
    # ══════════════════════════════════════════════════════════════════════════
    elif selected_view == "🎓 Avg Campus CGPA":
        st.markdown('<div class="section-header">🎓 Average Campus CGPA Analysis</div>', unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        kpi_card(m1, "🎓", "Campus Avg CGPA",   f"{global_avg_cgpa:.2f}" if not pd.isna(global_avg_cgpa) else "N/A", "All students", "neutral")
        kpi_card(m2, "🥇", "Highest Dept CGPA", top_dept_score,                                                         top_dept,       "good")
        kpi_card(m3, "📉", "Lowest Dept CGPA",
                 f"{dept_summary['avg_sgpa'].min():.2f}" if not dept_summary.empty else "N/A",
                 dept_summary.loc[dept_summary['avg_sgpa'].idxmin(),'programme'] if not dept_summary.empty else "N/A",
                 "bad")
        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            # Bar — avg CGPA by dept
            st.markdown("##### 📊 Avg CGPA by Department")
            sorted_cgpa = dept_summary.sort_values('avg_sgpa', ascending=True)
            fig_cgpa_bar = go.Figure(go.Bar(
                y=sorted_cgpa['programme'], x=sorted_cgpa['avg_sgpa'], orientation='h',
                marker=dict(color=sorted_cgpa['avg_sgpa'],
                            colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"  {v:.2f}" for v in sorted_cgpa['avg_sgpa']],
                textposition='outside', textfont=dict(color="#e2e8f0", size=13)
            ))
            fig_cgpa_bar.add_vline(x=global_avg_cgpa, line_dash="dot", line_color="#a78bfa",
                                   annotation_text=f"Campus Avg {global_avg_cgpa:.2f}",
                                   annotation_font_color="#a78bfa")
            fig_cgpa_bar.add_vline(x=6.0, line_dash="dash", line_color="#f43f5e",
                                   annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig_cgpa_bar.update_layout(**safe_layout(
                xaxis=dict(range=[0,10], title="Avg CGPA", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12)),
                yaxis=dict(title="", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
            ))
            st.plotly_chart(fig_cgpa_bar, width='stretch', key="fig_cgpa_bar")

        with c2:
            # Pie — student distribution by CGPA band
            st.markdown("##### 🥧 Students by CGPA Band")
            bands = pd.cut(df['sgp'].dropna(), bins=[0,5,6,7,8,10],
                           labels=["0–5 (Poor)","5–6 (Below Avg)","6–7 (Average)","7–8 (Good)","8–10 (Excellent)"])
            band_counts = bands.value_counts().reset_index()
            band_counts.columns = ['Band','Count']
            fig_band_pie = px.pie(band_counts, values='Count', names='Band',
                                  color_discrete_sequence=["#f43f5e","#f59e0b","#06b6d4","#10b981","#8b5cf6"])
            fig_band_pie.update_traces(
                textposition='inside', textinfo='label+percent',
                textfont=dict(size=12, color="#ffffff"),
                marker=dict(line=dict(color='#0d0f1e', width=2))
            )
            fig_band_pie.update_layout(**CHART_LAYOUT, showlegend=True)
            st.plotly_chart(fig_band_pie, width='stretch', key="fig_band_pie")

        # Bar — avg CGPA by year
        if not year_summary.empty:
            st.markdown("##### 📊 Avg CGPA by Study Year")
            fig_year_cgpa = go.Figure(go.Bar(
                x=year_summary['study year'].astype(str), y=year_summary['avg_sgpa'],
                marker=dict(
                    color=year_summary['avg_sgpa'],
                    colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)
                ),
                text=[f"{v:.2f}" for v in year_summary['avg_sgpa']],
                textposition='outside', textfont=dict(color="#e2e8f0", size=13)
            ))
            fig_year_cgpa.add_hline(y=global_avg_cgpa, line_dash="dot", line_color="#a78bfa",
                                    annotation_text=f"Overall Avg {global_avg_cgpa:.2f}",
                                    annotation_font_color="#a78bfa")
            fig_year_cgpa.add_hline(y=6.0, line_dash="dash", line_color="#f43f5e",
                                    annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig_year_cgpa.update_layout(**safe_layout(
                xaxis=dict(title="Study Year", gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12)),
                yaxis=dict(title="Avg CGPA", range=[0,10], gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
            ))
            st.plotly_chart(fig_year_cgpa, width='stretch', key="fig_year_cgpa")

        # Scatter — per-student CGPA scatter
        st.markdown("##### 🔵 Student CGPA Distribution (Scatter)")
        fig_stu_scatter = px.scatter(
            df.dropna(subset=['sgp']), x='programme', y='sgp',
            color='sgp', color_continuous_scale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]],
            labels={'sgp':'CGPA','programme':'Department'},
            hover_data=['Name'] if 'Name' in df.columns else None,
            opacity=0.75
        )
        fig_stu_scatter.add_hline(y=6.0, line_dash="dash", line_color="#f43f5e",
                                  annotation_text="Min 6.0", annotation_font_color="#f43f5e")
        fig_stu_scatter.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_stu_scatter, width='stretch', key="fig_stu_scatter")

    # ══════════════════════════════════════════════════════════════════════════
    #  RECORDS
    # ══════════════════════════════════════════════════════════════════════════
    elif selected_view == "📋 Records":
        st.markdown('<div class="section-header">📋 Master Records & Department Rankings</div>', unsafe_allow_html=True)

        left, right = st.columns([1, 2])
        with left:
            st.markdown("##### 🏆 Department Leaderboard")
            leaderboard = dept_summary[['programme','avg_sgpa','total_students','pass_rate']] \
                .sort_values('avg_sgpa', ascending=False).reset_index(drop=True)
            leaderboard.index += 1
            st.dataframe(
                leaderboard.rename(columns={'programme':'Department','avg_sgpa':'Avg SGPA',
                                            'total_students':'Students','pass_rate':'Pass Rate %'}),
                width='stretch', height=420
            )

        with right:
            st.markdown("##### 📂 Full Student Registry")
            sc1, sc2 = st.columns(2)
            with sc1:
                search_name = st.text_input("🔍 Search by Name", placeholder="Type student name…")
            with sc2:
                search_regno = st.text_input("🔢 Search by Redg. No", placeholder="Type redg. no…")

            display_df = df.copy()
            if search_name:
                display_df = display_df[display_df['Name'].str.contains(search_name, case=False, na=False)]
            if search_regno:
                regno_col = next((c for c in df.columns if 'redg' in c.lower()), None)
                if regno_col:
                    display_df = display_df[display_df[regno_col].astype(str).str.contains(search_regno, case=False, na=False)]
                else:
                    st.warning("⚠️ No redg. no column found. Make sure a column with 'redg' in its name exists.")
            st.dataframe(display_df, width='stretch', hide_index=True, height=420)

# ─── Error State ──────────────────────────────────────────────────────────────
except Exception as e:
    st.markdown("""
    <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.4);
    border-radius:18px;padding:36px;text-align:center;margin-top:40px">
        <div style="font-size:52px">🔌</div>
        <h2 style="color:#fca5a5;margin:16px 0 8px;font-size:22px">Connection Failed</h2>
        <p style="color:#f87171;font-size:15px">Unable to reach the Google Sheet. Check your URL and connection settings.</p>
    </div>""", unsafe_allow_html=True)
    with st.expander("🔍 Error Details"):
        st.code(str(e))
