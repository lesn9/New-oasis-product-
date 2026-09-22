"""Telegram command handlers."""
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from adapters import registry
from adapters.evm import EVM_CHAINS
from telegram.formatting import (
    build_analyze_message,
    build_chain_choice_message,
    build_help_message,
    build_start_message,
)
from telegram.keyboards import chain_choice_keyboard, analyze_actions_keyboard
from utils.logging import get_logger
from utils.validation import detect_ecosystem

log = get_logger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        build_start_message(),
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        build_help_message(),
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
    )


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "Usage: `/analyze <contract_address>`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    address = args[0].strip()
    ecosystem = detect_ecosystem(address)

    if ecosystem == "unknown":
        await update.message.reply_text(
            "⚠️ Unrecognized address format\\.\n"
            "Phase 1 supports EVM addresses \\(`0x...`\\)\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    if ecosystem != "evm":
        await update.message.reply_text(
            f"ℹ️ Detected ecosystem: *{ecosystem}*\n"
            "This ecosystem arrives in a later phase\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    evm = registry.get_evm()
    if evm is None:
        await update.message.reply_text("⚠️ Internal error: EVM adapter not registered\\.")
        return

    status = await update.message.reply_text("🔍 Detecting chain\\.\\.\\.")

    try:
        chains = await evm.find_chains(address)
    except Exception as e:
        log.exception("find_chains failed")
        await status.edit_text("⚠️ Chain detection failed\\. Please try again\\.")
        return

    if not chains:
        await status.edit_text(
            "⚠️ *No EVM contract found* for this address on supported chains\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    if len(chains) > 1:
        await status.edit_text(
            build_chain_choice_message(address, chains),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=chain_choice_keyboard(address, chains),
        )
        return

    chain = chains[0]
    await _render_analysis(status, evm, chain, address)


async def on_chain_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    parts = data.split(":", 2)
    if len(parts) != 3:
        return
    _, chain, address = parts

    evm = registry.get_evm()
    if evm is None:
        return

    await query.edit_message_text("📊 Fetching token data\\.\\.\\.")
    await _render_analysis(query.message, evm, chain, address, edit=True)


async def on_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("Refreshing…")
    data = query.data or ""
    parts = data.split(":", 2)
    if len(parts) != 3:
        return
    _, chain, address = parts
    evm = registry.get_evm()
    if evm is None:
        return
    await query.edit_message_text("🔄 Refreshing\\.\\.\\.")
    await _render_analysis(query.message, evm, chain, address, edit=True)


async def _render_analysis(message, evm, chain: str, address: str, edit: bool = False) -> None:
    try:
        snapshot = await evm.snapshot(chain, address)
    except Exception as e:
        log.exception("snapshot failed")
        text = "⚠️ Provider temporarily unavailable\\. Please try again\\."
        if edit:
            await message.edit_text(text)
        else:
            await message.edit_text(text)
        return

    text = build_analyze_message(snapshot)

    # Telegram message length cap ~4096; split if needed
    chunks = _chunk(text, 4000)
    try:
        if edit:
            await message.edit_text(
                chunks[0],
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
                reply_markup=analyze_actions_keyboard(chain, address),
            )
        else:
            await message.edit_text(
                chunks[0],
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
                reply_markup=analyze_actions_keyboard(chain, address),
            )
        for chunk in chunks[1:]:
            await message.reply_text(
                chunk,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
            )
    except Exception as e:
        log.exception("Failed to send analysis message")
        try:
            await message.edit_text(f"⚠️ Formatting error: {type(e).__name__}")
        except Exception:
            pass


def _chunk(text: str, size: int) -> list:
    return [text[i : i + size] for i in range(0, len(text), size)] or [text]
