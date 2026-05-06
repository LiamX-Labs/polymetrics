"""
Home/Dashboard Routes
"""
from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import desc, func
from app.database import get_session
from app.models import Wallet, Position
from app.services import LeaderboardFetcher
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    """Homepage with dashboard and leaderboards"""
    db = get_session()

    # Get platform statistics
    total_wallets = db.query(Wallet).count()
    total_positions = db.query(Position).count()
    total_volume = db.query(func.sum(Wallet.total_volume)).scalar() or 0

    # Fetch top 5 daily traders from Polymarket API for homepage preview
    leaderboard_fetcher = LeaderboardFetcher()
    live_traders = leaderboard_fetcher.get_leaderboard(
        category='OVERALL',
        time_period='DAY',
        limit=5
    ) or []

    # Merge live API data with our database analytics
    top_daily_traders = []
    for trader in live_traders:
        address = trader.get('proxyWallet', '').lower()

        # Check if we have analytics for this wallet
        wallet = db.query(Wallet).filter(Wallet.address == address).first()

        top_daily_traders.append({
            'rank': trader.get('rank'),
            'address': address,
            'userName': trader.get('userName', 'Anonymous'),
            'profileImage': trader.get('profileImage'),
            'xUsername': trader.get('xUsername'),
            'verifiedBadge': trader.get('verifiedBadge', False),
            # API data
            'pnl': trader.get('pnl', 0),
            'vol': trader.get('vol', 0),
            # Our calculated metrics (if available)
            'profit_factor': wallet.profit_factor if wallet else None,
            'win_rate': wallet.win_rate if wallet else None,
            'trading_style': wallet.trading_style if wallet else 'Unknown',
            'total_positions': wallet.total_positions if wallet else 0,
            'in_database': wallet is not None
        })

    # Fetch top 5 markets by volume
    top_markets = leaderboard_fetcher.get_top_markets(limit=5)

    # Get top traders by various metrics from our database
    top_by_pnl = db.query(Wallet).order_by(desc(Wallet.total_pnl)).limit(10).all()
    top_by_win_rate = db.query(Wallet).filter(Wallet.total_positions >= 10).order_by(desc(Wallet.win_rate)).limit(10).all()
    top_by_profit_factor = db.query(Wallet).filter(Wallet.total_positions >= 10).order_by(desc(Wallet.profit_factor)).limit(10).all()

    # Get recently analyzed wallets
    recent_wallets = db.query(Wallet).order_by(desc(Wallet.last_analyzed)).limit(10).all()

    return render_template('index.html',
                         total_wallets=total_wallets,
                         total_positions=total_positions,
                         total_volume=total_volume,
                         top_daily_traders=top_daily_traders,
                         top_markets=top_markets,
                         top_by_pnl=top_by_pnl,
                         top_by_win_rate=top_by_win_rate,
                         top_by_profit_factor=top_by_profit_factor,
                         recent_wallets=recent_wallets)


@bp.route('/leaderboard')
def leaderboard():
    """Full leaderboard page with live Polymarket data"""
    db = get_session()

    # Get filter parameters from query string
    category = request.args.get('category', 'OVERALL').upper()
    time_period = request.args.get('period', 'DAY').upper()

    # Fetch live leaderboard from Polymarket API
    leaderboard_fetcher = LeaderboardFetcher()
    live_traders = leaderboard_fetcher.get_leaderboard(
        category=category,
        time_period=time_period,
        limit=50
    ) or []

    # Merge live API data with our database analytics
    enriched_traders = []
    for trader in live_traders:
        address = trader.get('proxyWallet', '').lower()

        # Check if we have analytics for this wallet
        wallet = db.query(Wallet).filter(Wallet.address == address).first()

        enriched_traders.append({
            'rank': trader.get('rank'),
            'address': address,
            'userName': trader.get('userName', 'Anonymous'),
            'profileImage': trader.get('profileImage'),
            'xUsername': trader.get('xUsername'),
            'verifiedBadge': trader.get('verifiedBadge', False),
            # API data
            'pnl': trader.get('pnl', 0),
            'vol': trader.get('vol', 0),
            # Our calculated metrics (if available)
            'profit_factor': wallet.profit_factor if wallet else None,
            'win_rate': wallet.win_rate if wallet else None,
            'trading_style': wallet.trading_style if wallet else 'Unknown',
            'total_positions': wallet.total_positions if wallet else 0,
            'in_database': wallet is not None
        })

    # Get all analyzed wallets from our database
    analyzed_wallets = db.query(Wallet).order_by(desc(Wallet.total_pnl)).limit(100).all()

    return render_template('leaderboard.html',
                         live_traders=enriched_traders,
                         analyzed_wallets=analyzed_wallets,
                         selected_category=category,
                         selected_period=time_period,
                         categories=LeaderboardFetcher.CATEGORIES,
                         time_periods=LeaderboardFetcher.TIME_PERIODS)


@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
