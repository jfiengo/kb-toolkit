"""Tests for kb_toolkit.config."""

from pathlib import Path

import pytest
import yaml

from kb_toolkit.config import KbConfig, load_config


def test_example_yaml_round_trip(tmp_path: Path) -> None:
    example = Path(__file__).resolve().parents[1] / "kb.config.example.yaml"
    data = yaml.safe_load(example.read_text(encoding="utf-8"))
    data["vault_path"] = str(tmp_path / "vault")
    config = KbConfig.model_validate(data)
    assert config.folders.inbox == "inbox"
    assert config.compile.never_delete is True
    assert config.git.remote == "none"
    assert config.search.provider == "smart-connections"


def test_vault_inside_toolkit_raises(tmp_path: Path) -> None:
    toolkit_root = Path(__file__).resolve().parents[1]
    nested = toolkit_root / "notes-nested"
    config = KbConfig(vault_path=str(nested))
    with pytest.raises(ValueError, match="OUTSIDE"):
        config.validate_vault_outside_toolkit(toolkit_root)


def test_vault_outside_toolkit_ok(tmp_path: Path) -> None:
    vault = tmp_path / "my-vault"
    config = KbConfig(vault_path=str(vault))
    toolkit_root = Path(__file__).resolve().parents[1]
    config.validate_vault_outside_toolkit(toolkit_root)


def test_load_config_from_file(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    cfg_file = tmp_path / "kb.config.yaml"
    cfg_file.write_text(
        yaml.dump({"vault_path": str(vault), "folders": {"inbox": "inbox"}}),
        encoding="utf-8",
    )
    config = load_config(cfg_file)
    assert config.resolved_vault_path() == vault.resolve()
