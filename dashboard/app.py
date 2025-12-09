#!/usr/bin/env python3
"""
Marine Plankton AI Microscopy System - Streamlit Dashboard
Main application with camera input and real-time analysis
"""

# Fix TensorFlow mutex lock error on macOS
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable GPU

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

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(parent_dir))

# Change working directory to parent (project root)
os.chdir(parent_dir)

from pipeline.manager import PipelineManager
from config.config_loader import load_config

# Page configuration
st.set_page_config(
    page_title="Marine Plankton AI Microscopy",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False


def capture_camera_image():
    """Capture image from camera"""
    camera_input = st.camera_input("Take a microscope image")

    if camera_input is not None:
        # Convert to PIL Image
        image = Image.open(camera_input)
        # Convert to numpy array (RGB)
        img_array = np.array(image)
        return img_array
    return None


def upload_image_file():
    """Upload image file"""
    uploaded_file = st.file_uploader(
        "Or upload an image file",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        help="Upload a microscope image for analysis"
    )

    if uploaded_file is not None:
        # Convert to PIL Image
        image = Image.open(uploaded_file)
        # Convert to numpy array (RGB)
        img_array = np.array(image)
        return img_array
    return None


def run_pipeline(image):
    """Run the full 7-stage pipeline on the image"""
    import cv2
    import tempfile

    with st.spinner("Running analysis pipeline..."):
        # Initialize pipeline
        config = load_config()
        pipeline = PipelineManager(config)

        # Save image to temporary file for acquisition module
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            cv2.imwrite(tmp_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # Prepare acquisition parameters
        acquisition_params = {
            'mode': 'file',
            'image_path': tmp_path,
            'magnification': 2.0,
            'exposure_ms': 100,
            'capture_metadata': {
                'timestamp': datetime.now().isoformat(),
                'operator_id': 'dashboard',
                'source': st.session_state.get('location', 'camera')
            }
        }

        # Execute pipeline
        results = pipeline.execute_pipeline(acquisition_params)

        # Clean up temp file
        import os
        try:
            os.unlink(tmp_path)
        except:
            pass

        return results


def display_metrics(results):
    """Display key metrics in cards"""
    # Extract metrics from pipeline output
    summary = results.get('summary', {})
    detailed = results.get('detailed_results', {})
    diversity = detailed.get('diversity', {})

    total_organisms = summary.get('total_organisms', 0)
    species_count = summary.get('species_richness', 0)
    shannon_div = summary.get('shannon_diversity', 0)
    simpson_div = diversity.get('simpson', 0)

    # Display in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🦠 Total Organisms",
            value=total_organisms,
            help="Total number of organisms detected"
        )

    with col2:
        st.metric(
            label="🧬 Species Detected",
            value=species_count,
            help="Number of unique species found"
        )

    with col3:
        st.metric(
            label="📊 Shannon Diversity",
            value=f"{shannon_div:.3f}",
            help="Species diversity index (higher = more diverse)"
        )

    with col4:
        st.metric(
            label="📈 Simpson Diversity",
            value=f"{simpson_div:.3f}",
            help="Probability two random samples are different species"
        )


def plot_species_distribution(results):
    """Plot species distribution pie chart"""
    summary = results.get('summary', {})
    class_counts = summary.get('counts_by_class', {})

    if not class_counts:
        st.warning("No species detected")
        return

    # Prepare data
    species = list(class_counts.keys())
    counts = list(class_counts.values())

    # Create pie chart
    fig = px.pie(
        values=counts,
        names=species,
        title="Species Distribution",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_size_distribution(results):
    """Plot organism size distribution"""
    # Note: Size data not available in current pipeline output
    st.info("Size distribution visualization not available in current pipeline version")


def plot_confidence_scores(results):
    """Plot confidence scores for predictions"""
    # Note: Individual prediction confidence not available in pipeline summary
    st.info("Confidence score visualization not available in current pipeline version")


def display_detailed_results(results):
    """Display detailed results in expandable sections"""
    st.subheader("📋 Detailed Results")

    summary = results.get('summary', {})
    detailed = results.get('detailed_results', {})

    # Species Counts
    with st.expander("🔬 Species Counts", expanded=True):
        class_counts = summary.get('counts_by_class', {})
        if class_counts:
            df = pd.DataFrame([
                {'Species': species, 'Count': count}
                for species, count in class_counts.items()
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No organisms detected")

    # Analytics Results
    with st.expander("📊 Diversity Analytics"):
        diversity = detailed.get('diversity', {})

        st.write("**Diversity Metrics:**")
        if diversity:
            st.write(f"- Shannon Diversity: {summary.get('shannon_diversity', 0):.4f}")
            st.write(f"- Simpson Diversity: {diversity.get('simpson', 0):.4f}")
            st.write(f"- Species Richness: {summary.get('species_richness', 0)}")
            st.write(f"- Species Evenness: {diversity.get('evenness', 0):.4f}")

        st.write("**Bloom Detection:**")
        bloom_alerts = detailed.get('bloom_alerts', [])
        if bloom_alerts:
            for bloom in bloom_alerts:
                st.warning(f"⚠️ Bloom detected: {bloom.get('species', 'Unknown')}")
                st.write(f"- Dominance: {bloom.get('dominance', 0):.1f}%")
        else:
            st.success("✅ No blooms detected")


def display_annotated_image(results):
    """Display the annotated image with bounding boxes"""
    # Annotated images not directly available in pipeline output
    st.info("Check the results directory for annotated images and detailed CSV/JSON files")


def export_results(results):
    """Provide download buttons for results"""
    st.subheader("💾 Export Results")

    # Get exported file paths from pipeline results
    exported_files = results.get('exported_files', [])

    if exported_files:
        st.write("**Files exported:**")
        for file_path in exported_files:
            st.write(f"- {file_path}")
        st.info("Check the results directory for exported files")
    else:
        st.info("No files exported. Check the results directory for CSV/JSON files.")


def main():
    """Main application"""
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">🔬 Marine Plankton AI Microscopy System</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Location input
        location = st.text_input(
            "📍 Sample Location",
            value="Unknown",
            help="Enter the location where the sample was collected"
        )
        st.session_state['location'] = location

        st.markdown("---")

        # Model info
        st.subheader("🤖 Model Information")
        st.info("""
        **Architecture**: EfficientNetB0
        **Accuracy**: 83.48%
        **Species**: 19 plankton types
        **Input Size**: 224×224 pixels
        """)

        st.markdown("---")

        # About
        st.subheader("ℹ️ About")
        st.write("""
        This system uses AI to automatically:
        - Detect plankton organisms
        - Classify species
        - Count populations
        - Analyze diversity
        - Detect blooms
        """)

    # Main content
    tab1, tab2 = st.tabs(["📸 Capture & Analyze", "📊 Results"])

    with tab1:
        st.header("Image Acquisition")

        # Input method selection
        input_method = st.radio(
            "Select input method:",
            ["📷 Camera", "📁 Upload File"],
            horizontal=True
        )

        image = None

        if input_method == "📷 Camera":
            st.write("Capture a microscope image using your camera:")
            image = capture_camera_image()
        else:
            st.write("Upload a microscope image file:")
            image = upload_image_file()

        # Display captured/uploaded image
        if image is not None:
            st.subheader("📷 Input Image")
            st.image(image, caption="Input microscope image", use_container_width=True)

            # Analyze button
            if st.button("🔬 Run Analysis", type="primary", use_container_width=True):
                # Convert RGB to BGR for OpenCV
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                try:
                    # Run pipeline
                    results = run_pipeline(image_bgr)

                    # Store in session state
                    st.session_state.results = results
                    st.session_state.processed_image = image
                    st.session_state.analysis_complete = True

                    st.success("✅ Analysis complete! View results in the 'Results' tab.")

                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.exception(e)

    with tab2:
        if st.session_state.analysis_complete and st.session_state.results:
            results = st.session_state.results

            # Display metrics
            st.header("📊 Analysis Results")
            display_metrics(results)

            st.markdown("---")

            # Visualizations
            col1, col2 = st.columns(2)

            with col1:
                plot_species_distribution(results)

            with col2:
                plot_size_distribution(results)

            # Confidence scores
            plot_confidence_scores(results)

            st.markdown("---")

            # Annotated image
            display_annotated_image(results)

            st.markdown("---")

            # Detailed results
            display_detailed_results(results)

            st.markdown("---")

            # Export
            export_results(results)

        else:
            st.info("👆 Capture or upload an image in the 'Capture & Analyze' tab to see results here.")


if __name__ == "__main__":
    main()
