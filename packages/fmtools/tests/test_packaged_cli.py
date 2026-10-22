"""Regression coverage for commands shipped in the fmtools wheel."""

import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def installed_wheel(tmp_path_factory):
    workspace = tmp_path_factory.mktemp("fmtools-wheel")
    wheelhouse = workspace / "wheelhouse"
    wheelhouse.mkdir()
    install_dir = workspace / "installed"
    install_dir.mkdir()

    build_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            str(PACKAGE_ROOT),
            "--no-isolation",
            "--wheel",
            "--outdir",
            str(wheelhouse),
        ],
        cwd=workspace,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0, build_result.stdout + build_result.stderr
    wheel_path = next(wheelhouse.glob("fmtools-*.whl"))
    with zipfile.ZipFile(wheel_path) as wheel:
        wheel.extractall(install_dir)

    return workspace, install_dir


def _run_cli(installed_wheel, cwd, *arguments):
    workspace, install_dir = installed_wheel
    config_path = workspace / "test-config.json"
    config_path.write_text("{}", encoding="utf-8")
    command_log = cwd / "fmtools.log"
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONPATH"] = str(install_dir)
    package_path = subprocess.run(
        [sys.executable, "-c", "import fmtools; print(fmtools.__file__)"],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert install_dir in Path(package_path).parents
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fmtools",
            "--config",
            str(config_path),
            "--log-file",
            str(command_log),
            *map(str, arguments),
        ],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def test_file_commands_run_from_wheel_without_checkout_scripts(installed_wheel, tmp_path):
    cwd = tmp_path / "unrelated-working-directory"
    cwd.mkdir()
    fixture = tmp_path / "fixture"
    fixture.mkdir()

    duplicate_dir = fixture / "duplicates"
    duplicate_dir.mkdir()
    (duplicate_dir / "first.bin").write_bytes(b"same contents")
    (duplicate_dir / "second.bin").write_bytes(b"same contents")

    rename_dir = fixture / "rename"
    rename_dir.mkdir()
    (rename_dir / "photo.txt").write_text("photo", encoding="utf-8")

    organize_source = fixture / "organize-source"
    organize_source.mkdir()
    (organize_source / "notes.txt").write_text("notes", encoding="utf-8")
    organize_dest = fixture / "organize-dest"

    clean_dir = fixture / "clean"
    clean_dir.mkdir()
    empty_dir = clean_dir / "empty"
    empty_dir.mkdir()

    stats_dir = fixture / "stats"
    stats_dir.mkdir()
    (stats_dir / "report.txt").write_text("report", encoding="utf-8")
    stats_json = fixture / "stats.json"

    commands = [
        ("dedup", str(duplicate_dir), "--batch", "--dry-run", "--force-python"),
        (
            "rename",
            "--directory",
            str(rename_dir),
            "--extension",
            ".txt",
            "--dry-run",
            "--force-python",
        ),
        (
            "organize",
            "--source",
            str(organize_source),
            "--dest",
            str(organize_dest),
            "--dry-run",
            "--force-python",
        ),
        ("clean", "--directory", str(clean_dir), "--dry-run"),
        ("stats", "--directory", str(stats_dir), "--export-json", str(stats_json)),
    ]

    for command in commands:
        _run_cli(installed_wheel, cwd, *command)

    assert sorted(path.name for path in duplicate_dir.iterdir()) == [
        "first.bin",
        "second.bin",
    ]
    assert (rename_dir / "photo.txt").exists()
    assert not (rename_dir / "001_photo.txt").exists()
    assert (organize_source / "notes.txt").exists()
    assert not organize_dest.exists()
    assert empty_dir.is_dir()
    assert stats_json.is_file()
    assert {path.name for path in cwd.glob("*.log")} == {"fmtools.log"}


def test_built_rust_binaries_are_packaged_and_discoverable(installed_wheel, tmp_path):
    workspace, install_dir = installed_wheel
    source_bin = PACKAGE_ROOT / "src" / "fmtools" / "bin" / "windows"
    binaries = list(source_bin.glob("*.exe")) if source_bin.is_dir() else []
    if not binaries:
        pytest.skip("No Windows Rust binaries have been built in this checkout")

    installed_bin = install_dir / "fmtools" / "bin" / "windows"
    for source_binary in binaries:
        packaged_binary = installed_bin / source_binary.name
        assert packaged_binary.is_file()
        assert packaged_binary.read_bytes() == source_binary.read_bytes()

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONPATH"] = str(install_dir)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import platform; "
                "from fmtools.utils import get_rust_binary_path; "
                "platform.system = lambda: 'Windows'; "
                "platform.machine = lambda: 'AMD64'; "
                "path = get_rust_binary_path('rename_files'); "
                "assert path is not None and path.is_file(), path"
            ),
        ],
        cwd=workspace,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "script_name",
    [
        "delete_duplicates.py",
        "rename.py",
        "organize_files.py",
        "clean_empty_dirs.py",
        "file_stats.py",
        "convert_media.py",
        "speed.py",
    ],
)
def test_legacy_script_entrypoints_still_show_help(script_name, tmp_path):
    result = subprocess.run(
        [sys.executable, str(PACKAGE_ROOT / "scripts" / script_name), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "usage:" in result.stdout.lower()
    assert not list(tmp_path.glob("*.log"))
