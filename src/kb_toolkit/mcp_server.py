"""MCP server for vault note access (stdio transport for Claude Desktop)."""

from __future__ import annotations

import sys
from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from kb_toolkit.config import KbConfig, load_config
from kb_toolkit.notes import create_note as _create_note
from kb_toolkit.notes import list_notes as _list_notes
from kb_toolkit.notes import search_notes as _search_notes
from kb_toolkit.notes import update_note as _update_note

mcp = FastMCP("kb-toolkit")


@lru_cache(maxsize=1)
def _get_config() -> KbConfig:
    return load_config()


def _vault():
    cfg = _get_config()
    return cfg.resolved_vault_path(), cfg


@mcp.tool()
def search_notes(query: str, limit: int = 20) -> list[dict]:
    """Search vault notes by lexical substring match.

    Args:
        query: Text to search for in titles and bodies.
        limit: Maximum number of results (default 20).
    """
    vault, config = _vault()
    return _search_notes(vault, config, query=query, limit=limit)


@mcp.tool()
def create_note(
    title: str,
    body: str,
    folder: str = "inbox",
    tags: list[str] | None = None,
) -> dict:
    """Create a new markdown note in the vault.

    Args:
        title: Note title (used for filename slug).
        body: Markdown body content (without frontmatter).
        folder: Target folder: inbox, raw, wiki, daily, or archive.
        tags: Optional list of tags for frontmatter.
    """
    vault, config = _vault()
    return _create_note(vault, config, title=title, body=body, folder=folder, tags=tags)


@mcp.tool()
def update_note(
    path: str,
    body: str | None = None,
    tags_add: list[str] | None = None,
    tags_remove: list[str] | None = None,
) -> dict:
    """Update an existing note, preserving frontmatter.

    Args:
        path: Path relative to vault root (e.g. inbox/my-note.md).
        body: New body content, or None to leave unchanged.
        tags_add: Tags to add to frontmatter.
        tags_remove: Tags to remove from frontmatter.
    """
    vault, config = _vault()
    return _update_note(
        vault,
        config,
        path=path,
        body=body,
        tags_add=tags_add,
        tags_remove=tags_remove,
    )


@mcp.tool()
def list_notes(folder: str | None = None) -> list[dict]:
    """List notes in the vault with frontmatter excerpts.

    Args:
        folder: Optional folder filter (inbox, raw, wiki, daily, archive).
    """
    vault, config = _vault()
    return _list_notes(vault, config, folder=folder)


def main() -> None:
    try:
        _get_config()
    except Exception as exc:
        print(f"kb-mcp config error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
