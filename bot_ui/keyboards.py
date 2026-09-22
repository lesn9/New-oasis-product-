"""Inline keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from adapters.evm import EVM_CHAINS


def chain_choice_keyboard(address: str, chains: list) -> InlineKeyboardMarkup:
    """One button per chain. Callback data: chain:<chain>:<address>"""
    rows = []
    for c in chains:
        name = EVM_CHAINS.get(c, {}).get("name", c)
        rows.append([InlineKeyboardButton(name, callback_data=f"chain:{c}:{address}")])
    return InlineKeyboardMarkup(rows)


def analyze_actions_keyboard(chain: str, address: str) -> InlineKeyboardMarkup:
    """Post-analysis actions (Phase 2+ will wire these up)."""
    rows = [
        [
            InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{chain}:{address}"),
        ]
    ]
    return InlineKeyboardMarkup(rows)
