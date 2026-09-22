"""Blockscout explorer provider — contract info, verification, fallback metadata."""
from typing import Optional

from providers.base import BaseProvider, TokenMetadata
from utils.http import get_json
from utils.retry import with_retry
from utils.logging import get_logger

log = get_logger(__name__)


BLOCKSCOUT_URLS = {
    "ethereum": "https://eth.blockscout.com",
    "base": "https://base.blockscout.com",
    "arbitrum": "https://arbitrum.blockscout.com",
    "optimism": "https://optimism.blockscout.com",
    "polygon": "https://polygon.blockscout.com",
    "gnosis": "https://gnosis.blockscout.com",
    "celo": "https://celo.blockscout.com",
    "scroll": "https://scroll.blockscout.com",
    "zksync": "https://zksync.blockscout.com",
    "linea": "https://linea.blockscout.com",
    "mantle": "https://mantle.blockscout.com",
    "blast": "https://blast.blockscout.com",
    "robinhood": "https://robinhoodchain.blockscout.com",
}


class BlockscoutProvider(BaseProvider):
    name = "blockscout"

    def _base(self, chain: str) -> Optional[str]:
        return BLOCKSCOUT_URLS.get(chain)

    async def health(self) -> bool:
        try:
            await get_json(f"{BLOCKSCOUT_URLS['ethereum']}/api/v2/stats")
            return True
        except Exception:
            return False

    async def get_token_info(self, chain: str, address: str) -> Optional[dict]:
        base = self._base(chain)
        if not base:
            return None

        async def _fetch():
            return await get_json(f"{base}/api/v2/tokens/{address}")

        try:
            return await with_retry(_fetch, label=f"blockscout:{chain}")
        except Exception as e:
            log.debug(f"Blockscout token info failed {chain}/{address}: {e}")
            return None

    async def get_token_metadata(self, chain: str, address: str) -> Optional[TokenMetadata]:
        info = await self.get_token_info(chain, address)
        if not info:
            return None

        return TokenMetadata(
            address=address,
            chain=chain,
            name=info.get("name"),
            symbol=info.get("symbol"),
            decimals=_safe_int(info.get("decimals")),
            logo=info.get("icon_url"),
            total_supply=info.get("total_supply"),
            token_type=info.get("type"),
            verified=info.get("is_verified") if "is_verified" in info else None,
            raw=info,
        )

    async def get_contract_info(self, chain: str, address: str) -> Optional[dict]:
        base = self._base(chain)
        if not base:
            return None

        async def _fetch():
            return await get_json(f"{base}/api/v2/addresses/{address}")

        try:
            return await with_retry(_fetch, label=f"blockscout-addr:{chain}")
        except Exception as e:
            log.debug(f"Blockscout address failed {chain}/{address}: {e}")
            return None


def _safe_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None