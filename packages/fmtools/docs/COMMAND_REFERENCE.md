# Command reference

The installed CLI is the supported entry point. Run `fmtools COMMAND --help` for the current options and examples for a specific command. To see global options, run `fmtools --help`.

| Command | Purpose |
| --- | --- |
| `dedup` | Find duplicate files by content and optionally remove them. |
| `rename` | Rename files with numbering, prefixes, and suffixes. |
| `organize` | Organize files by type, date, or size. |
| `convert` | Convert media files between supported formats. |
| `stats` | Summarize directory contents and optionally export reports. |
| `clean` | Find and remove empty directories. |
| `speed` | Adjust GIF playback speed. |
| `hash` | Generate or verify file checksums. |
| `backup` | Create directory backups, optionally incrementally or compressed. |
| `find` | Search files using name, type, size, and age filters. |
| `compress` | Compress images or create archives. |
| `config` | Show, get, set, or reset configuration values. |

Examples:

```sh
fmtools dedup --help
fmtools rename --help
fmtools organize --help
fmtools config --help
```

Global options such as `--config`, `--verbose`, and `--log-file` go before the command:

```sh
fmtools --config ./settings.yaml --verbose dedup ./Downloads --dry-run
```

For a guided set of common commands, see the [quick start](QUICK_START.md). The [package README](../README.md) covers installation, configuration, and optional Rust executables.
