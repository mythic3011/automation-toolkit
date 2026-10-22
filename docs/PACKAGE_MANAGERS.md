# Homebrew and Scoop

The `automation-toolkit` package installs four native Rust commands. It does not require Python. The Python `fmtools` CLI has additional commands and can be [installed separately](../packages/fmtools/docs/INSTALL.md).

| Command | Purpose |
| --- | --- |
| `dupeforge-rs` | Find and remove duplicate files |
| `rename_files` | Rename files with sequential numbering |
| `organize_files` | Organize files by type, date, or size |
| `convert_media` | Convert media using FFmpeg |

## Homebrew: macOS and Linux

```sh
brew tap mythic3011/automation-toolkit https://github.com/mythic3011/automation-toolkit.git
brew install mythic3011/automation-toolkit/automation-toolkit
```

The explicit tap URL is required because the repository is named `automation-toolkit`. Homebrew verifies the source archive's SHA-256, installs Rust as a build dependency, and builds the locked workspace. This supports Intel and Apple Silicon macOS as well as Linux systems supported by Homebrew.

For media conversion, install FFmpeg separately:

```sh
brew install ffmpeg
```

Upgrade or uninstall:

```sh
brew update
brew upgrade mythic3011/automation-toolkit/automation-toolkit
brew uninstall automation-toolkit
```

## Scoop: Windows x64

With [Scoop](https://scoop.sh/) installed, run in PowerShell:

```powershell
scoop bucket add automation-toolkit https://github.com/mythic3011/automation-toolkit.git
scoop install automation-toolkit/automation-toolkit
```

Scoop verifies a Windows x64 ZIP's SHA-256 and creates shims for all four executables. The binaries include the C runtime and do not need Rust installed.

For media conversion:

```powershell
scoop install main/ffmpeg
```

Upgrade or uninstall:

```powershell
scoop update
scoop update automation-toolkit
scoop uninstall automation-toolkit
```

## Use the commands

Start with command help and previews. Replace these example paths with your own:

```sh
dupeforge-rs ./downloads --dry-run
rename_files --directory ./photos --extension jpg --prefix photo_ --dry-run
organize_files --source ./downloads --dest ./sorted --mode type --dry-run
convert_media --help
```

Remove `--dry-run` to apply an operation. The organizer copies by default; add `--move` to move files. Duplicate removal prompts for confirmation unless `--batch` is supplied. Conversion uses `ffmpeg` on PATH, or the executable specified by `FMTOOLS_FFMPEG`.

## Maintain releases

Native versions track `[workspace.package].version` in `packages/fmtools/rust/Cargo.toml`. Tags use `toolkit-vMAJOR.MINOR.PATCH`, independently of Python package versions and PyPI releases.

After updating the workspace version and running CI, push a native release tag:

```sh
git tag toolkit-v1.0.2
git push main toolkit-v1.0.2
```

Here `main` is this checkout's Git remote name. Replace it with your own remote name when needed. Alternatively, run the **Native toolkit release** workflow manually with the matching workspace version. Use only one trigger per release.

The workflow builds Windows x64, Linux x64, Intel macOS, and Apple Silicon macOS archives. It creates a source archive, generates `SHA256SUMS`, publishes a GitHub release, then commits updated installers to the default branch. The Homebrew formula uses the source archive; Scoop uses the Windows archive. Native release tags are excluded from the PyPI workflow.

The first release includes source and Windows archives. Additional platform binaries are produced by subsequent native workflow releases; Homebrew builds from source on every supported platform.

After publishing, run the **CI** workflow manually to exercise a real Homebrew install and `brew test` on macOS, alongside the regular test suite.

For local packaging, use Python 3.11 or newer from the repository root:

```powershell
$env:RUSTFLAGS = '-C target-feature=+crt-static'
cargo build --manifest-path packages/fmtools/rust/Cargo.toml --locked --release --workspace --target x86_64-pc-windows-msvc
python tools/native_release.py bundle --version 1.0.1 --target x86_64-pc-windows-msvc --binary-dir packages/fmtools/rust/target/x86_64-pc-windows-msvc/release --output dist/native-1.0.1
python tools/native_release.py source --version 1.0.1 --output dist/native-1.0.1
python tools/native_release.py manifests --version 1.0.1 --assets dist/native-1.0.1 --output-root .
python -m unittest discover -s tools/tests -v
```

Build each target on a host with the required compiler and linker. Use a fresh output directory for every release attempt: the helper refuses to overwrite archives. Finish documentation before making the source archive, and generate installers from the exact archives that will be uploaded.

Publish assets before making updated installer definitions available. Existing release assets must keep their original bytes and checksums. If release publication succeeds but the default-branch manifest push fails, copy the generated installers for that release into the latest default branch and push them normally; rerunning release creation will refuse the existing release.
