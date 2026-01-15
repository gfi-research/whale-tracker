"""
Nansen API Client - Complete Implementation
All available endpoints included
"""
import json
import requests
from config import API_URLS, API_KEYS


class NansenClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEYS.get('NANSEN_API_KEY')
        self.base_url = API_URLS['NANSEN']

    def _make_request(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        headers = {
            'apiKey': self.api_key,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.last_headers = response.headers
        response.raise_for_status()
        return response.json()

    # ==================== SMART MONEY ====================

    def get_smart_money_netflow(self, chains, labels=None, include_stablecoins=False,
                                 include_native_tokens=False, token_sectors=None,
                                 page=1, per_page=50, order_by=None):
        """Get Smart Money net capital flows"""
        data = {
            "chains": chains if isinstance(chains, list) else [chains],
            "filters": {
                "include_stablecoins": include_stablecoins,
                "include_native_tokens": include_native_tokens
            },
            "pagination": {"page": page, "per_page": per_page}
        }
        if labels:
            data["filters"]["include_smart_money_labels"] = labels
        if token_sectors:
            data["filters"]["token_sectors"] = token_sectors
        if order_by:
            data["order_by"] = order_by
        else:
            data["order_by"] = [{"field": "net_flow_24h_usd", "direction": "DESC"}]
        return self._make_request('/smart-money/netflow', data)

    def get_smart_money_holdings(self, chains, page=1, per_page=50):
        """Get Smart Money current token holdings"""
        data = {
            "chains": chains if isinstance(chains, list) else [chains],
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/smart-money/holdings', data)

    def get_smart_money_historical_holdings(self, chains, page=1, per_page=50):
        """Get Smart Money historical holdings over time"""
        data = {
            "chains": chains if isinstance(chains, list) else [chains],
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/smart-money/historical-holdings', data)

    def get_smart_money_dex_trades(self, chains, page=1, per_page=50):
        """Get Smart Money DEX trades in last 24h"""
        data = {
            "chains": chains if isinstance(chains, list) else [chains],
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/smart-money/dex-trades', data)

    def get_smart_money_dcas(self, page=1, per_page=50):
        """Get Smart Money Jupiter DCA orders (Solana)"""
        data = {
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/smart-money/dcas', data)

    def get_smart_money_perp_trades(self, page=1, per_page=50):
        """Get Smart Money Hyperliquid perp trades"""
        data = {
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/smart-money/perp-trades', data)

    # ==================== PROFILER ====================

    def get_address_current_balance(self, address, chain, hide_spam=True,
                                     token_symbol=None, min_value_usd=None,
                                     page=1, per_page=100):
        """Get current token balances for an address"""
        data = {
            "address": address,
            "chain": chain,
            "hide_spam_token": hide_spam,
            "pagination": {"page": page, "per_page": per_page}
        }
        if token_symbol or min_value_usd:
            data["filters"] = {}
            if token_symbol:
                data["filters"]["token_symbol"] = token_symbol
            if min_value_usd:
                data["filters"]["value_usd"] = {"min": min_value_usd}
        return self._make_request('/profiler/address/current-balance', data)

    def get_address_historical_balances(self, address, chain, start_date=None, end_date=None, page=1, per_page=100):
        """Get historical holdings for an address"""
        data = {
            "address": address,
            "chain": chain,
            "pagination": {"page": page, "per_page": per_page}
        }
        if start_date and end_date:
            data["date"] = {"from": start_date, "to": end_date}
        return self._make_request('/profiler/address/historical-balances', data)

    def get_address_transactions(self, address, chain, start_date=None, end_date=None, page=1, per_page=50):
        """Get transaction list for an address"""
        data = {
            "address": address,
            "chain": chain,
            "pagination": {"page": page, "per_page": per_page}
        }
        if start_date and end_date:
            data["date"] = {"from": start_date, "to": end_date}
        return self._make_request('/profiler/address/transactions', data)

    def get_address_related_wallets(self, address, chain, page=1, per_page=50):
        """Get related wallets (1st degree connections)"""
        data = {
            "address": address,
            "chain": chain,
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/profiler/address/related-wallets', data)

    def get_address_counterparties(self, address, chain, start_date=None, end_date=None, page=1, per_page=20):
        """Get top counterparties for an address"""
        data = {
            "address": address,
            "chain": chain,
            "pagination": {"page": page, "per_page": per_page}
        }
        if start_date and end_date:
            data["date"] = {"from": start_date, "to": end_date}
        return self._make_request('/profiler/address/counterparties', data)

    def get_address_pnl_summary(self, address, chain):
        """Get trade summary + top 5 trades"""
        data = {
            "address": address,
            "chain": chain
        }
        return self._make_request('/profiler/address/pnl-summary', data)

    def get_address_pnl(self, address, chain, start_date=None, end_date=None, page=1, per_page=50):
        """Get all past trades with PnL"""
        data = {
            "address": address,
            "chain": chain,
            "pagination": {"page": page, "per_page": per_page}
        }
        if start_date and end_date:
            data["date"] = {"from": start_date, "to": end_date}
        return self._make_request('/profiler/address/pnl', data)

    def get_address_labels(self, address, chain, page=1, per_page=100):
        """Get address labels (500 credits per call!)"""
        data = {
            "parameters": {
                "chain": chain,
                "address": address
            },
            "pagination": {
                "page": page,
                "recordsPerPage": per_page
            }
        }
        return self._make_request('/profiler/address/labels', data)

    def get_profiler_perp_positions(self, address):
        """Get Hyperliquid positions for address (requires Hyperliquid wallet address)"""
        data = {
            "address": address
        }
        return self._make_request('/profiler/perp-positions', data)

    def get_profiler_perp_trades(self, address, start_date, end_date, page=1, per_page=50):
        """Get Hyperliquid trades for address (requires Hyperliquid wallet address)"""
        data = {
            "address": address,
            "date": {"from": start_date, "to": end_date},
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/profiler/perp-trades', data)

    def get_profiler_perp_leaderboard(self, page=1, per_page=50):
        """Get Hyperliquid leaderboard"""
        data = {
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/profiler/perp-leaderboard', data)

    def search_entity(self, query):
        """Search entity by name"""
        data = {"query": query}
        return self._make_request('/profiler/entity/search', data)

    # ==================== TOKEN GOD MODE (TGM) ====================

    def get_token_screener(self, chains, min_mcap=None, max_mcap=None,
                           min_token_age=None, min_smart_money_flow=None,
                           page=1, per_page=50, order_by=None):
        """Get real-time token analytics"""
        data = {
            "chains": chains if isinstance(chains, list) else [chains],
            "filters": {},
            "pagination": {"page": page, "per_page": per_page}
        }
        if min_mcap or max_mcap:
            data["filters"]["market_cap_usd"] = {}
            if min_mcap:
                data["filters"]["market_cap_usd"]["min"] = min_mcap
            if max_mcap:
                data["filters"]["market_cap_usd"]["max"] = max_mcap
        if min_token_age:
            data["filters"]["token_age_days"] = {"min": min_token_age}
        if min_smart_money_flow:
            data["filters"]["smart_money_net_flow_24h_usd"] = {"min": min_smart_money_flow}
        if order_by:
            data["order_by"] = order_by
        else:
            data["order_by"] = [{"field": "smart_money_net_flow_24h_usd", "direction": "DESC"}]
        return self._make_request('/tgm/token-screener', data)

    def get_perp_screener(self, page=1, per_page=50):
        """Get Hyperliquid token screener"""
        data = {
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/tgm/perp-screener', data)

    def get_token_flow_intelligence(self, address, chain):
        """Get token flows summary for multiple timeframes"""
        timeframes = ["5m", "1h", "6h", "12h", "1d", "7d"]
        results = {}
        for tf in timeframes:
            try:
                data = {
                    "chain": chain,
                    "token_address": address,
                    "timeframe": tf,
                    "filters": {}
                }
                response = self._make_request('/tgm/flow-intelligence', data)
                results[tf] = response
            except Exception as e:
                results[tf] = {"error": str(e)}
        return results

    def get_token_flows(self, address, chain):
        """Get inflow/outflow by category"""
        data = {
            "token_address": address,
            "chain": chain
        }
        return self._make_request('/tgm/flows', data)

    def get_token_who_bought_sold(self, address, chain, start_date=None, end_date=None,
                                   buy_or_sell="BUY", page=1, per_page=50):
        """Get recent buyers/sellers"""
        data = {
            "chain": chain,
            "token_address": address,
            "buy_or_sell": buy_or_sell,
            "pagination": {"page": page, "per_page": per_page}
        }
        if start_date and end_date:
            data["date"] = {"from": start_date, "to": end_date}
        return self._make_request('/tgm/who-bought-sold', data)

    def get_token_dex_trades(self, address, chain, page=1, per_page=50):
        """Get all DEX trades"""
        data = {
            "token_address": address,
            "chain": chain,
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/tgm/dex-trades', data)

    def get_token_transfers(self, address, chain, start_date=None, end_date=None,
                            page=1, per_page=50):
        """Get top token transfers"""
        data = {
            "token_address": address,
            "chain": chain,
            "pagination": {"page": page, "per_page": per_page}
        }
        if start_date and end_date:
            data["date"] = {"from": start_date, "to": end_date}
        return self._make_request('/tgm/transfers', data)

    def get_token_jup_dca(self, address, page=1, per_page=50):
        """Get Jupiter DCA orders"""
        data = {
            "token_address": address,
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/tgm/jup-dca', data)

    def get_token_perp_trades(self, token_symbol, start_date=None, end_date=None,
                               page=1, per_page=50, filters=None, order_by=None):
        """Get perp trading history"""
        data = {
            "token_symbol": token_symbol,
            "pagination": {"page": page, "per_page": per_page}
        }
        if start_date and end_date:
            data["date"] = {"from": start_date, "to": end_date}
        if filters:
            data["filters"] = filters
        if order_by:
            data["order_by"] = order_by
        return self._make_request('/tgm/perp-trades', data)

    def get_token_perp_positions(self, token_symbol, page=1, per_page=50):
        """Get open perp positions"""
        data = {
            "token_symbol": token_symbol,
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/tgm/perp-positions', data)

    def get_token_holders(self, address, chain, aggregate_by_entity=False,
                          page=1, per_page=100):
        """Get top holders by category"""
        data = {
            "token_address": address,
            "chain": chain,
            "aggregate_by_entity": aggregate_by_entity,
            "pagination": {"page": page, "per_page": per_page},
            "order_by": [{"field": "ownership_percentage", "direction": "DESC"}]
        }
        return self._make_request('/tgm/holders', data)

    def get_token_pnl_leaderboard(self, address, chain, page=1, per_page=50):
        """Get PnL leaderboard for token"""
        data = {
            "token_address": address,
            "chain": chain,
            "pagination": {"page": page, "per_page": per_page}
        }
        return self._make_request('/tgm/pnl-leaderboard', data)

    def get_perp_pnl_leaderboard(self, token_symbol=None, page=1, per_page=50):
        """Get Hyperliquid PnL leaderboard"""
        data = {
            "pagination": {"page": page, "per_page": per_page}
        }
        if token_symbol:
            data["token_symbol"] = token_symbol
        return self._make_request('/tgm/perp-pnl-leaderboard', data)

    # ==================== PORTFOLIO ====================

    def get_defi_holdings(self, wallet_address):
        """Get DeFi positions for a wallet address"""
        data = {
            "wallet_address": wallet_address
        }
        return self._make_request('/portfolio/defi-holdings', data)
