# 📊 Polymetrics - Polymarket Wallet Analytics Platform

A comprehensive web-based analytics platform for analyzing Polymarket prediction market traders.

## 🌟 Features

### Core Platform Features
- **🏠 Dashboard**: Overview with top traders, recent analyses, and platform statistics
- **🔍 Wallet Analysis**: Deep-dive analytics for any Polymarket wallet address
- **🏆 Leaderboard**: Rankings by PnL, win rate, profit factor, and more
- **⚖️ Comparison Tool**: Side-by-side performance comparison of up to 4 wallets
- **📡 REST API**: Programmatic access to wallet data and leaderboards
- **💾 Database Storage**: Persistent storage with 1-hour caching

### Analytics Features
- 📈 **Performance Metrics**: PnL, win rate, profit factor, risk/reward ratio
- 📊 **Interactive Charts**: Cumulative PnL, distributions, drawdowns, scatter plots
- 🎯 **Trading Style Classification**: HFT Bot, Active Trader, Normal Trader
- 🔝 **Top Trades**: Best and worst performing positions
- 📋 **Complete History**: Searchable table of all closed positions
- 📱 **Mobile Responsive**: Beautiful design on all devices

### Design
- 🎨 **Stunning UI**: Purple/orange gradient dark theme with glassmorphism
- ✨ **Smooth Animations**: Hover effects, transitions, glows
- 🖱️ **Interactive**: Clickable rows, dynamic charts, live search
- 🎯 **Consistent**: Theme matches existing HTML reports

## 🚀 Quick Start

### Installation

1. **Install dependencies**:
```bash
pip install -r app/requirements.txt
```

2. **Run the platform**:
```bash
python run.py
```

3. **Access the platform**:
Open your browser to `http://localhost:5000`

### First Steps

1. **Analyze a wallet**: Enter any Polymarket wallet address in the search bar
2. **View leaderboard**: Click "Leaderboard" to see top traders
3. **Compare wallets**: Use the "Compare" feature to analyze multiple traders
4. **Explore the API**: Visit `/api/stats` for platform statistics

## 📁 Project Structure

```
Polymarkets/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── database.py           # Database initialization
│   ├── models/              # SQLAlchemy models
│   │   ├── wallet.py
│   │   ├── position.py
│   │   ├── market.py
│   │   └── ...
│   ├── routes/              # Flask routes/blueprints
│   │   ├── home.py          # Dashboard & leaderboard
│   │   ├── wallet.py        # Wallet analysis
│   │   ├── compare.py       # Comparison tool
│   │   └── api.py           # REST API
│   ├── services/            # Business logic
│   │   ├── fetcher.py       # Polymarket API client
│   │   ├── analyzer.py      # Performance analysis
│   │   └── cache.py         # Caching service
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── wallet_detail.html
│   │   ├── leaderboard.html
│   │   └── ...
│   └── static/              # Static files
│       ├── css/
│       │   └── polymetrics.css
│       └── js/
│           └── charts.js
├── config/
│   └── settings.py          # Configuration
├── database/
│   ├── schema.sql           # Database schema
│   └── polymetrics.db       # SQLite database (created on first run)
├── scripts/                 # Original CLI scripts (still functional)
├── data/                    # CSV data files
├── reports/                 # Generated reports
└── run.py                   # Application entry point
```

## 🌐 Routes

### Web Pages
- `/` - Homepage/dashboard
- `/leaderboard` - Full leaderboard
- `/wallet/analyze?address=0x...` - Analyze a wallet
- `/wallet/<address>` - View wallet details
- `/compare?wallet=0x1&wallet=0x2` - Compare wallets

### API Endpoints
- `GET /api/wallet/<address>` - Get wallet data
- `GET /api/wallet/<address>/positions` - Get wallet positions
- `GET /api/leaderboard?metric=total_pnl&limit=100` - Get leaderboard
- `GET /api/search?q=0x...` - Search wallets
- `GET /api/stats` - Platform statistics

## 🎯 Usage Examples

### Analyze a Wallet
1. Enter wallet address in search bar: `0x04b6d7e930cf9e493c5e6ef24b496294f95594c8`
2. Platform fetches data from Polymarket API
3. Analyzes performance metrics
4. Stores in database
5. Displays comprehensive report

### Compare Traders
1. Navigate to `/compare`
2. Enter 2-4 wallet addresses
3. View side-by-side comparison
4. See performance differences at a glance

### Use the API
```bash
# Get wallet data
curl http://localhost:5000/api/wallet/0x04b6d7e930cf9e493c5e6ef24b496294f95594c8

# Get leaderboard
curl http://localhost:5000/api/leaderboard?metric=win_rate&limit=50

# Get platform stats
curl http://localhost:5000/api/stats
```

## 🔧 Configuration

Edit `config/settings.py` to customize:

```python
# Database
DATABASE_PATH = 'database/polymetrics.db'

# Server
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# Caching
WALLET_CACHE_TIMEOUT = 3600  # 1 hour

# Pagination
POSITIONS_PER_PAGE = 50
LEADERBOARD_SIZE = 100
```

## 💾 Database

The platform uses SQLite for simplicity. Schema includes:

- **wallets**: Wallet addresses and performance metrics
- **positions**: Individual closed positions
- **markets**: Market metadata
- **wallet_snapshots**: Historical tracking
- **leaderboard_cache**: Cached rankings

Initialize database:
```bash
# Automatically created on first run
python run.py
```

## 🎨 Theming

The platform uses a consistent purple/orange gradient theme:

**Colors:**
- Primary Purple: `#7C3AED`
- Primary Orange: `#F97316`
- Success Green: `#10B981`
- Danger Red: `#EF4444`
- Dark Background: `#0F0A1E`

**Effects:**
- Glassmorphism cards
- Gradient backgrounds
- Hover glows
- Smooth transitions

## 📊 Analytics Details

### Trading Style Classification
- **HFT Bot**: >10 positions/hour on average
- **Active Trader**: >100 total positions
- **Normal Trader**: All others

### Key Metrics
- **PnL**: Realized profit and loss
- **Win Rate**: Percentage of profitable positions
- **Profit Factor**: Total wins ÷ Total losses
- **Risk/Reward**: Average win ÷ Average loss
- **ROI**: Return on investment per position

### Charts
1. Cumulative PnL Over Time
2. Win/Loss Distribution (pie chart)
3. PnL Distribution (histogram)
4. PnL by Outcome (Yes/No)
5. PnL by Hour of Day
6. Position Size Distribution
7. ROI Distribution
8. Drawdown Analysis
9. Entry Price vs PnL (scatter)
10. Position Size vs PnL (scatter)

## 🔌 Integration with Existing Scripts

Your original CLI scripts still work! The platform uses the same analysis logic:

```bash
# Original workflow still functional
cd scripts
python polymarket_api_fetcher.py 0xWALLET
python generate_html_report.py
```

The web platform provides a GUI alternative with additional features:
- Multi-wallet tracking
- Leaderboards
- Comparisons
- API access
- Persistent storage

## 🚦 Performance

- **Caching**: 1-hour cache prevents excessive API calls
- **Database**: Indexed queries for fast lookups
- **Pagination**: 50 positions per page for large wallets
- **Lazy Loading**: Charts load on-demand per tab

## 🐛 Troubleshooting

**Database errors:**
```bash
# Delete and recreate database
rm database/polymetrics.db
python run.py
```

**Module import errors:**
```bash
# Install missing dependencies
pip install -r app/requirements.txt
```

**API errors:**
- Check internet connection
- Verify wallet address is valid
- Try again (rate limiting may occur)

## 🔐 Security Notes

- This is a read-only analytics platform
- No private keys or wallet control
- All data from public Polymarket API
- Suitable for local/internal deployment
- For production: add authentication, HTTPS, rate limiting

## 📝 Development

### Adding New Features

1. **New route**: Create blueprint in `app/routes/`
2. **New model**: Add to `app/models/`
3. **New service**: Add to `app/services/`
4. **New template**: Add to `app/templates/`

### Running in Development

```bash
# Enable debug mode
export DEBUG=true
python run.py
```

### Database Migrations

```bash
# Reset database
rm database/polymetrics.db

# Schema changes: Update database/schema.sql and app/models/
```

## 🎉 Features Comparison

| Feature | CLI Scripts | Web Platform |
|---------|-------------|--------------|
| Single wallet analysis | ✅ | ✅ |
| Multiple wallets | ❌ | ✅ |
| Leaderboards | ❌ | ✅ |
| Comparisons | ❌ | ✅ |
| API access | ❌ | ✅ |
| Persistent storage | ❌ | ✅ |
| Real-time search | ❌ | ✅ |
| Mobile friendly | ❌ | ✅ |

## 📚 Next Steps

1. ✅ **Analyze wallets**: Start with known traders
2. ✅ **Build leaderboard**: Analyze top performers
3. 🔄 **Compare strategies**: Use comparison tool
4. 📈 **Track over time**: Re-analyze for historical tracking
5. 🔌 **Integrate**: Use API for custom applications

## 🤝 Credits

- **Data Source**: [Polymarket](https://polymarket.com)
- **Charts**: [Plotly.js](https://plotly.com/javascript/)
- **Framework**: Flask + SQLAlchemy
- **Theme**: Custom purple/orange gradient design

---

**Built with ❤️ for Polymarket traders**

*Last Updated: May 6, 2026*
