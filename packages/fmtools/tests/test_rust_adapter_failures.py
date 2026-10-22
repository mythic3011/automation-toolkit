import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fmtools import dedup, organize, rename
from fmtools.cli import create_parser


@pytest.fixture
def logger():
    return logging.getLogger("adapter-test")


@pytest.fixture
def config():
    return Mock(get=lambda key, default=None: default)


def test_organize_parser_accepts_repeatable_exclude_and_report():
    args = create_parser().parse_args([
        "organize", "--exclude", "cache", "--exclude", "nested/private.txt", "--report", "journal.jsonl"
    ])
    assert args.exclude == ["cache", "nested/private.txt"]
    assert args.report == "journal.jsonl"


def test_organize_forwards_rust_only_options(tmp_path, monkeypatch, config, logger):
    source = tmp_path / "source"
    source.mkdir()
    rust_path = tmp_path / "organize_files"
    monkeypatch.setattr(organize, "count_files_fast", lambda _path: 1)
    monkeypatch.setattr(organize, "should_use_rust", lambda **_kwargs: (True, "forced", rust_path))
    completed = SimpleNamespace(returncode=0)
    process = Mock(return_value=completed)
    monkeypatch.setattr(organize.subprocess, "run", process)
    args = SimpleNamespace(
        source=str(source), dest=None, mode="type", categories=None, move=False,
        recursive=False, dry_run=True, force_python=False, force_rust=False,
        exclude=["cache", "nested/private.txt"], report="journal.jsonl",
    )

    assert organize.run_organize(args, config, logger) == 0
    command = process.call_args.args[0]
    assert command.count("--exclude") == 2
    assert command[command.index("--exclude") + 1] == "cache"
    assert command[command.index("--exclude", command.index("--exclude") + 1) + 1] == "nested/private.txt"
    assert command[command.index("--report") + 1] == "journal.jsonl"
    assert "--dry-run" in command


def test_empty_report_argument_is_forwarded_instead_of_dropped(tmp_path, monkeypatch, config, logger):
    source = tmp_path / "source"
    source.mkdir()
    rust_path = tmp_path / "organize_files"
    monkeypatch.setattr(organize, "count_files_fast", lambda _path: 1)
    monkeypatch.setattr(organize, "should_use_rust", lambda **_kwargs: (True, "forced", rust_path))
    process = Mock(return_value=SimpleNamespace(returncode=2))
    monkeypatch.setattr(organize.subprocess, "run", process)
    args = SimpleNamespace(
        source=str(source), dest=None, mode="type", categories=None, move=False,
        recursive=False, dry_run=False, force_python=False, force_rust=False,
        exclude=[], report="",
    )

    assert organize.run_organize(args, config, logger) == 2
    command = process.call_args.args[0]
    assert command[command.index("--report") + 1] == ""


@pytest.mark.parametrize("force_python,rust_path", [(True, None), (False, None)])
def test_organize_rust_only_options_fail_clearly_without_rust(
    tmp_path, monkeypatch, config, logger, force_python, rust_path
):
    source = tmp_path / "source"
    source.mkdir()
    monkeypatch.setattr(organize, "count_files_fast", lambda _path: 1)
    monkeypatch.setattr(organize, "should_use_rust", lambda **_kwargs: (False, "unavailable", rust_path))
    python = Mock(side_effect=AssertionError("safety options were silently ignored"))
    monkeypatch.setattr(organize, "_run_python_organize", python)
    args = SimpleNamespace(
        source=str(source), dest=None, mode="type", categories=None, move=False,
        recursive=False, dry_run=False, force_python=force_python, force_rust=False,
        exclude=["important"], report=None,
    )

    assert organize.run_organize(args, config, logger) == 2
    python.assert_not_called()


def test_organize_rust_only_options_are_not_dropped_if_launch_fails(
    tmp_path, monkeypatch, config, logger
):
    source = tmp_path / "source"
    source.mkdir()
    monkeypatch.setattr(organize, "count_files_fast", lambda _path: 1)
    monkeypatch.setattr(organize, "should_use_rust", lambda **_kwargs: (True, "forced", Path("rust-tool")))
    monkeypatch.setattr(organize.subprocess, "run", Mock(side_effect=OSError("cannot launch")))
    python = Mock(side_effect=AssertionError("Rust-only safety options must not be dropped"))
    monkeypatch.setattr(organize, "_run_python_organize", python)
    args = SimpleNamespace(
        source=str(source), dest=None, mode="type", categories=None, move=False,
        recursive=False, dry_run=False, force_python=False, force_rust=False,
        exclude=["private"], report=None,
    )

    assert organize.run_organize(args, config, logger) == 1
    python.assert_not_called()


@pytest.mark.parametrize(
    "module,run,command_args,python_name",
    [
        (rename, "run_rename", {"extension": "txt", "prefix": "x_", "suffix": "", "padding": None, "start": None, "recursive": False, "dry_run": False, "force_python": False, "force_rust": True, "directory": "."}, "_run_python_rename"),
        (dedup, "run_dedup", {"directory": ".", "batch": True, "keep": "newest", "algorithm": "sha256", "min_size": 0, "workers": None, "dry_run": True, "force_python": False, "force_rust": True}, "_run_python_dedup"),
    ],
)
def test_rust_nonzero_exit_is_returned_without_python_retry(
    module, run, command_args, python_name, tmp_path, monkeypatch, config, logger
):
    if module is rename:
        command_args["directory"] = str(tmp_path)
    else:
        command_args["directory"] = str(tmp_path)
    monkeypatch.setattr(module, "count_files_fast", lambda _path: 10)
    rust_path = Path("rust-tool")
    monkeypatch.setattr(module, "should_use_rust", lambda **_kwargs: (True, "forced", rust_path))
    monkeypatch.setattr(module.subprocess, "run", Mock(return_value=SimpleNamespace(returncode=23)))
    python = Mock(side_effect=AssertionError("Rust failure must not repeat the operation in Python"))
    monkeypatch.setattr(module, python_name, python)

    args = SimpleNamespace(**command_args)
    assert getattr(module, run)(args, config, logger) == 23
    python.assert_not_called()


def test_organize_nonzero_exit_is_returned_without_python_retry(
    tmp_path, monkeypatch, config, logger
):
    source = tmp_path / "source"
    source.mkdir()
    monkeypatch.setattr(organize, "count_files_fast", lambda _path: 10)
    monkeypatch.setattr(organize, "should_use_rust", lambda **_kwargs: (True, "forced", Path("rust-tool")))
    monkeypatch.setattr(organize.subprocess, "run", Mock(return_value=SimpleNamespace(returncode=29)))
    python = Mock(side_effect=AssertionError("Rust failure must not repeat the operation in Python"))
    monkeypatch.setattr(organize, "_run_python_organize", python)
    args = SimpleNamespace(
        source=str(source), dest=None, mode="type", categories=None, move=True,
        recursive=True, dry_run=False, force_python=False, force_rust=True,
        exclude=[], report=None,
    )

    assert organize.run_organize(args, config, logger) == 29
    python.assert_not_called()


def test_dedup_forwards_zero_workers_and_negative_min_size_without_retry(
    tmp_path, monkeypatch, config, logger
):
    monkeypatch.setattr(dedup, "count_files_fast", lambda _path: 1)
    monkeypatch.setattr(dedup, "should_use_rust", lambda **_kwargs: (True, "forced", Path("rust-tool")))
    process = Mock(return_value=SimpleNamespace(returncode=2))
    monkeypatch.setattr(dedup.subprocess, "run", process)
    python = Mock(side_effect=AssertionError("Rust validation failure must not retry in Python"))
    monkeypatch.setattr(dedup, "_run_python_dedup", python)
    args = SimpleNamespace(
        directory=str(tmp_path), batch=True, keep="newest", algorithm="sha256",
        min_size=-1, workers=0, dry_run=True, force_python=False, force_rust=True,
    )

    assert dedup.run_dedup(args, config, logger) == 2
    command = process.call_args.args[0]
    assert command[command.index("--workers") + 1] == "0"
    assert command[command.index("--min-size") + 1] == "-1"
    python.assert_not_called()
