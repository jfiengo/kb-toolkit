"""Load and validate kb.config.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator

TOOLKIT_ROOT = Path(__file__).resolve().parents[2]


class Folders(BaseModel):
    inbox: str = "inbox"
    raw: str = "raw"
    wiki: str = "wiki"
    daily: str = "daily"
    archive: str = "archive"


class Agent(BaseModel):
    command: str = "claude"
    model: str = "claude-opus-4-7"


class Compile(BaseModel):
    schedule: str = "manual"
    never_delete: bool = True
    flag_contradictions: bool = True
    inbox_after_promotion: Literal["archive", "mark", "delete"] = "archive"


class Git(BaseModel):
    auto_commit: bool = True
    remote: str = "none"


class Search(BaseModel):
    provider: Literal["smart-connections", "open-connections", "none"] = "smart-connections"


class Mcp(BaseModel):
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8787


class KbConfig(BaseModel):
    vault_path: str
    folders: Folders = Field(default_factory=Folders)
    agent: Agent = Field(default_factory=Agent)
    compile: Compile = Field(default_factory=Compile)
    git: Git = Field(default_factory=Git)
    search: Search = Field(default_factory=Search)
    mcp: Mcp = Field(default_factory=Mcp)

    @field_validator("vault_path")
    @classmethod
    def expand_vault_path(cls, value: str) -> str:
        return str(Path(value).expanduser().resolve())

    def resolved_vault_path(self) -> Path:
        return Path(self.vault_path)

    def folder_path(self, name: Literal["inbox", "raw", "wiki", "daily", "archive"]) -> Path:
        return self.resolved_vault_path() / getattr(self.folders, name)

    def validate_vault_outside_toolkit(self, toolkit_root: Path | None = None) -> None:
        """Raise ValueError if vault_path is inside the toolkit repo."""
        root = (toolkit_root or TOOLKIT_ROOT).resolve()
        vault = self.resolved_vault_path()
        try:
            vault.relative_to(root)
        except ValueError:
            return
        msg = (
            f"vault_path ({vault}) must be OUTSIDE the kb-toolkit repo ({root}). "
            "Point vault_path to a separate folder for your notes."
        )
        raise ValueError(msg)


def default_config_path() -> Path:
    """Prefer kb.config.yaml in cwd, then toolkit root."""
    cwd_candidate = Path.cwd() / "kb.config.yaml"
    if cwd_candidate.is_file():
        return cwd_candidate
    root_candidate = TOOLKIT_ROOT / "kb.config.yaml"
    if root_candidate.is_file():
        return root_candidate
    return cwd_candidate


def load_config(path: str | Path | None = None) -> KbConfig:
    """Load kb.config.yaml, expand vault_path, and validate placement."""
    config_path = Path(path) if path else default_config_path()
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Config not found: {config_path}. "
            "Copy kb.config.example.yaml to kb.config.yaml and edit vault_path."
        )
    with config_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    config = KbConfig.model_validate(data)
    config.validate_vault_outside_toolkit()
    return config


def load_config_dict(path: str | Path | None = None) -> dict:
    """Load config and return a JSON-serializable dict (for setup.sh)."""
    return load_config(path).model_dump()


if __name__ == "__main__":
    import json
    import sys

    try:
        cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else None)
        print(json.dumps(cfg.model_dump(), indent=2))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
