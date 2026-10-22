# fmtools Command Reference Card

Quick reference for all fmtools commands. For detailed help: `fmtools COMMAND --help`

---

## Global Options

```bash
fmtools [OPTIONS] COMMAND [ARGS]

--verbose, -v         Enable verbose output
--log-file FILE       Log to specified file
--config FILE         Use custom config file
--version            Show version
--help               Show help
```

---

## Commands

### 📦 dedup - Find & Remove Duplicates

```bash
fmtools dedup [DIR] [OPTIONS]

Examples:
  fmtools dedup ~/Downloads --dry-run
  fmtools dedup ~/folder --batch --keep newest --min-size 1024
  fmtools dedup . --algorithm md5 --force-rust

Options:
  --batch              Auto-delete without prompts
  --keep {newest|oldest|first}
  --algorithm {sha256|md5|sha1}
  --min-size BYTES     Skip files smaller than X
  --workers N          Number of parallel workers
  --dry-run            Preview only
  --force-python       Use Python version
  --force-rust         Use Rust version (faster)
```

---

### ✏️ rename - Batch Rename Files

```bash
fmtools rename [OPTIONS]

Examples:
  fmtools rename --extension jpg --prefix "photo_" --padding 4
  fmtools rename -d ~/folder --suffix "_backup" --start 100
  fmtools rename --prefix "vacation_" -r --dry-run

Options:
  --directory DIR      Directory to process (default: .)
  --extension EXT      Filter by extension
  --prefix TEXT        Add prefix to filenames
  --suffix TEXT        Add suffix before extension
  --padding N          Zero-padding width (default: 3)
  --start N            Starting number (default: 1)
  --recursive, -r      Process subdirectories
  --dry-run            Preview only
  --force-python|--force-rust
```

---

### 📁 organize - Organize Files

```bash
fmtools organize [OPTIONS]

Examples:
  fmtools organize --source ~/Downloads --mode type --dry-run
  fmtools organize -s ~/Pictures --mode date --move -r
  fmtools organize --source ~/docs --categories custom.json

Options:
  --source DIR         Source directory (default: .)
  --dest DIR           Destination (default: source)
  --mode {type|date|cdate|size}
  --categories FILE    Custom categories JSON
  --move               Move instead of copy
  --recursive, -r      Process subdirectories
  --dry-run            Preview only
  --force-python|--force-rust
```

---

### 🎬 convert - Convert Media Files

```bash
fmtools convert [OPTIONS]

Examples:
  fmtools convert --from mp4 --to gif --speed 2.0
  fmtools convert -i ./videos -o ./gifs --from webm --to gif
  fmtools convert --from mp4 --to gif --fps 15 --quality high

Options:
  --input-dir DIR      Input directory (default: .)
  --output-dir DIR     Output directory
  --from FORMAT        Source format
  --to FORMAT          Target format
  --speed MULT         Speed multiplier (default: 1.0)
  --fps N              Frames per second
  --quality {low|medium|high}
  --workers N          Parallel workers
  --recursive, -r
```

---

### 📊 stats - File Statistics

```bash
fmtools stats [OPTIONS]

Examples:
  fmtools stats --directory ~/Documents
  fmtools stats -d ~/folder --duplicates --top 20
  fmtools stats --directory . --export-json report.json

Options:
  --directory DIR      Directory to analyze (default: .)
  --recursive, -r      Scan subdirectories (default: on)
  --duplicates         Include duplicate detection
  --top N              Number of top items (default: 10)
  --export-json FILE   Export to JSON
  --export-csv FILE    Export to CSV
```

---

### 🧹 clean - Remove Empty Directories

```bash
fmtools clean [OPTIONS]

Examples:
  fmtools clean --directory ~/Downloads --dry-run
  fmtools clean -d ~/folder --min-depth 1 --interactive
  fmtools clean --directory . --include-hidden

Options:
  --directory DIR      Directory to clean (default: .)
  --min-depth N        Minimum depth (default: 0)
  --include-hidden     Consider hidden files
  --interactive, -i    Confirm each deletion
  --dry-run            Preview only
```

---

### ⚡ speed - Adjust GIF Speed

```bash
fmtools speed [OPTIONS]

Examples:
  fmtools speed --input-dir ./gifs --speed 2.0
  fmtools speed -i ./gifs -o ./fast --speed 0.5 --fps 20
  fmtools speed --speed 3.0 --workers 8

Options:
  --input-dir DIR      Input directory (default: ./gif)
  --output-dir DIR     Output directory (default: ./output)
  --speed MULT         Speed multiplier (default: 2.0)
  --fps N              Target FPS
  --workers N          Parallel workers
```

---

### 🔐 hash - Generate & Verify Checksums

```bash
fmtools hash [FILES/OPTIONS]

Examples:
  fmtools hash file1.txt file2.txt
  fmtools hash --directory ~/downloads -r --output checksums.sha256
  fmtools hash --verify checksums.sha256

Options:
  FILES                Files to hash
  --directory DIR      Hash directory
  --algorithm {sha256|md5|sha1} (default: sha256)
  --recursive, -r      Hash recursively
  --verify FILE        Verify against checksum file
  --output FILE        Save checksums to file
  --format {simple|bsd|gnu} (default: gnu)
```

---

### 💾 backup - Create Backups

```bash
fmtools backup SOURCE DEST [OPTIONS]

Examples:
  fmtools backup ~/Documents ~/Backups --dry-run
  fmtools backup ~/docs ~/backups --incremental --compress gzip --keep 5
  fmtools backup ~/src ~/bak --exclude "*.tmp" --exclude ".git"

Options:
  SOURCE               Source directory
  DEST                 Backup destination
  --incremental, -i    Incremental backup (hardlinks)
  --compress {none|gzip|bz2|xz}
  --exclude PATTERN    Exclude pattern (can use multiple)
  --keep N             Keep N most recent backups (default: 5)
  --dry-run            Preview only
```

---

### 🔍 find - Advanced File Finder

```bash
fmtools find [OPTIONS]

Examples:
  fmtools find --larger 100MB --older 30d
  fmtools find --directory ~/logs --extension log --older 7d
  fmtools find --name "*.tmp" --exec "rm {}"

Options:
  --directory DIR      Directory to search (default: .)
  --name PATTERN       Name pattern (wildcards)
  --regex PATTERN      Regex pattern
  --extension EXT      Extension filter
  --larger SIZE        Larger than (e.g., 100MB, 1GB)
  --smaller SIZE       Smaller than
  --older DAYS         Older than N days (e.g., 30d)
  --newer DAYS         Newer than N days
  --type {file|dir|link}
  --output {list|json|exec}
  --exec CMD           Execute command ({} = filename)
  --limit N            Limit results
```

---

### 🗜️ compress - Compress Files

```bash
fmtools compress [OPTIONS]

Examples:
  fmtools compress --directory ~/images --type image --quality 85
  fmtools compress -d ~/folder --type archive --archive-format zip
  fmtools compress --type image --format webp -r --dry-run

Options:
  --directory DIR      Directory to process (default: .)
  --type {image|pdf|archive}
  --quality N          Image quality 1-100 (default: 85)
  --format FORMAT      Output format for images
  --archive-format {zip|tar.gz|tar.bz2}
  --output FILE        Output directory or archive name
  --recursive, -r      Process subdirectories
  --dry-run            Preview only
```

---

### ⚙️ config - Manage Configuration

```bash
fmtools config ACTION [ARGS]

Examples:
  fmtools config show
  fmtools config get defaults.dedup.algorithm
  fmtools config set defaults.dedup.algorithm md5
  fmtools config set rust.threshold 500
  fmtools config reset

Actions:
  show                 Show current configuration
  get KEY              Get configuration value
  set KEY VALUE        Set configuration value
  reset                Reset to defaults
```

---

## Common Workflows

### Daily Downloads Cleanup

```bash
fmtools dedup ~/Downloads --batch --keep newest
fmtools organize --source ~/Downloads --mode type --move
fmtools clean --directory ~/Downloads
```

### Photo Organization

```bash
fmtools organize --source ~/Pictures --mode date --move
fmtools dedup ~/Pictures --batch --keep newest
fmtools compress --directory ~/Pictures --type image --quality 85 -r
```

### Find & Remove Large Old Files

```bash
fmtools find --larger 1GB --older 90d --output list
fmtools find --larger 1GB --older 90d --exec "rm {}"
```

### Weekly Backup

```bash
fmtools backup ~/Documents ~/Backups \
  --incremental \
  --compress gzip \
  --exclude "*.tmp" \
  --keep 10
```

### Verify Downloads

```bash
fmtools hash --directory ~/downloads -r --output checksums.sha256
fmtools hash --verify checksums.sha256
```

---

## Configuration Quick Reference

### View Config

```bash
fmtools config show
```

### Common Settings

```bash
# Faster hashing (less secure)
fmtools config set defaults.dedup.algorithm md5

# Use Rust earlier (500 files instead of 1000)
fmtools config set rust.threshold 500

# Change default keep strategy
fmtools config set defaults.dedup.keep oldest

# Enable logging
fmtools config set logging.level DEBUG
fmtools config set logging.file ~/.fmtools/fmtools.log
```

### Reset

```bash
fmtools config reset
```

---

## Tips

1. **Always use `--dry-run` first** to preview changes
2. **Use `--force-rust` for large datasets** (10-50x faster)
3. **Set common options in config** to avoid repeating them
4. **Enable `--verbose`** for debugging
5. **Check logs** in `~/.fmtools/` if something goes wrong

---

**For detailed help on any command:**

```bash
fmtools COMMAND --help
```

**For more examples:**

- See [GETTING_STARTED.md](GETTING_STARTED.md)
- See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
