"""Utility functions for Whale Tracker"""

import hashlib
from typing import List, Dict

# Re-export from submodules
from utils.logger import setup_logger, log_to_ui, logger
from utils.validators import validate_contract_address

def calculate_perp_bias(long_value: float, short_value: float) -> str:
    """Calculate perp bias based on long/short ratio"""
    total = long_value + short_value
    if total == 0:
        return "Neutral"

    long_ratio = long_value / total

    if long_ratio >= 0.8:
        return "Extremely Bullish"
    elif long_ratio >= 0.6:
        return "Bullish"
    elif long_ratio <= 0.2:
        return "Extremely Bearish"
    elif long_ratio <= 0.4:
        return "Bearish"
    return "Neutral"

def calculate_size_cohort(equity: float) -> str:
    """Calculate size cohort based on equity"""
    if equity >= 50_000_000:
        return "🦑 Kraken"
    elif equity >= 10_000_000:
        return "🐋 Whale"
    elif equity >= 1_000_000:
        return "🦈 Shark"
    return "🐟 Fish"

def calculate_weighted_leverage(positions: List[Dict]) -> float:
    """Calculate weighted average leverage"""
    if not positions:
        return 0

    total_notional = sum(abs(p['notional']) for p in positions)
    if total_notional == 0:
        return 0

    weighted_sum = sum(p['leverage'] * abs(p['notional']) for p in positions)
    return weighted_sum / total_notional

def format_currency(value: float, compact: bool = False) -> str:
    """Format number as currency"""
    if compact:
        if abs(value) >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"${value / 1_000:.2f}K"
    return f"${value:,.2f}"

def truncate_address(address: str, chars: int = 4) -> str:
    """Truncate Ethereum address"""
    if not address:
        return ""
    return f"{address[:chars+2]}...{address[-chars:]}"

def seeded_random(seed: str) -> callable:
    """Generate deterministic random based on seed"""
    hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)

    def random():
        nonlocal hash_val
        hash_val = (hash_val * 1103515245 + 12345) & 0x7fffffff
        return hash_val / 0x7fffffff

    return random

__all__ = [
    'calculate_perp_bias',
    'calculate_size_cohort',
    'calculate_weighted_leverage',
    'format_currency',
    'truncate_address',
    'seeded_random',
    'setup_logger',
    'log_to_ui',
    'logger',
    'validate_contract_address',
]
