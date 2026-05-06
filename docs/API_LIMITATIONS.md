# Polymarket API Limitations & Workarounds

## Overview

The Polymarket Data API has certain limitations that affect how much historical data can be fetched. This document explains these limitations and provides workarounds.

---

## API Endpoints

### 1. `/closed-positions` Endpoint
**Status:** ✅ **No Limitations**

- **Offset Limit:** None - can fetch all historical positions
- **Reliability:** 100% complete data
- **Use Case:** Primary data source for analysis
- **Data Included:**
  - Market title and outcome
  - Realized PnL per position
  - Average entry price
  - Total shares bought
  - Current/exit price
  - Number of trades per position
  - Timestamps

**Recommendation:** Use this as your primary data source for performance analysis.

---

### 2. `/trades` Endpoint
**Status:** ⚠️ **Limited to ~4000 trades**

- **Offset Limit:** Maximum offset of 3000
- **Max Trades:** ~4000 (3000 offset + 1000 limit per request)
- **Reliability:** May be incomplete for high-volume wallets
- **Workaround:** Use timeframe filtering (days back)
- **Data Included:**
  - Individual trade details
  - Buy/sell side
  - Size and price
  - Transaction hashes
  - Timestamps

**Recommendation:** Use for recent trade details, but don't rely on it for complete historical data.

---

## Workarounds for High-Volume Wallets

### Option 1: Use Timeframe Filtering (Recommended)

When a wallet has >4000 trades, specify a shorter timeframe to ensure complete data:

```bash
python3 polymarket_api_fetcher.py
# When prompted: "How many days back to analyze?"
# Enter: 7, 14, or 30 (depending on trade volume)
```

**How it works:**
- Script sorts trades by timestamp (most recent first)
- Fetches trades until it reaches your cutoff date
- Stops early if all trades within timeframe are fetched
- **Guarantees complete data** within your specified timeframe

### Option 2: Focus on Closed Positions

The `/closed-positions` endpoint has NO offset limit:

```bash
python3 polymarket_api_fetcher.py
# This will fetch ALL positions regardless of count
```

**What you get:**
- Complete position history
- All realized PnL data
- Trade count per position (not individual trades)
- 100% reliable data

### Option 3: Use Blockchain Data

For complete trade history beyond API limits, use the blockchain analyzer:

```bash
python3 position_analyzer.py
```

**How it works:**
- Fetches data directly from Polygon blockchain via Etherscan
- Reconstructs positions from ERC-1155 token transfers
- No API offset limits (different rate limits apply)
- Complete historical data

---

## API Limit Warning

When you hit the trades API limit, you'll see this warning:

```
================================================================================
⚠️  WARNING: Reached Polymarket API offset limit (3000)
================================================================================
  Total trades fetched: 4000
  This wallet may have more than 4000 trades.

  To ensure complete data, specify a shorter timeframe:
    - Run with fewer days back (e.g., 7, 14, or 30 days)
    - This will fetch all trades within that period
================================================================================
```

---

## Best Practices

### For Daily/Weekly Analysis
**Use:** 7-14 day timeframe
```bash
python3 polymarket_api_fetcher.py
# Days back: 7 or 14
```

### For Monthly Reports
**Use:** 30 day timeframe
```bash
python3 polymarket_api_fetcher.py
# Days back: 30
```

### For Complete Historical Analysis
**Use:** Closed positions endpoint (automatic)
```bash
python3 polymarket_api_fetcher.py
# Will fetch ALL positions regardless of timeframe
```

### For Complete Trade History
**Use:** Blockchain analyzer
```bash
python3 position_analyzer.py
```

---

## Data Completeness Summary

| Data Type | API Limit | Completeness | Recommended For |
|-----------|-----------|--------------|-----------------|
| **Closed Positions** | None | 100% | Performance analysis, PnL tracking |
| **Recent Trades (7 days)** | 3000 offset | 100% (if <4000 trades) | Recent activity analysis |
| **Recent Trades (30 days)** | 3000 offset | 100% (if <4000 trades) | Monthly reports |
| **All Historical Trades** | 3000 offset | Limited (~4000) | Not recommended |
| **Blockchain Data** | Rate limits only | 100% | Complete historical analysis |

---

## Technical Details

### Closed Positions API
- **Endpoint:** `GET /closed-positions`
- **Parameters:** `user`, `limit`, `offset`, `sortBy`, `sortDirection`
- **Max per request:** 50 positions
- **Max offset:** None (unlimited pagination)
- **Sort options:** REALIZEDPNL, TITLE, PRICE, AVGPRICE, TIMESTAMP

### Trades API
- **Endpoint:** `GET /trades`
- **Parameters:** `user`, `limit`, `offset`, `side`, `takerOnly`
- **Max per request:** 1000 trades
- **Max offset:** 3000 ⚠️
- **Hard limit:** Cannot fetch beyond offset 3000
- **No time filtering:** Cannot specify startTime/endTime

---

## Questions?

- Check the [QUICKSTART.md](../QUICKSTART.md) for usage examples
- See [README.md](../README.md) for full documentation
- Review the code in [polymarket_api_fetcher.py](../scripts/polymarket_api_fetcher.py)
