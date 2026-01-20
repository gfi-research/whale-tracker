import requests
import os

class DefiLlamaClient:
    """
    DefiLlama API Client
    Supports both free and pro endpoints.
    Pro endpoints require API key set in DEFILLAMA_API_KEY environment variable.
    """

    def __init__(self, api_key=None):
        # Try to get API key from parameter, env, or config
        self.api_key = api_key or os.getenv('DEFILLAMA_API_KEY')

        # Base URLs
        self.base_url = "https://api.llama.fi"
        self.coins_url = "https://coins.llama.fi"
        self.yields_url = "https://yields.llama.fi"
        self.stablecoins_url = "https://stablecoins.llama.fi"
        self.pro_url = "https://pro-api.llama.fi"

        self.timeout = 30

    def _get(self, url, params=None):
        """Make GET request with error handling"""
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _pro_url(self, path):
        """Build pro API URL with API key"""
        if self.api_key:
            return f"{self.pro_url}/{self.api_key}{path}"
        raise ValueError("API key required for pro endpoints")

    # ========================
    # TVL Endpoints (Free)
    # ========================

    def get_all_protocols(self):
        """List all protocols with TVL"""
        return self._get(f"{self.base_url}/protocols")

    def get_protocol(self, protocol: str):
        """Get historical TVL of a protocol
        Args:
            protocol: Protocol slug (e.g., "aave", "uniswap")
        """
        return self._get(f"{self.base_url}/protocol/{protocol}")

    def get_historical_chain_tvl_all(self):
        """Get historical TVL of all chains"""
        return self._get(f"{self.base_url}/v2/historicalChainTvl")

    def get_historical_chain_tvl(self, chain: str):
        """Get historical TVL of a specific chain
        Args:
            chain: Chain name (e.g., "Ethereum", "Solana")
        """
        return self._get(f"{self.base_url}/v2/historicalChainTvl/{chain}")

    def get_current_tvl(self, protocol: str):
        """Get current TVL of a protocol (returns number only)
        Args:
            protocol: Protocol slug
        """
        return self._get(f"{self.base_url}/tvl/{protocol}")

    def get_all_chains(self):
        """Get current TVL of all chains"""
        return self._get(f"{self.base_url}/v2/chains")

    # ========================
    # TVL Endpoints (Pro)
    # ========================

    def get_token_protocols(self, symbol: str):
        """Get token usage across protocols (Pro)
        Args:
            symbol: Token symbol (e.g., "usdt")
        """
        return self._get(self._pro_url(f"/api/tokenProtocols/{symbol}"))

    def get_inflows(self, protocol: str, timestamp: int):
        """Get inflows/outflows at specific date (Pro)
        Note: This endpoint may not be available in all Pro plans
        Args:
            protocol: Protocol slug
            timestamp: Unix timestamp
        """
        return self._get(self._pro_url(f"/api/inflows/{protocol}/{timestamp}"))

    def get_chain_assets(self):
        """Get assets of all chains (Pro)"""
        return self._get(self._pro_url("/api/chainAssets"))

    # ========================
    # Coins/Prices Endpoints (Free)
    # ========================

    def get_current_prices(self, coins: list):
        """Get current prices for multiple coins
        Args:
            coins: List of coins in format ["coingecko:ethereum", "ethereum:0x..."]
        """
        coins_str = ",".join(coins)
        return self._get(f"{self.coins_url}/prices/current/{coins_str}")

    def get_historical_prices(self, coins: list, timestamp: int):
        """Get historical prices at specific timestamp
        Args:
            coins: List of coins
            timestamp: Unix timestamp
        """
        coins_str = ",".join(coins)
        return self._get(f"{self.coins_url}/prices/historical/{timestamp}/{coins_str}")

    def get_batch_historical(self, coins: list, timestamp: int, search_width: int = None):
        """Get batch historical prices
        Args:
            coins: List of coins
            timestamp: Unix timestamp
            search_width: Search width in seconds
        """
        coins_str = ",".join(coins)
        params = {"coins": coins_str, "timestamp": timestamp}
        if search_width:
            params["searchWidth"] = search_width
        return self._get(f"{self.coins_url}/batchHistorical", params=params)

    def get_price_chart(self, coins: list, start: int = None, end: int = None, span: int = None, period: str = None):
        """Get price chart data
        Args:
            coins: List of coins (e.g., ["ethereum:0x...", "coingecko:bitcoin"])
            start: Start timestamp
            end: End timestamp
            span: Number of data points
            period: Period string (e.g., "1d", "7d", "1y")
        """
        if isinstance(coins, list):
            coins_str = ",".join(coins)
        else:
            coins_str = coins
        params = {}
        if start: params["start"] = start
        if end: params["end"] = end
        if span: params["span"] = span
        if period: params["period"] = period
        return self._get(f"{self.coins_url}/chart/{coins_str}", params=params)

    def get_price_percentage_change(self, coins: list, timestamp: int = None, look_forward: bool = None, period: str = None):
        """Get price percentage change
        Args:
            coins: List of coins
            timestamp: Reference timestamp
            look_forward: Look forward from timestamp
            period: Period for calculation
        """
        if isinstance(coins, list):
            coins_str = ",".join(coins)
        else:
            coins_str = coins
        params = {}
        if timestamp: params["timestamp"] = timestamp
        if look_forward is not None: params["lookForward"] = str(look_forward).lower()
        if period: params["period"] = period
        return self._get(f"{self.coins_url}/percentage/{coins_str}", params=params)

    def get_first_price(self, coins: list):
        """Get first recorded price for coins
        Args:
            coins: List of coins
        """
        coins_str = ",".join(coins)
        return self._get(f"{self.coins_url}/prices/first/{coins_str}")

    def get_block_at_timestamp(self, chain: str, timestamp: int):
        """Get block number at timestamp
        Args:
            chain: Chain name (e.g., "ethereum")
            timestamp: Unix timestamp
        """
        return self._get(f"{self.coins_url}/block/{chain}/{timestamp}")

    # ========================
    # Stablecoins Endpoints (Free)
    # ========================

    def get_stablecoins(self, include_prices: bool = True):
        """Get list of all stablecoins
        Args:
            include_prices: Include current prices
        """
        params = {"includePrices": str(include_prices).lower()}
        return self._get(f"{self.stablecoins_url}/stablecoins", params=params)

    def get_stablecoin_charts_all(self, stablecoin: int = None):
        """Get historical mcap of all stablecoins
        Args:
            stablecoin: Stablecoin ID to filter
        """
        params = {}
        if stablecoin: params["stablecoin"] = stablecoin
        return self._get(f"{self.stablecoins_url}/stablecoincharts/all", params=params)

    def get_stablecoin_charts_chain(self, chain: str, stablecoin: int = None):
        """Get historical mcap of stablecoins on a chain
        Args:
            chain: Chain name
            stablecoin: Stablecoin ID to filter
        """
        params = {}
        if stablecoin: params["stablecoin"] = stablecoin
        return self._get(f"{self.stablecoins_url}/stablecoincharts/{chain}", params=params)

    def get_stablecoin(self, asset_id: int):
        """Get stablecoin details
        Args:
            asset_id: Stablecoin ID
        """
        return self._get(f"{self.stablecoins_url}/stablecoin/{asset_id}")

    def get_stablecoin_chains(self):
        """Get all chains with stablecoin data"""
        return self._get(f"{self.stablecoins_url}/stablecoinchains")

    def get_stablecoin_prices(self):
        """Get current stablecoin prices"""
        return self._get(f"{self.stablecoins_url}/stablecoinprices")

    # ========================
    # Stablecoins Endpoints (Pro)
    # ========================

    def get_stablecoin_dominance(self, chain: str):
        """Get stablecoin dominance on a chain (Pro)
        Args:
            chain: Chain name
        """
        return self._get(self._pro_url(f"/stablecoins/stablecoindominance/{chain}"))

    # ========================
    # Yields Endpoints (Free)
    # ========================

    def get_yield_pools(self):
        """Get all yield pools"""
        return self._get(f"{self.yields_url}/pools")

    def get_pool_chart(self, pool_id: str):
        """Get pool APY history
        Args:
            pool_id: Pool UUID
        """
        return self._get(f"{self.yields_url}/chart/{pool_id}")

    # ========================
    # Yields Endpoints (Pro)
    # ========================

    def get_pools_old(self):
        """Get legacy pools format (Pro)"""
        return self._get(self._pro_url("/yields/poolsOld"))

    def get_pools_borrow(self):
        """Get borrow pools (Pro)"""
        return self._get(self._pro_url("/yields/poolsBorrow"))

    def get_lend_borrow_chart(self, pool_id: str):
        """Get lend/borrow chart for a pool (Pro)
        Args:
            pool_id: Pool UUID
        """
        return self._get(self._pro_url(f"/yields/chartLendBorrow/{pool_id}"))

    def get_perp_yields(self):
        """Get perp funding rates (Pro)"""
        return self._get(self._pro_url("/yields/perps"))

    def get_lsd_rates(self):
        """Get LSD rates (Pro)"""
        return self._get(self._pro_url("/yields/lsdRates"))

    # ========================
    # Volumes (DEX) Endpoints (Free)
    # ========================

    def get_dex_overview(self, exclude_chart: bool = None, exclude_breakdown: bool = None, data_type: str = None):
        """Get DEX volumes overview
        Args:
            exclude_chart: Exclude total data chart
            exclude_breakdown: Exclude chart breakdown
            data_type: Data type filter
        """
        params = {}
        if exclude_chart is not None: params["excludeTotalDataChart"] = str(exclude_chart).lower()
        if exclude_breakdown is not None: params["excludeTotalDataChartBreakdown"] = str(exclude_breakdown).lower()
        if data_type: params["dataType"] = data_type
        return self._get(f"{self.base_url}/overview/dexs", params=params)

    def get_dex_overview_chain(self, chain: str, exclude_chart: bool = None, exclude_breakdown: bool = None, data_type: str = None):
        """Get DEX volumes on specific chain
        Args:
            chain: Chain name
        """
        params = {}
        if exclude_chart is not None: params["excludeTotalDataChart"] = str(exclude_chart).lower()
        if exclude_breakdown is not None: params["excludeTotalDataChartBreakdown"] = str(exclude_breakdown).lower()
        if data_type: params["dataType"] = data_type
        return self._get(f"{self.base_url}/overview/dexs/{chain}", params=params)

    def get_dex_summary(self, protocol: str, data_type: str = None):
        """Get DEX protocol summary
        Args:
            protocol: Protocol name (e.g., "uniswap")
            data_type: Data type filter
        """
        params = {}
        if data_type: params["dataType"] = data_type
        return self._get(f"{self.base_url}/summary/dexs/{protocol}", params=params)

    def get_options_overview(self, exclude_chart: bool = None, exclude_breakdown: bool = None, data_type: str = None):
        """Get options volumes overview"""
        params = {}
        if exclude_chart is not None: params["excludeTotalDataChart"] = str(exclude_chart).lower()
        if exclude_breakdown is not None: params["excludeTotalDataChartBreakdown"] = str(exclude_breakdown).lower()
        if data_type: params["dataType"] = data_type
        return self._get(f"{self.base_url}/overview/options", params=params)

    def get_options_overview_chain(self, chain: str):
        """Get options volumes on specific chain
        Args:
            chain: Chain name
        """
        return self._get(f"{self.base_url}/overview/options/{chain}")

    def get_options_summary(self, protocol: str):
        """Get options protocol summary
        Args:
            protocol: Protocol name
        """
        return self._get(f"{self.base_url}/summary/options/{protocol}")

    # ========================
    # Fees & Revenue Endpoints (Free)
    # ========================

    def get_fees_overview(self, exclude_chart: bool = None, exclude_breakdown: bool = None, data_type: str = None):
        """Get fees overview"""
        params = {}
        if exclude_chart is not None: params["excludeTotalDataChart"] = str(exclude_chart).lower()
        if exclude_breakdown is not None: params["excludeTotalDataChartBreakdown"] = str(exclude_breakdown).lower()
        if data_type: params["dataType"] = data_type
        return self._get(f"{self.base_url}/overview/fees", params=params)

    def get_fees_overview_chain(self, chain: str):
        """Get fees on specific chain
        Args:
            chain: Chain name
        """
        return self._get(f"{self.base_url}/overview/fees/{chain}")

    def get_fees_summary(self, protocol: str):
        """Get protocol fees summary
        Args:
            protocol: Protocol name
        """
        return self._get(f"{self.base_url}/summary/fees/{protocol}")

    # ========================
    # Perps Endpoints (Free)
    # ========================

    def get_open_interest(self):
        """Get open interest overview"""
        return self._get(f"{self.base_url}/overview/open-interest")

    # ========================
    # Perps Endpoints (Pro)
    # ========================

    def get_derivatives_overview(self):
        """Get derivatives overview (Pro)"""
        return self._get(self._pro_url("/api/overview/derivatives"))

    def get_derivatives_summary(self, protocol: str):
        """Get derivatives protocol summary (Pro)
        Args:
            protocol: Protocol name
        """
        return self._get(self._pro_url(f"/api/summary/derivatives/{protocol}"))

    # ========================
    # Bridges Endpoints (uses bridges.llama.fi)
    # ========================

    def get_bridges(self, include_chains: bool = None):
        """Get all bridges
        Args:
            include_chains: Include chain breakdown
        """
        params = {}
        if include_chains is not None:
            params["includeChains"] = str(include_chains).lower()
        return self._get("https://bridges.llama.fi/bridges", params=params)

    def get_bridge(self, bridge_id: int):
        """Get bridge details
        Args:
            bridge_id: Bridge ID
        """
        return self._get(f"https://bridges.llama.fi/bridge/{bridge_id}")

    def get_bridge_volume(self, chain: str):
        """Get bridge volume on chain
        Args:
            chain: Chain name
        """
        return self._get(f"https://bridges.llama.fi/bridgevolume/{chain}")

    def get_bridge_day_stats(self, timestamp: int, chain: str):
        """Get bridge day stats
        Args:
            timestamp: Unix timestamp
            chain: Chain name
        """
        return self._get(f"https://bridges.llama.fi/bridgedaystats/{timestamp}/{chain}")

    def get_bridge_transactions(self, bridge_id: int, start_timestamp: int = None, end_timestamp: int = None):
        """Get bridge transactions
        Args:
            bridge_id: Bridge ID
            start_timestamp: Start timestamp
            end_timestamp: End timestamp
        """
        params = {}
        if start_timestamp: params["starttimestamp"] = start_timestamp
        if end_timestamp: params["endtimestamp"] = end_timestamp
        return self._get(f"https://bridges.llama.fi/transactions/{bridge_id}", params=params)

    # ========================
    # Unlocks Endpoints (Pro)
    # ========================

    def get_emissions(self):
        """Get all token emissions (Pro)"""
        return self._get(self._pro_url("/api/emissions"))

    def get_emission(self, protocol: str):
        """Get protocol emissions (Pro)
        Args:
            protocol: Protocol name
        """
        return self._get(self._pro_url(f"/api/emission/{protocol}"))

    # ========================
    # Other Endpoints (Pro)
    # ========================

    def get_categories(self):
        """Get protocol categories (Pro)"""
        return self._get(self._pro_url("/api/categories"))

    def get_forks(self):
        """Get protocol forks (Pro)"""
        return self._get(self._pro_url("/api/forks"))

    def get_oracles(self):
        """Get oracle data (Pro)"""
        return self._get(self._pro_url("/api/oracles"))

    def get_hacks(self):
        """Get hack incidents (Pro)"""
        return self._get(self._pro_url("/api/hacks"))

    def get_raises(self):
        """Get funding raises (Pro)"""
        return self._get(self._pro_url("/api/raises"))

    def get_treasuries(self):
        """Get protocol treasuries (Pro)"""
        return self._get(self._pro_url("/api/treasuries"))

    def get_entities(self):
        """Get entities data (Pro)"""
        return self._get(self._pro_url("/api/entities"))

    def get_historical_liquidity(self, token: str):
        """Get token liquidity history (Pro)
        Args:
            token: Token identifier
        """
        return self._get(self._pro_url(f"/api/historicalLiquidity/{token}"))

    def get_etf_snapshot(self):
        """Get ETF snapshot (Pro)"""
        return self._get(self._pro_url("/etfs/snapshot"))

    def get_etf_flows(self):
        """Get ETF flows (Pro)"""
        return self._get(self._pro_url("/etfs/flows"))

    def get_fdv_performance(self, period: str = "7d"):
        """Get FDV performance (Pro)
        Args:
            period: Period - 1d, 7d, 30d, 90d, 180d, 365d
        """
        return self._get(self._pro_url(f"/api/fdv/performance/{period}"))

    def get_api_usage(self):
        """Get API usage stats (Pro)"""
        return self._get(self._pro_url("/usage/APIKEY"))
