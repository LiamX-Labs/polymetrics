# Polymarket Telegram Bot - Setup Guide

## Overview

The Polymarket Telegram Bot provides instant wallet analysis via Telegram messaging. Users can analyze any Polymarket wallet and receive:

- 📊 Performance metrics (PnL, win rate, profit factor)
- ⚡ HFT bot detection
- 📈 Visual charts (cumulative PnL, distributions, hourly analysis)
- 🏆 Top winning and losing trades
- 📉 Drawdown analysis and risk metrics

## Quick Start

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name: `Polymarket Analyzer` (or your preferred name)
4. Choose a username: `polymarket_analyzer_bot` (must end with 'bot')
5. BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
6. **Save this token securely** - you'll need it next

### 2. Configure the Bot

1. Navigate to the project directory:
```bash
cd /home/william/STRATEGIES/Polymarkets
```

2. Create `.env` file from the example:
```bash
cp .env.example .env
```

3. Edit `.env` and add your bot token:
```bash
nano .env
```

Add your token:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

Save and exit (Ctrl+X, Y, Enter)

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `python-telegram-bot` - Telegram bot framework
- `python-dotenv` - Environment variable management
- All existing dependencies (pandas, matplotlib, etc.)

### 4. Run the Bot

```bash
cd scripts
python3 telegram_bot.py
```

You should see:
```
✓ Configuration loaded successfully
✓ Polymarket Telegram Bot is running!
Press Ctrl+C to stop the bot
```

### 5. Test the Bot

1. Open Telegram
2. Search for your bot username (e.g., `@polymarket_analyzer_bot`)
3. Send `/start`
4. Follow the prompts:
   - Enter a wallet address: `0xc1200f03f07df479a041bb925a076d0b51c3b9f1`
   - Enter timeframe: `30`
5. Wait 30-60 seconds for analysis
6. Receive results with charts and metrics!

## Features

### Commands

- `/start` - Start new wallet analysis
- `/analyze` - Analyze another wallet (alias for /start)
- `/help` - Show help message with all features
- `/cancel` - Cancel current analysis

### Analysis Output

When you analyze a wallet, you receive:

1. **Summary Message**
   - Trading style classification (HFT Bot/Active Trader/Normal Trader)
   - Total PnL
   - Total positions
   - Win rate
   - Profit factor
   - Risk/reward ratio

2. **Detailed Metrics Table**
   - All performance metrics in formatted table
   - Win/loss statistics
   - Consecutive wins/losses
   - Max drawdown

3. **HFT Analysis**
   - Position frequency metrics
   - Time between positions
   - Trading pattern interpretation

4. **Visual Charts** (4 charts)
   - Cumulative PnL over time
   - Win/Loss distribution pie chart
   - PnL distribution histogram
   - Hourly PnL bar chart

5. **Top Trades**
   - Top 5 winning trades
   - Top 5 losing trades

## Optional: User Whitelist

To restrict bot access to specific users:

1. Get your Telegram user ID:
   - Message `@userinfobot` on Telegram
   - It will reply with your user ID (e.g., `123456789`)

2. Edit `.env` and add allowed user IDs:
```
ALLOWED_USER_IDS=123456789,987654321
```

Multiple users can be comma-separated.

If `ALLOWED_USER_IDS` is empty or not set, anyone can use the bot.

## Production Deployment

### Option 1: Local Server (Development)

Run the bot on your local computer:
```bash
python3 scripts/telegram_bot.py
```

**Pros**: Free, easy to test
**Cons**: Only works when computer is on

### Option 2: VPS (Recommended for Production)

Deploy to a VPS like DigitalOcean, Linode, or AWS EC2.

1. **Set up VPS**
```bash
ssh user@your-vps-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip git -y

# Clone/upload your project
git clone <your-repo> polymarket
cd polymarket

# Install dependencies
pip3 install -r requirements.txt

# Create .env file
nano .env
# Add your TELEGRAM_BOT_TOKEN
```

2. **Create systemd service** (runs bot automatically)
```bash
sudo nano /etc/systemd/system/polymarket-bot.service
```

Add:
```ini
[Unit]
Description=Polymarket Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/polymarket
Environment="PATH=/home/your-username/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 /home/your-username/polymarket/scripts/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Start the service**
```bash
sudo systemctl enable polymarket-bot
sudo systemctl start polymarket-bot
sudo systemctl status polymarket-bot
```

4. **View logs**
```bash
sudo journalctl -u polymarket-bot -f
```

**Cost**: $5-10/month for basic VPS

### Option 3: Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "scripts/telegram_bot.py"]
```

Run:
```bash
docker build -t polymarket-bot .
docker run -d --env-file .env polymarket-bot
```

## Troubleshooting

### Bot doesn't respond

1. **Check bot is running**:
```bash
ps aux | grep telegram_bot.py
```

2. **Check logs** for errors:
```bash
python3 scripts/telegram_bot.py
```

3. **Verify token** in `.env` is correct

### "TELEGRAM_BOT_TOKEN not set" error

- Make sure `.env` file exists
- Check token is correctly formatted (no quotes needed)
- Run from project root directory

### "No closed positions found" error

- Wallet has no trading history
- Try different wallet address
- Check wallet address is correct (42 characters, starts with 0x)

### Analysis takes too long

- Choose shorter timeframe (7 or 30 days)
- High-volume wallets may take 60+ seconds
- Consider increasing timeout if deploying to serverless

### Charts not displaying

- Check matplotlib is installed: `pip install matplotlib seaborn`
- Verify file permissions in bot/ directory
- Check logs for specific chart generation errors

## Performance Tips

### Caching

The bot automatically caches analysis results for 1 hour. If the same wallet+timeframe is requested within an hour, cached results are used instantly.

### Rate Limiting

By default, users can analyze up to 12 wallets per hour (one every 5 minutes). Modify `MAX_ANALYSES_PER_USER_PER_HOUR` in `bot/config.py` to adjust.

### Optimal Timeframes

- **7 days**: Fastest, good for recent performance
- **30 days**: Recommended balance of speed and data
- **90 days**: More comprehensive, slower
- **all**: Complete history, may be very slow for high-volume wallets

## Security Best Practices

1. **Never commit `.env` file** to git
   - Already in `.gitignore`
   - Keep bot token secret

2. **Use user whitelist** for private bots
   - Set `ALLOWED_USER_IDS` in `.env`

3. **Monitor usage** via logs
   - Track who uses the bot
   - Detect abuse or errors

4. **Keep dependencies updated**
```bash
pip install --upgrade python-telegram-bot
```

## Advanced Configuration

### Customize Chart Settings

Edit `bot/config.py`:
```python
CHART_DPI = 150  # Image quality (higher = better quality, larger files)
CHART_FORMAT = 'png'  # Image format
```

### Adjust Cache Duration

Edit `bot/config.py`:
```python
CACHE_DURATION_SECONDS = 3600  # 1 hour (default)
# Change to 1800 for 30 minutes, 7200 for 2 hours, etc.
```

### Custom Welcome Message

Edit `scripts/telegram_bot.py`, find the `start()` function and modify `welcome_message`.

## Support

### View Logs

When running directly:
```bash
python3 scripts/telegram_bot.py
```
Logs appear in console.

When running as systemd service:
```bash
sudo journalctl -u polymarket-bot -f
```

### Debug Mode

For more detailed logging, edit `scripts/telegram_bot.py`:
```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Change from INFO to DEBUG
)
```

## File Structure

```
/home/william/STRATEGIES/Polymarkets/
├── .env                    # Bot configuration (create from .env.example)
├── .env.example            # Template for .env
├── requirements.txt        # Python dependencies
├── scripts/
│   └── telegram_bot.py     # Main bot script
├── bot/
│   ├── __init__.py
│   ├── config.py           # Configuration and settings
│   ├── analysis.py         # Analysis logic wrapper
│   ├── charts.py           # Chart generation
│   └── formatters.py       # Text/table formatting
└── docs/
    └── TELEGRAM_BOT_SETUP.md  # This file
```

## Next Steps

1. ✅ Set up bot and test locally
2. ✅ Analyze a few wallets to verify functionality
3. 📝 Deploy to VPS for 24/7 availability (optional)
4. 🎨 Customize messages and settings (optional)
5. 📊 Consider adding HTML report generation (future enhancement)

## Example Usage Session

```
User: /start

Bot: 👋 Welcome to Polymarket Analyzer!
     Send me a wallet address (0x...)

User: 0xc1200f03f07df479a041bb925a076d0b51c3b9f1

Bot: ✅ Wallet: 0xc1200f03...c3b9f1
     How many days back to analyze?
     Send a number (e.g., 7, 30) or 'all'

User: 30

Bot: 🔍 Analyzing wallet...
     ⏳ This may take 30-60 seconds...
     📊 Fetching data from Polymarket API...
     ✅ Analysis complete!

Bot: [Sends summary message]
     📊 Polymarket Analysis Report
     Trading Style: 📊 Normal Trader
     Total PnL: $11,020.96
     Win Rate: 67.3%
     ...

Bot: [Sends metrics table]
Bot: [Sends HFT analysis]
Bot: [Sends 4 charts]
Bot: [Sends top trades]

Bot: ✅ Analysis complete!
     Want more?
     • Send /analyze to analyze another wallet
```

---

**Congratulations!** Your Polymarket Telegram Bot is now ready to use! 🎉
