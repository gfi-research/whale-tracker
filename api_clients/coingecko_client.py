"""
CoinGecko API Client - Complete Implementation
All FREE tier endpoints included
"""
import requests
from config import API_URLS, API_KEYS


class CoinGeckoClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEYS.get('COINGECKO_API_KEY')
        self.base_url = API_URLS['COINGECKO']

    def _get_headers(self):
        headers = {}
        if self.api_key:
            headers['x-cg-pro-api-key'] = self.api_key
        return headers

    def _make_request(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self._get_headers(), params=params)
        self.last_headers = response.headers
        response.raise_for_status()
        return response.json()

    # ==================== PING & STATUS ====================

    def ping(self):
        """Check API server status"""
        return self._make_request("/ping")

    def get_api_usage(self):
        """Check API usage (Pro plan)"""
        return self._make_request("/key")

    # ==================== SIMPLE (PRICE) ====================

    def get_simple_price(self, ids, vs_currencies='usd', include_market_cap=True,
                         include_24hr_vol=True, include_24hr_change=True):
        """Get current price of coins"""
        params = {
            'ids': ','.join(ids) if isinstance(ids, list) else ids,
            'vs_currencies': ','.join(vs_currencies) if isinstance(vs_currencies, list) else vs_currencies,
            'include_market_cap': str(include_market_cap).lower(),
            'include_24hr_vol': str(include_24hr_vol).lower(),
            'include_24hr_change': str(include_24hr_change).lower()
        }
        return self._make_request("/simple/price", params)

    def get_simple_token_price(self, platform_id, contract_addresses, vs_currencies='usd'):
        """Get token price by contract address"""
        params = {
            'contract_addresses': ','.join(contract_addresses) if isinstance(contract_addresses, list) else contract_addresses,
            'vs_currencies': vs_currencies
        }
        return self._make_request(f"/simple/token_price/{platform_id}", params)

    def get_supported_vs_currencies(self):
        """List all supported vs currencies"""
        return self._make_request("/simple/supported_vs_currencies")

    # ==================== COINS ====================

    def get_coins_list(self, include_platform=False):
        """List all coins with id, name, symbol"""
        params = {'include_platform': str(include_platform).lower()}
        return self._make_request("/coins/list", params)

    def get_coins_markets(self, vs_currency='usd', ids=None, category=None,
                          order='market_cap_desc', per_page=100, page=1, sparkline=False):
        """Get coins with market data (price, mcap, volume)"""
        params = {
            'vs_currency': vs_currency,
            'order': order,
            'per_page': per_page,
            'page': page,
            'sparkline': str(sparkline).lower()
        }
        if ids:
            params['ids'] = ','.join(ids) if isinstance(ids, list) else ids
        if category:
            params['category'] = category
        return self._make_request("/coins/markets", params)

    def get_coin_data(self, coin_id, localization=False, tickers=True,
                      market_data=True, community_data=False, developer_data=False):
        """Get coin data by ID"""
        params = {
            'localization': str(localization).lower(),
            'tickers': str(tickers).lower(),
            'market_data': str(market_data).lower(),
            'community_data': str(community_data).lower(),
            'developer_data': str(developer_data).lower()
        }
        return self._make_request(f"/coins/{coin_id}", params)

    def get_coin_tickers(self, coin_id, exchange_ids=None, page=1):
        """Get coin tickers (exchange trading pairs)"""
        params = {'page': page}
        if exchange_ids:
            params['exchange_ids'] = ','.join(exchange_ids) if isinstance(exchange_ids, list) else exchange_ids
        return self._make_request(f"/coins/{coin_id}/tickers", params)

    def get_coin_history(self, coin_id, date, localization=False):
        """Get historical data at specific date (dd-mm-yyyy)"""
        params = {
            'date': date,
            'localization': str(localization).lower()
        }
        return self._make_request(f"/coins/{coin_id}/history", params)

    def get_coin_market_chart(self, coin_id, vs_currency='usd', days=30, interval=None):
        """Get market chart data (price, mcap, volume) over time"""
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        if interval:
            params['interval'] = interval
        return self._make_request(f"/coins/{coin_id}/market_chart", params)

    def get_coin_market_chart_range(self, coin_id, vs_currency='usd', from_timestamp=None, to_timestamp=None):
        """Get market chart data within time range"""
        params = {
            'vs_currency': vs_currency,
            'from': from_timestamp,
            'to': to_timestamp
        }
        return self._make_request(f"/coins/{coin_id}/market_chart/range", params)

    def get_coin_ohlc(self, coin_id, vs_currency='usd', days=30):
        """Get OHLC data"""
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        return self._make_request(f"/coins/{coin_id}/ohlc", params)

    # ==================== CONTRACT ====================

    def get_coin_info_by_contract(self, platform_id, contract_address):
        """Get coin info by contract address"""
        return self._make_request(f"/coins/{platform_id}/contract/{contract_address}")

    def get_coin_historical_chart_by_contract(self, platform_id, contract_address,
                                               vs_currency='usd', days='max'):
        """Get market chart by contract address"""
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        return self._make_request(f"/coins/{platform_id}/contract/{contract_address}/market_chart", params)

    def get_coin_market_chart_range_by_contract(self, platform_id, contract_address,
                                                 vs_currency='usd', from_timestamp=None, to_timestamp=None):
        """Get market chart range by contract address"""
        params = {
            'vs_currency': vs_currency,
            'from': from_timestamp,
            'to': to_timestamp
        }
        return self._make_request(f"/coins/{platform_id}/contract/{contract_address}/market_chart/range", params)

    # ==================== CATEGORIES ====================

    def get_categories_list(self):
        """List all coin categories"""
        return self._make_request("/coins/categories/list")

    def get_categories(self, order='market_cap_desc'):
        """Get categories with market data"""
        params = {'order': order}
        return self._make_request("/coins/categories", params)

    # ==================== NFT ====================

    def get_nfts_list(self, order=None, per_page=100, page=1):
        """List all NFTs"""
        params = {'per_page': per_page, 'page': page}
        if order:
            params['order'] = order
        return self._make_request("/nfts/list", params)

    def get_nft(self, nft_id):
        """Get NFT data by ID"""
        return self._make_request(f"/nfts/{nft_id}")

    def get_nft_by_contract(self, platform_id, contract_address):
        """Get NFT by contract address"""
        return self._make_request(f"/nfts/{platform_id}/contract/{contract_address}")

    # ==================== EXCHANGES ====================

    def get_exchanges(self, per_page=100, page=1):
        """Get all exchanges"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request("/exchanges", params)

    def get_exchanges_list(self):
        """Get exchange ID map"""
        return self._make_request("/exchanges/list")

    def get_exchange(self, exchange_id):
        """Get exchange data by ID"""
        return self._make_request(f"/exchanges/{exchange_id}")

    def get_exchange_tickers(self, exchange_id, coin_ids=None, page=1):
        """Get exchange tickers"""
        params = {'page': page}
        if coin_ids:
            params['coin_ids'] = ','.join(coin_ids) if isinstance(coin_ids, list) else coin_ids
        return self._make_request(f"/exchanges/{exchange_id}/tickers", params)

    def get_exchange_volume_chart(self, exchange_id, days=30):
        """Get exchange volume chart"""
        params = {'days': days}
        return self._make_request(f"/exchanges/{exchange_id}/volume_chart", params)

    # ==================== DERIVATIVES ====================

    def get_derivatives(self, include_tickers=None):
        """Get all derivatives tickers"""
        params = {}
        if include_tickers:
            params['include_tickers'] = include_tickers
        return self._make_request("/derivatives", params)

    def get_derivatives_exchanges(self, order=None, per_page=100, page=1):
        """Get derivatives exchanges"""
        params = {'per_page': per_page, 'page': page}
        if order:
            params['order'] = order
        return self._make_request("/derivatives/exchanges", params)

    def get_derivatives_exchange(self, exchange_id, include_tickers=None):
        """Get derivatives exchange by ID"""
        params = {}
        if include_tickers:
            params['include_tickers'] = include_tickers
        return self._make_request(f"/derivatives/exchanges/{exchange_id}", params)

    def get_derivatives_exchanges_list(self):
        """Get derivatives exchange list"""
        return self._make_request("/derivatives/exchanges/list")

    # ==================== PUBLIC TREASURIES ====================

    def get_companies_treasury(self, coin_id):
        """Get companies holding coin (bitcoin or ethereum)"""
        return self._make_request(f"/companies/public_treasury/{coin_id}")

    # ==================== GENERAL ====================

    def get_asset_platforms(self, filter_type=None):
        """Get all asset platforms"""
        params = {}
        if filter_type:
            params['filter'] = filter_type
        return self._make_request("/asset_platforms", params)

    def get_exchange_rates(self):
        """Get BTC exchange rates"""
        return self._make_request("/exchange_rates")

    def search(self, query):
        """Search for coins, exchanges, categories"""
        params = {'query': query}
        return self._make_request("/search", params)

    def get_trending(self):
        """Get trending searches"""
        return self._make_request("/search/trending")

    def get_global(self):
        """Get global crypto data"""
        return self._make_request("/global")

    def get_global_defi(self):
        """Get global DeFi data"""
        return self._make_request("/global/decentralized_finance_defi")

    # ==================== ONCHAIN DEX (GeckoTerminal) ====================

    def get_onchain_simple_token_price(self, network, addresses):
        """Get onchain token prices"""
        addr_str = ','.join(addresses) if isinstance(addresses, list) else addresses
        return self._make_request(f"/onchain/simple/networks/{network}/token_price/{addr_str}")

    def get_onchain_networks(self, page=1):
        """Get all supported networks"""
        params = {'page': page}
        return self._make_request("/onchain/networks", params)

    def get_onchain_dexes(self, network, page=1):
        """Get DEXes on a network"""
        params = {'page': page}
        return self._make_request(f"/onchain/networks/{network}/dexes", params)

    def get_onchain_trending_pools(self, include=None, page=1, duration=None):
        """Get trending pools across all networks"""
        params = {'page': page}
        if include:
            params['include'] = include
        if duration:
            params['duration'] = duration
        return self._make_request("/onchain/networks/trending_pools", params)

    def get_onchain_trending_pools_network(self, network, include=None, page=1):
        """Get trending pools on specific network"""
        params = {'page': page}
        if include:
            params['include'] = include
        return self._make_request(f"/onchain/networks/{network}/trending_pools", params)

    def get_onchain_new_pools(self, include=None, page=1):
        """Get new pools across all networks"""
        params = {'page': page}
        if include:
            params['include'] = include
        return self._make_request("/onchain/networks/new_pools", params)

    def get_onchain_new_pools_network(self, network, include=None, page=1):
        """Get new pools on specific network"""
        params = {'page': page}
        if include:
            params['include'] = include
        return self._make_request(f"/onchain/networks/{network}/new_pools", params)

    def get_onchain_pools(self, network, include=None, page=1, sort=None):
        """Get top pools on network"""
        params = {'page': page}
        if include:
            params['include'] = include
        if sort:
            params['sort'] = sort
        return self._make_request(f"/onchain/networks/{network}/pools", params)

    def get_onchain_pool(self, network, pool_address):
        """Get pool data by address"""
        return self._make_request(f"/onchain/networks/{network}/pools/{pool_address}")

    def get_onchain_pool_info(self, network, pool_address):
        """Get pool info"""
        return self._make_request(f"/onchain/networks/{network}/pools/{pool_address}/info")

    def get_onchain_pool_ohlcv(self, network, pool_address, timeframe='day',
                                aggregate=1, limit=100, currency='usd'):
        """Get pool OHLCV data"""
        params = {
            'aggregate': aggregate,
            'limit': limit,
            'currency': currency
        }
        return self._make_request(f"/onchain/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}", params)

    def get_onchain_pool_trades(self, network, pool_address, trade_volume_min=None):
        """Get pool trades"""
        params = {}
        if trade_volume_min:
            params['trade_volume_in_usd_greater_than'] = trade_volume_min
        return self._make_request(f"/onchain/networks/{network}/pools/{pool_address}/trades", params)

    def get_onchain_token(self, network, token_address, include=None):
        """Get token data"""
        params = {}
        if include:
            params['include'] = include
        return self._make_request(f"/onchain/networks/{network}/tokens/{token_address}", params)

    def get_onchain_token_info(self, network, token_address):
        """Get token info"""
        return self._make_request(f"/onchain/networks/{network}/tokens/{token_address}/info")

    def get_onchain_token_pools(self, network, token_address, include=None, page=1, sort=None):
        """Get top pools for token"""
        params = {'page': page}
        if include:
            params['include'] = include
        if sort:
            params['sort'] = sort
        return self._make_request(f"/onchain/networks/{network}/tokens/{token_address}/pools", params)

    def search_onchain_pools(self, query, network=None, include=None, page=1):
        """Search pools"""
        params = {'query': query, 'page': page}
        if network:
            params['network'] = network
        if include:
            params['include'] = include
        return self._make_request("/onchain/search/pools", params)

    def get_onchain_tokens_recently_updated(self, include=None, network=None):
        """Get recently updated tokens"""
        params = {}
        if include:
            params['include'] = include
        if network:
            params['network'] = network
        return self._make_request("/onchain/tokens/info_recently_updated", params)
