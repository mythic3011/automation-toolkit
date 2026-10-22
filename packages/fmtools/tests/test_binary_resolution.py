from pathlib import Path

from fmtools.utils import get_rust_binary_path


def test_rust_binary_resolver_does_not_select_x64_linux_binary_on_arm(monkeypatch):
    monkeypatch.setattr("fmtools.utils.platform.system", lambda: "Linux")
    monkeypatch.setattr("fmtools.utils.platform.machine", lambda: "aarch64")
    monkeypatch.setattr(Path, "is_file", lambda self: True)

    assert get_rust_binary_path("rename_files") is None


def test_rust_binary_resolver_does_not_guess_unknown_macos_architecture(monkeypatch):
    monkeypatch.setattr("fmtools.utils.platform.system", lambda: "Darwin")
    monkeypatch.setattr("fmtools.utils.platform.machine", lambda: "mips64")
    monkeypatch.setattr(Path, "is_file", lambda self: True)

    assert get_rust_binary_path("rename_files") is None
