# Repository Reliability Implementation Plan

> Historical plan: this work preceded the removal of Media Catcher. Its package and JavaScript build instructions below are retained only as a record; use the root README for the current packages.

> **For Claude:** Use the superpowers debugging, test-driven-development, parallel-agent, and verification workflows while implementing these tasks.

**Goal:** Make fresh checkouts and installed packages usable, and add repeatable validation for the monorepo.

**Architecture:** Preserve the three packages remaining in this repository and their command interfaces. Linux Secure Server Setup is maintained in a separate repository. Repair packaging and build boundaries, isolate configuration state, and run local tests without touching live infrastructure.

**Tech Stack:** Python/setuptools/pytest, JavaScript/Node.js/ESLint, Rust/Cargo, Bash, GitHub Actions.

## Task 1: Make fmtools commands self-contained

- Inspect `packages/fmtools/src/fmtools/` adapters and `packages/fmtools/scripts/` implementations.
- Add failing tests that exercise commands using only installed package contents, outside the source checkout.
- Package the required implementation modules and use relative imports rather than modifying the process import path.
- Preserve script entry points where practical, remove duplicate package metadata, and verify wheel installation and command behavior.

## Task 2: Restore reproducible Media Catcher builds

- Inspect the locally ignored `packages/media-catcher/build/build.js` and reproduce build/lint failures from tracked files.
- Make build source visible to Git, preserve production/development outputs, and track a dependency lockfile.
- Add meaningful build smoke tests that parse and execute the bundled userscript with a small browser fixture.
- Run package tests, both build modes, and lint; fix defects revealed by those checks.

## Task 3: Isolate fmtools configuration defaults

- Add failing tests to `packages/fmtools/tests/test_config.py` for independent instances, reset behavior, and partially loaded configurations.
- Deep-copy mutable defaults in `packages/fmtools/src/fmtools/config.py`.
- Run the regression tests using an isolated config directory.

## Task 4: Add CI and repair release paths

- Add `.github/workflows/ci.yml` with Python tests and packaging checks, Media Catcher tests/build/lint, and safe syntax checks for tracked shell scripts.
- Review `.github/workflows/publish.yml` against actual Cargo binary names and packaged binary search paths; repair verified path defects.
- Do not execute provisioning, security hardening, or live service scripts.

## Task 5: Integrate and document

- Update root ignore rules so build source and the Media Catcher lockfile are tracked.
- Define shell/JavaScript line endings so Windows checkouts preserve executable source and lint behavior.
- Correct root README commands and prerequisites to match verified behavior; document how to run the checks.
- Review the complete diff, run the combined checks, and report the results and any unverified platform behavior.

## Repository scope update

`packages/linux-automation/` has been removed from this repository because Linux Secure Server Setup is maintained elsewhere. Its files were archived outside the workspace before removal. Root documentation and CI now describe only the three packages maintained here.
