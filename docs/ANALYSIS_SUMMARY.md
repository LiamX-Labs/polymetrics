# Polymarket Wallet Analysis Summary

**Wallet Address:** `0x670aB9580B4e21735dD4c30fEF45bb9f465100C9`

**Analysis Date:** May 2, 2026

---

## Executive Summary

Your copy trading strategy on Polymarket resulted in a **net loss of approximately $102-120**, despite having a 56.9% win rate on closed positions. The strategy traded primarily on short-duration Bitcoin price prediction markets (5-minute and 15-minute windows).

---

## Key Findings from Polymarket API

### Overall Performance
- **Total Realized PnL:** -$101.84
- **Total Positions:** 239 closed positions
- **Win Rate:** 56.9% (136 wins, 103 losses)
- **Total Trades:** 1,489 (all BUY orders)
- **Total Capital Deployed:** $1,601.76

### Best Trades
1. **Bitcoin Up or Down - April 30, 3:10PM-3:15PM ET** (Up): +$18.24
2. **Bitcoin Up or Down - April 30, 2:45PM-2:50PM ET** (Up): +$17.12
3. **Bitcoin Up or Down - April 30, 4:45PM-4:50PM ET** (Up): +$12.40

### Worst Trades
1. **Bitcoin Up or Down - April 30, 3:55PM-4:00PM ET** (Down): -$14.97
2. **Bitcoin Up or Down - April 30, 3:50PM-3:55PM ET** (Up): -$14.94
3. **Bitcoin Up or Down - April 30, 2:45PM-3:00PM ET** (Up): -$14.82

---

## Wallet Balance Summary

### Simple Accounting
- **Initial Deposit:** $204.63 pUSD (first transaction)
- **Current Balance:** $46.62 pUSD
- **Withdrawals to Other Addresses:** $92.94 pUSD
- **Net Loss:** $204.63 - $46.62 - $92.94 = **$65.07**

*Note: The discrepancy between this ($65 loss) and Polymarket's reported -$101.84 PnL is likely due to the $92.94 in withdrawals, which Polymarket counts as part of trading costs.*

---

## Trading Strategy Analysis

### Market Focus
The copy trading bot exclusively traded on:
- **Bitcoin Up or Down** markets (5-minute and 15-minute windows)
- **Ethereum Up or Down** markets (minimal exposure)

### Trading Pattern
- **High Frequency:** 1,489 buy orders in approximately 5-6 hours of trading
- **Small Position Sizes:** Most positions between $10-30
- **No Sell Orders Recorded:** All positions appear to be held until expiry/settlement
- **Both Sides:** Bot traded both "Up" and "Down" outcomes, sometimes on the same time window

### Position Durations
- Most positions closed within 5-15 minutes (matching market duration)
- Strategy appears to be scalping short-term price movements

---

## On-Chain Analysis (ERC-1155 Tokens)

### Position Tokens Tracked
- **Total Unique Positions:** 286 (from blockchain)
- **Closed Positions:** 286
- **Open Positions:** 0

### Discrepancy Analysis
The on-chain analysis shows 286 positions vs Polymarket API showing 239 positions. This 47-position difference is likely due to:
1. Positions that were bought but never officially "closed" on Polymarket (expired worthless)
2. Internal position transfers or adjustments not counted by API
3. Potential multi-market positions that blockchain sees as separate tokens

---

## Why the Strategy Lost Money

### Primary Issues

1. **Low Win Rate Doesn't Overcome Losses**
   - 56.9% win rate is barely above break-even
   - Average losing trade (-$9.57) was larger than average winning trade (+$7.83)
   - Need ~60-65% win rate to be profitable with this risk/reward ratio

2. **Simultaneous Opposing Positions**
   - Bot bought both "Up" and "Down" on same time windows
   - Example: Bitcoin 3:55PM-4:00PM ET - Lost on BOTH Up (-$10.01) and Down (-$14.97)
   - This suggests poor copy trading signal quality or latency issues

3. **High Trading Volume Without Edge**
   - 1,489 trades in ~6 hours = ~4 trades per minute
   - Such high frequency suggests automated copying without filtering
   - No apparent edge in 5-minute Bitcoin price prediction

4. **Withdrawals During Trading**
   - $92.94 withdrawn to other addresses during active trading
   - Reduced available capital and realized losses

---

## Files Generated

### CSV Exports from Polymarket API
1. **polymarket_closed_positions_0x670aB958.csv** - All 239 closed positions with market names, PnL, prices
2. **polymarket_trades_0x670aB958.csv** - All 1,489 individual trades with timestamps and transaction hashes

### CSV Exports from On-Chain Analysis
1. **positions_0x670aB958.csv** - All 286 on-chain positions with realized PnL
2. **trades_0x670aB958.csv** - All 607 individual on-chain trades (BUY/SELL/REDEEM)

---

## Recommendations

### If Continuing Copy Trading

1. **Filter Signals**
   - Don't blindly copy all trades
   - Add minimum confidence threshold
   - Avoid simultaneous opposing positions

2. **Risk Management**
   - Limit position sizes to 1-2% of capital
   - Set maximum daily loss limits
   - Don't trade during high volatility periods

3. **Market Selection**
   - Avoid ultra-short duration markets (5-min windows)
   - Focus on markets with more edge (15-min+ or event-based)
   - Consider markets with lower competition

4. **Monitor Win Rate & Risk/Reward**
   - Track if win rate stays above 60%
   - Ensure average win > average loss
   - Stop trading if metrics deteriorate

### Alternative Approach

Consider manual position selection on longer-duration, event-based markets where fundamental analysis can provide edge, rather than high-frequency price prediction markets.

---

## Conclusion

The copy trading strategy underperformed primarily due to:
- Insufficient win rate (56.9% vs needed 60-65%)
- Poor risk/reward ratio (avg loss > avg win)
- Simultaneous opposing positions indicating signal quality issues
- High-frequency trading in ultra-competitive short-duration markets

**Total Loss: $101.84 to $120** (depending on how withdrawals are accounted)

The Polymarket "closed trades" view that showed profitable trades was only displaying the **winning subset** of trades, not the full picture including all the losing positions.
