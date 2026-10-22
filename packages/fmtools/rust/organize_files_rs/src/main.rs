use anyhow::{bail, Context, Result};
use chrono::{DateTime, Local};
use clap::Parser;
use fmtools_fs::{copy_noclobber, move_noclobber};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, HashSet};
use std::ffi::OsString;
use std::fs::{self, File, Metadata, OpenOptions};
use std::io::{self, Write};
use std::path::{Component, Path, PathBuf};
use std::time::SystemTime;
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(
    author,
    version,
    about = "Organize files into categorized folders without overwriting"
)]
struct Args {
    /// Source directory containing files to organize
    #[arg(long)]
    source: PathBuf,
    /// Destination directory (default: create subdirs in source)
    #[arg(long)]
    dest: Option<PathBuf>,
    /// Organization mode
    #[arg(long, default_value = "type", value_parser = ["type", "date-modified", "date-created", "size"])]
    mode: String,
    /// JSON configuration with a categories object; invalid configs are rejected
    #[arg(long)]
    config: Option<PathBuf>,
    /// Move files instead of copying
    #[arg(long)]
    r#move: bool,
    /// Search recursively, excluding output trees and saved webpage resources
    #[arg(long)]
    recursive: bool,
    /// Preview exact destination names without changing files
    #[arg(long)]
    dry_run: bool,
    /// Exclude an exact basename or source-relative path; repeat as needed
    #[arg(long, value_name = "NAME_OR_PATH")]
    exclude: Vec<PathBuf>,
    /// Write a new JSONL operation journal; an existing report is never replaced
    #[arg(long, value_name = "PATH")]
    report: Option<PathBuf>,
    /// Enable verbose logging
    #[arg(short, long)]
    verbose: bool,
}

#[derive(Deserialize)]
struct Categories {
    categories: BTreeMap<String, Vec<String>>,
}

fn default_categories() -> BTreeMap<String, Vec<String>> {
    [
        ("Images", ".jpg .jpeg .png .gif .bmp .svg .webp .ico .tiff .tif .heic .avif"),
        ("Videos", ".mp4 .avi .mkv .mov .wmv .flv .webm .m4v .mpg .mpeg"),
        ("Audio", ".mp3 .wav .flac .aac .ogg .wma .m4a .opus .aiff"),
        ("Documents", ".pdf .doc .docx .txt .odt .rtf .tex .wpd .md .epub .mobi .ppt .pptx .xls .xlsx .ods .odp .csv .tsv"),
        ("Archives", ".zip .rar .7z .tar .gz .bz2 .xz .iso .tgz"),
        ("Code", ".py .js .java .c .cpp .h .cs .php .rb .go .rs .swift .ipynb .sql .html .htm .css .ts .tsx .jsx .sh .cmd .bat .ps1 .json .jsonl .xml .yaml .yml .conf .cfg .ini"),
        ("Executables", ".exe .msi .app .deb .rpm .dmg .apk .jar .appx .msix .msixbundle .appinstaller .xpi .vsix"),
        ("Subtitles", ".vtt .srt .sub .ass .ssa"),
    ].into_iter().map(|(category, extensions)| (category.into(), extensions.split_whitespace().map(String::from).collect())).collect()
}

fn valid_category(name: &str) -> bool {
    if name.is_empty()
        || name == "."
        || name == ".."
        || name.ends_with(['.', ' '])
        || name
            .chars()
            .any(|c| c.is_control() || "<>:\"/\\|?*".contains(c))
    {
        return false;
    }
    let stem = name.split('.').next().unwrap_or("").to_uppercase();
    !matches!(stem.as_str(), "CON" | "PRN" | "AUX" | "NUL")
        && !(stem.len() == 4
            && (stem.starts_with("COM") || stem.starts_with("LPT"))
            && matches!(stem.as_bytes()[3], b'1'..=b'9'))
}

fn load_categories(config: Option<&Path>) -> Result<BTreeMap<String, Vec<String>>> {
    let mut categories = match config {
        Some(path) => {
            let bytes = fs::read(path)
                .with_context(|| format!("Cannot read category config {}", path.display()))?;
            serde_json::from_slice::<Categories>(&bytes)
                .context("Invalid categories JSON")?
                .categories
        }
        None => default_categories(),
    };
    let mut extensions = HashSet::new();
    for (category, values) in &mut categories {
        if !valid_category(category) {
            bail!("Invalid category name {category:?}: use a single portable folder name");
        }
        for extension in values {
            *extension = extension.to_lowercase();
            if extension != "(no extension)" {
                let value = extension.strip_prefix('.').unwrap_or(extension);
                if value.is_empty()
                    || value
                        .chars()
                        .any(|c| c.is_control() || ".<>:\"/\\|?* ".contains(c))
                {
                    bail!("Invalid extension {extension:?} in category {category}");
                }
                *extension = format!(".{value}");
            }
            if !extensions.insert(extension.clone()) {
                bail!("Extension {extension:?} appears more than once in categories");
            }
        }
    }
    Ok(categories)
}

fn absolute(path: &Path) -> Result<PathBuf> {
    Ok(std::path::absolute(path)?)
}

/// Resolve existing ancestors even when the final destination is not created.
fn resolved(path: &Path) -> Result<PathBuf> {
    match path.canonicalize() {
        Ok(path) => Ok(path),
        Err(error) if error.kind() == io::ErrorKind::NotFound => {
            if fs::symlink_metadata(path).is_ok() {
                bail!("Cannot resolve {}: {error}", path.display());
            }
            let parent = path
                .parent()
                .context("Cannot resolve destination ancestor")?;
            let name = path.file_name().context("Missing destination component")?;
            Ok(resolved(parent)?.join(name))
        }
        Err(error) => Err(error).with_context(|| format!("Cannot resolve {}", path.display())),
    }
}

fn path_key(path: &Path) -> OsString {
    #[cfg(windows)]
    {
        OsString::from(path.to_string_lossy().to_lowercase())
    }
    #[cfg(not(windows))]
    {
        path.as_os_str().to_owned()
    }
}

fn reparse(metadata: &Metadata) -> bool {
    #[cfg(windows)]
    {
        use std::os::windows::fs::MetadataExt;
        metadata.file_attributes() & 0x400 != 0
    }
    #[cfg(not(windows))]
    {
        metadata.file_type().is_symlink()
    }
}

fn hidden(path: &Path, metadata: &Metadata) -> bool {
    let dotfile = path
        .file_name()
        .is_some_and(|name| name.to_string_lossy().starts_with('.'));
    #[cfg(windows)]
    {
        use std::os::windows::fs::MetadataExt;
        dotfile || metadata.file_attributes() & (0x2 | 0x4) != 0
    }
    #[cfg(not(windows))]
    {
        let _ = metadata;
        dotfile
    }
}

fn protected_name(path: &Path) -> bool {
    let name = path
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .to_lowercase();
    name == "desktop.ini"
        || name.starts_with("~$")
        || [
            ".crdownload",
            ".part",
            ".partial",
            ".download",
            ".opdownload",
            ".tmp",
            ".aria2",
        ]
        .iter()
        .any(|extension| name.ends_with(extension))
}

fn webpage(path: &Path, is_dir: bool) -> Result<bool> {
    if is_dir {
        let name = path_key(Path::new(path.file_name().unwrap_or_default()));
        if !name.to_string_lossy().ends_with("_files") {
            return Ok(false);
        }
        let parent = path.parent().unwrap_or_else(|| Path::new("."));
        for entry in fs::read_dir(parent).with_context(|| {
            format!(
                "Cannot check saved webpage companions in {}",
                parent.display()
            )
        })? {
            let entry = entry?;
            let page = entry.path();
            if !entry.file_type()?.is_file() || !is_html(&page) {
                continue;
            }
            let mut companion = page.file_stem().unwrap_or_default().to_os_string();
            companion.push("_files");
            if path_key(Path::new(&companion)) == name {
                return Ok(true);
            }
        }
        Ok(false)
    } else {
        if !is_html(path) {
            return Ok(false);
        }
        let mut name = path.file_stem().unwrap_or_default().to_os_string();
        name.push("_files");
        Ok(path.with_file_name(name).is_dir())
    }
}

fn is_html(path: &Path) -> bool {
    path.extension().is_some_and(|extension| {
        let extension = extension.to_string_lossy();
        extension.eq_ignore_ascii_case("htm") || extension.eq_ignore_ascii_case("html")
    })
}

fn size_category(size: u64) -> &'static str {
    match size {
        0..1024 => "Tiny",
        1024..1_048_576 => "Small",
        1_048_576..10_485_760 => "Medium",
        10_485_760..104_857_600 => "Large",
        _ => "Huge",
    }
}

fn category_for(
    path: &Path,
    metadata: &Metadata,
    mode: &str,
    categories: &BTreeMap<String, Vec<String>>,
) -> Result<String> {
    Ok(match mode {
        "type" => {
            let extension = path
                .extension()
                .filter(|ext| !ext.is_empty())
                .map(|ext| format!(".{}", ext.to_string_lossy().to_lowercase()))
                .unwrap_or_else(|| "(no extension)".into());
            categories
                .iter()
                .find(|(_, values)| values.contains(&extension))
                .map(|(category, _)| category.clone())
                .unwrap_or_else(|| "Other".into())
        }
        "size" => size_category(metadata.len()).into(),
        "date-created" | "date-modified" => {
            let time = if mode == "date-created" {
                metadata.created().or_else(|_| metadata.modified())?
            } else {
                metadata.modified()?
            };
            DateTime::<Local>::from(time).format("%Y-%m").to_string()
        }
        _ => bail!("Unknown organization mode: {mode}"),
    })
}

fn output_folder(name: &str, mode: &str, categories: &BTreeMap<String, Vec<String>>) -> bool {
    let same = |folder: &str| path_key(Path::new(folder)) == path_key(Path::new(name));
    match mode {
        "type" => same("Other") || categories.keys().any(|category| same(category)),
        "size" => ["Tiny", "Small", "Medium", "Large", "Huge"]
            .iter()
            .any(|folder| same(folder)),
        _ => {
            let bytes = name.as_bytes();
            name == "Unknown"
                || (bytes.len() == 7
                    && bytes[4] == b'-'
                    && bytes[..4].iter().all(u8::is_ascii_digit)
                    && bytes[5..].iter().all(u8::is_ascii_digit))
        }
    }
}

struct Operation {
    source: PathBuf,
    destination: PathBuf,
    size: u64,
    modified: SystemTime,
}

struct Notice {
    path: PathBuf,
    reason: String,
    is_file: bool,
}

struct Plan {
    operations: Vec<Operation>,
    skipped: Vec<Notice>,
    failed: Vec<Notice>,
}

fn occupied(path: &Path) -> Result<bool> {
    match fs::symlink_metadata(path) {
        Ok(_) => Ok(true),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(false),
        Err(error) => {
            Err(error).with_context(|| format!("Cannot inspect destination {}", path.display()))
        }
    }
}

fn reserve_destination(path: PathBuf, reserved: &mut HashSet<OsString>) -> Result<PathBuf> {
    let mut destination = path.clone();
    let mut counter = 0usize;
    while reserved.contains(&path_key(&destination)) || occupied(&destination)? {
        counter = counter
            .checked_add(1)
            .context("Too many filename conflicts")?;
        let mut name = path.file_stem().unwrap_or_default().to_os_string();
        name.push(format!("_{counter}"));
        if let Some(extension) = path.extension() {
            name.push(".");
            name.push(extension);
        }
        destination = path.with_file_name(name);
    }
    reserved.insert(path_key(&destination));
    Ok(destination)
}

fn make_plan(
    args: &Args,
    source: &Path,
    destination: &Path,
    categories: &BTreeMap<String, Vec<String>>,
) -> Result<Plan> {
    let source_real = source.canonicalize()?;
    let destination_real = resolved(destination)?;
    let in_place = source_real == destination_real;
    let nested_output = if !in_place && destination_real.starts_with(&source_real) {
        Some(source.join(destination_real.strip_prefix(&source_real)?))
    } else {
        None
    };
    let config_path = args
        .config
        .as_deref()
        .map(|path| resolved(&absolute(path)?))
        .transpose()?;
    let report_path = args
        .report
        .as_deref()
        .map(|path| resolved(&absolute(path)?))
        .transpose()?;
    let excludes = args
        .exclude
        .iter()
        .map(|exclude| {
            let mut normalized = PathBuf::new();
            for component in exclude.components() {
                match component {
                    Component::CurDir => (),
                    Component::Normal(name) => normalized.push(name),
                    _ => bail!(
                        "Exclusions must be names or source-relative paths without '..': {}",
                        exclude.display()
                    ),
                }
            }
            if normalized.as_os_str().is_empty() {
                bail!("An exclusion must identify a name or source-relative path");
            }
            Ok(normalized)
        })
        .collect::<Result<Vec<_>>>()?;
    let mut plan = Plan {
        operations: Vec::new(),
        skipped: Vec::new(),
        failed: Vec::new(),
    };
    let mut files = Vec::new();
    let mut walker = WalkDir::new(source)
        .min_depth(1)
        .max_depth(if args.recursive { usize::MAX } else { 1 })
        .follow_links(false)
        .sort_by_file_name()
        .into_iter();
    while let Some(entry) = walker.next() {
        let entry = match entry {
            Ok(entry) => entry,
            Err(error) => {
                plan.failed.push(Notice {
                    path: error.path().unwrap_or(source).to_path_buf(),
                    reason: error.to_string(),
                    is_file: true,
                });
                continue;
            }
        };
        let path = entry.path();
        let metadata = match fs::symlink_metadata(path) {
            Ok(metadata) => metadata,
            Err(error) => {
                plan.failed.push(Notice {
                    path: path.to_path_buf(),
                    reason: error.to_string(),
                    is_file: true,
                });
                continue;
            }
        };
        let is_dir = metadata.is_dir();
        let relative = path.strip_prefix(source)?;
        let real_path = source_real.join(relative);
        let excluded = excludes.iter().any(|exclude| {
            path_key(relative) == path_key(exclude)
                || (exclude.components().count() == 1
                    && path
                        .file_name()
                        .is_some_and(|name| path_key(Path::new(name)) == path_key(exclude)))
        });
        let reason = if metadata.file_type().is_symlink() || reparse(&metadata) {
            Some("symlink or reparse point")
        } else if nested_output
            .as_ref()
            .is_some_and(|output| path.starts_with(output))
        {
            Some("destination tree")
        } else if is_dir
            && in_place
            && relative.components().count() == 1
            && output_folder(&entry.file_name().to_string_lossy(), &args.mode, categories)
        {
            Some("existing category folder")
        } else if excluded {
            Some("explicit exclusion")
        } else if config_path
            .as_ref()
            .is_some_and(|config| path_key(&real_path) == path_key(config))
            || report_path
                .as_ref()
                .is_some_and(|report| path_key(&real_path) == path_key(report))
        {
            Some("organizer configuration or journal")
        } else if hidden(path, &metadata) || protected_name(path) {
            Some("hidden/system file, lock file, or incomplete download")
        } else if webpage(path, is_dir)? {
            Some("saved webpage and companion resources")
        } else {
            None
        };
        if let Some(reason) = reason {
            plan.skipped.push(Notice {
                path: path.to_path_buf(),
                reason: reason.into(),
                is_file: !is_dir,
            });
            if is_dir {
                walker.skip_current_dir();
            }
        } else if metadata.file_type().is_file() {
            files.push((path.to_path_buf(), metadata));
        }
    }
    files.sort_by(|(a, _), (b, _)| a.cmp(b));
    let mut reserved = HashSet::new();
    for (path, metadata) in files {
        let category = match category_for(&path, &metadata, &args.mode, categories) {
            Ok(category) => category,
            Err(error) => {
                plan.failed.push(Notice {
                    path,
                    reason: error.to_string(),
                    is_file: true,
                });
                continue;
            }
        };
        let directory = destination.join(category);
        if let Ok(metadata) = fs::symlink_metadata(&directory) {
            if !metadata.is_dir() || reparse(&metadata) || metadata.file_type().is_symlink() {
                bail!(
                    "Category destination must be a real directory: {}",
                    directory.display()
                );
            }
        }
        if !resolved(&directory)?.starts_with(&destination_real) {
            bail!(
                "Category destination escapes the output directory: {}",
                directory.display()
            );
        }
        let target = directory.join(path.file_name().context("Missing source filename")?);
        if let (Ok(original), Ok(target_real)) = (path.canonicalize(), target.canonicalize()) {
            if original == target_real {
                plan.skipped.push(Notice {
                    path,
                    reason: "already in the correct location".into(),
                    is_file: true,
                });
                continue;
            }
        }
        let target = reserve_destination(target, &mut reserved)?;
        if let Some(report) = &report_path {
            if path_key(report) == path_key(&resolved(&target)?) {
                bail!(
                    "The journal path conflicts with an organized file: {}",
                    target.display()
                );
            }
        }
        let modified = metadata
            .modified()
            .with_context(|| format!("Cannot read modification time for {}", path.display()))?;
        plan.operations.push(Operation {
            source: path,
            destination: target,
            size: metadata.len(),
            modified,
        });
    }
    Ok(plan)
}

#[derive(Serialize)]
struct Record<'a> {
    source: &'a Path,
    destination: Option<&'a Path>,
    action: &'a str,
    status: &'a str,
    reason: Option<&'a str>,
    size: Option<u64>,
}

struct Journal(Option<File>);

impl Journal {
    fn new(path: Option<&Path>) -> Result<Self> {
        Ok(Self(
            path.map(|path| {
                OpenOptions::new()
                    .write(true)
                    .create_new(true)
                    .open(path)
                    .with_context(|| format!("Cannot create new journal {}", path.display()))
            })
            .transpose()?,
        ))
    }

    fn write(&mut self, record: Record<'_>) -> Result<()> {
        if let Some(file) = &mut self.0 {
            let mut line = serde_json::to_vec(&record)?;
            line.push(b'\n');
            file.write_all(&line)
                .context("Cannot write journal; stopping further operations")?;
            file.sync_data()
                .context("Cannot sync journal; stopping further operations")?;
        }
        Ok(())
    }
}

fn apply(operation: &Operation, should_move: bool) -> Result<()> {
    let metadata = fs::symlink_metadata(&operation.source)?;
    if !metadata.file_type().is_file()
        || reparse(&metadata)
        || metadata.len() != operation.size
        || metadata.modified()? != operation.modified
    {
        bail!("Source changed after planning; leaving it untouched");
    }
    let parent = operation
        .destination
        .parent()
        .context("Missing destination directory")?;
    if let Ok(metadata) = fs::symlink_metadata(parent) {
        if !metadata.is_dir() || reparse(&metadata) || metadata.file_type().is_symlink() {
            bail!(
                "Destination is no longer a real directory: {}",
                parent.display()
            );
        }
    }
    fs::create_dir_all(parent)?;
    if should_move {
        move_noclobber(&operation.source, &operation.destination)?;
    } else {
        copy_noclobber(&operation.source, &operation.destination)?;
    }
    Ok(())
}

fn main() -> Result<()> {
    let args = Args::parse();
    env_logger::Builder::from_default_env()
        .filter_level(if args.verbose {
            log::LevelFilter::Debug
        } else {
            log::LevelFilter::Info
        })
        .init();
    let source = absolute(&args.source)?;
    if !source.is_dir() {
        bail!("{} is not a valid directory", source.display());
    }
    let destination = absolute(args.dest.as_deref().unwrap_or(&source))?;
    let categories = load_categories(args.config.as_deref())?;
    let plan = make_plan(&args, &source, &destination, &categories)?;
    let mut journal = Journal::new(args.report.as_deref())?;
    let action = if args.r#move { "move" } else { "copy" };
    println!(
        "Organizing files in: {}\nMode: {}\nDestination: {}\nAction: {action}",
        source.display(),
        args.mode,
        destination.display()
    );
    println!("Found {} files to organize", plan.operations.len());
    for notice in &plan.skipped {
        log::debug!("Skipping {}: {}", notice.path.display(), notice.reason);
        journal.write(Record {
            source: &notice.path,
            destination: None,
            action,
            status: "skipped",
            reason: Some(&notice.reason),
            size: None,
        })?;
    }
    for notice in &plan.failed {
        eprintln!(
            "Error scanning {}: {}",
            notice.path.display(),
            notice.reason
        );
        journal.write(Record {
            source: &notice.path,
            destination: None,
            action,
            status: "failed",
            reason: Some(&notice.reason),
            size: None,
        })?;
    }
    let mut organized = 0;
    let mut failed = plan.failed.len();
    for operation in &plan.operations {
        journal.write(Record {
            source: &operation.source,
            destination: Some(&operation.destination),
            action,
            status: if args.dry_run { "planned" } else { "pending" },
            reason: None,
            size: Some(operation.size),
        })?;
        if args.dry_run {
            println!(
                "[DRY RUN] Would {action}: {} -> {}",
                operation.source.display(),
                operation.destination.display()
            );
            organized += 1;
            continue;
        }
        match apply(operation, args.r#move) {
            Ok(()) => {
                organized += 1;
                journal.write(Record {
                    source: &operation.source,
                    destination: Some(&operation.destination),
                    action,
                    status: if args.r#move { "moved" } else { "copied" },
                    reason: None,
                    size: Some(operation.size),
                })?;
                log::info!(
                    "{}: {} -> {}",
                    if args.r#move { "Moved" } else { "Copied" },
                    operation.source.display(),
                    operation.destination.display()
                );
            }
            Err(error) => {
                failed += 1;
                eprintln!(
                    "Error processing {} -> {}: {error:#}",
                    operation.source.display(),
                    operation.destination.display()
                );
                journal.write(Record {
                    source: &operation.source,
                    destination: Some(&operation.destination),
                    action,
                    status: "failed",
                    reason: Some(&format!("{error:#}")),
                    size: Some(operation.size),
                })?;
            }
        }
    }
    let skipped = plan.skipped.iter().filter(|notice| notice.is_file).count();
    println!("\n{}\n{}Summary:\nFiles organized: {organized}\nFiles skipped: {skipped}\nFiles with errors: {failed}\nTotal: {}\n{}", "=".repeat(60), if args.dry_run { "[DRY RUN] " } else { "" }, organized + skipped + failed, "=".repeat(60));
    if failed > 0 {
        bail!("Organization completed with {failed} error(s); failed files were not counted as organized");
    }
    Ok(())
}
