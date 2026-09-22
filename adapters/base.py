"""Base adapter interface — one per ecosystem."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from providers.base import TokenMetadata, MarketData


@dataclass
class TokenSnapshot:
    address: str
    chain: str
    chain_id: Optional[int] = None
    ecosystem: str = "evm"
    metadata: Optional[TokenMetadata] = None
    market: Optional[MarketData] = None
    latest_block: Optional[int] = None
    contract_info: Optional[dict] = None
    warnings: list = field(default_factory=list)
    source_notes: list = field(default_factory=list)


class BaseAdapter(ABC):
    ecosystem: str = "base"

    @abstractmethod
    def supported_chains(self) -> list:
        ...

    @abstractmethod
    async def find_chains(self, address: str) -> list:
        ...

    @abstractmethod
    async def snapshot(self, chain: str, address: str) -> TokenSnapshot:
        ...