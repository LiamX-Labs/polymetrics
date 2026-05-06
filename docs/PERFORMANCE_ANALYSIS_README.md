# Polymarket Performance Analysis - Complete Guide

## Overview

This toolkit provides comprehensive analysis of Polymarket trading performance, including CSV exports and professional PDF reports.

---

## Generated Files

### 📊 CSV Data Files

#### From Polymarket API (Official Data)
1. **`polymarket_closed_positions_0x670aB958.csv`** (53KB, 239 positions)
   - Market names and descriptions
   - Entry/exit prices
   - Realized PnL per position
   - Timestamps (corrected)
   - Outcome (Up/Down)

2. **`polymarket_trades_0x670aB958.csv`** (381KB, 1,489 trades)
   - All individual trades
   - Market titles
   - Side (BUY/SELL)
   - Size and price
   - Transaction hashes

#### From On-Chain Analysis (Blockchain Data)
3. **`positions_0x670aB958.csv`** (40KB, 286 positions)
   - ERC-1155 token positions
   - Realized PnL from blockchain events
   - Duration and status (WIN/LOSS/BREAKEVEN)

4. **`trades_0x670aB958.csv`** (118KB, 607 trades)
   - On-chain BUY/SELL/REDEEM events
   - Token IDs
   - Price calculations from pUSD flows

---

### 📄 PDF Performance Report

**File:** `polymarket_performance_report_20260502_023510.pdf` (99KB, 11 pages)

#### Page 1: Performance Dashboard
- Cumulative PnL chart over time
- Win/Loss/Breakeven pie chart
- PnL distribution histogram
- PnL by outcome (Up vs Down)
- Hourly PnL analysis
- Summary metrics table

#### Page 2: Top Performers
- Top 10 winning trades with details
- Top 10 losing trades with details

#### Pages 3-11: All Closed Positions
- Exchange-style trade list
- All 239 positions sorted by close time
- Includes: Market, Side, Entry/Exit Price, Size, PnL, ROI%

---

## Key Performance Metrics

| Metric | Value |
|--------|-------|
| **Total Realized PnL** | **-$101.84** |
| Total Positions | 239 |
| Winning Positions | 136 (56.90%) |
| Losing Positions | 103 (43.10%) |
| Average Win | $3.93 |
| Average Loss | -$6.18 |
| Best Trade | +$18.24 |
| Worst Trade | -$14.97 |
| Risk/Reward Ratio | 0.64 |
| Profit Factor | 0.84 |
| Total Trades | 1,489 |

### What These Metrics Mean

- **Win Rate (56.9%)**: Barely above breakeven; need >60% for profitability
- **Risk/Reward Ratio (0.64)**: Average loss is 1.6x larger than average win - poor
- **Profit Factor (0.84)**: For every $1 made, you lost $1.19 - unprofitable
- **Total PnL (-$101.84)**: Net loss despite majority wins

---

## Analysis Tools

### 1. Polymarket API Fetcher
**Script:** `polymarket_api_fetcher.py`

Fetches official data from Polymarket's public API:
```bash
python3 polymarket_api_fetcher.py 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9
```

Features:
- Fetches closed positions with market names
- Retrieves all trades with timestamps
- Exports to CSV
- Generates summary statistics

### 2. On-Chain Position Analyzer
**Script:** `position_analyzer.py`

Reconstructs positions from blockchain events:
```bash
python3 position_analyzer.py 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9 \\
    --api-key ZA1X87TCSVVD53WECWZZ8UWJ7Y1VPKJ94A
```

Features:
- Fetches ERC-1155 token transfers
- Reconstructs position lifecycle (BUY → SELL → REDEEM)
- Calculates weighted average entry prices
- Tracks realized PnL using proper accounting

### 3. Wallet Balance Analyzer
**Script:** `wallet_analyzer.py`

Analyzes pUSD token flows:
```bash
python3 wallet_analyzer.py 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9 \\
    --api-key ZA1X87TCSVVD53WECWZZ8UWJ7Y1VPKJ94A
```

Features:
- Separates deposits/withdrawals from trading
- Identifies Polymarket contracts
- Calculates net balance changes

### 4. PDF Report Generator
**Script:** `generate_performance_report.py`

Creates professional PDF reports:
```bash
python3 generate_performance_report.py
```

Features:
- 6 performance visualizations
- Top 10 winners and losers
- Complete trade history table
- Exchange-style presentation
- Professional formatting

### 5. Jupyter Notebook
**File:** `performance_analysis.ipynb`

Interactive analysis notebook:
```bash
jupyter notebook performance_analysis.ipynb
```

Features:
- Step-by-step analysis
- Customizable visualizations
- Exports to PDF
- Easy to modify

---

## Understanding the Data

### Timestamp Fix
**Issue:** Original API calls had timestamps showing "1970-01-21"
**Fix:** Removed `/1000` division - API returns seconds, not milliseconds
**Result:** Correct dates now showing "2026-04-30"

### On-Chain vs API Discrepancy
- **On-chain:** 286 positions (includes all token movements)
- **Polymarket API:** 239 positions (only officially "closed" trades)
- **Difference:** 47 positions likely expired worthless or never settled

---

## Trading Strategy Issues Identified

### 1. Simultaneous Opposing Positions
The bot bought BOTH "Up" and "Down" on the same time windows:
- Example: Bitcoin 3:55PM-4:00PM ET
  - Lost -$10.01 on "Up" position
  - Lost -$14.97 on "Down" position
  - **Total loss:** -$24.98 on ONE time window

### 2. Poor Risk/Reward
- Average win: $3.93
- Average loss: -$6.18
- **Need to win 61% just to break even**
- Actual win rate: 56.9% → **guaranteed to lose money**

### 3. High-Frequency, Low-Edge Markets
- 1,489 trades in ~6 hours (4 trades/minute)
- Ultra-short 5-minute Bitcoin prediction markets
- Highly competitive, low-edge environment
- Copy trading signals had latency/quality issues

---

## Files You Can Share/Analyze

### For Quick Review
- `ANALYSIS_SUMMARY.md` - Executive summary
- `polymarket_performance_report_*.pdf` - Visual report

### For Detailed Analysis
- `polymarket_closed_positions_0x670aB958.csv` - Load into Excel
- `polymarket_trades_0x670aB958.csv` - All trade details

### For Technical Deep Dive
- `positions_0x670aB958.csv` - On-chain position tracking
- `performance_analysis.ipynb` - Interactive notebook

---

## Next Steps

### If Continuing Copy Trading
1. **Filter signals:** Don't copy all trades blindly
2. **Avoid opposing positions:** Add logic to prevent betting both sides
3. **Improve risk/reward:** Target 2:1 or better (avg win > 2x avg loss)
4. **Longer durations:** Avoid 5-minute markets, use 1-hour+ or event-based

### If Stopping Copy Trading
1. Review the PDF report to understand what went wrong
2. Consider manual trading on longer-duration, event-based markets
3. Focus on markets where you have informational edge

---

## Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
requests>=2.31.0
```

Install via conda:
```bash
conda install pandas numpy matplotlib seaborn requests
```

---

## Support & Documentation

- Polymarket API Docs: https://docs.polymarket.com
- Etherscan API Docs: https://docs.etherscan.io
- Analysis Summary: `ANALYSIS_SUMMARY.md`
- Setup Guide: `SETUP.md`
- Main README: `README.md`

---

## Author

Generated by Polymarket Analysis Toolkit
Analysis Date: May 2, 2026
Wallet: 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9
