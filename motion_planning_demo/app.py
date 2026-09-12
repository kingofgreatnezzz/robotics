# -*- coding: utf-8 -*-
"""
Robot Maze Solver
------------------------------------------------------------
UI polish pass only.
The planning logic is UNCHANGED: same grid codes, same colours, same
A* implementation, same animations and timings.
"""
import heapq, math, random, time, numpy as np, pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Robot Maze Solver", page_icon="🗺️", layout="wide")

# ===========================================================================
# UI THEME  (presentation only)
# ===========================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
html, body, [class*="css"] { font-family:'Inter','Segoe UI',system-ui,sans-serif; }
.stApp {
  background:
    radial-gradient(1100px 520px at 4% -12%, #eef0ff 0%, transparent 58%),
    radial-gradient(900px 480px at 104% 0%, #e0f2fe 0%, transparent 55%),
    #f6f8fc;
}
.block-container { padding-top:1.05rem; max-width:1540px; }
h1,h2,h3,h4 { color:#0f172a; letter-spacing:-.02em; }

/* ---------- dark sidebar (kept from the original fix, refined) ---------- */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#1e293b 0%,#111a2e 100%) !important;
  border-right:1px solid #0b1220; }
[data-testid="stSidebar"] * { color:#f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background:linear-gradient(120deg,#3730a3,#4f46e5) !important;
  color:#fff !important; border:none !important; border-radius:12px !important; font-weight:700 !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { color:#0f172a !important; }
[data-testid="stSidebar"] .stSlider * { color:#f8fafc !important; }
[data-testid="stSidebar"] details { background:rgba(255,255,255,.05) !important;
  border:1px solid rgba(255,255,255,.12) !important; border-radius:12px !important; }
[data-testid="stSidebar"] [data-testid="stMetric"] { background:rgba(255,255,255,.07) !important;
  border:1px solid rgba(255,255,255,.16) !important; border-radius:14px !important; padding:10px 12px !important; }
.side-brand { background:linear-gradient(120deg,#3730a3,#4f46e5); border-radius:16px; padding:14px 16px;
  box-shadow:0 16px 28px -20px rgba(0,0,0,.9); }
.side-brand .t { font-weight:800; font-size:1.02rem; }
.side-brand .s { font-size:.79rem; opacity:.93; }
.side-sec { display:flex; align-items:center; gap:8px; font-size:.71rem; font-weight:800;
  letter-spacing:.11em; text-transform:uppercase; opacity:.72; margin:16px 0 4px; }
.side-sec:before { content:""; width:14px; height:3px; border-radius:3px; background:#818cf8; }

/* ---------- hero ---------- */
.hero { position:relative; overflow:hidden; border-radius:22px; padding:20px 26px; color:#fff;
  background:linear-gradient(120deg,#312e81 0%, #4f46e5 58%, #818cf8 100%);
  box-shadow:0 24px 46px -24px rgba(79,70,229,.55); }
.hero:before { content:""; position:absolute; right:-70px; top:-95px; width:265px; height:265px;
  background:radial-gradient(circle, rgba(255,255,255,.38), transparent 62%); }
.hero-emoji { font-size:2rem; line-height:1; }
.hero-title { font-size:1.75rem; font-weight:800; margin:6px 0 4px; }
.hero-sub { font-size:.96rem; opacity:.95; max-width:1080px; line-height:1.5; }
.hero-chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
.hero-chip { background:rgba(255,255,255,.2); border:1px solid rgba(255,255,255,.4);
  border-radius:999px; padding:4px 12px; font-size:.78rem; font-weight:600; }

/* ---------- section headers ---------- */
.sec { display:flex; align-items:center; gap:12px; margin:18px 0 8px; }
.sec-bar { width:5px; height:36px; border-radius:6px; background:linear-gradient(180deg,#3730a3,#818cf8); }
.sec-t { font-size:1.12rem; font-weight:800; color:#0f172a; line-height:1.15; }
.sec-s { font-size:.83rem; color:#64748b; }

/* ---------- cards / legend ---------- */
.card { background:#fff; border:1px solid #e8eaf8; border-radius:16px; padding:14px 16px;
  box-shadow:0 18px 34px -30px rgba(15,23,42,.55); }
.note { background:linear-gradient(120deg,#eef2ff,#f5f3ff); border:1px solid #c7d2fe;
  border-radius:16px; padding:13px 17px; color:#3730a3; font-size:.91rem; line-height:1.55; }
.legend-chip { display:inline-block; padding:4px 12px; border-radius:999px; font-size:.76rem;
  font-weight:700; margin:2px 6px 2px 0; border:1px solid #e2e8f0; background:#fff; color:#334155; }

/* ---------- native widgets, restyled ---------- */
[data-testid="stMetric"] { background:#fff; border:1px solid #e8eaf8; border-radius:14px; padding:12px 14px; }
[data-testid="stMetricLabel"] p { font-size:.72rem; letter-spacing:.07em; text-transform:uppercase; color:#64748b; }
[data-testid="stMetricValue"] { font-weight:800; color:#0f172a; }
[data-testid="stAlert"] { border-radius:14px; }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#4f46e5,#818cf8); border-radius:999px; }
[data-testid="stPlotlyChart"] { background:#fff; border:1px solid #e8eaf8; border-radius:18px;
  padding:8px 8px 2px; box-shadow:0 20px 36px -32px rgba(15,23,42,.6); }
[data-testid="stDataFrame"] { border-radius:14px; overflow:hidden; border:1px solid #e8eaf8; }
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


N = 20
EMPTY, WALL, START, GOAL = 0, 1, 2, 3
D_EMPTY, D_WALL, D_START, D_GOAL, D_EXPL, D_FRONTIER, D_PATH = range(7)
COLORSCALE = [[0.0,"#ffffff"],[1/6,"#111111"],[2/6,"#10b981"],[3/6,"#ef4444"],[4/6,"#93c5fd"],[5/6,"#fdba74"],[1.0,"#fde047"]]

def make_grid(wall_count=34):
    g = np.zeros((N, N), dtype=int)
    g[0, :] = g[-1, :] = g[:, 0] = g[:, -1] = WALL
    rng = random.Random(7)
    for _ in range(wall_count):
        r, c = rng.randint(2, N - 3), rng.randint(2, N - 3)
        g[r, c] = WALL
    g[1, 1] = START
    g[N - 2, N - 2] = GOAL
    return g

def astar(grid, start, goal):
    occ = np.array(grid) == WALL
    h = lambda rc: abs(rc[0] - goal[0]) + abs(rc[1] - goal[1])
    open_heap = [(h(start), 0, start)]
    counter = 1
    g_score = {start: 0}
    came = {}
    closed = set()
    events = []
    while open_heap:
        _, _, cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        closed.add(cur)
        events.append(("close", cur))
        if cur == goal:
            path = []
            n = goal
            while n in came:
                path.append(n)
                n = came[n]
            path.append(start)
            path.reverse()
            return events, path, {"explored": len(closed)}
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nb = (cur[0]+dr, cur[1]+dc)
            if 0<=nb[0]<N and 0<=nb[1]<N and not occ[nb] and nb not in closed:
                tent = g_score[cur] + 1
                if tent < g_score.get(nb, math.inf):
                    came[nb] = cur
                    g_score[nb] = tent
                    heapq.heappush(open_heap, (tent+h(nb), counter, nb))
                    counter += 1
                    events.append(("open", nb))
    return events, [], {"explored": len(closed)}

def build_figure(display, path_px=None, current_pos=None):
    fig = go.Figure(go.Heatmap(z=display, zmin=0, zmax=6, colorscale=COLORSCALE, showscale=False, hoverinfo="skip"))
    if path_px and len(path_px) > 1:
        fig.add_trace(go.Scatter(x=[p[0] for p in path_px], y=[p[1] for p in path_px], mode="lines", line=dict(color="#fde047", width=5), showlegend=False))
    if current_pos:
        fig.add_trace(go.Scatter(x=[current_pos[0]], y=[current_pos[1]], mode="markers", marker=dict(size=18, color="#fbbf24", symbol="circle", line=dict(color="#000", width=2)), showlegend=False))
    fig.update_layout(height=580, margin=dict(l=5,r=5,t=5,b=5), xaxis=dict(dtick=1, range=[-0.5, N-0.5], constrain="domain"), yaxis=dict(dtick=1, range=[N-0.5, -0.5], constrain="domain", scaleanchor="x", scaleratio=1))
    return polish(fig)

ss = st.session_state
if "grid" not in ss:
    ss["grid"] = make_grid()

# ===========================================================================
# UI LAYOUT
# ===========================================================================
st.markdown("""
<div class="hero">
  <div class="hero-emoji">🗺️</div>
  <div class="hero-title">Robot Maze Solver</div>
  <div class="hero-sub">Watch a robot work out the shortest way through a maze. It starts on the <b>GREEN S</b>,
  thinks about the routes (the blue squares it checks), then drives along the winning path to the <b>RED G</b>.</div>
  <div class="hero-chips">
    <span class="hero-chip">A* pathfinding</span>
    <span class="hero-chip">20 × 20 world</span>
    <span class="hero-chip">Live "thinking" animation</span>
    <span class="hero-chip">Build your own maze</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="side-brand">
      <div class="t">🧠 Robot Brain</div>
      <div class="s">Pick a maze, then let the robot solve it.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-sec">Algorithm</div>', unsafe_allow_html=True)
    algo = st.selectbox("Which algorithm?", ["A* (Smart & Direct)"], help="A* checks every path to find the shortest route!")

    st.markdown('<div class="side-sec">🏗️ Quick Maze Builders</div>', unsafe_allow_html=True)
    if st.button("🏃 Empty Room", use_container_width=True):
        ss["grid"] = np.zeros((N, N), dtype=int)
        ss["grid"][0,:]=ss["grid"][-1,:]=ss["grid"][:,0]=ss["grid"][:,-1]=WALL
        ss["grid"][1,1]=START
        ss["grid"][N-2,N-2]=GOAL
        st.rerun()
    if st.button("🧱 Simple Maze", use_container_width=True):
        ss["grid"] = make_grid(20)
        st.rerun()
    if st.button("🌲 Complex Forest", use_container_width=True):
        ss["grid"] = make_grid(80)
        st.rerun()

    st.markdown('<div class="side-sec">Run</div>', unsafe_allow_html=True)
    run = st.button("▶ Run Planner", type="primary", use_container_width=True)
    metrics_ph = st.empty()

st.markdown(
    '<span class="legend-chip">▢ Empty floor</span>'
    '<span class="legend-chip" style="background:#111;color:#fff">▣ Wall</span>'
    '<span class="legend-chip" style="background:#10b981;color:#fff">S Start</span>'
    '<span class="legend-chip" style="background:#ef4444;color:#fff">G Goal</span>'
    '<span class="legend-chip" style="background:#93c5fd">Blue = checked</span>'
    '<span class="legend-chip" style="background:#fdba74">Orange = next to check</span>'
    '<span class="legend-chip" style="background:#fde047">Yellow = winning path</span>',
    unsafe_allow_html=True,
)

section("The maze", "Blue squares are places the robot already checked — watch it spread out from the start.")
left, right = st.columns([1.0, 1.05])
with left:
    st.markdown("<div class='card' style='padding:10px 14px'><b>✏️ Manual Grid Editor</b><br>"
                "<span style='font-size:.85rem;color:#64748b'>Optional: type <b>1</b> for walls, "
                "<b>2</b> for start, <b>3</b> for goal — or just use the sidebar buttons!</span></div>",
                unsafe_allow_html=True)
    grid_df = pd.DataFrame(ss["grid"])
    edited = st.data_editor(grid_df, key="grid_editor", num_rows="fixed", height=520, use_container_width=True)
    ss["grid"] = edited.to_numpy().astype(int)

with right:
    st.markdown("<div class='card' style='padding:10px 14px;margin-bottom:6px'>"
                "<b>🤖 Robot view</b> <span style='font-size:.85rem;color:#64748b'>"
                "— live map and animation</span></div>", unsafe_allow_html=True)
    map_ph = st.empty()
    status_ph = st.empty()
    map_ph.plotly_chart(build_figure(ss["grid"].copy()), use_container_width=True, key="map_idle")
    status_ph.markdown("_Robot is idle — press Run Planner to start!_")

m_nodes = m_len = m_time = "—"
if run:
    grid = ss["grid"]
    starts = list(map(tuple, np.argwhere(grid == START)))
    goals = list(map(tuple, np.argwhere(grid == GOAL)))
    if not starts or not goals:
        st.error("Set a start (2) and goal (3) first!")
    else:
        start_cell, goal_cell = starts[0], goals[0]
        t0 = time.perf_counter()
        events, path, stats = astar(grid, start_cell, goal_cell)
        plan_s = (time.perf_counter() - t0) * 1000.0
        
        display = np.zeros((N, N), dtype=int)
        for r in range(N):
            for c in range(N):
                display[r, c] = {EMPTY:D_EMPTY, WALL:D_WALL, START:D_START, GOAL:D_GOAL}[grid[r,c]]
        
        # ANIMATE EXPLORATION (SLOWER SO YOU CAN SEE IT)
        for k, (kind, cell) in enumerate(events):
            r, c = cell
            if grid[r, c] in (START, GOAL):
                continue
            display[r, c] = D_FRONTIER if kind == "open" else D_EXPL
            if k % 8 == 0:  # Update every 8 steps for smoother animation
                map_ph.plotly_chart(build_figure(display), use_container_width=True, key=f"astar_{k}")
                time.sleep(0.03)  # SLOW DOWN THE ANIMATION
                
        if path:
            # ANIMATE THE PATH BEING DRAWN
            status_ph.info("🤖 **Robot is moving along the path...**")
            for i, (r, c) in enumerate(path):
                if grid[r, c] not in (START, GOAL):
                    display[r, c] = D_PATH
                map_ph.plotly_chart(build_figure(display, current_pos=(c, r)), use_container_width=True, key=f"path_{i}")
                time.sleep(0.15)  # SLOW DOWN PATH ANIMATION SO YOU SEE THE ROBOT MOVE
            
            # FINAL VIEW
            map_ph.plotly_chart(build_figure(display), use_container_width=True, key="map_final")
            status_ph.success("✅ **Goal reached!** The yellow line is the safest path from GREEN to RED.")
            m_nodes, m_len, m_time = str(stats["explored"]), str(len(path)-1), f"{plan_s:.1f} ms"
        else:
            status_ph.error("❌ No path found. The maze is blocked!")

with metrics_ph.container():
    st.markdown('<div class="side-sec">📊 Brain Stats</div>', unsafe_allow_html=True)
    mc = st.columns(3)
    mc[0].metric("Cells Explored", m_nodes)
    mc[1].metric("Path Length", m_len)
    mc[2].metric("Time Taken", m_time)
