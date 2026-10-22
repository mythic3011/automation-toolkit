# Getting Started with fmtools

Welcome to fmtools! This guide will help you get started with the most common tasks.

## Your First Command

After installation, verify everything works:

```bash
fmtools --help
```

You should see a list of available commands.

---

## 5 Things to Try First

### 1. Find Duplicate Files (Safe Mode)

Let's find duplicates in your Downloads folder without deleting anything:

```bash
fmtools dedup ~/Downloads --dry-run
```

**What this does:**

- Scans your Downloads directory
- Finds files with identical content
- Shows what would be deleted
- **Doesn't actually delete anything** (--dry-run)

**Output:**

```
Analyzing directory: C:\Users\You\Downloads
Counting files... 1250 files found
Decision: Large dataset (1250 files) - Rust is 20-50x faster
Using Rust implementation for maximum performance

Scanning directory: C:\Users\You\Downloads
Grouping files by size...
Hashing files using sha256...
Found 15 groups of duplicate files

Duplicate group (hash: a3f5e8c2...)
  [KEEP] C:\Users\You\Downloads\photo1.jpg
  [DELETE] C:\Users\You\Downloads\photo1 (1).jpg
  [DELETE] C:\Users\You\Downloads\photo1-copy.jpg
```

**Next steps:**

- Review the output carefully
- If it looks good, run without `--dry-run` to actually delete duplicates
- Use `--batch` to skip confirmation prompts: `fmtools dedup ~/Downloads --batch --keep newest`

---

### 2. Organize Files by Type

Organize your messy Downloads folder:

```bash
fmtools organize --source ~/Downloads --mode type --dry-run
```

**What this does:**

- Groups files by extension (Documents, Images, Videos, etc.)
- Creates organized folders
- Shows what would be moved
- **Doesn't move anything** (--dry-run)

**Output:**

```
Organizing files from: C:\Users\You\Downloads
Mode: type
[DRY RUN] Would move photo1.jpg to Images/photo1.jpg
[DRY RUN] Would move document.pdf to Documents/document.pdf
[DRY RUN] Would move video.mp4 to Videos/video.mp4

Summary:
  Total files: 235
  Images: 87
  Documents: 45
  Videos: 12
  ...
```

**Next steps:**

- If satisfied, run with `--move` to actually move files
- Use `--dest` to specify a different destination folder
- Customize categories with a JSON file

---

### 3. Batch Rename Files

Rename all your vacation photos with a consistent pattern:

```bash
cd ~/Pictures/Vacation2024
fmtools rename --extension jpg --prefix "vacation_" --padding 4 --dry-run
```

**What this does:**

- Finds all .jpg files
- Renames them to: vacation_0001.jpg, vacation_0002.jpg, etc.
- Shows what would be renamed
- **Doesn't rename anything** (--dry-run)

**Output:**

```
Found 47 files to rename
[DRY RUN] Would rename: IMG_1234.jpg -> vacation_0001.jpg
[DRY RUN] Would rename: IMG_1235.jpg -> vacation_0002.jpg
[DRY RUN] Would rename: IMG_1236.jpg -> vacation_0003.jpg
...
```

**Next steps:**

- Remove `--dry-run` to actually rename
- Add `--suffix` for text before the extension
- Use `--start 100` to start numbering from 100

---

### 4. Get File Statistics

Analyze your system to see where space is being used:

```bash
fmtools stats --directory ~/Documents --duplicates
```

**What this does:**

- Scans all files in Documents
- Shows size breakdown by type
- Finds largest files
- Detects duplicates

**Output:**

```
File Statistics for: C:\Users\You\Documents

Total Files: 1,843
Total Size: 15.7 GB
Average Size: 8.9 MB

Size Distribution:
  < 1 MB:    1,234 files (12.3 MB)
  1-10 MB:     458 files (2.1 GB)
  10-100 MB:   127 files (6.8 GB)
  > 100 MB:     24 files (6.8 GB)

File Types:
  .pdf:  452 files (3.2 GB)
  .docx: 287 files (1.8 GB)
  .jpg:  734 files (4.1 GB)
  ...

Top 10 Largest Files:
  1. backup_2024.zip (2.1 GB)
  2. video_project.mp4 (1.3 GB)
  3. database.db (857 MB)
  ...

Duplicates:
  Found 23 groups of duplicates
  Wasted space: 438 MB
```

**Next steps:**

- Export to JSON: `--export-json report.json`
- Export to CSV: `--export-csv report.csv`
- Use the data to decide what to clean up

---

### 5. Create a Backup

Create a compressed backup of important files:

```bash
fmtools backup ~/Documents ~/Backups --compress gzip --keep 5
```

**What this does:**

- Backs up Documents to Backups folder
- Compresses with gzip
- Keeps only the 5 most recent backups
- Uses incremental backup (hardlinks for unchanged files)

**Output:**

```
Creating backup: C:\Backups\backup_Documents_20241014_143022.tar.gz
Source: C:\Users\You\Documents

Collecting files...
Found 1,843 files to backup

Compressing... [====================] 1843/1843

Backup completed: C:\Backups\backup_Documents_20241014_143022.tar.gz
  Files: 1,843
  Original size: 15.7 GB
  Archive size: 4.2 GB
  Compression ratio: 73.2%
```

**Next steps:**

- Schedule with cron (Linux) or Task Scheduler (Windows)
- Use `--exclude` patterns to skip certain files
- Try `--incremental` for faster subsequent backups

---

## Common Workflows

### Daily Downloads Cleanup

```bash
# Find and remove duplicates
fmtools dedup ~/Downloads --batch --keep newest --min-size 1024

# Organize remaining files
fmtools organize --source ~/Downloads --mode type --move

# Remove empty folders
fmtools clean --directory ~/Downloads
```

### Photo Organization

```bash
# Rename by date
fmtools organize --source ~/Pictures --mode date --move

# Remove duplicates
fmtools dedup ~/Pictures --batch --keep newest

# Compress images
fmtools compress --directory ~/Pictures --type image --quality 85 --recursive
```

### Project Backup

```bash
# Create incremental backup
fmtools backup ~/Projects ~/Backups/Projects \
  --incremental \
  --compress gzip \
  --exclude "*.pyc" \
  --exclude "node_modules" \
  --exclude ".git" \
  --keep 10
```

---

## Understanding Dry-Run Mode

**Always use `--dry-run` first!**

Most commands support `--dry-run` which shows what would happen without making changes:

```bash
# Safe - shows what would be deleted
fmtools dedup ~/folder --dry-run

# Dangerous - actually deletes files
fmtools dedup ~/folder --batch
```

---

## Configuration

View your current configuration:

```bash
fmtools config show
```

Change defaults:

```bash
# Use MD5 instead of SHA256 (faster)
fmtools config set defaults.dedup.algorithm md5

# Auto-use Rust for 500+ files instead of 1000+
fmtools config set rust.threshold 500

# Change default keep strategy
fmtools config set defaults.dedup.keep oldest
```

View a specific value:

```bash
fmtools config get defaults.dedup.algorithm
```

Reset to defaults:

```bash
fmtools config reset
```

---

## Performance Tips

### When to Use Rust vs Python

The tool automatically chooses, but you can force:

```bash
# Force Rust (10-50x faster for large datasets)
fmtools dedup ~/large_folder --force-rust

# Force Python (easier to debug, better for small datasets)
fmtools dedup ~/small_folder --force-python
```

**Rule of thumb:**

- < 100 files: Either is fine
- 100-1,000 files: Rust recommended
- 1,000+ files: **Always use Rust!**

See [USE_RUST_GUIDE.md](USE_RUST_GUIDE.md) for detailed performance comparisons.

---

## Getting Help

Every command has built-in help:

```bash
# General help
fmtools --help

# Command-specific help
fmtools dedup --help
fmtools organize --help
fmtools backup --help
```

Enable verbose output for debugging:

```bash
fmtools --verbose dedup ~/folder
```

Check log files:

```bash
# Windows
type %APPDATA%\fmtools\dedup.log

# Linux/macOS
cat ~/.fmtools/dedup.log
```

---

## Next Steps

Now that you're familiar with the basics:

1. **Read the full docs**: [README.md](README.md)
2. **See real examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
3. **Optimize performance**: [USE_RUST_GUIDE.md](USE_RUST_GUIDE.md)
4. **Explore all commands**: `fmtools --help`

---

## Quick Reference

### All Commands

| Command    | Purpose                    | Example                                             |
| ---------- | -------------------------- | --------------------------------------------------- |
| `dedup`    | Find & remove duplicates   | `fmtools dedup ~/folder --batch`                    |
| `rename`   | Batch rename files         | `fmtools rename --prefix photo_ --padding 3`        |
| `organize` | Organize by type/date/size | `fmtools organize --source ~/Downloads --mode type` |
| `convert`  | Convert media formats      | `fmtools convert --from mp4 --to gif`               |
| `stats`    | Generate file statistics   | `fmtools stats --directory ~/Documents`             |
| `clean`    | Remove empty directories   | `fmtools clean --directory ~/folder`                |
| `speed`    | Adjust GIF playback speed  | `fmtools speed --speed 2.0`                         |
| `hash`     | Generate/verify checksums  | `fmtools hash --directory ~/folder -r`              |
| `backup`   | Create backups             | `fmtools backup ~/source ~/dest --compress gzip`    |
| `find`     | Advanced file finding      | `fmtools find --larger 100MB --older 30d`           |
| `compress` | Compress images/archives   | `fmtools compress --type image --quality 85`        |
| `config`   | Manage configuration       | `fmtools config show`                               |

### Global Flags

- `--verbose`: Show detailed output
- `--log-file FILE`: Log to specific file
- `--config FILE`: Use custom config file

### Common Flags

- `--dry-run`: Preview without making changes
- `--batch`: Auto-confirm (no prompts)
- `--recursive`: Process subdirectories
- `--force-rust`: Use Rust implementation
- `--force-python`: Use Python implementation

---

**Ready to optimize your file management! 🚀**
