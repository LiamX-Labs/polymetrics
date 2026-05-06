"""
API Routes
"""
from flask import Blueprint, jsonify, request, redirect
from sqlalchemy import desc
from app.database import get_session
from app.models import Wallet, Position
from app.services import PolymarketFetcher, WalletAnalyzer
from app.services.cache import get_analysis_progress
from datetime import datetime
import logging
import threading

logger = logging.getLogger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/wallet/<address>')
def get_wallet(address):
    """Get wallet data by address"""
    db = get_session()
    wallet = db.query(Wallet).filter_by(address=address.lower()).first()

    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404

    return jsonify(wallet.to_dict())


@bp.route('/wallet/<address>/positions')
def get_wallet_positions(address):
    """Get all positions for a wallet"""
    db = get_session()
    wallet = db.query(Wallet).filter_by(address=address.lower()).first()

    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404

    positions = db.query(Position).filter_by(wallet_id=wallet.id).order_by(desc(Position.close_timestamp)).all()

    return jsonify({
        'wallet': wallet.to_dict(),
        'positions': [p.to_dict() for p in positions]
    })


@bp.route('/leaderboard')
def get_leaderboard():
    """Get leaderboard data"""
    metric = request.args.get('metric', 'total_pnl')
    limit = min(int(request.args.get('limit', 100)), 500)

    db = get_session()

    # Determine sort column
    sort_column = Wallet.total_pnl
    if metric == 'win_rate':
        sort_column = Wallet.win_rate
    elif metric == 'profit_factor':
        sort_column = Wallet.profit_factor
    elif metric == 'volume':
        sort_column = Wallet.total_volume

    # Filter for minimum positions on some metrics
    query = db.query(Wallet)
    if metric in ['win_rate', 'profit_factor']:
        query = query.filter(Wallet.total_positions >= 10)

    wallets = query.order_by(desc(sort_column)).limit(limit).all()

    return jsonify({
        'metric': metric,
        'count': len(wallets),
        'wallets': [w.to_dict() for w in wallets]
    })


@bp.route('/search')
def search_wallets():
    """Search for wallets"""
    query = request.args.get('q', '').strip().lower()

    if not query:
        return jsonify({'error': 'Query parameter required'}), 400

    db = get_session()

    # Search by address prefix
    wallets = db.query(Wallet).filter(Wallet.address.like(f'{query}%')).limit(20).all()

    return jsonify({
        'query': query,
        'count': len(wallets),
        'results': [w.to_dict() for w in wallets]
    })


@bp.route('/stats')
def get_platform_stats():
    """Get platform-wide statistics"""
    db = get_session()

    from sqlalchemy import func

    total_wallets = db.query(Wallet).count()
    total_positions = db.query(Position).count()
    total_volume = db.query(func.sum(Wallet.total_volume)).scalar() or 0
    total_pnl = db.query(func.sum(Wallet.total_pnl)).scalar() or 0

    return jsonify({
        'total_wallets': total_wallets,
        'total_positions': total_positions,
        'total_volume': float(total_volume),
        'total_pnl': float(total_pnl),
    })


@bp.route('/analyze')
def analyze_wallet():
    """Trigger immediate wallet analysis"""
    address = request.args.get('address', '').strip().lower()

    if not address:
        return jsonify({'error': 'Address parameter required'}), 400

    # Validate address format
    if not address.startswith('0x') or len(address) != 42:
        return jsonify({'error': 'Invalid Ethereum address format'}), 400

    db = get_session()

    # Check if wallet already exists
    existing_wallet = db.query(Wallet).filter_by(address=address).first()

    if existing_wallet:
        # Wallet already analyzed, redirect to wallet page
        return redirect(f'/wallet/{address}')

    # Start analysis in background thread
    progress_tracker = get_analysis_progress()
    progress_tracker.start(address)

    def analyze_in_background():
        """Background analysis task"""
        try:
            fetcher = PolymarketFetcher()
            analyzer = WalletAnalyzer()
            db_local = get_session()

            # Update progress
            progress_tracker.update(address, status='fetching', message='Fetching positions...')

            # Fetch positions
            positions_data = fetcher.get_all_closed_positions(address)

            if not positions_data or len(positions_data) < 5:
                progress_tracker.error(address, 'Insufficient trading data (minimum 5 positions required)')
                return

            progress_tracker.update(
                address,
                status='analyzing',
                message=f'Analyzing {len(positions_data)} positions...',
                total_positions=len(positions_data)
            )

            # Analyze
            analysis = analyzer.analyze_positions(positions_data)

            # Create wallet
            wallet = Wallet(
                address=address,
                first_analyzed=datetime.utcnow(),
                last_analyzed=datetime.utcnow(),
                total_positions=analysis['total_positions'],
                total_pnl=analysis['total_pnl'],
                win_rate=analysis['win_rate'],
                profit_factor=analysis['profit_factor'],
                risk_reward_ratio=analysis['risk_reward_ratio'],
                trading_style=analysis['trading_style'],
                total_wins=analysis['total_wins'],
                total_losses=analysis['total_losses'],
                avg_win=analysis['avg_win'],
                avg_loss=analysis['avg_loss'],
                best_trade=analysis['best_trade'],
                worst_trade=analysis['worst_trade'],
                avg_position_size=analysis['avg_position_size'],
                total_volume=analysis['total_volume']
            )
            db_local.add(wallet)
            db_local.commit()
            db_local.refresh(wallet)

            # Add positions
            for pos_data in analysis['positions']:
                position = Position(wallet_id=wallet.id, **pos_data)
                db_local.add(position)

            db_local.commit()

            progress_tracker.complete(address)
            logger.info(f"✓ Analysis complete for {address[:10]}...")

        except Exception as e:
            logger.error(f"Error analyzing wallet {address[:10]}: {e}")
            progress_tracker.error(address, str(e))
            if 'db_local' in locals():
                db_local.rollback()

    # Start background thread
    thread = threading.Thread(target=analyze_in_background, daemon=True)
    thread.start()

    # Redirect to wallet page with loading state
    return redirect(f'/wallet/{address}')


@bp.route('/analysis-progress/<address>')
def get_analysis_progress_endpoint(address):
    """Get progress of ongoing wallet analysis"""
    progress_tracker = get_analysis_progress()
    progress = progress_tracker.get(address.lower())

    if not progress:
        # Check if wallet exists in database
        db = get_session()
        wallet = db.query(Wallet).filter_by(address=address.lower()).first()

        if wallet:
            return jsonify({
                'status': 'complete',
                'exists': True
            })
        else:
            return jsonify({
                'status': 'not_found',
                'exists': False
            })

    return jsonify(progress)
