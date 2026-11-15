# easyscholar-mcp

An **unofficial** MCP server that lets AI agents (Claude, Cursor, Cline, Codex, and any other MCP client) look up a journal's impact factor, JCR quartile and CAS (中科院) zone through the [easyScholar](https://www.easyscholar.cc) open API.

Not affiliated with or endorsed by easyScholar. You need your own easyScholar secret key.

<!-- mcp-name: io.github.GITHUB_USERNAME/easyscholar-mcp -->

## Tools

| Tool | What it does |
|---|---|
| `journal_rank(publication_name)` | One journal |
| `journal_ranks(publication_names)` | Up to 50 journals per call, ~0.6 s apart to stay under the rate limit |

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

## Setup

1. Get a secret key from your easyScholar account: 个人中心 → 开放接口.
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

## 中文说明

给 AI agent 用的 easyScholar 期刊查询 MCP，非官方工具，与 easyScholar 无关联。

- 能查：影响因子、五年影响因子、JCR 分区、中科院分区（升级版、基础版、小类、Top）、中科院预警、新锐分区、JCI、ESI 学科等。
- 要用自己的 easyScholar 密钥，填到环境变量 `EASYSCHOLAR_SECRET_KEY`。
- 批量查询每次最多 50 本。
- 查不到时，返回内容会提示 agent 换一种期刊名写法重试。

## License

MIT
