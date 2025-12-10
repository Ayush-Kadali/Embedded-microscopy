#!/usr/bin/env python3
"""
🎯 LIVE DEMO - See Bounding Boxes in Real-Time!
Quick demonstration of YOLO detection with annotated images
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Live Detection Demo", page_icon="🔬", layout="wide")

st.title("🔬 Plankton Detection with Bounding Boxes")
st.markdown("**Custom YOLO model trained on 6 algal plankton species**")

# Show detected species
st.info("""
**🦠 This model detects 6 plankton/algae species:**
- Platymonas
- Chlorella
- Dunaliella salina
- Effrenium
- Porphyridium
- Haematococcus
""")

st.markdown("---")

# Helper function
@st.cache_resource
def load_model(model_path):
    """Load YOLO model (cached)"""
    from ultralytics import YOLO
    model = YOLO(str(model_path))

    # Display model info
    st.sidebar.success(f"✅ Loaded: Custom Plankton Model")
    if hasattr(model, 'names'):
        species = list(model.names.values()) if isinstance(model.names, dict) else model.names
        st.sidebar.info(f"**Detects {len(species)} species:**\n" + "\n".join([f"- {s}" for s in species]))

    return model


def run_yolo_detection(image, model, confidence=0.25):
    """Run YOLO and return annotated image"""
    try:
        results = model(image, conf=confidence, verbose=False)

        # Get annotated image (YOLO draws bounding boxes automatically)
        annotated_image = results[0].plot()

        # Extract detection info
        detections = []
        boxes = results[0].boxes

        for i, box in enumerate(boxes):
            detections.append({
                'id': i + 1,
                'class': model.names[int(box.cls[0])],
                'confidence': float(box.conf[0]),
                'bbox': box.xyxy[0].tolist()
            })

        return annotated_image, detections

    except Exception as e:
        st.error(f"Error: {e}")
        return None, []


# Sidebar
st.sidebar.header("⚙️ Settings")

# Find YOLO models
models_dir = Path("models")
downloaded_dir = Path("Downloaded models")

yolo_models = []
for model_dir in [models_dir, downloaded_dir]:
    if model_dir.exists():
        yolo_models.extend(list(model_dir.glob("*.pt")))

if not yolo_models:
    st.error("❌ No YOLO models found!")
    st.info("**Expected location:** `Downloaded models/best.pt`")
    st.stop()

# Prioritize best.pt (custom plankton model)
best_model = None
for model in yolo_models:
    if 'best.pt' in str(model):
        best_model = model
        break

if best_model:
    default_idx = yolo_models.index(best_model)
else:
    default_idx = 0

selected_model_path = st.sidebar.selectbox(
    "Select YOLO Model:",
    yolo_models,
    index=default_idx,
    help="best.pt is your custom-trained plankton detection model"
)
confidence = st.sidebar.slider("Confidence Threshold", 0.05, 0.50, 0.25, 0.01)

st.sidebar.markdown("---")
st.sidebar.success("""
**✅ How it works:**
1. Upload/select image
2. Click "Detect"
3. See bounding boxes!
4. View statistics
""")

# Load model
with st.spinner("Loading YOLO model..."):
    model = load_model(selected_model_path)

st.sidebar.info(f"Model loaded: {selected_model_path.name}")

# Main area - Input
st.header("📸 Input Image")

input_method = st.radio("Choose input:", ["Upload Image", "Use Test Image"], horizontal=True)

image_rgb = None

if input_method == "Upload Image":
    uploaded_file = st.file_uploader("Upload microscope image", type=['jpg', 'jpeg', 'png', 'bmp'])
    if uploaded_file:
        image_pil = Image.open(uploaded_file)
        image_rgb = np.array(image_pil)

else:  # Test image
    test_dir = Path("test_images")
    if test_dir.exists():
        test_images = list(test_dir.glob("*.jpeg")) + list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
        if test_images:
            selected_test = st.selectbox("Select test image:", test_images)
            image = cv2.imread(str(selected_test))
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            st.warning("No test images found in test_images/")
    else:
        st.warning("test_images/ directory not found")

# Display and process
if image_rgb is not None:
    # Show original
    col1, col2 = st.columns([2, 1])

    with col1:
        st.image(image_rgb, caption="Original Image", use_container_width=True)

    with col2:
        st.metric("Image Size", f"{image_rgb.shape[1]} x {image_rgb.shape[0]}")
        st.metric("Confidence", f"{confidence:.0%}")

        st.markdown("---")

        detect_button = st.button("🔬 **Run Detection**", type="primary", use_container_width=True)

    # Run detection
    if detect_button:
        with st.spinner("🔍 Detecting organisms..."):
            annotated_img, detections = run_yolo_detection(image_rgb, model, confidence)

        if annotated_img is not None:
            st.markdown("---")
            st.success(f"✅ **Detection Complete!** Found **{len(detections)}** organisms")

            st.markdown("---")

            # MAIN FEATURE: Show annotated image with bounding boxes
            st.header("🎯 Annotated Image with Bounding Boxes")

            # Convert BGR to RGB
            annotated_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)

            # Display full-width annotated image
            st.image(annotated_rgb, use_container_width=True, caption="✨ Live Detection Results - Bounding boxes automatically drawn by YOLO")

            st.markdown("---")

            # Side-by-side comparison
            st.header("📊 Before & After Comparison")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Original")
                st.image(image_rgb, use_container_width=True)

            with col2:
                st.markdown("### With Detections")
                st.image(annotated_rgb, use_container_width=True)

            # Statistics
            if detections:
                st.markdown("---")
                st.header("📈 Detection Statistics")

                # Count by species
                class_counts = {}
                for det in detections:
                    cls = det['class']
                    class_counts[cls] = class_counts.get(cls, 0) + 1

                # Metrics row
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("🦠 Total Organisms", len(detections))

                with col2:
                    st.metric("🧬 Unique Species", len(class_counts))

                with col3:
                    avg_conf = np.mean([d['confidence'] for d in detections])
                    st.metric("📊 Avg Confidence", f"{avg_conf:.1%}")

                with col4:
                    max_conf = max([d['confidence'] for d in detections])
                    st.metric("🎯 Best Detection", f"{max_conf:.1%}")

                st.markdown("---")

                # Charts
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Species Distribution")
                    fig = px.pie(
                        values=list(class_counts.values()),
                        names=list(class_counts.keys()),
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("Confidence Distribution")
                    fig = px.histogram(
                        x=[d['confidence'] for d in detections],
                        nbins=20,
                        labels={'x': 'Confidence', 'y': 'Count'},
                        color_discrete_sequence=['#636EFA']
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                # Detailed table
                st.markdown("---")
                st.subheader("🔍 Individual Detection Details")

                det_df = pd.DataFrame([
                    {
                        'ID': d['id'],
                        'Species': d['class'],
                        'Confidence': f"{d['confidence']:.2%}",
                        'Box Top-Left': f"({d['bbox'][0]:.0f}, {d['bbox'][1]:.0f})",
                        'Box Bottom-Right': f"({d['bbox'][2]:.0f}, {d['bbox'][3]:.0f})",
                        'Width': f"{d['bbox'][2] - d['bbox'][0]:.0f}px",
                        'Height': f"{d['bbox'][3] - d['bbox'][1]:.0f}px"
                    }
                    for d in detections
                ])

                st.dataframe(det_df, use_container_width=True, height=300)

                # Download button
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 1])

                with col2:
                    csv = det_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Detection Data (CSV)",
                        data=csv,
                        file_name=f"detections_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            else:
                st.warning("⚠️ No organisms detected. Try:")
                st.markdown("- Lowering confidence threshold")
                st.markdown("- Using a different image")
                st.markdown("- Checking if image contains plankton")

        else:
            st.error("❌ Detection failed!")

else:
    st.info("👆 **Upload an image or select a test image to start detection!**")

# Footer
st.markdown("---")
st.caption("🔬 Marine Plankton AI - Real-Time Bounding Box Detection Demo | Built for SIH 2025")
