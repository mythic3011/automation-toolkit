use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::sync::atomic::{AtomicU64, Ordering};

struct Fixture(PathBuf);

impl Fixture {
    fn new() -> Self {
        static NEXT_ID: AtomicU64 = AtomicU64::new(0);
        let path = env::temp_dir().join(format!(
            "convert-media-integration-{}-{}",
            std::process::id(),
            NEXT_ID.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&path).unwrap();
        Self(path)
    }

    fn path(&self) -> &Path {
        &self.0
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn ffmpeg_binary() -> Option<PathBuf> {
    if let Some(path) = env::var_os("FMTOOLS_FFMPEG") {
        let path = PathBuf::from(path);
        if path.is_file() {
            return Some(path);
        }
    }
    let executable = if cfg!(windows) {
        "ffmpeg.exe"
    } else {
        "ffmpeg"
    };
    env::split_paths(&env::var_os("PATH")?)
        .map(|p| p.join(executable))
        .find(|p| p.is_file())
}

fn setup_ffmpeg_path(fixture: &Fixture, ffmpeg: &Path) -> Option<std::ffi::OsString> {
    let bin_dir = fixture.path().join("bin");
    fs::create_dir(&bin_dir).ok()?;
    let alias = bin_dir.join(if cfg!(windows) {
        "ffmpeg.exe"
    } else {
        "ffmpeg"
    });
    if fs::hard_link(ffmpeg, &alias).is_err() {
        fs::copy(ffmpeg, &alias).ok()?;
    }
    let mut paths = vec![bin_dir];
    if let Some(existing) = env::var_os("PATH") {
        paths.extend(env::split_paths(&existing));
    }
    env::join_paths(paths).ok()
}

fn make_video(ffmpeg: &Path, path: &Path) {
    fs::create_dir_all(path.parent().unwrap()).unwrap();
    let output = Command::new(ffmpeg)
        .args([
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=red:s=32x32:d=0.4:r=12",
            "-an",
            "-c:v",
            "mpeg4",
            "-y",
        ])
        .arg(path)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "could not generate video fixture: {}",
        String::from_utf8_lossy(&output.stderr)
    );
}

fn run_cli(path: &std::ffi::OsStr, input: &Path, output: &Path, extra: &[&str]) -> Output {
    let mut cmd = Command::new(env!("CARGO_BIN_EXE_convert_media"));
    cmd.args([
        "--input-dir",
        input.to_str().unwrap(),
        "--output-dir",
        output.to_str().unwrap(),
        "--from",
        "avi",
        "--to",
        "mp4",
    ])
    .args(extra)
    .env("PATH", path)
    .output()
    .unwrap()
}

#[test]
fn cli_preserves_recursive_names_and_never_replaces_existing_outputs() {
    let Some(ffmpeg) = ffmpeg_binary() else {
        eprintln!("skipping FFmpeg CLI integration test: ffmpeg unavailable");
        return;
    };
    let fixture = Fixture::new();
    let path =
        setup_ffmpeg_path(&fixture, &ffmpeg).expect("could not prepare per-process ffmpeg PATH");
    let input = fixture.path().join("input");
    make_video(&ffmpeg, &input.join("a/clip.avi"));
    make_video(&ffmpeg, &input.join("b/clip.avi"));

    let output = fixture.path().join("output");
    let result = run_cli(path.as_os_str(), &input, &output, &["--recursive"]);
    assert!(
        result.status.success(),
        "CLI failed: {}",
        String::from_utf8_lossy(&result.stderr)
    );
    assert!(output.join("a/clip.mp4").is_file());
    assert!(output.join("b/clip.mp4").is_file());

    let sentinel_dir = fixture.path().join("occupied").join("a");
    fs::create_dir_all(&sentinel_dir).unwrap();
    let sentinel = b"keep this existing output";
    fs::write(sentinel_dir.join("clip.mp4"), sentinel).unwrap();
    let result = run_cli(
        path.as_os_str(),
        &input,
        &fixture.path().join("occupied"),
        &["--recursive"],
    );
    assert!(
        !result.status.success(),
        "occupied output unexpectedly succeeded"
    );
    assert_eq!(fs::read(sentinel_dir.join("clip.mp4")).unwrap(), sentinel);
}

#[test]
fn cli_reports_failed_conversion_and_cleans_its_temporary_output() {
    let Some(ffmpeg) = ffmpeg_binary() else {
        eprintln!("skipping FFmpeg CLI integration test: ffmpeg unavailable");
        return;
    };
    let fixture = Fixture::new();
    let path =
        setup_ffmpeg_path(&fixture, &ffmpeg).expect("could not prepare per-process ffmpeg PATH");
    let input = fixture.path().join("input");
    fs::create_dir_all(&input).unwrap();
    fs::write(input.join("broken.avi"), b"not a video").unwrap();
    let output = fixture.path().join("output");
    let result = run_cli(path.as_os_str(), &input, &output, &[]);
    assert!(
        !result.status.success(),
        "failed conversion returned success"
    );
    assert!(!output.join("broken.mp4").exists());
    let leftovers = fs::read_dir(&output)
        .unwrap()
        .filter_map(Result::ok)
        .any(|entry| {
            entry
                .file_name()
                .to_string_lossy()
                .starts_with(".convert-media-")
        });
    assert!(
        !leftovers,
        "failed conversion left an owned temporary directory"
    );
}

#[test]
fn cli_applies_speed_and_fps_when_creating_gif() {
    let Some(ffmpeg) = ffmpeg_binary() else {
        eprintln!("skipping FFmpeg CLI integration test: ffmpeg unavailable");
        return;
    };
    let fixture = Fixture::new();
    let path =
        setup_ffmpeg_path(&fixture, &ffmpeg).expect("could not prepare per-process ffmpeg PATH");
    let input = fixture.path().join("input");
    make_video(&ffmpeg, &input.join("clip.avi"));
    let output = fixture.path().join("gif");
    let mut cmd = Command::new(env!("CARGO_BIN_EXE_convert_media"));
    let result = cmd
        .args([
            "--input-dir",
            input.to_str().unwrap(),
            "--output-dir",
            output.to_str().unwrap(),
            "--from",
            "avi",
            "--to",
            "gif",
            "--speed",
            "2",
            "--fps",
            "20",
        ])
        .env("PATH", path)
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "GIF conversion failed: {}",
        String::from_utf8_lossy(&result.stderr)
    );
    assert!(output.join("clip.gif").is_file());
}
