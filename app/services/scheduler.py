"""
Background Task Scheduler
Handles periodic tasks like discovering traders and refreshing wallet data
"""
import threading
import time
import logging
from datetime import datetime, timedelta
from app.services import PolymarketFetcher, WalletAnalyzer, LeaderboardFetcher
from app.database import get_session
from app.models import Wallet, Position

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """Manages background tasks"""

    def __init__(self):
        self.wallet_fetcher = PolymarketFetcher()
        self.analyzer = WalletAnalyzer()
        self.leaderboard_fetcher = LeaderboardFetcher()
        self.running = False
        self.thread = None

    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Background scheduler started")

    def stop(self):
        """Stop the background scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Background scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        # Run immediately on startup
        self.refresh_leaderboard()

        last_leaderboard_refresh = time.time()

        while self.running:
            try:
                current_time = time.time()

                # Refresh leaderboard every hour
                if current_time - last_leaderboard_refresh >= 3600:
                    self.refresh_leaderboard()
                    last_leaderboard_refresh = current_time

                # Sleep for 60 seconds before next check
                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                time.sleep(60)

    def refresh_leaderboard(self):
        """
        Discover new traders from Polymarket and refresh existing stale wallets
        """
        try:
            logger.info("=== Starting Leaderboard Refresh ===")
            start_time = time.time()

            db = get_session()

            # Step 1: Discover active traders from Polymarket leaderboard API
            logger.info("Discovering active traders from Polymarket leaderboard...")
            discovered_traders = self.leaderboard_fetcher.get_all_unique_traders(
                time_period='DAY',
                categories=['OVERALL', 'POLITICS', 'SPORTS', 'CRYPTO']
            )

            # Get existing wallet addresses
            existing_addresses = set(
                w.address.lower() for w in db.query(Wallet.address).all()
            )

            # Filter to new traders not in database
            new_traders = [
                t for t in discovered_traders
                if t['address'].lower() not in existing_addresses
            ]

            logger.info(f"Discovered {len(discovered_traders)} traders, {len(new_traders)} are new")

            # Step 2: Auto-analyze top new traders (limit to prevent overload)
            max_new = 10
            analyzed_new = 0

            for trader in new_traders[:max_new]:
                address = trader['address'].lower()
                try:
                    logger.info(f"Analyzing new trader {address[:10]}...")

                    # Fetch positions
                    positions_data = self.wallet_fetcher.get_all_closed_positions(address)

                    if not positions_data or len(positions_data) < 5:
                        logger.info(f"Skipping {address[:10]} - insufficient data")
                        continue

                    # Analyze
                    analysis = self.analyzer.analyze_positions(positions_data)

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
                    db.add(wallet)
                    db.commit()
                    db.refresh(wallet)

                    # Add positions
                    for pos_data in analysis['positions']:
                        position = Position(wallet_id=wallet.id, **pos_data)
                        db.add(position)

                    db.commit()
                    analyzed_new += 1
                    logger.info(f"✓ Analyzed new trader {address[:10]} - {analysis['total_positions']} positions")

                except Exception as e:
                    logger.error(f"Error analyzing new trader {address[:10]}: {e}")
                    db.rollback()
                    continue

            # Step 3: Refresh stale existing wallets
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            stale_wallets = db.query(Wallet).filter(
                Wallet.last_analyzed < cutoff_time
            ).order_by(
                Wallet.total_pnl.desc()
            ).limit(10).all()

            logger.info(f"Found {len(stale_wallets)} stale wallets to refresh")

            # Re-analyze stale wallets to keep data fresh
            refreshed_count = 0
            for wallet in stale_wallets:
                address = wallet.address
                try:
                    logger.info(f"Refreshing wallet {address[:10]}...")

                    # Fetch latest positions
                    positions_data = self.wallet_fetcher.get_all_closed_positions(address)

                    if not positions_data or len(positions_data) < 5:
                        logger.info(f"Skipping {address[:10]} - insufficient data")
                        continue

                    # Re-analyze with fresh data
                    analysis = self.analyzer.analyze_positions(positions_data)

                    # Update wallet metrics
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
                    db.commit()

                    # Add fresh positions
                    for pos_data in analysis['positions']:
                        position = Position(wallet_id=wallet.id, **pos_data)
                        db.add(position)

                    db.commit()
                    refreshed_count += 1
                    logger.info(f"✓ Refreshed {address[:10]} - {analysis['total_positions']} positions")

                except Exception as e:
                    logger.error(f"Error refreshing wallet {address[:10]}: {e}")
                    db.rollback()
                    continue

            elapsed = time.time() - start_time
            logger.info(f"=== Leaderboard Refresh Complete ===")
            logger.info(f"Traders discovered from Polymarket: {len(discovered_traders)}")
            logger.info(f"New traders analyzed: {analyzed_new}")
            logger.info(f"Existing wallets refreshed: {refreshed_count}")
            logger.info(f"Time elapsed: {elapsed:.1f}s")

        except Exception as e:
            logger.error(f"Error in refresh_leaderboard: {e}", exc_info=True)


# Global scheduler instance
_scheduler = None


def get_scheduler() -> BackgroundScheduler:
    """Get or create global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler


def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler"""
    scheduler = get_scheduler()
    scheduler.stop()
