#!/usr/bin/env python3
"""
Generate Performance Report PDF from Polymarket Trading Data
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import warnings
import sys
import os
import glob
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Prompt for wallet address to match data files
wallet_input = input("\nEnter wallet address to generate report for (or press Enter for latest): ").strip()

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

# Calculate total trades from positions data (more reliable than trades CSV)
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

# NEW METRICS - Position sizing and trading patterns
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

# HFT Detection Metrics - Position frequency analysis
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
# HFT: >10 positions/hour AND <5 min between positions
# Active: >5 positions/hour
# Normal: <=5 positions/hour
if median_time_between_positions < 5 and avg_positions_per_hour > 10:
    trading_style = "HFT Bot"
    trading_style_emoji = "⚡"
elif avg_positions_per_hour > 5:
    trading_style = "Active Trader"
    trading_style_emoji = "📈"
else:
    trading_style = "Normal Trader"
    trading_style_emoji = "📊"

# Summary metrics with HFT detection
summary_metrics = pd.DataFrame({
    'Metric': [
        'Trading Style',
        'Total Realized PnL',
        'Total Positions',
        'Winning Positions',
        'Losing Positions',
        'Win Rate',
        'Average Win',
        'Average Loss',
        'Best Trade',
        'Worst Trade',
        'Risk/Reward Ratio',
        'Profit Factor',
        'Max Drawdown',
        'Max Consecutive Wins',
        'Max Consecutive Losses',
        'Avg Position Size',
        'Median Position Size',
        'Avg Entry Price',
        'Median Entry Price',
        'Avg Trades/Position',
        'Trading Duration (hrs)',
        'Avg Positions/Hour',
        'Median Time Between Pos (min)',
        'Max Positions/Hour',
        'Total Trades Executed'
    ],
    'Value': [
        f"{trading_style_emoji} {trading_style}",
        f"${total_pnl:.2f}",
        num_positions,
        len(winning_positions),
        len(losing_positions),
        f"{win_rate:.2f}%",
        f"${avg_win:.2f}",
        f"${avg_loss:.2f}",
        f"${best_trade:.2f}",
        f"${worst_trade:.2f}",
        f"{risk_reward_ratio:.2f}",
        f"{profit_factor:.2f}",
        f"${max_drawdown:.2f}",
        int(max_consecutive_wins),
        int(max_consecutive_losses),
        f"{avg_position_size:.2f}",
        f"{median_position_size:.2f}",
        f"${avg_entry_price:.4f}",
        f"${median_entry_price:.4f}",
        f"{avg_trades_per_position:.1f}",
        f"{trading_duration_hours:.1f}",
        f"{avg_positions_per_hour:.1f}",
        f"{median_time_between_positions:.1f}",
        int(max_positions_per_hour),
        int(total_trades) if total_trades > 0 else 'N/A'
    ]
})

# Top winners and losers
top_winners = positions.nlargest(10, 'Realized PnL')[[
    'Market Title', 'Outcome', 'Realized PnL', 'Avg Price', 'Total Bought', 'Trades', 'Timestamp'
]].copy()
top_winners['Timestamp'] = top_winners['Timestamp'].dt.strftime('%Y-%m-%d %H:%M')

top_losers = positions.nsmallest(10, 'Realized PnL')[[
    'Market Title', 'Outcome', 'Realized PnL', 'Avg Price', 'Total Bought', 'Trades', 'Timestamp'
]].copy()
top_losers['Timestamp'] = top_losers['Timestamp'].dt.strftime('%Y-%m-%d %H:%M')

# All closed positions
closed_positions_table = positions[[
    'Timestamp', 'Market Title', 'Outcome', 'Avg Price', 'Total Bought',
    'Current Price', 'Trades', 'Realized PnL'
]].copy()
closed_positions_table = closed_positions_table.sort_values('Timestamp', ascending=False)
closed_positions_table['Timestamp'] = closed_positions_table['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
closed_positions_table.columns = [
    'Close Time', 'Market', 'Side', 'Entry Price', 'Size', 'Exit Price', 'Trades', 'PnL ($)'
]
closed_positions_table['ROI (%)'] = (
    positions['Realized PnL'].values /
    (positions['Avg Price'].values * positions['Total Bought'].values) * 100
).round(2)
closed_positions_table['PnL ($)'] = closed_positions_table['PnL ($)'].apply(lambda x: f"${x:.2f}")

# Prepare data for visualizations
positions_sorted = positions.sort_values('Timestamp')
positions_sorted['Cumulative PnL'] = positions_sorted['Realized PnL'].cumsum()
positions_sorted['Hour'] = positions_sorted['Timestamp'].dt.hour

outcome_pnl = positions.groupby('Outcome')['Realized PnL'].sum()
hourly_pnl = positions_sorted.groupby('Hour')['Realized PnL'].sum()
win_loss_data = [len(winning_positions), len(losing_positions), len(breakeven_positions)]
colors = ['#06A77D', '#D72638', '#FFA69E']

# Generate PDF
print("\nGenerating PDF report...")

# Save to reports directory
reports_dir = '../reports' if os.path.exists('../reports') else 'reports'
os.makedirs(reports_dir, exist_ok=True)

pdf_filename = f'{reports_dir}/polymarket_performance_report_{wallet_from_file}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

with PdfPages(pdf_filename) as pdf:

    # Page 1: Performance Dashboard
    fig1, axes1 = plt.subplots(2, 3, figsize=(16, 11))
    fig1.suptitle(f'Polymarket Trading Performance Report\\nWallet: {wallet_from_file}',
                  fontsize=14, fontweight='bold')

    # 1. Cumulative PnL
    axes1[0, 0].plot(positions_sorted['Timestamp'], positions_sorted['Cumulative PnL'],
                    linewidth=2, color='#2E86AB')
    axes1[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes1[0, 0].set_title('Cumulative PnL Over Time', fontweight='bold')
    axes1[0, 0].set_ylabel('Cumulative PnL ($)')
    axes1[0, 0].grid(True, alpha=0.3)
    axes1[0, 0].tick_params(axis='x', rotation=45)

    # 2. Win/Loss pie
    axes1[0, 1].pie(win_loss_data, labels=['Wins', 'Losses', 'Breakeven'],
                   autopct='%1.1f%%', colors=colors, startangle=90)
    axes1[0, 1].set_title('Win/Loss Distribution', fontweight='bold')

    # 3. PnL histogram
    axes1[0, 2].hist(positions['Realized PnL'], bins=30, color='#4ECDC4', edgecolor='black', alpha=0.7)
    axes1[0, 2].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes1[0, 2].set_title('PnL Distribution', fontweight='bold')
    axes1[0, 2].set_xlabel('Realized PnL ($)')
    axes1[0, 2].set_ylabel('Frequency')
    axes1[0, 2].grid(True, alpha=0.3)

    # 4. Outcome analysis
    outcome_pnl.plot(kind='bar', ax=axes1[1, 0], color=['#FF6B6B', '#4ECDC4'])
    axes1[1, 0].set_title('PnL by Outcome', fontweight='bold')
    axes1[1, 0].set_xlabel('Outcome')
    axes1[1, 0].set_ylabel('Total PnL ($)')
    axes1[1, 0].tick_params(axis='x', rotation=0)
    axes1[1, 0].grid(True, alpha=0.3, axis='y')

    # 5. Hourly PnL
    axes1[1, 1].bar(hourly_pnl.index, hourly_pnl.values, color='#95B8D1', edgecolor='black')
    axes1[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes1[1, 1].set_title('PnL by Hour of Day', fontweight='bold')
    axes1[1, 1].set_xlabel('Hour (UTC)')
    axes1[1, 1].set_ylabel('Total PnL ($)')
    axes1[1, 1].grid(True, alpha=0.3, axis='y')

    # 6. Summary table
    axes1[1, 2].axis('off')
    table_data = summary_metrics.values
    table = axes1[1, 2].table(cellText=table_data, colLabels=['Metric', 'Value'],
                             cellLoc='left', loc='center',
                             colWidths=[0.6, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)

    for i in range(2):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')

    plt.tight_layout()
    pdf.savefig(fig1, bbox_inches='tight')
    plt.close()

    # Page 2: Top Winners and Losers
    fig2 = plt.figure(figsize=(16, 11))
    fig2.suptitle('Top 10 Best & Worst Trades', fontsize=14, fontweight='bold')

    ax1 = plt.subplot(2, 1, 1)
    ax1.axis('off')
    winners_table = ax1.table(
        cellText=top_winners.values,
        colLabels=top_winners.columns,
        cellLoc='left',
        loc='center',
        colWidths=[0.35, 0.08, 0.12, 0.08, 0.08, 0.07, 0.12]
    )
    winners_table.auto_set_font_size(False)
    winners_table.set_fontsize(8)
    winners_table.scale(1, 2)

    for i in range(len(top_winners.columns)):
        winners_table[(0, i)].set_facecolor('#06A77D')
        winners_table[(0, i)].set_text_props(weight='bold', color='white')

    ax1.set_title('Top 10 Winning Trades', fontweight='bold', pad=20)

    ax2 = plt.subplot(2, 1, 2)
    ax2.axis('off')
    losers_table = ax2.table(
        cellText=top_losers.values,
        colLabels=top_losers.columns,
        cellLoc='left',
        loc='center',
        colWidths=[0.35, 0.08, 0.12, 0.08, 0.08, 0.07, 0.12]
    )
    losers_table.auto_set_font_size(False)
    losers_table.set_fontsize(8)
    losers_table.scale(1, 2)

    for i in range(len(top_losers.columns)):
        losers_table[(0, i)].set_facecolor('#D72638')
        losers_table[(0, i)].set_text_props(weight='bold', color='white')

    ax2.set_title('Top 10 Losing Trades', fontweight='bold', pad=20)

    plt.tight_layout()
    pdf.savefig(fig2, bbox_inches='tight')
    plt.close()

    # Page 3: Advanced Analytics
    fig3, axes3 = plt.subplots(2, 3, figsize=(16, 11))
    fig3.suptitle('Advanced Trading Analytics', fontsize=14, fontweight='bold')

    # 1. Position Size Distribution
    axes3[0, 0].hist(positions['Total Bought'], bins=25, color='#9B59B6', edgecolor='black', alpha=0.7)
    axes3[0, 0].axvline(avg_position_size, color='red', linestyle='--', linewidth=2, label=f'Mean: {avg_position_size:.1f}')
    axes3[0, 0].axvline(median_position_size, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_position_size:.1f}')
    axes3[0, 0].set_title('Position Size Distribution', fontweight='bold')
    axes3[0, 0].set_xlabel('Position Size (shares)')
    axes3[0, 0].set_ylabel('Frequency')
    axes3[0, 0].legend()
    axes3[0, 0].grid(True, alpha=0.3)

    # 2. Entry Price vs PnL Scatter (sample for large datasets)
    plot_data = positions if len(positions) <= 2000 else positions.sample(n=2000, random_state=42)
    scatter = axes3[0, 1].scatter(plot_data['Avg Price'], plot_data['Realized PnL'],
                                   c=plot_data['Realized PnL'], cmap='RdYlGn',
                                   alpha=0.6, edgecolors='black', s=100)
    axes3[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes3[0, 1].axvline(avg_entry_price, color='blue', linestyle='--', alpha=0.5, label=f'Avg Entry: ${avg_entry_price:.4f}')
    title_suffix = '' if len(positions) <= 2000 else f' (sample of 2000/{len(positions)})'
    axes3[0, 1].set_title(f'Entry Price vs PnL{title_suffix}', fontweight='bold')
    axes3[0, 1].set_xlabel('Average Entry Price ($)')
    axes3[0, 1].set_ylabel('Realized PnL ($)')
    axes3[0, 1].legend()
    axes3[0, 1].grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=axes3[0, 1], label='PnL ($)')

    # 3. Trades Per Position
    if 'Trades' in positions.columns and positions['Trades'].sum() > 0:
        axes3[0, 2].hist(positions['Trades'], bins=range(1, int(positions['Trades'].max())+2),
                         color='#16A085', edgecolor='black', alpha=0.7)
        axes3[0, 2].axvline(avg_trades_per_position, color='red', linestyle='--', linewidth=2,
                           label=f'Avg: {avg_trades_per_position:.1f}')
        axes3[0, 2].set_title('Trades Per Position', fontweight='bold')
        axes3[0, 2].set_xlabel('Number of Trades')
        axes3[0, 2].set_ylabel('Frequency')
        axes3[0, 2].legend()
        axes3[0, 2].grid(True, alpha=0.3, axis='y')
    else:
        axes3[0, 2].text(0.5, 0.5, 'Trade count data\nnot available',
                        ha='center', va='center', fontsize=12)
        axes3[0, 2].set_title('Trades Per Position', fontweight='bold')
        axes3[0, 2].axis('off')

    # 4. Drawdown Chart (sample for large datasets to improve performance)
    if len(drawdown) > 2000:
        # Sample every Nth point to keep visualization clean
        sample_step = max(1, len(drawdown) // 2000)
        drawdown_sampled = drawdown[::sample_step]
        x_indices = range(0, len(drawdown), sample_step)
        axes3[1, 0].fill_between(x_indices, drawdown_sampled, 0, color='red', alpha=0.3)
        axes3[1, 0].plot(x_indices, drawdown_sampled, color='darkred', linewidth=2)
        dd_title_suffix = f' (sample: every {sample_step}th position)'
    else:
        axes3[1, 0].fill_between(range(len(drawdown)), drawdown, 0, color='red', alpha=0.3)
        axes3[1, 0].plot(drawdown, color='darkred', linewidth=2)
        dd_title_suffix = ''
    axes3[1, 0].axhline(y=max_drawdown, color='red', linestyle='--', linewidth=1,
                       label=f'Max DD: ${max_drawdown:.2f}')
    axes3[1, 0].set_title(f'Drawdown Over Time{dd_title_suffix}', fontweight='bold')
    axes3[1, 0].set_xlabel('Position Number')
    axes3[1, 0].set_ylabel('Drawdown ($)')
    axes3[1, 0].legend()
    axes3[1, 0].grid(True, alpha=0.3)

    # 5. Position Size vs PnL (sample for large datasets)
    plot_data2 = positions if len(positions) <= 2000 else positions.sample(n=2000, random_state=43)
    axes3[1, 1].scatter(plot_data2['Total Bought'], plot_data2['Realized PnL'],
                       c=plot_data2['Realized PnL'], cmap='RdYlGn',
                       alpha=0.6, edgecolors='black', s=100)
    axes3[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    title_suffix2 = '' if len(positions) <= 2000 else f' (sample of 2000/{len(positions)})'
    axes3[1, 1].set_title(f'Position Size vs PnL{title_suffix2}', fontweight='bold')
    axes3[1, 1].set_xlabel('Position Size (shares)')
    axes3[1, 1].set_ylabel('Realized PnL ($)')
    axes3[1, 1].grid(True, alpha=0.3)

    # 6. ROI Distribution
    roi = (positions['Realized PnL'] / (positions['Avg Price'] * positions['Total Bought']) * 100)
    axes3[1, 2].hist(roi, bins=30, color='#E67E22', edgecolor='black', alpha=0.7)
    axes3[1, 2].axvline(roi.mean(), color='red', linestyle='--', linewidth=2,
                       label=f'Avg ROI: {roi.mean():.1f}%')
    axes3[1, 2].axvline(0, color='black', linestyle='-', linewidth=1)
    axes3[1, 2].set_title('ROI Distribution', fontweight='bold')
    axes3[1, 2].set_xlabel('ROI (%)')
    axes3[1, 2].set_ylabel('Frequency')
    axes3[1, 2].legend()
    axes3[1, 2].grid(True, alpha=0.3)

    plt.tight_layout()
    pdf.savefig(fig3, bbox_inches='tight')
    plt.close()

    # Pages 4+: All closed positions (limit to avoid huge PDFs)
    rows_per_page = 30
    MAX_POSITION_PAGES = 50  # Limit to avoid huge PDFs for high-volume wallets
    total_pages = (len(closed_positions_table) + rows_per_page - 1) // rows_per_page
    num_pages = min(total_pages, MAX_POSITION_PAGES)

    if total_pages > MAX_POSITION_PAGES:
        print(f"  Note: Limiting to first {MAX_POSITION_PAGES} pages ({MAX_POSITION_PAGES * rows_per_page} positions) out of {total_pages} total pages")
        print(f"  ({len(closed_positions_table) - MAX_POSITION_PAGES * rows_per_page} positions omitted from PDF - see CSV for complete data)")

    print(f"  Generating {num_pages} pages of closed positions...")
    for page in range(num_pages):
        if page % 10 == 0 and page > 0:
            print(f"    Progress: {page}/{num_pages} pages generated...")

        start_idx = page * rows_per_page
        end_idx = min((page + 1) * rows_per_page, len(closed_positions_table))
        page_data = closed_positions_table.iloc[start_idx:end_idx]

        fig3 = plt.figure(figsize=(16, 11))
        fig3.suptitle(f'All Closed Positions (Page {page+1} of {num_pages})',
                     fontsize=14, fontweight='bold')

        ax = plt.subplot(1, 1, 1)
        ax.axis('off')

        table = ax.table(
            cellText=page_data.values,
            colLabels=page_data.columns,
            cellLoc='left',
            loc='center',
            colWidths=[0.11, 0.32, 0.07, 0.07, 0.07, 0.07, 0.05, 0.09, 0.07]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(7)
        table.scale(1, 1.8)

        for i in range(len(page_data.columns)):
            table[(0, i)].set_facecolor('#2E86AB')
            table[(0, i)].set_text_props(weight='bold', color='white')

        plt.tight_layout()
        pdf.savefig(fig3, bbox_inches='tight')
        plt.close()

    # Add metadata
    d = pdf.infodict()
    d['Title'] = 'Polymarket Trading Performance Report'
    d['Author'] = 'Polymarket Analysis Tool'
    d['Subject'] = f'Trading performance for wallet {wallet_from_file}'
    d['CreationDate'] = datetime.now()

print(f"\n{'='*60}")
print(f"✓ Performance report saved to: {pdf_filename}")
print(f"{'='*60}")
print(f"  Total pages: {3 + num_pages}")
print(f"  - Page 1: Performance Dashboard")
print(f"  - Page 2: Top 10 Best & Worst Trades")
print(f"  - Page 3: Advanced Trading Analytics")
positions_shown = min(num_pages * rows_per_page, len(closed_positions_table))
print(f"  - Pages 4-{3+num_pages}: Closed Positions ({positions_shown}/{len(closed_positions_table)} shown)")
if total_pages > MAX_POSITION_PAGES:
    print(f"    Note: PDF limited to {MAX_POSITION_PAGES} pages. See CSV for complete data.")
print(f"{'='*60}")

print("\nPerformance Summary:")
print(summary_metrics.to_string(index=False))
