# Utility Scripts Collection

Standalone Python utilities in `python/`. Each script has its own `--help`
output with full argument documentation.

## Scripts

- `python/clean_empty_dirs.py` — recursively find and remove empty directories
  (supports `--dry-run`, `--interactive`, `--min-depth`, `--include-hidden`).
- `python/convert_media.py` — convert between media formats
  (`gif`, `mp4`, `webm`, `avi`, `mov`) with optional speed/fps/quality changes
  and parallel workers. Requires `moviepy`.
- `python/delete_duplicates.py` — find duplicate files by size + SHA256/MD5/SHA1
  hash and optionally delete them (interactive or `--batch`).
- `python/file_stats.py` — produce size/type/age statistics for a directory;
  optional duplicate detection and JSON/CSV export.
- `python/organize_files.py` — sort files into sub-folders by type, date, or
  size. Supports `--dry-run`, `--move`, `--recursive`, custom category config.
- `python/rename.py` — sequentially rename files matching an extension with
  optional prefix/suffix/zero-padding. Uses temp names to avoid collisions.
- `python/smart_dedup.py` — wrapper that dispatches to either the Rust
  `dupeforge-rs.exe` (when present) or the Python implementation based
  on dataset size. Use `--force-python` / `--force-rust` to override.
- `python/speed.py` — change the playback speed of GIFs. Requires `moviepy`.
- `python/test.py` — **ad-hoc scratch helper** (despite the name, not a
  pytest module): converts `*.webm` files next to itself into 2x-speed GIFs.
- `python/test_tools.py` — verification harness that smoke-tests the other
  CLIs and checks for companion docs/executables.

## Quick start

```sh
python python/delete_duplicates.py /path/to/dir --dry-run
python python/rename.py --extension jpg --prefix photo_ --padding 4
python python/file_stats.py --directory . --export-json stats.json
```
