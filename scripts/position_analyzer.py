#!/usr/bin/env python3
"""
Polymarket Position Reconstruction Engine
Rebuilds closed trades from on-chain events using proper position accounting
"""

import requests
import sys
import csv
from datetime import datetime
from collections import defaultdict
from decimal import Decimal, getcontext

# Set high precision for financial calculations
getcontext().prec = 28


class PositionState:
    """Tracks state of a single position (wallet + tokenID)"""

    def __init__(self, token_id):
        self.token_id = token_id
        self.size = Decimal('0')  # Current position size
        self.avg_price = Decimal('0')  # Weighted average entry price
        self.realized_pnl = Decimal('0')  # Realized profit/loss
        self.trades = []  # History of all trades
        self.is_closed = False

    def buy(self, size, price, timestamp, tx_hash):
        """Add to position (weighted average cost)"""
        size = Decimal(str(size))
        price = Decimal(str(price))

        if self.size == 0:
            self.avg_price = price
        else:
            total_cost = (self.size * self.avg_price) + (size * price)
            self.size += size
            self.avg_price = total_cost / self.size
            return

        self.size += size
        self.trades.append({
            'type': 'BUY',
            'size': float(size),
            'price': float(price),
            'timestamp': timestamp,
            'tx_hash': tx_hash
        })

    def sell(self, size, price, timestamp, tx_hash):
        """Reduce position and realize PnL"""
        size = Decimal(str(size))
        price = Decimal(str(price))

        if size > self.size:
            print(f"WARNING: Selling {size} but only have {self.size}")
            size = self.size

        # Realize PnL on sold portion
        pnl = size * (price - self.avg_price)
        self.realized_pnl += pnl
        self.size -= size

        self.trades.append({
            'type': 'SELL',
            'size': float(size),
            'price': float(price),
            'pnl': float(pnl),
            'timestamp': timestamp,
            'tx_hash': tx_hash
        })

        # Check if position is closed
        if self.size == 0:
            self.is_closed = True

    def redeem(self, size, payout_price, timestamp, tx_hash):
        """Redeem tokens after market resolution"""
        size = Decimal(str(size))
        payout_price = Decimal(str(payout_price))

        pnl = size * (payout_price - self.avg_price)
        self.realized_pnl += pnl
        self.size -= size

        self.trades.append({
            'type': 'REDEEM',
            'size': float(size),
            'payout_price': float(payout_price),
            'pnl': float(pnl),
            'timestamp': timestamp,
            'tx_hash': tx_hash
        })

        if self.size == 0:
            self.is_closed = True


class PolymarketPositionAnalyzer:
    """Reconstructs Polymarket positions from on-chain events"""

    # Polymarket contracts
    CTF_EXCHANGE = "0xe111180000d2663c0091e4f400237545b87b996b"
    NEG_RISK_CTF = "0xe2222d279d744050d28e00520010520000310f59"
    CTF_CONTRACT = "0x4d97dcd97ec945f40cf65f87097ace5ea0476045"

    # Token contracts
    PUSD_CONTRACT = "0xc011a7e12a19f7b1f670d46f03b03f3342e82dfb"

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.etherscan.io/v2/api"

    def fetch_erc1155_transfers(self, wallet_address):
        """Fetch all ERC-1155 token transfers (position tokens)"""
        print(f"Fetching ERC-1155 position tokens for {wallet_address}...")

        all_transfers = []
        page = 1

        while True:
            params = {
                'chainid': '137',
                'module': 'account',
                'action': 'token1155tx',
                'address': wallet_address,
                'page': page,
                'offset': 1000,
                'sort': 'asc',
                'apikey': self.api_key
            }

            response = requests.get(self.base_url, params=params)
            data = response.json()

            if data['status'] != '1':
                break

            transfers = data.get('result', [])
            if not transfers or len(transfers) == 0:
                break

            all_transfers.extend(transfers)
            print(f"  Page {page}: {len(transfers)} transfers")

            if len(transfers) < 1000:
                break

            page += 1

        print(f"Total ERC-1155 transfers: {len(all_transfers)}\n")
        return all_transfers

    def fetch_pusd_transfers(self, wallet_address):
        """Fetch pUSD transfers to calculate prices"""
        print(f"Fetching pUSD transfers for price calculation...")

        all_transfers = []
        page = 1

        while True:
            params = {
                'chainid': '137',
                'module': 'account',
                'action': 'tokentx',
                'address': wallet_address,
                'contractaddress': self.PUSD_CONTRACT,
                'page': page,
                'offset': 1000,
                'sort': 'asc',
                'apikey': self.api_key
            }

            response = requests.get(self.base_url, params=params)
            data = response.json()

            if data['status'] != '1':
                break

            transfers = data.get('result', [])
            if not transfers:
                break

            all_transfers.extend(transfers)
            print(f"  Page {page}: {len(transfers)} transfers")

            if len(transfers) < 1000:
                break

            page += 1

        print(f"Total pUSD transfers: {len(all_transfers)}\n")
        return all_transfers

    def build_tx_pusd_map(self, pusd_transfers, wallet_address):
        """Build map of tx_hash -> pUSD delta for price calculation"""
        tx_map = defaultdict(lambda: {'in': Decimal('0'), 'out': Decimal('0')})

        wallet_address = wallet_address.lower()

        for tx in pusd_transfers:
            tx_hash = tx['hash']
            from_addr = tx['from'].lower()
            to_addr = tx['to'].lower()
            value = Decimal(tx['value']) / Decimal('1000000')  # 6 decimals

            # Track pUSD flowing in and out
            if to_addr == wallet_address:
                tx_map[tx_hash]['in'] += value
            if from_addr == wallet_address:
                tx_map[tx_hash]['out'] += value

        return tx_map

    def reconstruct_positions(self, wallet_address):
        """Main reconstruction engine"""

        wallet_address = wallet_address.lower()

        # Fetch data
        erc1155_transfers = self.fetch_erc1155_transfers(wallet_address)
        pusd_transfers = self.fetch_pusd_transfers(wallet_address)

        # Build price calculation map
        tx_pusd_map = self.build_tx_pusd_map(pusd_transfers, wallet_address)

        # Position tracking
        positions = defaultdict(lambda: PositionState(None))

        print("Processing trades...")
        for i, transfer in enumerate(erc1155_transfers):
            token_id = transfer['tokenID']
            tx_hash = transfer['hash']
            from_addr = transfer['from'].lower()
            to_addr = transfer['to'].lower()
            timestamp = int(transfer['timeStamp'])

            # Token value in shares (6 decimals like pUSD)
            token_value = Decimal(transfer['tokenValue']) / Decimal('1000000')

            # Initialize position if needed
            if positions[token_id].token_id is None:
                positions[token_id].token_id = token_id

            # Determine if BUY or SELL
            is_buy = (to_addr == wallet_address)
            is_sell = (from_addr == wallet_address)

            # Calculate price from pUSD delta
            pusd_data = tx_pusd_map.get(tx_hash, {'in': Decimal('0'), 'out': Decimal('0')})

            if is_buy:
                # Bought tokens - paid pUSD
                pusd_paid = pusd_data['out']
                if token_value > 0:
                    price = pusd_paid / token_value
                else:
                    price = Decimal('0')

                positions[token_id].buy(token_value, price, timestamp, tx_hash)

            elif is_sell:
                # Sold tokens - received pUSD (or redeemed)
                pusd_received = pusd_data['in']

                # Check if this is a redemption (from zero address = mint pUSD)
                if pusd_received > 0:
                    price = pusd_received / token_value if token_value > 0 else Decimal('0')
                    positions[token_id].sell(token_value, price, timestamp, tx_hash)
                else:
                    # No pUSD received - likely burned/expired worthless
                    positions[token_id].sell(token_value, Decimal('0'), timestamp, tx_hash)

            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(erc1155_transfers)} transfers")

        print(f"\nTotal positions tracked: {len(positions)}")

        # Separate open vs closed
        closed_positions = {k: v for k, v in positions.items() if v.is_closed}
        open_positions = {k: v for k, v in positions.items() if not v.is_closed}

        print(f"Closed positions: {len(closed_positions)}")
        print(f"Open positions: {len(open_positions)}")

        return closed_positions, open_positions

    def export_to_csv(self, closed_positions, open_positions, wallet_address):
        """Export positions and trades to CSV files"""

        # Save to data directory
        import os
        data_dir = '../data' if os.path.exists('../data') else 'data'
        os.makedirs(data_dir, exist_ok=True)

        # Export all closed positions
        positions_csv = f"{data_dir}/positions_{wallet_address}.csv"
        with open(positions_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Token ID', 'Realized PnL', 'Num Trades', 'Entry Time', 'Exit Time', 'Duration (hours)', 'Status'])

            sorted_positions = sorted(
                closed_positions.items(),
                key=lambda x: x[1].realized_pnl,
                reverse=True
            )

            for token_id, pos in sorted_positions:
                entry_trade = pos.trades[0]
                exit_trade = pos.trades[-1]
                duration = exit_trade['timestamp'] - entry_trade['timestamp']
                duration_hours = duration / 3600

                if pos.realized_pnl > 0:
                    status = "WIN"
                elif pos.realized_pnl < 0:
                    status = "LOSS"
                else:
                    status = "BREAKEVEN"

                writer.writerow([
                    token_id,
                    float(pos.realized_pnl),
                    len(pos.trades),
                    datetime.fromtimestamp(entry_trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.fromtimestamp(exit_trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                    f"{duration_hours:.2f}",
                    status
                ])

        print(f"✓ Exported {len(closed_positions)} positions to {positions_csv}")

        # Export all individual trades
        trades_csv = f"{data_dir}/trades_{wallet_address}.csv"
        with open(trades_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Token ID', 'Trade Type', 'Size', 'Price', 'PnL', 'Timestamp', 'Tx Hash'])

            for token_id, pos in sorted_positions:
                for trade in pos.trades:
                    writer.writerow([
                        token_id,
                        trade['type'],
                        trade['size'],
                        trade.get('price', trade.get('payout_price', 0)),
                        trade.get('pnl', ''),
                        datetime.fromtimestamp(trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                        trade['tx_hash']
                    ])

        print(f"✓ Exported all individual trades to {trades_csv}")

        # Export open positions
        if open_positions:
            open_csv = f"{data_dir}/open_positions_{wallet_address}.csv"
            with open(open_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Token ID', 'Size', 'Avg Entry Price', 'Realized PnL'])

                for token_id, pos in open_positions.items():
                    writer.writerow([
                        token_id,
                        float(pos.size),
                        float(pos.avg_price),
                        float(pos.realized_pnl)
                    ])

            print(f"✓ Exported {len(open_positions)} open positions to {open_csv}")

        print()

    def generate_report(self, closed_positions, open_positions):
        """Generate detailed PnL report"""

        print("\n" + "="*80)
        print("POLYMARKET POSITION RECONSTRUCTION REPORT")
        print("="*80)

        # Closed positions analysis
        if closed_positions:
            print("\n" + "-"*80)
            print("CLOSED POSITIONS (Full Round-Trip Trades)")
            print("-"*80)

            total_realized_pnl = Decimal('0')
            winning_trades = 0
            losing_trades = 0

            # Sort by realized PnL
            sorted_positions = sorted(
                closed_positions.items(),
                key=lambda x: x[1].realized_pnl,
                reverse=True
            )

            for token_id, pos in sorted_positions:
                total_realized_pnl += pos.realized_pnl

                if pos.realized_pnl > 0:
                    winning_trades += 1
                elif pos.realized_pnl < 0:
                    losing_trades += 1

            # Show top 10 winners
            print("\nTOP 10 WINNING TRADES:")
            for i, (token_id, pos) in enumerate(sorted_positions[:10]):
                num_trades = len(pos.trades)
                entry_trade = pos.trades[0]
                exit_trade = pos.trades[-1]
                duration = exit_trade['timestamp'] - entry_trade['timestamp']
                duration_hours = duration / 3600

                print(f"\n{i+1}. Position {token_id[:16]}...")
                print(f"   Realized PnL: ${float(pos.realized_pnl):.2f}")
                print(f"   Number of trades: {num_trades}")
                print(f"   Duration: {duration_hours:.1f} hours")
                print(f"   Entry: {datetime.fromtimestamp(entry_trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Exit: {datetime.fromtimestamp(exit_trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")

            # Show bottom 10 losers
            print("\n\nTOP 10 LOSING TRADES:")
            for i, (token_id, pos) in enumerate(sorted_positions[-10:]):
                num_trades = len(pos.trades)
                entry_trade = pos.trades[0]
                exit_trade = pos.trades[-1]
                duration = exit_trade['timestamp'] - entry_trade['timestamp']
                duration_hours = duration / 3600

                print(f"\n{i+1}. Position {token_id[:16]}...")
                print(f"   Realized PnL: ${float(pos.realized_pnl):.2f}")
                print(f"   Number of trades: {num_trades}")
                print(f"   Duration: {duration_hours:.1f} hours")
                print(f"   Entry: {datetime.fromtimestamp(entry_trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Exit: {datetime.fromtimestamp(exit_trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")

            print(f"\n" + "-"*80)
            print(f"CLOSED POSITIONS SUMMARY")
            print(f"-"*80)
            print(f"Total Closed Positions: {len(closed_positions)}")
            print(f"Winning Trades: {winning_trades}")
            print(f"Losing Trades: {losing_trades}")
            print(f"Win Rate: {winning_trades/len(closed_positions)*100:.1f}%")
            print(f"Total Realized PnL: ${float(total_realized_pnl):.2f}")

        # Open positions
        if open_positions:
            print("\n" + "-"*80)
            print(f"OPEN POSITIONS ({len(open_positions)} positions)")
            print("-"*80)

            total_unrealized = Decimal('0')

            for token_id, pos in list(open_positions.items())[:10]:
                print(f"\nToken: {token_id[:16]}...")
                print(f"  Size: {float(pos.size):.2f} shares")
                print(f"  Avg Entry Price: ${float(pos.avg_price):.4f}")
                print(f"  Realized PnL (so far): ${float(pos.realized_pnl):.2f}")

        print("\n" + "="*80)


def main():
    from datetime import datetime, timedelta

    # Default API key
    DEFAULT_API_KEY = "ZA1X87TCSVVD53WECWZZ8UWJ7Y1VPKJ94A"

    # Get wallet address from command line or prompt
    if len(sys.argv) >= 2 and not sys.argv[1].startswith('--'):
        wallet_address = sys.argv[1]
        days_back = None
    else:
        print("\n" + "="*60)
        print("Polymarket Position Analyzer")
        print("="*60)
        wallet_address = input("\nEnter wallet address to analyze: ").strip()

        if not wallet_address:
            print("Error: Wallet address is required")
            sys.exit(1)

        # Ask for timeframe
        days_input = input("\nHow many days back to analyze? (press Enter for all data): ").strip()
        days_back = int(days_input) if days_input else None

    # Parse API key
    api_key = DEFAULT_API_KEY
    for i, arg in enumerate(sys.argv):
        if arg == '--api-key' and i + 1 < len(sys.argv):
            api_key = sys.argv[i + 1]

    print(f"\nAnalyzing positions for wallet: {wallet_address}...")
    if days_back:
        print(f"Timeframe: Last {days_back} days")
        cutoff_timestamp = int((datetime.now() - timedelta(days=days_back)).timestamp())
    else:
        print("Timeframe: All available data")
        cutoff_timestamp = None

    analyzer = PolymarketPositionAnalyzer(api_key)
    closed, open_pos = analyzer.reconstruct_positions(wallet_address)

    # Filter positions by timeframe if specified
    if cutoff_timestamp:
        original_closed_count = len(closed)
        # Filter closed positions based on exit timestamp
        closed = {
            token_id: pos for token_id, pos in closed.items()
            if pos.trades and pos.trades[-1]['timestamp'] >= cutoff_timestamp
        }
        print(f"Filtered closed positions: {len(closed)}/{original_closed_count} within timeframe")

    analyzer.export_to_csv(closed, open_pos, wallet_address)
    analyzer.generate_report(closed, open_pos)


if __name__ == '__main__':
    main()
