use anyhow::{anyhow, bail, Context, Result};
use clap::Parser;
use indicatif::{ProgressBar, ProgressStyle};
use std::collections::HashSet;
use std::fs;
use std::path::{Component, Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(author, version, about = "Rename files with sequential numbering or custom patterns", long_about = None)]
struct Args {
    /// Directory containing files to rename
    #[arg(long, default_value = ".")]
    directory: PathBuf,
    /// File extension to filter (e.g., gif, txt, jpg)
    #[arg(long)]
    extension: String,
    /// Prefix to add before the number
    #[arg(long, default_value = "")]
    prefix: String,
    /// Suffix to add after the number but before extension
    #[arg(long, default_value = "")]
    suffix: String,
    /// Number of digits for zero-padding
    #[arg(long, default_value = "1")]
    padding: usize,
    /// Starting number
    #[arg(long, default_value = "1")]
    start: usize,
    /// Search recursively in subdirectories
    #[arg(long)]
    recursive: bool,
    /// Simulate renaming without actually renaming files
    #[arg(long)]
    dry_run: bool,
    /// Enable verbose logging
    #[arg(short, long)]
    verbose: bool,
}

fn validate_component_part(value: &str, label: &str) -> Result<()> {
    if value.contains('/')
        || value.contains('\\')
        || value.contains(':')
        || value.chars().any(char::is_control)
    {
        bail!("{label} must not contain path separators, drive markers, or control characters");
    }
    Ok(())
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct SourceSnapshot {
    len: u64,
    modified: Option<std::time::SystemTime>,
    created: Option<std::time::SystemTime>,
    identity: Option<(u64, u64)>,
}

#[derive(Clone, Debug)]
struct ScannedFile {
    path: PathBuf,
    snapshot: SourceSnapshot,
}

fn source_snapshot(path: &Path) -> Result<SourceSnapshot> {
    let (metadata, identity) = snapshot_metadata(path)
        .with_context(|| format!("could not inspect source {}", path.display()))?;
    if !metadata.file_type().is_file() {
        bail!("source is no longer a regular file: {}", path.display());
    }
    Ok(SourceSnapshot {
        len: metadata.len(),
        modified: metadata.modified().ok(),
        created: metadata.created().ok(),
        identity,
    })
}

#[cfg(not(windows))]
fn snapshot_metadata(path: &Path) -> Result<(fs::Metadata, Option<(u64, u64)>)> {
    let metadata = fs::symlink_metadata(path)?;
    let identity = file_identity(&metadata);
    Ok((metadata, identity))
}

#[cfg(windows)]
fn snapshot_metadata(path: &Path) -> Result<(fs::Metadata, Option<(u64, u64)>)> {
    use std::os::windows::fs::OpenOptionsExt;
    use std::os::windows::io::AsRawHandle;
    use windows_sys::Win32::Storage::FileSystem::{
        GetFileInformationByHandle, BY_HANDLE_FILE_INFORMATION, FILE_FLAG_OPEN_REPARSE_POINT,
        FILE_READ_ATTRIBUTES,
    };

    // Query attributes and identity through the same handle, without reading
    // file contents or following a replacement symlink.
    let file = fs::OpenOptions::new()
        .read(true)
        .access_mode(FILE_READ_ATTRIBUTES)
        .custom_flags(FILE_FLAG_OPEN_REPARSE_POINT)
        .open(path)?;
    let metadata = file.metadata()?;
    let mut information = std::mem::MaybeUninit::<BY_HANDLE_FILE_INFORMATION>::uninit();
    // SAFETY: file owns a live handle and information points to writable storage.
    if unsafe { GetFileInformationByHandle(file.as_raw_handle(), information.as_mut_ptr()) } == 0 {
        return Err(std::io::Error::last_os_error()).context("could not read source file identity");
    }
    // SAFETY: a successful call initializes the complete information structure.
    let information = unsafe { information.assume_init() };
    let index =
        (u64::from(information.nFileIndexHigh) << 32) | u64::from(information.nFileIndexLow);
    Ok((
        metadata,
        Some((u64::from(information.dwVolumeSerialNumber), index)),
    ))
}

#[cfg(unix)]
fn file_identity(metadata: &fs::Metadata) -> Option<(u64, u64)> {
    use std::os::unix::fs::MetadataExt;
    Some((metadata.dev(), metadata.ino()))
}

#[cfg(not(any(unix, windows)))]
fn file_identity(_metadata: &fs::Metadata) -> Option<(u64, u64)> {
    None
}

fn snapshot_matches(expected: &SourceSnapshot, actual: &SourceSnapshot) -> bool {
    expected == actual
}

fn get_files_to_rename(
    directory: &Path,
    extension: &str,
    recursive: bool,
) -> Result<Vec<ScannedFile>> {
    validate_component_part(extension.trim_start_matches('.'), "extension")?;
    let wanted = extension.trim_start_matches('.').to_lowercase();
    let mut files = Vec::new();
    if recursive {
        for entry in WalkDir::new(directory).follow_links(false) {
            let entry = entry.context("failed while traversing input directory")?;
            if entry.file_type().is_file()
                && entry.depth() > 0
                && entry
                    .path()
                    .extension()
                    .is_some_and(|ext| ext.to_string_lossy().eq_ignore_ascii_case(&wanted))
            {
                let path = entry.path().to_path_buf();
                files.push(ScannedFile {
                    snapshot: source_snapshot(&path)?,
                    path,
                });
            }
        }
    } else {
        for entry in fs::read_dir(directory)? {
            let entry = entry?;
            let kind = entry.file_type()?;
            if kind.is_file()
                && entry
                    .path()
                    .extension()
                    .is_some_and(|ext| ext.to_string_lossy().eq_ignore_ascii_case(&wanted))
            {
                let path = entry.path();
                files.push(ScannedFile {
                    snapshot: source_snapshot(&path)?,
                    path,
                });
            }
        }
    }
    files.sort_by(|a, b| a.path.cmp(&b.path));
    Ok(files)
}

fn generate_new_name(
    index: usize,
    extension: &str,
    prefix: &str,
    suffix: &str,
    padding: usize,
    start_num: usize,
) -> Result<String> {
    validate_component_part(prefix, "prefix")?;
    validate_component_part(suffix, "suffix")?;
    validate_component_part(extension.trim_start_matches('.'), "extension")?;
    if padding > 1000 {
        bail!("padding must be at most 1000 digits");
    }
    let num = start_num
        .checked_add(index)
        .ok_or_else(|| anyhow!("numbering overflow: start plus file count is too large"))?;
    let ext = extension.trim_start_matches('.');
    let name = format!(
        "{}{:0width$}{}{}",
        prefix,
        num,
        suffix,
        if ext.is_empty() {
            String::new()
        } else {
            format!(".{ext}")
        },
        width = padding
    );
    let mut components = Path::new(&name).components();
    if !matches!(components.next(), Some(Component::Normal(_))) || components.next().is_some() {
        bail!("generated target name must be a single file name");
    }
    Ok(name)
}

#[derive(Debug)]
struct MoveRecord {
    original: PathBuf,
    staged: PathBuf,
    final_path: PathBuf,
    snapshot: SourceSnapshot,
    staged_in_temp: bool,
    finalized: bool,
}

static STAGE_ID: AtomicU64 = AtomicU64::new(0);
fn create_stage_dir(parent: &Path) -> Result<PathBuf> {
    loop {
        let id = STAGE_ID.fetch_add(1, Ordering::Relaxed);
        let path = parent.join(format!(".rename-files-stage-{}-{id}", std::process::id()));
        match fs::create_dir(&path) {
            Ok(()) => return Ok(path),
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(e) => {
                return Err(e).with_context(|| {
                    format!("could not create staging directory in {}", parent.display())
                })
            }
        }
    }
}

fn rollback(
    records: &mut [MoveRecord],
    mover: &mut impl FnMut(&Path, &Path) -> std::io::Result<()>,
) -> Vec<String> {
    let mut failures = Vec::new();

    // Evacuate every published target before restoring any original paths. A target
    // may itself be another source path, so direct reverse moves can collide.
    for index in (0..records.len()).rev() {
        if !records[index].finalized {
            continue;
        }
        if let Err(error) = mover(&records[index].final_path, &records[index].staged) {
            failures.push(format!(
                "recover {} from {} (could not evacuate published target: {error})",
                records[index].original.display(),
                records[index].final_path.display()
            ));
        } else {
            records[index].finalized = false;
            records[index].staged_in_temp = true;
        }
    }

    // If any published target could not be evacuated, leave every remaining file
    // where it is and report all locations. Restoring into overlapping paths could
    // otherwise strand or overwrite another batch member.
    if !failures.is_empty() {
        for record in records.iter() {
            if record.finalized {
                failures.push(format!(
                    "{} remains at {}",
                    record.original.display(),
                    record.final_path.display()
                ));
            } else if record.staged_in_temp {
                failures.push(format!(
                    "{} remains at {}",
                    record.original.display(),
                    record.staged.display()
                ));
            }
        }
        return failures;
    }

    for record in records.iter_mut().rev().filter(|r| r.staged_in_temp) {
        if let Err(error) = mover(&record.staged, &record.original) {
            failures.push(format!(
                "recover {} from {} (rollback failed: {error})",
                record.original.display(),
                record.staged.display()
            ));
        } else {
            record.staged = record.original.clone();
            record.staged_in_temp = false;
        }
    }
    failures
}

fn run_transaction(
    records: &mut [MoveRecord],
    mut mover: impl FnMut(&Path, &Path) -> std::io::Result<()>,
) -> Result<()> {
    for index in 0..records.len() {
        if let Err(e) = mover(&records[index].original, &records[index].staged) {
            let cause = anyhow!("failed staging {}: {e}", records[index].original.display());
            let recovery = rollback(records, &mut mover);
            return Err(append_recovery(cause, recovery));
        }
        records[index].staged_in_temp = true;
        let actual = source_snapshot(&records[index].staged);
        let snapshot_error = match actual {
            Ok(actual) if snapshot_matches(&records[index].snapshot, &actual) => None,
            Ok(_) => Some(anyhow!(
                "source changed since scan: {}",
                records[index].original.display()
            )),
            Err(error) => Some(error),
        };
        if let Some(cause) = snapshot_error {
            let recovery = rollback(records, &mut mover);
            return Err(append_recovery(cause, recovery));
        }
    }
    for record in records.iter_mut() {
        if let Err(e) = mover(&record.staged, &record.final_path) {
            let cause = anyhow!(
                "failed applying {} -> {}: {e}",
                record.original.display(),
                record.final_path.display()
            );
            let recovery = rollback(records, &mut mover);
            return Err(append_recovery(cause, recovery));
        }
        record.finalized = true;
        record.staged_in_temp = false;
    }
    Ok(())
}

#[derive(Clone, Copy)]
struct RenameOptions<'a> {
    extension: &'a str,
    prefix: &'a str,
    suffix: &'a str,
    padding: usize,
    start_num: usize,
    dry_run: bool,
    recursive: bool,
}

fn rename_files(directory: &Path, options: &RenameOptions<'_>) -> Result<(usize, usize)> {
    let RenameOptions {
        extension,
        prefix,
        suffix,
        padding,
        start_num,
        dry_run,
        recursive,
    } = *options;
    validate_component_part(prefix, "prefix")?;
    validate_component_part(suffix, "suffix")?;
    validate_component_part(extension.trim_start_matches('.'), "extension")?;
    if padding > 1000 {
        bail!("padding must be at most 1000 digits");
    }
    let files = get_files_to_rename(directory, extension, recursive)?;
    if files.is_empty() {
        println!("No {} files found in {}", extension, directory.display());
        return Ok((0, 0));
    }
    println!("Found {} {} files to rename", files.len(), extension);
    let mut pairs = Vec::with_capacity(files.len());
    for (i, source) in files.iter().enumerate() {
        let name = generate_new_name(i, extension, prefix, suffix, padding, start_num)?;
        let target = source.path.parent().unwrap_or(Path::new(".")).join(name);
        pairs.push((source.path.clone(), target, source.snapshot.clone()));
    }
    let sources: HashSet<_> = files.iter().map(|file| file.path.clone()).collect();
    let mut targets = HashSet::new();
    for (_, target, _) in &pairs {
        if !targets.insert(target.clone()) {
            bail!("multiple source files map to {}", target.display());
        }
        if target.exists() && !sources.contains(target) {
            bail!(
                "naming conflict: {} already exists and is not part of the rename batch",
                target.display()
            );
        }
    }
    let actual: Vec<_> = pairs
        .into_iter()
        .filter(|(src, dst, _)| src != dst)
        .collect();
    let skipped = files.len() - actual.len();
    if dry_run {
        for (src, dst, _) in &actual {
            println!(
                "[DRY RUN] Would rename: {} -> {}",
                src.display(),
                dst.file_name().unwrap_or_default().to_string_lossy()
            );
        }
        return Ok((actual.len(), skipped));
    }
    if actual.is_empty() {
        return Ok((0, skipped));
    }
    let pb = ProgressBar::new(actual.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})",
            )?
            .progress_chars("#>-"),
    );

    let mut stages: std::collections::HashMap<PathBuf, PathBuf> = std::collections::HashMap::new();
    let mut records = Vec::with_capacity(actual.len());
    for (src, dst, snapshot) in actual {
        let parent = src.parent().unwrap_or(Path::new("."));
        let stage_dir = if let Some(path) = stages.get(parent) {
            path.clone()
        } else {
            let path = match create_stage_dir(parent) {
                Ok(path) => path,
                Err(error) => {
                    let cleanup_error = cleanup_stage_dirs(stages.values()).err();
                    return Err(match cleanup_error {
                        Some(cleanup) => anyhow!("{error}; {cleanup}"),
                        None => error,
                    });
                }
            };
            stages.insert(parent.to_path_buf(), path.clone());
            path
        };
        let staged = stage_dir.join(format!("{}", records.len()));
        records.push(MoveRecord {
            original: src,
            staged,
            final_path: dst,
            snapshot,
            staged_in_temp: false,
            finalized: false,
        });
    }
    if let Err(e) = run_transaction(&mut records, fmtools_fs::move_noclobber) {
        let _ = cleanup_stage_dirs(stages.values());
        return Err(e);
    }
    pb.set_position(records.len() as u64);
    cleanup_stage_dirs(stages.values())
        .context("renames succeeded but staging directories could not be removed")?;
    pb.finish_with_message("Renaming complete");
    Ok((records.len(), skipped))
}

fn cleanup_stage_dirs<'a>(paths: impl Iterator<Item = &'a PathBuf>) -> Result<()> {
    for path in paths {
        fs::remove_dir(path)
            .with_context(|| format!("could not remove staging directory {}", path.display()))?;
    }
    Ok(())
}

fn append_recovery(error: anyhow::Error, paths: Vec<String>) -> anyhow::Error {
    if paths.is_empty() {
        error
    } else {
        anyhow!(
            "{error}; rollback was incomplete. Recovery details: {}",
            paths.join("; ")
        )
    }
}

fn main() -> Result<()> {
    let args = Args::parse();
    if args.verbose {
        env_logger::Builder::from_default_env()
            .filter_level(log::LevelFilter::Debug)
            .init();
    } else {
        env_logger::Builder::from_default_env()
            .filter_level(log::LevelFilter::Info)
            .init();
    }
    if !args.directory.is_dir() {
        bail!("{} is not a valid directory", args.directory.display());
    }
    println!("Starting file rename in: {}", args.directory.display());
    println!(
        "Extension: {}, Prefix: '{}', Suffix: '{}'",
        args.extension, args.prefix, args.suffix
    );
    println!("Padding: {}, Start: {}", args.padding, args.start);
    let options = RenameOptions {
        extension: &args.extension,
        prefix: &args.prefix,
        suffix: &args.suffix,
        padding: args.padding,
        start_num: args.start,
        dry_run: args.dry_run,
        recursive: args.recursive,
    };
    let (files_renamed, files_skipped) = rename_files(&args.directory, &options)?;
    println!("\n{}", "=".repeat(60));
    if args.dry_run {
        println!("[DRY RUN] Summary:");
    } else {
        println!("Summary:");
    }
    println!("Files renamed: {}", files_renamed);
    println!("Files skipped: {}", files_skipped);
    println!("{}", "=".repeat(60));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicUsize, Ordering};

    static NEXT: AtomicUsize = AtomicUsize::new(0);
    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Self {
            let path = std::env::temp_dir().join(format!(
                "rename-files-test-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            fs::create_dir_all(&path).unwrap();
            Self(path)
        }
        fn put(&self, name: &str) {
            fs::write(self.0.join(name), b"fixture").unwrap();
        }
    }
    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    fn default_options() -> RenameOptions<'static> {
        RenameOptions {
            extension: "gif",
            prefix: "",
            suffix: "",
            padding: 1,
            start_num: 1,
            dry_run: false,
            recursive: false,
        }
    }
    fn rename_default(f: &Fixture, dry_run: bool) -> Result<(usize, usize)> {
        let options = RenameOptions {
            dry_run,
            ..default_options()
        };
        rename_files(&f.0, &options)
    }

    #[test]
    fn preserves_preexisting_tmp_name_and_completes_rename() {
        let f = Fixture::new();
        f.put("a.gif");
        f.put("a.tmp_0");
        assert_eq!(rename_default(&f, false).unwrap(), (1, 0));
        assert_eq!(fs::read(f.0.join("a.tmp_0")).unwrap(), b"fixture");
        assert!(f.0.join("1.gif").exists());
    }

    #[test]
    fn rejects_prefix_that_escapes_directory() {
        let f = Fixture::new();
        f.put("a.gif");
        assert!(rename_files(
            &f.0,
            &RenameOptions {
                prefix: "..\\escape\\",
                ..default_options()
            }
        )
        .is_err());
        assert!(f.0.join("a.gif").exists());
    }

    #[test]
    fn dry_run_does_not_change_files() {
        let f = Fixture::new();
        f.put("a.gif");
        assert_eq!(rename_default(&f, true).unwrap(), (1, 0));
        assert!(f.0.join("a.gif").exists());
        assert!(!f.0.join("1.gif").exists());
    }

    #[test]
    fn overlapping_batch_names_are_staged_safely() {
        let f = Fixture::new();
        f.put("1.gif");
        f.put("a.gif");
        assert_eq!(rename_default(&f, false).unwrap(), (1, 1));
        assert!(f.0.join("1.gif").exists());
        assert!(f.0.join("2.gif").exists());
    }

    #[test]
    fn rejects_number_overflow_before_mutating() {
        let f = Fixture::new();
        f.put("a.gif");
        f.put("b.gif");
        assert!(rename_files(
            &f.0,
            &RenameOptions {
                start_num: usize::MAX,
                padding: 2,
                ..default_options()
            }
        )
        .is_err());
        assert!(f.0.join("a.gif").exists());
    }

    #[test]
    fn rejects_excessive_padding_before_mutating() {
        let f = Fixture::new();
        f.put("a.gif");
        assert!(rename_files(
            &f.0,
            &RenameOptions {
                padding: 1001,
                ..default_options()
            }
        )
        .is_err());
        assert!(f.0.join("a.gif").exists());
    }

    #[cfg(unix)]
    #[test]
    fn skips_symlinks() {
        use std::os::unix::fs::symlink;
        let f = Fixture::new();
        f.put("target.gif");
        symlink(f.0.join("target.gif"), f.0.join("link.gif")).unwrap();
        assert_eq!(rename_default(&f, false).unwrap(), (1, 0));
        assert!(f
            .0
            .join("link.gif")
            .symlink_metadata()
            .unwrap()
            .file_type()
            .is_symlink());
    }

    #[test]
    fn rolls_back_if_source_is_replaced_between_scan_and_staging() {
        let f = Fixture::new();
        let original = f.0.join("a.gif");
        fs::write(&original, b"fixture").unwrap();
        let snapshot = source_snapshot(&original).unwrap();
        let stage_dir = f.0.join(".test-stage");
        fs::create_dir(&stage_dir).unwrap();
        let mut records = vec![MoveRecord {
            original: original.clone(),
            staged: stage_dir.join("a"),
            final_path: f.0.join("1.gif"),
            snapshot,
            staged_in_temp: false,
            finalized: false,
        }];
        let mut replaced = false;
        let result = run_transaction(&mut records, |from, to| {
            if from == original && !replaced {
                fs::remove_file(from)?;
                fs::write(from, b"swapped")?;
                replaced = true;
            }
            fmtools_fs::move_noclobber(from, to)
        });
        assert!(result.is_err());
        assert_eq!(fs::read(&original).unwrap(), b"swapped");
        assert!(!f.0.join("1.gif").exists());
        assert_eq!(fs::read_dir(&stage_dir).unwrap().count(), 0);
    }

    #[cfg(any(unix, windows))]
    #[test]
    fn rolls_back_replacement_with_matching_size_and_timestamps() {
        let f = Fixture::new();
        let original = f.0.join("a.gif");
        fs::write(&original, b"fixture").unwrap();
        let mut snapshot = source_snapshot(&original).unwrap();
        let retained = f.0.join("retained-original");
        fs::rename(&original, &retained).unwrap();
        fs::write(&original, b"swapped").unwrap();
        let replacement = source_snapshot(&original).unwrap();
        assert_eq!(snapshot.len, replacement.len);
        // Clock precision and restored timestamps can make distinct files share
        // these attributes. The transaction must still reject the replacement.
        snapshot.modified = replacement.modified;
        snapshot.created = replacement.created;
        let stage_dir = f.0.join(".test-stage");
        fs::create_dir(&stage_dir).unwrap();
        let mut records = vec![MoveRecord {
            original: original.clone(),
            staged: stage_dir.join("a"),
            final_path: f.0.join("1.gif"),
            snapshot,
            staged_in_temp: false,
            finalized: false,
        }];
        assert!(run_transaction(&mut records, fmtools_fs::move_noclobber).is_err());
        assert_eq!(fs::read(&original).unwrap(), b"swapped");
        assert_eq!(fs::read(retained).unwrap(), b"fixture");
        assert!(!f.0.join("1.gif").exists());
        assert_eq!(fs::read_dir(&stage_dir).unwrap().count(), 0);
    }

    #[test]
    fn rolls_back_overlapping_source_and_target_names() {
        let f = Fixture::new();
        for name in ["1.gif", "2.gif", "3.gif"] {
            f.put(name);
        }
        let stage_dir = f.0.join(".test-stage");
        fs::create_dir(&stage_dir).unwrap();
        let mut records = Vec::new();
        for (index, name) in ["1.gif", "2.gif", "3.gif"].iter().enumerate() {
            let original = f.0.join(name);
            records.push(MoveRecord {
                snapshot: source_snapshot(&original).unwrap(),
                original,
                staged: stage_dir.join(index.to_string()),
                final_path: f.0.join(format!("{}.gif", index + 2)),
                staged_in_temp: false,
                finalized: false,
            });
        }
        let mut calls = 0;
        let result = run_transaction(&mut records, |from, to| {
            calls += 1;
            if calls == 6 {
                return Err(std::io::Error::other("injected third publish failure"));
            }
            fmtools_fs::move_noclobber(from, to)
        });
        assert!(result.is_err());
        for name in ["1.gif", "2.gif", "3.gif"] {
            assert!(f.0.join(name).exists(), "missing restored source {name}");
        }
        assert!(!f.0.join("4.gif").exists());
        assert_eq!(fs::read_dir(&stage_dir).unwrap().count(), 0);
    }

    #[test]
    fn reports_staging_path_when_rollback_fails() {
        let f = Fixture::new();
        f.put("a.gif");
        let original = f.0.join("a.gif");
        let stage_dir = f.0.join(".test-stage");
        fs::create_dir(&stage_dir).unwrap();
        let staged = stage_dir.join("a");
        let mut records = vec![MoveRecord {
            original: original.clone(),
            staged: staged.clone(),
            final_path: f.0.join("1.gif"),
            snapshot: source_snapshot(&original).unwrap(),
            staged_in_temp: false,
            finalized: false,
        }];
        let mut calls = 0;
        let result = run_transaction(&mut records, |from, to| {
            calls += 1;
            if calls == 2 || calls == 3 {
                return Err(std::io::Error::other("injected move failure"));
            }
            fmtools_fs::move_noclobber(from, to)
        });
        let error = result.unwrap_err().to_string();
        assert!(error.contains("rollback was incomplete"));
        assert!(error.contains(staged.to_string_lossy().as_ref()));
        assert!(staged.exists());
        assert!(!original.exists());
    }

    #[test]
    fn partial_finalization_failure_rolls_back_all_sources() {
        let f = Fixture::new();
        f.put("a.gif");
        f.put("b.gif");
        let stage_dir = f.0.join(".test-stage");
        fs::create_dir(&stage_dir).unwrap();
        let mut records = vec![
            MoveRecord {
                original: f.0.join("a.gif"),
                staged: stage_dir.join("a"),
                final_path: f.0.join("1.gif"),
                snapshot: source_snapshot(&f.0.join("a.gif")).unwrap(),
                staged_in_temp: false,
                finalized: false,
            },
            MoveRecord {
                original: f.0.join("b.gif"),
                staged: stage_dir.join("b"),
                final_path: f.0.join("2.gif"),
                snapshot: source_snapshot(&f.0.join("b.gif")).unwrap(),
                staged_in_temp: false,
                finalized: false,
            },
        ];
        let mut calls = 0;
        let result = run_transaction(&mut records, |from, to| {
            calls += 1;
            if calls == 4 {
                return Err(std::io::Error::other("injected final move failure"));
            }
            fmtools_fs::move_noclobber(from, to)
        });
        assert!(result.is_err());
        assert!(f.0.join("a.gif").exists());
        assert!(f.0.join("b.gif").exists());
        assert!(!f.0.join("1.gif").exists());
        assert!(!f.0.join("2.gif").exists());
        assert_eq!(fs::read_dir(&stage_dir).unwrap().count(), 0);
    }
}
