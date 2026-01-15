"""
Nansen data fetcher - handles all Nansen API endpoints.
"""

from services.base_fetcher import BaseFetcher
from api_clients.nansen_client import NansenClient


class NansenFetcher(BaseFetcher):
    """Fetcher for Nansen API endpoints."""

    SOURCE = "nansen"

    def __init__(self, chain_name: str, contract_address: str, user_id: str,
                 chain_config: dict, start_date: str, end_date: str,
                 token_symbol: str = None, log_callback=None):
        super().__init__(chain_name, contract_address, user_id, chain_config, log_callback)
        self.client = NansenClient()
        self.nansen_chain = chain_config.get('nansen')
        self.start_date = start_date
        self.end_date = end_date
        self.token_symbol = token_symbol

    def fetch_all(self):
        """Fetch all Nansen endpoints."""
        self.log("=" * 40, "info")
        self.log("NANSEN ENDPOINTS", "info")
        self.log("=" * 40, "info")

        self._fetch_smart_money_endpoints()
        self._fetch_profiler_endpoints()
        self._fetch_token_endpoints()
        self._fetch_perp_endpoints()
        self._fetch_portfolio_endpoints()

    def _fetch_smart_money_endpoints(self):
        """Fetch Smart Money endpoints."""
        # Smart Money Netflow
        try:
            data = self.client.get_smart_money_netflow([self.nansen_chain])
            self.save(data, self.SOURCE, 'sm_netflow')
            self.update_status("sm_netflow", True)
            self.log("Smart Money Netflow fetched", "success")
        except Exception as e:
            self.update_status("sm_netflow", False)

        # Smart Money Holdings
        try:
            data = self.client.get_smart_money_holdings([self.nansen_chain])
            self.save(data, self.SOURCE, 'sm_holdings')
            self.update_status("sm_holdings", True)
            self.log("Smart Money Holdings fetched", "success")
        except Exception as e:
            self.update_status("sm_holdings", False)

        # Smart Money DEX Trades
        try:
            data = self.client.get_smart_money_dex_trades([self.nansen_chain])
            self.save(data, self.SOURCE, 'sm_dex_trades')
            self.update_status("sm_dex_trades", True)
            self.log("Smart Money DEX Trades fetched", "success")
        except Exception as e:
            self.update_status("sm_dex_trades", False)

    def _fetch_profiler_endpoints(self):
        """Fetch Profiler endpoints (using contract as address)."""
        # Address Balance
        try:
            data = self.client.get_address_current_balance(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'address_balance')
            self.update_status("address_balance", True)
            self.log("Address Balance fetched", "success")
        except Exception as e:
            self.update_status("address_balance", False)

        # Address Transactions
        try:
            data = self.client.get_address_transactions(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'address_transactions')
            self.update_status("address_transactions", True)
            self.log("Address Transactions fetched", "success")
        except Exception as e:
            self.update_status("address_transactions", False)

        # Address Related Wallets
        try:
            data = self.client.get_address_related_wallets(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'address_related_wallets')
            self.update_status("address_related_wallets", True)
            self.log("Address Related Wallets fetched", "success")
        except Exception as e:
            self.update_status("address_related_wallets", False)

        # Address Counterparties
        try:
            data = self.client.get_address_counterparties(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'address_counterparties')
            self.update_status("address_counterparties", True)
            self.log("Address Counterparties fetched", "success")
        except Exception as e:
            self.update_status("address_counterparties", False)

        # Address PnL
        try:
            data = self.client.get_address_pnl(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'address_pnl')
            self.update_status("address_pnl", True)
            self.log("Address PnL fetched", "success")
        except Exception as e:
            self.update_status("address_pnl", False)

    def _fetch_token_endpoints(self):
        """Fetch TGM Token endpoints."""
        # Token Screener
        try:
            data = self.client.get_token_screener([self.nansen_chain])
            self.save(data, self.SOURCE, 'token_screener')
            self.update_status("token_screener", True)
            self.log("Token Screener fetched", "success")
        except Exception as e:
            self.update_status("token_screener", False)

        # Token Flows
        try:
            data = self.client.get_token_flows(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'token_flows')
            self.update_status("token_flows", True)
            self.log("Token Flows fetched", "success")
        except Exception as e:
            self.update_status("token_flows", False)

        # Flow Intelligence
        try:
            data = self.client.get_token_flow_intelligence(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'flow_intelligence')
            self.update_status("flow_intelligence", True)
            self.log("Flow Intelligence fetched", "success")
        except Exception as e:
            self.update_status("flow_intelligence", False)

        # Who Bought/Sold
        try:
            data = self.client.get_token_who_bought_sold(
                self.contract_address, self.nansen_chain, self.start_date, self.end_date)
            self.save(data, self.SOURCE, 'who_bought_sold')
            self.update_status("who_bought_sold", True)
            self.log("Who Bought/Sold fetched", "success")
        except Exception as e:
            self.update_status("who_bought_sold", False)

        # Token DEX Trades
        try:
            data = self.client.get_token_dex_trades(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'token_dex_trades')
            self.update_status("token_dex_trades", True)
            self.log("Token DEX Trades fetched", "success")
        except Exception as e:
            self.update_status("token_dex_trades", False)

        # Token Transfers
        try:
            data = self.client.get_token_transfers(
                self.contract_address, self.nansen_chain, self.start_date, self.end_date)
            self.save(data, self.SOURCE, 'transfers')
            self.update_status("transfers", True)
            self.log("Token Transfers fetched", "success")
        except Exception as e:
            self.update_status("transfers", False)

        # Token Holders
        try:
            data = self.client.get_token_holders(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'holders')
            self.update_status("holders", True)
            self.log("Token Holders fetched", "success")
        except Exception as e:
            self.update_status("holders", False)

        # Token PnL Leaderboard
        try:
            data = self.client.get_token_pnl_leaderboard(self.contract_address, self.nansen_chain)
            self.save(data, self.SOURCE, 'token_pnl_leaderboard')
            self.update_status("token_pnl_leaderboard", True)
            self.log("Token PnL Leaderboard fetched", "success")
        except Exception as e:
            self.update_status("token_pnl_leaderboard", False)

    def _fetch_perp_endpoints(self):
        """Fetch TGM Perp endpoints."""
        # Perp Screener
        try:
            data = self.client.get_perp_screener()
            self.save(data, self.SOURCE, 'perp_screener')
            self.update_status("perp_screener", True)
            self.log("Perp Screener fetched", "success")
        except Exception as e:
            self.update_status("perp_screener", False)

        # Token Perp Trades & Positions (requires token_symbol)
        if self.token_symbol:
            try:
                data = self.client.get_token_perp_trades(
                    self.token_symbol, self.start_date, self.end_date)
                self.save(data, self.SOURCE, 'perp_trades')
                self.update_status("perp_trades", True)
                self.log(f"Perp Trades for {self.token_symbol} fetched", "success")
            except Exception as e:
                self.update_status("perp_trades", False)

            try:
                data = self.client.get_token_perp_positions(self.token_symbol)
                self.save(data, self.SOURCE, 'perp_positions')
                self.update_status("perp_positions", True)
                self.log(f"Perp Positions for {self.token_symbol} fetched", "success")
            except Exception as e:
                self.update_status("perp_positions", False)
        else:
            self.skip_status("perp_trades")
            self.skip_status("perp_positions")

        # Perp PnL Leaderboard
        try:
            data = self.client.get_perp_pnl_leaderboard()
            self.save(data, self.SOURCE, 'perp_pnl_leaderboard')
            self.update_status("perp_pnl_leaderboard", True)
            self.log("Perp PnL Leaderboard fetched", "success")
        except Exception as e:
            self.update_status("perp_pnl_leaderboard", False)

    def _fetch_portfolio_endpoints(self):
        """Fetch Portfolio endpoints."""
        try:
            data = self.client.get_defi_holdings([self.contract_address], [self.nansen_chain])
            self.save(data, self.SOURCE, 'defi_holdings')
            self.update_status("defi_holdings", True)
            self.log("DeFi Holdings fetched", "success")
        except Exception as e:
            self.update_status("defi_holdings", False)
