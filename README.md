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
- If `found` is `false`, the result includes a `hint`. easyScholar matches its own spelling of a journal title, so the agent should retry with the full title, the abbreviation, or a hyphenated variant.
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

If you use Claude Code:

```bash
claude mcp add easyscholar -e EASYSCHOLAR_SECRET_KEY=your-key -- uvx easyscholar-mcp
```

You can also keep the key out of config files: set `EASYSCHOLAR_SECRET_KEY` as a user environment variable, and reference it as `"${EASYSCHOLAR_SECRET_KEY}"` in clients that expand variables.

## License

MIT
