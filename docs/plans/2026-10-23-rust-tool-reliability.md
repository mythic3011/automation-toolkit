# Rust Tool Reliability Implementation Plan

**Goal:** Make the Rust file tools report failures accurately and preserve files when names collide, paths are invalid, or a file is locked.

**Architecture:** Keep the four existing commands and their flags. Share small no-overwrite file primitives through `fmtools-fs`; keep planning and command-specific recovery in each binary. Exercise changes only on temporary fixtures. Existing Downloads organization is complete and is not rerun during this work.

**Tech stack:** Rust standard library, Cargo workspace, existing Clap/Serde/Rayon dependencies, pytest for Python adapter integration, GitHub Actions.

## 1. Shared file operations

- Add `packages/fmtools/rust/fmtools-fs/` and register it in `packages/fmtools/rust/Cargo.toml`.
- Reproduce overwrite behavior with tests before replacing it with exclusive file creation and no-overwrite moves.
- Preserve sources on failure; include recovery paths if cleanup fails. Reject nonregular sources. Verify existing destinations and source bytes remain intact.

## 2. Organizer

- Add CLI regression tests in `packages/fmtools/rust/organize_files_rs/tests/` before changing `src/main.rs`.
- Validate category names/extensions and reject invalid explicit configurations before writes.
- Plan in deterministic order and reserve collision names during dry runs as well as execution.
- Keep hidden/system files, download/Office locks, symlinks, saved webpage pairs and recursive output trees out of the input set. Add repeatable exact-name/path exclusions.
- Use safe destination names for size mode on Windows. Report scan/operation errors with a failing exit code while continuing independent files.
- Offer a new exclusive `--report PATH` JSONL journal containing source and exact destination paths before/after operations. A failed journal write stops further changes.
- Expose Rust-specific organizer options through the Python CLI without silently falling back when those options are requested.

## 3. Rename

- Own changes within `packages/fmtools/rust/rename_files_rs/`.
- Test unsafe name fragments, preexisting temporary files, overlapping target names, dry runs and failed operations.
- Stage a batch in exclusively created directories, publish with no-overwrite moves, count finalized operations and recover staged files on failure.

## 4. Duplicate deletion

- Own changes within `packages/fmtools/rust/dupeforge-rs/`.
- Test stale/missing keepers, false hash matches, deletion failures and noninteractive previews.
- Validate worker counts, preserve scan/hash errors, use a local thread pool, recheck metadata and compare bytes before deletion, and count only successful removals.

## 5. Conversion

- Own changes within `packages/fmtools/rust/convert_media_rs/`.
- Test invalid numeric/format options, recursive duplicate basenames, existing outputs and filter construction.
- Preserve relative output paths, exclude nested output trees, convert into owned temporary directories, publish without overwriting, and return failure when conversions fail.

## 6. Integration and verification

- Add Rust formatting and workspace tests to `.github/workflows/ci.yml` on Windows and Ubuntu.
- Update `packages/fmtools/docs/USE_RUST_GUIDE.md` and package help for the verified behavior.
- Run `cargo fmt --all --check`, `cargo test --locked --workspace`, targeted Clippy checks, Python adapter/package tests and the native release build.
- Smoke-test rebuilt executables on temporary fixtures; leave all work uncommitted for review.
