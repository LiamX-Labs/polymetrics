"""
Wallet Analysis Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from app.database import get_session
from app.models import Wallet, Position
from app.services import PolymarketFetcher, WalletAnalyzer
from app.services.cache import cached, get_cache, get_analysis_progress
import logging
import json
import threading

logger = logging.getLogger(__name__)

bp = Blueprint('wallet', __name__, url_prefix='/wallet')

fetcher = PolymarketFetcher()
analyzer = WalletAnalyzer()
progress_tracker = get_analysis_progress()


def _run_analysis_background(wallet_address: str):
    """Run wallet analysis in background thread"""
    try:
        # Progress callback
        def update_progress(current, total, message):
            if total:
                progress_pct = int((current / total) * 70)  # 70% for fetching
            else:
                progress_pct = 5
            progress_tracker.update(
                wallet_address,
                progress=progress_pct,
                fetched_positions=current,
                total_positions=total or current,
                message=message
            )

        # Fetch data with progress
        progress_tracker.start(wallet_address)
        positions_data = fetcher.get_all_closed_positions(wallet_address, progress_callback=update_progress)

        if not positions_data:
            progress_tracker.error(wallet_address, 'No positions found for this wallet')
            return

        # Analyze data
        progress_tracker.update(wallet_address, status='analyzing', progress=75, message='Analyzing positions...')
        analysis = analyzer.analyze_positions(positions_data)

        # Store in database
        progress_tracker.update(wallet_address, status='saving', progress=90, message='Saving to database...')
        db = get_session()

        wallet = db.query(Wallet).filter_by(address=wallet_address).first()

        if wallet:
            # Update existing wallet
            wallet.last_analyzed = datetime.utcnow()
            wallet.total_positions = analysis['total_positions']
            wallet.total_pnl = analysis['total_pnl']
            wallet.win_rate = analysis['win_rate']
            wallet.profit_factor = analysis['profit_factor']
            wallet.risk_reward_ratio = analysis['risk_reward_ratio']
            wallet.trading_style = analysis['trading_style']
            wallet.total_wins = analysis['total_wins']
            wallet.total_losses = analysis['total_losses']
            wallet.avg_win = analysis['avg_win']
            wallet.avg_loss = analysis['avg_loss']
            wallet.best_trade = analysis['best_trade']
            wallet.worst_trade = analysis['worst_trade']
            wallet.avg_position_size = analysis['avg_position_size']
            wallet.total_volume = analysis['total_volume']

            # Delete old positions
            db.query(Position).filter_by(wallet_id=wallet.id).delete()
        else:
            # Create new wallet
            wallet = Wallet(
                address=wallet_address,
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
            db.add(wallet)

        # Commit to get wallet ID
        db.commit()
        db.refresh(wallet)

        # Add positions
        for pos_data in analysis['positions']:
            position = Position(
                wallet_id=wallet.id,
                **pos_data
            )
            db.add(position)

        db.commit()
        logger.info(f"Completed analysis for wallet {wallet_address[:10]}...")

        # Mark complete
        progress_tracker.complete(wallet_address)

    except Exception as e:
        logger.error(f"Error in background analysis for {wallet_address}: {e}", exc_info=True)
        progress_tracker.error(wallet_address, str(e))


@bp.route('/analyze')
def analyze_wallet():
    """
    Analyze a wallet address
    Query params: address=0x...
    """
    wallet_address = request.args.get('address', '').strip().lower()

    if not wallet_address:
        return redirect(url_for('home.index'))

    # Basic validation
    if not wallet_address.startswith('0x') or len(wallet_address) < 10:
        return render_template('error.html',
                             error='Invalid wallet address',
                             message='Please provide a valid Ethereum address starting with 0x')

    try:
        # Check if analysis is already in progress
        db = get_session()
        current_progress = progress_tracker.get(wallet_address)
        if current_progress and current_progress['status'] in ['fetching', 'analyzing', 'saving']:
            logger.info(f"Analysis already in progress for {wallet_address[:10]}...")
            return render_template('analyzing.html', wallet_address=wallet_address)

        # Start background analysis
        logger.info(f"Starting background analysis for wallet {wallet_address[:10]}...")
        thread = threading.Thread(target=_run_analysis_background, args=(wallet_address,))
        thread.daemon = True
        thread.start()

        # Show loading page
        return render_template('analyzing.html', wallet_address=wallet_address)

    except Exception as e:
        logger.error(f"Error analyzing wallet {wallet_address}: {e}", exc_info=True)
        return render_template('error.html',
                             error='Analysis Error',
                             message=f'An error occurred while analyzing the wallet: {str(e)}')


@bp.route('/progress/<address>')
def analysis_progress(address):
    """Get analysis progress for a wallet"""
    address = address.strip().lower()
    progress = progress_tracker.get(address)

    if not progress:
        # Check if wallet is already in database
        db = get_session()
        wallet = db.query(Wallet).filter_by(address=address).first()
        if wallet:
            return jsonify({
                'status': 'complete',
                'progress': 100,
                'message': 'Analysis complete',
                'redirect': url_for('wallet.view_wallet', address=address)
            })
        else:
            return jsonify({
                'status': 'not_found',
                'progress': 0,
                'message': 'Wallet not found'
            })

    response_data = {
        'status': progress['status'],
        'progress': progress['progress'],
        'message': progress['message'],
        'fetched_positions': progress.get('fetched_positions', 0),
        'total_positions': progress.get('total_positions', 0),
    }

    if progress['status'] == 'complete':
        response_data['redirect'] = url_for('wallet.view_wallet', address=address)
    elif progress['status'] == 'error':
        response_data['error'] = progress.get('error', 'Unknown error occurred')

    return jsonify(response_data)


# Old synchronous code removed - now uses background threading with progress tracking


@bp.route('/<address>')
def view_wallet(address):
    """View wallet analysis details"""
    address = address.strip().lower()
    db = get_session()

    wallet = db.query(Wallet).filter_by(address=address).first()

    if not wallet:
        return redirect(url_for('wallet.analyze_wallet', address=address))

    # Get time range filter from query params
    time_range = request.args.get('range', 'all')

    # Calculate cutoff timestamp based on range
    from datetime import datetime, timedelta
    cutoff_timestamp = None

    if time_range == '1d':
        cutoff_timestamp = datetime.utcnow() - timedelta(days=1)
    elif time_range == '7d':
        cutoff_timestamp = datetime.utcnow() - timedelta(days=7)
    elif time_range == '30d':
        cutoff_timestamp = datetime.utcnow() - timedelta(days=30)
    elif time_range == '90d':
        cutoff_timestamp = datetime.utcnow() - timedelta(days=90)
    elif time_range == 'ytd':
        # Year to date
        current_year = datetime.utcnow().year
        cutoff_timestamp = datetime(current_year, 1, 1)

    # Get positions with time filter
    query = db.query(Position).filter_by(wallet_id=wallet.id)
    if cutoff_timestamp:
        query = query.filter(Position.close_timestamp >= cutoff_timestamp)
    positions = query.order_by(Position.close_timestamp.desc()).all()

    # Recalculate metrics for filtered time range
    filtered_metrics = None
    if time_range != 'all' and positions:
        # Recalculate metrics using analyzer
        # IMPORTANT: p.position_size is already stored as dollars (totalBought × avgPrice)
        # To get shares back: shares = position_size / avgPrice
        positions_data = [
            {
                'timestamp': int(p.close_timestamp.timestamp()) if p.close_timestamp else 0,
                'realizedPnl': p.realized_pnl,
                'avgPrice': p.avg_entry_price,
                'totalBought': p.position_size / p.avg_entry_price if p.avg_entry_price > 0 else 0,  # Convert back to shares
                'outcome': p.outcome,
                'exitPrice': p.exit_price or 0,
            }
            for p in positions
        ]
        if positions_data:
            filtered_analysis = analyzer.analyze_positions(positions_data)
            filtered_metrics = {
                'total_pnl': filtered_analysis['total_pnl'],
                'total_positions': filtered_analysis['total_positions'],
                'win_rate': filtered_analysis['win_rate'],
                'profit_factor': filtered_analysis['profit_factor'],
                'risk_reward_ratio': filtered_analysis['risk_reward_ratio'],
                'best_trade': filtered_analysis['best_trade'],
                'worst_trade': filtered_analysis['worst_trade'],
                'avg_position_size': filtered_analysis['avg_position_size'],
                'total_volume': filtered_analysis['total_volume'],
            }

    # Prepare chart data from analyzer
    import pandas as pd
    if positions:
        # Create DataFrame with correct column names for analyzer
        df = pd.DataFrame([
            {
                'timestamp': p.close_timestamp,
                'realized_pnl': p.realized_pnl,  # Use underscore, not camelCase
                'avg_price': p.avg_entry_price,
                'position_size_dollars': p.position_size,  # Already stored as dollars
                'outcome': p.outcome,
                'transactions': p.num_trades,
                'roi': p.roi or 0,
            }
            for p in positions if p.close_timestamp
        ])

        if not df.empty:
            chart_data = analyzer._prepare_chart_data(df)
        else:
            chart_data = {}
    else:
        chart_data = {}

    # Prepare data for table
    all_positions_data = [
        {
            'timestamp': p.close_timestamp.strftime('%Y-%m-%d %H:%M') if p.close_timestamp else 'N/A',
            'market': p.market_title,
            'outcome': p.outcome,
            'entry_price': p.avg_entry_price,
            'size': p.position_size,
            'exit_price': p.exit_price or 0,
            'trades': p.num_trades,
            'pnl': p.realized_pnl,
            'roi': p.roi or 0,
        }
        for p in positions
    ]

    # Top winners and losers
    sorted_positions = sorted(positions, key=lambda p: p.realized_pnl, reverse=True)
    top_winners = sorted_positions[:10]
    top_losers = sorted_positions[-10:][::-1]

    return render_template('wallet_detail.html',
                         wallet=wallet,
                         positions=positions,
                         chart_data=json.dumps(chart_data),
                         all_positions_data=json.dumps(all_positions_data),
                         top_winners=top_winners,
                         top_losers=top_losers,
                         time_range=time_range,
                         filtered_metrics=filtered_metrics)
