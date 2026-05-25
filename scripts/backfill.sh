#!/usr/bin/env bash
# One-time backfill: extract wiki/ pages from pre-existing vault folders.
# Safe to re-run; agent will respect CLAUDE.md (search-before-create, no deletes).
set -euo pipefail

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

PROMPT_FILE="$ROOT/prompts/backfill.md"
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "error: missing $PROMPT_FILE" >&2
  exit 1
fi

if [[ ! -d "$VAULT_PATH" ]]; then
  echo "error: vault not found: $VAULT_PATH (run ./scripts/setup.sh first)" >&2
  exit 1
fi

if ! command -v "$AGENT_CMD" >/dev/null 2>&1; then
  echo "error: agent command not found: $AGENT_CMD" >&2
  exit 1
fi

echo "Vault: $VAULT_PATH"
echo "Agent: $AGENT_CMD (model: $AGENT_MODEL)"

"$ROOT/scripts/commit-wrapper.sh" "pre-backfill snapshot"

BACKFILL_PROMPT="$(cat "$PROMPT_FILE")"

LOG_FILE="/tmp/kb-backfill-$(date +%s).log"
echo "Invoking backfill agent (this may take 5-15 minutes)..."
echo "Streaming JSONL events to $LOG_FILE"
cd "$VAULT_PATH"
"$AGENT_CMD" \
  --model "$AGENT_MODEL" \
  --print \
  --dangerously-skip-permissions \
  --verbose \
  --output-format stream-json \
  --input-format text \
  "Working directory (vault): $VAULT_PATH

$BACKFILL_PROMPT" </dev/null 2>&1 | tee "$LOG_FILE"

echo ""
echo "=== final event from $LOG_FILE ==="
tail -n 1 "$LOG_FILE" || true

cd "$ROOT"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
"$ROOT/scripts/commit-wrapper.sh" "backfill: $TS"

echo "Backfill finished. Log: $LOG_FILE"
