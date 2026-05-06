# HTML Report Features Guide

## Overview

The interactive HTML report provides a modern, mobile-friendly interface for analyzing Polymarket trading performance.

## Key Features

### 1. Tab-Based Navigation

The report is organized into 4 main tabs for easy navigation:

```
┌─────────────────────────────────────────────────────────────┐
│ [Overview] [Charts] [Top Trades] [All Positions]            │
└─────────────────────────────────────────────────────────────┘
```

- **Overview** - Quick summary with key metrics
- **Charts** - All interactive visualizations
- **Top Trades** - Best and worst performers
- **All Positions** - Complete searchable history

### 2. Performance Metrics Cards

The Overview tab displays 18 key metrics in an easy-to-scan grid:

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Total PnL       │ Trading Style   │ Total Positions │ Win Rate        │
│ $11,076.82      │ 📊 Normal       │ 1,750          │ 67.26%          │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Average Win     │ Average Loss    │ Best Trade      │ Worst Trade     │
│ $14.55          │ -$8.67          │ $312.45         │ -$156.23        │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Risk/Reward     │ Profit Factor   │ Max Drawdown    │ Max Consec Wins │
│ 1.68            │ 1.88            │ -$487.92        │ 12              │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

Each card is color-coded:
- 🟢 **Green border** - Positive values (wins, profits)
- 🔴 **Red border** - Negative values (losses, drawdowns)
- ⚪ **Gray border** - Neutral metrics (counts, ratios)

### 3. Interactive Charts (Plotly.js)

All 10 charts support full interactivity:

**Mouse Actions:**
- **Hover** - Show detailed values
- **Click & Drag** - Zoom into specific area
- **Double-Click** - Reset zoom
- **Scroll** - Zoom in/out

**Touch Actions (Mobile):**
- **Tap** - Show values
- **Pinch** - Zoom
- **Swipe** - Pan

**Available Charts:**
1. Cumulative PnL Over Time (line chart with fill)
2. Win/Loss Distribution (donut pie chart)
3. PnL Distribution (histogram)
4. PnL by Outcome (bar chart)
5. PnL by Hour of Day (bar chart)
6. Position Size Distribution (histogram)
7. ROI Distribution (histogram)
8. Drawdown Over Time (area chart)
9. Entry Price vs PnL (scatter plot)
10. Position Size vs PnL (scatter plot)

### 4. HFT Bot Detection

The report automatically classifies trading style:

```
Trading Style: ⚡ HFT Bot
• Very rapid position taking (<5 min between trades)
• High volume (>10 positions/hour)
• Avg: 45.5 positions/hour
• Median time between: 0.3 minutes
```

**Classifications:**
- ⚡ **HFT Bot** - >10 pos/hr AND <5 min between
- 📈 **Active Trader** - >5 pos/hr
- 📊 **Normal Trader** - ≤5 pos/hr

### 5. Search & Filter

The "All Positions" tab includes a powerful search feature:

```
┌─────────────────────────────────────────────────────────────┐
│ Search: [BTC                                             ] │
└─────────────────────────────────────────────────────────────┘

Results: 47 positions found (filtered from 1,750)
```

Search across:
- Market titles
- Outcomes (Yes/No/Up/Down)
- PnL amounts
- Dates/times
- Entry/exit prices

### 6. Pagination

Large position lists are paginated for performance:

```
[First] [Previous] [1] [2] [3] ... [35] [Next] [Last]
                        ^^^ Current page
```

- 50 positions per page
- Fast navigation
- Smooth page transitions
- Maintains scroll position

### 7. Top Trades Tables

Clean, sortable tables for winners and losers:

**Top 10 Winning Trades**
```
┌────────────────────────────┬─────────┬──────────┬─────────┐
│ Market                     │ Outcome │ PnL      │ Entry   │
├────────────────────────────┼─────────┼──────────┼─────────┤
│ BTC >$95K by 5pm?         │ Yes     │ $312.45  │ $0.6523 │
│ Trump wins Pennsylvania?   │ Yes     │ $287.90  │ $0.7234 │
│ ...                        │ ...     │ ...      │ ...     │
└────────────────────────────┴─────────┴──────────┴─────────┘
```

- Green highlighting for wins
- Red highlighting for losses
- Hover for full market titles

### 8. Responsive Design

The report adapts to all screen sizes:

**Desktop (>768px):**
- Multi-column grid layouts
- Side-by-side charts
- Full-width tables

**Tablet (480-768px):**
- 2-column metrics grid
- Stacked charts
- Horizontal scrolling for tables

**Mobile (<480px):**
- Single column layout
- Touch-friendly buttons
- Optimized font sizes
- Compact tables

### 9. Color Coding

Consistent color scheme throughout:

- **Primary Blue** (#2E86AB) - Headers, accents
- **Success Green** (#06A77D) - Positive PnL, wins
- **Danger Red** (#D72638) - Negative PnL, losses
- **Warning Orange** (#FFA69E) - Neutral/breakeven

### 10. Print Support

The report includes print-optimized styles:

```css
@media print {
  - Remove navigation tabs
  - Remove search boxes
  - Expand all sections
  - Add page breaks
  - Simplify shadows/borders
}
```

Print preview shows clean, professional layout.

## Technical Specifications

### File Size
- Base template: ~40KB
- With 1,000 positions: ~400KB
- With 5,000 positions: ~1.5MB
- Scales linearly with position count

### Browser Support
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile Safari (iOS 14+)
- ✅ Chrome Mobile (Android 10+)

### Performance
- **Load time**: <2 seconds on 4G
- **Render time**: <500ms for 5,000 positions
- **Chart render**: <200ms per chart
- **Search**: Real-time (<50ms)

### Dependencies
- **Plotly.js** (2.27.0) - Loaded from CDN
- No other external dependencies
- Works offline except for Plotly library

## Usage Examples

### Opening the Report

**From File Explorer:**
- Double-click the `.html` file
- Opens in default browser

**From Command Line:**
```bash
# Linux
xdg-open report.html

# macOS
open report.html

# Windows
start report.html
```

**From Telegram Bot:**
- Receive as document attachment
- Tap to download
- Open in browser app

### Sharing the Report

**Email:**
- Attach the single HTML file
- Recipient opens in browser
- All functionality preserved

**Cloud Storage:**
- Upload to Google Drive, Dropbox, etc.
- Share link
- Recipients view in browser

**Web Hosting:**
- Upload to any web server
- Access via URL
- No server-side code needed

## Best Practices

### For Analysis
1. Start with **Overview** tab for quick assessment
2. Check **Trading Style** badge for HFT detection
3. Explore **Charts** tab with zoom/pan for trends
4. Review **Top Trades** to understand big wins/losses
5. Use **Search** in All Positions for specific markets

### For Sharing
1. Verify file size (<5MB for email)
2. Test in different browsers
3. Include wallet address in filename
4. Add timestamp for version tracking
5. Consider compressing for email (zip)

### For Mobile
1. Use landscape orientation for charts
2. Pinch-to-zoom on scatter plots
3. Swipe through pagination quickly
4. Use search to filter large datasets
5. Bookmark in mobile browser for quick access

## Troubleshooting

**Charts not loading:**
- Check internet connection (Plotly CDN)
- Disable ad blockers
- Enable JavaScript
- Clear browser cache

**Search not working:**
- Ensure JavaScript enabled
- Check for browser console errors
- Refresh page (F5)

**Slow performance:**
- Reduce number of positions (filter data)
- Close other browser tabs
- Use desktop for >5,000 positions

**Mobile display issues:**
- Rotate device to landscape
- Zoom out with pinch gesture
- Update mobile browser
- Try different browser

## Future Enhancements

Planned features:
- [ ] Dark mode toggle
- [ ] Export individual charts as PNG
- [ ] Custom date range filtering
- [ ] Compare multiple wallets
- [ ] Offline mode (embedded Plotly)
- [ ] PDF export from HTML
- [ ] Additional chart types
- [ ] Real-time data refresh

---

For more information, see [README_HTML_REPORTS.md](../README_HTML_REPORTS.md)
