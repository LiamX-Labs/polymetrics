╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          📊 POLYMETRICS - QUICK START GUIDE 📊               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

🚀 START THE PLATFORM (Pick one method):

Method 1 - Automated Script:
   ./RUN_PLATFORM.sh

Method 2 - Manual Commands:
   source venv/bin/activate
   pip install Flask Flask-SQLAlchemy Flask-CORS
   python run.py

Method 3 - One-liner:
   source venv/bin/activate && python run.py

═══════════════════════════════════════════════════════════════

📖 THEN:
   Open browser → http://localhost:5000

═══════════════════════════════════════════════════════════════

🎯 FIRST STEPS:

1. Enter a wallet address in the search bar
   Example: 0x04b6d7e930cf9e493c5e6ef24b496294f95594c8

2. Click "Analyze" 
   (Wait 5-10 seconds for data to fetch)

3. View the comprehensive analytics!

═══════════════════════════════════════════════════════════════

📚 DOCUMENTATION:

   START_HERE.md ............. Overview & getting started
   QUICKSTART_PLATFORM.md .... 60-second walkthrough
   PLATFORM_README.md ........ Complete documentation
   PLATFORM_SUMMARY.md ....... Technical details

═══════════════════════════════════════════════════════════════

🌟 FEATURES:

   ✓ Dashboard with leaderboards
   ✓ Individual wallet analysis (10+ charts)
   ✓ Compare up to 4 wallets
   ✓ REST API endpoints
   ✓ Mobile responsive
   ✓ 1-hour caching

═══════════════════════════════════════════════════════════════

🎨 DESIGN:

   Beautiful purple/orange gradient theme
   Glassmorphism effects
   Smooth animations
   Consistent with your existing HTML reports

═══════════════════════════════════════════════════════════════

🔧 TECH:

   Backend:  Flask + SQLAlchemy
   Database: SQLite (auto-created)
   Charts:   Plotly.js (interactive)
   Theme:    Custom CSS

═══════════════════════════════════════════════════════════════

💡 TIPS:

   - Analyze 10-20 wallets to build a leaderboard
   - Use comparison tool to study different strategies
   - API endpoints available at /api/*
   - Your original CLI scripts still work!

═══════════════════════════════════════════════════════════════

🆘 TROUBLESHOOTING:

   Port in use?
      → Edit config/settings.py, change PORT = 8000

   Module not found?
      → pip install Flask Flask-SQLAlchemy Flask-CORS

   Database error?
      → rm database/polymetrics.db
      → python run.py (recreates database)

═══════════════════════════════════════════════════════════════

Ready? Run:  ./RUN_PLATFORM.sh

═══════════════════════════════════════════════════════════════
