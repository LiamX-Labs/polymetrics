#!/usr/bin/env python3
"""
Generate Interactive HTML Performance Report from Polymarket Trading Data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import sys
import os
import glob
import json
warnings.filterwarnings('ignore')

# Prompt for wallet address to match data files
wallet_input = input("\nEnter wallet address to generate HTML report for (or press Enter for latest): ").strip()

# Find CSV files in data directory
data_dir = '../data' if os.path.exists('../data') else 'data' if os.path.exists('data') else '.'

if wallet_input:
    # Match specific wallet (case-insensitive) - try exact match first, then prefix
    all_files = glob.glob(f'{data_dir}/polymarket_closed_positions_*.csv')
    # Try exact match first (full wallet address)
    positions_files = [f for f in all_files if wallet_input.lower() in os.path.basename(f).lower()]
    # If no exact match, try prefix match (first 10 chars for backwards compatibility)
    if not positions_files:
        wallet_short = wallet_input[:10]
        positions_files = [f for f in all_files if wallet_short.lower() in os.path.basename(f).lower()]
else:
    # Use latest files
    positions_files = glob.glob(f'{data_dir}/polymarket_closed_positions_*.csv')

if not positions_files:
    print("\n" + "="*60)
    print("ERROR: No closed positions data found!")
    print("="*60)
    if wallet_input:
        print(f"\nNo data found for wallet: {wallet_input[:10]}")
    print("\nPlease run the data fetcher first:")
    print("  python polymarket_api_fetcher.py <wallet_address>")
    print("\nThis will generate the required CSV file in the data/ directory")
    sys.exit(1)

# Use the most recent file
positions_file = sorted(positions_files)[-1]

# Extract wallet from filename
wallet_from_file = positions_file.split('_')[-1].replace('.csv', '')

print(f"\nLoading data from:")
print(f"  Wallet: {wallet_from_file}")
print(f"  - {positions_file}")
print()

# Load data
positions = pd.read_csv(positions_file)

# Convert timestamps
positions['Timestamp'] = pd.to_datetime(positions['Timestamp'])

print(f"Loaded {len(positions)} closed positions")

# Calculate total trades from positions data
total_trades = positions['Trades'].sum() if 'Trades' in positions.columns else 0
if total_trades > 0:
    print(f"Total trades across all positions: {int(total_trades)}")

# Calculate metrics
print("\nCalculating performance metrics...")
total_pnl = positions['Realized PnL'].sum()
num_positions = len(positions)
winning_positions = positions[positions['Realized PnL'] > 0]
losing_positions = positions[positions['Realized PnL'] < 0]
breakeven_positions = positions[positions['Realized PnL'] == 0]

win_rate = len(winning_positions) / num_positions * 100
avg_win = winning_positions['Realized PnL'].mean() if len(winning_positions) > 0 else 0
avg_loss = losing_positions['Realized PnL'].mean() if len(losing_positions) > 0 else 0
best_trade = positions['Realized PnL'].max()
worst_trade = positions['Realized PnL'].min()

risk_reward_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
total_wins = winning_positions['Realized PnL'].sum()
total_losses = abs(losing_positions['Realized PnL'].sum())
profit_factor = total_wins / total_losses if total_losses > 0 else 0

# Position sizing and trading patterns
avg_position_size = positions['Total Bought'].mean()
median_position_size = positions['Total Bought'].median()
avg_entry_price = positions['Avg Price'].mean()
median_entry_price = positions['Avg Price'].median()
avg_trades_per_position = positions['Trades'].mean() if 'Trades' in positions.columns else 0

# Calculate holding time if we have enough data
positions_sorted = positions.sort_values('Timestamp')
if len(positions_sorted) > 1:
    time_diffs = positions_sorted['Timestamp'].diff()
    avg_holding_time_hours = time_diffs.dt.total_seconds().mean() / 3600 if len(time_diffs) > 1 else 0
else:
    avg_holding_time_hours = 0

# Calculate drawdown
positions_sorted['Cumulative PnL'] = positions_sorted['Realized PnL'].cumsum()
running_max = positions_sorted['Cumulative PnL'].expanding().max()
drawdown = positions_sorted['Cumulative PnL'] - running_max
max_drawdown = drawdown.min()

# Calculate consecutive wins/losses
positions_sorted['Win'] = positions_sorted['Realized PnL'] > 0
win_streaks = []
loss_streaks = []
current_streak = 0
last_was_win = None

for is_win in positions_sorted['Win']:
    if is_win:
        if last_was_win == True:
            current_streak += 1
        else:
            if last_was_win == False and current_streak > 0:
                loss_streaks.append(current_streak)
            current_streak = 1
        last_was_win = True
    else:
        if last_was_win == False:
            current_streak += 1
        else:
            if last_was_win == True and current_streak > 0:
                win_streaks.append(current_streak)
            current_streak = 1
        last_was_win = False

if current_streak > 0:
    if last_was_win:
        win_streaks.append(current_streak)
    else:
        loss_streaks.append(current_streak)

max_consecutive_wins = max(win_streaks) if win_streaks else 0
max_consecutive_losses = max(loss_streaks) if loss_streaks else 0

# HFT Detection Metrics
positions_sorted['Hour'] = positions_sorted['Timestamp'].dt.floor('h')
positions_per_hour = positions_sorted.groupby('Hour').size()
avg_positions_per_hour = positions_per_hour.mean()
median_positions_per_hour = positions_per_hour.median()
max_positions_per_hour = positions_per_hour.max()

# Calculate median time between positions (in minutes)
time_diffs = positions_sorted['Timestamp'].diff()
median_time_between_positions = time_diffs.median().total_seconds() / 60 if len(time_diffs) > 1 else 0

# Calculate total trading duration
trading_duration_hours = (positions_sorted['Timestamp'].max() - positions_sorted['Timestamp'].min()).total_seconds() / 3600

# HFT Classification
if median_time_between_positions < 5 and avg_positions_per_hour > 10:
    trading_style = "HFT Bot"
    trading_style_emoji = "⚡"
    badge_class = "hft"
elif avg_positions_per_hour > 5:
    trading_style = "Active Trader"
    trading_style_emoji = "📈"
    badge_class = "active"
else:
    trading_style = "Normal Trader"
    trading_style_emoji = "📊"
    badge_class = "normal"

# Prepare chart data
chart_data = {
    'cumulative_pnl': {
        'timestamps': positions_sorted['Timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
        'values': positions_sorted['Cumulative PnL'].tolist()
    },
    'win_loss': {
        'labels': ['Wins', 'Losses', 'Breakeven'],
        'values': [len(winning_positions), len(losing_positions), len(breakeven_positions)]
    },
    'pnl_distribution': positions['Realized PnL'].tolist(),
    'outcome_pnl': {
        'outcomes': positions.groupby('Outcome')['Realized PnL'].sum().index.tolist(),
        'values': positions.groupby('Outcome')['Realized PnL'].sum().tolist()
    },
    'hourly_pnl': {
        'hours': list(range(24)),
        'values': [positions_sorted[positions_sorted['Timestamp'].dt.hour == h]['Realized PnL'].sum()
                   for h in range(24)]
    },
    'position_sizes': positions['Total Bought'].tolist(),
    'roi_distribution': (positions['Realized PnL'] / (positions['Avg Price'] * positions['Total Bought']) * 100).tolist(),
    'drawdown': drawdown.tolist(),
    'entry_vs_pnl': {
        'entry_prices': positions['Avg Price'].tolist(),
        'pnl': positions['Realized PnL'].tolist()
    },
    'size_vs_pnl': {
        'sizes': positions['Total Bought'].tolist(),
        'pnl': positions['Realized PnL'].tolist()
    }
}

# Generate metrics cards HTML
metrics_cards_html = f"""
<div class="metric-card {('positive' if total_pnl > 0 else 'negative')}">
    <div class="metric-label">Total Realized PnL</div>
    <div class="metric-value {('positive' if total_pnl > 0 else 'negative')}">${total_pnl:,.2f}</div>
</div>
<div class="metric-card">
    <div class="metric-label">Trading Style</div>
    <div class="metric-value"><span class="badge {badge_class}">{trading_style_emoji} {trading_style}</span></div>
</div>
<div class="metric-card">
    <div class="metric-label">Total Positions</div>
    <div class="metric-value">{num_positions:,}</div>
</div>
<div class="metric-card positive">
    <div class="metric-label">Win Rate</div>
    <div class="metric-value">{win_rate:.2f}%</div>
</div>
<div class="metric-card positive">
    <div class="metric-label">Average Win</div>
    <div class="metric-value">${avg_win:.2f}</div>
</div>
<div class="metric-card negative">
    <div class="metric-label">Average Loss</div>
    <div class="metric-value">${avg_loss:.2f}</div>
</div>
<div class="metric-card positive">
    <div class="metric-label">Best Trade</div>
    <div class="metric-value positive">${best_trade:.2f}</div>
</div>
<div class="metric-card negative">
    <div class="metric-label">Worst Trade</div>
    <div class="metric-value negative">${worst_trade:.2f}</div>
</div>
<div class="metric-card">
    <div class="metric-label">Risk/Reward Ratio</div>
    <div class="metric-value">{risk_reward_ratio:.2f}</div>
</div>
<div class="metric-card {('positive' if profit_factor > 1 else 'negative')}">
    <div class="metric-label">Profit Factor</div>
    <div class="metric-value">{profit_factor:.2f}</div>
</div>
<div class="metric-card negative">
    <div class="metric-label">Max Drawdown</div>
    <div class="metric-value negative">${max_drawdown:.2f}</div>
</div>
<div class="metric-card">
    <div class="metric-label">Max Consecutive Wins</div>
    <div class="metric-value">{int(max_consecutive_wins)}</div>
</div>
<div class="metric-card">
    <div class="metric-label">Max Consecutive Losses</div>
    <div class="metric-value">{int(max_consecutive_losses)}</div>
</div>
<div class="metric-card">
    <div class="metric-label">Avg Position Size</div>
    <div class="metric-value">{avg_position_size:.2f}</div>
</div>
<div class="metric-card">
    <div class="metric-label">Avg Positions/Hour</div>
    <div class="metric-value">{avg_positions_per_hour:.1f}</div>
</div>
<div class="metric-card">
    <div class="metric-label">Median Time Between Positions</div>
    <div class="metric-value">{median_time_between_positions:.1f} min</div>
</div>
<div class="metric-card">
    <div class="metric-label">Total Trades Executed</div>
    <div class="metric-value">{int(total_trades) if total_trades > 0 else 'N/A'}</div>
</div>
<div class="metric-card">
    <div class="metric-label">Trading Duration</div>
    <div class="metric-value">{trading_duration_hours:.1f} hrs</div>
</div>
"""

# Top winners table
top_winners = positions.nlargest(10, 'Realized PnL')
top_winners_html = ""
for _, row in top_winners.iterrows():
    top_winners_html += f"""
    <tr>
        <td>{row['Market Title'][:80]}</td>
        <td>{row['Outcome']}</td>
        <td class="positive-value">${row['Realized PnL']:.2f}</td>
        <td>${row['Avg Price']:.4f}</td>
        <td>{row['Total Bought']:.2f}</td>
        <td>{int(row['Trades']) if 'Trades' in row and pd.notna(row['Trades']) else 'N/A'}</td>
        <td>{pd.to_datetime(row['Timestamp']).strftime('%Y-%m-%d %H:%M')}</td>
    </tr>
    """

# Top losers table
top_losers = positions.nsmallest(10, 'Realized PnL')
top_losers_html = ""
for _, row in top_losers.iterrows():
    top_losers_html += f"""
    <tr>
        <td>{row['Market Title'][:80]}</td>
        <td>{row['Outcome']}</td>
        <td class="negative-value">${row['Realized PnL']:.2f}</td>
        <td>${row['Avg Price']:.4f}</td>
        <td>{row['Total Bought']:.2f}</td>
        <td>{int(row['Trades']) if 'Trades' in row and pd.notna(row['Trades']) else 'N/A'}</td>
        <td>{pd.to_datetime(row['Timestamp']).strftime('%Y-%m-%d %H:%M')}</td>
    </tr>
    """

# All positions data for JavaScript
all_positions_data = []
for _, row in positions.iterrows():
    roi = (row['Realized PnL'] / (row['Avg Price'] * row['Total Bought']) * 100) if (row['Avg Price'] * row['Total Bought']) != 0 else 0
    # Use 'Exit Price' column if available, fallback to 'Current Price'
    exit_price = row.get('Exit Price', row.get('Current Price', 0))
    all_positions_data.append({
        'timestamp': pd.to_datetime(row['Timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
        'market': row['Market Title'][:60],
        'outcome': row['Outcome'],
        'entry_price': float(row['Avg Price']),
        'size': float(row['Total Bought']),
        'exit_price': float(exit_price) if pd.notna(exit_price) else 0,
        'trades': int(row['Trades']) if 'Trades' in row and pd.notna(row['Trades']) else 0,
        'pnl': float(row['Realized PnL']),
        'roi': float(roi)
    })

# Load HTML template
template_path = '../templates/report_template.html' if os.path.exists('../templates') else 'templates/report_template.html'
with open(template_path, 'r') as f:
    template = f.read()

# Replace placeholders
html_output = template.replace('{{wallet}}', wallet_from_file)
html_output = html_output.replace('{{timestamp}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
html_output = html_output.replace('{{metrics_cards}}', metrics_cards_html)
html_output = html_output.replace('{{chart_data}}', json.dumps(chart_data))
html_output = html_output.replace('{{top_winners}}', top_winners_html)
html_output = html_output.replace('{{top_losers}}', top_losers_html)
html_output = html_output.replace('{{all_positions}}', '')  # Will be loaded via JS
html_output = html_output.replace('{{all_positions_data}}', json.dumps(all_positions_data))
html_output = html_output.replace('{{total_positions}}', str(len(positions)))

# Save to reports directory
reports_dir = '../reports' if os.path.exists('../reports') else 'reports'
os.makedirs(reports_dir, exist_ok=True)

html_filename = f'{reports_dir}/polymarket_performance_report_{wallet_from_file}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

with open(html_filename, 'w', encoding='utf-8') as f:
    f.write(html_output)

print(f"\n{'='*60}")
print(f"✓ Interactive HTML report saved to:")
print(f"  {html_filename}")
print(f"{'='*60}")
print(f"\n📊 Report includes:")
print(f"  - Overview Dashboard with key metrics")
print(f"  - {len(chart_data)} interactive charts (Plotly.js)")
print(f"  - Top 10 winning and losing trades")
print(f"  - All {len(positions)} positions with search & pagination")
print(f"  - Mobile-friendly responsive design")
print(f"\n💡 Open the file in your web browser to view the report")
print(f"{'='*60}")

print("\nPerformance Summary:")
print(f"  Trading Style: {trading_style_emoji} {trading_style}")
print(f"  Total PnL: ${total_pnl:,.2f}")
print(f"  Win Rate: {win_rate:.2f}%")
print(f"  Profit Factor: {profit_factor:.2f}")
print(f"  Avg Positions/Hour: {avg_positions_per_hour:.1f}")
