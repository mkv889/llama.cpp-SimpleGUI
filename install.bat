@echo off
REM Installer script for llama.cpp-SimpleGUI
REM This script ensures Python is installed and checks for required dependencies

echo ============================================
echo llama.cpp-SimpleGUI Installation Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.6 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python is installed:
python --version
echo.

REM Check Python version (requires Python 3.6+)
python -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.6 or higher is required.
    echo Please upgrade your Python installation.
    pause
    exit /b 1
)

echo Checking for tkinter...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: tkinter is not available!
    echo.
    echo tkinter should be included with the standard Python installer from python.org
    echo If you installed Python from python.org, try reinstalling and ensure
    echo "tcl/tk and IDLE" is checked during installation.
    echo.
    pause
    exit /b 1
) else (
    echo tkinter is available.
)

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo All required dependencies are installed.
echo You can now run the application with:
echo     python llama_gui.py
echo.
echo Note: Make sure you have llama.cpp installed separately.
echo On Windows, you can install it with:
echo     winget install llama.cpp
echo.
pause
