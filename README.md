# Web3 Oasis

Multichain crypto intelligence bot for Telegram.

## Phase 1 (this release)
- `/start`, `/help`, `/analyze <address>`
- Automatic EVM chain detection
- Token metadata, supply, market data, on-chain info
- Multi-chain disambiguation with inline buttons
- Caching, retries, clean error handling

## Roadmap
- **Phase 2:** Holders + pagination + concentration analysis
- **Phase 3:** Solana, Sui, Tron, TON adapters
- **Phase 4:** `/risk`, `/report`, wallet intelligence
- **Phase 5:** Historical snapshots (PostgreSQL)

## Deploy on Railway

### 1. Get your keys
- **Telegram bot token** — [@BotFather](https://t.me/BotFather) → `/newbot`
- **Alchemy API key** — [alchemy.com](https://alchemy.com) → free tier

### 2. Push to GitHub
```bash
git init
git add .
git commit -m "Web3 Oasis Phase 1"
git branch -M main
git remote add origin https://github.com/YOUR_USER/web3-oasis.git
git push -u origin main
```

3. Deploy on Railway

1. Go to railway.app → New Project → Deploy from GitHub repo
2. Select web3-oasis
3. Railway auto-detects the Dockerfile
4. Open the Variables tab and add:
   · TELEGRAM_BOT_TOKEN = your bot token
   · ALCHEMY_API_KEY = your alchemy key
   · (optional) LOG_LEVEL = INFO
5. Railway builds and starts the bot automatically

4. Test

On Telegram, message your bot:

```
/start
/help
/analyze 0x... (any ERC-20 contract)
```

Local development

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # fill in your keys
python bot.py
```

Architecture

```
adapters/    → per-ecosystem logic (EVM now; Solana/Sui/Tron later)
providers/   → external API clients (Alchemy, Blockscout, DEX Screener)
intelligence/→ analysis + report composition
telegram/    → handlers, keyboards, formatting
utils/       → cache, retry, http, validation, logging
```

License

MIT
