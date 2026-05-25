#!/usr/bin/env bash
# Bootstrap the user's vault (separate repo, outside kb-toolkit).
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is required. Install from https://docs.astral.sh/uv/" >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "error: git is required." >&2
  exit 1
fi

echo "kb-toolkit setup"
echo "================"
uv sync --quiet
uv run python -m kb_toolkit.setup_vault "$@"
