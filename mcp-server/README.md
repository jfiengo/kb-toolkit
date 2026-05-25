# kb-toolkit MCP server

The MCP server exposes vault tools over **stdio** for Claude Desktop. It reads `vault_path` from `kb.config.yaml` in the kb-toolkit repo (or current working directory).

## Prerequisites

1. Copy `kb.config.example.yaml` to `kb.config.yaml` and set `vault_path` to your vault (outside this repo).
2. Set `mcp.enabled: true` in config (optional reminder flag).
3. Run `./scripts/setup.sh` once to bootstrap the vault.

## Claude Desktop configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kb-toolkit": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/kb-toolkit",
        "kb-mcp"
      ]
    }
  }
}
```

Replace `/ABSOLUTE/PATH/TO/kb-toolkit` with your clone path. `uv run` uses the project virtualenv implicitly.

Restart Claude Desktop after saving.

## Tools

| Tool | Description |
|------|-------------|
| `search_notes` | Lexical search over vault markdown |
| `create_note` | Create a note in inbox/wiki/etc. with frontmatter |
| `update_note` | Update body and tags |
| `list_notes` | List notes with excerpts |

Semantic search is **not** implemented in Python. Use the Smart Connections Obsidian plugin (`search.provider` in config).

## Local test

```bash
cd /path/to/kb-toolkit
uv sync
uv run kb-mcp
```

The process listens on stdio; press Ctrl+C to exit.
