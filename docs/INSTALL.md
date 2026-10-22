# Installation Guide for fmtools

## Quick Install

### Windows

```batch
# Clone or download the repository
git clone https://github.com/mythic3011/automation-toolkit.git
cd automation-toolkit/packages/fmtools

# Run the installer
install.bat
```

### Linux / macOS

```bash
# Clone or download the repository
git clone https://github.com/mythic3011/automation-toolkit.git
cd automation-toolkit/packages/fmtools

# Make the installer executable and run it
chmod +x install.sh
./install.sh
```

### Via uv (recommended)

```bash
uv pip install fmtools

# Or with all optional features
uv pip install fmtools[full]
```

### Via pip

```bash
pip install fmtools

# Or with all optional features
pip install fmtools[full]
```

---

## Manual Installation

### Prerequisites

1. **Python 3.8 or higher**

   ```bash
   python --version
   # Should show Python 3.8.x or higher
   ```

2. **uv (Fast Python package manager - recommended)**

   ```bash
   # Install uv
   # Linux/macOS:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell):
   irm https://astral.sh/uv/install.ps1 | iex

   # Or via pip:
   pip install uv
   ```

3. **FFmpeg (for media conversion)**
   - **Windows**: Download from https://ffmpeg.org/ and add to PATH
   - **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo yum install ffmpeg` (RHEL/CentOS)
   - **macOS**: `brew install ffmpeg`

### Step-by-Step Installation

1. **Download the source code**

   ```bash
   git clone https://github.com/mythic3011/automation-toolkit.git
   cd automation-toolkit/packages/fmtools
   ```

2. **Install Python dependencies**

   ```bash
   # Using uv (recommended - much faster)
   uv pip install -r requirements.txt

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Install the fmtools package**

   ```bash
   # Using uv (recommended)
   # Development mode (editable install)
   uv pip install -e .

   # Or regular install
   uv pip install .

   # Or using pip
   pip install -e .
   ```

4. **Install optional dependencies**

   ```bash
   # Using uv (recommended)
   # For image compression
   uv pip install Pillow

   # For development
   uv pip install -e .[dev]

   # Everything
   uv pip install -e .[full,dev]

   # Or using pip
   pip install Pillow
   pip install -e .[dev]
   pip install -e .[full,dev]
   ```

5. **Verify installation**
   ```bash
   fmtools --version
   fmtools --help
   ```

---

## Platform-Specific Notes

### Windows

- **PowerShell Execution Policy**: If you get an error running scripts, you may need to change the execution policy:

  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **PATH Configuration**: The installer will attempt to add fmtools to your PATH. If `fmtools` command is not found, you may need to restart your terminal or add Python's Scripts folder to PATH manually.

- **Rust Executables**: Windows executables are pre-built and included in the `exe/` directory.

### Linux

- **Permissions**: You may need to run with `sudo` for system-wide installation:

  ```bash
  sudo uv pip install .
  # or with pip:
  sudo pip install .
  ```

- **User Installation**: For user-only installation (recommended):

  ```bash
  uv pip install --user .
  # or with pip:
  pip install --user .
  ```

- **Rust Executables**: Linux binaries need to be built from source (see Cross-Platform Builds below) or you can use the Python implementations.

### macOS

- **Homebrew Python**: If using Homebrew Python, ensure you're using the correct package manager:

  ```bash
  uv pip install .
  # or with pip:
  python3 -m pip install .
  ```

- **Apple Silicon (M1/M2)**: Make sure you install the ARM64 version of Python for best performance.

- **Rust Executables**: macOS binaries need to be built from source or you can use the Python implementations.

---

## Rust Tools Setup

### Using Pre-Built Binaries (Windows)

Pre-built Windows executables are included in the `exe/` directory. They will be automatically used when:

- Dataset is large (>1,000 files by default)
- You explicitly request with `--force-rust` flag

### Building from Source

If you want to build the Rust versions yourself or need them for Linux/macOS:

1. **Install Rust**

   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Build all tools**

   ```bash
   cd rust_tools
   cargo build --release
   ```

3. **Copy binaries to exe directory**

   ```bash
   # Windows
   copy target\release\*.exe ..\exe\

   # Linux/macOS
   cp target/release/dupeforge-rs ../exe/
   cp target/release/rename_files ../exe/
   cp target/release/organize_files ../exe/
   cp target/release/convert_media ../exe/
   ```

### Cross-Platform Builds

For building on all platforms, see the `build_all.sh` script or use GitHub Actions.

---

## Configuration

After installation, fmtools creates a configuration directory:

- **Windows**: `%APPDATA%\fmtools\`
- **Linux/macOS**: `~/.fmtools/`

Default configuration file (`config.yaml`) will be created on first run.

You can customize defaults:

```bash
fmtools config show
fmtools config set defaults.dedup.algorithm md5
fmtools config set rust.threshold 500
```

---

## Troubleshooting

### Common Issues

**"fmtools: command not found"**

- Ensure Python's Scripts directory is in your PATH
- Try running with `python -m fmtools` instead
- Restart your terminal after installation

**"ModuleNotFoundError: No module named 'yaml'"**

```bash
uv pip install PyYAML
# or with pip:
pip install PyYAML
```

**"ModuleNotFoundError: No module named 'tqdm'"**

```bash
uv pip install -r requirements.txt
# or with pip:
pip install -r requirements.txt
```

**"ffmpeg not found" when converting media**

- Install FFmpeg (see Prerequisites above)
- Ensure ffmpeg is in your system PATH

**Rust executables not working**

- On Linux/macOS, ensure they're executable: `chmod +x exe/*`
- Build from source if pre-built binaries aren't available for your platform
- Fall back to Python versions (automatically done if Rust binaries unavailable)

**Permission denied errors**

- Use `uv pip install --user .` for user-only installation
- Don't use `sudo pip` or `sudo uv pip` on Linux/macOS (use virtual environments instead)

### Getting Help

If you encounter issues:

1. Check the [QUICK_START.md](QUICK_START.md) for common tasks
2. Read [USE_RUST_GUIDE.md](USE_RUST_GUIDE.md) for performance tips
3. Enable verbose logging: `fmtools --verbose COMMAND`
4. Check log files in `~/.fmtools/` or `%APPDATA%\fmtools\`
5. Open an issue on GitHub with error details

---

## Uninstallation

```bash
uv pip uninstall fmtools
# or with pip:
pip uninstall fmtools
```

To remove configuration files:

```bash
# Windows
rmdir /s %APPDATA%\fmtools

# Linux/macOS
rm -rf ~/.fmtools
```

---

## Next Steps

After installation:

1. Read [GETTING_STARTED.md](GETTING_STARTED.md) for your first tasks
2. Try: `fmtools dedup ~/Downloads --dry-run`
3. Explore: `fmtools --help`
4. Configure: `fmtools config show`

For more examples, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md).
