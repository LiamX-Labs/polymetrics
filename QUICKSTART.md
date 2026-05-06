# Quick Start Guide

## 🎯 TL;DR - Fastest Way to Analyze

```bash
# 1. Install dependencies
pip install pandas numpy matplotlib seaborn requests

# 2. Go to scripts directory
cd scripts

# 3. Run the data fetcher (enter wallet when prompted)
python3 polymarket_api_fetcher.py

# 4. Generate PDF report
python3 generate_performance_report.py

# Done! Check ../reports/ for your PDF
```

---

## 📱 Interactive Mode (Easiest)

All scripts support interactive mode - just run them without arguments:

```bash
cd scripts

# Fetch data from Polymarket
python3 polymarket_api_fetcher.py
Enter wallet address: 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9

# Analyze wallet balance
python3 wallet_analyzer.py
Enter wallet address: 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9

# Reconstruct positions from blockchain
python3 position_analyzer.py
Enter wallet address: 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9

# Generate PDF report (no wallet needed - uses latest data)
python3 generate_performance_report.py
```

---

## 💻 Command Line Mode (For Scripts)

```bash
cd scripts

# All-in-one
WALLET="0x670aB9580B4e21735dD4c30fEF45bb9f465100C9"

python3 polymarket_api_fetcher.py $WALLET
python3 wallet_analyzer.py $WALLET
python3 position_analyzer.py $WALLET
python3 generate_performance_report.py
```

---

## 🔑 API Keys

**Default included** - No need to provide API key!

All scripts use this working key by default:
```
ZA1X87TCSVVD53WECWZZ8UWJ7Y1VPKJ94A
```

To use your own (optional):
```bash
python3 wallet_analyzer.py 0xWALLET --api-key YOUR_KEY
python3 position_analyzer.py 0xWALLET --api-key YOUR_KEY
```

---

## 📊 What Gets Generated

### After running `polymarket_api_fetcher.py`:

```
data/
├── polymarket_closed_positions_0x670aB958.csv
└── polymarket_trades_0x670aB958.csv
```

### After running `generate_performance_report.py`:

```
reports/ (or current directory)
└── polymarket_performance_report_20260502_130902.pdf
```

### After running `position_analyzer.py`:

```
scripts/ (current directory)
├── positions_0x670aB958.csv
└── trades_0x670aB958.csv
```

---

## ⚡ One-Liner for Everything

```bash
cd scripts && \
python3 polymarket_api_fetcher.py 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9 && \
python3 generate_performance_report.py
```

---

## 🎓 What Each Tool Does

| Script | What it does | Output |
|--------|-------------|---------|
| `polymarket_api_fetcher.py` | Gets official trade data from Polymarket | CSV files in `data/` |
| `wallet_analyzer.py` | Analyzes pUSD deposits/withdrawals | Terminal summary |
| `position_analyzer.py` | Reconstructs positions from blockchain | CSV files in `scripts/` |
| `generate_performance_report.py` | Creates PDF with charts & tables | PDF in `reports/` |

---

## 🆘 Common Issues

**"No data files found"**
→ Run `polymarket_api_fetcher.py` first

**"Module not found"**
→ Run `pip install -r requirements.txt`

**"API Error"**
→ Wait 30 seconds, try again (rate limit)

---

## 📚 Next Steps

1. Open the generated PDF report in `reports/`
2. Review CSV files in `data/` with Excel/Sheets
3. Check [README.md](README.md) for full documentation
4. See [docs/](docs/) for detailed guides

---

**Ready to analyze? Just run:**
```bash
cd scripts && python3 polymarket_api_fetcher.py
```

---

## 🔧 Troubleshooting

### NumPy Version Error
If you see: `"A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x..."`

**Fix:**
```bash
pip install 'numpy<2'
```

This is already specified in `requirements.txt`, but if you have numpy 2.x installed, downgrade it.

### All Scripts Fixed and Working
✅ Interactive wallet prompts  
✅ Default API key included  
✅ NumPy compatibility fixed  
✅ Auto file detection  
✅ Clean organized structure  

**Everything is ready to use!**
