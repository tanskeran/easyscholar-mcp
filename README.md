# easyscholar-mcp

English | [简体中文](https://github.com/tanskeran/easyscholar-mcp/blob/main/README.zh-CN.md)

An **unofficial** MCP server that lets AI agents (Claude, Cursor, Cline, Codex, and any other MCP client) look up a journal's impact factor, JCR quartile and CAS (Chinese Academy of Sciences) zone through the [easyScholar](https://www.easyscholar.cc) open API.

Not affiliated with or endorsed by easyScholar. You need your own easyScholar secret key.

<!-- mcp-name: io.github.tanskeran/easyscholar-mcp -->

## Tools

| Tool | What it does |
|---|---|
| `journal_rank(publication_name)` | Looks up one journal |
| `journal_ranks(publication_names)` | Looks up up to 50 journals per call, about 0.6 s apart to stay under the rate limit |

Each result looks like this:

```json
{
  "query": "NeuroImage: Clinical",
  "found": true,
  "metrics": {
    "impact_factor": "4.2",
    "impact_factor_5y": "4.6",
    "jcr_quartile": "Q1",
    "cas_zone": "医学2区",
    "cas_subcategory_zone": "神经成像2区。",
    "jci": "1.07",
    "esi_field": "神经科学与行为"
  },
  "custom_ranks": ["新锐分区: 2区"]
}
```

- Keys are stable English names. Values are passed through from easyScholar as strings, and are often in Chinese.
- Only fields that easyScholar has data for are present.
- If a name is not found as given, the server tries up to three common respellings by itself: it drops a leading "The", swaps `&` and `and`, drops punctuation, and turns `:` into `-`. When one of them matches, `matched_name` shows which.
- If nothing matches, `found` is `false` and the result lists the spellings in `tried` plus a `hint`. The agent can then try the abbreviation or the full title.
- Found results are cached locally for 30 days, so repeated lookups don't use your API quota. See [Configuration](#configuration).
- The secret key is read only from the environment and is replaced with `***` in any error text the server returns.

### Metric keys

| Key | Meaning |
|---|---|
| `impact_factor`, `impact_factor_5y` | JCR impact factor, 5-year impact factor |
| `jcr_quartile` | JCR quartile (Q1–Q4) |
| `jci` | Journal Citation Indicator |
| `esi_field` | ESI subject field |
| `cas_zone`, `cas_subcategory_zone`, `cas_top` | CAS journal zone (upgraded edition): major category, subcategory, Top journal |
| `cas_zone_basic` | CAS journal zone (basic edition) |
| `cas_warning` | CAS early-warning journal list |
| `xinrui_zone`, `xinrui_subcategory_zone`, `xinrui_top` | Xinrui (新锐) journal zone |
| `ssci_quartile`, `esci_quartile`, `ei`, `pku_core`, `cssci`, `cscd`, `ccf` | Other indexes and lists |

## Setup

1. Get a secret key from your easyScholar account (Personal Center → Open API).
2. Add the server to your MCP client. Requires [uv](https://docs.astral.sh/uv/).

```json
{
  "mcpServers": {
    "easyscholar": {
      "command": "uvx",
      "args": ["easyscholar-mcp"],
      "env": { "EASYSCHOLAR_SECRET_KEY": "your-key" }
    }
  }
}
```

### Claude Code

```bash
claude mcp add easyscholar -e EASYSCHOLAR_SECRET_KEY=your-key -- uvx easyscholar-mcp
```

### Claude Desktop, Cursor, Cline, Windsurf

These clients use the `mcpServers` format shown above. Paste it into:

| Client | Config file |
|---|---|
| Claude Desktop | Settings → Developer → Edit Config (`claude_desktop_config.json`) |
| Cursor | `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project) |
| Cline | MCP Servers → Configure → `cline_mcp_settings.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |

### VS Code (Copilot agent mode)

`.vscode/mcp.json`. VS Code asks for the key the first time and stores it securely:

```json
{
  "inputs": [
    { "type": "promptString", "id": "easyscholar-key", "description": "easyScholar secret key", "password": true }
  ],
  "servers": {
    "easyscholar": {
      "type": "stdio",
      "command": "uvx",
      "args": ["easyscholar-mcp"],
      "env": { "EASYSCHOLAR_SECRET_KEY": "${input:easyscholar-key}" }
    }
  }
}
```

### Codex CLI

`~/.codex/config.toml`:

```toml
[mcp_servers.easyscholar]
command = "uvx"
args = ["easyscholar-mcp"]
env = { EASYSCHOLAR_SECRET_KEY = "your-key" }
```

### Keeping the key out of config files

Set `EASYSCHOLAR_SECRET_KEY` as a user environment variable, and reference it as `"${EASYSCHOLAR_SECRET_KEY}"` in clients that expand variables.

## Configuration

| Environment variable | Default | Meaning |
|---|---|---|
| `EASYSCHOLAR_SECRET_KEY` | (required) | Your easyScholar secret key |
| `EASYSCHOLAR_CACHE_DAYS` | `30` | How long found results are cached. `0` turns the cache off |
| `EASYSCHOLAR_CACHE_DIR` | `%LOCALAPPDATA%\easyscholar-mcp` on Windows, `~/.cache/easyscholar-mcp` elsewhere | Where the cache file is kept |

The cache holds journal metrics only, never the key.

## License

MIT
