# 🤖 Robot Posture Validation Framework (Perfect Pose Checker)

Single-file Streamlit engineering dashboard for calibrating a 3-link robot
arm to a reference posture.

## Run

```bash
pip install streamlit plotly
streamlit run app.py
```

## What it shows

- **Sidebar** – sliders for Base / Shoulder / Elbow joint angles (0–180°),
  a **✔ Validate Posture** button and a **🎯 Snap to reference** shortcut.
- **Live kinematics** – the arm is drawn with forward kinematics
  (`x = L1·cos θ1 + L2·cos(θ1+θ2) + …`) and updates instantly as sliders
  move; the hard-coded reference pose (45°/90°/45°) is shown behind it as a
  faint dotted grey line.
- **Validation report** – a colour-coded table (Target / Actual / Error /
  Status) per joint: green ✔ within ±5°, red ✘ otherwise, with an
  *"Adjust Joint X by Y°"* instruction. An overall PASS/FAIL badge plus a
  staleness warning when angles change after validation.
