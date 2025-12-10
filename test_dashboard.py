#!/usr/bin/env python3
"""
Quick test to verify dashboard can be imported
"""

import sys
sys.path.insert(0, '.')

print("Testing dashboard imports...")
print("=" * 50)

try:
    import dashboard.app_comprehensive as app
    print("✅ Dashboard module imported successfully")

    # Check for main components
    components = [
        "main",
        "initialize_session_state",
        "render_home_page",
        "render_single_image_page",
        "render_video_analysis_page",
        "render_flow_cell_page",
        "render_batch_processing_page",
        "render_results_page",
        "render_model_management_page",
        "render_settings_page",
        "render_sidebar",
        "load_available_models"
    ]

    missing = []
    for comp in components:
        if hasattr(app, comp):
            print(f"✅ {comp}")
        else:
            print(f"❌ {comp} - MISSING")
            missing.append(comp)

    print("=" * 50)
    if missing:
        print(f"❌ Missing {len(missing)} components: {missing}")
        sys.exit(1)
    else:
        print("✅ All dashboard components loaded successfully!")
        print("\nTo run the dashboard:")
        print("  ./run_dashboard.sh")
        print("  or")
        print("  streamlit run dashboard/app_comprehensive.py")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
