# 🗺️ 2D Motion Planning Demonstrator (A* & RRT)

Single-file Streamlit app that animates **A\*** and **RRT** path planning on
a 20×20 grid world.

## Run

```bash
pip install streamlit numpy pandas plotly
streamlit run app.py
```

## What it shows

- **Grid editor** (st.data_editor matrix): type `1` = obstacle (black),
  `2` = start (green), `3` = goal (red), `0` = empty. Or press
  *Random Maze*.
- **A\*** – best-first grid search with a priority queue (heapq) and the
  Manhattan-distance heuristic. Explored cells turn light blue, the live
  frontier orange.
- **RRT** – random sampling + nearest-node connection with configurable
  *step size* and *goal bias*; tree growth is animated.
- Live metrics after the run: **Nodes Explored**, **Path Length**,
  **Time Taken**. Final path drawn in bright yellow.

> The click-to-paint alternative (`streamlit-plotly-events`) is avoided on
> purpose so this file stays dependency-light and robust.
