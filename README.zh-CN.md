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
- `found` 为 `false` 时会附带 `hint`：easyScholar 要按它收录的写法匹配期刊名，agent 可以换全称、缩写或带连字符的写法再试。
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

Claude Code 用户：

```bash
claude mcp add easyscholar -e EASYSCHOLAR_SECRET_KEY=你的密钥 -- uvx easyscholar-mcp
```

如果不想把密钥写进配置文件，可以把 `EASYSCHOLAR_SECRET_KEY` 设成用户环境变量，再在支持变量展开的客户端里写成 `"${EASYSCHOLAR_SECRET_KEY}"`。

## 许可证

MIT
