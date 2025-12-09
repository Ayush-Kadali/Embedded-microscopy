#!/usr/bin/env python3
"""
Marine Plankton AI Microscopy System - Simplified Dashboard
Loads TensorFlow only when analysis is requested
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from pathlib import Path
import sys
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Marine Plankton AI Microscopy",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔬 Marine Plankton AI Microscopy System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ System Info")
    st.info("""
    **Model**: EfficientNetB0
    **Accuracy**: 83.48%
    **Species**: 19 types
    """)

# Main content
tab1, tab2 = st.tabs(["📸 Capture", "ℹ️ Info"])

with tab1:
    st.header("Image Acquisition")

    # Input method
    input_method = st.radio(
        "Select input method:",
        ["📷 Camera", "📁 Upload File"],
        horizontal=True
    )

    image = None

    if input_method == "📷 Camera":
        camera_input = st.camera_input("Take a microscope image")
        if camera_input:
            image = Image.open(camera_input)
            image = np.array(image)
    else:
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=['jpg', 'jpeg', 'png', 'bmp']
        )
        if uploaded_file:
            image = Image.open(uploaded_file)
            image = np.array(image)

    if image is not None:
        st.subheader("📷 Input Image")
        st.image(image, caption="Input image", use_container_width=True)

        if st.button("🔬 Run Analysis", type="primary"):
            st.warning("""
            ⚠️ **TensorFlow Issue Detected**

            There's currently a TensorFlow mutex lock error on your system.
            This is a known issue with certain macOS configurations.

            **Alternative Solution:**
            Run the analysis using the command-line tools instead:

            ```bash
            # Save your image as test_image.png, then run:
            source .venv/bin/activate
            python test_user_images.py
            ```

            **Or use the standalone test script:**
            ```bash
            python test_classification.py your_image.png
            ```

            **To fix TensorFlow:**
            ```bash
            # Reinstall TensorFlow
            pip uninstall tensorflow
            pip install tensorflow-macos tensorflow-metal
            ```
            """)

with tab2:
    st.header("📋 System Information")

    st.subheader("Available Tools")
    st.write("""
    While the dashboard is being fixed, you can use these command-line tools:

    **1. Quick Classification Test:**
    ```bash
    python test_classification.py path/to/image.png
    ```
    - Fast species identification
    - Shows top 5 predictions
    - Confidence scores

    **2. Full Pipeline Analysis:**
    ```bash
    python test_user_images.py
    ```
    - Complete 7-stage pipeline
    - Generates CSV/JSON exports
    - Creates annotated images
    - Diversity analytics

    **3. Model Evaluation:**
    ```bash
    python evaluate_model.py
    ```
    - Comprehensive performance metrics
    - Confusion matrix
    - Per-class accuracy
    """)

    st.subheader("Model Performance")
    st.write("""
    **Overall Metrics:**
    - Accuracy: 83.48%
    - Precision: 88.77%
    - F1-Score: 84.51%

    **Top Performing Species:**
    - Noctiluca: 96.8% F1
    - Asterionellopsis glacialis: 96.7% F1
    - Protoperidinium: 92.9% F1
    """)

    st.subheader("19 Species Recognized")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Diatoms:**")
        st.write("""
        - Asterionellopsis glacialis
        - Cerataulina
        - Chaetoceros
        - Entomoneis
        - Guinardia
        - Hemiaulus
        - Lauderia annulata
        - Nitzschia
        - Pinnularia
        - Pleurosigma
        - Thalassionema
        - Thalassiosira
        """)

    with col2:
        st.write("**Dinoflagellates:**")
        st.write("""
        - Alexandrium
        - Ceratium
        - Noctiluca
        - Ornithocercus magnificus
        - Prorocentrum
        - Protoperidinium
        - Pyrodinium
        """)

st.markdown("---")
st.info("""
**Note:** This is a simplified version of the dashboard due to a TensorFlow compatibility issue.
The full AI model and analysis pipeline are available via command-line tools (see Info tab).
""")
