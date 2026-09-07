# 🛠️ Mechanical Assembly Error Detector (AI Digital Inspector)

Single-file Streamlit teaching app styled like a modern medical/technical
diagnostic tool. Students upload a photo of their physical robot build and an
"AI inspector" reports assembly mistakes with a confidence score and a
concrete fix.

## Run

```bash
pip install streamlit
streamlit run app.py
```

## What it shows

- **Main area** – image uploader (`st.file_uploader`) + photo preview
  (`st.image`) and the **🔬 Analyze** button with a
  *"Analyzing mechanical configuration…"* spinner.
- **Sidebar** – an **AI Diagnostic Report** card with:
  - Predicted condition (bold, with severity pill: OK / WARNING / CRITICAL),
  - Confidence as a progress bar (85–98 %),
  - Error description and a recommended fix,
  - Final verdict colour-coded with `st.success` / `st.warning` / `st.error`.
- **Mock AI** – `mock_ai_predict(image)` randomly returns one of the 7
  classes (`Correct Assembly`, `Wheel Misalignment`, `Motor Misalignment`,
  `Loose Component`, `Joint Error`, `Gear Error`, `Sensor Error`) with a
  realistic confidence. Swap its body for `model.predict(...)` when a real
  `.h5` checkpoint is available.
- **Diagnostic database** – a Python dict mapping every class to a
  severity, description and recommended fix (e.g. Wheel Misalignment →
  *"Check the axle connection and ensure the wheel is perpendicular to the
  motor shaft."*).
- Uploading a new photo invalidates the previous scan; each analysis gets a
  fresh SCAN ID.
