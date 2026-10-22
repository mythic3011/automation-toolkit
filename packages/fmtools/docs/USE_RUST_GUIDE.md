# Optional Rust executables

fmtools includes Python implementations for its supported commands. Rust executables are optional and are used by `dedup`, `rename`, and `organize` when a matching executable is available and the configured file-count threshold is exceeded. Use `--force-python` to select Python or `--force-rust` to request Rust for a command that supports it.

Build from the repository checkout with Rust installed. Run these commands from `packages/fmtools`:

```sh
bash build_all.sh
```

With no target argument, the script builds for the host Rust target. To request a supported target explicitly, pass one of:

```sh
bash build_all.sh x86_64-pc-windows-msvc
bash build_all.sh x86_64-unknown-linux-gnu
bash build_all.sh x86_64-apple-darwin
bash build_all.sh aarch64-apple-darwin
```

The script places executables in `src/fmtools/bin/<platform>/`, using `windows`, `linux`, `macos-x64`, or `macos-arm64` for `<platform>`. Build natively on the target platform when cross-compilation tools are not configured. A wheel built from a checkout without these files uses the Python implementations. The release workflow builds the supported platform binaries and packages them into the wheel.

The runtime selects Rust automatically only when a matching bundled binary is present and the file-count threshold is met. `--force-python` always selects the Python implementation. `--force-rust` returns to Python with a message if the executable is unavailable; it does not make an unsupported platform executable run.

Once a Rust process starts and exits, fmtools returns its exit status and does not repeat the operation in Python. This avoids applying a destructive operation twice after Rust reports a partial failure. Python fallback is reserved for cases where a Rust executable cannot be launched.

The Rust organizer also supports safety options that the Python organizer does not implement. Repeat `--exclude` to skip basenames or source-relative paths, and use `--report` to create a JSONL operation journal:

```sh
fmtools organize --source ./downloads --dest ./sorted --recursive \
  --exclude .DS_Store --exclude private/notes.txt \
  --report ./organize-report.jsonl --dry-run
```

These options select Rust even below the normal file-count threshold. They return an error if the matching executable is unavailable, and cannot be combined with `--force-python`; fmtools never silently drops an exclusion or report request. The journal is created only at a new path and records planned, skipped, failed, and completed operations. If an organizer run reports failures, inspect the journal and filesystem before retrying it.

The JSONL journal is an audit record only; it does not roll back changes or resume an interrupted operation. Treat the filesystem as authoritative when reviewing a partial run. Rust move operations refuse to overwrite a destination. If a move crosses filesystem volumes and the operating system cannot move it atomically, the operation fails and retains the source; fmtools does not copy-and-delete as a fallback.

Rust conversions validate extensions and numeric options, plan output names before processing, preserve relative directories in recursive mode, and refuse output collisions or existing destinations. Each successful conversion is published from a private temporary directory without replacing an existing file. Any per-file conversion failure makes the command exit nonzero; inspect the reported files before retrying.

The optional Rust binaries accelerate fmtools operations; they do not define the package's platform support. Removing a separate Linux server or deployment package does not remove the cross-platform fmtools Python package or its Windows, Linux, and macOS support.

Examples, from any working directory after installation:

```sh
fmtools dedup ./downloads --dry-run --force-rust
fmtools rename --directory ./photos --extension jpg --dry-run --force-rust
fmtools organize --source ./downloads --dest ./sorted --mode type --dry-run --force-rust
```

Use `--force-python` in place of `--force-rust` to exercise those commands without Rust. See the [installation guide](INSTALL.md) and [command reference](COMMAND_REFERENCE.md) for the package setup and available commands.
