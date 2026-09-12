# -*- coding: utf-8 -*-
"""
Robot Posture Validation
------------------------------------------------------------
UI polish pass only.
The kinematics and validation logic are UNCHANGED: same reference posture,
same tolerance, same forward-kinematics maths, same per-joint checks.
"""
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Robot Posture Checker", page_icon="🦾", layout="wide")

# ===========================================================================
# UI THEME  (presentation only)
# ===========================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
html, body, [class*="css"] { font-family:'Inter','Segoe UI',system-ui,sans-serif; }
.stApp {
  background:
    radial-gradient(1000px 500px at 4% -12%, #e0f2fe 0%, transparent 58%),
    radial-gradient(900px 480px at 104% 0%, #eef2ff 0%, transparent 55%),
    #f7f9fc;
}
.block-container { padding-top:1.05rem; max-width:1520px; }
h1,h2,h3,h4 { color:#0f172a; letter-spacing:-.02em; }

/* ---------- dark sidebar (kept from the original fix, refined) ---------- */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#1e293b 0%,#111a2e 100%) !important;
  border-right:1px solid #0b1220; }
[data-testid="stSidebar"] * { color:#f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background:linear-gradient(120deg,#0369a1,#0ea5e9) !important;
  color:#fff !important; border:none !important; border-radius:12px !important; font-weight:700 !important; }
[data-testid="stSidebar"] .stSlider * { color:#f8fafc !important; }
[data-testid="stSidebar"] details { background:rgba(255,255,255,.05) !important;
  border:1px solid rgba(255,255,255,.12) !important; border-radius:12px !important; }
.side-brand { background:linear-gradient(120deg,#0369a1,#0ea5e9); border-radius:16px; padding:14px 16px;
  box-shadow:0 16px 28px -20px rgba(0,0,0,.9); }
.side-brand .t { font-weight:800; font-size:1.02rem; }
.side-brand .s { font-size:.79rem; opacity:.93; }
.side-sec { display:flex; align-items:center; gap:8px; font-size:.71rem; font-weight:800;
  letter-spacing:.11em; text-transform:uppercase; opacity:.72; margin:16px 0 4px; }
.side-sec:before { content:""; width:14px; height:3px; border-radius:3px; background:#38bdf8; }
.side-ref { background:rgba(56,189,248,.14); border:1px solid rgba(56,189,248,.38);
  border-radius:12px; padding:10px 12px; font-size:.83rem; line-height:1.5; }

/* ---------- hero ---------- */
.hero { position:relative; overflow:hidden; border-radius:22px; padding:20px 26px; color:#fff;
  background:linear-gradient(120deg,#075985 0%, #0284c7 55%, #38bdf8 100%);
  box-shadow:0 24px 46px -24px rgba(2,132,199,.55); }
.hero:before { content:""; position:absolute; right:-70px; top:-95px; width:265px; height:265px;
  background:radial-gradient(circle, rgba(255,255,255,.4), transparent 62%); }
.hero-emoji { font-size:2rem; line-height:1; }
.hero-title { font-size:1.75rem; font-weight:800; margin:6px 0 4px; }
.hero-sub { font-size:.96rem; opacity:.95; max-width:1080px; line-height:1.5; }
.hero-chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
.hero-chip { background:rgba(255,255,255,.2); border:1px solid rgba(255,255,255,.42);
  border-radius:999px; padding:4px 12px; font-size:.78rem; font-weight:600; }

/* ---------- section headers ---------- */
.sec { display:flex; align-items:center; gap:12px; margin:18px 0 8px; }
.sec-bar { width:5px; height:36px; border-radius:6px; background:linear-gradient(180deg,#075985,#38bdf8); }
.sec-t { font-size:1.12rem; font-weight:800; color:#0f172a; line-height:1.15; }
.sec-s { font-size:.83rem; color:#64748b; }

/* ---------- cards / kpis ---------- */
.kpi-row { display:flex; gap:10px; flex-wrap:wrap; margin:8px 0 2px; }
.kpi { flex:1 1 150px; background:#fff; border:1px solid #e6eef7; border-left:4px solid #0ea5e9;
  border-radius:14px; padding:11px 14px; box-shadow:0 16px 30px -28px rgba(15,23,42,.55); }
.kpi-v { font-size:1.25rem; font-weight:800; color:#0f172a; }
.kpi-l { font-size:.7rem; letter-spacing:.09em; text-transform:uppercase; color:#64748b; }
.card { background:#fff; border:1px solid #e6eef7; border-radius:16px; padding:14px 16px;
  box-shadow:0 18px 34px -30px rgba(15,23,42,.55); }
.note { background:linear-gradient(120deg,#f0f9ff,#ecfeff); border:1px solid #bae6fd;
  border-radius:16px; padding:14px 18px; color:#0c4a6e; font-size:.92rem; line-height:1.55; }

/* ---------- native widgets, restyled ---------- */
[data-testid="stMetric"] { background:#fff; border:1px solid #e6eef7; border-radius:14px; padding:12px 14px; }
[data-testid="stMetricLabel"] p { font-size:.72rem; letter-spacing:.07em; text-transform:uppercase; color:#64748b; }
[data-testid="stMetricValue"] { font-weight:800; color:#0f172a; }
[data-testid="stAlert"] { border-radius:14px; }
[data-testid="stPlotlyChart"] { background:#fff; border:1px solid #e6eef7; border-radius:18px;
  padding:8px 8px 2px; box-shadow:0 20px 36px -32px rgba(15,23,42,.6); }
.stButton>button { border-radius:12px; font-weight:600; }
</style>
""", unsafe_allow_html=True)


def section(title, subtitle=""):
    """Styled section header (UI helper)."""
    st.markdown(
        f'<div class="sec"><span class="sec-bar"></span><div>'
        f'<div class="sec-t">{title}</div><div class="sec-s">{subtitle}</div></div></div>',
        unsafe_allow_html=True,
    )


PLOTLY_FONT = dict(family="Inter, Segoe UI, sans-serif", size=12.5, color="#334155")


def polish(fig):
    """Shared chart theme (presentation only — no data is touched)."""
    fig.update_layout(template="plotly_white", font=PLOTLY_FONT,
                      hoverlabel=dict(bgcolor="white", bordercolor="#e2e8f0", font=dict(size=12)))
    return fig


# Reference posture (the "perfect" pose)
REFERENCE = {"Base": 45, "Shoulder": 90, "Elbow": 45}
TOLERANCE = 5  # degrees

def build_arm_fig(base_ang, shoulder_ang, elbow_ang, ref_base, ref_shoulder, ref_elbow):
    """Draw the robot arm with current angles and reference (dotted) overlay."""
    L1, L2, L3 = 2.0, 1.8, 1.5
    
    # Current arm
    x0, y0 = 0, 0
    x1 = L1 * math.cos(math.radians(base_ang))
    y1 = L1 * math.sin(math.radians(base_ang))
    x2 = x1 + L2 * math.cos(math.radians(base_ang + shoulder_ang))
    y2 = y1 + L2 * math.sin(math.radians(base_ang + shoulder_ang))
    x3 = x2 + L3 * math.cos(math.radians(base_ang + shoulder_ang + elbow_ang))
    y3 = y2 + L3 * math.sin(math.radians(base_ang + shoulder_ang + elbow_ang))
    
    # Reference arm (dotted gray)
    rx0, ry0 = 0, 0
    rx1 = L1 * math.cos(math.radians(ref_base))
    ry1 = L1 * math.sin(math.radians(ref_base))
    rx2 = rx1 + L2 * math.cos(math.radians(ref_base + ref_shoulder))
    ry2 = ry1 + L2 * math.sin(math.radians(ref_base + ref_shoulder))
    rx3 = rx2 + L3 * math.cos(math.radians(ref_base + ref_shoulder + ref_elbow))
    ry3 = ry2 + L3 * math.sin(math.radians(ref_base + ref_shoulder + ref_elbow))
    
    fig = go.Figure()
    
    # Reference arm (dotted gray)
    fig.add_trace(go.Scatter(x=[rx0, rx1, rx2, rx3], y=[ry0, ry1, ry2, ry3], mode="lines+markers", 
                             line=dict(color="#cbd5e1", width=3, dash="dot"), 
                             marker=dict(size=10, color="#cbd5e1"), name="Reference Pose", showlegend=True))
    
    # Current arm (solid colored)
    fig.add_trace(go.Scatter(x=[x0, x1, x2, x3], y=[y0, y1, y2, y3], mode="lines+markers", 
                             line=dict(color="#3b82f6", width=5), 
                             marker=dict(size=12, color="#1e40af"), name="Current Pose", showlegend=True))
    
    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), 
                      xaxis=dict(range=[-1, 6], visible=False), 
                      yaxis=dict(range=[-1, 6], visible=False),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    return polish(fig)

# ===========================================================================
# UI LAYOUT
# ===========================================================================
st.markdown("""
<div class="hero">
  <div class="hero-emoji">🦾</div>
  <div class="hero-title">Robot Posture Validation</div>
  <div class="hero-sub">Calibrate the three joints until the blue arm sits exactly on top of the
  <b>dotted grey reference pose</b>. Green means the joint is within tolerance, red means it needs a nudge.</div>
  <div class="hero-chips">
    <span class="hero-chip">3 joints</span>
    <span class="hero-chip">±5° tolerance</span>
    <span class="hero-chip">Live forward kinematics</span>
    <span class="hero-chip">Pass / fail report</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="side-brand">
      <div class="t">⚙️ Joint Controls</div>
      <div class="s">Match the dotted reference pose.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-sec">Tune the joints</div>', unsafe_allow_html=True)
    base = st.slider("🔄 Base Angle", 0, 180, 45)
    shoulder = st.slider("💪 Shoulder Angle", 0, 180, 90)
    elbow = st.slider("🦾 Elbow Angle", 0, 180, 45)

    st.markdown(f"""
    <div class="side-ref">
      🎯 <b>Target pose</b><br>
      Base {REFERENCE['Base']}° · Shoulder {REFERENCE['Shoulder']}° · Elbow {REFERENCE['Elbow']}°<br>
      <span style="opacity:.8">Tolerance ±{TOLERANCE}° per joint</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-sec">Check the pose</div>', unsafe_allow_html=True)
    validate = st.button("✅ Validate Posture", type="primary", use_container_width=True)

    with st.expander("🧠 For the Lecturers: The Math Behind the Magic"):
        st.markdown(f"**Reference angles:** Base={REFERENCE['Base']}°, Shoulder={REFERENCE['Shoulder']}°, Elbow={REFERENCE['Elbow']}°")
        st.caption("Forward kinematics: x = L1·cos(θ1) + L2·cos(θ1+θ2) + L3·cos(θ1+θ2+θ3)")

# Main display
section("The arm", "Blue = where the arm actually is right now. Dotted grey = where it should be.")
col1, col2 = st.columns([1.2, 1])

with col1:
    fig = build_arm_fig(base, shoulder, elbow, REFERENCE["Base"], REFERENCE["Shoulder"], REFERENCE["Elbow"])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi"><div class="kpi-l">🔄 Base now</div><div class="kpi-v">{base}°</div></div>
      <div class="kpi"><div class="kpi-l">💪 Shoulder now</div><div class="kpi-v">{shoulder}°</div></div>
      <div class="kpi"><div class="kpi-l">🦾 Elbow now</div><div class="kpi-v">{elbow}°</div></div>
      <div class="kpi"><div class="kpi-l">Tolerance</div><div class="kpi-v">±{TOLERANCE}°</div></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if validate:
        st.markdown("### 📊 Validation Report")
        
        errors = {
            "Base": abs(base - REFERENCE["Base"]),
            "Shoulder": abs(shoulder - REFERENCE["Shoulder"]),
            "Elbow": abs(elbow - REFERENCE["Elbow"])
        }
        
        # display-only summary chips (computed from the same error values)
        n_ok = sum(1 for e in errors.values() if e <= TOLERANCE)
        st.markdown(f"""
        <div class="kpi-row">
          <div class="kpi"><div class="kpi-l">Joints in tolerance</div><div class="kpi-v">{n_ok} / 3</div></div>
          <div class="kpi"><div class="kpi-l">Largest error</div><div class="kpi-v">{max(errors.values()):.1f}°</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        for joint, error in errors.items():
            if error <= TOLERANCE:
                st.success(f"✅ **{joint}**: {error:.1f}° error (Correct!)")
            else:
                st.error(f"❌ **{joint}**: {error:.1f}° error (Adjust by {error:.1f}°)")
        
        total_error = sum(errors.values())
        if total_error <= TOLERANCE * 3:
            st.balloons()
            st.success("🎉 **Perfect posture!** All joints are within tolerance.")
        else:
            st.warning(f"⚠️ Total error: {total_error:.1f}°. Keep adjusting!")
    else:
        st.markdown("""
        <div class="note">
          <b>👆 Press <i>Validate Posture</i> to check the pose.</b><br><br>
          Each joint is compared with the reference and scored:
          <b style="color:#166534">green ✅ within ±5°</b>,
          <b style="color:#991b1b">red ❌ further off</b> — and the report tells you how far to adjust.
        </div>
        """, unsafe_allow_html=True)
