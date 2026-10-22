"""Behavior checks for archives consumed by Homebrew and Scoop."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile


spec = importlib.util.spec_from_file_location(
    "native_release", Path(__file__).resolve().parents[1] / "native_release.py"
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class NativeReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "packages/fmtools/rust"
        self.workspace.mkdir(parents=True)
        (self.workspace / "Cargo.toml").write_text(
            '[workspace.package]\nversion = "1.0.0"\n', encoding="utf-8"
        )
        (self.workspace / "Cargo.lock").write_text("version = 3\n", encoding="utf-8")
        (self.workspace / "tool/src").mkdir(parents=True)
        (self.workspace / "tool/src/main.rs").write_text("fn main() {}\n", encoding="utf-8")
        (self.root / "LICENSE").write_text("MIT\n", encoding="utf-8")
        (self.root / "README.md").write_text("Native file tools\n", encoding="utf-8")
        self.binaries = self.root / "binaries"
        self.binaries.mkdir()
        for binary in release.BINARIES:
            for suffix in ("", ".exe"):
                (self.binaries / (binary + suffix)).write_bytes((binary + " payload").encode())
        self.assets = self.root / "assets"

    def bundle(self, target="x86_64-pc-windows-msvc", output=None):
        return release.create_binary_archive(
            self.root, self.binaries, "1.0.0", target, output or self.assets
        )

    def test_windows_archive_exposes_all_four_executables_at_root(self):
        archive = self.bundle()
        with zipfile.ZipFile(archive) as package:
            self.assertEqual(
                set(package.namelist()), {name + ".exe" for name in release.BINARIES} | {"LICENSE"}
            )
            for binary in release.BINARIES:
                self.assertEqual(
                    package.read(binary + ".exe"), (self.binaries / (binary + ".exe")).read_bytes()
                )

    def test_unix_archive_preserves_executable_modes(self):
        archive = self.bundle("aarch64-apple-darwin")
        with tarfile.open(archive) as package:
            self.assertEqual(set(package.getnames()), set(release.BINARIES) | {"LICENSE"})
            for binary in release.BINARIES:
                self.assertEqual(package.getmember(binary).mode, 0o755)
            self.assertEqual(package.getmember("LICENSE").mode, 0o644)

    def test_missing_binary_does_not_leave_a_partial_archive(self):
        (self.binaries / "organize_files.exe").unlink()
        with self.assertRaises((FileNotFoundError, ValueError)):
            self.bundle()
        self.assertFalse(list(self.assets.glob("*")))

    def test_existing_release_archive_is_never_overwritten(self):
        archive = self.bundle()
        original = archive.read_bytes()
        (self.binaries / "rename_files.exe").write_bytes(b"changed")
        with self.assertRaises(FileExistsError):
            self.bundle()
        self.assertEqual(archive.read_bytes(), original)

    def test_binary_archives_are_reproducible(self):
        for target in ("x86_64-pc-windows-msvc", "x86_64-unknown-linux-gnu"):
            first = self.bundle(target)
            second = self.bundle(target, self.root / "again")
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_source_archive_has_workspace_and_lockfile_without_build_outputs(self):
        (self.workspace / "target/debug").mkdir(parents=True)
        (self.workspace / "target/debug/secret.rs").write_text("generated", encoding="utf-8")
        archive = release.create_source_archive(self.root, "1.0.0", self.assets)
        with tarfile.open(archive) as package:
            names = package.getnames()
            prefix = "automation-toolkit-1.0.0/"
            self.assertIn(prefix + "packages/fmtools/rust/Cargo.lock", names)
            self.assertIn(prefix + "packages/fmtools/rust/tool/src/main.rs", names)
            self.assertIn(prefix + "LICENSE", names)
            self.assertFalse(any("/target/" in name for name in names))
            self.assertFalse(any(name.startswith("/") or ".." in Path(name).parts for name in names))
        second = release.create_source_archive(self.root, "1.0.0", self.root / "source-again")
        self.assertEqual(archive.read_bytes(), second.read_bytes())

    def test_invalid_or_mismatched_versions_are_rejected(self):
        for version in ("../../other", "v1.0.0", "01.0.0", "1.0", "1.0.0\n", "2.0.0"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                release.validate_version(self.root, version)
        self.assertEqual(release.version_from_tag(self.root, "toolkit-v1.0.0"), "1.0.0")
        with self.assertRaises(ValueError):
            release.version_from_tag(self.root, "v1.0.0")

    def test_unknown_target_is_rejected_without_creating_an_archive(self):
        with self.assertRaises(ValueError):
            self.bundle("../../other")
        self.assertFalse(self.assets.exists())

    def test_installers_use_the_actual_source_and_windows_archive_hashes(self):
        windows = self.bundle()
        source = release.create_source_archive(self.root, "1.0.0", self.assets)
        output = self.root / "installers"
        release.write_installers("1.0.0", self.assets, output)
        manifest = json.loads((output / "bucket/automation-toolkit.json").read_text())
        self.assertEqual(manifest["architecture"]["64bit"]["hash"], hashlib.sha256(windows.read_bytes()).hexdigest())
        self.assertTrue(manifest["architecture"]["64bit"]["url"].endswith("/" + windows.name))
        self.assertEqual(set(manifest["bin"]), {name + ".exe" for name in release.BINARIES})
        formula = (output / "Formula/automation-toolkit.rb").read_text()
        self.assertIn(hashlib.sha256(source.read_bytes()).hexdigest(), formula)
        self.assertIn("/toolkit-v1.0.0/" + source.name, formula)
        self.assertIn('def fetch', formula)
        self.assertIn('std_cargo_fetch_args', formula)
        sums = (self.assets / "SHA256SUMS").read_text()
        for archive in (windows, source):
            self.assertIn(hashlib.sha256(archive.read_bytes()).hexdigest() + "  " + archive.name, sums)

    def test_incomplete_release_does_not_publish_installers(self):
        self.bundle()
        output = self.root / "installers"
        with self.assertRaises((FileNotFoundError, ValueError)):
            release.write_installers("1.0.0", self.assets, output)
        self.assertFalse(output.exists())
        self.assertFalse((self.assets / "SHA256SUMS").exists())


if __name__ == "__main__":
    unittest.main()
