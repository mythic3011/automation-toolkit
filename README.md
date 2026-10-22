# Automation Toolkit

Automation tools for file management and standalone utilities. The two packages are independent: install only the tools you need. Linux Secure Server Setup is maintained in a separate repository.

```sh
git clone https://github.com/mythic3011/automation-toolkit.git
cd automation-toolkit
```

| Package | Purpose | Requirements |
| --- | --- | --- |
| [fmtools](packages/fmtools/) | Python CLI for deduplication, organization, renaming, checksums, and backups; optional Rust tools | Python 3.8+ |
| [Standalone scripts](packages/scripts/) | Individual Python utilities | Python 3.8+ and each script's dependencies |

## File management

Install the four native Rust tools with Homebrew on macOS/Linux:

```sh
brew tap mythic3011/automation-toolkit https://github.com/mythic3011/automation-toolkit.git
brew install mythic3011/automation-toolkit/automation-toolkit
```

Or with Scoop on Windows x64:

```powershell
scoop bucket add automation-toolkit https://github.com/mythic3011/automation-toolkit.git
scoop install automation-toolkit/automation-toolkit
```

These installs provide `dupeforge-rs`, `rename_files`, `organize_files`, and `convert_media`. Preview organization with `organize_files --source ./downloads --dest ./sorted --dry-run`. See the [package manager guide](docs/PACKAGE_MANAGERS.md) for examples, FFmpeg, upgrades, and release maintenance.

The Python CLI provides additional commands and is installed separately.
From the repository root, install fmtools in a Python virtual environment:

```sh
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on Linux/macOS, or `.venv\Scripts\Activate.ps1` in PowerShell, then install:

```sh
python -m pip install ./packages/fmtools
fmtools --help
```

Preview file operations before applying them:

```sh
fmtools dedup ~/Downloads --dry-run
fmtools organize --source ~/Downloads --dest ~/Organized --mode type --dry-run
fmtools rename --directory ./photos --extension jpg --prefix photo_ --dry-run
fmtools clean --directory ./workspace --dry-run
```

Other commands include `stats`, `convert`, `speed`, `hash`, `backup`, `find`, `compress`, and `config`. Run `fmtools COMMAND --help` for the accepted options. See the [fmtools README](packages/fmtools/README.md) for installation, media dependencies, and optional Rust tools.

## Standalone utilities

Scripts in `packages/scripts/python/` have their own command interfaces:

```sh
python packages/scripts/python/delete_duplicates.py ~/Downloads --dry-run
python packages/scripts/python/file_stats.py --directory . --export-json stats.json
```

See the [script catalog](packages/scripts/README.md) for dependencies and options. The files named `test.py` and `test_tools.py` in the script collections are legacy helpers; the automated fmtools suite lives in `packages/fmtools/tests/`.

## Development and validation

Run Python checks from the repository root:

```sh
python -m pip install -e "./packages/fmtools[dev]"
python -m pytest
cd packages/fmtools
python -m build
```

The root pytest configuration collects the fmtools suite and leaves the legacy helper scripts out of test discovery.

Check native release packaging from the root with Python 3.11 or newer:

```sh
python -m unittest discover -s tools/tests -v
```

Check shell syntax from the repository root using Bash:

```bash
while IFS= read -r -d '' script; do
  bash -n "$script" || exit 1
done < <(git ls-files -z -- '*.sh')
```

The root [CI workflow](.github/workflows/ci.yml) runs Python tests, a wheel installation check, Rust tests and Clippy, native packaging tests, and shell syntax checks. The [native release workflow](.github/workflows/native-release.yml) builds platform archives and updates the Homebrew and Scoop installers.

## Repository layout

```text
packages/
  fmtools/             Python package, Rust workspace, tests, and CLI docs
  scripts/python/      Standalone Python utilities
docs/                  Existing guides and historical project notes
Formula/               Homebrew formula for the native Rust tools
bucket/                Scoop manifest for Windows x64
tools/native_release.py  Reproducible release archives and installer generation
tools/archive/         Historical repository restructuring helpers
.github/workflows/     CI, native toolkit, and PyPI release workflows
```

Package READMEs and command help describe the current entry points. Older guides under `docs/` may reference paths from before the monorepo restructure.

Licensed under [MIT](LICENSE).
