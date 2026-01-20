"""
DefiLlama data fetcher - handles all DefiLlama API endpoints.
"""

from services.base_fetcher import BaseFetcher
from api_clients.defillama_client import DefiLlamaClient


class DefiLlamaFetcher(BaseFetcher):
    """Fetcher for DefiLlama API endpoints."""

    SOURCE = "defillama"

    def __init__(self, chain_name: str, contract_address: str, user_id: str,
                 chain_config: dict, log_callback=None):
        super().__init__(chain_name, contract_address, user_id, chain_config, log_callback)
        self.client = DefiLlamaClient()
        self.dl_chain = chain_config.get('defillama', chain_name.lower())
        self.coin_identifier = f"{self.dl_chain}:{contract_address}"

    def fetch_all(self):
        """Fetch all DefiLlama endpoints."""
        self.log("=" * 40, "info")
        self.log("DEFILLAMA ENDPOINTS", "info")
        self.log("=" * 40, "info")

        self._fetch_tvl_endpoints()
        self._fetch_price_endpoints()
        self._fetch_stablecoin_endpoints()
        self._fetch_yield_endpoints()
        self._fetch_dex_endpoints()
        self._fetch_fees_endpoints()
        self._fetch_bridge_endpoints()
        self._fetch_other_endpoints()

    def _fetch_tvl_endpoints(self):
        """Fetch TVL-related endpoints."""
        # All Protocols TVL
        try:
            data = self.client.get_all_protocols()
            self.save(data, self.SOURCE, 'all_protocols')
            self.update_status("all_protocols", True)
            self.log(f"All Protocols TVL: {len(data)} protocols", "success")
        except Exception as e:
            self.update_status("all_protocols", False)
            self.log(f"All Protocols error: {str(e)[:50]}", "error")

        # Chain TVL
        try:
            data = self.client.get_historical_chain_tvl(self.dl_chain)
            self.save(data, self.SOURCE, 'chain_tvl')
            self.update_status("chain_tvl", True)
            self.log(f"Chain TVL for {self.dl_chain} fetched", "success")
        except Exception as e:
            self.update_status("chain_tvl", False)

        # All Chains
        try:
            data = self.client.get_all_chains()
            self.save(data, self.SOURCE, 'all_chains')
            self.update_status("all_chains", True)
            self.log(f"All Chains TVL: {len(data)} chains", "success")
        except Exception as e:
            self.update_status("all_chains", False)

        # Protocol TVL - skip (needs protocol name)
        self.skip_status("protocol_tvl")

    def _fetch_price_endpoints(self):
        """Fetch price-related endpoints."""
        # Current Prices
        try:
            data = self.client.get_current_prices([self.coin_identifier])
            self.save(data, self.SOURCE, 'current_prices')
            self.update_status("current_prices", True)
            self.log("Current Prices fetched", "success")
        except Exception as e:
            self.update_status("current_prices", False)

        # Price Chart
        try:
            data = self.client.get_price_chart([self.coin_identifier])
            self.save(data, self.SOURCE, 'price_chart')
            self.update_status("price_chart", True)
            self.log("Price Chart fetched", "success")
        except Exception as e:
            self.update_status("price_chart", False)

        # Price Percentage Change
        try:
            data = self.client.get_price_percentage_change([self.coin_identifier])
            self.save(data, self.SOURCE, 'price_percentage')
            self.update_status("price_percentage", True)
            self.log("Price Percentage Change fetched", "success")
        except Exception as e:
            self.update_status("price_percentage", False)

    def _fetch_stablecoin_endpoints(self):
        """Fetch stablecoin-related endpoints."""
        try:
            data = self.client.get_stablecoins()
            self.save(data, self.SOURCE, 'stablecoins')
            self.update_status("stablecoins", True)
            self.log("Stablecoins fetched", "success")
        except Exception as e:
            self.update_status("stablecoins", False)

        try:
            data = self.client.get_stablecoin_chains()
            self.save(data, self.SOURCE, 'stablecoin_chains')
            self.update_status("stablecoin_chains", True)
            self.log("Stablecoin Chains fetched", "success")
        except Exception as e:
            self.update_status("stablecoin_chains", False)

    def _fetch_yield_endpoints(self):
        """Fetch yield-related endpoints."""
        try:
            data = self.client.get_yield_pools()
            self.save(data, self.SOURCE, 'yield_pools')
            self.update_status("yield_pools", True)
            self.log("Yield Pools fetched", "success")
        except Exception as e:
            self.update_status("yield_pools", False)

    def _fetch_dex_endpoints(self):
        """Fetch DEX-related endpoints."""
        try:
            data = self.client.get_dex_overview()
            self.save(data, self.SOURCE, 'dex_overview')
            self.update_status("dex_overview", True)
            self.log("DEX Overview fetched", "success")
        except Exception as e:
            self.update_status("dex_overview", False)

        try:
            data = self.client.get_dex_overview_chain(self.dl_chain)
            self.save(data, self.SOURCE, 'dex_chain_volume')
            self.update_status("dex_chain_volume", True)
            self.log(f"DEX Chain Volume for {self.dl_chain} fetched", "success")
        except Exception as e:
            self.update_status("dex_chain_volume", False)

    def _fetch_fees_endpoints(self):
        """Fetch fees-related endpoints."""
        try:
            data = self.client.get_fees_overview()
            self.save(data, self.SOURCE, 'fees_overview')
            self.update_status("fees_overview", True)
            self.log("Fees Overview fetched", "success")
        except Exception as e:
            self.update_status("fees_overview", False)

        try:
            data = self.client.get_fees_overview_chain(self.dl_chain)
            self.save(data, self.SOURCE, 'fees_chain')
            self.update_status("fees_chain", True)
            self.log(f"Fees Chain for {self.dl_chain} fetched", "success")
        except Exception as e:
            self.update_status("fees_chain", False)

    def _fetch_bridge_endpoints(self):
        """Fetch bridge-related endpoints."""
        try:
            data = self.client.get_bridges()
            self.save(data, self.SOURCE, 'bridges')
            self.update_status("bridges", True)
            self.log("Bridges fetched", "success")
        except Exception as e:
            self.update_status("bridges", False)

        try:
            data = self.client.get_bridge_volume(self.dl_chain)
            self.save(data, self.SOURCE, 'bridge_volume')
            self.update_status("bridge_volume", True)
            self.log(f"Bridge Volume for {self.dl_chain} fetched", "success")
        except Exception as e:
            self.update_status("bridge_volume", False)

    def _fetch_other_endpoints(self):
        """Fetch other DefiLlama endpoints."""
        try:
            data = self.client.get_open_interest()
            self.save(data, self.SOURCE, 'open_interest')
            self.update_status("open_interest", True)
            self.log("Open Interest fetched", "success")
        except Exception as e:
            self.update_status("open_interest", False)

        try:
            data = self.client.get_hacks()
            self.save(data, self.SOURCE, 'hacks')
            self.update_status("hacks", True)
            self.log(f"Hacks: {len(data)} incidents", "success")
        except Exception as e:
            self.update_status("hacks", False)

        try:
            data = self.client.get_raises()
            self.save(data, self.SOURCE, 'raises')
            self.update_status("raises", True)
            self.log("Raises fetched", "success")
        except Exception as e:
            self.update_status("raises", False)
