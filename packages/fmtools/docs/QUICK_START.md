# fmtools quick start

Install fmtools from the repository root in a Python 3.8+ virtual environment. Follow [the installation guide](INSTALL.md) if you have not installed it yet. The examples below assume `fmtools` is installed; run them from the directory whose files you want to process.

Preview duplicate detection before deleting anything:

```sh
fmtools dedup ./Downloads --dry-run
```

Rename matching files with a numbered prefix:

```sh
fmtools rename --directory ./photos --extension jpg --prefix photo_ --dry-run
```

Preview organizing downloads by file type:

```sh
fmtools organize --source ./Downloads --dest ./Organized --mode type --dry-run
```

Preview removal of empty directories:

```sh
fmtools clean --directory ./workspace --dry-run
```

Generate a statistics report:

```sh
fmtools stats --directory ./photos --export-json ./stats.json
```

Other commands include `convert`, `speed`, `hash`, `backup`, `find`, `compress`, and `config`. Get the current options for any command with `fmtools COMMAND --help`; see the [command reference](COMMAND_REFERENCE.md) for the full command list.

`--dry-run` is available on commands that change or remove files, such as `dedup`, `rename`, `organize`, `clean`, `backup`, and `compress`. Review each command's help before running it on important data. Deduplication prompts before deletion unless `--batch` is supplied.
