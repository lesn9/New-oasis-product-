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