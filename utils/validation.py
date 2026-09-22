"""Address and input validation."""
import re

EVM_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
SOLANA_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
SUI_COIN_RE = re.compile(r"^0x[a-fA-F0-9]{1,64}::[a-zA-Z0-9_]+::[A-Z0-9_]+$")
TRON_RE = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")


def is_evm_address(s: str) -> bool:
    return bool(EVM_RE.match(s.strip()))


def is_solana_address(s: str) -> bool:
    s = s.strip()
    if s.startswith("0x"):
        return False
    return bool(SOLANA_RE.match(s))


def is_sui_coin_type(s: str) -> bool:
    return bool(SUI_COIN_RE.match(s.strip()))


def is_tron_address(s: str) -> bool:
    return bool(TRON_RE.match(s.strip()))


def detect_ecosystem(s: str) -> str:
    s = s.strip()
    if is_evm_address(s):
        return "evm"
    if is_sui_coin_type(s):
        return "sui"
    if is_tron_address(s):
        return "tron"
    if is_solana_address(s):
        return "solana"
    return "unknown"


def sanitize_text(s: str, max_len: int = 500) -> str:
    if not s:
        return ""
    s = s.replace("\x00", "")
    if len(s) > max_len:
        s = s[: max_len - 3] + "..."
    return s