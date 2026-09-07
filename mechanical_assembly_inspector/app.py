# -*- coding: utf-8 -*-
import random, time, uuid
import streamlit as st

st.set_page_config(page_title="AI Robot Inspector", page_icon="🛠️", layout="wide")

# --- UI FIX ---
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e293b !important; }
[data-testid="stSidebar"] * { color: #f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background-color: #3b82f6 !important; color: white !important; border: none !important; }
.block-container {padding-top: 1.3rem; max-width: 1500px;}
</style>
""", unsafe_allow_html=True)

CLASSES = ["Correct Assembly", "Wheel Misalignment", "Motor Misalignment", "Loose Component", "Joint Error", "Gear Error", "Sensor Error"]
DIAGNOSTIC_DB = {
    "Correct Assembly": {"severity": "ok", "icon": "✅", "description": "All parts are aligned and firmly mounted.", "fix": "No action needed. Proceed to test run."},
    "Wheel Misalignment": {"severity": "critical", "icon": "🛞", "description": "Wheels are not perpendicular to the drive shaft.", "fix": "Check the axle connection and ensure the wheel is perpendicular to the motor shaft."},
    "Motor Misalignment": {"severity": "critical", "icon": "⚙️", "description": "Motor axis is offset from the gearbox.", "fix": "Loosen the motor mount, push the motor so the shaft and gearbox are coaxial, then re-tighten."},
    "Loose Component": {"severity": "warning", "icon": "🔩", "description": "A fastener or bracket is not torqued down.", "fix": "Torque down all screws/bolts and apply thread-locker."},
    "Joint Error": {"severity": "critical", "icon": "🦾", "description": "A servo joint is out of its calibrated range.", "fix": "Zero the joint, remove obstructions, and re-run calibration."},
    "Gear Error": {"severity": "critical", "icon": "⚙️", "description": "Excessive backlash or damaged teeth.", "fix": "Inspect gear train, adjust mesh gap, and apply grease."},
    "Sensor Error": {"severity": "warning", "icon": "📡", "description": "Sensor is misaligned or mis-wired.", "fix": "Verify mounting and wiring, then recalibrate thresholds."}
}

def mock_ai_predict(image):
    _ = image
    return random.choice(CLASSES), random.uniform(85.0, 98.0)

ss = st.session_state
if "report" not in ss: ss["report"] = None

st.title("🛠️ AI Robot Inspector")
st.info("👋 **Welcome!** Did you build your robot but it's acting weird? Upload a photo of your robot, and our AI will act like a digital mechanic to find out what's wrong!")

with st.sidebar:
    st.markdown("### 🩺 Diagnostic Report")
    report_box = st.empty()

uploaded = st.file_uploader("📤 Step 1: Upload a photo of your robot", type=["jpg", "jpeg", "png"])

if uploaded:
    st.image(uploaded, use_container_width=True, caption="Your Robot Build")
    if st.button("🔬 Analyze Mechanical Configuration", type="primary", use_container_width=True):
        with st.spinner("AI is inspecting your robot..."):
            time.sleep(1.2)
            label, conf = mock_ai_predict(uploaded)
            entry = DIAGNOSTIC_DB[label]
            ss["report"] = {"label": label, "confidence": round(conf, 1), "icon": entry["icon"], "severity": entry["severity"], "description": entry["description"], "fix": entry["fix"]}

with report_box.container():
    if ss["report"] is None:
        st.warning("🔍 Awaiting scan... Upload a photo and press Analyze.")
    else:
        r = ss["report"]
        st.markdown(f"### {r['icon']} {r['label']}")
        st.progress(int(r["confidence"]), text=f"Confidence: {r['confidence']}%")
        st.markdown(f"**📋 What's wrong:** {r['description']}")
        st.markdown(f"**🔧 How to fix it:** {r['fix']}")
        
        if r["severity"] == "ok": st.success("✅ Correct Assembly — all systems nominal.")
        elif r["severity"] == "warning": st.warning(f"⚠️ {r['label']} detected. Inspect before running.")
        else: st.error(f"⛔ {r['label']} detected. Do not operate until fixed.")