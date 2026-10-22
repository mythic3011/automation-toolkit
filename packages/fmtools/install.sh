#!/bin/bash
# fmtools Installation Script for Linux/macOS
# This script installs the fmtools package and sets up Rust executables

set -e

echo "========================================"
echo "fmtools Installation Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
fi

# Check Python version
echo "[1/4] Checking Python version..."
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.8 or higher is required"
    exit 1
fi
echo "    Python version OK"

# Check if uv is installed, if not install it
echo ""
echo "[2/4] Checking uv installation..."
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh || {
        echo "ERROR: Failed to install uv"
        exit 1
    }
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo "    uv is ready"

# Install fmtools
echo ""
echo "[3/4] Installing fmtools package..."
uv pip install -e . || {
    echo "ERROR: Failed to install fmtools"
    exit 1
}

# Install optional dependencies
echo ""
echo "[4/4] Installing optional dependencies..."
uv pip install Pillow || echo "WARNING: Could not install Pillow (image compression will not work)"

# Check for Rust binaries
echo ""
if [ -d "exe" ]; then
    # Make Rust binaries executable on Linux/macOS
    if [ "$(uname)" != "Darwin" ]; then
        find exe -type f -executable -exec chmod +x {} \; 2>/dev/null || true
    fi
    echo "Rust executables are located in: exe/"
else
    echo "NOTE: Rust executables not found. Python implementations will be used."
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Quick Start:"
echo "  fmtools --help                     # Show all commands"
echo "  fmtools dedup ~/folder --dry-run   # Find duplicates"
echo "  fmtools organize --source ~/Downloads --mode type"
echo ""
echo "For detailed documentation, see:"
echo "  README.md"
echo "  QUICK_START.md"
echo "  USE_RUST_GUIDE.md"
echo ""
echo "Configuration file will be created at:"
echo "  ~/.fmtools/config.yaml"
echo ""

