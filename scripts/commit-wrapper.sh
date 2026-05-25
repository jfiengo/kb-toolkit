#!/usr/bin/env bash
# Commit helper for the vault repo (not kb-toolkit).
# Usage: commit-wrapper.sh "commit message"
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MESSAGE="${1:-}"
if [[ -z "$MESSAGE" ]]; then
  echo "usage: commit-wrapper.sh \"commit message\"" >&2
  exit 1
fi

uv run python -m kb_toolkit.config >/dev/null 2>&1 || {
  echo "error: could not load kb.config.yaml" >&2
  exit 1
}

VAULT_PATH="$(uv run python -c 'from kb_toolkit.config import load_config; print(load_config().vault_path)')"
AUTO_COMMIT="$(uv run python -c 'from kb_toolkit.config import load_config; print("true" if load_config().git.auto_commit else "false")')"

if [[ "$AUTO_COMMIT" != "true" ]]; then
  echo "git.auto_commit is false; skipping commit."
  exit 0
fi

if [[ ! -d "$VAULT_PATH/.git" ]]; then
  echo "error: no git repo at vault: $VAULT_PATH" >&2
  exit 1
fi

cd "$VAULT_PATH"
if [[ -z "$(git status --porcelain)" ]]; then
  echo "nothing to commit in vault"
  exit 0
fi

git add -A
git commit -m "$MESSAGE"
echo "committed: $MESSAGE"
