#!/bin/bash
# EcoTaxa Exploration Setup Script

set -e  # Exit on error

echo "======================================"
echo "EcoTaxa Exploration Setup"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

# Install EcoTaxa client from GitHub
echo ""
echo "Installing EcoTaxa Python client..."
pip install git+https://github.com/ecotaxa/ecotaxa_py_client.git

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Read getting started guide:"
echo "     cat GETTING_STARTED.md"
echo ""
echo "  3. Test authentication:"
echo "     python scripts/01_basic_authentication.py"
echo ""
echo "  4. Set environment variables (optional):"
echo "     export ECOTAXA_USERNAME='your_username'"
echo "     export ECOTAXA_PASSWORD='your_password'"
echo ""
echo "======================================"
