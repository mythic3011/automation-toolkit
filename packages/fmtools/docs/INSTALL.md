# Install fmtools

To install the standalone Rust tools through Homebrew or Scoop, follow the [package manager guide](../../../docs/PACKAGE_MANAGERS.md). The instructions below install the separate Python `fmtools` CLI.

fmtools supports Python 3.8 and newer. Install it from the repository root in a virtual environment.

```sh
python -m venv .venv
```

Activate the environment, then install the package:

```powershell
# PowerShell
.venv\Scripts\Activate.ps1
python -m pip install ./packages/fmtools
```

```sh
# Linux or macOS
source .venv/bin/activate
python -m pip install ./packages/fmtools
```

Check the installation:

```sh
fmtools --help
python -m fmtools --version
```

For image compression, install the optional `full` extra:

```sh
python -m pip install "./packages/fmtools[full]"
```

For development, install the editable package and development dependencies:

```sh
python -m pip install -e "./packages/fmtools[dev]" build
```

Conversion and GIF speed commands use MoviePy 1.x and FFmpeg through `imageio-ffmpeg`. Some formats may require codecs supported by the available FFmpeg binary. See [the package README](../README.md) for command examples and configuration details.

## Optional Rust executables

The Python implementations work without Rust. The package can use bundled Rust executables for deduplication, renaming, and organization when available. See the [Rust guide](USE_RUST_GUIDE.md) for building them.

## Configuration and logs

Configuration and log files are stored under `%APPDATA%\fmtools\` on Windows and `~/.fmtools/` on Linux and macOS. Use `fmtools --config PATH COMMAND` to select a configuration file.

## Uninstall

With the virtual environment activated, run:

```sh
python -m pip uninstall fmtools
```

Remove the configuration directory separately if you also want to delete saved settings and logs.
