#!/bin/bash
# Launcher script for Streamlit dashboard
# Sets TensorFlow environment variables before loading

# Set TensorFlow environment variables
export TF_CPP_MIN_LOG_LEVEL=2
export CUDA_VISIBLE_DEVICES=-1
export TF_FORCE_GPU_ALLOW_GROWTH=false
export KMP_DUPLICATE_LIB_OK=TRUE

# Activate virtual environment
source .venv/bin/activate

# Run Streamlit
streamlit run dashboard/app.py
