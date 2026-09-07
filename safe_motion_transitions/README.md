# 🎢 Safe vs Unsafe Robot Motion Transitions (S-curves)

Single-file Streamlit app that shows *why* robots use **jerk-limited
S-curve velocity profiles** instead of abrupt bang-bang steps.

## Run

```bash
pip install streamlit numpy plotly
streamlit run app.py
```

## What it shows

- **Sidebar** – target distance, max velocity, max acceleration, max jerk
  limit, and an **⚡ Execute** button.
- **Unsafe graph** (red/orange): velocity steps instantly to Vmax; the
  acceleration is a Dirac spike, drawn as a very sharp triangle.
- **Safe graph** (green/blue): a 3rd-order S-curve planned from the jerk
  limit — jerk → acceleration → velocity are integrated in numpy/closed
  form. Acceleration ramps up, holds, ramps down; velocity follows a smooth
  S shape.
- The safe graph **recalculates instantly** as you drag the jerk slider:
  a lower jerk limit makes the acceleration curve wider/smoother but
  increases the total transition time.
- Physics note below the graphs explains shock, gear wear and why jerk
  limiting matters.
