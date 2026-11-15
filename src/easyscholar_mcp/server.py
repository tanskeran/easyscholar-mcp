"""easyScholar MCP server: journal impact factor / JCR / CAS (中科院) zone lookup for AI agents.

Unofficial. Not affiliated with easyScholar.
The secret key is read only from the EASYSCHOLAR_SECRET_KEY environment variable and is
scrubbed from every error message the server returns.
"""
import asyncio
import logging
import os

import httpx
from mcp.server.fastmcp import FastMCP

# httpx logs every request URL at INFO, and the URL carries the secret key. MCP clients often
# write server stderr to log files, so keep these loggers quiet.
for _name in ("httpx", "httpcore"):
    logging.getLogger(_name).setLevel(logging.WARNING)

API = "https://www.easyscholar.cc/open/getPublicationRank"
GAP_S = 0.6          # pause between requests in a batch (avoid easyScholar rate limiting)
MAX_BATCH = 50       # max journals per batch call

# easyScholar officialRank field -> stable English key (unlisted fields are passed through as-is)
FIELDS = {
    "sciif": "impact_factor",
    "sciif5": "impact_factor_5y",
    "sci": "jcr_quartile",
    "jci": "jci",
    "esi": "esi_field",
    "sciUp": "cas_zone",              # 中科院分区（升级版）
    "sciUpSmall": "cas_subcategory_zone",
    "sciUpTop": "cas_top",
    "sciBase": "cas_zone_basic",      # 中科院分区（基础版）
    "sciwarn": "cas_warning",         # 中科院预警
    "xr": "xinrui_zone",              # 新锐分区
    "xrSmall": "xinrui_subcategory_zone",
    "xrTop": "xinrui_top",
    "ssci": "ssci_quartile",
    "esci": "esci_quartile",
    "eii": "ei",
    "ccf": "ccf",
    "cscd": "cscd",
    "pku": "pku_core",                # 北大核心
    "cssci": "cssci",
}
# Per-university journal lists (西南交大、新疆大学、地大 …): dropped to keep output compact
SKIP = {"swjtu", "xju", "cug", "scu", "cpu", "cufe", "xdu", "hhu", "nju", "swufe", "ruc", "uibe"}

NOT_FOUND_HINT = (
    "Not found. easyScholar matches its own spelling of the journal name: retry with the full "
    "official title, the abbreviation, or a hyphenated variant (e.g. 'JPAD-Journal of Prevention "
    "of Alzheimers Disease'); drop leading 'The'; '&' vs 'and' can matter."
)

mcp = FastMCP("easyscholar")


def _key() -> str:
    k = os.environ.get("EASYSCHOLAR_SECRET_KEY", "").strip()
    if not k:
        raise RuntimeError("EASYSCHOLAR_SECRET_KEY is not set (get a key at https://www.easyscholar.cc)")
    return k


def _custom(custom: dict | None) -> list[str]:
    """Decode customRank (user-defined datasets in the easyScholar account) into 'name: level' strings."""
    if not custom:
        return []
    out = []
    try:
        info = {i["uuid"]: i for i in custom.get("rankInfo", [])}
        texts = ["oneRankText", "twoRankText", "threeRankText", "fourRankText", "fiveRankText"]
        for item in custom.get("rank", []):
            uuid, level = item.split("&&&")
            i = info.get(uuid, {})
            lv = int(level)
            txt = i.get(texts[lv - 1], level) if 1 <= lv <= 5 else level
            out.append(f"{i.get('abbName', uuid)}: {txt}")
    except Exception:
        return []
    return out


async def _query(client: httpx.AsyncClient, name: str) -> dict:
    for attempt in range(2):  # retry once on transient connection errors
        try:
            r = await client.get(API, params={"secretKey": _key(), "publicationName": name}, timeout=20)
            break
        except httpx.TransportError:
            if attempt:
                raise
            await asyncio.sleep(1.0)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 200:
        return {"query": name, "found": False, "error": f"easyScholar {j.get('code')}: {j.get('msg')}"}
    data = j.get("data") or {}
    official = (data.get("officialRank") or {}).get("all") or {}
    metrics = {FIELDS.get(k, k): v for k, v in official.items() if k not in SKIP}
    custom = _custom(data.get("customRank"))
    if not metrics and not custom:
        return {"query": name, "found": False, "hint": NOT_FOUND_HINT}
    res = {"query": name, "found": True, "metrics": metrics}
    if custom:
        res["custom_ranks"] = custom
    return res


async def _safe_query(client: httpx.AsyncClient, name: str) -> dict:
    """Never raise; replace the secret key in any error text with ***."""
    try:
        return await _query(client, name)
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        k = os.environ.get("EASYSCHOLAR_SECRET_KEY", "").strip()
        if k:
            msg = msg.replace(k, "***")
        return {"query": name, "found": False, "error": msg}


@mcp.tool()
async def journal_rank(publication_name: str) -> dict:
    """Look up one journal's impact factor and quartiles/zones via easyScholar (查期刊影响因子和分区).

    publication_name: journal title, e.g. "NeuroImage: Clinical", "Annals of Neurology".

    Returns {"query", "found", "metrics", "custom_ranks"?} or {"found": false, "hint"/"error"}.
    metrics keys: impact_factor (JCR IF), impact_factor_5y, jcr_quartile (Q1-Q4), jci, esi_field,
    cas_zone (中科院分区升级版), cas_subcategory_zone, cas_top, cas_zone_basic (中科院基础版),
    cas_warning (中科院预警), xinrui_zone (新锐分区), ssci_quartile, esci_quartile, ei, pku_core,
    cssci, cscd, ccf. Only keys easyScholar has data for are present; values are strings.
    If found is false, follow the hint and retry with another spelling of the name.
    """
    async with httpx.AsyncClient() as c:
        return await _safe_query(c, publication_name)


@mcp.tool()
async def journal_ranks(publication_names: list[str]) -> list[dict]:
    """Look up several journals at once (max 50; ~0.6 s between requests). Same output per journal as journal_rank."""
    names = list(dict.fromkeys(n.strip() for n in publication_names if n and n.strip()))
    if len(names) > MAX_BATCH:
        return [{"found": False, "error": f"Too many journals ({len(names)}); max {MAX_BATCH} per call. Split the list."}]
    out = []
    async with httpx.AsyncClient() as c:
        for i, n in enumerate(names):
            if i:
                await asyncio.sleep(GAP_S)
            out.append(await _safe_query(c, n))
    return out


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
