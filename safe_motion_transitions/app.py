# -*- coding: utf-8 -*-
import math, numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Smooth Rides vs Jerky Rides", page_icon="🎢", layout="wide")

# --- DARK SIDEBAR FIX ---
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e293b !important; }
[data-testid="stSidebar"] * { color: #f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background-color: #3b82f6 !important; color: white !important; border: none !important; }
[data-testid="stSidebar"] .stSlider * { color: #f8fafc !important; }
.block-container {padding-top: 1.3rem; max-width: 1500px;}
h1, h2, h3 {color: #0f172a;}
</style>
""", unsafe_allow_html=True)

def accel_segments(J, A, Vt):
    segs = []
    if Vt <= 1e-9:
        return segs, 0.0
    if J * Vt <= A * A:
        tau = math.sqrt(Vt / J)
        segs = [("j", +J, tau), ("j", -J, tau)]
    else:
        ta = A / J
        tp = (Vt - A * A / J) / A
        segs = [("j", +J, ta), ("a", +A, tp), ("j", -J, ta)]
    v = a = s = 0.0
    out = []
    for kind, x, t in segs:
        if kind == "j":
            a_new = a + x * t
            v_new = v + a * t + 0.5 * x * t * t
            s += v * t + 0.5 * a * t * t + x * t ** 3 / 6.0
        else:
            a_new = x
            v_new = v + x * t
            s += v * t + 0.5 * x * t * t
        out.append((kind, x, t))
        v, a = v_new, a_new
    return out, s

def plan_s_curve(D, V, A, J):
    acc_segs, d_acc = accel_segments(J, A, V)
    if 2.0 * d_acc <= D:
        Vt = V
        cruise = (D - 2.0 * d_acc) / V
    else:
        lo, hi = 0.0, V
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            _, dm = accel_segments(J, A, mid)
            if 2.0 * dm <= D:
                lo = mid
            else:
                hi = mid
        Vt = 0.5 * (lo + hi)
        _, d_acc = accel_segments(J, A, Vt)
        cruise = 0.0
    acc, _ = accel_segments(J, A, Vt)
    dec = [("j" if k == "j" else "a", -a_, t) for (k, a_, t) in acc]
    segments = acc + ([("a", 0.0, cruise)] if cruise > 1e-12 else []) + dec
    return {"segments": segments, "Vmax_used": Vt, "total_t": sum(t for _, _, t in segments)}

def build_timeline(segments, n_samples=4000):
    total_t = sum(t for _, _, t in segments)
    dt = max(total_t / n_samples, 1e-9)
    times, jrk, acc, vel, pos = [], [], [], [], []
    v = a = s = t = 0.0
    for kind, x, dur in segments:
        n = max(2, int(round(dur / dt)))
        lt = np.linspace(0.0, dur, n, endpoint=False)
        times.append(t + lt)
        jrk.append(np.full(n, x if kind == "j" else 0.0))
        if kind == "j":
            acc.append(a + x * lt)
            vel.append(v + a * lt + 0.5 * x * lt * lt)
            pos.append(s + v * lt + 0.5 * a * lt * lt + x * lt ** 3 / 6.0)
            a_new = a + x * dur
            v_new = v + a * dur + 0.5 * x * dur * dur
            s_new = s + v * dur + 0.5 * a * dur * dur + x * dur ** 3 / 6.0
        else:
            acc.append(np.full(n, x))
            vel.append(v + x * lt)
            pos.append(s + v * lt + 0.5 * x * lt * lt)
            a_new = x
            v_new = v + x * dur
            s_new = s + v * dur + 0.5 * x * dur * dur
        v, a, s = v_new, a_new, s_new
        t = t + dur
    times.append(np.array([total_t]))
    jrk.append(np.zeros(1))
    acc.append(np.array([a]))
    vel.append(np.array([v]))
    pos.append(np.array([s]))
    return (np.concatenate(times), np.concatenate(jrk), np.concatenate(acc), np.concatenate(vel), np.concatenate(pos))

st.title("🎢 Smooth Rides vs. Jerky Rides")
st.info("👋 **Welcome!** Imagine you're in a car. **Unsafe** is when the driver slams the gas pedal to the floor and slams the brakes. **Safe** is a gentle, smooth driver. This tool shows why robots need to be smooth drivers so they don't break their gears!")

ss = st.session_state
if "executed" not in ss:
    ss["executed"] = False

with st.sidebar:
    st.markdown("### ⚙️ Robot Physics")
    D = st.slider("📏 Distance to Move (m)", 2.0, 60.0, 20.0, 1.0)
    V = st.slider("🏃 Max Speed (m/s)", 0.5, 6.0, 2.5, 0.1)
    A = st.slider("🚀 Max Acceleration", 0.5, 10.0, 3.0, 0.1)
    J = st.slider("🛑 Smoothness (Jerk Limit)", 0.5, 50.0, 8.0, 0.1, help="Lower = Smoother but slower. Higher = Jerky but fast.")
    
    if st.button("⚡ Show Unsafe vs Safe", type="primary", use_container_width=True):
        ss["executed"] = True
    
    with st.expander("🧠 For the Lecturers: The Physics of Jerk"):
        st.markdown("The unsafe profile is a step function. A step in velocity means an *infinite* acceleration spike (Dirac delta). The safe profile uses a 3rd-order S-curve where jerk is limited.")

plan = plan_s_curve(D, V, A, J)
t_s, j_s, a_s, v_s, p_s = build_timeline(plan["segments"])
v_s[-1] = 0.0
a_s[-1] = 0.0
stop_t = D / V
tt_safe = plan["total_t"]

t_u = np.arange(0.0, tt_safe, tt_safe / 4000)
v_u = np.where(t_u < stop_t, V, 0.0)
xs_v = np.concatenate([t_u, np.array([0.0, 0.0, stop_t, stop_t])])
ys_v = np.concatenate([v_u, np.array([0.0, V, V, 0.0])])
order_v = np.argsort(xs_v)
xs_v, ys_v = xs_v[order_v], ys_v[order_v]

st.markdown("## 🚦 Motion Profiles")
left_col, right_col = st.columns(2)

with left_col:
    if ss["executed"]:
        fig_u = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, row_heights=[0.55, 0.45])
        fig_u.add_trace(go.Scatter(x=xs_v, y=ys_v, mode="lines", name="v(t) unsafe", line=dict(color="#ef4444", width=3)), row=1, col=1)
        fig_u.update_layout(title="⚡ UNSAFE — Slams the gas pedal", height=430)
        st.plotly_chart(fig_u, use_container_width=True)
    else:
        st.warning("Press **⚡ Show Unsafe vs Safe** in the sidebar to reveal the jerky profile.")

with right_col:
    fig_s = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, row_heights=[0.55, 0.45])
    fig_s.add_trace(go.Scatter(x=t_s, y=v_s, mode="lines", name="v(t) safe", line=dict(color="#059669", width=3)), row=1, col=1)
    fig_s.add_trace(go.Scatter(x=t_s, y=a_s, mode="lines", name="a(t) safe", line=dict(color="#3b82f6", width=2.2)), row=2, col=1)
    fig_s.update_layout(title="🟢 SAFE — Gentle S-Curve", height=430)
    st.plotly_chart(fig_s, use_container_width=True)

c1, c2 = st.columns(2)
c1.metric("⏱️ Safe Time", f"{tt_safe:.2f} s")
c2.metric("⚡ Ideal (Unsafe) Time", f"{D/V:.2f} s")