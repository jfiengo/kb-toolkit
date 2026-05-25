#!/usr/bin/env bash
# Run a full compile: pre-commit -> agent -> post-commit.
set -euo pipefail

# Obsidian Shell Commands (and other GUI launchers) often omit Homebrew from PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is required." >&2
  exit 1
fi

uv sync --quiet

VAULT_PATH="$(uv run python -c 'from kb_toolkit.config import load_config; print(load_config().vault_path)')"
AGENT_CMD="$(uv run python -c 'from kb_toolkit.config import load_config; print(load_config().agent.command)')"
AGENT_MODEL="$(uv run python -c 'from kb_toolkit.config import load_config; print(load_config().agent.model)')"
SCHEDULE="$(uv run python -c 'from kb_toolkit.config import load_config; print(load_config().compile.schedule)')"

PROMPT_FILE="$ROOT/prompts/compile.md"
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "error: missing $PROMPT_FILE" >&2
  exit 1
fi

if [[ ! -d "$VAULT_PATH" ]]; then
  echo "error: vault not found: $VAULT_PATH (run ./scripts/setup.sh first)" >&2
  exit 1
fi

if [[ "$SCHEDULE" != "manual" ]]; then
  echo "compile.schedule is '$SCHEDULE'. To run on a schedule, add to crontab:"
  echo "  $SCHEDULE cd $ROOT && ./scripts/compile.sh"
fi

echo "Vault: $VAULT_PATH"
echo "Agent: $AGENT_CMD (model: $AGENT_MODEL)"

"$ROOT/scripts/commit-wrapper.sh" "pre-compile snapshot"

COMPILE_PROMPT="$(cat "$PROMPT_FILE")"

echo "Invoking compile agent..."
if command -v "$AGENT_CMD" >/dev/null 2>&1; then
  cd "$VAULT_PATH"
  # Redirect stdin from /dev/null so claude doesn't hang waiting on a
  # pipe/socket when launched by a GUI (Obsidian Shell Commands, Cursor, etc.).
  "$AGENT_CMD" \
    --model "$AGENT_MODEL" \
    --print \
    --dangerously-skip-permissions \
    "Working directory (vault): $VAULT_PATH

$COMPILE_PROMPT" </dev/null
  cd "$ROOT"
else
  echo "error: agent command not found: $AGENT_CMD" >&2
  exit 1
fi

TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
"$ROOT/scripts/commit-wrapper.sh" "compile: $TS"

echo "Compile finished."
