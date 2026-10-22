# Automation Toolkit

Automation tools for file management, browser media capture, and standalone utilities. The three packages are independent: install only the tools you need. Linux Secure Server Setup is maintained in a separate repository.

```sh
git clone https://github.com/mythic3011/automation-toolkit.git
cd automation-toolkit
```

| Package | Purpose | Requirements |
| --- | --- | --- |
| [fmtools](packages/fmtools/) | Python CLI for deduplication, organization, renaming, checksums, and backups; optional Rust tools | Python 3.8+ |
| [Media Catcher](packages/media-catcher/) | Tampermonkey userscript for Panopto JSON and Zoom VTT transcripts | Node.js 18+ to build; a browser with Tampermonkey to use |
| [Standalone scripts](packages/scripts/) | Individual Python utilities | Python 3.8+ and each script's dependencies |

## File management

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

## Media Catcher

```sh
cd packages/media-catcher
npm ci
npm run build
```

Install the generated `dist/media-catcher.user.js` or `dist/media-catcher.min.user.js` through Tampermonkey. Build output is generated locally and is not checked into Git.

For development, `npm run build:dev` generates `dist/media-catcher.dev.user.js`, and `npm run watch` rebuilds when source files change. See the [package README](packages/media-catcher/README.md) and [build guide](packages/media-catcher/docs/BUILD_SYSTEM.md).

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

Run Media Catcher checks from its package directory:

```sh
npm ci
npm test
npm run lint:all
npm run build
npm run build:dev
```

Check shell syntax from the repository root using Bash:

```bash
while IFS= read -r -d '' script; do
  bash -n "$script" || exit 1
done < <(git ls-files -z -- '*.sh')
```

The root [CI workflow](.github/workflows/ci.yml) runs Python tests, a wheel installation check, Media Catcher tests/builds/lint, and shell syntax checks for tracked shell scripts.

## Repository layout

```text
packages/
  fmtools/             Python package, Rust workspace, tests, and CLI docs
  media-catcher/       Userscript source, build tooling, and tests
  scripts/python/     Standalone Python utilities
docs/                  Existing guides and historical project notes
tools/archive/         Historical repository restructuring helpers
.github/workflows/     CI and PyPI release workflows
```

Package READMEs and command help describe the current entry points. Older guides under `docs/` may reference paths from before the monorepo restructure.

Licensed under [MIT](LICENSE).
