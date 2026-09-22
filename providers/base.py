"""Base provider interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TokenMetadata:
    address: str
    chain: str
    name: Optional[str] = None
    symbol: Optional[str] = None
    decimals: Optional[int] = None
    logo: Optional[str] = None
    total_supply: Optional[str] = None
    token_type: Optional[str] = None
    verified: Optional[bool] = None
    raw: dict = field(default_factory=dict)


@dataclass
class MarketData:
    pair_address: Optional[str] = None
    dex: Optional[str] = None
    pair_label: Optional[str] = None
    price_usd: Optional[float] = None
    price_change_24h: Optional[float] = None
    liquidity_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    market_cap_usd: Optional[float] = None
    fdv_usd: Optional[float] = None
    pair_url: Optional[str] = None
    pairs: list = field(default_factory=list)
    raw: dict = field(default_factory=dict)


class ProviderError(Exception):
    """Raised when a provider cannot return data."""


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def health(self) -> bool:
        ...
