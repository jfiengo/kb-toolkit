"""Tests for vault note helpers (MCP tool backing logic)."""

from pathlib import Path

import pytest

from kb_toolkit.config import KbConfig
from kb_toolkit.notes import create_note, list_notes, search_notes, update_note


@pytest.fixture
def vault_config(tmp_path: Path) -> tuple[Path, KbConfig]:
    vault = tmp_path / "vault"
    for name in ("inbox", "raw", "wiki", "daily", "archive"):
        (vault / name).mkdir(parents=True)
    config = KbConfig(
        vault_path=str(vault),
        folders={
            "inbox": "inbox",
            "raw": "raw",
            "wiki": "wiki",
            "daily": "daily",
            "archive": "archive",
        },
    )
    return vault, config


def test_create_and_list(vault_config: tuple[Path, KbConfig]) -> None:
    vault, config = vault_config
    created = create_note(vault, config, title="Test Idea", body="Some content", tags=["idea"])
    assert created["path"] == "inbox/test-idea.md"

    notes = list_notes(vault, config, folder="inbox")
    assert len(notes) == 1
    assert notes[0]["title"] == "Test Idea"
    assert "idea" in notes[0]["tags"]


def test_search_lexical(vault_config: tuple[Path, KbConfig]) -> None:
    vault, config = vault_config
    create_note(vault, config, title="Python Tips", body="Use pathlib for paths")
    hits = search_notes(vault, config, query="pathlib", limit=5)
    assert len(hits) >= 1
    assert hits[0]["path"].endswith(".md")


def test_update_tags_and_body(vault_config: tuple[Path, KbConfig]) -> None:
    vault, config = vault_config
    created = create_note(vault, config, title="Update Me", body="original")
    updated = update_note(
        vault,
        config,
        path=created["path"],
        body="revised",
        tags_add=["done"],
    )
    assert "done" in updated["tags"]
    notes = list_notes(vault, config, folder="inbox")
    assert "revised" in notes[0]["excerpt"] or notes[0]["excerpt"] == "revised"


def test_create_refuses_overwrite(vault_config: tuple[Path, KbConfig]) -> None:
    vault, config = vault_config
    create_note(vault, config, title="Duplicate", body="a")
    with pytest.raises(FileExistsError):
        create_note(vault, config, title="Duplicate", body="b")
