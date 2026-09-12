# -*- coding: utf-8 -*-
"""
Real AI Mechanical Inspector
------------------------------------------------------------
UI polish pass only.
The AI pipeline is UNCHANGED: same TensorFlow/MobileNetV2 few-shot
embedding, same cosine similarity scoring, same reference-image folder
lookup and same diagnostic database (only two missing emoji glyphs were
restored for the icons).
"""
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Real AI Robot Inspector", page_icon="🛠️", layout="wide")

# ===========================================================================
# UI THEME  (presentation only)
# ===========================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
html, body, [class*="css"] { font-family:'Inter','Segoe UI',system-ui,sans-serif; }
.stApp {
  background:
    radial-gradient(1000px 500px at 4% -12%, #e0f2fe 0%, transparent 58%),
    radial-gradient(900px 480px at 104% 0%, #ecfeff 0%, transparent 55%),
    #f6f9fc;
}
.block-container { padding-top:1.05rem; max-width:1520px; }
h1, h2, h3 { color:#0f172a !important; letter-spacing:-.02em; }

/* ---------- dark sidebar (consistent with the other tools) ---------- */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#1e293b 0%,#0b1220 100%) !important;
  border-right:1px solid #0b1220; }
[data-testid="stSidebar"] * { color:#f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background:linear-gradient(120deg,#0369a1,#06b6d4) !important;
  color:#fff !important; border:none !important; border-radius:12px !important; font-weight:700 !important; }
[data-testid="stSidebar"] details { background:rgba(255,255,255,.05) !important;
  border:1px solid rgba(255,255,255,.12) !important; border-radius:12px !important; }
.side-brand { background:linear-gradient(120deg,#075985,#06b6d4); border-radius:16px; padding:14px 16px;
  box-shadow:0 16px 28px -20px rgba(0,0,0,.9); }
.side-brand .t { font-weight:800; font-size:1.02rem; }
.side-brand .s { font-size:.79rem; opacity:.93; }
.side-sec { display:flex; align-items:center; gap:8px; font-size:.71rem; font-weight:800;
  letter-spacing:.11em; text-transform:uppercase; opacity:.72; margin:16px 0 4px; }
.side-sec:before { content:""; width:14px; height:3px; border-radius:3px; background:#22d3ee; }
.side-step { background:rgba(34,211,238,.12); border:1px solid rgba(34,211,238,.32);
  border-radius:12px; padding:9px 12px; font-size:.83rem; line-height:1.5; margin-bottom:7px; }

/* ---------- hero ---------- */
.hero { position:relative; overflow:hidden; border-radius:22px; padding:20px 26px; color:#fff;
  background:linear-gradient(120deg,#0c4a6e 0%, #0284c7 55%, #22d3ee 100%);
  box-shadow:0 24px 46px -24px rgba(2,132,199,.6); }
.hero:before { content:""; position:absolute; right:-70px; top:-95px; width:265px; height:265px;
  background:radial-gradient(circle, rgba(255,255,255,.4), transparent 62%); }
.hero-emoji { font-size:2rem; line-height:1; }
.hero-title { font-size:1.75rem; font-weight:800; margin:6px 0 4px; }
.hero-sub { font-size:.96rem; opacity:.95; max-width:1080px; line-height:1.5; }
.hero-chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
.hero-chip { background:rgba(255,255,255,.2); border:1px solid rgba(255,255,255,.42);
  border-radius:999px; padding:4px 12px; font-size:.78rem; font-weight:600; }

/* ---------- section headers ---------- */
.sec { display:flex; align-items:center; gap:12px; margin:18px 0 8px; }
.sec-bar { width:5px; height:36px; border-radius:6px; background:linear-gradient(180deg,#075985,#22d3ee); }
.sec-t { font-size:1.12rem; font-weight:800; color:#0f172a; line-height:1.15; }
.sec-s { font-size:.83rem; color:#64748b; }

/* ---------- cards (diagnostic panel look) ---------- */
.card { background:#fff; border:1px solid #e2eef7; border-radius:16px; padding:14px 16px;
  box-shadow:0 18px 34px -30px rgba(15,23,42,.55); }
.panel { background:#fff; border:1px solid #dbeafe; border-radius:18px; padding:16px 18px;
  box-shadow:0 22px 40px -34px rgba(2,132,199,.6); }
.note { background:linear-gradient(120deg,#f0f9ff,#ecfeff); border:1px solid #bae6fd;
  border-radius:16px; padding:14px 18px; color:#0c4a6e; font-size:.92rem; line-height:1.55; }
.kpi-row { display:flex; gap:10px; flex-wrap:wrap; margin:8px 0 2px; }
.kpi { flex:1 1 130px; background:#fff; border:1px solid #e2eef7; border-left:4px solid #0284c7;
  border-radius:14px; padding:10px 13px; }
.kpi-v { font-size:1.1rem; font-weight:800; color:#0f172a; }
.kpi-l { font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; color:#64748b; }
.pill { display:inline-block; padding:5px 14px; border-radius:999px; font-size:.76rem;
  font-weight:800; letter-spacing:.05em; color:#fff; }
.pill.ok { background:#059669; }
.pill.warning { background:#d97706; }
.pill.critical { background:#dc2626; }
.diagnosis-title { font-size:1.35rem; font-weight:800; color:#0f172a; margin:6px 0 2px; }
.diagnosis-sub { font-size:.85rem; color:#64748b; }

/* ---------- result cards (class names kept from the original app) ---------- */
.error-card { background:linear-gradient(120deg,#fee2e2,#fef2f2); border:1px solid #ef4444;
  color:#991b1b; padding:14px 16px; border-radius:14px; margin-bottom:10px; font-weight:600;
  font-size:.92rem; line-height:1.55; }
.success-card { background:linear-gradient(120deg,#dcfce7,#f0fdf4); border:1px solid #22c55e;
  color:#166534; padding:14px 16px; border-radius:14px; margin-bottom:10px; font-weight:600;
  font-size:.92rem; line-height:1.55; }

/* ---------- native widgets, restyled ---------- */
[data-testid="stAlert"] { border-radius:14px; }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#0284c7,#22d3ee); border-radius:999px; }
[data-testid="stFileUploaderDropzone"] { border:2px dashed #7dd3fc !important; border-radius:16px !important;
  background:linear-gradient(120deg,#f0f9ff,#ecfeff) !important; padding:14px !important; }
[data-testid="stImage"] img { border-radius:14px; }
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


# --- DIAGNOSTIC DATABASE ---
DIAGNOSTIC_DB = {
    "Correct Assembly": {"severity": "ok", "icon": "✅", "desc": "All parts aligned.", "fix": "No action needed."},
    "Wheel Misalignment": {"severity": "critical", "icon": "🛞", "desc": "Wheels not perpendicular.", "fix": "Check axle connection."},
    "Motor Misalignment": {"severity": "critical", "icon": "⚙️", "desc": "Motor axis offset.", "fix": "Re-align motor shaft."},
    "Loose Component": {"severity": "warning", "icon": "🔩", "desc": "Fastener not torqued.", "fix": "Tighten all screws."},
    "Joint Error": {"severity": "critical", "icon": "🦾", "desc": "Joint out of range.", "fix": "Zero and recalibrate joint."},
    "Gear Error": {"severity": "critical", "icon": "⚙️", "desc": "Gear backlash/damage.", "fix": "Inspect gear train."},
    "Sensor Error": {"severity": "warning", "icon": "📡", "desc": "Sensor misaligned.", "fix": "Verify mounting and wiring."}
}

# --- FIXED: Match your actual folder names ---
CLASS_MAP = {
    "correct": "Correct Assembly", 
    "wheel_misalignment": "Wheel Misalignment", 
    "motor_driver_misalignment": "Motor Misalignment", 
    "loose_component": "Loose Component", 
    "joint_error": "Joint Error", 
    "gear_error": "Gear Error", 
    "sensor_error": "Sensor Error"
}

# --- LOAD REAL AI MODEL ---
@st.cache_resource
def load_model():
    return MobileNetV2(weights='imagenet', include_top=False, pooling='avg')

model = load_model()

def get_embedding(img_path):
    """Converts image to a 1280-dimensional AI feature vector."""
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return model.predict(img_array, verbose=0)[0]

def cosine_similarity(vec1, vec2):
    """Calculates mathematical similarity between two AI feature vectors."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

def analyze_image(uploaded_img):
    """Compares uploaded image against reference images using Few-Shot Embedding."""
    # Save uploaded image temporarily
    img_path = "temp_uploaded.jpg"
    with open(img_path, "wb") as f:
        f.write(uploaded_img.getbuffer())
    
    uploaded_vec = get_embedding(img_path)
    
    # --- FIXED: Get path relative to this script ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ref_dir = os.path.join(script_dir, "reference_images")
    
    if not os.path.exists(ref_dir):
        st.error(f"Reference folder not found at: {ref_dir}")
        return None, 0.0
    
    scores = {}
    
    for folder_name, class_name in CLASS_MAP.items():
        folder_path = os.path.join(ref_dir, folder_name)
        if not os.path.exists(folder_path):
            continue
        
        folder_scores = []
        for img_file in os.listdir(folder_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                ref_vec = get_embedding(os.path.join(folder_path, img_file))
                sim = cosine_similarity(uploaded_vec, ref_vec)
                folder_scores.append(sim)
        
        if folder_scores:
            scores[class_name] = np.mean(folder_scores)
            
    if not scores:
        return None, 0.0
    return max(scores, key=scores.get), max(scores.values()) * 100

# ===========================================================================
# UI LAYOUT
# ===========================================================================
st.markdown("""
<div class="hero">
  <div class="hero-emoji">🛠️</div>
  <div class="hero-title">Real AI Mechanical Inspector</div>
  <div class="hero-sub">Upload a photo of your robot build. The inspector converts it into a 1280-dimension
  <b>AI feature vector</b> (MobileNetV2) and compares it with your reference images using
  <b>few-shot embedding similarity</b> to name the fault and tell you how to fix it.</div>
  <div class="hero-chips">
    <span class="hero-chip">MobileNetV2 embeddings</span>
    <span class="hero-chip">Cosine similarity</span>
    <span class="hero-chip">7 diagnostic classes</span>
    <span class="hero-chip">Repair instructions</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="side-brand">
      <div class="t">🩺 Inspection Console</div>
      <div class="s">Photo in → diagnosis out.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-sec">How the inspector works</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="side-step">1️⃣ <b>Upload</b> a clear photo of the assembled robot.</div>
    <div class="side-step">2️⃣ The photo becomes a <b>feature vector</b> — a numerical "fingerprint".</div>
    <div class="side-step">3️⃣ It is compared with every image in <code>reference_images/</code> folders.</div>
    <div class="side-step">4️⃣ The closest matching fault class is reported with its <b>similarity score</b>.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-sec">Diagnostic classes</div>', unsafe_allow_html=True)
    for _cls, _info in DIAGNOSTIC_DB.items():
        _colour = {"ok": "#059669", "warning": "#d97706", "critical": "#dc2626"}[_info["severity"]]
        st.markdown(
            f"<div style='font-size:.82rem;margin:3px 0'>"
            f"<span style='color:{_colour}'>{_info['icon']}</span> {_cls}"
            f"<span style='opacity:.6'> — {_info['desc']}</span></div>",
            unsafe_allow_html=True,
        )

    with st.expander("📁 Reference image folders"):
        st.caption("Expected sub-folders inside reference_images/")
        st.code("\n".join(CLASS_MAP.keys()), language="text")

section("Step 1 — Upload a photo", "A sharp, well-lit picture of the whole assembly works best.")
uploaded = st.file_uploader(" Step 1: Upload a photo of your robot", type=["jpg", "jpeg", "png"])

if uploaded:
    left, right = st.columns([1.15, 1], gap="medium")
    with left:
        st.markdown("<div class='card' style='padding:10px 14px 4px'><b>🖼️ Uploaded image</b></div>",
                    unsafe_allow_html=True)
        st.image(uploaded, width=450, caption="Uploaded Image")
    with right:
        st.markdown(f"""
        <div class="kpi-row">
          <div class="kpi"><div class="kpi-l">File</div><div class="kpi-v" style="font-size:.95rem">{uploaded.name[:22]}</div></div>
          <div class="kpi"><div class="kpi-l">Size</div><div class="kpi-v">{uploaded.size/1024:.0f} KB</div></div>
          <div class="kpi"><div class="kpi-l">Classes compared</div><div class="kpi-v">{len(CLASS_MAP)}</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="note" style="margin-top:12px">
          <b>Ready to inspect.</b><br>
          The model will be run on your photo and on every reference image, then the
          <b>cosine similarity</b> between the vectors picks the closest class.
        </div>
        """, unsafe_allow_html=True)

    section("Step 2 — Run the AI inspection", "Feature extraction + similarity scoring on your photo.")
    if st.button("🔬 Run Real AI Analysis", type="primary", use_container_width=True):
        with st.spinner("Extracting AI feature vectors and calculating cosine similarity..."):
            predicted_class, confidence = analyze_image(uploaded)
            
            if predicted_class and confidence > 0:
                entry = DIAGNOSTIC_DB[predicted_class]
                pill_cls = {"ok": "ok", "warning": "warning", "critical": "critical"}[entry['severity']]
                pill_txt = {"ok": "OK — NO FAULT", "warning": "WARNING", "critical": "CRITICAL FAULT"}[entry['severity']]
                st.markdown("---")
                st.markdown(f"""
                <div class="panel">
                  <span class="pill {pill_cls}">{pill_txt}</span>
                  <div class="diagnosis-title">{entry['icon']} Diagnosis: {predicted_class}</div>
                  <div class="diagnosis-sub">Few-shot embedding match against your reference images</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(int(confidence), text=f"Similarity Score: {confidence:.1f}%")
                
                if entry['severity'] == 'ok':
                    st.markdown(f'<div class="success-card">✅ <b>Description:</b> {entry["desc"]}<br><b>Fix:</b> {entry["fix"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-card">❌ <b>Description:</b> {entry["desc"]}<br><b>Fix:</b> {entry["fix"]}</div>', unsafe_allow_html=True)
            else:
                st.error("❌ Reference images folder is missing or empty! Please check the reference_images folder.")
                st.info(" Make sure you have images in the reference_images subfolders.")
else:
    st.markdown("""
    <div class="note">
      👆 <b>Upload a photo to start the AI scan.</b><br>
      Tip: take the picture straight on, with the whole robot visible — the model compares overall
      appearance, so distance and angle matter.
    </div>
    """, unsafe_allow_html=True)
