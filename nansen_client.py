"""Nansen API Client with cost tracking"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Credit costs per endpoint
ENDPOINT_COSTS = {
    "/api/v1/perp-leaderboard": 5,
    "/api/v1/profiler/perp-positions": 1,
    "/api/v1/tgm/perp-positions": 5,
    "/api/v1/tgm/perp-screener": 1,
}

@dataclass
class APIUsageTracker:
    """Track API usage and costs"""
    total_credits_used: int = 0
    calls_made: int = 0
    call_history: List[Dict] = field(default_factory=list)

    def log_call(self, endpoint: str, success: bool, response_time_ms: float):
        cost = ENDPOINT_COSTS.get(endpoint, 1)
        if success:
            self.total_credits_used += cost
        self.calls_made += 1

        call_info = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "cost": cost if success else 0,
            "success": success,
            "response_time_ms": round(response_time_ms, 2),
        }
        self.call_history.append(call_info)

        # Log to console
        status = "✓" if success else "✗"
        logger.info(f"[NANSEN API] {status} {endpoint} | Cost: {cost} credits | Time: {response_time_ms:.0f}ms | Total: {self.total_credits_used} credits")

    def get_summary(self) -> Dict:
        return {
            "total_credits_used": self.total_credits_used,
            "total_calls": self.calls_made,
            "successful_calls": len([c for c in self.call_history if c["success"]]),
            "failed_calls": len([c for c in self.call_history if not c["success"]]),
            "avg_response_time_ms": sum(c["response_time_ms"] for c in self.call_history) / max(len(self.call_history), 1),
        }

# Global tracker instance
usage_tracker = APIUsageTracker()

class NansenClient:
    """Nansen API Client"""

    BASE_URL = "https://api.nansen.ai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NANSEN_API_KEY", "")
        if not self.api_key:
            logger.warning("NANSEN_API_KEY not set - API calls will fail")

    def _make_request(self, endpoint: str, payload: Dict) -> Optional[Dict]:
        """Make POST request to Nansen API"""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json",
            "Accept": "*/*",
        }

        start_time = datetime.now()
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                usage_tracker.log_call(endpoint, True, response_time_ms)
                return response.json()
            else:
                usage_tracker.log_call(endpoint, False, response_time_ms)
                logger.error(f"API Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            usage_tracker.log_call(endpoint, False, response_time_ms)
            logger.error(f"Request failed: {e}")
            return None

    def get_perp_leaderboard(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_account_value: float = 1_000_000,
        page: int = 1,
        per_page: int = 50,
    ) -> List[Dict]:
        """
        Get perpetual trading leaderboard (top traders)
        Cost: 5 credits
        """
        # Default to last 30 days if no date specified
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        payload = {
            "date": {"from": date_from, "to": date_to},
            "pagination": {"page": page, "per_page": per_page},
            "filters": {
                "account_value": {"min": min_account_value}
            },
            "order_by": [{"field": "total_pnl", "direction": "DESC"}]
        }

        result = self._make_request("/api/v1/perp-leaderboard", payload)
        if result and "data" in result:
            return result["data"]
        return []

    def get_wallet_positions(self, address: str) -> Optional[Dict]:
        """
        Get perpetual positions for a specific wallet address
        Cost: 1 credit
        """
        payload = {
            "address": address,
            "order_by": [{"field": "position_value_usd", "direction": "DESC"}]
        }

        result = self._make_request("/api/v1/profiler/perp-positions", payload)
        if result and "data" in result:
            return result["data"]
        return None

    def get_token_positions(
        self,
        token_symbol: str,
        label_type: str = "all_traders",
        page: int = 1,
        per_page: int = 50,
        min_position_value: float = 10000,
    ) -> List[Dict]:
        """
        Get all positions for a specific token
        Cost: 5 credits
        """
        payload = {
            "token_symbol": token_symbol,
            "label_type": label_type,
            "pagination": {"page": page, "per_page": per_page},
            "filters": {
                "position_value_usd": {"min": min_position_value}
            },
            "order_by": [{"field": "position_value_usd", "direction": "DESC"}]
        }

        result = self._make_request("/api/v1/tgm/perp-positions", payload)
        if result and "data" in result:
            return result["data"]
        return []

    def get_token_positions_by_side(
        self,
        token_symbol: str,
        side: str = "Long",  # "Long" or "Short"
        min_position_value: float = 100000,
    ) -> List[Dict]:
        """
        Get positions for a token filtered by side (Long/Short)
        Cost: 5 credits
        """
        payload = {
            "token_symbol": token_symbol,
            "label_type": "all_traders",
            "pagination": {"page": 1, "per_page": 100},
            "filters": {
                "position_value_usd": {"min": min_position_value},
                "side": [side]
            },
            "order_by": [{"field": "position_value_usd", "direction": "DESC"}]
        }

        result = self._make_request("/api/v1/tgm/perp-positions", payload)
        if result and "data" in result:
            return result["data"]
        return []


def get_usage_tracker() -> APIUsageTracker:
    """Get the global usage tracker"""
    return usage_tracker


def reset_usage_tracker():
    """Reset the usage tracker"""
    global usage_tracker
    usage_tracker = APIUsageTracker()
