//! File operations that preserve an existing destination.

use std::{fs, io, io::Write, path::Path};

/// Move a regular file without replacing any existing destination.
///
/// Uses the platform's atomic, exclusive rename operation. Cross-filesystem
/// moves and unsupported filesystems return an error and preserve the source.
pub fn move_noclobber(source: &Path, destination: &Path) -> io::Result<()> {
    require_regular_file(source)?;
    move_file(source, destination)
}

/// Copy a regular file into an exclusively created destination.
/// An incomplete output is removed when copying fails.
pub fn copy_noclobber(source: &Path, destination: &Path) -> io::Result<u64> {
    require_regular_file(source)?;
    let mut input = open_source(source)?;
    let metadata = input.metadata()?;
    if !regular_file(&metadata) {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Source is not a regular file",
        ));
    }
    let mut output = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(destination)?;
    let result: io::Result<u64> = (|| {
        let bytes = io::copy(&mut input, &mut output)?;
        output.flush()?;
        output.set_permissions(metadata.permissions())?;
        Ok(bytes)
    })();
    drop(output);
    if let Err(error) = result {
        if let Err(cleanup) = fs::remove_file(destination) {
            return Err(io::Error::new(
                error.kind(),
                format!(
                "Copy failed: {error}; incomplete output remains at {} (cleanup failed: {cleanup})",
                destination.display()
            ),
            ));
        }
        return Err(error);
    }
    result
}

fn require_regular_file(path: &Path) -> io::Result<()> {
    if !regular_file(&fs::symlink_metadata(path)?) {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Source must be a regular file, not a directory or symlink",
        ));
    }
    Ok(())
}

fn regular_file(metadata: &fs::Metadata) -> bool {
    #[cfg(windows)]
    {
        use std::os::windows::fs::MetadataExt;
        metadata.file_type().is_file() && metadata.file_attributes() & 0x400 == 0
    }
    #[cfg(not(windows))]
    {
        metadata.file_type().is_file()
    }
}

fn open_source(path: &Path) -> io::Result<fs::File> {
    let mut options = fs::OpenOptions::new();
    options.read(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK);
    }
    #[cfg(windows)]
    {
        use std::os::windows::fs::OpenOptionsExt;
        // Open the entry itself, so a symlink swap cannot redirect the read.
        // Deny concurrent writes/deletion while copying from the open handle.
        options.custom_flags(0x00200000).share_mode(1);
    }
    options.open(path)
}

#[cfg(windows)]
fn move_file(source: &Path, destination: &Path) -> io::Result<()> {
    use std::os::windows::ffi::OsStrExt;

    #[link(name = "Kernel32")]
    extern "system" {
        fn MoveFileExW(existing: *const u16, new: *const u16, flags: u32) -> i32;
    }

    // Canonicalize parents for long-path support, leaving the final entry
    // unresolved. Resolving the source itself could follow a replaced symlink.
    fn entry_path(path: &Path) -> io::Result<std::path::PathBuf> {
        let filename = path
            .file_name()
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "Missing filename"))?;
        let parent = path
            .parent()
            .filter(|path| !path.as_os_str().is_empty())
            .unwrap_or_else(|| Path::new("."));
        Ok(parent.canonicalize()?.join(filename))
    }
    let source = entry_path(source)?;
    let destination = entry_path(destination)?;
    let mut source_wide: Vec<u16> = source.as_os_str().encode_wide().collect();
    let mut destination_wide: Vec<u16> = destination.as_os_str().encode_wide().collect();
    if source_wide.contains(&0) || destination_wide.contains(&0) {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Paths cannot contain NUL characters",
        ));
    }
    source_wide.push(0);
    destination_wide.push(0);
    // SAFETY: Both vectors contain valid NUL-terminated UTF-16 paths, remain
    // alive throughout this synchronous call, and are never mutated by it.
    // Flags zero forbids replacing an existing entry or copying across volumes.
    if unsafe { MoveFileExW(source_wide.as_ptr(), destination_wide.as_ptr(), 0) } == 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(())
}

#[cfg(any(all(target_os = "linux", target_env = "gnu"), target_os = "macos"))]
fn move_file(source: &Path, destination: &Path) -> io::Result<()> {
    use std::{ffi::CString, os::unix::ffi::OsStrExt};
    let source = CString::new(source.as_os_str().as_bytes())?;
    let destination = CString::new(destination.as_os_str().as_bytes())?;
    // SAFETY: Both C strings are NUL-terminated and live for the call. The
    // exclusive flag prevents replacing any concurrently created destination.
    #[cfg(all(target_os = "linux", target_env = "gnu"))]
    let result = unsafe {
        // Avoid requiring the newer glibc renameat2 wrapper. Unsupported
        // kernels/filesystems return an error without a destructive fallback.
        libc::syscall(
            libc::SYS_renameat2,
            libc::AT_FDCWD,
            source.as_ptr(),
            libc::AT_FDCWD,
            destination.as_ptr(),
            libc::RENAME_NOREPLACE,
        )
    };
    #[cfg(target_os = "macos")]
    let result =
        unsafe { libc::renamex_np(source.as_ptr(), destination.as_ptr(), libc::RENAME_EXCL) };
    if result != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(())
}

#[cfg(not(any(
    windows,
    all(target_os = "linux", target_env = "gnu"),
    target_os = "macos"
)))]
fn move_file(_source: &Path, _destination: &Path) -> io::Result<()> {
    Err(io::Error::new(
        io::ErrorKind::Unsupported,
        "Atomic no-overwrite moves are not supported on this platform",
    ))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicU64, Ordering};

    struct Fixture(PathBuf);

    impl Fixture {
        fn new() -> Self {
            static NEXT: AtomicU64 = AtomicU64::new(0);
            loop {
                let path = std::env::temp_dir().join(format!(
                    "fmtools-fs-{}-{}",
                    std::process::id(),
                    NEXT.fetch_add(1, Ordering::Relaxed)
                ));
                match fs::create_dir(&path) {
                    Ok(()) => return Self(path),
                    Err(error) if error.kind() == io::ErrorKind::AlreadyExists => continue,
                    Err(error) => panic!("Cannot create fixture: {error}"),
                }
            }
        }
    }

    impl Drop for Fixture {
        fn drop(&mut self) {
            assert!(self.0.starts_with(std::env::temp_dir()));
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn move_preserves_an_existing_destination_and_source() {
        let fixture = Fixture::new();
        let source = fixture.0.join("source.txt");
        let destination = fixture.0.join("existing.txt");
        fs::write(&source, b"source bytes").unwrap();
        fs::write(&destination, b"existing bytes").unwrap();
        assert!(move_noclobber(&source, &destination).is_err());
        assert_eq!(fs::read(&source).unwrap(), b"source bytes");
        assert_eq!(fs::read(&destination).unwrap(), b"existing bytes");
    }

    #[test]
    fn copy_preserves_an_existing_destination_and_source() {
        let fixture = Fixture::new();
        let source = fixture.0.join("source.txt");
        let destination = fixture.0.join("existing.txt");
        fs::write(&source, b"source bytes").unwrap();
        fs::write(&destination, b"existing bytes").unwrap();
        assert!(copy_noclobber(&source, &destination).is_err());
        assert_eq!(fs::read(&source).unwrap(), b"source bytes");
        assert_eq!(fs::read(&destination).unwrap(), b"existing bytes");
    }

    #[test]
    fn move_to_an_empty_destination_preserves_metadata() {
        let fixture = Fixture::new();
        let source = fixture.0.join("source.txt");
        let destination = fixture.0.join("new.txt");
        fs::write(&source, b"source bytes").unwrap();
        let modified = fs::metadata(&source).unwrap().modified().unwrap();
        move_noclobber(&source, &destination).unwrap();
        assert!(!source.exists());
        assert_eq!(fs::read(&destination).unwrap(), b"source bytes");
        assert_eq!(
            fs::metadata(destination).unwrap().modified().unwrap(),
            modified
        );
    }

    #[test]
    fn copy_to_an_empty_destination_keeps_the_source() {
        let fixture = Fixture::new();
        let source = fixture.0.join("source.txt");
        let destination = fixture.0.join("new.txt");
        fs::write(&source, b"source bytes").unwrap();
        assert_eq!(copy_noclobber(&source, &destination).unwrap(), 12);
        assert_eq!(fs::read(&source).unwrap(), b"source bytes");
        assert_eq!(fs::read(destination).unwrap(), b"source bytes");
    }

    #[test]
    fn failed_move_keeps_the_source() {
        let fixture = Fixture::new();
        let source = fixture.0.join("source.txt");
        fs::write(&source, b"source bytes").unwrap();
        assert!(move_noclobber(&source, &fixture.0.join("missing/new.txt")).is_err());
        assert_eq!(fs::read(&source).unwrap(), b"source bytes");
    }

    #[test]
    fn directories_cannot_be_moved_as_files() {
        let fixture = Fixture::new();
        let source = fixture.0.join("directory");
        fs::create_dir(&source).unwrap();
        assert!(move_noclobber(&source, &fixture.0.join("new")).is_err());
        assert!(source.is_dir());
    }

    #[test]
    fn concurrent_moves_keep_the_losing_source_and_winning_bytes() {
        let fixture = Fixture::new();
        let first = fixture.0.join("first.txt");
        let second = fixture.0.join("second.txt");
        let destination = fixture.0.join("winner.txt");
        fs::write(&first, b"first").unwrap();
        fs::write(&second, b"second").unwrap();
        let barrier = std::sync::Arc::new(std::sync::Barrier::new(2));
        let results = std::thread::scope(|scope| {
            let run = |source: &Path| {
                let source = source.to_owned();
                let barrier = barrier.clone();
                let destination = &destination;
                scope.spawn(move || {
                    barrier.wait();
                    move_noclobber(&source, destination)
                })
            };
            let first_result = run(&first);
            let second_result = run(&second);
            (first_result.join().unwrap(), second_result.join().unwrap())
        });
        assert_ne!(results.0.is_ok(), results.1.is_ok());
        let (winner, loser, bytes) = if results.0.is_ok() {
            (&first, &second, b"first".as_slice())
        } else {
            (&second, &first, b"second".as_slice())
        };
        assert!(!winner.exists());
        assert!(loser.exists());
        assert_eq!(fs::read(destination).unwrap(), bytes);
    }

    #[cfg(unix)]
    #[test]
    fn symlink_sources_and_destinations_never_replace_their_targets() {
        let fixture = Fixture::new();
        let source = fixture.0.join("source.txt");
        let target = fixture.0.join("target.txt");
        let link = fixture.0.join("link.txt");
        let destination = fixture.0.join("destination.txt");
        fs::write(&source, b"source").unwrap();
        fs::write(&target, b"target").unwrap();
        std::os::unix::fs::symlink(&target, &link).unwrap();
        assert!(move_noclobber(&link, &destination).is_err());
        assert!(copy_noclobber(&link, &destination).is_err());
        assert!(move_noclobber(&source, &link).is_err());
        assert!(copy_noclobber(&source, &link).is_err());
        assert_eq!(fs::read(source).unwrap(), b"source");
        assert_eq!(fs::read(target).unwrap(), b"target");
        assert!(link.is_symlink());
        assert!(!destination.exists());
    }
}
