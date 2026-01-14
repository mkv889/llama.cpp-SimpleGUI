#!/bin/bash
# Installer script for llama.cpp-SimpleGUI
# This script ensures Python is installed and checks for required dependencies

echo "============================================"
echo "llama.cpp-SimpleGUI Installation Script"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo ""
    echo "Please install Python 3.6 or higher:"
    echo "  - Ubuntu/Debian: sudo apt-get install python3"
    echo "  - Fedora: sudo dnf install python3"
    echo "  - macOS: brew install python3 or download from python.org"
    exit 1
fi

echo "Python is installed:"
python3 --version
echo ""

# Check Python version (requires Python 3.6+)
python3 -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.6 or higher is required."
    echo "Please upgrade your Python installation."
    exit 1
fi

echo "Checking for tkinter..."
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: tkinter is not available!"
    echo ""
    echo "Please install tkinter for your system:"
    echo "  - Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  - Fedora: sudo dnf install python3-tkinter"
    echo "  - macOS: brew install python-tk (if using Homebrew Python)"
    echo "           or use Python from python.org (includes tkinter)"
    echo ""
    exit 1
else
    echo "tkinter is available."
fi

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""
echo "All required dependencies are installed."
echo "You can now run the application with:"
echo "    python3 llama_gui.py"
echo ""
echo "Or make it executable:"
echo "    chmod +x llama_gui.py"
echo "    ./llama_gui.py"
echo ""
echo "Note: Make sure you have llama.cpp installed separately."
echo "See: https://github.com/ggml-org/llama.cpp"
echo ""
