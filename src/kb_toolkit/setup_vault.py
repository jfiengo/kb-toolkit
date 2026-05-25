"""Vault bootstrap logic invoked by scripts/setup.sh."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from kb_toolkit.config import TOOLKIT_ROOT, KbConfig, default_config_path, load_config

TEMPLATE_DIR = TOOLKIT_ROOT / "templates"


def _render_template(template_path: Path, config: KbConfig) -> str:
    text = template_path.read_text(encoding="utf-8")
    replacements = {
        "folders.inbox": config.folders.inbox,
        "folders.raw": config.folders.raw,
        "folders.wiki": config.folders.wiki,
        "folders.daily": config.folders.daily,
        "folders.archive": config.folders.archive,
        "compile.inbox_after_promotion": config.compile.inbox_after_promotion,
        "compile.never_delete": str(config.compile.never_delete).lower(),
        "compile.flag_contradictions": str(config.compile.flag_contradictions).lower(),
        "agent.command": config.agent.command,
        "agent.model": config.agent.model,
    }
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", str(value))
    return text


def _copy_if_missing(src: Path, dst: Path, content: str | None = None) -> bool:
    if dst.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if content is not None:
        dst.write_text(content, encoding="utf-8")
    else:
        shutil.copy2(src, dst)
    return True


def bootstrap_vault(interactive: bool = True) -> KbConfig:
    config_path = default_config_path()
    if not config_path.is_file():
        shutil.copy2(TOOLKIT_ROOT / "kb.config.example.yaml", config_path)
        print(f"Created {config_path}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if interactive:
        current = raw.get("vault_path", "~/notes")
        answer = input(f"Vault path [{current}]: ").strip()
        if answer:
            raw["vault_path"] = answer
            config_path.write_text(yaml.dump(raw, default_flow_style=False), encoding="utf-8")

    config = load_config(config_path)
    vault = config.resolved_vault_path()
    vault.mkdir(parents=True, exist_ok=True)

    for folder in (
        config.folders.inbox,
        config.folders.raw,
        config.folders.wiki,
        config.folders.daily,
        config.folders.archive,
    ):
        (vault / folder).mkdir(parents=True, exist_ok=True)
        print(f"  folder: {vault / folder}")

    git_dir = vault / ".git"
    if not git_dir.exists():
        subprocess.run(["git", "init"], cwd=vault, check=True)
        print(f"Initialized git repo at {vault}")
    else:
        print(f"Git repo already exists at {vault}")

    remotes = subprocess.run(
        ["git", "remote"],
        cwd=vault,
        capture_output=True,
        text=True,
        check=False,
    )
    if config.git.remote == "none":
        for remote in (remotes.stdout or "").strip().splitlines():
            if remote:
                print(f"WARNING: vault has remote '{remote}' but config git.remote is 'none'.")
    elif config.git.remote != "none":
        existing = (remotes.stdout or "").strip()
        if config.git.remote not in existing:
            print(
                f"Note: git.remote is '{config.git.remote}' but not configured. "
                "Add your remote manually if desired."
            )

    gitignore_dst = vault / ".gitignore"
    if _copy_if_missing(TEMPLATE_DIR / "vault.gitignore", gitignore_dst):
        print(f"  wrote {gitignore_dst}")

    claude_template = TEMPLATE_DIR / "CLAUDE.md.template"
    claude_dst = vault / "CLAUDE.md"
    if claude_template.is_file():
        rendered = _render_template(claude_template, config)
        if _copy_if_missing(claude_template, claude_dst, content=rendered):
            print(f"  wrote {claude_dst}")
        else:
            print(f"  skipped {claude_dst} (already exists)")
    else:
        print(f"  skipped CLAUDE.md (template not found: {claude_template})")

    vault_config_dst = vault / "kb.config.yaml"
    if not vault_config_dst.exists():
        shutil.copy2(config_path, vault_config_dst)
        print(f"  wrote {vault_config_dst}")

    print(f"\nVault ready at {vault}")
    return config


def main() -> None:
    try:
        bootstrap_vault(interactive="--non-interactive" not in sys.argv)
    except Exception as exc:
        print(f"setup failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
