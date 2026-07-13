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
.kpi-card { background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(59,130,246,0.1) 100%); border: 1px solid rgba(139,92,246,0.4); border-radius: 18px; padding: 22px 18px; text-align: center; backdrop-filter: blur(8px); margin-bottom: 8px; }
.kpi-icon { font-size: 26px; margin-bottom: 6px; }
.kpi-label { font-size: 11px; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase; color: #a78bfa; margin-bottom: 10px; }
.kpi-value { font-size: 30px; font-weight: 800; color: #ffffff; line-height: 1.1; }
.kpi-delta-good    { font-size: 12px; color: #34d399; margin-top: 8px; font-weight: 600; }
.kpi-delta-bad     { font-size: 12px; color: #f87171; margin-top: 8px; font-weight: 600; }
.kpi-delta-neutral { font-size: 12px; color: #94a3b8; margin-top: 8px; font-weight: 600; }
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

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1c_SFKeTPoFWCvF38iNKdI4qbl16BU6sNRqJVj9DsaE4/edit?gid=0#gid=0"

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

    df.columns = [c.strip() for c in df.columns]
    df['sgp'] = pd.to_numeric(df['sgp'], errors='coerce')
    if 'college' not in df.columns:
        df['college'] = 'N/A'
    df['college'] = df['college'].fillna('N/A').astype(str).str.strip()

    dept_s = df.groupby('programme').agg(
        total_students=('Name','count'),
        avg_sgpa=('sgp','mean'),
        pass_count=('sgp', lambda x: (x>=6.0).sum())
    ).reset_index()
    dept_s['pass_rate'] = (dept_s['pass_count']/dept_s['total_students']*100).round(1)

    coll_s = df.groupby('college').agg(
        total_students=('Name','count'),
        avg_sgpa=('sgp','mean'),
        pass_count=('sgp', lambda x: (x>=6.0).sum())
    ).reset_index()
    coll_s['pass_rate'] = (coll_s['pass_count']/coll_s['total_students']*100).round(1)

    year_s = pd.DataFrame()
    if 'study year' in df.columns:
        year_s = df.groupby('study year').agg(
            avg_sgpa=('sgp','mean'),
            pass_rate=('sgp', lambda x: round((x>=6.0).sum()/len(x)*100,1)),
            total=('Name','count')
        ).reset_index().sort_values('study year')

    N = len(df)
    gcgpa = df['sgp'].mean()
    npass = int((df['sgp']>=6.0).sum())
    prate = round(npass/N*100,1) if N>0 else 0
    at_risk = df[df['sgp']<6.0]
    top_row = dept_s.loc[dept_s['avg_sgpa'].idxmax()] if not dept_s.empty else None
    top_dept = top_row['programme'] if top_row is not None else "N/A"
    top_score = f"{top_row['avg_sgpa']:.2f}" if top_row is not None else "0.00"

    with filter_ph.container():
        all_years = ["All Years"] + sorted(df['study year'].dropna().unique().tolist())
        all_depts = ["All Departments"] + sorted(df['programme'].dropna().unique().tolist())
        sel_year = st.selectbox("Study Year", all_years)
        sel_dept = st.selectbox("Department", all_depts)

    fdf = df.copy()
    if sel_year != "All Years":       fdf = fdf[fdf['study year']==sel_year]
    if sel_dept != "All Departments": fdf = fdf[fdf['programme']==sel_dept]

    # KPIs
    st.markdown('<div class="section-header">📌 Key Performance Indicators</div>', unsafe_allow_html=True)
    k1,k2,k3,k4,k5 = st.columns(5)
    kpi(k1,"🥇","Top Department",    top_dept,              f"SGPA {top_score}","good")
    kpi(k2,"📈","Overall Pass Rate", f"{prate}%",           f"{npass} passed","good")
    kpi(k3,"🎓","Avg Campus CGPA",   f"{gcgpa:.2f}" if not pd.isna(gcgpa) else "N/A", "Across all programmes","neutral")
    kpi(k4,"👥","Total Students",    N,                     f"{df['programme'].nunique()} depts","neutral")
    kpi(k5,"🚨","At-Risk Students",  len(at_risk),          "SGPA below 6.0","bad")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── OVERVIEW ─────────────────────────────────────────────────────────────
    if selected_view == "📊 Overview":
        st.markdown('<div class="section-header">📊 Department Analytics</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)

        with c1:
            st.markdown("##### 🥧 Student Enrollment by Department")
            fig = px.pie(dept_s, values='total_students', names='programme', color_discrete_sequence=ACCENT)
            fig.update_traces(textposition='inside', textinfo='label+percent', textfont=dict(size=12,color="#fff"), marker=dict(line=dict(color='#0d0f1e',width=2)))
            fig.update_layout(**base_layout(showlegend=True))
            st.plotly_chart(fig, key="pie_dept")

        with c2:
            st.markdown("##### 📊 Avg SGPA by Department")
            sd = dept_s.sort_values('avg_sgpa', ascending=True)
            fig2 = go.Figure(go.Bar(y=sd['programme'], x=sd['avg_sgpa'], orientation='h',
                marker=dict(color=sd['avg_sgpa'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"  {v:.2f}" for v in sd['avg_sgpa']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig2.add_vline(x=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig2.update_layout(**safe_layout(
                xaxis=dict(range=[0,10], title="Avg SGPA", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="", **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig2, key="bar_dept_sgpa")

        c3,c4 = st.columns(2)
        with c3:
            st.markdown("##### 🔵 SGPA vs Student Count (Scatter)")
            fig3 = px.scatter(dept_s, x='avg_sgpa', y='total_students', size='total_students',
                color='programme', text='programme', color_discrete_sequence=ACCENT, size_max=50,
                labels={'avg_sgpa':'Avg SGPA','total_students':'No. of Students'})
            fig3.update_traces(textposition='top center', textfont=dict(color="#e2e8f0",size=11), marker=dict(opacity=0.85, line=dict(width=2,color='#0d0f1e')))
            fig3.add_vline(x=6.0, line_dash="dot", line_color="#f43f5e", annotation_text="SGPA 6.0", annotation_font_color="#f43f5e")
            fig3.update_layout(**base_layout())
            st.plotly_chart(fig3, key="scatter_dept")

        with c4:
            st.markdown("##### 📊 College SGPA Comparison")
            fig4 = go.Figure(go.Bar(x=coll_s['college'], y=coll_s['avg_sgpa'],
                marker=dict(color=ACCENT[:len(coll_s)], line=dict(width=0)),
                text=[f"{v:.2f}" for v in coll_s['avg_sgpa']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig4.add_hline(y=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig4.add_hline(y=coll_s['avg_sgpa'].mean(), line_dash="dot", line_color="#f59e0b",
                annotation_text=f"Avg {coll_s['avg_sgpa'].mean():.2f}", annotation_font_color="#f59e0b", annotation_position="top right")
            fig4.update_layout(**safe_layout(
                xaxis=dict(title="College", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="Avg SGPA", range=[0,10], **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig4, key="bar_college_sgpa")

        st.markdown('<div class="section-header">🗺️ SGPA Heatmap — Department vs College</div>', unsafe_allow_html=True)
        heat = df.groupby(['programme','college'])['sgp'].mean().unstack(fill_value=0).round(2)
        fig5 = go.Figure(go.Heatmap(z=heat.values, x=heat.columns.tolist(), y=heat.index.tolist(),
            colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]],
            text=heat.values.round(2), texttemplate="%{text}", textfont=dict(color="#fff",size=12),
            colorbar=dict(tickfont=dict(color="#c4b5fd"), title=dict(text="SGPA", font=dict(color="#c4b5fd")))))
        fig5.update_layout(**safe_layout(
            xaxis=dict(title="College", **{k:v for k,v in XDEF.items()}),
            yaxis=dict(title="Department", **{k:v for k,v in YDEF.items()})
        ))
        st.plotly_chart(fig5, key="heatmap")

        st.markdown('<div class="section-header">🏆 Top Students — Highest CGPA</div>', unsafe_allow_html=True)
        top_n = df.dropna(subset=['sgp']).sort_values('sgp', ascending=False).head(10).reset_index(drop=True)
        top_n.index += 1
        top_cols = [c for c in ['Name','programme','college','study year','sgp'] if c in top_n.columns]
        top_display = top_n[top_cols].rename(columns={'programme':'Department','college':'College','study year':'Year','sgp':'CGPA'})

        medals = {1:"🥇", 2:"🥈", 3:"🥉"}
        t1, t2, t3 = st.columns(3)
        for col, idx in zip([t1, t2, t3], [1, 2, 3]):
            if idx <= len(top_n):
                row = top_n.iloc[idx-1]
                dept = row.get('programme', 'N/A')
                cgpa = f"{row['sgp']:.2f}"
                name = row.get('Name', 'N/A')
                col.markdown(
                    f'<div class="kpi-card">'
                    f'<div class="kpi-icon">{medals[idx]}</div>'
                    f'<div class="kpi-label">Rank {idx}</div>'
                    f'<div class="kpi-value" style="font-size:20px">{name}</div>'
                    f'<div class="kpi-delta-good">CGPA {cgpa}</div>'
                    f'<div class="kpi-delta-neutral">{dept}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📋 Top 10 Students by CGPA")
        st.dataframe(top_display, use_container_width=True, hide_index=False, height=320)

        st.markdown('<div class="section-header">🚨 At-Risk Students (SGPA &lt; 6.0)</div>', unsafe_allow_html=True)
        if not at_risk.empty:
            cols = [c for c in ['Name','programme','college','sgp'] if c in at_risk.columns]
            st.dataframe(at_risk[cols].sort_values('sgp').rename(columns={'programme':'Department','college':'College','sgp':'SGPA'}), hide_index=True, use_container_width=True, height=280)
        else:
            st.success("🎉 No at-risk students! All students have SGPA ≥ 6.0")

    # ── PASS RATE ─────────────────────────────────────────────────────────────
    elif selected_view == "📈 Overall Pass Rate":
        st.markdown('<div class="section-header">📈 Overall Pass Rate Analysis</div>', unsafe_allow_html=True)
        m1,m2,m3 = st.columns(3)
        kpi(m1,"📈","Overall Pass Rate",f"{prate}%",   f"{npass} students passed","good")
        kpi(m2,"🚨","Fail Rate",        f"{100-prate}%", f"{len(at_risk)} below 6.0","bad")
        kpi(m3,"👥","Total Evaluated",  N,              "All programmes","neutral")
        st.markdown("<br>", unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("##### 📊 Pass Rate by Department (%)")
            sp = dept_s.sort_values('pass_rate', ascending=True)
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
            fig2 = px.pie(values=[npass, len(at_risk)], names=["Passed (≥6.0)","Failed (<6.0)"], color_discrete_sequence=["#10b981","#f43f5e"])
            fig2.update_traces(textposition='inside', textinfo='label+percent+value', textfont=dict(size=13,color="#fff"), marker=dict(line=dict(color='#0d0f1e',width=2)))
            fig2.update_layout(**base_layout(showlegend=True))
            st.plotly_chart(fig2, key="pie_pass_fail")

        if not year_s.empty:
            st.markdown("##### 📊 Pass Rate by Study Year")
            fig3 = go.Figure(go.Bar(x=year_s['study year'].astype(str), y=year_s['pass_rate'],
                marker=dict(color=year_s['pass_rate'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"{v}%" for v in year_s['pass_rate']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig3.add_hline(y=75, line_dash="dash", line_color="#f59e0b", annotation_text="Target 75%", annotation_font_color="#f59e0b")
            fig3.update_layout(**safe_layout(
                xaxis=dict(title="Study Year", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="Pass Rate (%)", range=[0,110], **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig3, key="bar_pass_year")

        st.markdown("##### 📊 Pass Rate by College (%)")
        sc = coll_s.sort_values('pass_rate', ascending=True)
        fig4 = go.Figure(go.Bar(y=sc['college'], x=sc['pass_rate'], orientation='h',
            marker=dict(color=sc['pass_rate'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
            text=[f"  {v:.1f}%" for v in sc['pass_rate']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
        fig4.add_vline(x=75, line_dash="dash", line_color="#f59e0b", annotation_text="Target 75%", annotation_font_color="#f59e0b")
        fig4.update_layout(**safe_layout(
            xaxis=dict(range=[0,110], title="Pass Rate (%)", **{k:v for k,v in XDEF.items()}),
            yaxis=dict(title="", **{k:v for k,v in YDEF.items()})
        ))
        st.plotly_chart(fig4, key="bar_pass_college")

    # ── CGPA ──────────────────────────────────────────────────────────────────
    elif selected_view == "🎓 Avg Campus CGPA":
        st.markdown('<div class="section-header">🎓 Average Campus CGPA Analysis</div>', unsafe_allow_html=True)
        low_row = dept_s.loc[dept_s['avg_sgpa'].idxmin()] if not dept_s.empty else None
        m1,m2,m3 = st.columns(3)
        kpi(m1,"🎓","Campus Avg CGPA",  f"{gcgpa:.2f}" if not pd.isna(gcgpa) else "N/A", "All students","neutral")
        kpi(m2,"🥇","Highest Dept CGPA",top_score, top_dept,"good")
        kpi(m3,"📉","Lowest Dept CGPA", f"{low_row['avg_sgpa']:.2f}" if low_row is not None else "N/A",
            low_row['programme'] if low_row is not None else "N/A","bad")
        st.markdown("<br>", unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("##### 📊 Avg CGPA by Department")
            sc = dept_s.sort_values('avg_sgpa', ascending=True)
            fig = go.Figure(go.Bar(y=sc['programme'], x=sc['avg_sgpa'], orientation='h',
                marker=dict(color=sc['avg_sgpa'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"  {v:.2f}" for v in sc['avg_sgpa']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig.add_vline(x=gcgpa, line_dash="dot", line_color="#a78bfa", annotation_text=f"Campus Avg {gcgpa:.2f}", annotation_font_color="#a78bfa")
            fig.add_vline(x=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig.update_layout(**safe_layout(
                xaxis=dict(range=[0,10], title="Avg CGPA", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="", **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig, key="bar_cgpa_dept")

        with c2:
            st.markdown("##### 🥧 Students by CGPA Band")
            bands = pd.cut(df['sgp'].dropna(), bins=[0,5,6,7,8,10],
                labels=["0–5 (Poor)","5–6 (Below Avg)","6–7 (Average)","7–8 (Good)","8–10 (Excellent)"])
            bc = bands.value_counts().reset_index()
            bc.columns = ['Band','Count']
            fig2 = px.pie(bc, values='Count', names='Band', color_discrete_sequence=["#f43f5e","#f59e0b","#06b6d4","#10b981","#8b5cf6"])
            fig2.update_traces(textposition='inside', textinfo='label+percent', textfont=dict(size=12,color="#fff"), marker=dict(line=dict(color='#0d0f1e',width=2)))
            fig2.update_layout(**base_layout(showlegend=True))
            st.plotly_chart(fig2, key="pie_cgpa_band")

        if not year_s.empty:
            st.markdown("##### 📊 Avg CGPA by Study Year")
            fig3 = go.Figure(go.Bar(x=year_s['study year'].astype(str), y=year_s['avg_sgpa'],
                marker=dict(color=year_s['avg_sgpa'], colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]], line=dict(width=0)),
                text=[f"{v:.2f}" for v in year_s['avg_sgpa']], textposition='outside', textfont=dict(color="#e2e8f0",size=13)))
            fig3.add_hline(y=gcgpa, line_dash="dot", line_color="#a78bfa", annotation_text=f"Overall Avg {gcgpa:.2f}", annotation_font_color="#a78bfa")
            fig3.add_hline(y=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
            fig3.update_layout(**safe_layout(
                xaxis=dict(title="Study Year", **{k:v for k,v in XDEF.items()}),
                yaxis=dict(title="Avg CGPA", range=[0,10], **{k:v for k,v in YDEF.items()})
            ))
            st.plotly_chart(fig3, key="bar_cgpa_year")

        st.markdown("##### 🔵 Student CGPA Distribution (Scatter)")
        fig4 = px.scatter(df.dropna(subset=['sgp']), x='programme', y='sgp',
            color='sgp', color_continuous_scale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]],
            labels={'sgp':'CGPA','programme':'Department'},
            hover_data=['Name'] if 'Name' in df.columns else None, opacity=0.75)
        fig4.add_hline(y=6.0, line_dash="dash", line_color="#f43f5e", annotation_text="Min 6.0", annotation_font_color="#f43f5e")
        fig4.update_layout(**base_layout())
        st.plotly_chart(fig4, key="scatter_cgpa")

    # ── RECORDS ───────────────────────────────────────────────────────────────
    elif selected_view == "📋 Records":
        st.markdown('<div class="section-header">📋 Master Records & Department Rankings</div>', unsafe_allow_html=True)
        left, right = st.columns([1,2])

        with left:
            st.markdown("##### 🏆 Department Leaderboard")
            lb = dept_s[['programme','avg_sgpa','total_students','pass_rate']].sort_values('avg_sgpa', ascending=False).reset_index(drop=True)
            lb.index += 1
            st.dataframe(lb.rename(columns={'programme':'Department','avg_sgpa':'Avg SGPA','total_students':'Students','pass_rate':'Pass Rate %'}), use_container_width=True, height=420)

        with right:
            st.markdown("##### 📂 Full Student Registry")
            s1,s2 = st.columns(2)
            with s1: sname  = st.text_input("🔍 Search by Name",     placeholder="Type student name…")
            with s2: sregno = st.text_input("🔢 Search by Redg. No", placeholder="Type redg. no…")
            ddf = df.copy()
            if sname:  ddf = ddf[ddf['Name'].str.contains(sname, case=False, na=False)]
            if sregno:
                rc = next((c for c in df.columns if 'redg' in c.lower()), None)
                if rc: ddf = ddf[ddf[rc].astype(str).str.contains(sregno, case=False, na=False)]
                else:  st.warning("⚠️ No redg. no column found.")
            st.dataframe(ddf, use_container_width=True, hide_index=True, height=420)

except Exception as e:
    st.markdown('<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.4);border-radius:18px;padding:36px;text-align:center;margin-top:40px"><div style="font-size:52px">🔌</div><h2 style="color:#fca5a5;margin:16px 0 8px;font-size:22px">Connection Failed</h2><p style="color:#f87171;font-size:15px">Unable to reach the Google Sheet.</p></div>', unsafe_allow_html=True)
    with st.expander("🔍 Error Details"):
        st.code(str(e))
