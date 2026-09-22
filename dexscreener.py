"""DEX Screener market-data provider (no API key required)."""
from typing import Optional

from providers.base import BaseProvider, MarketData
from utils.http import get_json
from utils.retry import with_retry
from utils.logging import get_logger

log = get_logger(__name__)

BASE = "https://api.dexscreener.com/latest/dex"


class DexScreenerProvider(BaseProvider):
    name = "dexscreener"

    async def health(self) -> bool:
        try:
            await get_json(f"{BASE}/search", params={"q": "eth"})
            return True
        except Exception:
            return False

    async def get_market_data(self, chain_id: str, token_address: str) -> Optional[MarketData]:
        async def _fetch():
            return await get_json(f"{BASE}/tokens/{token_address}")

        try:
            data = await with_retry(_fetch, label="dexscreener")
        except Exception as e:
            log.warning(f"DEX Screener failed for {token_address}: {e}")
            return None

        if not isinstance(data, dict):
            return None

        pairs = data.get("pairs") or []
        if not pairs:
            return None

        pairs = sorted(
            pairs,
            key=lambda p: float((p.get("liquidity") or {}).get("usd") or 0),
            reverse=True,
        )

        best = pairs[0]
        liq = best.get("liquidity") or {}
        vol = best.get("volume") or {}
        change = best.get("priceChange") or {}
        base_t = best.get("baseToken") or {}
        quote_t = best.get("quoteToken") or {}

        pair_label = f"{base_t.get('symbol', '?')}/{quote_t.get('symbol', '?')}"

        return MarketData(
            pair_address=best.get("pairAddress"),
            dex=best.get("dexId"),
            pair_label=pair_label,
            price_usd=_to_float(best.get("priceUsd")),
            price_change_24h=_to_float(change.get("h24")),
            liquidity_usd=_to_float(liq.get("usd")),
            volume_24h_usd=_to_float(vol.get("h24")),
            market_cap_usd=_to_float(best.get("marketCap")),
            fdv_usd=_to_float(best.get("fdv")),
            pair_url=best.get("url"),
            pairs=[_summarize_pair(p) for p in pairs[:10]],
            raw=best,
        )


def _to_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _summarize_pair(p: dict) -> dict:
    liq = p.get("liquidity") or {}
    vol = p.get("volume") or {}
    base_t = p.get("baseToken") or {}
    quote_t = p.get("quoteToken") or {}
    return {
        "label": f"{base_t.get('symbol', '?')}/{quote_t.get('symbol', '?')}",
        "dex": p.get("dexId"),
        "liquidity_usd": _to_float(liq.get("usd")),
        "volume_24h_usd": _to_float(vol.get("h24")),
        "price_usd": _to_float(p.get("priceUsd")),
        "url": p.get("url"),
    }
