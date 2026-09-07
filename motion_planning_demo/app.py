# -*- coding: utf-8 -*-
import heapq, math, random, time, numpy as np, pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Robot Maze Solver", page_icon="🗺️", layout="wide")

# --- DARK SIDEBAR FIX ---
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e293b !important; }
[data-testid="stSidebar"] * { color: #f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background-color: #3b82f6 !important; color: white !important; border: none !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { color: #0f172a !important; }
[data-testid="stSidebar"] .stSlider * { color: #f8fafc !important; }
.block-container {padding-top: 1.3rem; max-width: 1500px;}
h1, h2, h3 {color: #0f172a;}
</style>
""", unsafe_allow_html=True)

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
    return fig

ss = st.session_state
if "grid" not in ss:
    ss["grid"] = make_grid()

st.title("🗺️ Robot Maze Solver")
st.info("👋 **Watch the robot find its way!** The robot starts at the **GREEN 'S'** and needs to reach the **RED 'G'**. Press 'Run Planner' to see it think and move!")

with st.sidebar:
    st.markdown("### 🧠 Robot Brain")
    algo = st.selectbox("Which algorithm?", ["A* (Smart & Direct)"], help="A* checks every path to find the shortest route!")
    
    st.markdown("---")
    st.markdown("**🏗️ Quick Maze Builders**")
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
        
    run = st.button("▶ Run Planner", type="primary", use_container_width=True)
    metrics_ph = st.empty()

left, right = st.columns([1.0, 1.05])
with left:
    st.markdown("**✏️ Manual Grid Editor** *(Optional: Type 1 for walls, or use the sidebar buttons!)*")
    grid_df = pd.DataFrame(ss["grid"])
    edited = st.data_editor(grid_df, key="grid_editor", num_rows="fixed", height=520, use_container_width=True)
    ss["grid"] = edited.to_numpy().astype(int)

with right:
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
    st.markdown("**📊 Brain Stats**")
    mc = st.columns(3)
    mc[0].metric("Cells Explored", m_nodes)
    mc[1].metric("Path Length", m_len)
    mc[2].metric("Time Taken", m_time)