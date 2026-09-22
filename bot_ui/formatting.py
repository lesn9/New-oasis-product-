"""Message formatting — Telegram MarkdownV2-safe text builders."""
from adapters.evm import EVM_CHAINS
from intelligence.market import fmt_usd, fmt_pct, fmt_price


def _esc(s) -> str:
    """Escape MarkdownV2 special chars."""
    if s is None:
        return ""
    special = r"_*[]()~`>#+-=|{}.!"
    out = []
    for ch in str(s):
        if ch in special:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def _esc_url(url: str) -> str:
    """URLs inside MarkdownV2 link syntax need different escaping."""
    if not url:
        return ""
    return url.replace(")", "\\)").replace("\\", "\\\\")


def short_addr(addr: str, head: int = 6, tail: int = 4) -> str:
    if not addr or len(addr) <= head + tail + 2:
        return addr or ""
    return f"{addr[:head]}…{addr[-tail:]}"


def build_analyze_message(snapshot) -> str:
    md = snapshot.metadata
    market = snapshot.market
    chain_info = EVM_CHAINS.get(snapshot.chain, {})
    chain_name = chain_info.get("name", snapshot.chain)
    chain_id = snapshot.chain_id or chain_info.get("id", "—")

    lines = []
    lines.append("🤖 *Web3 Oasis — Token Analysis*")
    lines.append("")

    # Identity
    if md and md.name and md.symbol:
        lines.append(f"🪙 *{_esc(md.name)}* \\(${_esc(md.symbol)}\\)")
    elif md and md.symbol:
        lines.append(f"🪙 *${_esc(md.symbol)}*")
    else:
        lines.append("🪙 *Unknown Token*")

    lines.append(f"⛓️ {_esc(chain_name)}")
    lines.append(f"🆔 Chain ID: `{chain_id}`")
    lines.append(f"📜 `{_esc(snapshot.address)}`")
    lines.append("")

    # Token metadata
    lines.append("*📋 Token Metadata*")
    if md:
        lines.append(f"• Name: {_esc(md.name or '—')}")
        lines.append(f"• Symbol: {_esc(md.symbol or '—')}")
        lines.append(f"• Decimals: {md.decimals if md.decimals is not None else '—'}")
        if md.token_type:
            lines.append(f"• Type: {_esc(md.token_type)}")
        if md.verified is not None:
            lines.append(f"• Verified: {'✅' if md.verified else '❌'}")
    else:
        lines.append("• _Unavailable from all providers_")
    lines.append("")

    # Supply
    lines.append("*💰 Supply*")
    if md and md.total_supply:
        lines.append(f"• Total: `{_esc(str(md.total_supply))}`")
    else:
        lines.append("• Total: _unavailable_")
    lines.append("")

    # On-chain
    lines.append("*🌐 On-Chain*")
    if snapshot.latest_block:
        lines.append(f"• Latest block: `{snapshot.latest_block:,}`")
    else:
        lines.append("• Latest block: _unavailable_")

    ci = snapshot.contract_info or {}
    if ci.get("creation_transaction_hash"):
        lines.append(f"• Creator tx: `{short_addr(ci['creation_transaction_hash'], 10, 6)}`")
    if ci.get("creator_address_hash"):
        lines.append(f"• Creator: `{_esc(ci['creator_address_hash'])}`")
    lines.append("")

    # Market
    lines.append("*📊 Market Data*")
    if market:
        if market.pair_label:
            lines.append(f"• Pair: {_esc(market.pair_label)}")
        if market.dex:
            lines.append(f"• DEX: {_esc(market.dex)}")
        lines.append(f"• Price: {_esc(fmt_price(market.price_usd))}")
        lines.append(f"• 24h: {_esc(fmt_pct(market.price_change_24h))}")
        lines.append(f"• Liquidity: {_esc(fmt_usd(market.liquidity_usd))}")
        lines.append(f"• Volume 24h: {_esc(fmt_usd(market.volume_24h_usd))}")
        lines.append(f"• Market Cap: {_esc(fmt_usd(market.market_cap_usd))}")
        lines.append(f"• FDV: {_esc(fmt_usd(market.fdv_usd))}")
        if market.pairs and len(market.pairs) > 1:
            lines.append("")
            lines.append(f"*Top Pairs \\(by liquidity\\) — {_esc(str(len(market.pairs)))} shown*")
            for i, p in enumerate(market.pairs[:5], 1):
                lines.append(
                    f"{i}\\. {_esc(p['label'])} on {_esc(p.get('dex') or '—')} "
                    f"— Liq: {_esc(fmt_usd(p.get('liquidity_usd')))}"
                )
        if market.pair_url:
            lines.append("")
            lines.append(f"[View on DEX Screener]({_esc_url(market.pair_url)})")
    else:
        lines.append("• _No supported DEX pair found_")
    lines.append("")

    # Warnings
    if snapshot.warnings:
        lines.append("*⚠️ Notes*")
        for w in snapshot.warnings:
            lines.append(f"• {_esc(w)}")
        lines.append("")

    # Source notes
    if snapshot.source_notes:
        lines.append(f"_Sources: {_esc(', '.join(snapshot.source_notes))}_")

    return "\n".join(lines)


def build_help_message() -> str:
    return (
        "🤖 *Web3 Oasis*\n"
        "_Multichain blockchain intelligence_\n\n"
        "*Commands*\n"
        "• /analyze `<address>` — Analyze a token \\(EVM chains\\)\n"
        "• /help — Show this message\n\n"
        "*Supported EVM chains \\(Phase 1\\)*\n"
        "Ethereum, Base, Arbitrum, Optimism, Polygon, BNB Chain, "
        "Avalanche, Linea, zkSync Era, Scroll, Mantle, Blast, Gnosis, "
        "Celo, Unichain, World Chain, Soneium, Shape, Sonic, Berachain, "
        "Monad, Robinhood Chain, Arc, Ink, Abstract\n\n"
        "*Tips*\n"
        "• Just paste the contract address — Web3 Oasis detects the chain\n"
        "• If the contract exists on multiple chains, you'll be asked to pick one\n\n"
        "_Non\\-EVM support \\(Solana, Sui, Tron, TON\\), holders, risk, and full "
        "reports arrive in later phases\\._"
    )


def build_start_message() -> str:
    return (
        "👋 *Welcome to Web3 Oasis*\n\n"
        "Paste any token contract address and I'll analyze it across "
        "supported chains\\.\n\n"
        "Try:\n"
        "`/analyze 0x...`\n\n"
        "Type /help for commands\\."
    )


def build_chain_choice_message(address: str, chains: list) -> str:
    lines = ["⚠️ *Contract found on multiple networks*", ""]
    for c in chains:
        info = EVM_CHAINS.get(c, {})
        lines.append(f"• {_esc(info.get('name', c))}")
    lines.append("")
    lines.append("Please select the network:")
    return "\n".join(lines)