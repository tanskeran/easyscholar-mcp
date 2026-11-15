# easyscholar-mcp

[English](README.md) | 简体中文

给 AI agent 用的期刊查询 MCP 服务。Claude、Cursor、Cline、Codex 等支持 MCP 的 agent 都能用，通过 [easyScholar](https://www.easyscholar.cc) 开放接口查期刊的影响因子、JCR 分区和中科院分区。

非官方工具，与 easyScholar 无关联。需要你自己的 easyScholar 密钥。

## 工具

| 工具 | 作用 |
|---|---|
| `journal_rank(publication_name)` | 查一本期刊 |
| `journal_ranks(publication_names)` | 一次最多查 50 本，每本间隔约 0.6 秒，避免触发频率限制 |

返回示例：

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

- 字段名是固定的英文名，方便 agent 读取；值原样取自 easyScholar，以字符串返回，很多是中文。
- easyScholar 没有数据的字段不返回。
- 按原名查不到时，服务端会自动换最多三种常见写法再查：去掉开头的 "The"、`&` 和 `and` 互换、去掉标点、把 `:` 换成 `-`。换写法后查到的，`matched_name` 会写明用的是哪个名字。
- 都查不到时 `found` 为 `false`，`tried` 列出已经试过的写法，并附带 `hint`。agent 可以再换缩写或全称。
- 查到的结果会在本地缓存 30 天，重复查询不消耗接口次数。见[配置](#配置)。
- 密钥只从环境变量读取；返回的错误信息里如果出现密钥，会替换成 `***`。

### 字段说明

| 字段 | 含义 |
|---|---|
| `impact_factor`、`impact_factor_5y` | JCR 影响因子、五年影响因子 |
| `jcr_quartile` | JCR 分区（Q1–Q4） |
| `jci` | 期刊引文指标（JCI） |
| `esi_field` | ESI 学科 |
| `cas_zone`、`cas_subcategory_zone`、`cas_top` | 中科院分区（升级版）：大类、小类、Top 期刊 |
| `cas_zone_basic` | 中科院分区（基础版） |
| `cas_warning` | 中科院预警期刊 |
| `xinrui_zone`、`xinrui_subcategory_zone`、`xinrui_top` | 新锐分区 |
| `ssci_quartile`、`esci_quartile`、`ei`、`pku_core`、`cssci`、`cscd`、`ccf` | 其他收录和目录（北大核心等） |

## 安装

1. 登录 easyScholar，在 个人中心 → 开放接口 复制密钥。
2. 把下面的配置加到你的 MCP 客户端里。需要先装 [uv](https://docs.astral.sh/uv/)。

```json
{
  "mcpServers": {
    "easyscholar": {
      "command": "uvx",
      "args": ["easyscholar-mcp"],
      "env": { "EASYSCHOLAR_SECRET_KEY": "你的密钥" }
    }
  }
}
```

### Claude Code

```bash
claude mcp add easyscholar -e EASYSCHOLAR_SECRET_KEY=你的密钥 -- uvx easyscholar-mcp
```

### Claude Desktop、Cursor、Cline、Windsurf

这几个客户端都用上面的 `mcpServers` 格式，粘贴到：

| 客户端 | 配置文件 |
|---|---|
| Claude Desktop | 设置 → 开发者 → 编辑配置（`claude_desktop_config.json`） |
| Cursor | `~/.cursor/mcp.json`（所有项目）或 `.cursor/mcp.json`（单个项目） |
| Cline | MCP Servers → Configure → `cline_mcp_settings.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |

### VS Code（Copilot agent 模式）

`.vscode/mcp.json`。第一次启动时 VS Code 会让你输入密钥，并加密保存：

```json
{
  "inputs": [
    { "type": "promptString", "id": "easyscholar-key", "description": "easyScholar 密钥", "password": true }
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

`~/.codex/config.toml`：

```toml
[mcp_servers.easyscholar]
command = "uvx"
args = ["easyscholar-mcp"]
env = { EASYSCHOLAR_SECRET_KEY = "你的密钥" }
```

### 不把密钥写进配置文件

可以把 `EASYSCHOLAR_SECRET_KEY` 设成用户环境变量，再在支持变量展开的客户端里写成 `"${EASYSCHOLAR_SECRET_KEY}"`。

## 配置

| 环境变量 | 默认值 | 含义 |
|---|---|---|
| `EASYSCHOLAR_SECRET_KEY` | （必填） | easyScholar 密钥 |
| `EASYSCHOLAR_CACHE_DAYS` | `30` | 查到的结果缓存几天，设为 `0` 关闭缓存 |
| `EASYSCHOLAR_CACHE_DIR` | Windows 为 `%LOCALAPPDATA%\easyscholar-mcp`，其他系统为 `~/.cache/easyscholar-mcp` | 缓存文件位置 |

缓存里只有期刊数据，不含密钥。

## 许可证

MIT
