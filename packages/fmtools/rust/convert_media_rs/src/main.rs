use anyhow::{bail, Context, Result};
use clap::Parser;
use indicatif::{ProgressBar, ProgressStyle};
use rayon::prelude::*;
use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(author, version, about = "Convert media files between formats with parallel processing", long_about = None)]
struct Args {
    /// Input directory containing media files
    #[arg(long)]
    input_dir: PathBuf,
    /// Output directory for converted files
    #[arg(long)]
    output_dir: PathBuf,
    /// Input file format
    #[arg(long, value_name = "FORMAT")]
    from: String,
    /// Output file format
    #[arg(long, value_name = "FORMAT")]
    to: String,
    /// Speed multiplication factor (1.0 = normal speed)
    #[arg(long, default_value = "1.0")]
    speed: f64,
    /// Output frames per second (default: auto from input)
    #[arg(long)]
    fps: Option<u32>,
    /// Quality preset for video encoding
    #[arg(long, value_parser = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"])]
    quality: Option<String>,
    /// Number of parallel workers (default: CPU count)
    #[arg(long)]
    workers: Option<usize>,
    /// Search recursively in subdirectories
    #[arg(long)]
    recursive: bool,
    /// Enable verbose logging
    #[arg(short, long)]
    verbose: bool,
}

fn normalize_format(format: &str) -> Result<String> {
    let value = format.strip_prefix('.').unwrap_or(format);
    if value.is_empty() || !value.bytes().all(|b| b.is_ascii_alphanumeric()) {
        bail!("invalid format '{format}': use a simple file extension");
    }
    Ok(value.to_ascii_lowercase())
}

fn validate_options(speed: f64, fps: Option<u32>, workers: Option<usize>) -> Result<()> {
    if !speed.is_finite() || speed <= 0.0 {
        bail!("speed must be a finite number greater than zero");
    }
    if fps == Some(0) {
        bail!("fps must be greater than zero");
    }
    if workers == Some(0) {
        bail!("workers must be greater than zero");
    }
    Ok(())
}

fn video_filter(format: &str, speed: f64, fps: Option<u32>) -> Result<Option<String>> {
    let mut filters = Vec::new();
    if (speed - 1.0).abs() > f64::EPSILON {
        filters.push(format!("setpts={:.12}*PTS", 1.0 / speed));
    }
    if format == "gif" {
        filters.push(format!(
            "fps={},scale=320:-1:flags=lanczos",
            fps.unwrap_or(10)
        ));
    } else if let Some(fps) = fps {
        filters.push(format!("fps={fps}"));
    }
    Ok((!filters.is_empty()).then(|| filters.join(",")))
}

fn audio_filter(speed: f64, format: &str) -> Result<Option<String>> {
    if (speed - 1.0).abs() <= f64::EPSILON || format == "gif" {
        return Ok(None);
    }
    if !matches!(format, "mp4" | "webm" | "avi") {
        bail!("speed adjustment for audio is unsupported for output format '{format}'");
    }
    // FFmpeg's atempo accepts factors from 0.5 through 2.0; chain factors for wider ranges.
    let mut remaining = speed;
    let mut factors = Vec::new();
    while remaining > 2.0 {
        factors.push("2.0".to_string());
        remaining /= 2.0;
    }
    while remaining < 0.5 {
        factors.push("0.5".to_string());
        remaining /= 0.5;
    }
    factors.push(format!("{remaining:.12}"));
    Ok(Some(
        factors
            .into_iter()
            .map(|f| format!("atempo={f}"))
            .collect::<Vec<_>>()
            .join(","),
    ))
}

fn find_media_files(
    directory: &Path,
    extension: &str,
    recursive: bool,
    excluded_tree: Option<&Path>,
) -> Result<Vec<PathBuf>> {
    let mut media_files = Vec::new();
    if recursive {
        let walker = WalkDir::new(directory)
            .follow_links(false)
            .into_iter()
            .filter_entry(|entry| {
                entry.path() == directory
                    || !excluded_tree.is_some_and(|tree| entry.path().starts_with(tree))
            });
        for entry in walker {
            let entry =
                entry.with_context(|| format!("Failed scanning {}", directory.display()))?;
            let path = entry.path();
            if entry.file_type().is_file() && extension_matches(path, extension) {
                media_files.push(path.to_path_buf());
            }
        }
    } else {
        for entry in fs::read_dir(directory)
            .with_context(|| format!("Failed reading {}", directory.display()))?
        {
            let entry = entry?;
            let path = entry.path();
            if entry.file_type()?.is_file() && extension_matches(&path, extension) {
                media_files.push(path);
            }
        }
    }
    media_files.sort();
    Ok(media_files)
}

fn extension_matches(path: &Path, extension: &str) -> bool {
    path.extension()
        .is_some_and(|ext| ext.to_string_lossy().eq_ignore_ascii_case(extension))
}

fn plan_outputs(
    output_dir: &Path,
    input_dir: &Path,
    inputs: &[PathBuf],
    extension: &str,
    recursive: bool,
) -> Result<Vec<(PathBuf, PathBuf)>> {
    let mut tasks = Vec::with_capacity(inputs.len());
    let mut destinations = HashSet::new();
    for input in inputs {
        let relative = input.strip_prefix(input_dir).with_context(|| {
            format!(
                "Input {} is outside {}",
                input.display(),
                input_dir.display()
            )
        })?;
        let parent = if recursive {
            relative.parent().unwrap_or(Path::new(""))
        } else {
            Path::new("")
        };
        let stem = input.file_stem().context("input has no file name")?;
        let output =
            output_dir
                .join(parent)
                .join(format!("{}.{}", stem.to_string_lossy(), extension));
        let key = destination_key(&output);
        if !destinations.insert(key) {
            bail!("multiple inputs map to output {}", output.display());
        }
        tasks.push((input.clone(), output));
    }
    Ok(tasks)
}

fn destination_key(path: &Path) -> String {
    let text = path.to_string_lossy();
    if cfg!(windows) {
        text.to_lowercase()
    } else {
        text.into_owned()
    }
}

fn temp_directory(parent: &Path) -> Result<PathBuf> {
    static NEXT_ID: AtomicU64 = AtomicU64::new(0);
    for _ in 0..1000 {
        let candidate = parent.join(format!(
            ".convert-media-{}-{}",
            std::process::id(),
            NEXT_ID.fetch_add(1, Ordering::Relaxed)
        ));
        match fs::create_dir(&candidate) {
            Ok(()) => return Ok(candidate),
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(e) => {
                return Err(e).with_context(|| {
                    format!(
                        "Failed creating temporary directory in {}",
                        parent.display()
                    )
                })
            }
        }
    }
    bail!(
        "could not allocate temporary output directory in {}",
        parent.display()
    )
}

fn convert_media_file(
    input_path: &Path,
    output_path: &Path,
    output_format: &str,
    speed_factor: f64,
    fps: Option<u32>,
    quality: Option<&str>,
) -> Result<()> {
    let parent = output_path.parent().context("output path has no parent")?;
    fs::create_dir_all(parent).with_context(|| format!("Failed to create {}", parent.display()))?;
    let temp_dir = temp_directory(parent)?;
    let temp_output = temp_dir.join(
        output_path
            .file_name()
            .context("output path has no file name")?,
    );
    let result = (|| -> Result<()> {
        let mut cmd = Command::new("ffmpeg");
        cmd.arg("-nostdin").arg("-i").arg(input_path);
        if let Some(filter) = video_filter(output_format, speed_factor, fps)? {
            cmd.arg("-vf").arg(filter);
        }
        if let Some(filter) = audio_filter(speed_factor, output_format)? {
            cmd.arg("-af").arg(filter);
        }
        if let Some(preset) = quality {
            cmd.arg("-preset").arg(preset);
        }
        match output_format {
            "mp4" => {
                cmd.args(["-c:v", "libx264", "-c:a", "aac"]);
            }
            "webm" => {
                cmd.args(["-c:v", "libvpx", "-c:a", "libvorbis"]);
            }
            "avi" => {
                cmd.args(["-c:v", "mpeg4"]);
            }
            "gif" => {}
            _ => {}
        }
        cmd.arg("-n")
            .arg(&temp_output)
            .stdout(Stdio::null())
            .stderr(Stdio::null());
        let status = cmd
            .status()
            .context("Failed to execute ffmpeg. Make sure ffmpeg is installed and in PATH")?;
        if !status.success() {
            bail!(
                "ffmpeg exited with status {status} for {}",
                input_path.display()
            );
        }
        if !temp_output.is_file() {
            bail!(
                "ffmpeg reported success but did not create an output for {}",
                input_path.display()
            );
        }
        fmtools_fs::move_noclobber(&temp_output, output_path).with_context(|| {
            format!(
                "Could not publish output {}; it may already exist",
                output_path.display()
            )
        })?;
        Ok(())
    })();
    let cleanup = fs::remove_dir_all(&temp_dir);
    if let Err(err) = cleanup {
        log::warn!(
            "Could not remove temporary directory {}: {err}",
            temp_dir.display()
        );
    }
    result
}

fn batch_convert_media(args: &Args) -> Result<(usize, usize)> {
    let input_dir = &args.input_dir;
    let output_dir = &args.output_dir;
    validate_options(args.speed, args.fps, args.workers)?;
    let input_format = normalize_format(&args.from)?;
    let output_format = normalize_format(&args.to)?;
    fs::create_dir_all(output_dir).with_context(|| {
        format!(
            "Failed to create output directory: {}",
            output_dir.display()
        )
    })?;
    let input_root = fs::canonicalize(input_dir)?;
    let output_root = fs::canonicalize(output_dir)?;
    if input_root == output_root {
        bail!("input and output directories must be different");
    }
    let excluded_tree = if output_root.starts_with(&input_root) {
        Some(output_root.as_path())
    } else {
        None
    };
    let media_files = find_media_files(&input_root, &input_format, args.recursive, excluded_tree)?;
    if media_files.is_empty() {
        println!("No {} files found in {}", input_format, input_dir.display());
        return Ok((0, 0));
    }
    println!(
        "Found {} {} files to convert",
        media_files.len(),
        input_format
    );
    let tasks = plan_outputs(
        &output_root,
        &input_root,
        &media_files,
        &output_format,
        args.recursive,
    )?;
    let mut keys = HashSet::new();
    for (input, output) in &tasks {
        let canonical_input = fs::canonicalize(input)?;
        let target_key = destination_key(output);
        if !keys.insert(target_key) {
            bail!("output collision at {}", output.display());
        }
        if canonical_input == *output {
            bail!(
                "input and output resolve to the same file: {}",
                input.display()
            );
        }
        if output.exists() {
            bail!("output already exists: {}", output.display());
        }
    }
    let pb = ProgressBar::new(tasks.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})",
            )?
            .progress_chars("#>-"),
    );
    let convert = || {
        tasks
            .par_iter()
            .map(|(input, output)| {
                let result = convert_media_file(
                    input,
                    output,
                    &output_format,
                    args.speed,
                    args.fps,
                    args.quality.as_deref(),
                );
                pb.inc(1);
                if let Err(ref error) = result {
                    eprintln!("Error converting {}: {error:#}", input.display());
                }
                result
            })
            .collect::<Vec<_>>()
    };
    let results = if let Some(workers) = args.workers {
        rayon::ThreadPoolBuilder::new()
            .num_threads(workers)
            .build()?
            .install(convert)
    } else {
        convert()
    };
    pb.finish_with_message("Conversion complete");
    let successful = results.iter().filter(|r| r.is_ok()).count();
    let failed = results.len() - successful;
    Ok((successful, failed))
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
    validate_options(args.speed, args.fps, args.workers)?;
    let from = normalize_format(&args.from)?;
    let to = normalize_format(&args.to)?;
    if !args.input_dir.is_dir() {
        bail!("{} is not a valid directory", args.input_dir.display());
    }
    println!("Converting {} files to {}", from, to);
    println!("Input directory: {}", args.input_dir.display());
    println!("Output directory: {}", args.output_dir.display());
    println!("Speed factor: {}x", args.speed);
    if let Some(fps) = args.fps {
        println!("Output FPS: {}", fps);
    }
    if let Some(quality) = &args.quality {
        println!("Quality: {}", quality);
    }
    if Command::new("ffmpeg").arg("-version").output().is_err() {
        bail!("ffmpeg not found. Please install ffmpeg and make sure it's in your PATH.");
    }
    let (successful, failed) = batch_convert_media(&args)?;
    println!("\n{}", "=".repeat(60));
    println!(
        "Conversion Summary:\nSuccessfully converted: {successful}\nFailed: {failed}\nTotal: {}",
        successful + failed
    );
    println!("{}", "=".repeat(60));
    if failed > 0 {
        bail!("{failed} media conversion(s) failed");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_are_normalized_and_reject_paths() {
        assert_eq!(normalize_format(".MP4").unwrap(), "mp4");
        assert!(normalize_format("../mp4").is_err());
        assert!(normalize_format("mp4/out").is_err());
    }

    #[test]
    fn recursive_outputs_preserve_relative_directories() {
        let inputs = vec![
            PathBuf::from("root/a/clip.mov"),
            PathBuf::from("root/b/clip.mov"),
        ];
        let planned =
            plan_outputs(Path::new("out"), Path::new("root"), &inputs, "mp4", true).unwrap();
        assert_eq!(planned[0].1, PathBuf::from("out/a/clip.mp4"));
        assert_eq!(planned[1].1, PathBuf::from("out/b/clip.mp4"));
    }

    #[test]
    fn nonrecursive_duplicate_stems_are_rejected_before_conversion() {
        let inputs = vec![
            PathBuf::from("root/clip.MOV"),
            PathBuf::from("root/clip.mov"),
        ];
        assert!(plan_outputs(Path::new("out"), Path::new("root"), &inputs, "mp4", false).is_err());
    }

    #[test]
    fn invalid_numeric_options_are_rejected() {
        assert!(validate_options(0.0, Some(0), Some(0)).is_err());
        assert!(validate_options(f64::NAN, None, None).is_err());
        assert!(validate_options(-1.0, None, None).is_err());
    }

    #[test]
    fn gif_filter_combines_speed_and_fps() {
        assert_eq!(
            video_filter("gif", 2.0, Some(20)).unwrap().as_deref(),
            Some("setpts=0.500000000000*PTS,fps=20,scale=320:-1:flags=lanczos")
        );
    }

    #[test]
    fn speed_adjustment_keeps_audio_in_sync_or_rejects_it() {
        assert_eq!(
            audio_filter(4.0, "mp4").unwrap().as_deref(),
            Some("atempo=2.0,atempo=2.000000000000")
        );
        assert!(audio_filter(2.0, "mkv").is_err());
    }
}
