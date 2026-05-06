# 🚀 Polymetrics Platform - Quick Start Guide

Get your Polymarket analytics platform running in 60 seconds!

## Prerequisites

- Python 3.8+
- Internet connection (for fetching Polymarket data)

## Installation

### 1. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install Flask Flask-SQLAlchemy Flask-CORS
```

(Pandas, NumPy, and other dependencies are already installed from your existing setup)

## Running the Platform

### Start the Server

```bash
python run.py
```

You should see:

```
============================================================
🚀 Starting Polymetrics - Polymarket Analytics Platform
============================================================

Server running at: http://0.0.0.0:5000
Debug mode: True
Database: /home/william/STRATEGIES/Polymarkets/database/polymetrics.db

Press CTRL+C to stop the server
```

### Access the Platform

Open your web browser and navigate to:

```
http://localhost:5000
```

## First Steps

### 1. Analyze Your First Wallet

On the homepage, use the search bar at the top:

1. Enter a Polymarket wallet address (e.g., `0x04b6d7e930cf9e493c5e6ef24b496294f95594c8`)
2. Click "Analyze"
3. Wait 5-10 seconds while data is fetched
4. View the comprehensive analysis!

### 2. Explore the Dashboard

- **Homepage**: Overview of platform statistics and top traders
- **Leaderboard**: Rankings by PnL, win rate, and profit factor
- **Compare**: Side-by-side comparison of multiple wallets

### 3. Use the API

Try these API endpoints:

```bash
# Get platform statistics
curl http://localhost:5000/api/stats

# Get leaderboard
curl http://localhost:5000/api/leaderboard?limit=10

# Get wallet data (after analyzing it first)
curl http://localhost:5000/api/wallet/0x04b6d7e930cf9e493c5e6ef24b496294f95594c8
```

## Example Wallets to Analyze

Here are some example wallet addresses from your existing reports:

- `0x04b6d7e9` (from your data files)
- `0xa877f7dd`
- `0x0e06348f`
- `0xe613a7ce`
- `0xbe601e36`

(Use the full addresses from the reports/ directory filenames)

## Features Tour

### Homepage (/)
- Platform statistics
- Top traders by PnL, win rate, and profit factor
- Recently analyzed wallets
- Quick search bar

### Wallet Analysis (/wallet/<address>)
- Comprehensive performance metrics
- 10+ interactive charts
- Top winning and losing trades
- Searchable position history
- Trading style classification

### Leaderboard (/leaderboard)
- Top 100 traders ranked by total PnL
- Sortable columns
- Clickable rows to view details

### Compare (/compare)
- Add up to 4 wallet addresses
- Side-by-side performance comparison
- Quick links to individual analyses

## Tips

### Caching
- Wallet analyses are cached for 1 hour
- Re-analyzing before 1 hour uses cached data
- After 1 hour, fresh data is fetched from Polymarket

### Performance
- First analysis of a wallet takes 5-15 seconds
- Subsequent views are instant (cached)
- Database stores all analyses for fast retrieval

### Multiple Wallets
- Analyze as many wallets as you want!
- Build your own leaderboard
- Compare different trading strategies

## Troubleshooting

### Port Already in Use

If port 5000 is busy:

```bash
# Edit config/settings.py
PORT = 8000  # Change to any available port

# Or set environment variable
export PORT=8000
python run.py
```

### Module Not Found

```bash
# Make sure you're in the venv
source venv/bin/activate

# Install missing packages
pip install Flask Flask-SQLAlchemy Flask-CORS
```

### Database Issues

```bash
# Reset the database
rm database/polymetrics.db

# Restart the server (will recreate database)
python run.py
```

## Integration with Existing Workflow

Your existing CLI scripts still work perfectly:

```bash
cd scripts

# Fetch data
python polymarket_api_fetcher.py 0xWALLET

# Generate HTML report
python generate_html_report.py
```

The web platform **adds** these features:
- Multi-wallet tracking and storage
- Leaderboards and rankings
- Wallet comparison tool
- REST API for programmatic access
- Persistent database storage
- Web-based interface

## Next Steps

1. ✅ Analyze 5-10 interesting wallets
2. ✅ Check out the leaderboard
3. ✅ Compare 2-3 trading styles
4. ✅ Experiment with the API
5. 🎯 Build your custom dashboards using the API!

## Customization

### Change Theme Colors

Edit `config/settings.py`:

```python
THEME = {
    'primary_purple': '#7C3AED',  # Change these!
    'primary_orange': '#F97316',
    # ... more colors
}
```

### Adjust Cache Duration

```python
WALLET_CACHE_TIMEOUT = 3600  # Seconds (1 hour)
```

### Change Pagination

```python
POSITIONS_PER_PAGE = 50  # Positions per page
LEADERBOARD_SIZE = 100   # Max leaderboard entries
```

## Support

- Check [PLATFORM_README.md](PLATFORM_README.md) for detailed documentation
- View the [original project README](README.md) for CLI script usage
- Check `app/` directory for code structure

---

**Happy analyzing!** 📊

*Built for Polymarket traders, by Polymarket enthusiasts*
