# 🦗 Hexapod Leg Coordination Simulator (CPG)

Single-file Streamlit app that teaches how a 6-legged robot coordinates its
legs with **Central Pattern Generators** (sine oscillators + phase offsets).

## Run

```bash
pip install streamlit numpy plotly
streamlit run app.py
```

## What it shows

- **Sidebar** – gait selector (Tripod / Ripple / Wave), speed (frequency),
  duty factor slider, demo duration.
- **Top view** – circle body + 6 legs. Dark, full-length legs are in
  *stance* (on the ground); short, faint legs are *swinging* in the air.
- **Bottom chart** – live scrolling Plotly chart of the six CPG sine waves,
  with the stance threshold for the chosen duty factor.
- Legs on the ground push backward in phase with the sine oscillators;
  stance window width == duty factor of the cycle.
