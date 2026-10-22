"""Configuration changes must stay local to the selected configuration file."""

from copy import deepcopy

import pytest

from fmtools import config as config_module
from fmtools.config import Config


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch, tmp_path):
    config_dir = tmp_path / "settings"
    config_dir.mkdir()
    monkeypatch.setattr(config_module, "get_config_dir", lambda: config_dir)
    # Keep the failing regression tests from contaminating other tests.
    monkeypatch.setattr(config_module, "DEFAULT_CONFIG", deepcopy(config_module.DEFAULT_CONFIG))


@pytest.mark.parametrize("initial_yaml", [None, "logging:\n  level: DEBUG\n", "[invalid yaml"])
def test_changes_do_not_modify_defaults(tmp_path, initial_yaml):
    config_file = tmp_path / "custom.yaml"
    if initial_yaml is not None:
        config_file.write_text(initial_yaml, encoding="utf-8")

    config = Config(config_file)
    config.set("defaults.dedup.keep", "first")

    assert config.get("defaults.dedup.keep") == "first"
    assert config_module.DEFAULT_CONFIG["defaults"]["dedup"]["keep"] == "newest"


def test_existing_instances_do_not_share_nested_settings(tmp_path):
    first = Config(tmp_path / "first.yaml")
    second = Config(tmp_path / "second.yaml")

    first.set("defaults.rename.padding", 8)

    assert first.get("defaults.rename.padding") == 8
    assert second.get("defaults.rename.padding") == 3


def test_reset_restores_original_defaults(tmp_path):
    config_file = tmp_path / "custom.yaml"
    config = Config(config_file)
    config.set("defaults.dedup.algorithm", "md5")

    config.reset()

    assert config.get("defaults.dedup.algorithm") == "sha256"
    assert Config(config_file).get("defaults.dedup.algorithm") == "sha256"


def test_reset_does_not_reintroduce_shared_settings(tmp_path):
    first = Config(tmp_path / "first.yaml")
    second = Config(tmp_path / "second.yaml")
    first.reset()

    first.set("defaults.organize.mode", "date")

    assert second.get("defaults.organize.mode") == "type"
    assert config_module.DEFAULT_CONFIG["defaults"]["organize"]["mode"] == "type"


def test_saved_settings_survive_loading_without_affecting_other_configs(tmp_path):
    config_file = tmp_path / "custom.yaml"
    config = Config(config_file)
    config.set("defaults.rename.padding", 5)

    loaded = Config(config_file)
    independent = Config(tmp_path / "other.yaml")

    assert loaded.get("defaults.rename.padding") == 5
    assert independent.get("defaults.rename.padding") == 3
