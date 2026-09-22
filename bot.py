"""Web3 Oasis — Telegram bot entry point."""
import asyncio
import sys

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from adapters.evm import EVMAdapter
from adapters import registry
from config import get_config, ConfigError
from providers.alchemy import AlchemyProvider
from providers.blockscout import BlockscoutProvider
from providers.dexscreener import DexScreenerProvider
from telegram.handlers import (
    cmd_analyze,
    cmd_help,
    cmd_start,
    on_chain_choice,
    on_refresh,
)
from utils.http import close_session
from utils.logging import get_logger, setup_logging

log = get_logger(__name__)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Unhandled exception", exc_info=context.error)


def build_application():
    cfg = get_config()
    setup_logging(cfg.log_level)

    alchemy = AlchemyProvider(cfg.alchemy_api_key)
    blockscout = BlockscoutProvider()
    dexscreener = DexScreenerProvider()

    evm = EVMAdapter(alchemy=alchemy, blockscout=blockscout, dexscreener=dexscreener)
    registry.register_evm(evm)

    app = ApplicationBuilder().token(cfg.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("analyze", cmd_analyze))
    app.add_handler(CallbackQueryHandler(on_chain_choice, pattern=r"^chain:"))
    app.add_handler(CallbackQueryHandler(on_refresh, pattern=r"^refresh:"))
    app.add_error_handler(on_error)

    return app


def main() -> int:
    try:
        app = build_application()
    except ConfigError as e:
        print(f"[FATAL] Config error: {e}", file=sys.stderr)
        return 1

    log.info("Web3 Oasis starting (polling mode)…")

    async def _shutdown():
        await close_session()

    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        try:
            asyncio.get_event_loop().run_until_complete(_shutdown())
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
