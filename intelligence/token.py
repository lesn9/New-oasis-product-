"""Combine adapter snapshots into a report structure."""
from dataclasses import dataclass, field
from adapters.base import TokenSnapshot


@dataclass
class TokenReport:
    snapshot: TokenSnapshot
    facts: list = field(default_factory=list)
    warnings: list = field(default_factory=list)