# -*- coding: utf-8 -*-
"""
Spider-Robot Walking Simulator
------------------------------------------------------------
UI polish pass only.
The simulation logic is UNCHANGED: same constants, same gait tables,
same CPG sine maths, same figure geometry, same animation loop.
"""
import math, time, numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Spider-Robot Simulator", page_icon="🦗", layout="wide")

# ===========================================================================
# UI THEME  (presentation only)
# ===========================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
html, body, [class*="css"] { font-family:'Inter','Segoe UI',system-ui,sans-serif; }
.stApp {
  background:
    radial-gradient(1100px 520px at 4% -12%, #e7fbf3 0%, transparent 58%),
    radial-gradient(900px 480px at 104% 0%, #eef2ff 0%, transparent 55%),
    #f6f9fc;
}
.block-container { padding-top:1.05rem; max-width:1520px; }
h1,h2,h3,h4 { color:#0f172a; letter-spacing:-.02em; }

/* ---------- dark sidebar (kept from the original fix, refined) ---------- */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#1e293b 0%,#0f172a 100%) !important;
  border-right:1px solid #0b1220; }
[data-testid="stSidebar"] * { color:#f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background:linear-gradient(120deg,#0f766e,#10b981) !important;
  color:#fff !important; border:none !important; border-radius:12px !important; font-weight:700 !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { color:#0f172a !important; }
[data-testid="stSidebar"] details { background:rgba(255,255,255,.05) !important;
  border:1px solid rgba(255,255,255,.12) !important; border-radius:12px !important; }
.side-brand { background:linear-gradient(120deg,#0f766e,#10b981); border-radius:16px; padding:14px 16px;
  box-shadow:0 16px 28px -20px rgba(0,0,0,.85); }
.side-brand .t { font-weight:800; font-size:1.02rem; }
.side-brand .s { font-size:.79rem; opacity:.93; }
.side-sec { display:flex; align-items:center; gap:8px; font-size:.71rem; font-weight:800;
  letter-spacing:.11em; text-transform:uppercase; opacity:.72; margin:16px 0 4px; }
.side-sec:before { content:""; width:14px; height:3px; border-radius:3px; background:#10b981; }
.side-tip { background:rgba(16,185,129,.14); border:1px solid rgba(16,185,129,.35);
  border-radius:12px; padding:9px 12px; font-size:.82rem; line-height:1.45; }

/* ---------- hero ---------- */
.hero { position:relative; overflow:hidden; border-radius:22px; padding:20px 26px; color:#fff;
  background:linear-gradient(120deg,#0f766e 0%, #10b981 55%, #34d399 100%);
  box-shadow:0 24px 46px -24px rgba(16,185,129,.55); }
.hero:before { content:""; position:absolute; right:-70px; top:-95px; width:265px; height:265px;
  background:radial-gradient(circle, rgba(255,255,255,.42), transparent 62%); }
.hero-emoji { font-size:2rem; line-height:1; }
.hero-title { font-size:1.75rem; font-weight:800; margin:6px 0 4px; }
.hero-sub { font-size:.96rem; opacity:.95; max-width:1080px; line-height:1.5; }
.hero-chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
.hero-chip { background:rgba(255,255,255,.2); border:1px solid rgba(255,255,255,.4);
  border-radius:999px; padding:4px 12px; font-size:.78rem; font-weight:600; }

/* ---------- section headers ---------- */
.sec { display:flex; align-items:center; gap:12px; margin:20px 0 8px; }
.sec-bar { width:5px; height:36px; border-radius:6px; background:linear-gradient(180deg,#0f766e,#34d399); }
.sec-t { font-size:1.12rem; font-weight:800; color:#0f172a; line-height:1.15; }
.sec-s { font-size:.83rem; color:#64748b; }

/* ---------- cards / kpis ---------- */
.kpi-row { display:flex; gap:10px; flex-wrap:wrap; margin:10px 0 2px; }
.kpi { flex:1 1 150px; background:#fff; border:1px solid #e6efe9; border-left:4px solid #10b981;
  border-radius:14px; padding:11px 14px; box-shadow:0 16px 30px -28px rgba(15,23,42,.55); }
.kpi-v { font-size:1.25rem; font-weight:800; color:#0f172a; }
.kpi-l { font-size:.7rem; letter-spacing:.09em; text-transform:uppercase; color:#64748b; }
.note { background:linear-gradient(120deg,#ecfdf5,#f0fdfa); border:1px solid #a7f3d0;
  border-radius:16px; padding:14px 18px; color:#065f46; font-size:.92rem; line-height:1.55; }
.chip { display:inline-block; padding:5px 14px; border-radius:999px; font-size:.81rem; font-weight:600;
  margin:2px 6px 2px 0; border:1px solid #d7e6df; }
.chip.ground { background:linear-gradient(120deg,#0f766e,#10b981); color:#fff; border:0; }
.chip.air { background:#f1f5f9; color:#475569; }

/* ---------- native widgets, restyled ---------- */
[data-testid="stMetric"] { background:#fff; border:1px solid #e6efe9; border-radius:14px; padding:12px 14px; }
[data-testid="stAlert"] { border-radius:14px; }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#10b981,#34d399); border-radius:999px; }
[data-testid="stPlotlyChart"] { background:#fff; border:1px solid #e6efe9; border-radius:18px;
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


# Constants
BODY_R, FOOT_R, LIFT_TUCK, SA, DT = 0.70, 1.80, 0.50, 0.55, 0.05
PALETTE = ["#d62728", "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b"]

# SIMPLIFIED GAITS FOR LAYMEN
GAITS = {
    "🏃 Tripod (Fast & Stable)": {
        "offsets": [0.0, 180.0, 0.0, 180.0, 0.0, 180.0], "duty": 0.50,
        "desc": "Like a camera tripod! 3 legs are always on the ground while the other 3 move. It's fast and stable."
    },
    "🐛 Wave (Slow & Super Safe)": {
        "offsets": [0.0, 60.0, 120.0, 180.0, 240.0, 300.0], "duty": 0.85,
        "desc": "Like a caterpillar. Only 1 leg moves at a time. Very slow, but almost impossible to fall over."
    },
    "🌊 Ripple (Medium)": {
        "offsets": [0.0, 120.0, 0.0, 180.0, 300.0, 180.0], "duty": 0.65,
        "desc": "A mix of both. Front and back legs move together while the middle legs follow."
    },
}

def build_robot_fig(t, freq, offsets_deg, duty):
    fig = go.Figure()
    fig.add_shape(type="circle", xref="x", yref="y", x0=-BODY_R, y0=-BODY_R, x1=BODY_R, y1=BODY_R,
                  line=dict(color="#334155", width=2), fillcolor="#e2e8f0", layer="below")
    fig.add_annotation(x=0, y=0, text="BODY", showarrow=False, font=dict(size=11, color="#64748b"))
    swing_frac = 1.0 - duty
    for i in range(6):
        th_root = math.radians(90.0 - i * 60.0)
        rx, ry = BODY_R * math.cos(th_root), BODY_R * math.sin(th_root)
        p = (freq * t + offsets_deg[i] / 360.0) % 1.0
        ps = 0.25 - duty / 2.0
        q = (p - ps) % 1.0
        stance = q < duty
        if stance:
            u = q / duty
            stroke = SA * (1.0 - 2.0 * u); lift = 0.0
        else:
            u2 = (q - duty) / swing_frac if swing_frac > 0 else 0.0
            stroke = SA * (-1.0 + 2.0 * u2)
            lift = math.sin(math.pi * u2)
        ang = th_root + stroke
        foot_r = FOOT_R - LIFT_TUCK * lift
        fx, fy = foot_r * math.cos(ang), foot_r * math.sin(ang)
        color, width, opacity = PALETTE[i], (6.0 if stance else 3.0), (1.0 if stance else 0.45)
        fig.add_trace(go.Scatter(x=[rx, fx], y=[ry, fy], mode="lines", line=dict(color=color, width=width), opacity=opacity, showlegend=False, hovertemplate=None, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=[fx], y=[fy], mode="markers", marker=dict(size=9 if stance else 7, color="#0f172a" if stance else color, symbol="circle" if stance else "circle-open", line=dict(color=color, width=1.5)), opacity=opacity, showlegend=False, hoverinfo="skip"))
    fig.update_layout(xaxis=dict(range=[-2.7, 2.7], visible=False), yaxis=dict(range=[-2.7, 2.7], visible=False), height=540, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white")
    return polish(fig)

def build_cpg_fig(t_hist, freq, offsets_deg, duty):
    ts = np.arange(-3.0, 0.001, DT) if t_hist is None else np.asarray(t_hist)
    ts = ts[ts >= max(ts[-1] - 3.0, 0.0)]
    fig = go.Figure()
    omega = 2.0 * math.pi * freq
    for i in range(6):
        y = np.sin(omega * ts + math.radians(offsets_deg[i]))
        fig.add_trace(go.Scatter(x=ts, y=y, mode="lines", name=f"Leg {i+1}", line=dict(color=PALETTE[i], width=2.2)))
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=25, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), xaxis_title="time (s)", yaxis_title="Brain Signal", yaxis=dict(range=[-1.25, 1.25]))
    return polish(fig)

# ===========================================================================
# UI LAYOUT
# ===========================================================================
st.markdown("""
<div class="hero">
  <div class="hero-emoji">🦗</div>
  <div class="hero-title">Spider-Robot Walking Simulator</div>
  <div class="hero-sub">See how a six-legged robot moves its legs in a coordinated pattern so it never falls over —
  no maths needed. Pick a walking style, press <b>Start Walking</b>, and watch the legs and "brain signals" move together.</div>
  <div class="hero-chips">
    <span class="hero-chip">6 legs</span>
    <span class="hero-chip">3 walking styles</span>
    <span class="hero-chip">Live brain signals</span>
    <span class="hero-chip">Beginner friendly</span>
  </div>
</div>
""", unsafe_allow_html=True)

ss = st.session_state
with st.sidebar:
    st.markdown("""
    <div class="side-brand">
      <div class="t">🦗 Robot Controls</div>
      <div class="s">Choose a walking style, then fine-tune the movement.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-sec">1 · Walking style</div>', unsafe_allow_html=True)
    gait = st.selectbox("Walking Style", list(GAITS.keys()), key="gait")
    info = GAITS[gait]
    if ss.get("_last_gait") != gait:
        ss["_last_gait"] = gait; ss["duty"] = info["duty"]

    st.markdown(f"<div class='side-tip'>💡 {info['desc']}</div>", unsafe_allow_html=True)

    st.markdown('<div class="side-sec">2 · Fine-tune</div>', unsafe_allow_html=True)
    freq = st.slider("🏃 Walking Speed", 0.2, 2.5, 0.8, 0.05)
    duty = st.slider("🦶 Ground Contact Time", 0.20, 0.95, float(ss.get("duty", 0.5)), 0.01, key="duty", help="How long feet stay on the ground.")
    run_dur = st.slider("⏱️ Demo Length (s)", 2, 12, 6, 1)

    # HIDE THE MATH
    with st.expander("🧠 For the Lecturers: The Math Behind the Magic"):
        offs = info["offsets"]
        st.markdown(f"**Phase offsets (deg):** {', '.join(f'L{i+1}={offs[i]:g}°' for i in range(6))}")
        st.caption("These numbers represent the Central Pattern Generator (CPG) sine-wave phase delays.")

    st.markdown('<div class="side-sec">3 · Run it</div>', unsafe_allow_html=True)
    start = st.button("▶ Start Walking", type="primary", use_container_width=True)

# --- live parameter chips (display only) ---
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi"><div class="kpi-l">Walking style</div><div class="kpi-v">{gait.split(' ')[0]} {gait.split(' ',1)[1].split('(')[0].strip()}</div></div>
  <div class="kpi"><div class="kpi-l">Steps per second</div><div class="kpi-v">{freq:.2f} Hz</div></div>
  <div class="kpi"><div class="kpi-l">Ground contact time</div><div class="kpi-v">{duty*100:.0f}%</div></div>
  <div class="kpi"><div class="kpi-l">Cycle time</div><div class="kpi-v">{1.0/freq:.2f} s</div></div>
</div>
""", unsafe_allow_html=True)

section("The robot, seen from above", "Each of the 6 legs is drawn from the body (circle) out to its foot.")
left_ph, right_ph = st.columns([1.35, 1])
with left_ph:
    anim_ph = st.empty()
with right_ph:
    st.markdown("""
    <div class="note">
      <b>How to read the picture</b><br><br>
      <span class="chip ground">● Solid, full-length leg</span><br>
      This foot is <b>planted on the ground</b> and pushing the robot forward.<br><br>
      <span class="chip air">○ Pale, shorter leg</span><br>
      This leg is <b>in the air</b>, swinging forward to its next step.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="note" style="margin-top:12px;background:linear-gradient(120deg,#eef2ff,#f5f3ff);border-color:#c7d2fe;color:#3730a3">
      <b>Try this 👉</b> Switch between <b>Tripod</b>, <b>Wave</b> and <b>Ripple</b> and press Start.
      Tripod always keeps 3 feet down (fast), Wave moves one leg at a time (super safe).
    </div>
    """, unsafe_allow_html=True)

section("Brain signals (the 6 leg oscillators)", "Each coloured line is one leg's internal rhythm — the 'brain signal' that decides when to step.")
chart_ph = st.empty()

if start:
    steps = int(run_dur / DT)
    hist = []
    progress = st.progress(0.0, text="Walking…")
    for k in range(steps):
        t = k * DT; hist.append(t)
        anim_ph.plotly_chart(build_robot_fig(t, freq, info["offsets"], duty), use_container_width=True, key=f"a{k}")
        chart_ph.plotly_chart(build_cpg_fig(hist, freq, info["offsets"], duty), use_container_width=True, key=f"c{k}")
        progress.progress((k + 1) / steps)
        time.sleep(DT)
    st.success("✅ Demo finished! Notice how the legs move in sync.")
else:
    anim_ph.plotly_chart(build_robot_fig(0.0, freq, info["offsets"], duty), use_container_width=True, key="idle_r")
    chart_ph.plotly_chart(build_cpg_fig(None, freq, info["offsets"], duty), use_container_width=True, key="idle_c")
    st.info("👆 Press **Start Walking** in the sidebar to see the robot move!")
