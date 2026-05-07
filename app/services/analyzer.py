"""
Wallet Analysis Service
Analyzes trading performance and calculates metrics
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class WalletAnalyzer:
    """Analyzes wallet trading performance"""

    # Trading style classification thresholds
    HFT_THRESHOLD_TRADES_PER_HOUR = 10
    ACTIVE_TRADER_THRESHOLD = 100

    def __init__(self):
        pass

    def analyze_positions(self, positions_data: List[Dict]) -> Dict:
        """
        Analyze closed positions and return comprehensive metrics

        Args:
            positions_data: List of position dictionaries from API

        Returns:
            Dictionary containing all performance metrics
        """
        if not positions_data:
            return self._empty_analysis()

        # Convert to DataFrame
        df = pd.DataFrame(positions_data)

        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df['realized_pnl'] = df['realizedPnl'].astype(float)
        df['avg_price'] = df['avgPrice'].astype(float)
        df['total_bought'] = df['totalBought'].astype(float)  # This is the actual $ amount invested

        # Calculate exit price from PnL and investment
        # Formula: realizedPnl = totalBought * (exitPrice - avgPrice)
        # Therefore: exitPrice = (realizedPnl / totalBought) + avgPrice
        df['exit_price'] = (df['realized_pnl'] / df['total_bought']) + df['avg_price']
        df['exit_price'] = df['exit_price'].fillna(0)

        # Calculate basic metrics
        total_pnl = df['realized_pnl'].sum()
        num_positions = len(df)

        # Win/Loss analysis
        winning_positions = df[df['realized_pnl'] > 0]
        losing_positions = df[df['realized_pnl'] < 0]
        breakeven_positions = df[df['realized_pnl'] == 0]

        num_wins = len(winning_positions)
        num_losses = len(losing_positions)
        win_rate = (num_wins / num_positions * 100) if num_positions > 0 else 0

        # Average wins/losses
        avg_win = winning_positions['realized_pnl'].mean() if num_wins > 0 else 0
        avg_loss = losing_positions['realized_pnl'].mean() if num_losses > 0 else 0
        total_wins = winning_positions['realized_pnl'].sum() if num_wins > 0 else 0
        total_losses = abs(losing_positions['realized_pnl'].sum()) if num_losses > 0 else 0

        # Risk/Reward metrics
        risk_reward_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Best and worst trades
        best_trade = df['realized_pnl'].max()
        worst_trade = df['realized_pnl'].min()

        # Position sizing - total_bought is already the $ amount invested
        avg_position_size = df['total_bought'].mean()
        median_position_size = df['total_bought'].median()
        total_volume = df['total_bought'].sum()

        # Trading frequency analysis
        avg_trades_per_position = df['transactions'].mean() if 'transactions' in df.columns else 1

        # Calculate trading style
        trading_style = self._classify_trading_style(df)

        # Time-based analysis
        df_sorted = df.sort_values('timestamp')
        holding_times = self._calculate_holding_times(df_sorted)

        # Calculate ROI for each position: (PnL / amount invested) * 100
        # ROI = (realizedPnl / totalBought) * 100
        df['roi'] = (df['realized_pnl'] / df['total_bought'] * 100).fillna(0)

        # Prepare position list for database storage
        positions_list = []
        for _, row in df.iterrows():
            positions_list.append({
                'condition_id': row.get('conditionId', ''),
                'market_title': row.get('title', 'Unknown Market'),
                'outcome': row.get('outcome', 'Unknown'),
                'side': row.get('side', 'Unknown'),
                'avg_entry_price': float(row.get('avgPrice', 0)),
                'exit_price': float(row.get('price', 0)),
                'position_size': float(row.get('totalBought', 0)),
                'realized_pnl': float(row.get('realizedPnl', 0)),
                'roi': float(row.get('roi', 0)),
                'num_trades': int(row.get('transactions', 1)),
                'close_timestamp': row.get('timestamp'),
                'event_slug': row.get('eventSlug', ''),
                'end_date': pd.to_datetime(row.get('endDate', None), unit='s') if row.get('endDate') else None,
            })

        return {
            # Summary metrics
            'total_positions': num_positions,
            'total_pnl': float(total_pnl),
            'win_rate': float(win_rate),
            'profit_factor': float(profit_factor),
            'risk_reward_ratio': float(risk_reward_ratio),
            'trading_style': trading_style,

            # Win/Loss details
            'num_wins': num_wins,
            'num_losses': num_losses,
            'num_breakeven': len(breakeven_positions),
            'total_wins': float(total_wins),
            'total_losses': float(total_losses),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'best_trade': float(best_trade),
            'worst_trade': float(worst_trade),

            # Position sizing
            'avg_position_size': float(avg_position_size),
            'median_position_size': float(median_position_size),
            'total_volume': float(total_volume),
            'avg_trades_per_position': float(avg_trades_per_position),

            # Timing
            'avg_holding_time_hours': holding_times,

            # Position data for database
            'positions': positions_list,

            # Chart data
            'chart_data': self._prepare_chart_data(df),
        }

    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'total_positions': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'risk_reward_ratio': 0.0,
            'trading_style': 'unknown',
            'num_wins': 0,
            'num_losses': 0,
            'num_breakeven': 0,
            'total_wins': 0.0,
            'total_losses': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'avg_position_size': 0.0,
            'median_position_size': 0.0,
            'total_volume': 0.0,
            'avg_trades_per_position': 0.0,
            'avg_holding_time_hours': 0.0,
            'positions': [],
            'chart_data': {},
        }

    def _classify_trading_style(self, df: pd.DataFrame) -> str:
        """
        Classify trading style based on comprehensive activity patterns

        Categories:
        - HFT (High-Frequency Trader): Very fast trading with high win rate
        - Scalper: Quick trades (< 1 day) with consistent small profits
        - Day Trader: Intraday positions (< 3 days) with moderate frequency
        - Swing Trader: Medium-term positions (3-14 days) with good risk/reward
        - Position Trader: Long-term positions (> 14 days) with low frequency
        """
        num_positions = len(df)

        if num_positions == 0:
            return 'unknown'

        # Calculate time span and frequency
        time_span_hours = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600

        if time_span_hours <= 0:
            return 'unknown'

        positions_per_hour = num_positions / time_span_hours

        # Calculate average position duration (if we have position-level timestamps)
        # For now, use time between positions as a proxy
        df_sorted = df.sort_values('timestamp')
        time_diffs = df_sorted['timestamp'].diff()
        avg_time_between_positions = time_diffs.dt.total_seconds().mean() / 3600  # in hours

        # Calculate win rate
        win_rate = (len(df[df['realized_pnl'] > 0]) / num_positions * 100) if num_positions > 0 else 0

        # Calculate average ROI
        avg_roi = df['roi'].mean() if 'roi' in df.columns else 0

        # Calculate risk/reward from wins and losses
        winning_pnl = df[df['realized_pnl'] > 0]['realized_pnl']
        losing_pnl = df[df['realized_pnl'] < 0]['realized_pnl']

        avg_win = winning_pnl.mean() if len(winning_pnl) > 0 else 0
        avg_loss = abs(losing_pnl.mean()) if len(losing_pnl) > 0 else 0
        risk_reward = avg_win / avg_loss if avg_loss > 0 else 0

        # Classification logic with multiple factors

        # HFT: Very high frequency (>10 positions/hour OR >200 positions with <1 hour between trades)
        if positions_per_hour >= self.HFT_THRESHOLD_TRADES_PER_HOUR:
            return 'hft'
        if num_positions >= 200 and avg_time_between_positions < 1:
            return 'hft'

        # Scalper: Quick exits (<24 hours between trades), high volume, win rate >55%
        if avg_time_between_positions < 24 and num_positions >= 50 and win_rate > 55:
            return 'scalper'

        # Day Trader: Fast trading (<72 hours between trades), moderate frequency
        if avg_time_between_positions < 72 and num_positions >= 20:
            return 'day_trader'

        # Swing Trader: Medium-term (3-14 days), good risk/reward (>1.2), moderate activity
        if 72 <= avg_time_between_positions <= 336 and risk_reward > 1.2 and num_positions >= 10:
            return 'swing_trader'

        # Position Trader: Long-term holds (>14 days), lower frequency
        if avg_time_between_positions > 336:
            return 'position_trader'

        # Active Trader: High volume but doesn't fit other categories
        if num_positions >= self.ACTIVE_TRADER_THRESHOLD:
            return 'active_trader'

        # Default: Normal trader
        return 'normal'

    def _calculate_holding_times(self, df_sorted: pd.DataFrame) -> float:
        """Calculate average holding time between positions"""
        if len(df_sorted) <= 1:
            return 0.0

        time_diffs = df_sorted['timestamp'].diff()
        avg_holding_time_hours = time_diffs.dt.total_seconds().mean() / 3600

        return float(avg_holding_time_hours) if not pd.isna(avg_holding_time_hours) else 0.0

    def _prepare_chart_data(self, df: pd.DataFrame) -> Dict:
        """Prepare data for charts"""
        df_sorted = df.sort_values('timestamp')

        # Cumulative PnL
        cumulative_pnl = df_sorted['realized_pnl'].cumsum()

        # Win/Loss distribution
        win_count = len(df[df['realized_pnl'] > 0])
        loss_count = len(df[df['realized_pnl'] < 0])
        breakeven_count = len(df[df['realized_pnl'] == 0])

        # PnL by outcome
        outcome_pnl = df.groupby('outcome')['realized_pnl'].sum().to_dict()

        # Hourly PnL
        df_sorted['hour'] = df_sorted['timestamp'].dt.hour
        hourly_pnl = df_sorted.groupby('hour')['realized_pnl'].sum()
        hourly_dict = {int(h): float(pnl) for h, pnl in hourly_pnl.items()}

        # Drawdown calculation
        cumulative_max = cumulative_pnl.cummax()
        drawdown = cumulative_pnl - cumulative_max

        return {
            'cumulative_pnl': {
                'timestamps': df_sorted['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                'values': cumulative_pnl.tolist(),
            },
            'win_loss': {
                'labels': ['Wins', 'Losses', 'Breakeven'],
                'values': [win_count, loss_count, breakeven_count],
            },
            'pnl_distribution': df['realized_pnl'].tolist(),
            'outcome_pnl': {
                'outcomes': list(outcome_pnl.keys()),
                'values': list(outcome_pnl.values()),
            },
            'hourly_pnl': {
                'hours': list(range(24)),
                'values': [hourly_dict.get(h, 0) for h in range(24)],
            },
            'position_sizes': df['total_bought'].tolist(),
            'roi_distribution': df['roi'].tolist() if 'roi' in df.columns else [],
            'drawdown': drawdown.tolist(),
            'entry_vs_pnl': {
                'entry_prices': df['avg_price'].tolist(),
                'pnl': df['realized_pnl'].tolist(),
            },
            'size_vs_pnl': {
                'sizes': df['total_bought'].tolist(),
                'pnl': df['realized_pnl'].tolist(),
            },
        }

    def compare_wallets(self, analyses: List[Dict]) -> Dict:
        """Compare multiple wallet analyses"""
        if not analyses:
            return {}

        comparison = {
            'wallets': [],
            'metrics_comparison': {},
            'chart_overlays': {},
        }

        # Extract key metrics for each wallet
        for analysis in analyses:
            comparison['wallets'].append({
                'total_pnl': analysis.get('total_pnl', 0),
                'win_rate': analysis.get('win_rate', 0),
                'profit_factor': analysis.get('profit_factor', 0),
                'total_positions': analysis.get('total_positions', 0),
                'trading_style': analysis.get('trading_style', 'unknown'),
            })

        return comparison
