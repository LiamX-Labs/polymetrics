# Changelog

## Version 2.0 - May 2, 2026

### ✨ Major Features Added

#### 1. Transaction Count Per Position
- Added "Trades" column to all CSV exports
- Shows number of transactions per closed position
- Included in PDF reports (top winners/losers and full position list)

#### 2. Interactive Mode for All Scripts
- All scripts now prompt for wallet address if not provided
- User-friendly interface for non-technical users
- Maintains backward compatibility with command-line mode

#### 3. Default API Key Included
- Etherscan API key (`ZA1X87TCSVVD53WECWZZ8UWJ7Y1VPKJ94A`) included by default
- No setup required - works out of the box
- Optional: Users can still provide their own key with `--api-key` flag

#### 4. Smart File Detection
- `generate_performance_report.py` auto-finds CSV files in `data/` directory
- Uses most recent files automatically
- Clear error messages if data files are missing

#### 5. Organized Project Structure
```
Polymarkets/
├── scripts/     # All Python scripts
├── data/        # CSV data files
├── reports/     # PDF reports
├── docs/        # Documentation
└── *.md         # Main docs in root
```

---

### 🔧 Technical Improvements

#### Fixed Issues
- **Timestamp Format**: Fixed Polymarket API timestamps (removed incorrect `/1000` division)
- **NumPy Compatibility**: Pinned numpy to `<2.0.0` to avoid compatibility issues
- **File Paths**: Updated all scripts to work with new directory structure

#### Code Quality
- Added input validation and error handling
- Improved error messages
- Better file path handling (relative paths)
- Consistent coding style

---

### 📚 Documentation Updates

#### New Files
- **README.md** - Complete rewrite with full feature documentation
- **QUICKSTART.md** - Fast-start guide for new users
- **PROJECT_STRUCTURE.txt** - Directory overview and file descriptions
- **CHANGELOG.md** - This file

#### Updated Files
- **requirements.txt** - Added numpy version constraint
- **docs/ANALYSIS_SUMMARY.md** - Updated with latest findings
- **docs/PERFORMANCE_ANALYSIS_README.md** - Added transaction count info

---

### 🎯 User Experience Improvements

#### Before (v1.0)
```bash
# Required manual setup
python wallet_analyzer.py 0xWALLET --api-key YOUR_KEY

# No transaction counts
# Files scattered everywhere
# Complex setup process
```

#### After (v2.0)
```bash
# Interactive mode - just run it!
python wallet_analyzer.py
# → Prompts for wallet
# → Uses default API key
# → Auto-saves to data/
# → Shows transaction counts
```

---

### 📊 Data Features

#### CSV Exports Enhanced
- Transaction count column added
- Corrected timestamps (proper Unix epoch handling)
- Organized in `data/` directory
- Consistent naming: `*_0xWALLET.csv`

#### PDF Reports Enhanced
- Transaction count in all tables
- 11 pages with comprehensive analysis
- Auto-detects latest data files
- Saves to `reports/` directory

---

### 🚀 Performance

- Faster data loading with smart file detection
- Reduced API calls with better caching
- Optimized CSV parsing
- Cleaner output formatting

---

### 🐛 Bug Fixes

1. Fixed timestamp conversion (API returns seconds, not milliseconds)
2. Fixed NumPy 2.x compatibility issues
3. Fixed file path issues when running from different directories
4. Fixed CSV column alignment issues
5. Fixed interactive prompt edge cases

---

### 📦 Dependencies

```
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0,<2.0.0    # ← Version constraint added
matplotlib>=3.7.0
seaborn>=0.12.0
jupyter>=1.0.0
```

---

### 🔄 Migration from v1.0

**No breaking changes!** All v1.0 command-line usage still works:

```bash
# v1.0 commands still work
python wallet_analyzer.py 0xWALLET --api-key KEY

# v2.0 adds interactive mode (backward compatible)
python wallet_analyzer.py  # ← New: prompts for input
```

**New features are additive:**
- Transaction counts automatically appear in CSV/PDF
- Files auto-organize into directories
- Interactive mode is optional

---

### 👨‍💻 Developer Changes

#### File Organization
- All scripts moved to `scripts/`
- All data moved to `data/`
- All reports moved to `reports/`
- All docs moved to `docs/`

#### API Changes
- `export_closed_positions_csv()` now accepts optional `trades` parameter
- All main functions now support interactive prompts
- Default API key constant added to all scripts

---

### 🎉 Summary

**Version 2.0 makes the toolkit:**
- ✅ Easier to use (interactive mode)
- ✅ Better organized (clean directory structure)
- ✅ More informative (transaction counts)
- ✅ Production-ready (default API key)
- ✅ Well-documented (comprehensive guides)
- ✅ Bug-free (fixed all known issues)

---

## Version 1.0 - May 1, 2026

### Initial Release

- Polymarket API data fetcher
- Wallet balance analyzer
- On-chain position reconstructor
- PDF report generator
- Jupyter notebook for analysis
- CSV exports
- Basic documentation

---

**Latest Version:** 2.0
**Last Updated:** May 2, 2026
