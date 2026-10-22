# Homebrew and Scoop Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Install the four native Rust file tools through Homebrew and Scoop, remove Media Catcher, and publish the repository publicly as requested.

**Architecture:** This repository serves as a custom Homebrew tap (`Formula/`) and Scoop bucket (`bucket/`). Homebrew builds a checksummed Rust source archive; Scoop installs a checksummed Windows ZIP with the four executables at its root. Native release tags use `toolkit-vVERSION`, separately from Python package releases. A release helper builds reproducible archives and generates both installers from their actual SHA-256 hashes.

**Tech Stack:** Python 3.11 standard library, Rust/Cargo, Homebrew Ruby formula, Scoop JSON manifest, GitHub Actions/CLI.

---

### Task 1: Remove Media Catcher

- Back up its source outside the repository and verify the archive.
- Remove `packages/media-catcher`, its active documentation, CI job, and ignore exceptions.
- Preserve historical archive and completed plan documents.

### Task 2: Add verified release packaging

**Files:** `tools/native_release.py`, `tools/tests/test_native_release.py`.

- Test archive contents, executable permissions, reproducibility, missing inputs, immutable outputs, unsafe versions, and installer hashes before implementation.
- Validate the requested native release version against the Rust workspace.
- Package Windows/macOS/Linux binaries and a source archive containing the Rust workspace and lockfile.
- Generate a source-build Homebrew formula, a Windows x64 Scoop manifest, and `SHA256SUMS` from completed archives.
- Build Windows release binaries with a static CRT, then smoke-test extracted executables.

### Task 3: Add the release workflow and installer documentation

**Files:** `.github/workflows/native-release.yml`, `.github/workflows/publish.yml`, `.github/workflows/ci.yml`, `README.md`, `packages/fmtools/README.md`, `packages/fmtools/docs/INSTALL.md`, `docs/PACKAGE_MANAGERS.md`.

- Build all four supported targets with the locked workspace, package artifacts, and publish under `toolkit-vVERSION`.
- Publish assets before updating the default branch's formula and manifest; reject overwriting an existing release.
- Keep native releases from triggering PyPI uploads.
- Document explicit tap/bucket registration, all four commands, optional FFmpeg, upgrades, uninstalling, and the separate Python CLI.
- Add package-manager validation to CI and check generated manifests against real archives.

### Task 4: Publish and verify

- Review the complete diff and scan tracked files for credentials before changing visibility.
- Make the GitHub repository public using the user's explicit approval.
- Publish the verified source and Windows archives for the first native release, and push the installer definitions and package removal.
- Verify anonymous downloads, SHA-256 hashes, native executable smoke tests, and the actual Scoop install in an isolated root.
- Run Homebrew installation tests on macOS/Linux when a runner is available; report any runner limitation accurately.
