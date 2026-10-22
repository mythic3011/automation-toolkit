# Documentation Index

Master hub for project-wide documentation. Each package under `packages/` also
ships its own README and `docs/` directory — start there for
package-specific guidance.

## Master Documentation

- [Getting Started](GETTING_STARTED.md) — quick start for the entire project
- [Troubleshooting](TROUBLESHOOTING.md) — common issues and solutions
- [Changelog](CHANGELOG.md) — version history
- [Homebrew and Scoop](../PACKAGE_MANAGERS.md) — install native tools and maintain releases

Older one-off status/summary notes (restructure plans, completion reports,
etc.) live alongside this index but are kept for historical reference only.
They are candidates to be moved into `docs/master/archive/` in a future
cleanup pass — see the top-level `README.md` for context.

## Package Documentation

### fmtools — File Management Tools

Python CLI with optional Rust-accelerated implementations.

- [README](../../packages/fmtools/README.md)
- [Install](../../packages/fmtools/docs/INSTALL.md)
- [Quick Start](../../packages/fmtools/docs/QUICK_START.md)
- [Command Reference](../../packages/fmtools/docs/COMMAND_REFERENCE.md)
- [Usage Examples](../../packages/fmtools/docs/USAGE_EXAMPLES.md)
- [Rust Guide](../../packages/fmtools/docs/USE_RUST_GUIDE.md)

### scripts — Utility Scripts

Standalone automation scripts.

- [README](../../packages/scripts/README.md)
- [Python scripts](../../packages/scripts/python/)

## Project Layout

```
automation-toolkit/
├── packages/          # All sub-projects
│   ├── fmtools/
│   └── scripts/
├── docs/
│   └── master/        # This directory (project-wide docs)
├── Formula/           # Homebrew formula
├── bucket/            # Scoop manifest
├── tools/             # Release packaging and archived restructure helpers
├── README.md
├── LICENSE
└── .gitignore
```

## Quick Links

- [Main README](../../README.md)
- [License](../../LICENSE)
