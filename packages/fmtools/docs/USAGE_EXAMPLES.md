# Usage examples

These examples use the installed `fmtools` command. Unless noted otherwise, run each from a directory where its relative input and output paths make sense. Commands with `--dry-run` show planned file operations without applying them.

## File operations

Preview duplicates in Downloads:

```sh
fmtools dedup ./Downloads --dry-run
```

After reviewing the preview, delete duplicates in batch mode while keeping the newest copy:

```sh
fmtools dedup ./Downloads --batch --keep newest
```

Preview a numbered rename of JPG files:

```sh
fmtools rename --directory ./photos --extension jpg --prefix photo_ --padding 3 --dry-run
```

Preview organizing files into type folders:

```sh
fmtools organize --source ./Downloads --dest ./Organized --mode type --dry-run
```

Preview empty-directory cleanup:

```sh
fmtools clean --directory ./workspace --dry-run
```

## Reports and checksums

Write directory statistics to JSON and CSV files:

```sh
fmtools stats --directory ./Documents --export-json ./stats.json --export-csv ./stats.csv
```

Generate a checksum for a file:

```sh
fmtools hash ./example.txt --algorithm sha256
```

Search for text files and save the results as JSON:

```sh
fmtools find --directory ./Documents --extension txt --output json
```

## Media and archives

Convert MP4 files to GIFs in an output directory:

```sh
fmtools convert --input-dir ./videos --output-dir ./gifs --from mp4 --to gif --fps 15
```

Write faster GIF copies to a separate directory:

```sh
fmtools speed --input-dir ./gifs --output-dir ./faster --speed 2
```

Preview creating an archive from a directory:

```sh
fmtools compress --directory ./photos --type archive --output ./photos.zip --dry-run
```

See `fmtools COMMAND --help` for additional options and format support. Conversion and GIF speed commands use MoviePy 1.x; see the [package README](../README.md) for media requirements.

## Configuration

Use a separate settings file for a project by placing the global `--config` option before the command:

```sh
fmtools --config ./settings.yaml config set defaults.dedup.algorithm sha256
fmtools --config ./settings.yaml config get defaults.dedup.algorithm
fmtools --config ./settings.yaml config show
```

For optional Rust acceleration, see the [Rust guide](USE_RUST_GUIDE.md). Use `--force-python` to explicitly select Python or `--force-rust` to request a matching bundled executable for supported commands.
