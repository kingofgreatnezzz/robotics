# -*- coding: utf-8 -*-
import math, time, numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Spider-Robot Simulator", page_icon="🦗", layout="wide")

# --- UI FIX: Dark sidebar, white text ---
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e293b !important; }
[data-testid="stSidebar"] * { color: #f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background-color: #3b82f6 !important; color: white !important; border: none !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { color: #0f172a !important; }
.block-container {padding-top: 1.3rem; max-width: 1500px;}
h1, h2, h3 {color: #0f172a;}
</style>
""", unsafe_allow_html=True)

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
        fig.add_trace(go.Scatter(x=[rx, fx], y=[ry, fy], mode="lines", line=dict(color=color, width=width), opacity=opacity, showlegend=False))
        fig.add_trace(go.Scatter(x=[fx], y=[fy], mode="markers", marker=dict(size=9 if stance else 7, color="#0f172a" if stance else color, symbol="circle" if stance else "circle-open", line=dict(color=color, width=1.5)), opacity=opacity, showlegend=False))
    fig.update_layout(xaxis=dict(range=[-2.7, 2.7], visible=False), yaxis=dict(range=[-2.7, 2.7], visible=False), height=540, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white")
    return fig

def build_cpg_fig(t_hist, freq, offsets_deg, duty):
    ts = np.arange(-3.0, 0.001, DT) if t_hist is None else np.asarray(t_hist)
    ts = ts[ts >= max(ts[-1] - 3.0, 0.0)]
    fig = go.Figure()
    omega = 2.0 * math.pi * freq
    for i in range(6):
        y = np.sin(omega * ts + math.radians(offsets_deg[i]))
        fig.add_trace(go.Scatter(x=ts, y=y, mode="lines", name=f"Leg {i+1}", line=dict(color=PALETTE[i], width=2.2)))
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=25, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), xaxis_title="time (s)", yaxis_title="Brain Signal", yaxis=dict(range=[-1.25, 1.25]))
    return fig

# --- UI LAYOUT ---
st.title("🦗 Spider-Robot Walking Simulator")
st.info("👋 **Welcome!** This tool shows how a 6-legged robot coordinates its legs to walk without falling over. You don't need to know any math—just pick a walking style and press Start!")

ss = st.session_state
with st.sidebar:
    st.markdown("### ⚙️ Robot Controls")
    gait = st.selectbox("Walking Style", list(GAITS.keys()), key="gait")
    info = GAITS[gait]
    if ss.get("_last_gait") != gait:
        ss["_last_gait"] = gait; ss["duty"] = info["duty"]
    
    st.markdown(f"💡 *{info['desc']}*")
    freq = st.slider("🏃 Walking Speed", 0.2, 2.5, 0.8, 0.05)
    duty = st.slider("🦶 Ground Contact Time", 0.20, 0.95, float(ss.get("duty", 0.5)), 0.01, key="duty", help="How long feet stay on the ground.")
    run_dur = st.slider("⏱️ Demo Length (s)", 2, 12, 6, 1)
    
    # HIDE THE MATH
    with st.expander("🧠 For the Lecturers: The Math Behind the Magic"):
        offs = info["offsets"]
        st.markdown(f"**Phase offsets (deg):** {', '.join(f'L{i+1}={offs[i]:g}°' for i in range(6))}")
        st.caption("These numbers represent the Central Pattern Generator (CPG) sine-wave phase delays.")
        
    start = st.button("▶ Start Walking", type="primary", use_container_width=True)

anim_ph = st.empty()
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