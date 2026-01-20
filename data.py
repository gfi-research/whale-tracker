"""Wallet data and mock data generators"""

from typing import List, Dict
from utils import seeded_random

# Whale wallets data
WHALE_WALLETS = [
    {"address": "0xffbd3e51ae0e2c4407434e157965c064f2a11628", "label": "Trading Bot [0xffbd3e]", "entity": "retail", "account_value": 34792137.22, "roi": 0.03, "total_pnl": 767452.49},
    {"address": "0xfce053a5e461683454bf37ad66d20344c0e3f4c0", "label": "Smart HL Perps Trader", "entity": "retail", "account_value": 3879232.68, "roi": 0.02, "total_pnl": 415587.99},
    {"address": "0xfc667adba8d4837586078f4fdcdc29804337ca06", "label": "Bridge User [0xfc667a]", "entity": "retail", "account_value": 28196371.28, "roi": 0.02, "total_pnl": 1154648.28},
    {"address": "0xecb63caa47c7c4e77f60f1ce858cf28dc2b82b00", "label": "Wintermute Market Making", "entity": "MM", "account_value": 43353163.27, "roi": 0.00, "total_pnl": 5103131.64},
    {"address": "0xea6670ebdb4a388a8cfc16f6497bf4f267b061ee", "label": "Smart HL Perps Trader", "entity": "retail", "account_value": 11546661.75, "roi": 0.54, "total_pnl": 1036133.21},
    {"address": "0xcac19662ec88d23fa1c81ac0e8570b0cf2ff26b3", "label": "Galaxy Digital", "entity": "VCs", "account_value": 17181889.44, "roi": 0.18, "total_pnl": 6671819.44},
    {"address": "0x7fdafde5cfb5465924316eced2d3715494c517d1", "label": "Fasanara Capital", "entity": "VCs", "account_value": 47298990.58, "roi": 0.11, "total_pnl": 7436920.51},
    {"address": "0x621c5551678189b9a6c94d929924c225ff1d63ab", "label": "Fasanara Capital 2", "entity": "VCs", "account_value": 61814094.23, "roi": 0.10, "total_pnl": 8095502.41},
    {"address": "0xd47587702a91731dc1089b5db0932cf820151a91", "label": "Dex Trader [0xd47587]", "entity": "retail", "account_value": 53954916.83, "roi": 0.01, "total_pnl": 457468.62},
    {"address": "0x880ac484a1743862989a441d6d867238c7aa311c", "label": "High Activity Whale", "entity": "retail", "account_value": 31485024.97, "roi": 0.02, "total_pnl": 12011879.59},
    {"address": "0x856c35038594767646266bc7fd68dc26480e910d", "label": "Whale [0x856c35]", "entity": "retail", "account_value": 30821037.25, "roi": 0.02, "total_pnl": 1826981.90},
    {"address": "0x94d3735543ecb3d339064151118644501c933814", "label": "Whale [0x94d373]", "entity": "retail", "account_value": 32285798.04, "roi": 0.00, "total_pnl": 1406291.17},
    {"address": "0xb83de012dba672c76a7dbbbf3e459cb59d7d6e36", "label": "Abraxas Capital", "entity": "retail", "account_value": 20865656.14, "roi": 0.38, "total_pnl": 6717386.21},
    {"address": "0xa312114b5795dff9b8db50474dd57701aa78ad1e", "label": "Smart HL Perps Trader", "entity": "retail", "account_value": 21932601.62, "roi": 0.06, "total_pnl": 5256448.78},
    {"address": "0x8e096995c3e4a3f0bc5b3ea1cba94de2aa4d70c9", "label": "High Activity Trader", "entity": "retail", "account_value": 17806910.37, "roi": 0.06, "total_pnl": 4200591.68},
    {"address": "0xf9109ada2f73c62e9889b45453065f0d99260a2d", "label": "Whale [0xf9109a]", "entity": "retail", "account_value": 16729817.00, "roi": 0.00, "total_pnl": 358610.44},
    {"address": "0x985f02b19dbc062e565c981aac5614baf2cf501f", "label": "Whale [0x985f02]", "entity": "retail", "account_value": 14943925.14, "roi": 0.00, "total_pnl": 1062398.78},
    {"address": "0x9c89f595f5515609ad61f6fda94beff85ae6600e", "label": "Token Millionaire", "entity": "retail", "account_value": 11909720.97, "roi": 0.05, "total_pnl": 155086.18},
    {"address": "0x8ae4c5b303bc77c3aa68f2b71f37c9fa6d3b3d60", "label": "Former Smart Trader", "entity": "retail", "account_value": 11142560.66, "roi": 0.46, "total_pnl": 268215.00},
    {"address": "0x76c2164fc79492401db1890db0d17d16b9155aa0", "label": "Bridge User [0x76c216]", "entity": "retail", "account_value": 9591882.83, "roi": 0.36, "total_pnl": 3942621.86},
    {"address": "0x8cc94dc843e1ea7a19805e0cca43001123512b6a", "label": "Token Millionaire", "entity": "retail", "account_value": 7831178.15, "roi": 0.00, "total_pnl": 120637.82},
    {"address": "0xd911e53d53b663972254e086450fd6198a25961e", "label": "Whale [0xd911e5]", "entity": "retail", "account_value": 7704711.31, "roi": 0.07, "total_pnl": 357503.34},
    {"address": "0x7717a7a245d9f950e586822b8c9b46863ed7bd7e", "label": "Trading Bot", "entity": "retail", "account_value": 7434084.20, "roi": 0.00, "total_pnl": 243183.87},
    {"address": "0x5bc43f38c2ddcd85857f218674cd384f172c3b0c", "label": "High Balance", "entity": "retail", "account_value": 7346256.78, "roi": 0.01, "total_pnl": 189353.88},
    {"address": "0x8def9f50456c6c4e37fa5d3d57f108ed23992dae", "label": "Laurent Zeimes", "entity": "retail", "account_value": 7255082.42, "roi": 0.02, "total_pnl": 501607.15},
    {"address": "0xb8eb97eaed8367079894d2f1bed69bd220ec1dd5", "label": "Whale [0xb8eb97]", "entity": "retail", "account_value": 6796652.34, "roi": 0.12, "total_pnl": 229649.52},
    {"address": "0xd4c1f7e8d876c4749228d515473d36f919583d1d", "label": "Bridge User", "entity": "retail", "account_value": 6464055.99, "roi": 0.00, "total_pnl": 438780.30},
    {"address": "0x7ca165f354e3260e2f8d5a7508cc9dd2fa009235", "label": "Smart Trader", "entity": "retail", "account_value": 6016296.32, "roi": 0.06, "total_pnl": 625393.23},
    {"address": "0xc613bd93c62e62bf3e583c36ae8c4118f1fb2456", "label": "Token Millionaire", "entity": "retail", "account_value": 5865412.69, "roi": 0.03, "total_pnl": 931046.80},
    {"address": "0x720a68bf0813853cd3ed74d2fd0f54edfc7a43e1", "label": "Trading Bot", "entity": "retail", "account_value": 5482787.23, "roi": 0.05, "total_pnl": 234718.34},
]

TOKENS = ["BTC", "ETH", "SOL", "ARB", "DOGE", "AVAX", "LINK", "OP", "APT", "SUI"]

TOKEN_PRICES = {
    "BTC": 95000, "ETH": 3200, "SOL": 180, "ARB": 0.85, "DOGE": 0.32,
    "AVAX": 35, "LINK": 22, "OP": 1.8, "APT": 8.5, "SUI": 3.2,
}

def generate_mock_positions(address: str, account_value: float) -> List[Dict]:
    """Generate mock positions for a wallet"""
    random = seeded_random(address)

    num_positions = int(random() * 5) + 1
    positions = []

    for i in range(num_positions):
        token = TOKENS[int(random() * len(TOKENS))]
        direction = "long" if random() > 0.45 else "short"
        leverage = int(random() * 20) + 1
        notional_pct = (random() * 0.4 + 0.1) / num_positions
        notional = account_value * notional_pct
        base_price = TOKEN_PRICES[token]
        size = notional / base_price

        price_variance = (random() - 0.5) * 0.1
        entry_price = base_price * (1 + price_variance)
        mark_price = base_price * (1 + (random() - 0.5) * 0.05)

        price_diff = mark_price - entry_price if direction == "long" else entry_price - mark_price
        unrealized_pnl = (price_diff / entry_price) * notional

        liq_distance = 1 / leverage
        liq_price = entry_price * (1 - liq_distance) if direction == "long" else entry_price * (1 + liq_distance)

        positions.append({
            "token": token,
            "direction": direction,
            "entry_price": entry_price,
            "mark_price": mark_price,
            "size": abs(size),
            "notional": abs(notional),
            "leverage": leverage,
            "liquidation_price": liq_price,
            "margin_used": notional / leverage,
            "unrealized_pnl": unrealized_pnl,
        })

    return positions

def generate_mock_market_data() -> List[Dict]:
    """Generate mock market data"""
    market_data = []

    for token in TOKENS[:6]:  # Top 6 tokens
        long_notional = sum(
            w['account_value'] * 0.15 for w in WHALE_WALLETS
            if seeded_random(w['address'] + token)() > 0.5
        )
        short_notional = sum(
            w['account_value'] * 0.10 for w in WHALE_WALLETS
            if seeded_random(w['address'] + token)() <= 0.5
        )

        market_data.append({
            "token": token,
            "long_notional": long_notional,
            "short_notional": short_notional,
            "trader_count": int(len(WHALE_WALLETS) * 0.4),
            "unrealized_pnl_profit": long_notional * 0.02,
            "unrealized_pnl_loss": short_notional * 0.015,
        })

    return sorted(market_data, key=lambda x: x['long_notional'] + x['short_notional'], reverse=True)
