"""Alchemy provider — EVM metadata + RPC."""
from typing import Optional

from providers.base import BaseProvider, TokenMetadata
from utils.http import get_json, get_session, post_json
from utils.retry import with_retry
from utils.logging import get_logger

log = get_logger(__name__)

ALCHEMY_NETWORKS = {
    "ethereum": "eth-mainnet",
    "base": "base-mainnet",
    "arbitrum": "arb-mainnet",
    "optimism": "opt-mainnet",
    "polygon": "polygon-mainnet",
    "bsc": "bnb-mainnet",
    "avalanche": "avax-mainnet",
    "linea": "linea-mainnet",
    "zksync": "zksync-mainnet",
    "scroll": "scroll-mainnet",
    "mantle": "mantle-mainnet",
    "blast": "blast-mainnet",
    "gnosis": "gnosis-mainnet",
    "celo": "celo-mainnet",
    "unichain": "unichain-mainnet",
    "worldchain": "worldchain-mainnet",
    "soneium": "soneium-mainnet",
    "shape": "shape-mainnet",
    "sonic": "sonic-mainnet",
    "berachain": "berachain-mainnet",
    "abstract": "abstract-mainnet",
}


class AlchemyProvider(BaseProvider):
    name = "alchemy"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _url(self, network: str, path: str) -> str:
        return f"https://{network}.g.alchemy.com/v2/{self.api_key}{path}"

    def _network(self, chain: str) -> Optional[str]:
        return ALCHEMY_NETWORKS.get(chain)

    async def health(self) -> bool:
        try:
            net = ALCHEMY_NETWORKS["ethereum"]
            await post_json(
                self._url(net, ""),
                json={"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []},
            )
            return True
        except Exception:
            return False

    async def get_token_metadata(self, chain: str, address: str) -> Optional[TokenMetadata]:
        network = self._network(chain)
        if not network:
            return None

        url = self._url(network, "/getTokenMetadata")
        payload = {"tokenAddresses": [address]}

        async def _fetch():
            return await post_json(url, json=payload)

        try:
            data = await with_retry(_fetch, label=f"alchemy:{chain}")
        except Exception as e:
            log.warning(f"Alchemy metadata failed {chain}/{address}: {e}")
            return None

        if not data:
            return None

        md = data[0] if isinstance(data, list) else data
        if not md or not md.get("symbol"):
            return None

        return TokenMetadata(
            address=address,
            chain=chain,
            name=md.get("name"),
            symbol=md.get("symbol"),
            decimals=md.get("decimals"),
            logo=md.get("logo"),
            raw=md,
        )

    async def get_latest_block(self, chain: str) -> Optional[int]:
        network = self._network(chain)
        if not network:
            return None
        url = self._url(network, "")
        payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}

        async def _fetch():
            return await post_json(url, json=payload)

        try:
            data = await with_retry(_fetch, label=f"alchemy-block:{chain}")
            return int(data.get("result", "0x0"), 16)
        except Exception as e:
            log.warning(f"Alchemy block failed {chain}: {e}")
            return None
