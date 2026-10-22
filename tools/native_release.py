#!/usr/bin/env python3
"""Package the native Rust tools and generate checksummed Homebrew/Scoop installers."""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import tarfile
import tomllib
import zipfile


REPOSITORY = "https://github.com/mythic3011/automation-toolkit"
BINARIES = ("dupeforge-rs", "rename_files", "organize_files", "convert_media")
TARGETS = (
    "x86_64-pc-windows-msvc",
    "x86_64-unknown-linux-gnu",
    "x86_64-apple-darwin",
    "aarch64-apple-darwin",
)
VERSION_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")


def _check_version(version):
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError("Expected a release version such as 1.0.0")


def validate_version(root, version):
    _check_version(version)
    workspace = Path(root) / "packages/fmtools/rust/Cargo.toml"
    with workspace.open("rb") as source:
        expected = tomllib.load(source)["workspace"]["package"]["version"]
    if version != expected:
        raise ValueError(f"Release version {version} differs from Rust workspace version {expected}")
    return version


def version_from_tag(root, tag):
    if not tag.startswith("toolkit-v"):
        raise ValueError("Native release tags must start with toolkit-v")
    return validate_version(root, tag.removeprefix("toolkit-v"))


def _read_regular(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise FileNotFoundError(f"Expected a regular release input: {path}")
    data = path.read_bytes()
    if not data:
        raise ValueError(f"Release input is empty: {path}")
    return data


def _write_archive(destination, entries):
    """Use fixed metadata and exclusive creation; never replace an existing asset."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with destination.open("xb") as output:
            created = True
            if destination.suffix == ".zip":
                with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                    for name, data, mode in entries:
                        entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                        entry.create_system = 3
                        entry.external_attr = (stat.S_IFREG | mode) << 16
                        entry.compress_type = zipfile.ZIP_DEFLATED
                        archive.writestr(entry, data)
            else:
                with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=0) as compressed:
                    with tarfile.open(fileobj=compressed, mode="w") as archive:
                        for name, data, mode in entries:
                            entry = tarfile.TarInfo(name)
                            entry.mode = mode
                            entry.size = len(data)
                            archive.addfile(entry, io.BytesIO(data))
    except BaseException:
        if created:
            destination.unlink(missing_ok=True)
        raise
    return destination


def create_binary_archive(root, binary_dir, version, target, output_dir):
    validate_version(root, version)
    if target not in TARGETS:
        raise ValueError(f"Unsupported release target: {target}")
    windows = target.endswith("windows-msvc")
    suffix = ".exe" if windows else ""
    entries = [
        (binary + suffix, _read_regular(Path(binary_dir) / (binary + suffix)), 0o755)
        for binary in BINARIES
    ]
    entries.append(("LICENSE", _read_regular(Path(root) / "LICENSE"), 0o644))
    extension = ".zip" if windows else ".tar.gz"
    destination = Path(output_dir) / f"automation-toolkit-{version}-{target}{extension}"
    return _write_archive(destination, entries)


def create_source_archive(root, version, output_dir):
    validate_version(root, version)
    root = Path(root)
    workspace = root / "packages/fmtools/rust"
    # Cargo sources and manifests are sufficient to build every workspace member.
    # Excluding target/ also prevents platform build output from leaking into releases.
    inputs = [root / "LICENSE", root / "README.md", workspace / "Cargo.lock"]
    inputs.extend(
        path
        for path in sorted(workspace.rglob("*"))
        if "target" not in path.relative_to(workspace).parts
        and path.suffix in (".rs", ".toml")
        and (path.is_file() or path.is_symlink())
    )
    prefix = f"automation-toolkit-{version}/"
    entries = [
        (prefix + path.relative_to(root).as_posix(), _read_regular(path), 0o644)
        for path in inputs
    ]
    destination = Path(output_dir) / f"automation-toolkit-{version}-source.tar.gz"
    return _write_archive(destination, entries)


def _sha256(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def _write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write(text)


def write_installers(version, assets_dir, output_root):
    _check_version(version)
    assets_dir, output_root = Path(assets_dir), Path(output_root)
    source = assets_dir / f"automation-toolkit-{version}-source.tar.gz"
    windows = assets_dir / f"automation-toolkit-{version}-x86_64-pc-windows-msvc.zip"
    for required in (source, windows):
        if not required.is_file() or required.is_symlink():
            raise FileNotFoundError(f"Missing completed release archive: {required}")
    download = f"{REPOSITORY}/releases/download/toolkit-v{version}"
    formula = f'''# Generated by tools/native_release.py from the release archives.
class AutomationToolkit < Formula
  desc "File organization, deduplication, renaming, and media conversion tools"
  homepage "{REPOSITORY}"
  url "{download}/{source.name}"
  version "{version}"
  sha256 "{_sha256(source)}"
  license "MIT"

  depends_on "rust" => :build

  def fetch
    system "cargo", "fetch", "--manifest-path=packages/fmtools/rust/Cargo.toml", *std_cargo_fetch_args
  end

  def install
    %w[dupeforge-rs rename_files_rs organize_files_rs convert_media_rs].each do |member|
      system "cargo", "install", *std_cargo_args(path: "packages/fmtools/rust/#{{member}}")
    end
  end

  def caveats
    <<~EOS
      Media conversion requires FFmpeg: brew install ffmpeg
      Commands: dupeforge-rs, rename_files, organize_files, convert_media
    EOS
  end

  test do
    %w[dupeforge-rs rename_files organize_files convert_media].each do |tool|
      assert_match "Usage:", shell_output("#{{bin}}/#{{tool}} --help")
    end
    (testpath/"input").mkpath
    (testpath/"input/note.txt").write("Homebrew smoke test\\n")
    system bin/"organize_files", "--source", testpath/"input",
                               "--dest", testpath/"sorted", "--dry-run"
    assert_path_exists testpath/"input/note.txt"
    refute_path_exists testpath/"sorted"
  end
end
'''
    manifest = {
        "version": version,
        "description": "File organization, deduplication, renaming, and media conversion tools",
        "homepage": REPOSITORY,
        "license": "MIT",
        "architecture": {"64bit": {"url": f"{download}/{windows.name}", "hash": _sha256(windows)}},
        "bin": [binary + ".exe" for binary in BINARIES],
        "suggest": {"FFmpeg for media conversion": "main/ffmpeg"},
        "checkver": {"url": REPOSITORY + "/releases", "regex": r"/releases/tag/toolkit-v([\d.]+)"},
        "autoupdate": {
            "architecture": {
                "64bit": {
                    "url": REPOSITORY + "/releases/download/toolkit-v$version/automation-toolkit-$version-x86_64-pc-windows-msvc.zip"
                }
            },
            "hash": {"url": "$baseurl/SHA256SUMS"},
        },
    }
    names = [source.name]
    names.extend(
        f"automation-toolkit-{version}-{target}" + (".zip" if target.endswith("windows-msvc") else ".tar.gz")
        for target in TARGETS
    )
    archives = [assets_dir / name for name in sorted(names) if (assets_dir / name).is_file()]
    checksums = "".join(f"{_sha256(archive)}  {archive.name}\n" for archive in archives)
    _write_text(output_root / "Formula/automation-toolkit.rb", formula)
    _write_text(output_root / "bucket/automation-toolkit.json", json.dumps(manifest, indent=4) + "\n")
    _write_text(assets_dir / "SHA256SUMS", checksums)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    version = commands.add_parser("version", help="Validate a native release tag")
    version.add_argument("tag")
    for name in ("bundle", "source", "manifests"):
        command = commands.add_parser(name)
        command.add_argument("--version", required=True)
        if name == "manifests":
            command.add_argument("--assets", type=Path, required=True)
            command.add_argument("--output-root", type=Path, default=Path.cwd())
        else:
            command.add_argument("--output", type=Path, required=True)
        if name == "bundle":
            command.add_argument("--target", choices=TARGETS, required=True)
            command.add_argument("--binary-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "version":
            print(version_from_tag(args.root, args.tag))
        elif args.command == "bundle":
            print(create_binary_archive(args.root, args.binary_dir, args.version, args.target, args.output))
        elif args.command == "source":
            print(create_source_archive(args.root, args.version, args.output))
        else:
            validate_version(args.root, args.version)
            write_installers(args.version, args.assets, args.output_root)
    except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError) as error:
        parser.exit(1, f"Release packaging failed: {error}\n")


if __name__ == "__main__":
    main()
