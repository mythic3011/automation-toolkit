use anyhow::{anyhow, Context, Result};
use clap::Parser;
use indicatif::{ProgressBar, ProgressStyle};
use rayon::prelude::*;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fs;
use std::io::{self, BufReader, Read, Write};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(author, version, about = "Find and delete duplicate files using parallel hashing", long_about = None)]
struct Args {
    /// Directory to scan for duplicates
    #[arg(default_value = ".")]
    directory: PathBuf,

    /// Automatically delete duplicates without prompting
    #[arg(long)]
    batch: bool,

    /// Which file to keep in each duplicate group
    #[arg(long, value_name = "MODE", default_value = "newest")]
    #[arg(value_parser = ["newest", "oldest", "first"])]
    keep: String,

    /// Hash algorithm to use
    #[arg(long, value_name = "ALGORITHM", default_value = "sha256")]
    #[arg(value_parser = ["sha256", "md5"])]
    algorithm: String,

    /// Minimum file size in bytes to consider
    #[arg(long, default_value = "0")]
    min_size: u64,

    /// Number of parallel workers (default: CPU count)
    #[arg(long)]
    workers: Option<usize>,

    /// Simulate deletions without actually deleting files
    #[arg(long)]
    dry_run: bool,

    /// Enable verbose logging
    #[arg(short, long)]
    verbose: bool,
}

#[derive(Clone)]
struct FileInfo {
    path: PathBuf,
    size: u64,
    modified: std::time::SystemTime,
}

fn calculate_hash(path: &Path, algorithm: &str) -> Result<String> {
    let file =
        fs::File::open(path).with_context(|| format!("Failed to open file: {}", path.display()))?;

    let mut reader = BufReader::new(file);
    let mut buffer = vec![0; 1024 * 1024]; // 1MB buffer

    match algorithm {
        "sha256" => {
            let mut hasher = Sha256::new();
            loop {
                let bytes_read = reader.read(&mut buffer)?;
                if bytes_read == 0 {
                    break;
                }
                hasher.update(&buffer[..bytes_read]);
            }
            Ok(format!("{:x}", hasher.finalize()))
        }
        "md5" => {
            let mut hasher = md5::Context::new();
            loop {
                let bytes_read = reader.read(&mut buffer)?;
                if bytes_read == 0 {
                    break;
                }
                hasher.consume(&buffer[..bytes_read]);
            }
            Ok(format!("{:x}", hasher.compute()))
        }
        _ => anyhow::bail!("Unsupported hash algorithm: {}", algorithm),
    }
}

fn collect_files(directory: &Path, min_size: u64) -> Result<Vec<FileInfo>> {
    let mut files = Vec::new();

    for entry in WalkDir::new(directory).follow_links(false) {
        let entry =
            entry.with_context(|| format!("Failed while scanning {}", directory.display()))?;
        if entry.file_type().is_file() {
            {
                let metadata = entry.metadata().with_context(|| {
                    format!("Failed to read metadata for {}", entry.path().display())
                })?;
                let size = metadata.len();
                if size >= min_size {
                    files.push(FileInfo {
                        path: entry.path().to_path_buf(),
                        size,
                        modified: metadata.modified().with_context(|| {
                            format!(
                                "Failed to read modification time for {}",
                                entry.path().display()
                            )
                        })?,
                    });
                }
            }
        }
    }

    Ok(files)
}

fn find_duplicates(
    directory: &Path,
    algorithm: &str,
    min_size: u64,
    workers: Option<usize>,
) -> Result<HashMap<String, Vec<FileInfo>>> {
    println!("Scanning directory: {}", directory.display());
    if workers == Some(0) {
        anyhow::bail!("--workers must be greater than zero");
    }

    // Step 1: Collect all files
    let files = collect_files(directory, min_size)?;
    println!("Found {} files", files.len());

    if files.is_empty() {
        return Ok(HashMap::new());
    }

    // Step 2: Group by size (fast pre-filtering)
    let mut size_groups: HashMap<u64, Vec<FileInfo>> = HashMap::new();
    for file in files {
        size_groups.entry(file.size).or_default().push(file);
    }

    // Get files with potential duplicates
    let potential_duplicates: Vec<FileInfo> = size_groups
        .into_iter()
        .filter(|(_, files)| files.len() > 1)
        .flat_map(|(_, files)| files)
        .collect();

    println!(
        "Found {} files with matching sizes",
        potential_duplicates.len()
    );

    if potential_duplicates.is_empty() {
        return Ok(HashMap::new());
    }

    // Step 3: Hash files in parallel
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(workers.unwrap_or_else(rayon::current_num_threads))
        .build()
        .context("Failed to create hashing thread pool")?;

    let pb = ProgressBar::new(potential_duplicates.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})",
            )
            .unwrap()
            .progress_chars("#>-"),
    );

    let results: Vec<Result<(String, FileInfo)>> = pool.install(|| {
        potential_duplicates
            .par_iter()
            .map(|file| {
                pb.inc(1);
                calculate_hash(&file.path, algorithm)
                    .map(|hash| (hash, file.clone()))
                    .with_context(|| format!("Failed to hash {}", file.path.display()))
            })
            .collect()
    });

    pb.finish_with_message("Hashing complete");

    // Group by hash
    let mut duplicates: HashMap<String, Vec<FileInfo>> = HashMap::new();
    for result in results {
        let (hash, file) = result?;
        duplicates.entry(hash).or_default().push(file);
    }

    // Keep only actual duplicates
    duplicates.retain(|_, files| files.len() > 1);

    Ok(duplicates)
}

fn format_size(size: u64) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB", "TB"];
    let mut size = size as f64;
    let mut unit_index = 0;

    while size >= 1024.0 && unit_index < UNITS.len() - 1 {
        size /= 1024.0;
        unit_index += 1;
    }

    format!("{:.2} {}", size, UNITS[unit_index])
}

fn delete_duplicates(
    duplicates: &HashMap<String, Vec<FileInfo>>,
    keep_mode: &str,
    batch: bool,
    dry_run: bool,
) -> Result<(usize, u64)> {
    let mut files_deleted = 0;
    let mut space_freed = 0u64;

    for (hash, files) in duplicates {
        if files.len() < 2 {
            continue;
        }

        // Sort files based on keep mode
        let mut sorted_files = files.clone();
        match keep_mode {
            "newest" => sorted_files.sort_by(|a, b| {
                b.modified
                    .cmp(&a.modified)
                    .then_with(|| a.path.cmp(&b.path))
            }),
            "oldest" => sorted_files.sort_by(|a, b| {
                a.modified
                    .cmp(&b.modified)
                    .then_with(|| a.path.cmp(&b.path))
            }),
            "first" => sorted_files.sort_by(|a, b| a.path.cmp(&b.path)),
            _ => {}
        }

        let keep_file = &sorted_files[0];
        let delete_files = &sorted_files[1..];

        println!(
            "\nDuplicate group (hash: {}...):",
            hash.chars().take(16).collect::<String>()
        );
        println!("  [KEEP] {}", keep_file.path.display());
        for df in delete_files {
            println!("  [DELETE] {}", df.path.display());
        }

        // Delete files
        for file in delete_files {
            let should_delete = if dry_run || batch {
                true
            } else {
                print!("Delete {}? (y/n/q): ", file.path.display());
                io::stdout().flush()?;

                let mut input = String::new();
                io::stdin().read_line(&mut input)?;
                let input = input.trim().to_lowercase();

                if input == "q" {
                    println!("Deletion cancelled by user");
                    return Ok((files_deleted, space_freed));
                }
                input == "y"
            };

            if should_delete {
                if dry_run {
                    println!(
                        "[DRY RUN] Would delete: {} ({} bytes)",
                        file.path.display(),
                        file.size
                    );
                } else {
                    delete_candidate(
                        keep_file,
                        file,
                        &mut fmtools_fs::move_noclobber,
                        &mut |path| fs::remove_file(path),
                    )
                    .with_context(|| {
                        format!(
                            "Failed to safely delete {} ({} files deleted, {} bytes freed so far)",
                            file.path.display(),
                            files_deleted,
                            space_freed
                        )
                    })?;
                    println!("Deleted: {} ({} bytes)", file.path.display(), file.size);
                    files_deleted += 1;
                    space_freed += file.size;
                }
            }
        }
    }

    Ok((files_deleted, space_freed))
}

fn verify_unchanged_at(file: &FileInfo, path: &Path) -> Result<()> {
    let m = fs::metadata(path)
        .with_context(|| format!("Cannot verify scanned file {}", path.display()))?;
    let modified = m
        .modified()
        .with_context(|| format!("Cannot verify modification time for {}", path.display()))?;
    if m.len() != file.size || modified != file.modified {
        anyhow::bail!("File changed since scan: {}", path.display());
    }
    Ok(())
}

static QUARANTINE_ID: AtomicU64 = AtomicU64::new(0);

fn quarantine_candidate(
    candidate: &FileInfo,
    mover: &mut impl FnMut(&Path, &Path) -> std::io::Result<()>,
) -> Result<PathBuf> {
    let parent = candidate.path.parent().unwrap_or(Path::new("."));
    loop {
        let id = QUARANTINE_ID.fetch_add(1, Ordering::Relaxed);
        let quarantine = parent.join(format!(".dupeforge-quarantine-{}-{id}", std::process::id()));
        match mover(&candidate.path, &quarantine) {
            Ok(()) => return Ok(quarantine),
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(e) => {
                return Err(e)
                    .with_context(|| format!("Could not quarantine {}", candidate.path.display()))
            }
        }
    }
}

fn restore_quarantine(
    original: &Path,
    quarantine: &Path,
    mover: &mut impl FnMut(&Path, &Path) -> std::io::Result<()>,
) -> Result<()> {
    mover(quarantine, original).map_err(|e| {
        anyhow!(
            "could not restore {} without overwriting; recovery file remains at {}: {e}",
            original.display(),
            quarantine.display()
        )
    })
}

fn delete_candidate(
    keeper: &FileInfo,
    candidate: &FileInfo,
    mover: &mut impl FnMut(&Path, &Path) -> std::io::Result<()>,
    remover: &mut impl FnMut(&Path) -> std::io::Result<()>,
) -> Result<()> {
    verify_unchanged_at(keeper, &keeper.path)?;
    let quarantine = quarantine_candidate(candidate, mover)?;
    let validation = (|| {
        verify_unchanged_at(keeper, &keeper.path)?;
        verify_unchanged_at(candidate, &quarantine)?;
        ensure_same_contents(&keeper.path, &quarantine)?;
        verify_unchanged_at(keeper, &keeper.path)?;
        verify_unchanged_at(candidate, &quarantine)
    })();
    if let Err(error) = validation {
        return match restore_quarantine(&candidate.path, &quarantine, mover) {
            Ok(()) => Err(error),
            Err(recovery) => Err(anyhow!("{error}; {recovery}")),
        };
    }
    if let Err(error) = remover(&quarantine) {
        return match restore_quarantine(&candidate.path, &quarantine, mover) {
            Ok(()) => Err(anyhow!(
                "could not remove verified quarantine {}: {error}",
                quarantine.display()
            )),
            Err(recovery) => Err(anyhow!(
                "could not remove verified quarantine {}: {error}; {recovery}",
                quarantine.display()
            )),
        };
    }
    Ok(())
}

fn ensure_same_contents(a: &Path, b: &Path) -> Result<()> {
    let mut left = BufReader::new(
        fs::File::open(a).with_context(|| format!("Cannot open keeper {}", a.display()))?,
    );
    let mut right = BufReader::new(
        fs::File::open(b).with_context(|| format!("Cannot open candidate {}", b.display()))?,
    );
    let mut x = [0u8; 65536];
    let mut y = [0u8; 65536];
    loop {
        let nx = left
            .read(&mut x)
            .with_context(|| format!("Cannot read keeper {}", a.display()))?;
        let ny = right
            .read(&mut y)
            .with_context(|| format!("Cannot read candidate {}", b.display()))?;
        if nx != ny || x[..nx] != y[..ny] {
            anyhow::bail!("Files no longer match: {} and {}", a.display(), b.display());
        }
        if nx == 0 {
            return Ok(());
        }
    }
}

fn main() -> Result<()> {
    let args = Args::parse();

    // Initialize logging
    if args.verbose {
        env_logger::Builder::from_default_env()
            .filter_level(log::LevelFilter::Debug)
            .init();
    } else {
        env_logger::Builder::from_default_env()
            .filter_level(log::LevelFilter::Info)
            .init();
    }

    // Validate directory
    if !args.directory.is_dir() {
        anyhow::bail!("{} is not a valid directory", args.directory.display());
    }

    println!(
        "Starting duplicate file scan in: {}",
        args.directory.display()
    );
    println!(
        "Algorithm: {}, Keep mode: {}, Min size: {} bytes",
        args.algorithm, args.keep, args.min_size
    );

    // Find duplicates
    let duplicates = find_duplicates(
        &args.directory,
        &args.algorithm,
        args.min_size,
        args.workers,
    )?;

    if duplicates.is_empty() {
        println!("\nNo duplicate files found!");
        return Ok(());
    }

    // Display summary
    let total_duplicates: usize = duplicates.values().map(|v| v.len() - 1).sum();
    let total_waste: u64 = duplicates
        .values()
        .map(|files| files.iter().skip(1).map(|f| f.size).sum::<u64>())
        .sum();

    println!("\n{}", "=".repeat(60));
    println!("Found {} groups of duplicates", duplicates.len());
    println!("Total duplicate files: {}", total_duplicates);
    println!("Potential space savings: {}", format_size(total_waste));
    println!("{}", "=".repeat(60));

    // List all duplicates
    for (hash, files) in &duplicates {
        println!("\nHash: {}", hash);
        for file in files {
            println!("  - {} ({})", file.path.display(), format_size(file.size));
        }
    }

    // Delete if requested
    let proceed = if args.batch || args.dry_run {
        true
    } else {
        print!("\nProceed with deletion? (y/n): ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        input.trim().to_lowercase() == "y"
    };

    if proceed {
        let (files_deleted, space_freed) =
            delete_duplicates(&duplicates, &args.keep, args.batch, args.dry_run)?;

        println!("\n{}", "=".repeat(60));
        if args.dry_run {
            println!("[DRY RUN] Summary:");
        } else {
            println!("Summary:");
        }
        println!("Files deleted: {}", files_deleted);
        println!("Space freed: {}", format_size(space_freed));
        println!("{}", "=".repeat(60));
    }

    Ok(())
}

#[cfg(test)]
mod safety_tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};
    use std::time::{SystemTime, UNIX_EPOCH};

    static FIXTURE_ID: AtomicU64 = AtomicU64::new(0);

    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Self {
            loop {
                let timestamp = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_nanos();
                let id = FIXTURE_ID.fetch_add(1, Ordering::Relaxed);
                let p = std::env::temp_dir().join(format!(
                    "dupeforge-test-{}-{timestamp}-{id}",
                    std::process::id()
                ));
                match fs::create_dir(&p) {
                    Ok(()) => return Self(p),
                    Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                    Err(error) => panic!("Failed to create test fixture {}: {error}", p.display()),
                }
            }
        }
        fn put(&self, name: &str, bytes: &[u8]) -> FileInfo {
            let p = self.0.join(name);
            fs::write(&p, bytes).unwrap();
            let m = fs::metadata(&p).unwrap();
            FileInfo {
                path: p,
                size: m.len(),
                modified: m.modified().unwrap(),
            }
        }
    }
    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn dry_run_never_counts_deletions() {
        let f = Fixture::new();
        let a = f.put("a", b"same");
        let b = f.put("b", b"same");
        let d = HashMap::from([("hash".to_owned(), vec![a, b.clone()])]);
        let (n, bytes) = delete_duplicates(&d, "first", true, true).unwrap();
        assert_eq!((n, bytes), (0, 0));
        assert!(b.path.exists());
    }

    #[test]
    fn content_is_compared_before_removal() {
        let f = Fixture::new();
        let a = f.put("a", b"same");
        let b = f.put("b", b"else");
        let d = HashMap::from([("collision".to_owned(), vec![a, b.clone()])]);
        assert!(delete_duplicates(&d, "first", true, false).is_err());
        assert!(b.path.exists());
    }

    #[test]
    fn missing_keeper_prevents_deletion() {
        let f = Fixture::new();
        let a = f.put("a", b"same");
        let b = f.put("b", b"same");
        let d = HashMap::from([("hash".to_owned(), vec![a.clone(), b.clone()])]);
        fs::remove_file(&a.path).unwrap();
        assert!(delete_duplicates(&d, "first", true, false).is_err());
        assert!(b.path.exists());
    }

    #[test]
    fn changed_candidate_is_quarantined_checked_and_restored() {
        let f = Fixture::new();
        let a = f.put("a", b"same");
        let b = f.put("b", b"same");
        fs::write(&b.path, b"replacement").unwrap();
        let d = HashMap::from([("hash".to_owned(), vec![a, b.clone()])]);
        assert!(delete_duplicates(&d, "first", true, false).is_err());
        assert_eq!(fs::read(&b.path).unwrap(), b"replacement");
        assert_eq!(fs::read_dir(&f.0).unwrap().count(), 2);
    }

    #[test]
    fn changed_keeper_prevents_candidate_removal() {
        let f = Fixture::new();
        let a = f.put("a", b"same");
        let b = f.put("b", b"same");
        fs::write(&a.path, b"changed keeper").unwrap();
        let d = HashMap::from([("hash".to_owned(), vec![a, b.clone()])]);
        assert!(delete_duplicates(&d, "first", true, false).is_err());
        assert_eq!(fs::read(&b.path).unwrap(), b"same");
        assert_eq!(fs::read_dir(&f.0).unwrap().count(), 2);
    }

    #[test]
    fn later_stale_candidate_reports_partial_deletion_counts() {
        let f = Fixture::new();
        let a = f.put("a", b"same");
        let b = f.put("b", b"same");
        let c = f.put("c", b"same");
        fs::write(&c.path, b"changed-size").unwrap();
        let d = HashMap::from([("hash".to_owned(), vec![a, b.clone(), c.clone()])]);
        let error = delete_duplicates(&d, "first", true, false).unwrap_err();
        assert!(error
            .to_string()
            .contains("1 files deleted, 4 bytes freed so far"));
        assert!(!b.path.exists());
        assert_eq!(fs::read(&c.path).unwrap(), b"changed-size");
    }

    #[test]
    fn failed_restore_reports_quarantine_recovery_path() {
        let f = Fixture::new();
        let keeper = f.put("a", b"same");
        let candidate = f.put("b", b"same");
        fs::write(&candidate.path, b"replacement").unwrap();
        let mut moves = 0;
        let mut mover = |from: &Path, to: &Path| {
            moves += 1;
            if moves == 2 {
                return Err(std::io::Error::new(
                    std::io::ErrorKind::PermissionDenied,
                    "injected restore failure",
                ));
            }
            fmtools_fs::move_noclobber(from, to)
        };
        let error = delete_candidate(&keeper, &candidate, &mut mover, &mut |path| {
            fs::remove_file(path)
        })
        .unwrap_err();
        let message = error.to_string();
        assert!(
            message.contains("recovery file remains at ")
                && message.contains(".dupeforge-quarantine"),
            "{message}"
        );
        assert!(!candidate.path.exists());
        assert_eq!(fs::read_dir(&f.0).unwrap().count(), 2);
        let quarantine = fs::read_dir(&f.0)
            .unwrap()
            .map(|e| e.unwrap().path())
            .find(|p| {
                p.file_name()
                    .unwrap()
                    .to_string_lossy()
                    .starts_with(".dupeforge-quarantine")
            })
            .unwrap();
        assert_eq!(fs::read(quarantine).unwrap(), b"replacement");
    }

    #[test]
    fn failed_quarantine_removal_restores_candidate() {
        let f = Fixture::new();
        let keeper = f.put("a", b"same");
        let candidate = f.put("b", b"same");
        let error = delete_candidate(
            &keeper,
            &candidate,
            &mut fmtools_fs::move_noclobber,
            &mut |_| {
                Err(std::io::Error::new(
                    std::io::ErrorKind::PermissionDenied,
                    "injected remove failure",
                ))
            },
        )
        .unwrap_err();
        assert!(error.to_string().contains("injected remove failure"));
        assert_eq!(fs::read(&candidate.path).unwrap(), b"same");
        assert_eq!(fs::read_dir(&f.0).unwrap().count(), 2);
    }
}
