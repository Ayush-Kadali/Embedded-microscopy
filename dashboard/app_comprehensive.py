#!/usr/bin/env python3
"""
Marine Plankton AI Microscopy System - Comprehensive Dashboard
Integrates all detection methods: Pipeline, YOLO, Flow Cell, and Batch Processing
"""

# Fix TensorFlow issues
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys
import json
from datetime import datetime
import tempfile
import subprocess
import time
from io import BytesIO

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(parent_dir))
os.chdir(parent_dir)

# Page configuration
st.set_page_config(
    page_title="Marine Plankton AI - Complete System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .feature-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'results': None,
        'processed_image': None,
        'analysis_complete': False,
        'video_results': None,
        'flow_cell_running': False,
        'batch_results': [],
        'current_page': 'Home',
        'models_loaded': False,
        'yolo_models': [],
        'classification_models': []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_available_models():
    """Scan for available models and prioritize plankton models"""
    models_dir = Path("models")
    downloaded_models_dir = Path("Downloaded models")

    yolo_models = []
    classification_models = []

    # Find YOLO models
    for model_dir in [models_dir, downloaded_models_dir]:
        if model_dir.exists():
            yolo_models.extend(list(model_dir.glob("*.pt")))

    # Sort YOLO models - prioritize best.pt (custom plankton model)
    yolo_models.sort(key=lambda x: (
        0 if 'best.pt' in str(x) else 1,  # best.pt first
        str(x)
    ))

    # Find classification models
    if models_dir.exists():
        classification_models.extend(list(models_dir.glob("*.keras")))
        classification_models.extend(list(models_dir.glob("*.h5")))

    return yolo_models, classification_models


def run_yolo_inference(image, model_path, confidence=0.25):
    """
    Run YOLO inference on an image and return annotated image + results
    Uses custom plankton detection model (best.pt)
    """
    try:
        from ultralytics import YOLO

        # Load model
        model = YOLO(str(model_path))

        # Verify it's a plankton model
        plankton_species = ['Platymonas', 'Chlorella', 'Dunaliella', 'Effrenium', 'Porphyridium', 'Haematococcus']
        model_classes = list(model.names.values()) if hasattr(model, 'names') and isinstance(model.names, dict) else []

        is_plankton_model = any(species in ' '.join(model_classes) for species in plankton_species)

        if not is_plankton_model:
            st.warning(f"⚠️ This may not be the plankton model. Detected classes: {model_classes}")
            st.info("💡 Use 'best.pt' for plankton detection (trained on 6 algal species)")

        # Run inference
        results = model(image, conf=confidence, verbose=False)

        # Get annotated image
        annotated_image = results[0].plot()

        # Extract detections
        detections = []
        boxes = results[0].boxes

        for i, box in enumerate(boxes):
            det = {
                'id': i,
                'class': model.names[int(box.cls[0])],
                'confidence': float(box.conf[0]),
                'bbox': box.xyxy[0].tolist()
            }
            detections.append(det)

        return annotated_image, detections

    except Exception as e:
        st.error(f"YOLO inference failed: {e}")
        return None, []


def draw_detections_on_image(image, detections, class_colors=None):
    """
    Draw bounding boxes and labels on image
    """
    import cv2

    img_copy = image.copy()

    if class_colors is None:
        # Default color scheme
        class_colors = {
            'copepod': (0, 255, 0),
            'diatom': (255, 0, 0),
            'dinoflagellate': (0, 0, 255),
            'default': (255, 255, 0)
        }

    for det in detections:
        # Get bbox coordinates
        if 'bbox' in det:
            x1, y1, x2, y2 = map(int, det['bbox'])
        elif 'x' in det and 'y' in det:
            # Handle different format
            x, y, w, h = det['x'], det['y'], det['width'], det['height']
            x1, y1, x2, y2 = x, y, x + w, y + h
        else:
            continue

        # Get color
        class_name = det.get('class', 'default').lower()
        color = class_colors.get(class_name, class_colors['default'])

        # Draw bbox
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)

        # Draw label
        label = f"{det['class']}"
        if 'confidence' in det:
            label += f" {det['confidence']:.2f}"

        # Label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        cv2.rectangle(img_copy, (x1, y1 - label_size[1] - 10),
                     (x1 + label_size[0], y1), color, -1)

        # Label text
        cv2.putText(img_copy, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return img_copy


def extract_video_frames(video_path, num_frames=6):
    """Extract sample frames from video for preview"""
    import cv2

    frames = []

    try:
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames == 0:
            return frames

        # Extract evenly spaced frames
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()

            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append((idx, frame_rgb))

        cap.release()

    except Exception as e:
        st.warning(f"Could not extract frames: {e}")

    return frames


def display_video_preview(video_path, title="Video Preview"):
    """Display video with frame previews"""
    st.subheader(title)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.video(str(video_path))

    with col2:
        st.markdown("**Sample Frames:**")
        frames = extract_video_frames(video_path, num_frames=4)

        if frames:
            for idx, (frame_num, frame) in enumerate(frames):
                st.image(frame, caption=f"Frame {frame_num}", use_container_width=True)
        else:
            st.info("Could not extract preview frames")


def render_sidebar():
    """Render sidebar with system info and navigation"""
    with st.sidebar:
        st.markdown("### 🔬 Plankton AI System")
        st.markdown("---")

        # System Status
        st.markdown("#### 📊 System Status")

        yolo_models, classification_models = load_available_models()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("YOLO Models", len(yolo_models))
        with col2:
            st.metric("ML Models", len(classification_models))

        st.markdown("---")

        # Quick Info
        with st.expander("ℹ️ System Info", expanded=False):
            st.markdown("""
            **Available Methods:**
            - 🖼️ Single Image Analysis
            - 📹 Video Detection (YOLO)
            - 🔬 Flow Cell Scanning
            - 📦 Batch Processing

            **Models:**
            - YOLOv8 (6 species)
            - MobileNetV2 (19 species)
            - EfficientNet (19 species)
            """)

        with st.expander("🎯 Detection Capabilities", expanded=False):
            st.markdown("""
            **🔬 Custom YOLO Model (best.pt):**
            Trained on 6 algal plankton species:
            - Platymonas
            - Chlorella
            - Dunaliella salina
            - Effrenium
            - Porphyridium
            - Haematococcus

            **🧠 Classification Models:**
            Trained on 19 marine plankton species:
            - Multiple diatoms
            - Multiple dinoflagellates
            - Other marine plankton

            **💡 Use YOLO (best.pt) for algal detection**
            **💡 Use Classification models for diatoms/dinoflagellates**
            """)

        st.markdown("---")

        # Quick Actions
        st.markdown("#### ⚡ Quick Actions")
        if st.button("🔄 Refresh Models", use_container_width=True):
            st.rerun()

        if st.button("📁 Open Results Folder", use_container_width=True):
            subprocess.run(["open", "results"], check=False)

        st.markdown("---")
        st.markdown("**Built for SIH 2025**")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


def render_home_page():
    """Render home/overview page"""
    st.markdown('<div class="main-header">🔬 Marine Plankton AI Microscopy System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Complete AI-Powered Plankton Detection & Analysis Platform</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Feature Overview
    st.markdown("### 🚀 System Capabilities")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🖼️ Single Image Analysis</h3>
            <p>Upload or capture microscope images for instant species identification and counting.</p>
            <ul>
                <li>Real-time classification</li>
                <li>Species counting</li>
                <li>Diversity metrics</li>
                <li>Bloom detection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📹 Video Analysis</h3>
            <p>Process video streams with YOLO object detection for real-time tracking.</p>
            <ul>
                <li>YOLO detection</li>
                <li>Bounding boxes</li>
                <li>Confidence scores</li>
                <li>Slow-motion playback</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🔬 Flow Cell Scanner</h3>
            <p>Continuous scanning of flowing water samples for volume-based analysis.</p>
            <ul>
                <li>Real-time scanning</li>
                <li>Volume tracking</li>
                <li>Concentration calc</li>
                <li>Session logging</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick Stats
    st.markdown("### 📊 System Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🤖 Detection Models",
            value="3+",
            delta="YOLO + MobileNet + EfficientNet"
        )

    with col2:
        st.metric(
            label="🧬 Species Recognition",
            value="25+",
            delta="Diatoms & Dinoflagellates"
        )

    with col3:
        results_dir = Path("results")
        result_count = len(list(results_dir.glob("**/*"))) if results_dir.exists() else 0
        st.metric(
            label="📁 Results Generated",
            value=result_count,
            delta="All processing modes"
        )

    with col4:
        st.metric(
            label="⚡ Processing Speed",
            value="<2s",
            delta="Per image"
        )

    st.markdown("---")

    # Getting Started
    st.markdown("### 🎯 Getting Started")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-box">
            <h4>👨‍🔬 For Quick Analysis</h4>
            <ol>
                <li>Go to <b>📸 Single Image</b> tab</li>
                <li>Upload or capture an image</li>
                <li>Click <b>Analyze</b></li>
                <li>View results instantly</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-box">
            <h4>🎬 For Video Analysis</h4>
            <ol>
                <li>Go to <b>📹 Video Analysis</b> tab</li>
                <li>Upload a video file</li>
                <li>Select YOLO model</li>
                <li>Process and download results</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Model Performance
    st.markdown("### 🎓 Model Performance")

    performance_data = {
        'Model': ['YOLO (best.pt)\nAlgal Plankton', 'MobileNetV2\nMarine Plankton', 'EfficientNetB0\nMarine Plankton'],
        'Accuracy': [0.85, 0.83, 0.88],
        'Species': [6, 19, 19],
        'Type': ['Algae', 'Diatoms/Dinos', 'Diatoms/Dinos']
    }

    df = pd.DataFrame(performance_data)

    fig = px.bar(
        df,
        x='Model',
        y='Accuracy',
        title='Model Accuracy Comparison',
        color='Accuracy',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Recent Activity (if available)
    st.markdown("### 📈 Recent Activity")

    results_dir = Path("results")
    if results_dir.exists():
        recent_files = sorted(results_dir.glob("**/*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]

        if recent_files:
            activity_data = []
            for file in recent_files:
                activity_data.append({
                    'File': file.name,
                    'Type': file.parent.name,
                    'Modified': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })

            st.dataframe(pd.DataFrame(activity_data), use_container_width=True)
        else:
            st.info("No recent activity. Start analyzing images to see results here!")
    else:
        st.info("No results directory found. Results will appear here after your first analysis.")


def render_single_image_page():
    """Render single image analysis page"""
    st.header("📸 Single Image Analysis")
    st.markdown("Upload or capture a microscope image for comprehensive analysis")

    st.markdown("---")

    # Input method selection
    col1, col2 = st.columns([2, 1])

    with col1:
        input_method = st.radio(
            "Select input method:",
            ["📷 Camera", "📁 Upload File", "🖼️ Use Test Image"],
            horizontal=True
        )

    with col2:
        analysis_method = st.selectbox(
            "Analysis Method:",
            ["Pipeline (Full)", "Quick Classification", "YOLO Detection"]
        )

    image = None
    image_path = None

    # Image Input
    if input_method == "📷 Camera":
        camera_input = st.camera_input("Take a microscope image")
        if camera_input is not None:
            image = Image.open(camera_input)
            image = np.array(image)

    elif input_method == "📁 Upload File":
        uploaded_file = st.file_uploader(
            "Upload a microscope image",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image = np.array(image)

    else:  # Use Test Image
        test_images_dir = Path("test_images")
        if test_images_dir.exists():
            test_images = list(test_images_dir.glob("*.jpeg")) + list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
            if test_images:
                selected_test = st.selectbox("Select a test image:", test_images)
                image = cv2.imread(str(selected_test))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image_path = str(selected_test)
        else:
            st.warning("No test_images directory found")

    # Display image
    if image is not None:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📷 Input Image")
            st.image(image, caption="Input microscope image", use_container_width=True)

        with col2:
            st.subheader("⚙️ Settings")

            if analysis_method == "Pipeline (Full)":
                magnification = st.slider("Magnification", 1.0, 10.0, 2.5, 0.5)
                exposure = st.slider("Exposure (ms)", 50, 200, 100, 10)
                confidence = st.slider("Confidence Threshold", 0.1, 0.9, 0.7, 0.1)

            elif analysis_method == "YOLO Detection":
                yolo_models, _ = load_available_models()
                if yolo_models:
                    selected_yolo = st.selectbox(
                        "YOLO Model:",
                        yolo_models,
                        help="best.pt = Custom plankton model (6 algal species)"
                    )

                    # Show model info
                    if 'best.pt' in str(selected_yolo):
                        st.success("✅ Using custom plankton model (6 algal species)")
                    else:
                        st.warning("⚠️ Generic YOLO - use best.pt for plankton!")

                    confidence = st.slider("Confidence Threshold", 0.1, 0.9, 0.25, 0.05)
                else:
                    st.error("No YOLO models found!")
                    return

            else:  # Quick Classification
                confidence = st.slider("Confidence Threshold", 0.1, 0.9, 0.5, 0.1)

            st.markdown("---")

            analyze_button = st.button("🔬 Analyze Image", type="primary", use_container_width=True)

        # Run Analysis
        if analyze_button:
            with st.spinner("Analyzing image..."):
                try:
                    if analysis_method == "Pipeline (Full)":
                        # Run full pipeline
                        from pipeline.manager import PipelineManager
                        from config.config_loader import load_config

                        # Save temp file
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                            cv2.imwrite(tmp.name, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                            tmp_path = tmp.name

                        config = load_config()
                        pipeline = PipelineManager(config)

                        acquisition_params = {
                            'mode': 'file',
                            'image_path': tmp_path,
                            'magnification': magnification,
                            'exposure_ms': exposure,
                            'capture_metadata': {
                                'timestamp': datetime.now().isoformat(),
                                'operator_id': 'dashboard',
                                'source': 'upload'
                            }
                        }

                        results = pipeline.execute_pipeline(acquisition_params)

                        # Clean up
                        os.unlink(tmp_path)

                        # Display results
                        st.success("✅ Analysis complete!")
                        display_pipeline_results(results)

                    elif analysis_method == "YOLO Detection":
                        # Run YOLO detection inline
                        st.info("Running YOLO detection...")

                        # Run inference
                        annotated_img, detections = run_yolo_inference(image, selected_yolo, confidence)

                        if annotated_img is not None:
                            st.success(f"✅ YOLO detection complete! Found {len(detections)} organisms")

                            # Display results side by side
                            st.markdown("---")
                            st.subheader("🎯 Detection Results")

                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown("**Original Image**")
                                st.image(image, use_container_width=True)

                            with col2:
                                st.markdown("**Annotated Image with Detections**")
                                # Convert BGR to RGB for display
                                annotated_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
                                st.image(annotated_rgb, use_container_width=True)

                            # Detection statistics
                            st.markdown("---")
                            st.subheader("📊 Detection Statistics")

                            if detections:
                                # Count by class
                                class_counts = {}
                                for det in detections:
                                    cls = det['class']
                                    class_counts[cls] = class_counts.get(cls, 0) + 1

                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.metric("Total Detections", len(detections))

                                with col2:
                                    st.metric("Unique Species", len(class_counts))

                                with col3:
                                    avg_conf = np.mean([d['confidence'] for d in detections])
                                    st.metric("Avg Confidence", f"{avg_conf:.2%}")

                                # Species distribution
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("**Species Distribution**")
                                    fig = px.pie(
                                        values=list(class_counts.values()),
                                        names=list(class_counts.keys()),
                                        title="Detected Species"
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                with col2:
                                    st.markdown("**Detection Details**")
                                    det_df = pd.DataFrame([
                                        {
                                            'ID': d['id'],
                                            'Species': d['class'],
                                            'Confidence': f"{d['confidence']:.2%}",
                                            'BBox': f"[{d['bbox'][0]:.0f}, {d['bbox'][1]:.0f}, {d['bbox'][2]:.0f}, {d['bbox'][3]:.0f}]"
                                        }
                                        for d in detections
                                    ])
                                    st.dataframe(det_df, use_container_width=True)

                                # Confidence distribution
                                st.markdown("---")
                                st.markdown("**Confidence Score Distribution**")

                                fig = px.histogram(
                                    x=[d['confidence'] for d in detections],
                                    nbins=20,
                                    title="Detection Confidence Scores",
                                    labels={'x': 'Confidence', 'y': 'Count'}
                                )
                                st.plotly_chart(fig, use_container_width=True)

                            else:
                                st.warning("No organisms detected. Try lowering the confidence threshold.")

                        else:
                            st.error("❌ YOLO detection failed")

                    else:  # Quick Classification
                        st.info("Quick classification mode")
                        st.warning("Quick classification requires integration with classification model - use Pipeline mode for full analysis")

                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.exception(e)


def display_pipeline_results(results):
    """Display results from pipeline analysis"""
    if not results:
        st.error("No results to display")
        return

    st.markdown("---")
    st.subheader("📊 Analysis Results")

    # Metrics
    summary = results.get('summary', {})
    detailed = results.get('detailed_results', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🦠 Total Organisms", summary.get('total_organisms', 0))
    with col2:
        st.metric("🧬 Species Found", summary.get('species_richness', 0))
    with col3:
        st.metric("📊 Shannon Diversity", f"{summary.get('shannon_diversity', 0):.3f}")
    with col4:
        diversity = detailed.get('diversity', {})
        st.metric("📈 Simpson Index", f"{diversity.get('simpson', 0):.3f}")

    # Look for annotated images in results
    st.markdown("---")
    st.subheader("🖼️ Visual Results")

    results_dir = Path("results")

    # Find recent annotated images
    annotated_images = sorted(
        results_dir.glob("**/annotated_*.png"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )[:5]  # Show last 5

    if annotated_images:
        st.markdown("**Annotated Images with Detections:**")

        # Show images in gallery
        cols = st.columns(min(len(annotated_images), 3))
        for idx, img_path in enumerate(annotated_images[:3]):
            with cols[idx % 3]:
                img = Image.open(img_path)
                st.image(img, caption=img_path.name, use_container_width=True)

        # Show more in expander if available
        if len(annotated_images) > 3:
            with st.expander(f"View {len(annotated_images) - 3} more annotated images"):
                cols = st.columns(3)
                for idx, img_path in enumerate(annotated_images[3:]):
                    with cols[idx % 3]:
                        img = Image.open(img_path)
                        st.image(img, caption=img_path.name, use_container_width=True)

    # Find segmentation/processing images
    processing_images = sorted(
        results_dir.glob("**/segmented_*.png"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )[:3]

    if processing_images:
        with st.expander("🔬 View Processing Steps (Segmentation)"):
            cols = st.columns(len(processing_images))
            for idx, img_path in enumerate(processing_images):
                with cols[idx]:
                    img = Image.open(img_path)
                    st.image(img, caption=img_path.name, use_container_width=True)

    # Species Distribution
    st.markdown("---")
    class_counts = summary.get('counts_by_class', {})

    if class_counts:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🥧 Species Distribution")
            fig = px.pie(
                values=list(class_counts.values()),
                names=list(class_counts.keys()),
                title="Species Composition",
                hole=0.3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 Species Counts")
            df = pd.DataFrame([
                {'Species': k, 'Count': v, 'Percentage': f"{(v/sum(class_counts.values()))*100:.1f}%"}
                for k, v in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
            ])
            st.dataframe(df, use_container_width=True)

    # Individual organism details if available
    organisms = detailed.get('organisms', [])
    if organisms and len(organisms) > 0:
        st.markdown("---")
        st.subheader("🔍 Individual Organism Details")

        # Create detailed table
        org_data = []
        for org in organisms:
            org_data.append({
                'ID': org.get('id', 'N/A'),
                'Species': org.get('class_name', 'Unknown'),
                'Confidence': f"{org.get('confidence', 0):.2%}",
                'Size (px)': f"{org.get('size_px', 0):.0f}",
                'Position': f"({org.get('centroid_x', 0):.0f}, {org.get('centroid_y', 0):.0f})"
            })

        if org_data:
            org_df = pd.DataFrame(org_data)
            st.dataframe(org_df, use_container_width=True)

            # Download button for CSV
            csv = org_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Detection Data (CSV)",
                data=csv,
                file_name=f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    # Bloom Alerts
    bloom_alerts = detailed.get('bloom_alerts', [])
    if bloom_alerts:
        st.markdown("---")
        st.subheader("⚠️ Bloom Alerts")
        for bloom in bloom_alerts:
            st.warning(f"Bloom detected: {bloom.get('species', 'Unknown')} - {bloom.get('dominance', 0):.1f}% dominance")
    else:
        st.success("✅ No harmful blooms detected")

    # Export options
    st.markdown("---")
    st.subheader("💾 Export Options")

    exported_files = results.get('exported_files', [])
    if exported_files:
        st.info(f"Results exported to {len(exported_files)} files:")
        for file_path in exported_files:
            st.text(f"📄 {file_path}")

    # Show raw results option
    with st.expander("🔍 View Raw Analysis Results (JSON)"):
        st.json(results)


def render_video_analysis_page():
    """Render video analysis page with YOLO"""
    st.header("📹 Video Analysis (YOLO Detection)")
    st.markdown("Upload videos or use camera feed for real-time plankton detection")

    st.markdown("---")

    # Model selection
    yolo_models, _ = load_available_models()

    if not yolo_models:
        st.error("❌ No YOLO models found! Please download models first.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_model = st.selectbox("Select YOLO Model:", yolo_models)

    with col2:
        confidence = st.slider("Confidence Threshold", 0.05, 0.50, 0.18, 0.01)

    with col3:
        processing_mode = st.selectbox("Processing Mode:", ["Real-time", "Slow Motion", "Enhanced"])

    st.markdown("---")

    # Video input
    input_type = st.radio("Video Source:", ["📁 Upload Video", "🎬 Use Test Video", "📹 Webcam (Coming Soon)"], horizontal=True)

    video_path = None

    if input_type == "📁 Upload Video":
        uploaded_video = st.file_uploader("Upload a video file", type=['mp4', 'mov', 'avi', 'mkv'])

        if uploaded_video:
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                tmp.write(uploaded_video.read())
                video_path = tmp.name

            st.video(uploaded_video)

    elif input_type == "🎬 Use Test Video":
        video_dir = Path("Real_Time_Vids")
        if video_dir.exists():
            videos = list(video_dir.glob("*.mov")) + list(video_dir.glob("*.mp4"))
            if videos:
                selected_video = st.selectbox("Select test video:", videos)
                video_path = str(selected_video)
                st.video(str(selected_video))
        else:
            st.warning("No test videos found in Real_Time_Vids/")

    else:
        st.info("🚧 Webcam support coming soon!")

    # Processing settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)

        with col1:
            delay = st.slider("Playback Delay (ms)", 50, 500, 150, 10)
            save_output = st.checkbox("Save Output Video", value=True)

        with col2:
            skip_frames = st.slider("Process Every N Frames", 1, 10, 2, 1)
            show_stats = st.checkbox("Show Statistics Overlay", value=True)

    # Process button
    if video_path and st.button("🎬 Process Video", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("Starting video processing...")

            # Select script based on mode
            if processing_mode == "Slow Motion":
                script = "yolo_slow_motion.py"
            elif processing_mode == "Enhanced":
                script = "yolo_enhanced.py"
            else:
                script = "yolo_realtime.py"

            # Build command
            cmd = [
                'python', script,
                '--model', str(selected_model),
                '--video', video_path,
                '--conf', str(confidence),
                '--delay', str(delay)
            ]

            if save_output:
                cmd.append('--save')

            status_text.text("Processing video with YOLO...")
            progress_bar.progress(50)

            # Run processing
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            progress_bar.progress(100)

            if result.returncode == 0:
                status_text.text("✅ Processing complete!")
                st.success("Video processing completed successfully!")

                # Show output
                with st.expander("📋 Processing Log", expanded=False):
                    st.code(result.stdout)

                # Find output video
                results_dir = Path("results")
                output_videos = sorted(results_dir.glob("yolo_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)

                if output_videos:
                    latest_video = output_videos[0]

                    # Show video with frame previews
                    st.markdown("---")
                    display_video_preview(latest_video, "📹 Processed Video with Detections")

                    # Download button
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        with open(latest_video, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download Processed Video",
                                data=f,
                                file_name=latest_video.name,
                                mime="video/mp4",
                                use_container_width=True
                            )

                    # Extract and analyze sample frames
                    st.markdown("---")
                    st.subheader("📊 Sample Frame Analysis")

                    with st.spinner("Extracting frames for analysis..."):
                        frames = extract_video_frames(latest_video, num_frames=6)

                        if frames:
                            st.markdown(f"**Showing {len(frames)} sample frames from the processed video:**")

                            # Display in grid
                            cols = st.columns(3)
                            for idx, (frame_num, frame) in enumerate(frames):
                                with cols[idx % 3]:
                                    st.image(frame, caption=f"Frame {frame_num}", use_container_width=True)
            else:
                status_text.text("❌ Processing failed")
                st.error("Video processing failed!")
                st.code(result.stderr)

        except subprocess.TimeoutExpired:
            st.error("❌ Processing timeout! Video may be too long.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
        finally:
            # Clean up temp file
            if input_type == "📁 Upload Video" and video_path:
                try:
                    os.unlink(video_path)
                except:
                    pass


def render_flow_cell_page():
    """Render flow cell scanner page"""
    st.header("🔬 Flow Cell Scanner")
    st.markdown("Real-time continuous scanning of flowing water samples")

    st.markdown("---")

    # System check
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 System Status")

        if st.button("🔍 Run Diagnostics"):
            with st.spinner("Running system diagnostics..."):
                result = subprocess.run(['python', 'diagnose_flow_cell.py'], capture_output=True, text=True)
                st.code(result.stdout)

    with col2:
        st.subheader("⚙️ Quick Info")
        st.info("""
        **Modes Available:**
        - GUI Scanner
        - Headless Scanner
        - Camera Test
        """)

    st.markdown("---")

    # Scanner settings
    st.subheader("🎛️ Scanner Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        camera_id = st.number_input("Camera ID", 0, 10, 0)
        duration = st.number_input("Duration (seconds)", 10, 600, 120)

    with col2:
        flow_rate = st.number_input("Flow Rate (mL/min)", 0.1, 10.0, 2.0, 0.1)
        interval = st.number_input("Frame Interval (s)", 0.5, 5.0, 1.0, 0.1)

    with col3:
        scanner_mode = st.selectbox("Scanner Mode:", ["GUI", "Headless"])
        auto_stop = st.checkbox("Auto-stop on completion", value=True)

    st.markdown("---")

    # Control buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎥 Test Camera", use_container_width=True):
            with st.spinner("Testing camera..."):
                result = subprocess.run(
                    ['python', 'test_flow_cell.py', '--camera', str(camera_id)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                st.code(result.stdout)

    with col2:
        start_scan = st.button("▶️ Start Scan", type="primary", use_container_width=True)

    with col3:
        if st.button("🛑 Stop Scan", use_container_width=True):
            st.warning("Stop functionality - press 'q' in the scanner window")

    # Start scanning
    if start_scan:
        st.markdown("---")
        st.subheader("🔄 Scanning in Progress")

        script = "flow_cell_scanner.py" if scanner_mode == "GUI" else "flow_cell_headless.py"

        cmd = [
            'python', script,
            '--camera', str(camera_id),
            '--duration', str(duration),
            '--flow-rate', str(flow_rate),
            '--interval', str(interval)
        ]

        st.info(f"Running: {' '.join(cmd)}")
        st.warning("⚠️ Scanner will open in a new window. Press 'q' to stop early.")

        with st.spinner("Scanning..."):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)

                if result.returncode == 0:
                    st.success("✅ Scan completed!")

                    # Show output
                    with st.expander("📋 Scan Results", expanded=True):
                        st.code(result.stdout)

                    # Find session results
                    results_dir = Path("results")
                    flow_cell_sessions = list(results_dir.glob("flow_cell_*"))

                    if flow_cell_sessions:
                        latest_session = max(flow_cell_sessions, key=lambda x: x.stat().st_mtime)

                        # Display session summary
                        summary_file = latest_session / "session_summary.txt"
                        if summary_file.exists():
                            st.subheader("📊 Session Summary")
                            st.text(summary_file.read_text())

                        # Show CSV if available
                        csv_files = list(latest_session.glob("*.csv"))
                        if csv_files:
                            df = pd.read_csv(csv_files[0])
                            st.subheader("📈 Detection Data")
                            st.dataframe(df, use_container_width=True)
                else:
                    st.error("❌ Scan failed!")
                    st.code(result.stderr)

            except subprocess.TimeoutExpired:
                st.error("⏱️ Scan timeout!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_batch_processing_page():
    """Render batch processing page"""
    st.header("📦 Batch Processing")
    st.markdown("Process multiple images at once for high-throughput analysis")

    st.markdown("---")

    # Batch upload
    uploaded_files = st.file_uploader(
        "Upload multiple images",
        type=['jpg', 'jpeg', 'png', 'bmp'],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} images uploaded")

        # Preview
        with st.expander("🖼️ Preview Images", expanded=False):
            cols = st.columns(4)
            for idx, file in enumerate(uploaded_files[:8]):  # Show first 8
                with cols[idx % 4]:
                    st.image(file, caption=file.name, use_container_width=True)

            if len(uploaded_files) > 8:
                st.info(f"... and {len(uploaded_files) - 8} more")

        # Processing options
        st.markdown("---")
        st.subheader("⚙️ Batch Settings")

        col1, col2, col3 = st.columns(3)

        with col1:
            batch_mode = st.selectbox("Processing Mode:", ["Pipeline", "YOLO", "Quick Classification"])

        with col2:
            parallel = st.checkbox("Parallel Processing", value=True)
            save_individual = st.checkbox("Save Individual Results", value=True)

        with col3:
            confidence = st.slider("Confidence", 0.1, 0.9, 0.5, 0.1)

        # Process button
        if st.button("⚡ Process Batch", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status = st.empty()

            results = []

            for idx, file in enumerate(uploaded_files):
                status.text(f"Processing {idx + 1}/{len(uploaded_files)}: {file.name}")

                # Save to temp
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    tmp.write(file.read())
                    tmp_path = tmp.name

                try:
                    # Process based on mode
                    if batch_mode == "Pipeline":
                        # Run pipeline
                        from pipeline.manager import PipelineManager
                        from config.config_loader import load_config

                        config = load_config()
                        pipeline = PipelineManager(config)

                        acquisition_params = {
                            'mode': 'file',
                            'image_path': tmp_path,
                            'magnification': 2.5,
                            'exposure_ms': 100
                        }

                        result = pipeline.execute_pipeline(acquisition_params)
                        results.append({
                            'file': file.name,
                            'organisms': result.get('summary', {}).get('total_organisms', 0),
                            'species': result.get('summary', {}).get('species_richness', 0),
                            'status': 'success'
                        })

                    else:
                        results.append({
                            'file': file.name,
                            'status': 'pending',
                            'note': f'{batch_mode} mode not yet implemented in batch'
                        })

                except Exception as e:
                    results.append({
                        'file': file.name,
                        'status': 'error',
                        'error': str(e)
                    })

                finally:
                    os.unlink(tmp_path)

                progress_bar.progress((idx + 1) / len(uploaded_files))

            status.text("✅ Batch processing complete!")

            # Display results
            st.markdown("---")
            st.subheader("📊 Batch Results")

            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            # Summary stats
            if batch_mode == "Pipeline":
                col1, col2, col3 = st.columns(3)

                with col1:
                    total_organisms = sum(r.get('organisms', 0) for r in results)
                    st.metric("Total Organisms", total_organisms)

                with col2:
                    avg_species = np.mean([r.get('species', 0) for r in results])
                    st.metric("Avg Species/Image", f"{avg_species:.1f}")

                with col3:
                    success_rate = len([r for r in results if r.get('status') == 'success']) / len(results) * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")

                # Show annotated results gallery
                st.markdown("---")
                st.subheader("🖼️ Annotated Results Gallery")

                results_dir = Path("results")
                recent_annotated = sorted(
                    results_dir.glob("**/annotated_*.png"),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )[:len(uploaded_files)]  # Show results from this batch

                if recent_annotated:
                    st.markdown(f"**Showing {len(recent_annotated)} annotated images from this batch:**")

                    # Display in grid (3 per row)
                    for i in range(0, len(recent_annotated), 3):
                        cols = st.columns(3)
                        for j in range(3):
                            if i + j < len(recent_annotated):
                                img_path = recent_annotated[i + j]
                                with cols[j]:
                                    img = Image.open(img_path)
                                    st.image(img, caption=img_path.name, use_container_width=True)

                                    # Show quick stats if available
                                    matching_result = next((r for r in results if r['file'] in img_path.name), None)
                                    if matching_result:
                                        st.caption(f"🦠 {matching_result.get('organisms', 0)} organisms | 🧬 {matching_result.get('species', 0)} species")

                else:
                    st.info("No annotated images found. Results may have been saved to different location.")

                # Download all results
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 1])

                with col2:
                    # Create CSV of all results
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Batch Results (CSV)",
                        data=csv,
                        file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )


def render_results_page():
    """Render results dashboard page"""
    st.header("📊 Results Dashboard")
    st.markdown("Visualize and explore all analysis results")

    st.markdown("---")

    # Scan results directory
    results_dir = Path("results")

    if not results_dir.exists():
        st.warning("No results directory found. Run some analyses first!")
        return

    # Find all result types
    flow_cell_results = list(results_dir.glob("flow_cell_*"))
    batch_results = list(results_dir.glob("batch/"))
    json_results = list(results_dir.glob("**/*.json"))
    csv_results = list(results_dir.glob("**/*.csv"))
    video_results = list(results_dir.glob("yolo_*.mp4"))

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Flow Cell Sessions", len(flow_cell_results))
    with col2:
        st.metric("JSON Results", len(json_results))
    with col3:
        st.metric("CSV Results", len(csv_results))
    with col4:
        st.metric("Video Results", len(video_results))

    st.markdown("---")

    # Tabbed results view
    tab1, tab2, tab3, tab4 = st.tabs(["📁 All Files", "🔬 Flow Cell", "📹 Videos", "📈 Analytics"])

    with tab1:
        st.subheader("All Result Files")

        all_files = list(results_dir.glob("**/*"))
        all_files = [f for f in all_files if f.is_file()]

        if all_files:
            files_data = [{
                'Name': f.name,
                'Type': f.suffix,
                'Size': f"{f.stat().st_size / 1024:.1f} KB",
                'Modified': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
                'Path': str(f.relative_to(results_dir))
            } for f in sorted(all_files, key=lambda x: x.stat().st_mtime, reverse=True)[:50]]

            df = pd.DataFrame(files_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No result files found")

    with tab2:
        st.subheader("Flow Cell Sessions")

        if flow_cell_results:
            for session in sorted(flow_cell_results, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                with st.expander(f"📊 {session.name}", expanded=False):
                    summary_file = session / "session_summary.txt"
                    if summary_file.exists():
                        st.text(summary_file.read_text())

                    csv_files = list(session.glob("*.csv"))
                    if csv_files:
                        df = pd.read_csv(csv_files[0])
                        st.dataframe(df, use_container_width=True)
        else:
            st.info("No flow cell sessions found")

    with tab3:
        st.subheader("Video Results")

        if video_results:
            for video in sorted(video_results, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                st.markdown(f"**{video.name}**")
                st.video(str(video))

                col1, col2 = st.columns([3, 1])
                with col2:
                    with open(video, 'rb') as f:
                        st.download_button(
                            "⬇️ Download",
                            f,
                            file_name=video.name,
                            mime="video/mp4"
                        )
        else:
            st.info("No video results found")

    with tab4:
        st.subheader("Analytics Overview")

        # Aggregate statistics from JSON files
        if json_results:
            total_organisms = 0
            species_counts = {}

            for json_file in json_results[:20]:  # Last 20 results
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        summary = data.get('summary', {})
                        total_organisms += summary.get('total_organisms', 0)

                        counts = summary.get('counts_by_class', {})
                        for species, count in counts.items():
                            species_counts[species] = species_counts.get(species, 0) + count
                except:
                    continue

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Organisms (Last 20 analyses)", total_organisms)

                if species_counts:
                    st.subheader("Species Distribution")
                    fig = px.bar(
                        x=list(species_counts.keys()),
                        y=list(species_counts.values()),
                        title="Cumulative Species Counts"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.metric("Unique Species Detected", len(species_counts))

                if species_counts:
                    st.subheader("Top Species")
                    top_species = sorted(species_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    for species, count in top_species:
                        st.write(f"**{species}**: {count}")
        else:
            st.info("No JSON results for analytics")


def render_model_management_page():
    """Render model management page"""
    st.header("🤖 Model Management")
    st.markdown("View and manage detection models")

    st.markdown("---")

    # Scan for models
    yolo_models, classification_models = load_available_models()

    # YOLO Models
    st.subheader("🎯 YOLO Models")

    if yolo_models:
        for model in yolo_models:
            with st.expander(f"📦 {model.name}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Path:** `{model}`")
                    st.write(f"**Size:** {model.stat().st_size / (1024*1024):.1f} MB")
                    st.write(f"**Modified:** {datetime.fromtimestamp(model.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")

                with col2:
                    if 'best.pt' in model.name:
                        st.info("""
                        **Custom Trained Model**
                        - Species: 6
                        - Platymonas, Chlorella, etc.
                        """)
                    else:
                        st.info("Pre-trained YOLO model")
    else:
        st.warning("No YOLO models found")

    st.markdown("---")

    # Classification Models
    st.subheader("🧠 Classification Models")

    if classification_models:
        for model in classification_models:
            with st.expander(f"📦 {model.name}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Path:** `{model}`")
                    st.write(f"**Size:** {model.stat().st_size / (1024*1024):.1f} MB")
                    st.write(f"**Modified:** {datetime.fromtimestamp(model.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")

                with col2:
                    if 'mobilenet' in model.name.lower():
                        st.info("""
                        **MobileNetV2**
                        - Species: 19
                        - Accuracy: ~83%
                        """)
                    elif 'efficient' in model.name.lower():
                        st.info("""
                        **EfficientNet**
                        - Species: 19
                        - Accuracy: ~88%
                        """)
                    else:
                        st.info("Classification model")

                # Show metadata if available
                metadata_file = model.with_suffix('.json')
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    st.json(metadata)
    else:
        st.warning("No classification models found")

    st.markdown("---")

    # Model download section
    st.subheader("⬇️ Download Models")

    st.info("""
    **Available Model Downloads:**

    1. **YOLO Models:**
       - YOLOv8n: `yolo export model=yolov8n.pt`
       - Custom trained models in `Downloaded models/`

    2. **Classification Models:**
       - Located in `models/` directory
       - MobileNetV2 and EfficientNet variants

    3. **Download Production Dataset:**
       ```bash
       python download_production_dataset.py
       ```
    """)


def render_settings_page():
    """Render settings/configuration page"""
    st.header("⚙️ Settings & Configuration")
    st.markdown("System configuration and preferences")

    st.markdown("---")

    # Load current config
    config_file = Path("config/config.yaml")

    if config_file.exists():
        import yaml
        with open(config_file) as f:
            config = yaml.safe_load(f)

        st.subheader("📝 Current Configuration")

        # Editable config sections
        tab1, tab2, tab3, tab4 = st.tabs(["🔬 Classification", "📊 Analytics", "🎥 Acquisition", "💾 Export"])

        with tab1:
            st.markdown("### Classification Settings")

            if 'classification' in config:
                class_config = config['classification']

                confidence = st.slider(
                    "Confidence Threshold",
                    0.1, 0.9,
                    float(class_config.get('confidence_threshold', 0.7)),
                    0.05
                )

                st.text_area(
                    "Class Names",
                    value=str(class_config.get('class_names', [])),
                    height=150
                )

        with tab2:
            st.markdown("### Analytics Settings")

            if 'analytics' in config:
                analytics_config = config['analytics']

                st.checkbox("Calculate Shannon Diversity", value=True)
                st.checkbox("Calculate Simpson Index", value=True)
                st.checkbox("Detect Blooms", value=True)

                st.markdown("**Bloom Thresholds:**")
                bloom_config = analytics_config.get('bloom_thresholds', {})

                for species, threshold in bloom_config.items():
                    st.number_input(f"{species} threshold", value=threshold)

        with tab3:
            st.markdown("### Acquisition Settings")

            if 'acquisition' in config:
                acq_config = config['acquisition']

                st.number_input("Default Magnification", value=2.5, step=0.5)
                st.number_input("Default Exposure (ms)", value=100, step=10)
                st.text_input("Default Operator", value="dashboard")

        with tab4:
            st.markdown("### Export Settings")

            if 'export' in config:
                export_config = config['export']

                st.checkbox("Export CSV", value=export_config.get('formats', {}).get('csv', True))
                st.checkbox("Export JSON", value=export_config.get('formats', {}).get('json', True))
                st.text_input("Output Directory", value=export_config.get('output_dir', 'results'))

        st.markdown("---")

        if st.button("💾 Save Configuration", type="primary"):
            st.warning("Configuration saving not yet implemented - edit config/config.yaml directly")

        # Show raw config
        with st.expander("🔍 View Raw Configuration", expanded=False):
            st.json(config)

    else:
        st.error("Configuration file not found!")

    st.markdown("---")

    # System info
    st.subheader("ℹ️ System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Environment:**
        - Python version
        - OpenCV version
        - TensorFlow version
        - Streamlit version
        """)

    with col2:
        st.markdown(f"""
        **Paths:**
        - Working dir: `{os.getcwd()}`
        - Results: `{Path('results').absolute()}`
        - Models: `{Path('models').absolute()}`
        """)


def main():
    """Main application"""
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🏠 Home",
        "📸 Single Image",
        "📹 Video Analysis",
        "🔬 Flow Cell",
        "📦 Batch Process",
        "📊 Results",
        "🤖 Models",
        "⚙️ Settings"
    ])

    with tab1:
        render_home_page()

    with tab2:
        render_single_image_page()

    with tab3:
        render_video_analysis_page()

    with tab4:
        render_flow_cell_page()

    with tab5:
        render_batch_processing_page()

    with tab6:
        render_results_page()

    with tab7:
        render_model_management_page()

    with tab8:
        render_settings_page()


if __name__ == "__main__":
    main()
