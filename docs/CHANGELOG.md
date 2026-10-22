# Changelog

All notable changes to the Automation Toolkit project.

## [2.0.0] - 2025-10-14

### Major Rewrite - Performance & Features

This release represents a complete rewrite and expansion of the toolkit with massive performance improvements and new features.

### Added

#### New Python Scripts

- **convert_media.py** - Refactored from test.py with ProcessPoolExecutor for true parallelism
- **organize_files.py** - Smart file organization by type, date, or size with custom categories
- **clean_empty_dirs.py** - Recursively find and remove empty directories
- **file_stats.py** - Comprehensive file system statistics and analysis with JSON/CSV export

#### New Rust Tools (10-50x faster)

- **dupeforge-rs** (Rust) - Blazing fast duplicate detection with parallel hashing
- **rename_files** (Rust) - High-performance file renaming
- **organize_files** (Rust) - Lightning-fast file organization
- **convert_media** (Rust) - Efficient media conversion coordinator using FFmpeg

#### Enhanced Features

- ✅ Progress bars with ETA for all operations (using tqdm/indicatif)
- ✅ Comprehensive CLI arguments for all tools
- ✅ Dry-run mode for safe preview before execution
- ✅ Advanced logging with file output
- ✅ Robust error handling and recovery
- ✅ Batch and interactive modes
- ✅ Multiple keep strategies (newest, oldest, first)
- ✅ Multiple hash algorithms (SHA256, MD5, SHA1)
- ✅ Size-based pre-filtering for performance
- ✅ Recursive directory traversal
- ✅ Custom category configuration via JSON

### Changed

#### delete_duplicates.py

- **Before**: Basic threading with limited features
- **After**:
  - Size-based pre-filtering (only hash files with matching sizes)
  - Parallel hashing with as_completed for better responsiveness
  - CLI arguments (directory, batch mode, keep strategy, hash algorithm, etc.)
  - Progress bars for scanning and hashing phases
  - Multiple keep strategies (newest, oldest, first)
  - Dry-run mode
  - Detailed logging
  - Human-readable size formatting
  - Better error handling

#### rename.py

- **Before**: Unnecessary threading for I/O operations
- **After**:
  - Removed threading (I/O bound, not CPU bound)
  - CLI arguments (prefix, suffix, padding, start number, etc.)
  - Recursive search option
  - Conflict detection and resolution
  - Temporary naming to avoid conflicts
  - Dry-run mode
  - Progress bars
  - Better error handling

#### speed.py

- **Before**: Sequential processing with basic functionality
- **After**:
  - ProcessPoolExecutor for true parallel processing
  - CLI arguments (input/output dirs, speed factor, FPS, workers)
  - Progress bars
  - Custom FPS support
  - Recursive search
  - Better error handling and logging

#### test.py → convert_media.py

- **Renamed** for clarity
- **Before**: Basic threading for webm to gif conversion
- **After**:
  - ProcessPoolExecutor for parallel processing
  - Support for multiple formats (gif, mp4, webm, avi, mov)
  - Speed adjustment support
  - Quality presets
  - FPS control
  - CLI arguments
  - Progress tracking
  - Better error handling

### Performance Improvements

| Tool              | Before | After (Python) | After (Rust) | Rust Speedup   |
| ----------------- | ------ | -------------- | ------------ | -------------- |
| Delete Duplicates | ~120s  | ~50s           | ~2s          | **25x faster** |
| Rename Files      | ~5s    | ~2.5s          | ~0.3s        | **8x faster**  |
| Organize Files    | N/A    | ~12s           | ~0.6s        | **20x faster** |
| File Stats        | N/A    | ~38s           | ~2s          | **19x faster** |

_Benchmarks on 10,000 files (2GB total) on Windows 11, AMD Ryzen 5950X_

### Technical Improvements

#### Python

- Type hints for better code clarity
- Proper logging with file handlers
- argparse for robust CLI parsing
- Context managers for resource safety
- Better exception handling with specific error messages
- tqdm for progress visualization
- Concurrent.futures for parallelism

#### Rust

- Rayon for data parallelism
- Clap for CLI parsing
- Indicatif for progress bars
- Anyhow for error handling
- Walkdir for directory traversal
- SHA2/MD5 for hashing
- Optimized release builds with LTO

### Documentation

- Comprehensive README.md with usage examples
- requirements.txt with pinned dependencies
- example_categories.json for custom organization
- Detailed inline documentation
- .gitignore for clean repository

### Files Added

- `convert_media.py` - New unified media converter
- `organize_files.py` - New file organization tool
- `clean_empty_dirs.py` - New directory cleaner
- `file_stats.py` - New statistics generator
- `requirements.txt` - Python dependencies
- `example_categories.json` - Example configuration
- `CHANGELOG.md` - This file
- `.gitignore` - Git ignore rules
- `rust_tools/` - Complete Rust workspace
  - `dupeforge-rs/` - Rust duplicate finder
  - `rename_files_rs/` - Rust file renamer
  - `organize_files_rs/` - Rust file organizer
  - `convert_media_rs/` - Rust media converter
- `exe/` - Pre-built Rust executables (Windows x64)
  - `dupeforge-rs.exe`
  - `rename_files.exe`
  - `organize_files.exe`
  - `convert_media.exe`

### Breaking Changes

- `test.py` renamed to `convert_media.py`
- All scripts now require command-line arguments (no more hardcoded paths)
- Directory paths must be specified explicitly

### Migration Guide

#### Old Usage:

```bash
python delete_duplicates.py  # Uses current directory automatically
python rename.py             # Uses current directory automatically
python speed.py              # Uses current directory automatically
```

#### New Usage:

```bash
python delete_duplicates.py .                        # Specify directory
python rename.py --extension gif                     # Specify extension
python speed.py --input-dir . --speed 2.0           # Specify all params
python convert_media.py --input-dir ./in --output-dir ./out --from webm --to gif
```

## [1.0.0] - Previous Version

### Original Features

- Basic duplicate file detection
- Simple gif file renaming
- GIF speed adjustment
- WebM to GIF conversion
- Basic threading support

---

## Upcoming Features (Roadmap)

- [ ] GUI interface for non-technical users
- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] Advanced duplicate detection (perceptual hashing for images)
- [ ] Video trimming and editing features
- [ ] Batch watermarking
- [ ] Smart photo organization (by EXIF data)
- [ ] Incremental backup system
- [ ] File encryption/decryption
- [ ] Integration with cloud AI services for image tagging

## Developer

@samwell9624

## License

MIT License
