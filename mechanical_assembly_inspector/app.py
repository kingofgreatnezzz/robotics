# -*- coding: utf-8 -*-
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Real AI Robot Inspector", page_icon="🛠️", layout="wide")

# --- UI STYLING ---
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e293b !important; }
[data-testid="stSidebar"] * { color: #f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background-color: #3b82f6 !important; color: white !important; border: none !important; }
.stApp { background-color: #ffffff !important; }
h1, h2, h3 { color: #0f172a !important; }
.error-card { background-color: #fee2e2; border: 1px solid #ef4444; color: #991b1b; padding: 12px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; }
.success-card { background-color: #dcfce7; border: 1px solid #22c55e; color: #166534; padding: 12px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- DIAGNOSTIC DATABASE ---
DIAGNOSTIC_DB = {
    "Correct Assembly": {"severity": "ok", "icon": "✅", "desc": "All parts aligned.", "fix": "No action needed."},
    "Wheel Misalignment": {"severity": "critical", "icon": "🛞", "desc": "Wheels not perpendicular.", "fix": "Check axle connection."},
    "Motor Misalignment": {"severity": "critical", "icon": "️", "desc": "Motor axis offset.", "fix": "Re-align motor shaft."},
    "Loose Component": {"severity": "warning", "icon": "🔩", "desc": "Fastener not torqued.", "fix": "Tighten all screws."},
    "Joint Error": {"severity": "critical", "icon": "", "desc": "Joint out of range.", "fix": "Zero and recalibrate joint."},
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

# --- UI LAYOUT ---
st.title("🛠️ Real AI Mechanical Inspector")
st.info("👋 **Welcome!** This uses **Few-Shot Embedding Similarity** with MobileNetV2. Upload a photo to compare its AI feature vector against reference images.")

uploaded = st.file_uploader(" Step 1: Upload a photo of your robot", type=["jpg", "jpeg", "png"])

if uploaded:
    st.image(uploaded, use_container_width=True, caption="Uploaded Image")
    
    if st.button("🔬 Run Real AI Analysis", type="primary", use_container_width=True):
        with st.spinner("Extracting AI feature vectors and calculating cosine similarity..."):
            predicted_class, confidence = analyze_image(uploaded)
            
            if predicted_class and confidence > 0:
                entry = DIAGNOSTIC_DB[predicted_class]
                st.markdown("---")
                st.subheader(f"{entry['icon']} Diagnosis: {predicted_class}")
                st.progress(int(confidence), text=f"Similarity Score: {confidence:.1f}%")
                
                if entry['severity'] == 'ok':
                    st.markdown(f'<div class="success-card">✅ <b>Description:</b> {entry["desc"]}<br><b>Fix:</b> {entry["fix"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-card">❌ <b>Description:</b> {entry["desc"]}<br><b>Fix:</b> {entry["fix"]}</div>', unsafe_allow_html=True)
            else:
                st.error("❌ Reference images folder is missing or empty! Please check the reference_images folder.")
                st.info(" Make sure you have images in the reference_images subfolders.")
else:
    st.info("👆 Upload a photo to start the AI scan.")