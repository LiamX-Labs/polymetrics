"""
Polymarket Data Fetcher Service
Refactored from scripts/polymarket_api_fetcher.py
"""
import requests
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class PolymarketFetcher:
    """Fetches trading data from Polymarket's official API"""

    BASE_URL = "https://data-api.polymarket.com"

    def __init__(self):
        self.session = requests.Session()

    def get_closed_positions(self, wallet_address: str, limit: int = 50,
                           offset: int = 0, sort_by: str = "REALIZEDPNL",
                           sort_direction: str = "DESC") -> Optional[List[Dict]]:
        """
        Fetch closed positions for a user

        Args:
            wallet_address: User's wallet address
            limit: Results per page (max 50)
            offset: Pagination offset
            sort_by: REALIZEDPNL, TITLE, PRICE, AVGPRICE, or TIMESTAMP
            sort_direction: ASC or DESC
        """
        endpoint = f"{self.BASE_URL}/closed-positions"

        params = {
            'user': wallet_address,
            'limit': min(limit, 50),
            'offset': offset,
            'sortBy': sort_by,
            'sortDirection': sort_direction
        }

        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching closed positions: {e}")
            return None

    def get_all_closed_positions(self, wallet_address: str,
                                cutoff_timestamp: Optional[int] = None,
                                progress_callback=None) -> List[Dict]:
        """
        Fetch ALL closed positions with pagination

        Args:
            wallet_address: User's wallet address
            cutoff_timestamp: Optional unix timestamp - stop fetching when data is older
            progress_callback: Optional callback(current, total, message) to report progress
        """
        all_positions = []
        offset = 0
        limit = 50

        sort_by = "TIMESTAMP" if cutoff_timestamp else "REALIZEDPNL"

        logger.info(f"Fetching closed positions for {wallet_address[:10]}...")

        # Report initial progress
        if progress_callback:
            progress_callback(0, None, "Fetching first batch of positions...")

        while True:
            positions = self.get_closed_positions(
                wallet_address,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_direction="DESC"
            )

            if not positions or len(positions) == 0:
                break

            # If cutoff timestamp specified, filter
            if cutoff_timestamp:
                filtered_positions = [p for p in positions if p.get('timestamp', 0) >= cutoff_timestamp]
                all_positions.extend(filtered_positions)

                if len(filtered_positions) < len(positions):
                    logger.info(f"Reached cutoff date - stopping fetch")
                    break
            else:
                all_positions.extend(positions)

            # Report progress
            if progress_callback:
                # Estimate total (positions come in batches of 50)
                estimated_total = len(all_positions) + (limit if len(positions) == limit else 0)
                progress_callback(
                    len(all_positions),
                    estimated_total,
                    f"Fetched {len(all_positions)} positions..."
                )

            if len(positions) < limit:
                break

            offset += limit

        logger.info(f"Total positions fetched: {len(all_positions)}")

        # Final progress update
        if progress_callback:
            progress_callback(len(all_positions), len(all_positions), "Analyzing positions...")

        return all_positions

    def get_trades(self, wallet_address: str, limit: int = 100,
                  offset: int = 0, side: Optional[str] = None,
                  taker_only: bool = True) -> Optional[List[Dict]]:
        """
        Fetch trades for a user

        Args:
            wallet_address: User's wallet address
            limit: Results per page (max 1000)
            offset: Pagination offset
            side: "BUY" or "SELL" or None for both
            taker_only: Only show taker trades
        """
        endpoint = f"{self.BASE_URL}/trades"

        params = {
            'user': wallet_address,
            'limit': min(limit, 1000),
            'offset': offset,
            'takerOnly': taker_only
        }

        if side:
            params['side'] = side

        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trades: {e}")
            return None

    def get_all_trades(self, wallet_address: str,
                      cutoff_timestamp: Optional[int] = None) -> List[Dict]:
        """
        Fetch ALL trades with pagination (up to API limit of ~4000 trades)

        Args:
            wallet_address: User's wallet address
            cutoff_timestamp: Optional unix timestamp
        """
        all_trades = []
        offset = 0
        limit = 1000
        max_offset = 3000  # API limitation

        logger.info(f"Fetching trades for {wallet_address[:10]}...")

        while offset <= max_offset:
            trades = self.get_trades(
                wallet_address,
                limit=limit,
                offset=offset
            )

            if not trades or len(trades) == 0:
                break

            # Filter by cutoff if specified
            if cutoff_timestamp:
                filtered_trades = [t for t in trades if t.get('timestamp', 0) >= cutoff_timestamp]
                all_trades.extend(filtered_trades)

                if len(filtered_trades) < len(trades):
                    logger.info(f"Reached cutoff date - stopping trade fetch")
                    break
            else:
                all_trades.extend(trades)

            if len(trades) < limit:
                break

            offset += limit

        logger.info(f"Total trades fetched: {len(all_trades)}")
        return all_trades
