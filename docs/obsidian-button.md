# Obsidian quality-of-life setup

Two optional Obsidian plugins make kb-toolkit nicer to live with:

1. **Shell Commands** + **Commander** — one-click compile from a ribbon button (no Terminal).
2. **Smart Connections** — semantic "related notes" sidebar inside Obsidian.

Both are optional. kb-toolkit works end-to-end without either of them.

---

## Part 1 — One-click compile button

Trigger `./scripts/compile.sh` from Obsidian's left ribbon. Recommended for daily use.

### Prerequisites

- kb-toolkit installed and `./scripts/setup.sh` already run against your vault.
- `claude` CLI on your `PATH` (or your configured `agent.command`).
- macOS or Linux. The Shell Commands plugin does **not** run on Obsidian Mobile — capture on mobile, compile on the desktop.

### 1. Install Shell Commands

Settings → **Community plugins** → **Browse** → search **Shell commands** (author *Taitava*) → Install → Enable.

### 2. Create a "Compile Vault" command

Settings → **Shell commands** → **New shell command**. Click the gear icon on the new row to open the per-command settings modal.

#### Environments tab

Put the absolute path to your kb-toolkit clone in **Default shell command**:

```
/ABSOLUTE/PATH/TO/kb-toolkit/scripts/compile.sh
```

The kb-toolkit scripts already prepend `/opt/homebrew/bin` (and `/usr/local/bin`) to `PATH` and redirect stdin from `/dev/null`, so they work from GUI launchers without extra env-var configuration.

#### General tab

- **Alias**: `Compile Vault`
- **Icon**: pick anything (e.g. `backpack`, `refresh-cw`, `sparkles`).
- **Ask confirmation before execution**: ON (compile spends LLM credits — guards against accidental clicks).

#### Output tab

Route command output to a UI surface you'll actually see:

- **stdout** → **Notification balloon** (or "Modal" if your plugin version has it).
- **stderr** → same as stdout.

Avoid routing to the **status bar** — it shows only the last line and **clicking it can kill the running command** in some Shell Commands versions. Don't click the status bar while compile is running.

The `claude` CLI runs in `--print` mode, so it emits its summary only when the run finishes. Streaming displays won't show progress mid-run; just wait. A typical compile on `opus` takes 2–8 minutes.

#### Events tab

Leave all the automatic triggers (`Obsidian starts`, `Caret moved`, etc.) **off**. This is a manual command.

### 3. Add the ribbon button via Commander

Shell Commands doesn't expose a ribbon toggle in every version. The cross-version path is the **Commander** plugin:

1. Community plugins → install **Commander** → enable.
2. Settings → **Commander** → **Left ribbon** (or "Ribbon").
3. **+ Add command** → search `Compile Vault` (or `Shell commands: Compile Vault`).
4. Pick an icon → save.

A new icon appears in Obsidian's left ribbon. Click = run.

### 4. (Optional) Hotkey

Settings → **Hotkeys** → search `Shell commands: Compile Vault` → bind e.g. `Cmd+Shift+K`.

### Alternative: in-note button

If you prefer a clickable button **inside a markdown note** (e.g. on your vault homepage):

1. Install the **Buttons** plugin (author *Shabegom*).
2. Drop this block into any note:

   ````md
   ```button
   name Compile Vault
   type command
   action Shell commands: Compile Vault
   ```
   ````

The button renders inline. Pin a note like `wiki/index.md` and you have a click-to-compile dashboard.

---

## Part 2 — Semantic search with Smart Connections

The kb-toolkit Python package deliberately does **not** ship embeddings. Semantic "find related notes" lives in the **Smart Connections** Obsidian plugin (author *Brian Petro*), which runs a small local embedding model entirely on your machine — no API key, no remote calls.

### Install

Settings → **Community plugins** → **Browse** → search **Smart Connections** → Install → Enable.

After enabling, the plugin builds an embedding index in the background. First pass takes a few minutes on a small vault. Open the **Smart Connections** panel from the right sidebar (or Command Palette → "Smart Connections: Open Smart View") to see "notes similar to the one you're currently viewing."

### Setting

In `kb.config.yaml`:

```yaml
search:
  provider: "smart-connections"   # smart-connections | open-connections | none
```

This is informational. The MCP `search_notes` tool always returns lexical matches; with `smart-connections` set, results include a hint suggesting users open the plugin in Obsidian for semantic similarity. Semantic search through MCP is intentionally out of scope (see README "What is NOT a dependency").

### iCloud + Smart Connections caveat

If your vault lives in iCloud (e.g. `Mobile Documents/iCloud~md~obsidian/...`), the plugin's embedding cache (`.smart-env/`, `.smart-connections/`) will sync to iCloud and consume mobile storage even though the plugin only runs on desktop. The kb-toolkit vault `.gitignore` template already excludes these caches from git. For iCloud size, you have two options:

- Accept the cost (~200–500 MB depending on vault size).
- Set `search.provider: "none"` and skip the plugin if you don't need semantic search.

---

## Troubleshooting

### "Executing" status bar sits forever, no output, no commit

`claude` CLI hangs when stdin is a unix socket — which is what Obsidian's Shell Commands plugin provides. kb-toolkit's `compile.sh` and `backfill.sh` redirect stdin from `/dev/null` to fix this. If you see this on an older clone, pull `main`.

### `uv: command not found` or `claude: command not found`

The scripts prepend Homebrew to `PATH`. If your install is non-standard, edit `scripts/compile.sh`:

```bash
export PATH="/your/bin:${PATH:-/usr/bin:/bin}"
```

### Status bar disappears immediately with no commit

The run was likely killed — clicking the status bar in some Shell Commands versions cancels the running command. Don't click it; wait for it to clear on its own.

### Compile produced a pre-compile commit but no follow-up

This is normal when `inbox/` is empty and the agent has no edits to make. The pre-compile commit happens unconditionally (it captures any vault changes since last compile, e.g. plugin config); the post-compile commit only runs if the agent actually wrote something.

### I want to see live progress instead of just a summary

Switch the model to a faster one in `kb.config.yaml` (`agent.model: sonnet`) or add `--output-format stream-json` to the `claude` invocation in `compile.sh`. Trade-off: more verbose output for less wall-clock wait.

---

## Mobile workflow

Capture in `inbox/` from Obsidian Mobile. iCloud syncs the note to your Mac within seconds (depending on iCloud). On the Mac, click the ribbon button when you're ready to compile. The agent promotes content into `wiki/`, applies the inbox-after-promotion policy, and commits.
