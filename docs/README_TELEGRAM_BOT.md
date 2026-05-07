# Polymarket Telegram Bot

Instant Polymarket wallet analysis via Telegram! 📱

## Quick Start

### 1. Get a Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow prompts to create your bot
4. Save the token

### 2. Configure

```bash
# Copy environment template
cp .env.example .env

# Edit and add your token
nano .env
```

### 3. Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python3 scripts/telegram_bot.py
```

### 4. Use the Bot

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Enter wallet address
5. Get instant analysis! 📊

## Features

✅ **HFT Bot Detection** - Identifies algorithmic trading patterns
✅ **Complete Metrics** - PnL, win rate, profit factor, drawdown
✅ **Visual Charts** - Cumulative PnL, distributions, hourly analysis
✅ **Top Trades** - Best and worst positions
✅ **Fast** - Results in 30-60 seconds
✅ **Caching** - Instant re-queries within 1 hour

## What You Get

When you analyze a wallet, the bot sends:

1. 📊 **Summary** - Trading style, PnL, win rate
2. 📋 **Metrics Table** - Detailed performance stats
3. 🤖 **HFT Analysis** - Trading pattern detection
4. 📈 **4 Charts** - Visual performance analysis
5. 🏆 **Top Trades** - Best and worst positions

## Example Output

```
📊 Polymarket Analysis Report

Wallet: 0xc1200f03...c3b9f1
Trading Style: 📊 Normal Trader

💰 Performance
• Total PnL: $11,020.96
• Positions: 1,750
• Win Rate: 67.3%
• Profit Factor: 1.87

⚡ Trading Activity
• Positions/Hour: 4.5
• Time Between Positions: 5.0 min
• Total Trades: 1,254
```

Plus 4 visual charts and detailed metrics!

## Commands

- `/start` - Begin analysis
- `/analyze` - Analyze another wallet
- `/help` - Show help
- `/cancel` - Cancel current analysis

## Configuration

### Optional: Restrict Access

Add allowed user IDs to `.env`:
```
ALLOWED_USER_IDS=123456789,987654321
```

Get your Telegram ID from [@userinfobot](https://t.me/userinfobot).

## Deployment

### Local (Development)

```bash
python3 scripts/telegram_bot.py
```

### Production (VPS)

See [full setup guide](docs/TELEGRAM_BOT_SETUP.md) for systemd service configuration.

**Recommended VPS providers:**
- DigitalOcean ($5/month)
- Linode ($5/month)
- AWS EC2 (t2.micro free tier)

## Files

```
bot/
├── __init__.py
├── analysis.py      # Wraps existing analysis scripts
├── charts.py        # Matplotlib chart generation
├── config.py        # Bot configuration
└── formatters.py    # Message formatting

scripts/
└── telegram_bot.py  # Main bot script

.env.example         # Configuration template
README_TELEGRAM_BOT.md  # This file
```

## Troubleshooting

**Bot doesn't respond?**
- Check bot is running: `ps aux | grep telegram_bot`
- Verify token in `.env`

**"No positions found" error?**
- Wallet has no trading history
- Try a different wallet or timeframe

**Analysis too slow?**
- Use shorter timeframe (7 or 30 days)
- High-volume wallets take longer

## Documentation

📖 **Full Setup Guide**: [docs/TELEGRAM_BOT_SETUP.md](docs/TELEGRAM_BOT_SETUP.md)

Includes:
- Detailed setup instructions
- Production deployment guide
- Troubleshooting
- Advanced configuration
- Security best practices

## Support

**View logs:**
```bash
# If running directly
python3 scripts/telegram_bot.py

# If running as systemd service
sudo journalctl -u polymarket-bot -f
```

## Tech Stack

- **python-telegram-bot** - Telegram Bot API wrapper
- **matplotlib/seaborn** - Chart generation
- **pandas** - Data analysis
- **Existing analysis scripts** - Reused from generate_performance_report.py

## Roadmap

Future enhancements:
- [ ] HTML report generation with interactive charts
- [ ] PDF report generation via Telegram
- [ ] Multi-wallet comparison
- [ ] Scheduled analysis (daily/weekly reports)
- [ ] Position alerts

## License

Same as main project.

---

**Ready to analyze wallets on the go? Get started now!** 🚀

For detailed setup instructions, see [TELEGRAM_BOT_SETUP.md](docs/TELEGRAM_BOT_SETUP.md)
