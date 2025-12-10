#!/usr/bin/env python3
"""
Flow Cell System Diagnostic Tool

Quickly check if everything is ready for your demo.
"""

import sys
import cv2
from pathlib import Path
import yaml


def check_camera():
    """Test camera availability."""
    print("\n1. CAMERA CHECK")
    print("-" * 50)

    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        print(f"✅ Camera 0 detected")
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps}")
        return True
    else:
        print("❌ Camera 0 not available")
        print("   Try: python test_flow_cell.py --list")
        return False


def check_files():
    """Check required files exist."""
    print("\n2. FILE CHECK")
    print("-" * 50)

    required_files = [
        ('flow_cell_scanner.py', 'Main scanner (GUI)'),
        ('flow_cell_headless.py', 'Headless scanner'),
        ('test_flow_cell.py', 'Camera test tool'),
        ('config/config.yaml', 'Pipeline configuration'),
        ('modules/acquisition.py', 'Acquisition module'),
        ('modules/preprocessing.py', 'Preprocessing module'),
        ('modules/segmentation.py', 'Segmentation module'),
        ('modules/classification.py', 'Classification module'),
    ]

    all_good = True
    for filepath, description in required_files:
        path = Path(filepath)
        if path.exists():
            print(f"✅ {filepath:<30} ({description})")
        else:
            print(f"❌ {filepath:<30} MISSING!")
            all_good = False

    return all_good


def check_config():
    """Validate configuration file."""
    print("\n3. CONFIGURATION CHECK")
    print("-" * 50)

    config_path = Path('config/config.yaml')
    if not config_path.exists():
        print("❌ config/config.yaml not found")
        return False

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check key sections
        sections = ['acquisition', 'preprocessing', 'segmentation', 'classification']
        all_good = True

        for section in sections:
            if section in config:
                print(f"✅ {section:20} configured")
            else:
                print(f"❌ {section:20} MISSING!")
                all_good = False

        return all_good

    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False


def check_models():
    """Check if models exist."""
    print("\n4. MODEL CHECK")
    print("-" * 50)

    models_dir = Path('models')
    if not models_dir.exists():
        print("❌ models/ directory not found")
        return False

    # Look for any .keras or .h5 files
    keras_models = list(models_dir.glob('*.keras'))
    h5_models = list(models_dir.glob('*.h5'))

    if keras_models or h5_models:
        print(f"✅ Found {len(keras_models)} .keras models")
        for model in keras_models[:3]:  # Show first 3
            print(f"   - {model.name}")
        return True
    else:
        print("⚠️  No .keras models found")
        print("   System will use stub classification")
        return True  # Not critical


def check_dependencies():
    """Check Python dependencies."""
    print("\n5. DEPENDENCY CHECK")
    print("-" * 50)

    required = {
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'yaml': 'PyYAML',
    }

    all_good = True
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✅ {name:20} installed")
        except ImportError:
            print(f"❌ {name:20} MISSING!")
            all_good = False

    return all_good


def check_permissions():
    """Check file permissions."""
    print("\n6. PERMISSIONS CHECK")
    print("-" * 50)

    scripts = [
        'flow_cell_scanner.py',
        'flow_cell_headless.py',
        'test_flow_cell.py',
    ]

    all_good = True
    for script in scripts:
        path = Path(script)
        if path.exists() and path.stat().st_mode & 0o111:
            print(f"✅ {script:30} executable")
        else:
            print(f"⚠️  {script:30} not executable")
            print(f"   Fix with: chmod +x {script}")
            all_good = False

    return all_good


def check_results_dir():
    """Check results directory."""
    print("\n7. RESULTS DIRECTORY CHECK")
    print("-" * 50)

    results_dir = Path('results')
    if not results_dir.exists():
        print("⚠️  results/ directory doesn't exist")
        print("   It will be created automatically")
        return True
    else:
        # Count existing flow cell results
        flow_results = list(results_dir.glob('flow_cell_*'))
        print(f"✅ results/ directory exists")
        print(f"   Found {len(flow_results)} previous flow cell scans")
        return True


def run_diagnostics():
    """Run all diagnostics."""
    print("="*60)
    print("FLOW CELL SYSTEM DIAGNOSTICS")
    print("="*60)

    checks = [
        ("Camera", check_camera),
        ("Files", check_files),
        ("Configuration", check_config),
        ("Models", check_models),
        ("Dependencies", check_dependencies),
        ("Permissions", check_permissions),
        ("Results Directory", check_results_dir),
    ]

    results = {}
    for name, check_func in checks:
        results[name] = check_func()

    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:25} {status}")

    print("-"*60)
    print(f"Score: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 ALL SYSTEMS GO! You're ready for the demo!")
        print("\nQuick start:")
        print("  python test_flow_cell.py --camera 0")
        print("  python flow_cell_scanner.py --camera 0 --duration 120")
        return 0
    elif passed >= total - 2:
        print("\n⚠️  MOSTLY READY - Minor issues detected")
        print("   Review the failures above")
        print("   System should still work for demo")
        return 0
    else:
        print("\n❌ CRITICAL ISSUES - Please fix before demo")
        print("   Review the failures above")
        return 1


if __name__ == '__main__':
    exit_code = run_diagnostics()
    sys.exit(exit_code)
