# Usage Examples

Real-world examples for common scenarios using Automation Toolkit.

## Scenario 1: Clean Up Your Downloads Folder

You have 5GB of files in Downloads with many duplicates and no organization.

**Step 1: Analyze the situation**

```bash
python file_stats.py --directory ~/Downloads --duplicates
```

**Output:**

```
FILE STATISTICS REPORT
=====================
Total files: 3,542
Total directories: 87
Total size: 5.23 GB
Average file size: 1.51 MB

Size Distribution:
  Tiny: 842 (23.8%)
  Small: 1,234 (34.8%)
  Medium: 987 (27.9%)
  Large: 421 (11.9%)
  Huge: 58 (1.6%)

Duplicate Analysis:
  Duplicate groups: 234
  Duplicate files: 567
  Wasted space: 1.2 GB
```

**Step 2: Remove duplicates (dry-run first)**

```bash
python delete_duplicates.py ~/Downloads --dry-run --keep newest
```

**Step 3: Actually remove them**

```bash
# Use Rust for 25x speed boost!
.\exe\dupeforge-rs.exe ~/Downloads --batch --keep newest
```

**Output:**

```
Starting duplicate file scan in: C:\Users\YourName\Downloads
Algorithm: sha256, Keep mode: newest, Min size: 0 bytes
Found 3542 files
Found 1156 files with matching sizes
[████████████████████████████] 1156/1156 (0:00:02)
Hashing complete

============================================================
Found 234 groups of duplicates
Total duplicate files: 567
Potential space savings: 1.2 GB
============================================================

Proceed with deletion? (y/n): y

Summary:
Files deleted: 567
Space freed: 1.2 GB
```

**Step 4: Organize by type**

```bash
# Use Rust for 20x speed boost!
.\exe\organize_files.exe --source ~/Downloads --mode type --move
```

**Output:**

```
Organizing files in: C:\Users\YourName\Downloads
Mode: type
Action: move
Found 2975 files to organize
[████████████████████████████] 15/15 categories

Summary:
Files organized: 2975
Files skipped: 0
Files with errors: 0
```

**Step 5: Clean up empty folders**

```bash
python clean_empty_dirs.py --directory ~/Downloads
```

**Result:** Clean, organized Downloads folder with 1.2 GB of space freed!

---

## Scenario 2: Organize 10 Years of Photos

You have 50,000 photos scattered across multiple folders.

**Step 1: Centralize first**

```bash
# Move all photos to one location
mkdir ~/AllPhotos
find ~/Pictures -name "*.jpg" -o -name "*.png" | xargs -I {} mv {} ~/AllPhotos/
```

**Step 2: Remove duplicates**

```bash
# Rust version handles 50k files easily
.\exe\dupeforge-rs.exe ~/AllPhotos --algorithm md5 --min-size 10000 --batch --keep newest
```

**Why MD5?** Faster than SHA256, and collision risk is negligible for personal files.  
**Why min-size?** Skip tiny thumbnails.

**Step 3: Organize by date**

```bash
# Creates folders like 2015-01, 2015-02, etc.
.\exe\organize_files.exe --source ~/AllPhotos --dest ~/PhotosByDate --mode date-modified --move
```

**Step 4: Generate statistics**

```bash
python file_stats.py --directory ~/PhotosByDate --export-json photo_report.json
```

**Step 5: Find the largest files (for archiving)**

```bash
python file_stats.py --directory ~/PhotosByDate
# Check "Top 10 Largest Files" section
```

**Result:** 50,000 photos organized by year-month, duplicates removed!

---

## Scenario 3: Process Video Collection for Social Media

You have 100 MP4 videos that need to be converted to GIFs for social media.

**Step 1: Convert to GIF with speed-up**

```bash
python convert_media.py \
  --input-dir ./Videos \
  --output-dir ./Gifs \
  --from mp4 \
  --to gif \
  --speed 2.0 \
  --fps 15 \
  --workers 4
```

**Output:**

```
Converting mp4 files to gif
Input directory: C:\Videos
Output directory: C:\Gifs
Speed factor: 2.0x
Output FPS: 15
[████████████████████████████] 100/100 (0:05:23)

Conversion Summary:
Successfully converted: 98
Failed: 2
Total: 100
```

**Step 2: Rename sequentially**

```bash
python rename.py \
  --directory ./Gifs \
  --extension gif \
  --prefix social_ \
  --padding 3 \
  --start 1
```

**Result:** social_001.gif through social_098.gif

**Step 3: Organize by size**

```bash
# Separate small/medium/large GIFs
python organize_files.py --source ./Gifs --mode size
```

**Result:** Videos converted, renamed, and organized by size for different platforms!

---

## Scenario 4: Cleanup After Project

Your project folder has accumulated build artifacts, temp files, and duplicates.

**Step 1: Remove obvious duplicates**

```bash
.\exe\dupeforge-rs.exe ~/Project --batch --keep first
```

**Why "first"?** Keep original files, remove copies.

**Step 2: Organize source files**

```bash
# Use custom categories
cat > project_categories.json << EOF
{
  "categories": {
    "Source Code": [".py", ".js", ".ts", ".java", ".cpp", ".h"],
    "Configuration": [".json", ".yaml", ".toml", ".ini", ".env"],
    "Documentation": [".md", ".txt", ".pdf", ".docx"],
    "Assets": [".png", ".jpg", ".svg", ".gif"],
    "Data": [".csv", ".xlsx", ".db", ".sqlite"]
  }
}
EOF

python organize_files.py \
  --source ~/Project \
  --mode type \
  --config project_categories.json \
  --recursive
```

**Step 3: Clean empty directories**

```bash
python clean_empty_dirs.py --directory ~/Project --min-depth 1
```

**Step 4: Generate project report**

```bash
python file_stats.py \
  --directory ~/Project \
  --export-json project_stats.json \
  --export-csv file_breakdown.csv
```

**Result:** Clean, organized project with detailed statistics!

---

## Scenario 5: Prepare Files for Backup

You want to backup your important files but need to reduce size first.

**Step 1: Find duplicates across all folders**

```bash
.\exe\dupeforge-rs.exe ~/Documents --batch --keep newest --dry-run
# Review what would be deleted, then run without --dry-run
.\exe\dupeforge-rs.exe ~/Documents --batch --keep newest
```

**Step 2: Organize by type for easier backup**

```bash
python organize_files.py \
  --source ~/Documents \
  --dest ~/DocumentsOrganized \
  --mode type \
  --recursive \
  --move
```

**Step 3: Generate size report**

```bash
python file_stats.py \
  --directory ~/DocumentsOrganized \
  --export-json backup_manifest.json
```

**Step 4: Identify large files to exclude**

```bash
# Check the JSON for files > 100MB
# Move them to a separate "LargeFiles" folder for cloud storage
```

**Result:** Optimized backup with no duplicates and organized structure!

---

## Scenario 6: Batch Processing Animated GIFs

You have 500 GIFs that are too slow and need renaming.

**Step 1: Speed them up**

```bash
# Use Rust for 3x faster processing, but Python is fine too
python speed.py \
  --input-dir ./SlowGifs \
  --output-dir ./FastGifs \
  --speed 2.5 \
  --fps 20 \
  --workers 4
```

**Step 2: Rename with descriptive pattern**

```bash
python rename.py \
  --directory ./FastGifs \
  --extension gif \
  --prefix animation_ \
  --padding 4 \
  --start 1000
```

**Result:** animation_1000.gif through animation_1500.gif, all at 2.5x speed!

---

## Scenario 7: Manage Music Collection

You have 20,000 MP3 files with many duplicates from different sources.

**Step 1: Find duplicates**

```bash
# Use MD5 for speed with large collections
.\exe\dupeforge-rs.exe ~/Music --algorithm md5 --batch --keep newest
```

**Step 2: Organize by artist/album (manual) or by date**

```bash
python organize_files.py \
  --source ~/Music \
  --mode date-modified \
  --recursive
```

**Step 3: Generate collection statistics**

```bash
python file_stats.py \
  --directory ~/Music \
  --export-csv music_stats.csv
```

**Result:** Deduplicated music collection with statistics!

---

## Advanced Workflows

### Automated Cleanup Script (Bash/PowerShell)

**cleanup.sh:**

```bash
#!/bin/bash
FOLDER="$1"

echo "Starting cleanup of $FOLDER"

# Step 1: Stats
python file_stats.py --directory "$FOLDER" --duplicates

# Step 2: Remove duplicates
./exe/dupeforge-rs "$FOLDER" --batch --keep newest

# Step 3: Organize
./exe/organize_files --source "$FOLDER" --mode type --move

# Step 4: Clean empty dirs
python clean_empty_dirs.py --directory "$FOLDER"

# Step 5: Final report
python file_stats.py --directory "$FOLDER" --export-json "${FOLDER}_report.json"

echo "Cleanup complete! Check ${FOLDER}_report.json for details."
```

**Usage:**

```bash
chmod +x cleanup.sh
./cleanup.sh ~/Downloads
```

### Weekly Maintenance (Cron/Task Scheduler)

**weekly_maintenance.sh:**

```bash
#!/bin/bash
# Run every Sunday at 2 AM

# Clean downloads
./exe/dupeforge-rs ~/Downloads --batch --keep newest --min-size 1000
python organize_files.py --source ~/Downloads --mode type --move
python clean_empty_dirs.py --directory ~/Downloads

# Generate reports
python file_stats.py --directory ~/Downloads --export-json ~/Reports/downloads_$(date +%Y%m%d).json
```

**Add to crontab:**

```bash
0 2 * * 0 /path/to/weekly_maintenance.sh
```

---

## Pro Tips

### 1. Combine Tools with Pipes

```bash
# Find duplicates and export list
python delete_duplicates.py ~/Folder --dry-run | grep "DELETE" > duplicates.txt
```

### 2. Use Rust for Large Operations

```bash
# Python: ~45 seconds
python delete_duplicates.py ./BigFolder

# Rust: ~2 seconds
.\exe\dupeforge-rs.exe ./BigFolder
```

### 3. Chain Operations

```bash
python delete_duplicates.py ~/Folder --batch && \
python organize_files.py --source ~/Folder --mode type --move && \
python clean_empty_dirs.py --directory ~/Folder && \
echo "All done!"
```

### 4. Test First

```bash
# Always dry-run first!
python delete_duplicates.py ~/Important --dry-run
python organize_files.py --source ~/Important --dry-run
```

### 5. Use Custom Categories

Create your own organization rules:

```json
{
  "categories": {
    "Work": [".docx", ".xlsx", ".pptx"],
    "Personal": [".jpg", ".mp4"],
    "Archives": [".zip", ".rar"]
  }
}
```

---

## Troubleshooting Common Issues

### "Too many open files" error

Reduce workers:

```bash
python speed.py --workers 2
```

### Out of memory

Process in batches or use Rust version:

```bash
.\exe\dupeforge-rs.exe ~/BigFolder
```

### Permission denied

Run with elevated privileges:

```bash
sudo python delete_duplicates.py /protected/folder
```

---

## Questions?

See:

- [README.md](README.md) for full documentation
- [QUICK_START.md](QUICK_START.md) for quick reference
- [CHANGELOG.md](CHANGELOG.md) for version history

Happy organizing! 🎉
