# Interactive HTML Reports

Generate beautiful, interactive HTML reports from Polymarket wallet analysis with full mobile support.

## Features

### 📊 Interactive Visualizations
- **Plotly.js charts** with zoom, pan, and hover capabilities
- All charts from the PDF report, but fully interactive
- Responsive design that works on desktop, tablet, and mobile

### 📱 Mobile-Friendly
- Fully responsive layout adapts to any screen size
- Touch-friendly navigation and controls
- Optimized for viewing on phones and tablets

### 🔍 Advanced Features
- **Searchable positions table** - Find specific markets instantly
- **Pagination** - Browse through thousands of positions easily
- **Tab navigation** - Organized into Overview, Charts, Top Trades, and All Positions
- **Print-friendly** - Clean printing layout for paper reports

### 📈 Complete Analysis
All the same comprehensive metrics as the PDF report:
- Trading style classification (HFT Bot, Active Trader, Normal Trader)
- Win rate, profit factor, risk/reward ratios
- Cumulative PnL tracking
- Drawdown analysis
- Position size distribution
- Top winning and losing trades
- Hourly trading patterns
- And much more!

## Usage

### Standalone Script

Generate an HTML report for any wallet:

```bash
cd scripts
python3 generate_html_report.py
```

When prompted, enter the wallet address (or press Enter to use the latest data).

The script will:
1. Load existing CSV data from the `data/` directory
2. Calculate all performance metrics
3. Generate interactive charts
4. Create an HTML file in the `reports/` directory

### Via Telegram Bot

When you analyze a wallet through the Telegram bot, it automatically:
1. Sends summary metrics and charts as images
2. **Generates and sends the interactive HTML report** as a file
3. You can download and open it in any web browser

### Integration with Python Code

```python
from bot.analysis import run_wallet_analysis, generate_html_report

# Run analysis
results = run_wallet_analysis(wallet_address, days_back=30)

# Generate HTML report
html_path = generate_html_report(results)
print(f"Report saved to: {html_path}")
```

## Report Structure

The HTML report is organized into 4 main tabs:

### 1. Overview
- **Key Metrics Grid** - All important performance metrics at a glance
- **Mini Charts** - Quick view of cumulative PnL and win/loss distribution
- Perfect for quick performance check

### 2. Charts
- Cumulative PnL Over Time
- Win/Loss Distribution (pie chart)
- PnL Distribution (histogram)
- PnL by Outcome (bar chart)
- PnL by Hour of Day
- Position Size Distribution
- ROI Distribution
- Drawdown Over Time
- Entry Price vs PnL (scatter)
- Position Size vs PnL (scatter)

All charts are **interactive** - hover for details, zoom in/out, pan around!

### 3. Top Trades
- **Top 10 Winning Trades** - Your best performers
- **Top 10 Losing Trades** - Understand your losses
- Full details for each trade (market, outcome, PnL, entry price, size)

### 4. All Positions
- **Complete position history** with search and pagination
- **Search box** - Filter by market name, outcome, or any field
- **50 positions per page** with easy navigation
- Sortable columns
- Color-coded PnL (green for wins, red for losses)

## Technical Details

### File Size
- Typical report size: 300KB - 1MB (depends on number of positions)
- Self-contained single HTML file (no external dependencies except Plotly.js CDN)
- Fast loading even on mobile connections

### Browser Compatibility
- Works on all modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers fully supported (iOS Safari, Chrome Mobile)
- No installation or plugins required

### Data Privacy
- All data is embedded in the HTML file
- No data sent to external servers (except Plotly.js library load)
- Safe to share or archive

## Examples

### Command Line Usage

```bash
# Generate report for specific wallet
cd scripts
python3 generate_html_report.py
# Enter: 0xc1200f03f07df479a041bb925a076d0b51c3b9f1

# Output:
# ✓ Interactive HTML report saved to:
#   ../reports/polymarket_performance_report_0xc1200f03_20260505_171043.html
#
# 📊 Report includes:
#   - Overview Dashboard with key metrics
#   - 10 interactive charts (Plotly.js)
#   - Top 10 winning and losing trades
#   - All 1750 positions with search & pagination
#   - Mobile-friendly responsive design
```

### Viewing the Report

Simply open the generated `.html` file in your browser:

```bash
# On Linux
xdg-open reports/polymarket_performance_report_*.html

# On macOS
open reports/polymarket_performance_report_*.html

# On Windows
start reports/polymarket_performance_report_*.html
```

## Comparison: HTML vs PDF Reports

| Feature | HTML Report | PDF Report |
|---------|-------------|------------|
| Interactive Charts | ✅ Zoom, pan, hover | ❌ Static images |
| Search Positions | ✅ Live search | ❌ Ctrl+F only |
| Mobile Friendly | ✅ Fully responsive | ⚠️ Requires zoom |
| File Size | ~500KB | ~2-5MB |
| Pagination | ✅ Fast navigation | ❌ All on pages |
| Sharing | ✅ Single file | ✅ Single file |
| Printing | ✅ Optimized | ✅ Native |
| Offline Viewing | ⚠️ Needs Plotly CDN | ✅ Fully offline |

**Recommendation**: Use HTML for analysis and exploration, use PDF for archival and printing.

## Customization

The HTML template is located at `templates/report_template.html`. You can customize:
- Colors and styling (CSS in `<style>` section)
- Chart configurations (Plotly.js settings in `<script>` section)
- Layout and structure (HTML markup)

## Troubleshooting

### Report doesn't load charts
- Check internet connection (Plotly.js loads from CDN)
- Ensure JavaScript is enabled in your browser

### Search not working
- JavaScript must be enabled
- Clear browser cache and reload

### Mobile view looks wrong
- Ensure viewport meta tag is present (should be in template)
- Try rotating device or refreshing page

### File won't open
- Make sure file extension is `.html`
- Try opening in a different browser
- Check if file was fully downloaded (should be ~500KB+)

## Future Enhancements

Potential improvements:
- [ ] Offline mode (embed Plotly.js library)
- [ ] Dark mode toggle
- [ ] Export charts as images
- [ ] Custom date range filtering in the UI
- [ ] Additional chart types (candlestick, etc.)
- [ ] Compare multiple wallets side-by-side

## Support

For issues or questions:
1. Check this README
2. Review the generated HTML source for errors
3. Check browser console for JavaScript errors
4. Verify input data CSV is properly formatted

---

**Note**: The HTML report requires an active internet connection to load the Plotly.js library from CDN. For fully offline reports, use the PDF generator instead.
