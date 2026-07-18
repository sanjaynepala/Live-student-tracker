import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Academic Command Center",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
.stApp { background: linear-gradient(135deg, #0d0f1e 0%, #111827 40%, #1a0a2e 100%); font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #12102b 0%, #0e0c22 100%); border-right: 1px solid rgba(139,92,246,0.3); }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.kpi-card { background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(59,130,246,0.1) 100%); border: 1px solid rgba(139,92,246,0.4); border-radius: 12px; padding: 14px 12px; text-align: center; backdrop-filter: blur(8px); margin-bottom: 6px; }
.kpi-icon { font-size: 22px; margin-bottom: 4px; }
.kpi-label { font-size: 10px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: #a78bfa; margin-bottom: 6px; }
.kpi-value { font-size: 22px; font-weight: 800; color: #ffffff; line-height: 1.1; }
.kpi-delta-good    { font-size: 11px; color: #34d399; margin-top: 4px; font-weight: 600; }
.kpi-delta-bad     { font-size: 11px; color: #f87171; margin-top: 4px; font-weight: 600; }
.kpi-delta-neutral { font-size: 11px; color: #94a3b8; margin-top: 4px; font-weight: 600; }
.section-header { font-size: 19px; font-weight: 800; color: #e2e8f0; border-left: 5px solid #8b5cf6; padding-left: 14px; margin: 28px 0 18px; }
h5, .element-container h5 { color: #c4b5fd !important; font-size: 15px !important; font-weight: 700 !important; }
.stSelectbox > div > div { background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.4); border-radius: 10px; }
.stTextInput > div > div > input { background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.4); border-radius: 10px; color: #e2e8f0; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 4px; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

ACCENT = ["#8b5cf6","#06b6d4","#10b981","#f59e0b","#f43f5e","#a78bfa","#3b82f6","#ec4899"]
BG   = "rgba(0,0,0,0)"
FONT = dict(family="Inter", color="#e2e8f0", size=13)
XDEF = dict(gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
YDEF = dict(gridcolor="rgba(139,92,246,0.15)", tickfont=dict(color="#c4b5fd", size=12))
LEG  = dict(bgcolor="rgba(13,15,30,0.8)", bordercolor="rgba(139,92,246,0.3)", borderwidth=1, font=dict(color="#e2e8f0", size=12))
MARG = dict(t=40, b=40, l=10, r=10)

def base_layout(**extra):
    d = dict(paper_bgcolor=BG, plot_bgcolor=BG, font=FONT, margin=MARG, xaxis=XDEF, yaxis=YDEF, legend=LEG)
    for k, v in extra.items():
        d[k] = v
    return d

def safe_layout(**extra):
    d = dict(paper_bgcolor=BG, plot_bgcolor=BG, font=FONT, margin=MARG, legend=LEG)
    d.update(extra)
    return d

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/17Pl6zv1vg2khQzACApBrNlIUB7ij0bc-LLAigwAhPEc/edit?resourcekey=&gid=1753095568#gid=1753095568"

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:10px 0 6px'><span style='font-size:42px'>🎓</span><h2 style='color:#c4b5fd;margin:6px 0 2px;font-size:18px;font-weight:800'>Academic Hub</h2><p style='color:#7c6fa0;font-size:12px;margin:0'>Powered by Google Sheets</p></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid rgba(139,92,246,0.3);margin:12px 0'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a78bfa;font-size:12px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px'>Navigation</p>", unsafe_allow_html=True)
    selected_view = st.radio("View", ["📊 Overview","📈 Overall Pass Rate","🎓 Avg Campus CGPA","📋 Records"], label_visibility="collapsed")
    st.markdown("<hr style='border:1px solid rgba(139,92,246,0.3);margin:12px 0'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a78bfa;font-size:12px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px'>Filters</p>", unsafe_allow_html=True)
    filter_ph = st.empty()
    st.markdown("<hr style='border:1px solid rgba(139,92,246,0.3);margin:12px 0'>", unsafe_allow_html=True)
    st.info("📡 Live sync every 60 seconds")

st.markdown("<div style='background:linear-gradient(90deg,rgba(139,92,246,0.2),rgba(59,130,246,0.1));border:1px solid rgba(139,92,246,0.35);border-radius:18px;padding:20px 28px;margin-bottom:20px'><div style='display:flex;align-items:center;gap:16px'><span style='font-size:46px'>🏫</span><div><h1 style='color:#fff;margin:0;font-size:26px;font-weight:800'>University Academic Command Center</h1><p style='color:#a78bfa;margin:4px 0 0;font-size:14px'>Real-time academic insights · Google Sheets integration</p></div></div></div>", unsafe_allow_html=True)

def kpi(col, icon, label, value, delta, dtype="neutral"):
    cls = {"good":"kpi-delta-good","bad":"kpi-delta-bad"}.get(dtype,"kpi-delta-neutral")
    arrow = {"good":"▲","bad":"▼"}.get(dtype,"•")
    col.markdown(f'<div class="kpi-card"><div class="kpi-icon">{icon}</div><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="{cls}">{arrow} {delta}</div></div>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    with st.spinner("🔄 Syncing live data..."):
        df = conn.read(spreadsheet=GOOGLE_SHEET_URL, ttl=60)

    # Remove Timestamp column from Google Form responses (always in the first column)
    if 'Timestamp' in df.columns:
        df = df.drop(columns=['Timestamp'])
    
    df.columns = [c.strip() for c in df.columns]
    df['overall sgp'] = pd.to_numeric(df['overall sgp'], errors='coerce')
    
    # Calculate overall SGP from semester CGPAs if missing
    # Detect semester CGPA columns (sem1_cgpa, sem2_cgpa, s1_cgpa, sem1_sgpa, etc.)
    sem_cols = [c for c in df.columns if any(x in c.lower() for x in ['sem', 'sem1', 'sem2', 'sem3', 'sem4', 's1', 's2', 's3', 's4']) 
                and any(x in c.lower() for x in ['cgpa', 'sgpa', 'gpa'])]
    
    # Convert semester columns to numeric
    for col in sem_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill missing overall sgp with average of semester CGPAs
    if sem_cols:
        def calc_overall_sgp(row):
            if pd.isna(row['overall sgp']):
                sem_values = [row[col] for col in sem_cols if not pd.isna(row[col])]
                if sem_values:
                    return round(sum(sem_values) / len(sem_values), 2)
            return row['overall sgp']
        df['overall sgp'] = df.apply(calc_overall_sgp, axis=1)
    
    if 'college' not in df.columns:
        df['college'] = 'N/A'
    df['college'] = df['college'].fillna('N/A').astype(str).str.strip()

    # Normalize result column (Pass/Fail) if it exists
    if 'result' in df.columns:
        df['result'] = df['result'].fillna('N/A').astype(str).str.strip().str.upper()

    import re
    def normalize_text_col(series):
        cleaned = series.astype(str).str.strip().str.upper()
        cleaned = cleaned.str.replace(r'\s+', ' ', regex=True)
        return cleaned.replace({'NAN': 'N/A', '': 'N/A'})

    STUDY_YEAR_MAP = {
        '1': '1ST YEAR', '1ST': '1ST YEAR', '1ST YEAR': '1ST YEAR', 'FIRST': '1ST YEAR',
        'FIRST YEAR': '1ST YEAR', 'YEAR 1': '1ST YEAR', 'I': '1ST YEAR', 'I YEAR': '1ST YEAR',
        '2': '2ND YEAR', '2ND': '2ND YEAR', '2ND YEAR': '2ND YEAR', 'SECOND': '2ND YEAR',
        'SECOND YEAR': '2ND YEAR', 'YEAR 2': '2ND YEAR', 'II': '2ND YEAR', 'II YEAR': '2ND YEAR',
        '3': '3RD YEAR', '3RD': '3RD YEAR', '3RD YEAR': '3RD YEAR', 'THIRD': '3RD YEAR',
        'THIRD YEAR': '3RD YEAR', 'YEAR 3': '3RD YEAR', 'III': '3RD YEAR', 'III YEAR': '3RD YEAR',
        '4': 'FINAL YEAR', '4TH': 'FINAL YEAR', '4TH YEAR': 'FINAL YEAR', 'FOURTH': 'FINAL YEAR',
        'FOURTH YEAR': 'FINAL YEAR', 'YEAR 4': 'FINAL YEAR', 'IV': 'FINAL YEAR', 'IV YEAR': 'FINAL YEAR',
        'FINAL': 'FINAL YEAR', 'FINAL YEAR': 'FINAL YEAR', 'FINALYEAR': 'FINAL YEAR',
    }

    for col in ['programme', 'college']:
        if col in df.columns:
            df[col] = normalize_text_col(df[col])

    if 'study year' in df.columns:
        df['study year'] = normalize_text_col(df['study year'])
        df['study year'] = df['study year'].map(lambda v: STUDY_YEAR_MAP.get(v, v))

    if 'Name' in df.columns:
        df['Name'] = df['Name'].astype(str).str.strip().str.title()

    YEAR_ORDER = ['1ST YEAR', '2ND YEAR', '3RD YEAR', 'FINAL YEAR']
    def year_sort_key(y):
        return YEAR_ORDER.index(y) if y in YEAR_ORDER else len(YEAR_ORDER)

    # Registration-number column (used for Records sorting/search)
    REDG_COL = next((c for c in df.columns if 'redg' in c.lower()), None)

    # ── Sidebar Filters ────────────────────────────────────────────────────────
    with filter_ph.container():
        all_years_unique = sorted(df['study year'].dropna().unique().tolist(), key=year_sort_key)
        all_years = ["All Years"] + all_years_unique
        all_depts = ["All Departments"] + sorted(df['programme'].dropna().unique().tolist())
        sel_year = st.selectbox("Study Year", all_years)
        sel_dept = st.selectbox("Department", all_depts)

    # ── Compute statistics on FILTERED data ─────────────────────────────────────
    fdf = df.copy()
    if sel_year != "All Years":       fdf = fdf[fdf['study year']==sel_year]
    if sel_dept != "All Departments": fdf = fdf[fdf['programme']==sel_dept]

    # Aggregations on filtered data
    dept_s_f = fdf.groupby('programme').agg(
        total_students=('Name','count'),
        avg_sgpa=('overall sgp','mean'),
        pass_count=('overall sgp', lambda x: (x>=6.0).sum())
    ).reset_index()
    dept_s_f['pass_rate'] = (dept_s_f['pass_count']/dept_s_f['total_students']*100).round(1)

    coll_s_f = fdf.groupby('college').agg(
        total_students=('Name','count'),
        avg_sgpa=('overall sgp','mean'),
        pass_count=('overall sgp', lambda x: (x>=6.0).sum())
    ).reset_index()
    coll_s_f['pass_rate'] = (coll_s_f['pass_count']/coll_s_f['total_students']*100).round(1)

    year_s_f = pd.DataFrame()
    if 'study year' in fdf.columns:
        year_s_f = fdf.groupby('study year').agg(
            avg_sgpa=('overall sgp','mean'),
            pass_rate=('overall sgp', lambda x: round((x>=6.0).sum()/len(x)*100,1)),
            total=('Name','count')
        ).reset_index()
        year_s_f = year_s_f.iloc[year_s_f['study year'].map(year_sort_key).argsort()]

    # Filtered statistics
    N_f = len(fdf)
    gcgpa_f = fdf['overall sgp'].mean()
    npass_f = int((fdf['overall sgp']>=6.0).sum())
    prate_f = round(npass_f/N_f*100,1) if N_f>0 else 0

    # At-Risk Students: derived from the 'result' column (Fail) instead of CGPA
    if 'result' in fdf.columns:
        at_risk_f = fdf[fdf['result'].astype(str).str.upper().str.contains('FAIL', na=False)]
    else:
        at_risk_f = fdf[fdf['overall sgp']<6.0]

    top_student_f = fdf.dropna(subset=['overall sgp']).sort_values('overall sgp', ascending=False).iloc[0] if not fdf.dropna(subset=['overall sgp']).empty else None
    top_student_name_f  = top_student_f['Name'] if top_student_f is not None and 'Name' in fdf.columns else "N/A"
    top_student_cgpa_f  = f"{top_student_f['overall sgp']:.2f}" if top_student_f is not None else "N/A"
    top_student_dept_f  = top_student_f['programme'] if top_student_f is not None and 'programme' in fdf.columns else "N/A" 
    top_row_f = dept_s_f.loc[dept_s_f['avg_sgpa'].idxmax()] if not dept_s_f.empty else None
    top_dept_f = top_row_f['programme'] if top_row_f is not None else "N/A"
    top_score_f = f"{top_row_f['avg_sgpa']:.2f}" if top_row_f is not None else "0.00"

    # KPIs
    st.markdown('<div class="section-header">📌 Key Performance Indicators</div>', unsafe_allow_html=True)
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    kpi(k1,"🥇","Top Department",    top_dept_f,              f"CGPA {top_score_f}","good")
    kpi(k2,"📈","Overall Pass Rate", f"{prate_f}%",           f"{npass_f} passed","good")
    kpi(k3,"🎓","Avg Campus CGPA",   f"{gcgpa_f:.2f}" if not pd.isna(gcgpa_f) else "N/A", "Across all programmes","neutral")
    kpi(k4,"👥","Total Students",    N_f,                     f"{fdf['programme'].nunique()} depts","neutral")
    kpi(k5,"🚨","At-Risk Students",  len(at_risk_f),          "Result: Fail","bad")
    kpi(k6,"🌟","Top Student",       top_student_name_f,      f"CGPA {top_student_cgpa_f} · {top_student_dept_f}","good")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── OVERVIEW ─────────────────────────────────────────────────────────────
    if selected_view == "📊 Overview":
        st.markdown(f'<div class="section-header">📊 Department Analytics {f"— {sel_dept}" if sel_dept != "All Departments" else ""} {f"— {sel_year}" if sel_year != "All Years" else ""}</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)

        with c1:
            st.markdown("##### 🥧 Student Enrollment by Department")
            fig = px.pie(dept_s_f, values='total_students', names='programme', color_discrete_sequence=ACCENT)
            fig.update_traces(textposition='inside', textinfo='label+percent', textfont=dict(size=12,color="#fff"), marker=dict(line=dict(color='#0d0f1e',width=2)))
            fig.update_layout(**base_layout(showlegend=True))
            st.plotly_chart(fig, key="pie_dept")

        with c2:
            st.markdown("##### 📊 Avg CGPA by Department")
            sd = dept_s_f.sort_values('avg_sgpa', ascending=True)
            fig2 = go.Figure(go.Bar(y=sd['programme'], x=sd['avg_sgpa'], orientation='h',
                marker=dict(color=sd['avg_sgpa'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"  {v:.2f}" for v in sd['avg_sgpa']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig2.add_vline(x=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig2.update_layout(**safe_layout(
                xaxis=dict(range=[0,10], title="Avg CGPA", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="", **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig2, key="bar_dept_cgpa")

        st.markdown("##### 🔵 CGPA vs Student Count (Scatter)")
        fig3 = px.scatter(dept_s_f, x='avg_sgpa', y='total_students', size='total_students',
            color='programme', text='programme', color_discrete_sequence=ACCENT, size_max=50,
            labels={'avg_sgpa':'Avg CGPA','total_students':'No. of Students'})
        fig3.update_traces(textposition='top center', textfont=dict(color="#e2e8f0",size=11), marker=dict(opacity=0.85, line=dict(width=2,color='#0d0f1e')))
        fig3.add_vline(x=6.0, line_dash="dot", line_color="#f43f5e", annotation_text="CGPA 6.0", annotation_font_color="#f43f5e")
        fig3.update_layout(**base_layout())
        st.plotly_chart(fig3, key="scatter_dept")

        st.markdown('<div class="section-header">🏆 Top Students — Highest CGPA</div>', unsafe_allow_html=True)
        top_n = fdf.dropna(subset=['overall sgp']).sort_values('overall sgp', ascending=False).head(10).reset_index(drop=True)
        top_n.index += 1
        top_cols = [c for c in ['Name','programme','college','study year','overall sgp'] if c in top_n.columns]
        top_display = top_n[top_cols].rename(columns={'programme':'Department','college':'College','study year':'Year','overall sgp':'CGPA'})

        medals = {1:"🥇", 2:"🥈", 3:"🥉"}
        t1, t2, t3 = st.columns(3)
        for col, idx in zip([t1, t2, t3], [1, 2, 3]):
            if idx <= len(top_n):
                row = top_n.iloc[idx-1]
                dept = row.get('programme', 'N/A')
                cgpa = f"{row['overall sgp']:.2f}"
                name = row.get('Name', 'N/A')
                col.markdown(f'<div class="kpi-card"><div class="kpi-icon">{medals[idx]}</div><div class="kpi-label">Rank {idx}</div><div class="kpi-value" style="font-size:20px">{name}</div><div class="kpi-delta-good">CGPA {cgpa}</div><div class="kpi-delta-neutral">{dept}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📋 Top 10 Students by CGPA")
        st.dataframe(top_display, use_container_width=True, hide_index=False, height=320)

        st.markdown('<div class="section-header">🚨 At-Risk Students (Result: Fail)</div>', unsafe_allow_html=True)
        if not at_risk_f.empty:
            cols = [c for c in ['Name','programme','college','result','overall sgp'] if c in at_risk_f.columns]
            st.dataframe(at_risk_f[cols].sort_values('overall sgp').rename(columns={'programme':'Department','college':'College','result':'Result','overall sgp':'CGPA'}), hide_index=True, use_container_width=True, height=280)
        else:
            st.success("🎉 No at-risk students! All students have Result = Pass")

    # ── PASS RATE ─────────────────────────────────────────────────────────────
    elif selected_view == "📈 Overall Pass Rate":
        st.markdown(f'<div class="section-header">📈 Overall Pass Rate Analysis {f"— {sel_dept}" if sel_dept != "All Departments" else ""} {f"— {sel_year}" if sel_year != "All Years" else ""}</div>', unsafe_allow_html=True)
        m1,m2,m3 = st.columns(3)
        kpi(m1,"📈","Overall Pass Rate",f"{prate_f}%",   f"{npass_f} students passed","good")
        kpi(m2,"🚨","Fail Rate",        f"{100-prate_f}%", f"{len(at_risk_f)} below 6.0","bad")
        kpi(m3,"👥","Total Evaluated",  N_f,              "All programmes","neutral")
        st.markdown("<br>", unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("##### 📊 Pass Rate by Department (%)")
            sp = dept_s_f.sort_values('pass_rate', ascending=True)
            fig = go.Figure(go.Bar(y=sp['programme'], x=sp['pass_rate'], orientation='h',
                marker=dict(color=sp['pass_rate'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"  {v:.1f}%" for v in sp['pass_rate']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig.add_vline(x=75, line_dash="dash", line_color="#f59e0b", annotation_text="Target 75%", annotation_font_color="#f59e0b")
            fig.update_layout(**safe_layout(
                xaxis=dict(range=[0,110], title="Pass Rate (%)", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="", **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig, key="bar_pass_dept")

        with c2:
            st.markdown("##### 🥧 Pass vs Fail Distribution")
            fig2 = px.pie(values=[npass_f, len(at_risk_f)], names=["Passed (≥6.0)","Failed (<6.0)"], color_discrete_sequence=["#10b981","#f43f5e"])
            fig2.update_traces(textposition='inside', textinfo='label+percent+value', textfont=dict(size=13,color="#fff"), marker=dict(line=dict(color='#0d0f1e',width=2)))
            fig2.update_layout(**base_layout(showlegend=True))
            st.plotly_chart(fig2, key="pie_pass_fail")

        if not year_s_f.empty:
            st.markdown("##### 📊 Pass Rate by Study Year")
            fig3 = go.Figure(go.Bar(x=year_s_f['study year'].astype(str), y=year_s_f['pass_rate'],
                marker=dict(color=year_s_f['pass_rate'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"{v}%" for v in year_s_f['pass_rate']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig3.add_hline(y=75, line_dash="dash", line_color="#f59e0b", annotation_text="Target 75%", annotation_font_color="#f59e0b")
            fig3.update_layout(**safe_layout(
                xaxis=dict(title="Study Year", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="Pass Rate (%)", range=[0,110], **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig3, key="bar_pass_year")

    # ── CGPA ──────────────────────────────────────────────────────────────────
    elif selected_view == "🎓 Avg Campus CGPA":
        st.markdown(f'<div class="section-header">🎓 Average Campus CGPA Analysis {f"— {sel_dept}" if sel_dept != "All Departments" else ""} {f"— {sel_year}" if sel_year != "All Years" else ""}</div>', unsafe_allow_html=True)
        low_row = dept_s_f.loc[dept_s_f['avg_sgpa'].idxmin()] if not dept_s_f.empty else None
        m1,m2,m3 = st.columns(3)
        kpi(m1,"🎓","Campus Avg CGPA",  f"{gcgpa_f:.2f}" if not pd.isna(gcgpa_f) else "N/A", "All students","neutral")
        kpi(m2,"🥇","Highest Dept CGPA",top_score_f, top_dept_f,"good")
        kpi(m3,"📉","Lowest Dept CGPA", f"{low_row['avg_sgpa']:.2f}" if low_row is not None else "N/A",
            low_row['programme'] if low_row is not None else "N/A","bad")
        st.markdown("<br>", unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("##### 📊 Avg CGPA by Department")
            sc = dept_s_f.sort_values('avg_sgpa', ascending=True)
            fig = go.Figure(go.Bar(y=sc['programme'], x=sc['avg_sgpa'], orientation='h',
                marker=dict(color=sc['avg_sgpa'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"  {v:.2f}" for v in sc['avg_sgpa']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig.add_vline(x=gcgpa_f, line_dash="dot", line_color="#a78bfa", annotation_text=f"Campus Avg {gcgpa_f:.2f}", annotation_font_color="#a78bfa")
            fig.add_vline(x=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig.update_layout(**safe_layout(
                xaxis=dict(range=[0,10], title="Avg CGPA", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="", **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig, key="bar_cgpa_dept")

        with c2:
            st.markdown("##### 🔵 Student CGPA Distribution (Scatter)")
            fig2 = px.scatter(fdf.dropna(subset=['overall sgp']), x='programme', y='overall sgp',
                color='overall sgp', color_continuous_scale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]],
                labels={'overall sgp':'CGPA','programme':'Department'},
                hover_data=['Name'] if 'Name' in fdf.columns else None, opacity=0.75)
            fig2.add_hline(y=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig2.update_layout(**base_layout())
            st.plotly_chart(fig2, key="scatter_cgpa")

        if not year_s_f.empty:
            st.markdown("##### 📊 Avg CGPA by Study Year")
            fig3 = go.Figure(go.Bar(x=year_s_f['study year'].astype(str), y=year_s_f['avg_sgpa'],
                marker=dict(color=year_s_f['avg_sgpa'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"{v:.2f}" for v in year_s_f['avg_sgpa']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig3.add_hline(y=gcgpa_f, line_dash="dot", line_color="#a78bfa", annotation_text=f"Overall Avg {gcgpa_f:.2f}", annotation_font_color="#a78bfa")
            fig3.add_hline(y=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig3.update_layout(**safe_layout(
                xaxis=dict(title="Study Year", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="Avg CGPA", range=[0,10], **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig3, key="bar_cgpa_year")

    # ── RECORDS ───────────────────────────────────────────────────────────────
    elif selected_view == "📋 Records":
        st.markdown('<div class="section-header">📋 Master Records & Department Rankings</div>', unsafe_allow_html=True)
        left, right = st.columns([1,2])

        with left:
            st.markdown("##### 🏆 Department Leaderboard")
            lb = dept_s_f[['programme','avg_sgpa','total_students','pass_rate']].sort_values('avg_sgpa', ascending=False).reset_index(drop=True)
            lb.index += 1
            st.dataframe(lb.rename(columns={'programme':'Department','avg_sgpa':'Avg CGPA','total_students':'Students','pass_rate':'Pass Rate %'}), use_container_width=True, height=420)

        with right:
            st.markdown("##### 📂 Full Student Registry")
            s1,s2 = st.columns(2)
            with s1: sname  = st.text_input("🔍 Search by Name",     placeholder="Type student name…")
            with s2: sregno = st.text_input("🔢 Search by Redg. No", placeholder="Type redg. no…")
            ddf = fdf.copy()
            if sname:  ddf = ddf[ddf['Name'].str.contains(sname, case=False, na=False)]
            if sregno:
                if REDG_COL: ddf = ddf[ddf[REDG_COL].astype(str).str.contains(sregno, case=False, na=False)]
                else:        st.warning("⚠️ No redg. no column found.")
            # When a specific department is selected, sort the registry by Redg. No.
            if sel_dept != "All Departments" and REDG_COL:
                ddf = ddf.sort_values(REDG_COL, na_position='last')
            st.dataframe(ddf, use_container_width=True, hide_index=True, height=420)

except Exception as e:
    st.markdown('<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.4);border-radius:18px;padding:36px;text-align:center;margin-top:40px"><div style="font-size:52px">🔌</div><h2 style="color:#fca5a5;margin:16px 0 8px;font-size:22px">Connection Failed</h2><p style="color:#f87171;font-size:15px">Unable to reach the Google Sheet.</p></div>', unsafe_allow_html=True)
    with st.expander("🔍 Error Details"):
        st.code(str(e))
