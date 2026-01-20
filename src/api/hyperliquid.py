"""Hyperliquid API client for fetching portfolio data."""

import requests
import time as time_module
import threading
from typing import Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta


# Global rate limiter shared across all HyperliquidClient instances
class GlobalRateLimiter:
    """Thread-safe global rate limiter for Hyperliquid API."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.calls_per_second = 4  # Conservative: 4 req/sec
                    cls._instance.min_interval = 1.0 / cls._instance.calls_per_second
                    cls._instance.last_call = 0
                    cls._instance.call_lock = threading.Lock()
        return cls._instance

    def wait(self):
        """Wait if necessary to respect rate limit."""
        with self.call_lock:
            now = time_module.time()
            elapsed = now - self.last_call
            if elapsed < self.min_interval:
                time_module.sleep(self.min_interval - elapsed)
            self.last_call = time_module.time()


# Singleton instance
_global_rate_limiter = GlobalRateLimiter()


@dataclass
class PortfolioMetrics:
    """Portfolio metrics for a specific time period."""
    account_value: float
    pnl: float
    volume: float


@dataclass
class PortfolioBreakdown:
    """Breakdown of portfolio into Perp vs Spot."""
    total: PortfolioMetrics
    perp: PortfolioMetrics
    spot: PortfolioMetrics  # Calculated: total - perp


@dataclass
class TradeFill:
    """A single trade fill."""
    coin: str
    side: str  # "B" (buy) or "A" (ask/sell)
    direction: str  # "Open Long", "Open Short", "Close Long", "Close Short", etc.
    size: float
    price: float
    pnl: float
    timestamp: datetime
    fee: float


class HyperliquidClient:
    """Client for interacting with Hyperliquid Info API."""

    BASE_URL = "https://api.hyperliquid.xyz/info"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.rate_limiter = _global_rate_limiter
        self.max_retries = 5

    def _make_request(self, payload: dict) -> Optional[dict]:
        """Make API request with rate limiting and retry logic."""
        for attempt in range(self.max_retries):
            self.rate_limiter.wait()  # Global rate limiting
            try:
                response = self.session.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                if "429" in str(e):
                    # Exponential backoff on rate limit
                    wait_time = (2 ** attempt) + 1  # 3, 5, 9, 17, 33 seconds
                    time_module.sleep(wait_time)
                elif attempt == self.max_retries - 1:
                    raise
                else:
                    time_module.sleep(0.5)
        return None

    def get_portfolio(self, user_address: str) -> Optional[dict]:
        """
        Fetch user portfolio data.

        Args:
            user_address: Ethereum address (0x...)

        Returns:
            Raw portfolio response or None if error
        """
        try:
            return self._make_request({"type": "portfolio", "user": user_address})
        except requests.RequestException as e:
            print(f"Error fetching portfolio: {e}")
            return None

    def get_portfolio_breakdown(self, user_address: str, period: str = "day") -> Optional[PortfolioBreakdown]:
        """
        Get portfolio breakdown for Perp vs Spot.

        Args:
            user_address: Ethereum address
            period: Time period ("day", "week", "month", "allTime")

        Returns:
            PortfolioBreakdown with total, perp, and spot metrics
        """
        raw_data = self.get_portfolio(user_address)
        if not raw_data:
            return None

        # Convert list to dict for easier access
        portfolio_dict = {item[0]: item[1] for item in raw_data}

        # Get period data
        perp_period = f"perp{period.capitalize()}" if period != "allTime" else "perpAllTime"

        total_data = portfolio_dict.get(period, {})
        perp_data = portfolio_dict.get(perp_period, {})

        if not total_data:
            return None

        # Extract metrics
        total_metrics = self._extract_metrics(total_data)
        perp_metrics = self._extract_metrics(perp_data)

        # Calculate spot (total - perp)
        spot_metrics = PortfolioMetrics(
            account_value=max(0, total_metrics.account_value - perp_metrics.account_value),
            pnl=total_metrics.pnl - perp_metrics.pnl,
            volume=max(0, total_metrics.volume - perp_metrics.volume)
        )

        return PortfolioBreakdown(
            total=total_metrics,
            perp=perp_metrics,
            spot=spot_metrics
        )

    def _extract_metrics(self, period_data: dict) -> PortfolioMetrics:
        """Extract metrics from period data."""
        # Get latest account value from history
        account_value_history = period_data.get("accountValueHistory", [])
        account_value = float(account_value_history[-1][1]) if account_value_history else 0.0

        # Get latest PnL from history
        pnl_history = period_data.get("pnlHistory", [])
        pnl = float(pnl_history[-1][1]) if pnl_history else 0.0

        # Get volume
        volume = float(period_data.get("vlm", "0"))

        return PortfolioMetrics(
            account_value=account_value,
            pnl=pnl,
            volume=volume
        )

    def get_user_fills(self, user_address: str, limit: int = 2000) -> List[TradeFill]:
        """
        Fetch user's trade fills (trading history).

        Args:
            user_address: Ethereum address (0x...)
            limit: Max number of fills to return (max 2000)

        Returns:
            List of TradeFill objects
        """
        try:
            response = self.session.post(
                self.BASE_URL,
                json={"type": "userFills", "user": user_address}
            )
            response.raise_for_status()
            raw_fills = response.json()

            fills = []
            for fill in raw_fills[:limit]:
                try:
                    fills.append(TradeFill(
                        coin=fill.get("coin", ""),
                        side=fill.get("side", ""),
                        direction=fill.get("dir", ""),
                        size=float(fill.get("sz", 0)),
                        price=float(fill.get("px", 0)),
                        pnl=float(fill.get("closedPnl", 0)),
                        timestamp=datetime.fromtimestamp(fill.get("time", 0) / 1000),
                        fee=float(fill.get("fee", 0))
                    ))
                except (ValueError, TypeError):
                    continue

            return fills
        except requests.RequestException as e:
            print(f"Error fetching user fills: {e}")
            return []

    def get_user_fills_by_time(self, user_address: str, start_time: datetime, end_time: datetime = None) -> List[TradeFill]:
        """
        Fetch user's trade fills within a time range.

        Args:
            user_address: Ethereum address
            start_time: Start datetime
            end_time: End datetime (defaults to now)

        Returns:
            List of TradeFill objects
        """
        try:
            payload = {
                "type": "userFillsByTime",
                "user": user_address,
                "startTime": int(start_time.timestamp() * 1000)
            }
            if end_time:
                payload["endTime"] = int(end_time.timestamp() * 1000)

            response = self.session.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            raw_fills = response.json()

            fills = []
            for fill in raw_fills:
                try:
                    fills.append(TradeFill(
                        coin=fill.get("coin", ""),
                        side=fill.get("side", ""),
                        direction=fill.get("dir", ""),
                        size=float(fill.get("sz", 0)),
                        price=float(fill.get("px", 0)),
                        pnl=float(fill.get("closedPnl", 0)),
                        timestamp=datetime.fromtimestamp(fill.get("time", 0) / 1000),
                        fee=float(fill.get("fee", 0))
                    ))
                except (ValueError, TypeError):
                    continue

            return fills
        except requests.RequestException as e:
            print(f"Error fetching user fills by time: {e}")
            return []

    def get_user_fills_paginated(
        self,
        user_address: str,
        start_time: datetime,
        end_time: datetime = None,
        max_fills: int = 10000,
        on_progress: Callable[[int, int], None] = None
    ) -> List[TradeFill]:
        """
        Fetch user's trade fills with pagination to get up to 10,000 trades.

        Uses time-based pagination strategy:
        - Each request returns max 2000 fills
        - Uses last fill's timestamp - 1ms as new endTime for next request
        - Continues until no more fills or max_fills reached

        Args:
            user_address: Ethereum address
            start_time: Start datetime
            end_time: End datetime (defaults to now)
            max_fills: Maximum fills to fetch (default 10000, API hard limit)
            on_progress: Optional callback(current_count, total_estimate) for progress updates

        Returns:
            List of TradeFill objects (up to max_fills)
        """
        all_fills = []
        current_end = end_time or datetime.now()
        page = 0
        max_pages = (max_fills // 2000) + 1  # Safety limit

        while len(all_fills) < max_fills and page < max_pages:
            try:
                payload = {
                    "type": "userFillsByTime",
                    "user": user_address,
                    "startTime": int(start_time.timestamp() * 1000),
                    "endTime": int(current_end.timestamp() * 1000)
                }

                # Use _make_request for rate limiting and retry
                raw_fills = self._make_request(payload)

                if not raw_fills:
                    break  # No more data

                # Parse fills
                page_fills = []
                for fill in raw_fills:
                    try:
                        page_fills.append(TradeFill(
                            coin=fill.get("coin", ""),
                            side=fill.get("side", ""),
                            direction=fill.get("dir", ""),
                            size=float(fill.get("sz", 0)),
                            price=float(fill.get("px", 0)),
                            pnl=float(fill.get("closedPnl", 0)),
                            timestamp=datetime.fromtimestamp(fill.get("time", 0) / 1000),
                            fee=float(fill.get("fee", 0))
                        ))
                    except (ValueError, TypeError):
                        continue

                all_fills.extend(page_fills)

                # Progress callback
                if on_progress:
                    on_progress(len(all_fills), max_fills)

                # Check if we need to paginate
                if len(raw_fills) < 2000:
                    break  # Last page, no more data

                # Pagination: use oldest fill's time - 1ms as new endTime
                # Fills are returned newest first, so last item is oldest
                oldest_time_ms = raw_fills[-1].get("time", 0)
                current_end = datetime.fromtimestamp((oldest_time_ms - 1) / 1000)

                page += 1

            except Exception as e:
                print(f"Error fetching fills page {page}: {e}")
                break

        # Sort by timestamp (newest first) and remove duplicates by time
        seen_times = set()
        unique_fills = []
        for fill in sorted(all_fills, key=lambda x: x.timestamp, reverse=True):
            time_key = fill.timestamp.timestamp()
            if time_key not in seen_times:
                seen_times.add(time_key)
                unique_fills.append(fill)

        return unique_fills[:max_fills]


# Mock data for testing without real wallet
def get_mock_portfolio_breakdown() -> PortfolioBreakdown:
    """Return mock data for demonstration."""
    return PortfolioBreakdown(
        total=PortfolioMetrics(
            account_value=125000.50,
            pnl=8500.25,
            volume=1250000.00
        ),
        perp=PortfolioMetrics(
            account_value=95000.00,
            pnl=7200.00,
            volume=1100000.00
        ),
        spot=PortfolioMetrics(
            account_value=30000.50,
            pnl=1300.25,
            volume=150000.00
        )
    )
