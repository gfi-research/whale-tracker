"""
CoinGecko data fetcher - handles all CoinGecko API endpoints.
"""

from services.base_fetcher import BaseFetcher
from api_clients.coingecko_client import CoinGeckoClient


class CoinGeckoFetcher(BaseFetcher):
    """Fetcher for CoinGecko API endpoints."""

    SOURCE = "coingecko"

    def __init__(self, chain_name: str, contract_address: str, user_id: str,
                 chain_config: dict, cg_days: str, log_callback=None):
        super().__init__(chain_name, contract_address, user_id, chain_config, log_callback)
        self.client = CoinGeckoClient()
        self.cg_chain = chain_config.get('coingecko')
        self.cg_days = cg_days
        self.token_symbol = None
        self.coin_id = None

    def fetch_all(self):
        """Fetch all CoinGecko endpoints."""
        self.log("=" * 40, "info")
        self.log("COINGECKO ENDPOINTS", "info")
        self.log("=" * 40, "info")

        # Get coin info first (needed for other endpoints)
        self._fetch_coin_info()
        self._fetch_price_endpoints()
        self._fetch_coins_endpoints()
        self._fetch_contract_endpoints()
        self._fetch_category_endpoints()
        self._fetch_exchange_endpoints()
        self._fetch_derivatives_endpoints()
        self._fetch_general_endpoints()
        self._fetch_onchain_endpoints()

        return self.token_symbol, self.coin_id

    def _fetch_coin_info(self):
        """Fetch coin info by contract to get coin_id and symbol."""
        try:
            coin_info = self.client.get_coin_info_by_contract(self.cg_chain, self.contract_address)
            self.save(coin_info, self.SOURCE, 'coin_info')
            self.update_status("coin_info", True)
            self.token_symbol = coin_info.get('symbol', '').upper()
            self.coin_id = coin_info.get('id')
            self.log(f"Coin Info: {self.token_symbol} (ID: {self.coin_id})", "success")
        except Exception as e:
            self.log(f"Coin Info error: {str(e)[:50]}", "error")
            self.update_status("coin_info", False)

    def _fetch_price_endpoints(self):
        """Fetch simple/price endpoints."""
        # Simple Price (requires coin_id)
        try:
            if self.coin_id:
                data = self.client.get_simple_price([self.coin_id])
                self.save(data, self.SOURCE, 'simple_price')
                self.update_status("simple_price", True)
                self.log("Simple Price fetched", "success")
        except Exception as e:
            self.update_status("simple_price", False)

        # Token Price by Contract
        try:
            data = self.client.get_simple_token_price(self.cg_chain, self.contract_address)
            self.save(data, self.SOURCE, 'simple_token_price')
            self.update_status("simple_token_price", True)
            self.log("Token Price by Contract fetched", "success")
        except Exception as e:
            self.update_status("simple_token_price", False)

    def _fetch_coins_endpoints(self):
        """Fetch coins-related endpoints."""
        # Coins List
        try:
            data = self.client.get_coins_list()
            self.save(data, self.SOURCE, 'coins_list')
            self.update_status("coins_list", True)
            self.log(f"Coins List: {len(data)} coins", "success")
        except Exception as e:
            self.update_status("coins_list", False)

        # Coins Markets
        try:
            data = self.client.get_coins_markets(per_page=100)
            self.save(data, self.SOURCE, 'coins_markets')
            self.update_status("coins_markets", True)
            self.log("Coins Markets fetched", "success")
        except Exception as e:
            self.update_status("coins_markets", False)

        # Coin-specific endpoints (require coin_id)
        if self.coin_id:
            # Coin Data
            try:
                data = self.client.get_coin_data(self.coin_id)
                self.save(data, self.SOURCE, 'coin_data')
                self.update_status("coin_data", True)
                self.log("Coin Data by ID fetched", "success")
            except Exception as e:
                self.update_status("coin_data", False)

            # Coin Tickers
            try:
                data = self.client.get_coin_tickers(self.coin_id)
                self.save(data, self.SOURCE, 'coin_tickers')
                self.update_status("coin_tickers", True)
                self.log("Coin Tickers fetched", "success")
            except Exception as e:
                self.update_status("coin_tickers", False)

            # Coin Market Chart
            try:
                data = self.client.get_coin_market_chart(self.coin_id, days=self.cg_days)
                self.save(data, self.SOURCE, 'coin_market_chart')
                self.update_status("coin_market_chart", True)
                self.log("Coin Market Chart fetched", "success")
            except Exception as e:
                self.update_status("coin_market_chart", False)

            # Coin OHLC
            try:
                data = self.client.get_coin_ohlc(self.coin_id, days=30)
                self.save(data, self.SOURCE, 'coin_ohlc')
                self.update_status("coin_ohlc", True)
                self.log("Coin OHLC fetched", "success")
            except Exception as e:
                self.update_status("coin_ohlc", False)
        else:
            for k in ["coin_data", "coin_tickers", "coin_market_chart", "coin_ohlc"]:
                self.skip_status(k)

    def _fetch_contract_endpoints(self):
        """Fetch contract-based endpoints."""
        try:
            data = self.client.get_coin_historical_chart_by_contract(
                self.cg_chain, self.contract_address, days=self.cg_days)
            self.save(data, self.SOURCE, 'historical_chart')
            self.update_status("historical_chart", True)
            self.log("Chart by Contract fetched", "success")
        except Exception as e:
            self.update_status("historical_chart", False)

    def _fetch_category_endpoints(self):
        """Fetch category-related endpoints."""
        try:
            data = self.client.get_categories_list()
            self.save(data, self.SOURCE, 'categories_list')
            self.update_status("categories_list", True)
            self.log("Categories List fetched", "success")
        except Exception as e:
            self.update_status("categories_list", False)

        try:
            data = self.client.get_categories()
            self.save(data, self.SOURCE, 'categories')
            self.update_status("categories", True)
            self.log("Categories fetched", "success")
        except Exception as e:
            self.update_status("categories", False)

    def _fetch_exchange_endpoints(self):
        """Fetch exchange-related endpoints."""
        try:
            data = self.client.get_exchanges(per_page=50)
            self.save(data, self.SOURCE, 'exchanges')
            self.update_status("exchanges", True)
            self.log("Exchanges fetched", "success")
        except Exception as e:
            self.update_status("exchanges", False)

        try:
            data = self.client.get_exchanges_list()
            self.save(data, self.SOURCE, 'exchanges_list')
            self.update_status("exchanges_list", True)
            self.log("Exchanges List fetched", "success")
        except Exception as e:
            self.update_status("exchanges_list", False)

    def _fetch_derivatives_endpoints(self):
        """Fetch derivatives-related endpoints."""
        try:
            data = self.client.get_derivatives()
            self.save(data, self.SOURCE, 'derivatives')
            self.update_status("derivatives", True)
            self.log("Derivatives fetched", "success")
        except Exception as e:
            self.update_status("derivatives", False)

        try:
            data = self.client.get_derivatives_exchanges()
            self.save(data, self.SOURCE, 'derivatives_exchanges')
            self.update_status("derivatives_exchanges", True)
            self.log("Derivatives Exchanges fetched", "success")
        except Exception as e:
            self.update_status("derivatives_exchanges", False)

    def _fetch_general_endpoints(self):
        """Fetch general CoinGecko endpoints."""
        # Asset Platforms
        try:
            data = self.client.get_asset_platforms()
            self.save(data, self.SOURCE, 'asset_platforms')
            self.update_status("asset_platforms", True)
            self.log("Asset Platforms fetched", "success")
        except Exception as e:
            self.update_status("asset_platforms", False)

        # Exchange Rates
        try:
            data = self.client.get_exchange_rates()
            self.save(data, self.SOURCE, 'exchange_rates')
            self.update_status("exchange_rates", True)
            self.log("Exchange Rates fetched", "success")
        except Exception as e:
            self.update_status("exchange_rates", False)

        # Search (requires token_symbol)
        if self.token_symbol:
            try:
                data = self.client.search(self.token_symbol)
                self.save(data, self.SOURCE, 'search')
                self.update_status("search", True)
                self.log(f"Search for {self.token_symbol} done", "success")
            except Exception as e:
                self.update_status("search", False)
        else:
            self.skip_status("search")

        # Trending
        try:
            data = self.client.get_trending()
            self.save(data, self.SOURCE, 'trending')
            self.update_status("trending", True)
            self.log("Trending fetched", "success")
        except Exception as e:
            self.update_status("trending", False)

        # Global
        try:
            data = self.client.get_global()
            self.save(data, self.SOURCE, 'global')
            self.update_status("global", True)
            self.log("Global data fetched", "success")
        except Exception as e:
            self.update_status("global", False)

        # Global DeFi
        try:
            data = self.client.get_global_defi()
            self.save(data, self.SOURCE, 'global_defi')
            self.update_status("global_defi", True)
            self.log("Global DeFi fetched", "success")
        except Exception as e:
            self.update_status("global_defi", False)

    def _fetch_onchain_endpoints(self):
        """Fetch onchain DEX endpoints."""
        # Onchain Networks
        try:
            data = self.client.get_onchain_networks()
            self.save(data, self.SOURCE, 'onchain_networks')
            self.update_status("onchain_networks", True)
            self.log("Onchain Networks fetched", "success")
        except Exception as e:
            self.update_status("onchain_networks", False)

        # Onchain Token
        try:
            data = self.client.get_onchain_token(self.cg_chain, self.contract_address)
            self.save(data, self.SOURCE, 'onchain_token')
            self.update_status("onchain_token", True)
            self.log("Onchain Token fetched", "success")
        except Exception as e:
            self.update_status("onchain_token", False)

        # Onchain Token Pools
        try:
            data = self.client.get_onchain_token_pools(self.cg_chain, self.contract_address)
            self.save(data, self.SOURCE, 'onchain_token_pools')
            self.update_status("onchain_token_pools", True)
            self.log("Onchain Token Pools fetched", "success")
        except Exception as e:
            self.update_status("onchain_token_pools", False)

        # Onchain Trending Pools
        try:
            data = self.client.get_onchain_trending_pools()
            self.save(data, self.SOURCE, 'onchain_trending_pools')
            self.update_status("onchain_trending_pools", True)
            self.log("Onchain Trending Pools fetched", "success")
        except Exception as e:
            self.update_status("onchain_trending_pools", False)

        # Onchain New Pools
        try:
            data = self.client.get_onchain_new_pools()
            self.save(data, self.SOURCE, 'onchain_new_pools')
            self.update_status("onchain_new_pools", True)
            self.log("Onchain New Pools fetched", "success")
        except Exception as e:
            self.update_status("onchain_new_pools", False)
