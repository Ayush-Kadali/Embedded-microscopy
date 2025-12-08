#!/usr/bin/env python3
"""
Setup Verification Script

Run this script to verify that your development environment is properly configured.
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need Python 3.8+)")
        return False


def check_dependencies():
    """Check required dependencies."""
    print("\nChecking dependencies...")
    required = {
        'numpy': 'NumPy',
        'cv2': 'OpenCV',
        'yaml': 'PyYAML',
    }

    all_ok = True
    for module_name, display_name in required.items():
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} (Not installed)")
            all_ok = False

    return all_ok


def check_project_structure():
    """Check project directory structure."""
    print("\nChecking project structure...")

    required_dirs = [
        'modules',
        'pipeline',
        'config',
        'tests',
        'docs',
        'results',
        'models',
    ]

    all_ok = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (Missing)")
            all_ok = False

    return all_ok


def check_config_files():
    """Check configuration files."""
    print("\nChecking configuration files...")

    required_files = [
        'config/config.yaml',
        'requirements.txt',
        'main.py',
    ]

    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (Missing)")
            all_ok = False

    return all_ok


def check_module_imports():
    """Check if modules can be imported."""
    print("\nChecking module imports...")

    modules = [
        'modules.base',
        'modules.acquisition',
        'modules.preprocessing',
        'modules.segmentation',
        'modules.classification',
        'modules.counting',
        'modules.analytics',
        'modules.export',
        'pipeline.manager',
    ]

    all_ok = True
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {module_name}")
        except Exception as e:
            print(f"  ✗ {module_name} ({e})")
            all_ok = False

    return all_ok


def check_pipeline_execution():
    """Check if pipeline can be initialized."""
    print("\nChecking pipeline initialization...")

    try:
        import yaml
        from pipeline import PipelineManager

        # Load config
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        # Initialize pipeline
        pipeline = PipelineManager(config)

        print("  ✓ Pipeline initialized successfully")
        return True
    except Exception as e:
        print(f"  ✗ Pipeline initialization failed: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 70)
    print("Marine Plankton AI Microscopy System - Setup Verification")
    print("=" * 70)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Configuration Files", check_config_files),
        ("Module Imports", check_module_imports),
        ("Pipeline Initialization", check_pipeline_execution),
    ]

    results = {}
    for check_name, check_func in checks:
        results[check_name] = check_func()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    all_passed = all(results.values())
    passed = sum(results.values())
    total = len(results)

    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {check_name}")

    print(f"\nTotal: {passed}/{total} checks passed")

    if all_passed:
        print("\n🎉 All checks passed! Your environment is ready.")
        print("\nNext steps:")
        print("  1. Run the pipeline: python main.py")
        print("  2. Read QUICKSTART.md for usage examples")
        print("  3. Read docs/DEVELOPER_GUIDE.md for development")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Activate virtual environment: source .venv/bin/activate")
        print("  - Check you're in the project root directory")
        return 1


if __name__ == '__main__':
    sys.exit(main())
