"""Vault note I/O helpers (used by MCP tools and tests)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import frontmatter

from kb_toolkit.config import KbConfig

MARKDOWN_SUFFIX = ".md"
VALID_FOLDERS = frozenset({"inbox", "raw", "wiki", "daily", "archive"})


def slugify(title: str) -> str:
    slug = title.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    return slug or "untitled"


def _resolve_note_path(vault: Path, path: str, config: KbConfig) -> Path:
    note_path = Path(path)
    if not note_path.is_absolute():
        note_path = vault / note_path
    note_path = note_path.resolve()
    vault_resolved = vault.resolve()
    if not str(note_path).startswith(str(vault_resolved)):
        raise ValueError(f"path must be inside vault: {path}")
    return note_path


def _folder_name(config: KbConfig, folder: str) -> str:
    key = folder.lower()
    if key not in VALID_FOLDERS:
        raise ValueError(f"folder must be one of {sorted(VALID_FOLDERS)}: {folder}")
    return getattr(config.folders, key)


def iter_notes(vault: Path, folder: str | None, config: KbConfig) -> list[Path]:
    if folder:
        roots = [vault / _folder_name(config, folder)]
    else:
        roots = [
            vault / config.folders.inbox,
            vault / config.folders.raw,
            vault / config.folders.wiki,
            vault / config.folders.daily,
            vault / config.folders.archive,
        ]
    notes: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob(f"*{MARKDOWN_SUFFIX}"):
            if path.is_file():
                notes.append(path)
    return sorted(notes)


def list_notes(vault: Path, config: KbConfig, folder: str | None = None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in iter_notes(vault, folder, config):
        post = frontmatter.load(path)
        rel = str(path.relative_to(vault))
        tags = post.metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        results.append(
            {
                "path": rel,
                "title": post.metadata.get("title") or path.stem,
                "tags": list(tags),
                "created": post.metadata.get("created"),
                "excerpt": (post.content or "")[:200].strip(),
            }
        )
    return results


def search_notes(
    vault: Path,
    config: KbConfig,
    query: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    query_lower = query.lower().strip()
    if not query_lower:
        return []
    hits: list[dict[str, Any]] = []
    for path in iter_notes(vault, None, config):
        post = frontmatter.load(path)
        haystack = f"{path.stem}\n{post.content}\n{post.metadata}".lower()
        if query_lower in haystack:
            rel = str(path.relative_to(vault))
            hits.append(
                {
                    "path": rel,
                    "title": post.metadata.get("title") or path.stem,
                    "score": haystack.count(query_lower),
                    "excerpt": _excerpt(post.content or "", query_lower),
                }
            )
        if len(hits) >= limit:
            break
    hits.sort(key=lambda h: h.get("score", 0), reverse=True)
    if config.search.provider in ("smart-connections", "open-connections"):
        for hit in hits:
            hit["semantic_note"] = (
                f"Lexical match only. Use Obsidian plugin '{config.search.provider}' "
                "for semantic search."
            )
    return hits[:limit]


def _excerpt(content: str, query: str, radius: int = 80) -> str:
    idx = content.lower().find(query)
    if idx < 0:
        return content[: radius * 2].strip()
    start = max(0, idx - radius)
    end = min(len(content), idx + len(query) + radius)
    return content[start:end].strip()


def create_note(
    vault: Path,
    config: KbConfig,
    title: str,
    body: str,
    folder: str = "inbox",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    folder_name = _folder_name(config, folder)
    slug = slugify(title)
    dest_dir = vault / folder_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{slug}{MARKDOWN_SUFFIX}"
    if dest.exists():
        raise FileExistsError(f"note already exists: {dest.relative_to(vault)}")

    tag_list = list(tags or [])
    metadata = {
        "title": title,
        "created": datetime.now(UTC).isoformat(),
        "tags": tag_list,
    }
    post = frontmatter.Post(body, **metadata)
    dest.write_text(frontmatter.dumps(post), encoding="utf-8")
    return {"path": str(dest.relative_to(vault)), "title": title, "tags": tag_list}


def update_note(
    vault: Path,
    config: KbConfig,
    path: str,
    body: str | None = None,
    tags_add: list[str] | None = None,
    tags_remove: list[str] | None = None,
) -> dict[str, Any]:
    note_path = _resolve_note_path(vault, path, config)
    if not note_path.is_file():
        raise FileNotFoundError(f"note not found: {path}")

    post = frontmatter.load(note_path)
    if body is not None:
        post.content = body

    tags = post.metadata.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    tag_set = set(tags)
    for tag in tags_add or []:
        tag_set.add(tag)
    for tag in tags_remove or []:
        tag_set.discard(tag)
    post.metadata["tags"] = sorted(tag_set)
    post.metadata["updated"] = datetime.now(UTC).isoformat()

    note_path.write_text(frontmatter.dumps(post), encoding="utf-8")
    return {
        "path": str(note_path.relative_to(vault)),
        "tags": post.metadata["tags"],
        "updated": post.metadata["updated"],
    }
