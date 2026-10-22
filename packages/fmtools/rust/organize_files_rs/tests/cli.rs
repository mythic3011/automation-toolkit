use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::sync::atomic::{AtomicU64, Ordering};

struct Fixture(PathBuf);

impl Fixture {
    fn new() -> Self {
        static NEXT: AtomicU64 = AtomicU64::new(0);
        loop {
            let path = std::env::temp_dir().join(format!(
                "fmtools-organize-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            match fs::create_dir(&path) {
                Ok(()) => return Self(path),
                Err(error) if error.kind() == io::ErrorKind::AlreadyExists => continue,
                Err(error) => panic!("Cannot create test fixture: {error}"),
            }
        }
    }

    fn source(&self) -> PathBuf {
        let path = self.0.join("source");
        fs::create_dir_all(&path).unwrap();
        path
    }

    fn run(&self, source: &Path, args: &[&str]) -> Output {
        Command::new(env!("CARGO_BIN_EXE_organize_files"))
            .arg("--source")
            .arg(source)
            .args(args)
            .output()
            .unwrap()
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        assert!(self.0.starts_with(std::env::temp_dir()));
        let _ = fs::remove_dir_all(&self.0);
    }
}

#[test]
fn unsafe_category_names_are_rejected_before_moving() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("notes.txt"), "notes").unwrap();
    let config = fixture.0.join("categories.json");
    fs::write(&config, r#"{"categories":{"../escaped":[".txt"]}}"#).unwrap();
    let output = fixture.run(&source, &["--move", "--config", config.to_str().unwrap()]);
    assert!(!output.status.success(), "unsafe category was accepted");
    assert_eq!(fs::read(source.join("notes.txt")).unwrap(), b"notes");
    assert!(!fixture.0.join("escaped").exists());
}

#[test]
fn invalid_explicit_config_does_not_fall_back_to_defaults() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("notes.txt"), "notes").unwrap();
    let config = fixture.0.join("categories.json");
    fs::write(&config, "invalid json").unwrap();
    let output = fixture.run(&source, &["--move", "--config", config.to_str().unwrap()]);
    assert!(
        !output.status.success(),
        "invalid config silently used defaults"
    );
    assert!(source.join("notes.txt").exists());
    assert!(!source.join("Documents").exists());
}

#[test]
fn duplicate_extension_categories_are_rejected() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("notes.txt"), "notes").unwrap();
    let config = fixture.0.join("categories.json");
    fs::write(&config, r#"{"categories":{"A":[".txt"],"B":[".TXT"]}}"#).unwrap();
    assert!(!fixture
        .run(&source, &["--config", config.to_str().unwrap()])
        .status
        .success());
    assert_eq!(fs::read_dir(&source).unwrap().count(), 1);
}

#[test]
fn dry_run_reserves_exact_collision_destinations_without_writing() {
    let fixture = Fixture::new();
    let source = fixture.source();
    for folder in ["a", "b"] {
        fs::create_dir(source.join(folder)).unwrap();
        fs::write(source.join(folder).join("same.txt"), folder).unwrap();
    }
    let destination = fixture.0.join("output");
    let output = fixture.run(
        &source,
        &[
            "--dest",
            destination.to_str().unwrap(),
            "--recursive",
            "--move",
            "--dry-run",
        ],
    );
    assert!(output.status.success());
    let stdout = String::from_utf8(output.stdout).unwrap();
    assert!(
        stdout.contains(
            &destination
                .join("Documents")
                .join("same.txt")
                .display()
                .to_string()
        ),
        "{stdout}"
    );
    assert!(
        stdout.contains(
            &destination
                .join("Documents")
                .join("same_1.txt")
                .display()
                .to_string()
        ),
        "{stdout}"
    );
    assert!(!destination.exists());
    assert_eq!(fs::read(source.join("a/same.txt")).unwrap(), b"a");
    assert_eq!(fs::read(source.join("b/same.txt")).unwrap(), b"b");
}

#[test]
fn recursive_scan_excludes_the_nested_destination() {
    let fixture = Fixture::new();
    let source = fixture.source();
    let destination = source.join("sorted");
    fs::create_dir(&destination).unwrap();
    fs::write(destination.join("existing.txt"), "existing").unwrap();
    fs::write(source.join("new.txt"), "new").unwrap();
    let output = fixture.run(
        &source,
        &[
            "--dest",
            destination.to_str().unwrap(),
            "--recursive",
            "--move",
        ],
    );
    assert!(output.status.success());
    assert_eq!(
        fs::read(destination.join("existing.txt")).unwrap(),
        b"existing"
    );
    assert_eq!(
        fs::read(destination.join("Documents/new.txt")).unwrap(),
        b"new"
    );
}

#[test]
fn recursive_in_place_scan_preserves_existing_category_folders() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::create_dir(source.join("Images")).unwrap();
    fs::write(
        source.join("Images/readme.txt"),
        "keep with image collection",
    )
    .unwrap();
    fs::write(source.join("new.txt"), "new").unwrap();
    assert!(fixture
        .run(&source, &["--recursive", "--move"])
        .status
        .success());
    assert!(source.join("Images/readme.txt").exists());
    assert!(source.join("Documents/new.txt").exists());
}

#[test]
fn protected_files_and_webpage_resources_stay_together() {
    let fixture = Fixture::new();
    let source = fixture.source();
    for name in [
        "desktop.ini",
        "~$book.docx",
        "unfinished.zip.crdownload",
        ".settings",
        "SAVE.htm",
    ] {
        fs::write(source.join(name), name).unwrap();
    }
    fs::create_dir(source.join("SAVE_files")).unwrap();
    fs::write(source.join("SAVE_files/image.png"), "asset").unwrap();
    fs::write(source.join("new.pdf"), "pdf").unwrap();
    assert!(fixture
        .run(&source, &["--recursive", "--move"])
        .status
        .success());
    for name in [
        "desktop.ini",
        "~$book.docx",
        "unfinished.zip.crdownload",
        ".settings",
        "SAVE.htm",
        "SAVE_files/image.png",
    ] {
        assert!(source.join(name).is_file(), "protected file moved: {name}");
    }
    assert_eq!(fs::read(source.join("Documents/new.pdf")).unwrap(), b"pdf");
}

#[test]
fn mixed_case_page_and_resource_names_stay_together() {
    let fixture = Fixture::new();
    let source = fixture.source();
    let resources = source.join(if cfg!(windows) {
        "page_FILES"
    } else {
        "page_files"
    });
    fs::write(source.join("page.HtMl"), "page").unwrap();
    fs::create_dir(&resources).unwrap();
    fs::write(resources.join("asset.png"), "asset").unwrap();
    assert!(fixture
        .run(&source, &["--recursive", "--move"])
        .status
        .success());
    assert_eq!(fs::read(source.join("page.HtMl")).unwrap(), b"page");
    assert_eq!(fs::read(resources.join("asset.png")).unwrap(), b"asset");
}

#[test]
fn size_mode_uses_a_windows_safe_folder_name() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("tiny.txt"), "tiny").unwrap();
    let output = fixture.run(&source, &["--mode", "size", "--move"]);
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(fs::read(source.join("Tiny/tiny.txt")).unwrap(), b"tiny");
}

#[test]
fn failed_file_operations_produce_a_failure_exit_status() {
    let fixture = Fixture::new();
    let source = fixture.source();
    let destination = fixture.0.join("output");
    fs::create_dir(&destination).unwrap();
    fs::write(destination.join("Documents"), "blocked").unwrap();
    fs::write(source.join("notes.txt"), "notes").unwrap();
    let output = fixture.run(
        &source,
        &["--dest", destination.to_str().unwrap(), "--move"],
    );
    assert!(
        !output.status.success(),
        "failed operation reported success"
    );
    assert_eq!(fs::read(source.join("notes.txt")).unwrap(), b"notes");
    assert_eq!(fs::read(destination.join("Documents")).unwrap(), b"blocked");
}

#[test]
fn exact_exclusions_are_preserved() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("keep.txt"), "keep").unwrap();
    fs::write(source.join("move.txt"), "move").unwrap();
    assert!(fixture
        .run(&source, &["--move", "--exclude", "keep.txt"])
        .status
        .success());
    assert!(source.join("keep.txt").exists());
    assert!(source.join("Documents/move.txt").exists());
}

#[test]
fn report_records_exact_destinations_and_preserves_conflicts() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("notes.txt"), "new notes").unwrap();
    fs::create_dir(source.join("Documents")).unwrap();
    fs::write(source.join("Documents/notes.txt"), "old notes").unwrap();
    let report = fixture.0.join("moves.jsonl");
    let output = fixture.run(&source, &["--move", "--report", report.to_str().unwrap()]);
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let records: Vec<serde_json::Value> = fs::read_to_string(report)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    let moved = records
        .iter()
        .find(|record| record["status"] == "moved")
        .unwrap();
    assert_eq!(
        moved["source"],
        source.join("notes.txt").display().to_string()
    );
    assert_eq!(
        moved["destination"],
        source
            .join("Documents")
            .join("notes_1.txt")
            .display()
            .to_string()
    );
    assert!(records.iter().any(|record| record["status"] == "pending"));
    assert_eq!(
        fs::read(source.join("Documents/notes.txt")).unwrap(),
        b"old notes"
    );
    assert_eq!(
        fs::read(source.join("Documents/notes_1.txt")).unwrap(),
        b"new notes"
    );
}

#[test]
fn existing_report_is_not_overwritten_and_blocks_moves() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("notes.txt"), "notes").unwrap();
    let report = fixture.0.join("moves.jsonl");
    fs::write(&report, "old report").unwrap();
    assert!(!fixture
        .run(&source, &["--move", "--report", report.to_str().unwrap()])
        .status
        .success());
    assert_eq!(fs::read(report).unwrap(), b"old report");
    assert!(source.join("notes.txt").exists());
}

#[test]
fn a_dry_run_journal_records_planned_moves_without_changing_sources() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("notes.txt"), "notes").unwrap();
    let report = source.join("preview.jsonl");
    let output = fixture.run(
        &source,
        &["--move", "--dry-run", "--report", report.to_str().unwrap()],
    );
    assert!(output.status.success());
    let records: Vec<serde_json::Value> = fs::read_to_string(report)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(records.len(), 1);
    assert_eq!(records[0]["status"], "planned");
    assert_eq!(
        records[0]["destination"],
        source
            .join("Documents")
            .join("notes.txt")
            .display()
            .to_string()
    );
    assert_eq!(fs::read(source.join("notes.txt")).unwrap(), b"notes");
    assert!(!source.join("Documents").exists());
}

#[test]
fn category_config_inside_the_source_is_not_organized() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("notes.txt"), "notes").unwrap();
    let config = source.join("categories.json");
    let config_bytes = r#"{"categories":{"Text":[".txt"]}}"#;
    fs::write(&config, config_bytes).unwrap();
    assert!(fixture
        .run(&source, &["--move", "--config", config.to_str().unwrap()])
        .status
        .success());
    assert_eq!(fs::read(config).unwrap(), config_bytes.as_bytes());
    assert_eq!(fs::read(source.join("Text/notes.txt")).unwrap(), b"notes");
}

#[cfg(windows)]
#[test]
fn existing_categories_are_recognized_without_case_sensitivity() {
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::create_dir(source.join("other")).unwrap();
    fs::write(source.join("other/collection.txt"), "collection").unwrap();
    fs::write(source.join("new.txt"), "new").unwrap();
    assert!(fixture
        .run(&source, &["--recursive", "--move"])
        .status
        .success());
    assert!(source.join("other/collection.txt").exists());
    assert_eq!(fs::read(source.join("Documents/new.txt")).unwrap(), b"new");
}

#[cfg(unix)]
#[test]
fn category_symlinks_cannot_redirect_output() {
    let fixture = Fixture::new();
    let source = fixture.source();
    let outside = fixture.0.join("outside");
    fs::create_dir(&outside).unwrap();
    std::os::unix::fs::symlink(&outside, source.join("Documents")).unwrap();
    fs::write(source.join("notes.txt"), "notes").unwrap();
    assert!(!fixture.run(&source, &["--move"]).status.success());
    assert_eq!(fs::read(source.join("notes.txt")).unwrap(), b"notes");
    assert_eq!(fs::read_dir(outside).unwrap().count(), 0);
}

#[cfg(windows)]
#[test]
fn a_locked_file_does_not_stop_other_files_and_is_reported_as_failure() {
    use std::os::windows::fs::OpenOptionsExt;
    let fixture = Fixture::new();
    let source = fixture.source();
    fs::write(source.join("locked.txt"), "locked").unwrap();
    fs::write(source.join("other.txt"), "other").unwrap();
    let guard = fs::OpenOptions::new()
        .read(true)
        .share_mode(1)
        .open(source.join("locked.txt"))
        .unwrap();
    let output = fixture.run(&source, &["--move"]);
    assert!(
        !output.status.success(),
        "locked operation reported success"
    );
    assert_eq!(fs::read(source.join("locked.txt")).unwrap(), b"locked");
    assert_eq!(
        fs::read(source.join("Documents/other.txt")).unwrap(),
        b"other"
    );
    drop(guard);
}

#[cfg(unix)]
#[test]
fn symlinks_are_not_copied_or_moved() {
    let fixture = Fixture::new();
    let source = fixture.source();
    let target = fixture.0.join("outside.txt");
    fs::write(&target, "outside").unwrap();
    std::os::unix::fs::symlink(&target, source.join("linked.txt")).unwrap();
    assert!(fixture.run(&source, &["--move"]).status.success());
    assert!(source.join("linked.txt").is_symlink());
    assert_eq!(fs::read(target).unwrap(), b"outside");
}
