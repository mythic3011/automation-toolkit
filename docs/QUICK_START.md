# Quick Start Guide

Fast reference for common tasks with Automation Toolkit. For the current package CLI, see the [fmtools quick start](../packages/fmtools/docs/QUICK_START.md). The examples below use the standalone scripts.

## Installation

```bash
# Clone repository
git clone https://github.com/mythic3011/automation-toolkit.git
cd automation-toolkit/packages/fmtools

# Install Python dependencies (using uv - recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt

# Run the legacy script examples below from the scripts directory
cd scripts
```

## Common Tasks

### 1. Find & Remove Duplicate Files

**Python:**

```bash
# Dry run first (recommended)
python delete_duplicates.py ~/Downloads --dry-run

# Remove duplicates, keep newest
python delete_duplicates.py ~/Downloads --batch --keep newest

# Interactive mode
python delete_duplicates.py ~/Downloads
```

**Rust (much faster):**

```bash
# Windows
.\exe\dupeforge-rs.exe ~/Downloads --batch --keep newest

# Linux/Mac
./exe/dupeforge-rs ~/Downloads --batch --keep newest
```

### 2. Batch Rename Files

**Rename all JPG files to photo_001.jpg, photo_002.jpg, etc:**

```bash
python rename.py --extension jpg --prefix photo_ --padding 3
```

**Rename with suffix:**

```bash
python rename.py --extension txt --suffix _backup --start 100
# Result: 100_backup.txt, 101_backup.txt, ...
```

### 3. Organize Files

**By file type:**

```bash
python organize_files.py --source ~/Downloads --mode type --move
```

**By date:**

```bash
python organize_files.py --source ./Photos --mode date-modified
```

**By size:**

```bash
python organize_files.py --source ./Files --mode size --dry-run
```

### 4. Convert Media Files

**WebM to GIF with double speed:**

```bash
python convert_media.py \
  --input-dir ./videos \
  --output-dir ./gifs \
  --from webm \
  --to gif \
  --speed 2.0
```

**MP4 to GIF with custom FPS:**

```bash
python convert_media.py \
  --input-dir ./clips \
  --output-dir ./animations \
  --from mp4 \
  --to gif \
  --fps 15 \
  --speed 1.5
```

### 5. Speed Up GIFs

```bash
# Double speed
python speed.py --input-dir ./gifs --speed 2.0

# Triple speed with custom output
python speed.py \
  --input-dir ./input \
  --output-dir ./output \
  --speed 3.0 \
  --fps 20
```

### 6. Clean Empty Directories

```bash
# Dry run first
python clean_empty_dirs.py --directory ~/Downloads --dry-run

# Actually remove them
python clean_empty_dirs.py --directory ~/Downloads

# Interactive mode
python clean_empty_dirs.py --directory ~/Projects --interactive
```

### 7. Analyze Files

```bash
# Basic stats
python file_stats.py --directory ~/Documents

# With duplicate detection
python file_stats.py --directory ~/Downloads --duplicates

# Export results
python file_stats.py \
  --directory ~/Data \
  --duplicates \
  --export-json stats.json \
  --export-csv file_types.csv
```

## Complete Workflows

### Clean Up Downloads Folder

```bash
# 1. See what's there
python file_stats.py --directory ~/Downloads --duplicates

# 2. Remove duplicates (dry run)
python delete_duplicates.py ~/Downloads --dry-run --keep newest

# 3. Actually remove duplicates
python delete_duplicates.py ~/Downloads --batch --keep newest

# 4. Organize by type
python organize_files.py --source ~/Downloads --mode type --move

# 5. Clean up empty folders
python clean_empty_dirs.py --directory ~/Downloads
```

### Process Video Collection

```bash
# 1. Convert all videos to GIFs
python convert_media.py \
  --input-dir ./videos \
  --output-dir ./gifs \
  --from mp4 \
  --to gif \
  --speed 2.0 \
  --fps 15

# 2. Rename sequentially
python rename.py \
  --directory ./gifs \
  --extension gif \
  --prefix clip_ \
  --padding 4

# 3. Organize by size
python organize_files.py \
  --source ./gifs \
  --mode size
```

### Photo Organization

```bash
# 1. Organize by date
python organize_files.py \
  --source ~/Photos \
  --mode date-modified \
  --move

# 2. Remove duplicates in each folder
for dir in ~/Photos/*/; do
  python delete_duplicates.py "$dir" --batch --keep newest
done

# 3. Generate report
python file_stats.py \
  --directory ~/Photos \
  --export-json photo_stats.json
```

## Tips & Tricks

### Always Use Dry-Run First

```bash
# Preview changes before committing
python delete_duplicates.py . --dry-run
python organize_files.py --source . --dry-run
python rename.py --extension jpg --prefix photo_ --dry-run
```

### Use Rust for Large Operations

For directories with thousands of files, use Rust versions for 10-50x speedup:

```bash
# Python: ~45 seconds
python delete_duplicates.py ./large_folder --batch

# Rust: ~2 seconds
.\exe\dupeforge-rs.exe ./large_folder --batch
```

### Combine Tools

```bash
# Clean up, organize, and analyze in one go
python delete_duplicates.py ~/Downloads --batch && \
python organize_files.py --source ~/Downloads --mode type --move && \
python clean_empty_dirs.py --directory ~/Downloads && \
python file_stats.py --directory ~/Downloads --export-json summary.json
```

### Custom Categories

Create `my_categories.json`:

```json
{
  "categories": {
    "Work Documents": [".docx", ".xlsx", ".pptx"],
    "Personal Files": [".jpg", ".mp4", ".pdf"],
    "Code Projects": [".py", ".js", ".rs"]
  }
}
```

Use it:

```bash
python organize_files.py \
  --source ~/Files \
  --mode type \
  --config my_categories.json
```

### Get Help

Every tool has detailed help:

```bash
python delete_duplicates.py --help
python rename.py --help
python organize_files.py --help
# etc.
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'tqdm'"

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### "ffmpeg not found" (for media conversion)

**Windows:**

1. Download from https://ffmpeg.org/download.html
2. Extract and add to PATH

**Linux:**

```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

**macOS:**

```bash
brew install ffmpeg
```

### Permission Errors

Run with appropriate permissions:

```bash
# Windows (PowerShell as Admin)
# Linux/Mac
sudo python delete_duplicates.py /protected/folder
```

### Rust Tools Not Running (Linux/Mac)

Make executables executable:

```bash
chmod +x exe/dupeforge-rs
chmod +x exe/rename_files
chmod +x exe/organize_files
chmod +x exe/convert_media
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [CHANGELOG.md](CHANGELOG.md) for version history
- Explore [example_categories.json](example_categories.json) for custom organization
- Join discussions and report issues on GitHub

## Support

- GitHub Issues: Report bugs or request features
- Documentation: See README.md for comprehensive guide
- Examples: Check the README for more usage examples

Happy organizing! 🚀
