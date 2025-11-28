#!/bin/bash
# Setup virtual environment for download tools

echo "🔧 Setting up download tools virtual environment..."

# Create virtual environment
python3 -m venv .venv_download

# Activate
source .venv_download/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install requests beautifulsoup4

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "To use the download tools:"
echo "  1. Activate: source .venv_download/bin/activate"
echo "  2. Run tool: python3 tools/download_santa_ana_meetings.py --help"
echo "  3. Deactivate when done: deactivate"
echo ""
