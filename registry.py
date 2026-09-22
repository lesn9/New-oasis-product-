"""Adapter registry — routes an address to the right adapter."""
from typing import Optional
from adapters.evm import EVMAdapter

_evm: Optional[EVMAdapter] = None


def register_evm(adapter: EVMAdapter) -> None:
    global _evm
    _evm = adapter


def get_evm() -> Optional[EVMAdapter]:
    return _evm


def get_adapter_for(ecosystem: str):
    if ecosystem == "evm":
        return _evm
    return None
