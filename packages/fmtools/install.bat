@echo off
REM fmtools Installation Script for Windows
REM This script installs the fmtools package and sets up Rust executables

echo ========================================
echo fmtools Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    pause
    exit /b 1
)
echo     Python version OK

echo.
echo [2/4] Checking uv installation...
uv --version >nul 2>&1
if errorlevel 1 (
    echo uv not found. Installing uv...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if errorlevel 1 (
        echo ERROR: Failed to install uv
        pause
        exit /b 1
    )
)
echo     uv is ready

echo.
echo [3/4] Installing fmtools package...
uv pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install fmtools
    pause
    exit /b 1
)

echo.
echo [4/4] Installing optional dependencies...
uv pip install Pillow
if errorlevel 1 (
    echo WARNING: Could not install Pillow (image compression will not work)
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Rust executables are located in: exe\
echo.
echo Quick Start:
echo   fmtools --help                     Show all commands
echo   fmtools dedup ~/folder --dry-run   Find duplicates
echo   fmtools organize --source ~/Downloads --mode type
echo.
echo For detailed documentation, see:
echo   README.md
echo   QUICK_START.md
echo   USE_RUST_GUIDE.md
echo.
echo Configuration file will be created at:
echo   %%APPDATA%%\fmtools\config.yaml
echo.

pause

