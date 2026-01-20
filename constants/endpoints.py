"""
Endpoint mappings for all data sources.
Format: "Display Name": ("source", "endpoint_key")
"""

ENDPOINT_MAPPING = {
    # ==================== DefiLlama ====================
    # TVL
    "DL: All Protocols TVL": ("defillama", "all_protocols"),
    "DL: Protocol TVL": ("defillama", "protocol_tvl"),
    "DL: Chain TVL": ("defillama", "chain_tvl"),
    "DL: All Chains TVL": ("defillama", "all_chains"),
    # Prices
    "DL: Current Prices": ("defillama", "current_prices"),
    "DL: Price Chart": ("defillama", "price_chart"),
    "DL: Price Change %": ("defillama", "price_percentage"),
    # Stablecoins
    "DL: Stablecoins": ("defillama", "stablecoins"),
    "DL: Stablecoin Chains": ("defillama", "stablecoin_chains"),
    # Yields
    "DL: Yield Pools": ("defillama", "yield_pools"),
    # DEX
    "DL: DEX Overview": ("defillama", "dex_overview"),
    "DL: DEX Chain Volume": ("defillama", "dex_chain_volume"),
    # Fees
    "DL: Fees Overview": ("defillama", "fees_overview"),
    "DL: Fees Chain": ("defillama", "fees_chain"),
    # Bridges
    "DL: Bridges": ("defillama", "bridges"),
    "DL: Bridge Volume": ("defillama", "bridge_volume"),
    # Other
    "DL: Open Interest": ("defillama", "open_interest"),
    "DL: Hacks": ("defillama", "hacks"),
    "DL: Raises": ("defillama", "raises"),

    # ==================== CoinGecko ====================
    # Simple/Price
    "CG: Simple Price": ("coingecko", "simple_price"),
    "CG: Token Price by Contract": ("coingecko", "simple_token_price"),
    # Coins
    "CG: Coins List": ("coingecko", "coins_list"),
    "CG: Coins Markets": ("coingecko", "coins_markets"),
    "CG: Coin Data by ID": ("coingecko", "coin_data"),
    "CG: Coin Tickers": ("coingecko", "coin_tickers"),
    "CG: Coin Market Chart": ("coingecko", "coin_market_chart"),
    "CG: Coin OHLC": ("coingecko", "coin_ohlc"),
    # Contract
    "CG: Coin Info by Contract": ("coingecko", "coin_info"),
    "CG: Chart by Contract": ("coingecko", "historical_chart"),
    # Categories
    "CG: Categories List": ("coingecko", "categories_list"),
    "CG: Categories": ("coingecko", "categories"),
    # Exchanges
    "CG: Exchanges": ("coingecko", "exchanges"),
    "CG: Exchanges List": ("coingecko", "exchanges_list"),
    # Derivatives
    "CG: Derivatives": ("coingecko", "derivatives"),
    "CG: Derivatives Exchanges": ("coingecko", "derivatives_exchanges"),
    # General
    "CG: Asset Platforms": ("coingecko", "asset_platforms"),
    "CG: Exchange Rates": ("coingecko", "exchange_rates"),
    "CG: Search": ("coingecko", "search"),
    "CG: Trending": ("coingecko", "trending"),
    "CG: Global": ("coingecko", "global"),
    "CG: Global DeFi": ("coingecko", "global_defi"),
    # Onchain DEX
    "CG: Onchain Networks": ("coingecko", "onchain_networks"),
    "CG: Onchain Token": ("coingecko", "onchain_token"),
    "CG: Onchain Token Pools": ("coingecko", "onchain_token_pools"),
    "CG: Onchain Trending Pools": ("coingecko", "onchain_trending_pools"),
    "CG: Onchain New Pools": ("coingecko", "onchain_new_pools"),

    # ==================== Nansen ====================
    # Smart Money
    "NS: Smart Money Netflow": ("nansen", "sm_netflow"),
    "NS: Smart Money Holdings": ("nansen", "sm_holdings"),
    "NS: Smart Money DEX Trades": ("nansen", "sm_dex_trades"),
    # Profiler
    "NS: Address Balance": ("nansen", "address_balance"),
    "NS: Address Transactions": ("nansen", "address_transactions"),
    "NS: Address Related Wallets": ("nansen", "address_related_wallets"),
    "NS: Address Counterparties": ("nansen", "address_counterparties"),
    "NS: Address PnL": ("nansen", "address_pnl"),
    # TGM - Token
    "NS: Token Screener": ("nansen", "token_screener"),
    "NS: Token Flows": ("nansen", "token_flows"),
    "NS: Token Flow Intelligence": ("nansen", "flow_intelligence"),
    "NS: Token Who Bought/Sold": ("nansen", "who_bought_sold"),
    "NS: Token DEX Trades": ("nansen", "token_dex_trades"),
    "NS: Token Transfers": ("nansen", "transfers"),
    "NS: Token Holders": ("nansen", "holders"),
    "NS: Token PnL Leaderboard": ("nansen", "token_pnl_leaderboard"),
    # TGM - Perp
    "NS: Perp Screener": ("nansen", "perp_screener"),
    "NS: Token Perp Trades": ("nansen", "perp_trades"),
    "NS: Token Perp Positions": ("nansen", "perp_positions"),
    "NS: Perp PnL Leaderboard": ("nansen", "perp_pnl_leaderboard"),
    # Portfolio
    "NS: DeFi Holdings": ("nansen", "defi_holdings"),
}

# Source display name mapping
SOURCE_DISPLAY_MAP = {
    "coingecko": "CoinGecko",
    "nansen": "Nansen",
    "defillama": "DefiLlama",
    "dune": "Dune"
}
