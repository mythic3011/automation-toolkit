use std::fs;
use std::process::{Command, Stdio};
use std::time::{SystemTime, UNIX_EPOCH};

struct Fixture(std::path::PathBuf);

impl Fixture {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!(
            "dupeforge-cli-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&path).unwrap();
        fs::write(path.join("a"), b"duplicate").unwrap();
        fs::write(path.join("b"), b"duplicate").unwrap();
        Self(path)
    }

    fn run(&self, args: &[&str]) -> std::process::Output {
        Command::new(env!("CARGO_BIN_EXE_dupeforge-rs"))
            .arg(&self.0)
            .args(args)
            .stdin(Stdio::null())
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
fn batch_deletion_preserves_the_selected_keeper_and_unique_files() {
    let fixture = Fixture::new();
    fs::write(fixture.0.join("unique"), b"unique").unwrap();
    let output = fixture.run(&["--batch", "--keep", "first"]);
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(fs::read(fixture.0.join("a")).unwrap(), b"duplicate");
    assert_eq!(fs::read(fixture.0.join("unique")).unwrap(), b"unique");
    assert!(!fixture.0.join("b").exists());
    assert_eq!(fs::read_dir(&fixture.0).unwrap().count(), 2);
    assert!(String::from_utf8_lossy(&output.stdout).contains("Files deleted: 1"));
}

#[test]
fn zero_workers_fails_without_deleting_files() {
    let fixture = Fixture::new();
    let output = fixture.run(&["--workers", "0", "--batch"]);
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stderr).contains("workers must be greater than zero"));
    assert!(fixture.0.join("a").exists() && fixture.0.join("b").exists());
}

#[cfg(windows)]
#[test]
fn a_hash_read_failure_aborts_before_any_deletion() {
    use std::os::windows::fs::OpenOptionsExt;
    let fixture = Fixture::new();
    let guard = fs::OpenOptions::new()
        .read(true)
        .share_mode(0)
        .open(fixture.0.join("a"))
        .unwrap();
    let output = fixture.run(&["--batch"]);
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stderr).contains("Failed to hash"));
    drop(guard);
    assert_eq!(fs::read(fixture.0.join("a")).unwrap(), b"duplicate");
    assert_eq!(fs::read(fixture.0.join("b")).unwrap(), b"duplicate");
    assert_eq!(fs::read_dir(&fixture.0).unwrap().count(), 2);
}

#[test]
fn dry_run_with_closed_stdin_does_not_prompt_or_delete() {
    let dir = std::env::temp_dir().join(format!(
        "dupeforge-cli-{}-{}",
        std::process::id(),
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    fs::create_dir_all(&dir).unwrap();
    let a = dir.join("a");
    let b = dir.join("b");
    fs::write(&a, b"duplicate").unwrap();
    fs::write(&b, b"duplicate").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_dupeforge-rs"))
        .arg(&dir)
        .arg("--dry-run")
        .stdin(Stdio::null())
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(a.exists() && b.exists());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(!stdout.contains("Proceed with deletion?"));
    assert!(!stdout.contains("Delete "));
    fs::remove_dir_all(dir).unwrap();
}
