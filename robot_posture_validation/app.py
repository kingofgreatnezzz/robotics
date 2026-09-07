# -*- coding: utf-8 -*-
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Robot Posture Checker", page_icon="🦾", layout="wide")

# --- DARK SIDEBAR FIX ---
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e293b !important; }
[data-testid="stSidebar"] * { color: #f8fafc !important; }
[data-testid="stSidebar"] .stButton > button { background-color: #3b82f6 !important; color: white !important; border: none !important; }
[data-testid="stSidebar"] .stSlider * { color: #f8fafc !important; }
.block-container {padding-top: 1.3rem; max-width: 1500px;}
h1, h2, h3 {color: #0f172a;}
</style>
""", unsafe_allow_html=True)

# Reference posture (the "perfect" pose)
REFERENCE = {"Base": 45, "Shoulder": 90, "Elbow": 45}
TOLERANCE = 5  # degrees

def build_arm_fig(base_ang, shoulder_ang, elbow_ang, ref_base, ref_shoulder, ref_elbow):
    """Draw the robot arm with current angles and reference (dotted) overlay."""
    L1, L2, L3 = 2.0, 1.8, 1.5
    
    # Current arm
    x0, y0 = 0, 0
    x1 = L1 * math.cos(math.radians(base_ang))
    y1 = L1 * math.sin(math.radians(base_ang))
    x2 = x1 + L2 * math.cos(math.radians(base_ang + shoulder_ang))
    y2 = y1 + L2 * math.sin(math.radians(base_ang + shoulder_ang))
    x3 = x2 + L3 * math.cos(math.radians(base_ang + shoulder_ang + elbow_ang))
    y3 = y2 + L3 * math.sin(math.radians(base_ang + shoulder_ang + elbow_ang))
    
    # Reference arm (dotted gray)
    rx0, ry0 = 0, 0
    rx1 = L1 * math.cos(math.radians(ref_base))
    ry1 = L1 * math.sin(math.radians(ref_base))
    rx2 = rx1 + L2 * math.cos(math.radians(ref_base + ref_shoulder))
    ry2 = ry1 + L2 * math.sin(math.radians(ref_base + ref_shoulder))
    rx3 = rx2 + L3 * math.cos(math.radians(ref_base + ref_shoulder + ref_elbow))
    ry3 = ry2 + L3 * math.sin(math.radians(ref_base + ref_shoulder + ref_elbow))
    
    fig = go.Figure()
    
    # Reference arm (dotted gray)
    fig.add_trace(go.Scatter(x=[rx0, rx1, rx2, rx3], y=[ry0, ry1, ry2, ry3], mode="lines+markers", 
                             line=dict(color="#cbd5e1", width=3, dash="dot"), 
                             marker=dict(size=10, color="#cbd5e1"), name="Reference Pose", showlegend=True))
    
    # Current arm (solid colored)
    fig.add_trace(go.Scatter(x=[x0, x1, x2, x3], y=[y0, y1, y2, y3], mode="lines+markers", 
                             line=dict(color="#3b82f6", width=5), 
                             marker=dict(size=12, color="#1e40af"), name="Current Pose", showlegend=True))
    
    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), 
                      xaxis=dict(range=[-1, 6], visible=False), 
                      yaxis=dict(range=[-1, 6], visible=False),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    return fig

st.title("🦾 Robot Posture Validation")
st.info("👋 **Welcome!** Adjust the sliders to match the **dotted gray reference pose**. Green = correct, Red = needs adjustment!")

with st.sidebar:
    st.markdown("### ⚙️ Joint Controls")
    base = st.slider("🔄 Base Angle", 0, 180, 45)
    shoulder = st.slider("💪 Shoulder Angle", 0, 180, 90)
    elbow = st.slider("🦾 Elbow Angle", 0, 180, 45)
    
    validate = st.button("✅ Validate Posture", type="primary", use_container_width=True)
    
    with st.expander("🧠 For the Lecturers: The Math Behind the Magic"):
        st.markdown(f"**Reference angles:** Base={REFERENCE['Base']}°, Shoulder={REFERENCE['Shoulder']}°, Elbow={REFERENCE['Elbow']}°")
        st.caption("Forward kinematics: x = L1·cos(θ1) + L2·cos(θ1+θ2) + L3·cos(θ1+θ2+θ3)")

# Main display
col1, col2 = st.columns([1.2, 1])

with col1:
    fig = build_arm_fig(base, shoulder, elbow, REFERENCE["Base"], REFERENCE["Shoulder"], REFERENCE["Elbow"])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    if validate:
        st.markdown("### 📊 Validation Report")
        
        errors = {
            "Base": abs(base - REFERENCE["Base"]),
            "Shoulder": abs(shoulder - REFERENCE["Shoulder"]),
            "Elbow": abs(elbow - REFERENCE["Elbow"])
        }
        
        for joint, error in errors.items():
            if error <= TOLERANCE:
                st.success(f"✅ **{joint}**: {error:.1f}° error (Correct!)")
            else:
                st.error(f"❌ **{joint}**: {error:.1f}° error (Adjust by {error:.1f}°)")
        
        total_error = sum(errors.values())
        if total_error <= TOLERANCE * 3:
            st.balloons()
            st.success("🎉 **Perfect posture!** All joints are within tolerance.")
        else:
            st.warning(f"⚠️ Total error: {total_error:.1f}°. Keep adjusting!")
    else:
        st.info("👆 Press **Validate Posture** to check your robot's pose!")