"""EVM adapter — orchestrates providers for EVM chains."""
import asyncio
from typing import Optional

from adapters.base import BaseAdapter, TokenSnapshot
from providers.alchemy import AlchemyProvider
from providers.blockscout import BlockscoutProvider
from providers.dexscreener import DexScreenerProvider
from utils.logging import get_logger

log = get_logger(__name__)


EVM_CHAINS = {
    "ethereum":   {"id": 1,      "name": "Ethereum",         "native": "ETH",   "explorer": "https://etherscan.io"},
    "base":       {"id": 8453,   "name": "Base",             "native": "ETH",   "explorer": "https://basescan.org"},
    "arbitrum":   {"id": 42161,  "name": "Arbitrum One",     "native": "ETH",   "explorer": "https://arbiscan.io"},
    "optimism":   {"id": 10,     "name": "Optimism",         "native": "ETH",   "explorer": "https://optimistic.etherscan.io"},
    "polygon":    {"id": 137,    "name": "Polygon",          "native": "POL",   "explorer": "https://polygonscan.com"},
    "bsc":        {"id": 56,     "name": "BNB Smart Chain",  "native": "BNB",   "explorer": "https://bscscan.com"},
    "avalanche":  {"id": 43114,  "name": "Avalanche",        "native": "AVAX",  "explorer": "https://snowtrace.io"},
    "linea":      {"id": 59144,  "name": "Linea",            "native": "ETH",   "explorer": "https://lineascan.build"},
    "zksync":     {"id": 324,    "name": "zkSync Era",       "native": "ETH",   "explorer": "https://explorer.zksync.io"},
    "scroll":     {"id": 534352, "name": "Scroll",           "native": "ETH",   "explorer": "https://scrollscan.com"},
    "mantle":     {"id": 5000,   "name": "Mantle",           "native": "MNT",   "explorer": "https://explorer.mantle.xyz"},
    "blast":      {"id": 81457,  "name": "Blast",            "native": "ETH",   "explorer": "https://blastscan.io"},
    "gnosis":     {"id": 100,    "name": "Gnosis",           "native": "xDAI",  "explorer": "https://gnosisscan.io"},
    "celo":       {"id": 42220,  "name": "Celo",             "native": "CELO",  "explorer": "https://celoscan.io"},
    "unichain":   {"id": 130,    "name": "Unichain",         "native": "ETH",   "explorer": "https://uniscan.xyz"},
    "worldchain": {"id": 480,    "name": "World Chain",      "native": "ETH",   "explorer": "https://worldscan.org"},
    "soneium":    {"id": 1868,   "name": "Soneium",          "native": "ETH",   "explorer": "https://soneium.blockscout.com"},
    "shape":      {"id": 360,    "name": "Shape",            "native": "ETH",   "explorer": "https://shapescan.xyz"},
    "sonic":      {"id": 146,    "name": "Sonic",            "native": "S",     "explorer": "https://sonicscan.org"},
    "berachain":  {"id": 80094,  "name": "Berachain",        "native": "BERA",  "explorer": "https://berascan.com"},
    "monad":      {"id": 143,    "name": "Monad",            "native": "MON",   "explorer": "https://monadscan.com"},
    "robinhood":  {"id": 4663,   "name": "Robinhood Chain",  "native": "ETH",   "explorer": "https://explorer.robinhood.com"},
    "arc":        {"id": 5042,   "name": "Arc",              "native": "ARC",   "explorer": "https://explorer.arc.network"},
    "ink":        {"id": 57073,  "name": "Ink",              "native": "ETH",   "explorer": "https://explorer.inkonchain.com"},
    "abstract":   {"id": 2741,   "name": "Abstract",         "native": "ETH",   "explorer": "https://abscan.org"},
}


class EVMAdapter(BaseAdapter):
    ecosystem = "evm"

    def __init__(
        self,
        alchemy: AlchemyProvider,
        blockscout: BlockscoutProvider,
        dexscreener: DexScreenerProvider,
    ):
        self.alchemy = alchemy
        self.blockscout = blockscout
        self.dexscreener = dexscreener

    def supported_chains(self) -> list:
        return list(EVM_CHAINS.keys())

    async def find_chains(self, address: str) -> list:
        chains = list(EVM_CHAINS.keys())

        async def probe(chain: str) -> Optional[str]:
            info = await self.blockscout.get_token_info(chain, address)
            if info and info.get("name"):
                return chain
            md = await self.alchemy.get_token_metadata(chain, address)
            if md and md.symbol:
                return chain
            return None

        results = await asyncio.gather(*(probe(c) for c in chains), return_exceptions=True)
        return [c for c, r in zip(chains, results) if isinstance(r, str)]

    async def snapshot(self, chain: str, address: str) -> TokenSnapshot:
        snap = TokenSnapshot(
            address=address,
            chain=chain,
            chain_id=EVM_CHAINS.get(chain, {}).get("id"),
            ecosystem="evm",
        )

        meta = await self.blockscout.get_token_metadata(chain, address)
        if not meta or not meta.symbol:
            meta = await self.alchemy.get_token_metadata(chain, address)
            if meta:
                snap.source_notes.append("metadata: alchemy")
        else:
            snap.source_notes.append("metadata: blockscout")

        if not meta:
            snap.warnings.append("Token metadata unavailable from all providers.")

        snap.metadata = meta

        try:
            snap.market = await self.dexscreener.get_market_data(chain, address)
        except Exception as e:
            log.warning(f"Market data failed: {e}")
            snap.warnings.append("Market data temporarily unavailable.")

        try:
            snap.latest_block = await self.alchemy.get_latest_block(chain)
        except Exception:
            pass

        try:
            snap.contract_info = await self.blockscout.get_contract_info(chain, address)
        except Exception:
            pass

        return snap