# -*- coding: utf-8 -*-
"""
Smooth Rides vs Jerky Rides
------------------------------------------------------------
UI polish pass only.
The physics is UNCHANGED: same jerk-limited S-curve planner, same
timeline integration, same step-function "unsafe" profile.
"""
import math, numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Smooth Rides vs Jerky Rides", page_icon="🎢", layout="wide")

# ===========================================================================
# UI THEME  (presentation only)
# ===========================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
html, body, [class*="css"] { font-family:'Inter','Segoe UI',system-ui,sans-serif; }
.stApp {
  background:
    radial-gradient(1000px 500px at 4% -12%, #fef2f2 0%, transparent 58%),
    radial-gradient(900px 480px at 104% 0%, #ecfdf5 0%, transparent 55%),
    #f7f9fc;
}
.block-container { padding-top:1.05rem; max-width:1520px; }
h1,h2,h3,h4 { color:#0f172a; letter-spacing:-.02em; }

/* ---------- dark sidebar (kept from the original fix, refined) ---------- */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#1e293b 0%,#111a2e 100%) !important;
  border-right:1px solid #0b1220; }
[data-testid="stSidebar"] * { color:#f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background:linear-gradient(120deg,#b91c1c,#ef4444) !important;
  color:#fff !important; border:none !important; border-radius:12px !important; font-weight:700 !important; }
[data-testid="stSidebar"] .stSlider * { color:#f8fafc !important; }
[data-testid="stSidebar"] details { background:rgba(255,255,255,.05) !important;
  border:1px solid rgba(255,255,255,.12) !important; border-radius:12px !important; }
.side-brand { background:linear-gradient(120deg,#b91c1c,#f59e0b); border-radius:16px; padding:14px 16px;
  box-shadow:0 16px 28px -20px rgba(0,0,0,.9); }
.side-brand .t { font-weight:800; font-size:1.02rem; }
.side-brand .s { font-size:.79rem; opacity:.93; }
.side-sec { display:flex; align-items:center; gap:8px; font-size:.71rem; font-weight:800;
  letter-spacing:.11em; text-transform:uppercase; opacity:.72; margin:16px 0 4px; }
.side-sec:before { content:""; width:14px; height:3px; border-radius:3px; background:#f59e0b; }

/* ---------- hero ---------- */
.hero { position:relative; overflow:hidden; border-radius:22px; padding:20px 26px; color:#fff;
  background:linear-gradient(115deg,#7f1d1d 0%, #ef4444 48%, #f59e0b 100%);
  box-shadow:0 24px 46px -24px rgba(239,68,68,.5); }
.hero:before { content:""; position:absolute; right:-70px; top:-95px; width:265px; height:265px;
  background:radial-gradient(circle, rgba(255,255,255,.34), transparent 62%); }
.hero-emoji { font-size:2rem; line-height:1; }
.hero-title { font-size:1.75rem; font-weight:800; margin:6px 0 4px; }
.hero-sub { font-size:.96rem; opacity:.96; max-width:1080px; line-height:1.5; }
.hero-chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
.hero-chip { background:rgba(255,255,255,.2); border:1px solid rgba(255,255,255,.42);
  border-radius:999px; padding:4px 12px; font-size:.78rem; font-weight:600; }

/* ---------- section headers ---------- */
.sec { display:flex; align-items:center; gap:12px; margin:18px 0 8px; }
.sec-bar { width:5px; height:36px; border-radius:6px; background:linear-gradient(180deg,#ef4444,#22c55e); }
.sec-t { font-size:1.12rem; font-weight:800; color:#0f172a; line-height:1.15; }
.sec-s { font-size:.83rem; color:#64748b; }

/* ---------- cards ---------- */
.badge { display:inline-block; padding:5px 14px; border-radius:999px; font-size:.78rem;
  font-weight:800; letter-spacing:.04em; }
.badge.bad { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; }
.badge.good { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
.note { background:linear-gradient(120deg,#f0f9ff,#ecfeff); border:1px solid #bae6fd;
  border-radius:16px; padding:14px 18px; color:#0c4a6e; font-size:.92rem; line-height:1.55; }
.card { background:#fff; border:1px solid #e9eef7; border-radius:16px; padding:14px 16px;
  box-shadow:0 18px 34px -30px rgba(15,23,42,.55); }

/* ---------- native widgets, restyled ---------- */
[data-testid="stMetric"] { background:#fff; border:1px solid #e9eef7; border-radius:14px; padding:12px 14px; }
[data-testid="stMetricLabel"] p { font-size:.72rem; letter-spacing:.07em; text-transform:uppercase; color:#64748b; }
[data-testid="stMetricValue"] { font-weight:800; color:#0f172a; }
[data-testid="stAlert"] { border-radius:14px; }
[data-testid="stPlotlyChart"] { background:#fff; border:1px solid #e9eef7; border-radius:18px;
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

# ===========================================================================
# UI LAYOUT
# ===========================================================================
st.markdown("""
<div class="hero">
  <div class="hero-emoji">🎢</div>
  <div class="hero-title">Smooth Rides vs. Jerky Rides</div>
  <div class="hero-sub">Imagine you're in a car. <b>Unsafe</b> is a driver who slams the gas pedal to the floor and
  stamps on the brakes. <b>Safe</b> is a gentle driver who eases in and out. Robots need to be smooth drivers
  so they don't wreck their gears.</div>
  <div class="hero-chips">
    <span class="hero-chip">⚡ Jerky = unsafe</span>
    <span class="hero-chip">🟢 Smooth = safe</span>
    <span class="hero-chip">Jerk-limited S-curve</span>
    <span class="hero-chip">Live re-calculation</span>
  </div>
</div>
""", unsafe_allow_html=True)

ss = st.session_state
if "executed" not in ss:
    ss["executed"] = False

with st.sidebar:
    st.markdown("""
    <div class="side-brand">
      <div class="t">⚙️ Robot Physics</div>
      <div class="s">Set the move, then compare the two drivers.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-sec">The journey</div>', unsafe_allow_html=True)
    D = st.slider("📏 Distance to Move (m)", 2.0, 60.0, 20.0, 1.0)
    V = st.slider("🏃 Max Speed (m/s)", 0.5, 6.0, 2.5, 0.1)
    A = st.slider("🚀 Max Acceleration", 0.5, 10.0, 3.0, 0.1)
    J = st.slider("🛑 Smoothness (Jerk Limit)", 0.5, 50.0, 8.0, 0.1, help="Lower = Smoother but slower. Higher = Jerky but fast.")

    st.markdown('<div class="side-sec">Compare</div>', unsafe_allow_html=True)
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

section("Motion profiles", "Two drivers, same journey: one stamps the pedals, one eases in and out.")
left_col, right_col = st.columns(2)

with left_col:
    if ss["executed"]:
        fig_u = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, row_heights=[0.55, 0.45])
        fig_u.add_trace(go.Scatter(x=xs_v, y=ys_v, mode="lines", name="v(t) unsafe", line=dict(color="#ef4444", width=3)), row=1, col=1)
        fig_u.update_layout(title="⚡ UNSAFE — Slams the gas pedal", height=430)
        # presentation-only annotations: the acceleration is a Dirac spike (no new data)
        fig_u.add_vline(x=0.0, line_dash="dot", line_color="#f97316", row=2, col=1)
        fig_u.add_vline(x=stop_t, line_dash="dot", line_color="#f97316", row=2, col=1)
        fig_u.add_annotation(x=stop_t / 2.0, y=0.5, xref="x2", yref="y2", showarrow=False,
                             text="⚠️ Acceleration = ∞  (infinite Dirac spike at both pedals)",
                             font=dict(color="#c2410c", size=12.5))
        fig_u.update_yaxes(title_text="velocity (m/s)", row=1, col=1)
        fig_u.update_yaxes(title_text="acceleration", row=2, col=1)
        fig_u.update_xaxes(title_text="time (s)", row=2, col=1)
        st.markdown('<span class="badge bad">⚡ UNSAFE DRIVER</span>', unsafe_allow_html=True)
        st.plotly_chart(polish(fig_u), use_container_width=True)
    else:
        st.markdown('<span class="badge bad">⚡ UNSAFE DRIVER</span>', unsafe_allow_html=True)
        st.warning("Press **⚡ Show Unsafe vs Safe** in the sidebar to reveal the jerky profile.")

with right_col:
    fig_s = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, row_heights=[0.55, 0.45])
    fig_s.add_trace(go.Scatter(x=t_s, y=v_s, mode="lines", name="v(t) safe", line=dict(color="#059669", width=3)), row=1, col=1)
    fig_s.add_trace(go.Scatter(x=t_s, y=a_s, mode="lines", name="a(t) safe", line=dict(color="#3b82f6", width=2.2)), row=2, col=1)
    fig_s.update_layout(title="🟢 SAFE — Gentle S-Curve", height=430)
    fig_s.update_yaxes(title_text="velocity (m/s)", row=1, col=1)
    fig_s.update_yaxes(title_text="acceleration", row=2, col=1)
    fig_s.update_xaxes(title_text="time (s)", row=2, col=1)
    st.markdown('<span class="badge good">🟢 SAFE DRIVER (S-curve)</span>', unsafe_allow_html=True)
    st.plotly_chart(polish(fig_s), use_container_width=True)

c1, c2 = st.columns(2)
c1.metric("⏱️ Safe Time", f"{tt_safe:.2f} s")
c2.metric("⚡ Ideal (Unsafe) Time", f"{D/V:.2f} s")

st.markdown("""
<div class="note" style="margin-top:14px">
  <b>🔧 What this means in the workshop.</b><br>
  A jerky start or stop is a mechanical shock: the gears, belts and joints take a hit every single time.
  <b>High jerk causes mechanical shock and gear wear. Limiting jerk ensures smooth, safe motion.</b><br>
  Drag the <b>Smoothness (Jerk Limit)</b> slider and watch the green/blue curves: a lower limit gives a wider,
  gentler acceleration ramp — safer, but the journey takes a little longer.
</div>
""", unsafe_allow_html=True)
