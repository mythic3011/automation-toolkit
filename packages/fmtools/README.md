# fmtools — File Management Tools

A Python CLI for common file operations, with optional Rust executables for deduplication, renaming, and organization.

## Install

Requires Python 3.8 or newer. From the repository root, with a virtual environment activated:

```sh
python -m pip install ./packages/fmtools
fmtools --help
python -m fmtools --version
```

Install image compression support with `python -m pip install "./packages/fmtools[full]"`. For development, use `python -m pip install -e "./packages/fmtools[dev]"`.

The Python implementations ship inside the package, so installed commands work outside the repository. The scripts under `scripts/` remain compatibility entry points for source checkouts.

## Commands

| Command | Purpose | Example |
| --- | --- | --- |
| `dedup` | Find duplicate files by content | `fmtools dedup ./photos --dry-run` |
| `rename` | Number files with a prefix or suffix | `fmtools rename --directory ./photos --extension jpg --prefix photo_ --dry-run` |
| `organize` | Sort files by type, date, or size | `fmtools organize --source ./downloads --dest ./sorted --mode type --dry-run` |
| `clean` | Remove empty directories | `fmtools clean --directory ./workspace --dry-run` |
| `stats` | Summarize file types, sizes, and duplicates | `fmtools stats --directory ./photos --export-json stats.json` |
| `convert` | Convert media formats | `fmtools convert --input-dir ./videos --output-dir ./converted --from mp4 --to webm` |
| `speed` | Adjust GIF playback speed | `fmtools speed --input-dir ./gifs --output-dir ./faster --speed 2` |
| `hash` | Generate or verify checksums | `fmtools hash ./example.txt --algorithm sha256` |
| `backup` | Copy or archive a directory | `fmtools backup ./documents ./backups --dry-run` |
| `find` | Search with name, extension, size, and age filters | `fmtools find --directory . --extension txt` |
| `compress` | Compress images or create archives | `fmtools compress --directory ./photos --type archive --output photos.zip --dry-run` |
| `config` | Show, change, or reset saved settings | `fmtools config show` |

Run `fmtools COMMAND --help` for all options. `--dry-run` previews the commands shown above without applying their file changes. Deduplication prompts before deletion unless `--batch` is specified.

## Configuration

The default configuration is stored at `%APPDATA%\fmtools\config.yaml` on Windows and `~/.fmtools/config.yaml` on Linux/macOS. Pass a custom file before the subcommand:

```sh
fmtools --config ./settings.yaml config set defaults.dedup.algorithm sha256
fmtools --config ./settings.yaml config get defaults.dedup.algorithm
fmtools --config ./settings.yaml config reset
```

Configuration files have independent defaults. Logs are written to the configuration directory unless configured otherwise.

## Media processing

Conversion and GIF speed adjustment use the MoviePy 1.x API. The package declares the compatible version range; install dependencies through the package metadata. MoviePy uses FFmpeg through `imageio-ffmpeg`. Some operations also require codecs supported by the FFmpeg binary on your system.

## Optional Rust tools

Python implementations are available without Rust. Deduplication, renaming, and organization choose a bundled Rust executable when one is available for the current platform and the configured file-count threshold is exceeded. Use `--force-python` to select Python, or `--force-rust` to request Rust.

Packaged executables live under `src/fmtools/bin/<platform>/` in a source checkout and `fmtools/bin/<platform>/` after installation. The platform directories are `windows`, `linux`, `macos-x64`, and `macos-arm64`.

After a Rust executable starts, fmtools propagates its exit status and does not retry the operation in Python. Organizer `--exclude` (repeatable) and `--report` require Rust; requests fail clearly when Rust is unavailable or `--force-python` is set. Rust conversions also reject output collisions and existing files, publish each result without replacement, and return a nonzero status if any file fails. See the [Rust guide](docs/USE_RUST_GUIDE.md) for details.

See the [Rust workspace](rust/) and the root release workflow for build targets. A locally built wheel without these executables uses Python implementations.

## Tests and distribution

From this directory, after installing the development dependencies:

```sh
python -m pytest
python -m pip install build
python -m build
```

The tests use temporary files and isolated configuration directories. Packaging checks exercise the command adapters without relying on the checkout's `scripts/` directory.
