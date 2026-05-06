"""
Polymarket Leaderboard Fetcher
Fetches trader rankings from Polymarket's official leaderboard API
"""
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LeaderboardFetcher:
    """Fetches trader rankings from Polymarket's official leaderboard API"""

    BASE_URL = "https://data-api.polymarket.com"
    LEADERBOARD_ENDPOINT = f"{BASE_URL}/v1/leaderboard"

    # Available categories
    CATEGORIES = [
        'OVERALL', 'POLITICS', 'SPORTS', 'CRYPTO', 'CULTURE',
        'MENTIONS', 'WEATHER', 'ECONOMICS', 'TECH', 'FINANCE'
    ]

    # Available time periods
    TIME_PERIODS = ['DAY', 'WEEK', 'MONTH', 'ALL']

    def __init__(self):
        self.session = requests.Session()

    def get_leaderboard(
        self,
        category: str = 'OVERALL',
        time_period: str = 'DAY',
        order_by: str = 'PNL',
        limit: int = 50,
        offset: int = 0
    ) -> Optional[List[Dict]]:
        """
        Fetch trader leaderboard from Polymarket's official API

        Args:
            category: Market category (OVERALL, POLITICS, SPORTS, etc.)
            time_period: Time range (DAY, WEEK, MONTH, ALL)
            order_by: Ranking metric (PNL or VOL)
            limit: Number of traders to fetch (1-50)
            offset: Pagination offset (0-1000)

        Returns:
            List of trader ranking dictionaries with fields:
            - rank: Position in leaderboard
            - proxyWallet: Trader's Ethereum address
            - userName: Display name
            - vol: Trading volume
            - pnl: Profit/loss
            - profileImage: Avatar URL
            - xUsername: Twitter handle
            - verifiedBadge: Verification status
        """
        try:
            params = {
                'category': category.upper(),
                'timePeriod': time_period.upper(),
                'orderBy': order_by.upper(),
                'limit': min(max(limit, 1), 50),
                'offset': min(max(offset, 0), 1000)
            }

            logger.info(f"Fetching leaderboard: {category}/{time_period} (limit={limit})")

            response = self.session.get(
                self.LEADERBOARD_ENDPOINT,
                params=params,
                timeout=15
            )

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                logger.info(f"Fetched {len(data)} traders from leaderboard")
                return data
            else:
                logger.warning(f"Unexpected response format: {type(data)}")
                return []

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching leaderboard: {e.response.status_code} - {e.response.text}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching leaderboard: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching leaderboard: {e}")
            return []

    def get_top_traders_multi_category(
        self,
        time_period: str = 'DAY',
        limit_per_category: int = 50
    ) -> Dict[str, List[Dict]]:
        """
        Fetch top traders across multiple categories

        Args:
            time_period: Time range to query
            limit_per_category: Number of traders per category

        Returns:
            Dictionary mapping category names to trader lists
        """
        results = {}

        for category in self.CATEGORIES:
            traders = self.get_leaderboard(
                category=category,
                time_period=time_period,
                limit=limit_per_category
            )

            if traders:
                results[category] = traders

        logger.info(f"Fetched traders from {len(results)} categories")
        return results

    def get_all_unique_traders(
        self,
        time_period: str = 'DAY',
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get unique traders across multiple categories (for auto-discovery)

        Args:
            time_period: Time range to query
            categories: List of categories to search (defaults to key categories)

        Returns:
            Deduplicated list of trader wallet addresses with metadata
        """
        if categories is None:
            # Focus on high-activity categories
            categories = ['OVERALL', 'POLITICS', 'SPORTS', 'CRYPTO']

        seen_addresses = set()
        unique_traders = []

        for category in categories:
            traders = self.get_leaderboard(
                category=category,
                time_period=time_period,
                limit=50
            )

            for trader in traders:
                address = trader.get('proxyWallet', '').lower()

                if address and address not in seen_addresses:
                    seen_addresses.add(address)
                    unique_traders.append({
                        'address': address,
                        'userName': trader.get('userName'),
                        'pnl': trader.get('pnl', 0),
                        'vol': trader.get('vol', 0),
                        'rank': trader.get('rank'),
                        'category': category,
                        'verifiedBadge': trader.get('verifiedBadge', False)
                    })

        # Sort by PnL descending
        unique_traders.sort(key=lambda x: x.get('pnl', 0), reverse=True)

        logger.info(f"Found {len(unique_traders)} unique traders across {len(categories)} categories")
        return unique_traders

    def get_trader_stats(self, wallet_address: str) -> Optional[Dict]:
        """
        Get specific trader's stats from leaderboard

        Args:
            wallet_address: Ethereum address (0x-prefixed)

        Returns:
            Trader stats if found in leaderboard
        """
        try:
            params = {
                'user': wallet_address.lower()
            }

            response = self.session.get(
                self.LEADERBOARD_ENDPOINT,
                params=params,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                return data[0]
            else:
                logger.info(f"Trader {wallet_address[:10]}... not found in leaderboard")
                return None

        except Exception as e:
            logger.error(f"Error fetching trader stats: {e}")
            return None

    def get_top_markets(self, limit: int = 5) -> List[Dict]:
        """
        Get top markets by volume from Polymarket

        Args:
            limit: Number of markets to fetch

        Returns:
            List of top markets with volume data
        """
        try:
            # Polymarket markets endpoint
            markets_url = f"{self.BASE_URL}/markets"

            params = {
                'limit': limit,
                'active': True
            }

            response = self.session.get(
                markets_url,
                params=params,
                timeout=15
            )

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                # Sort by volume and return top markets
                sorted_markets = sorted(data, key=lambda x: float(x.get('volume', 0) or 0), reverse=True)
                logger.info(f"Fetched {len(sorted_markets[:limit])} top markets")
                return sorted_markets[:limit]
            else:
                logger.warning(f"Unexpected markets response format: {type(data)}")
                return []

        except Exception as e:
            logger.error(f"Error fetching top markets: {e}")
            return []
