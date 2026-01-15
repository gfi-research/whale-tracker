"""
Main data fetcher orchestrator - coordinates all API fetchers.
"""

import streamlit as st
from datetime import datetime, timedelta

from config import SUPPORTED_CHAINS
from constants.endpoints import ENDPOINT_MAPPING
from utils.logger import log_to_ui as log_to_ui_util
from services.defillama_fetcher import DefiLlamaFetcher
from services.coingecko_fetcher import CoinGeckoFetcher
from services.nansen_fetcher import NansenFetcher


def fetch_all_data(chain_name: str, contract_address: str, period: str = "3 months",
                   log_placeholder=None, user_id: str = None, theme: str = "Dark"):
    """
    Main function to fetch data from all API sources.

    Args:
        chain_name: Blockchain name (e.g., 'Ethereum', 'Solana')
        contract_address: Token contract address
        period: Time period ('3 months', '6 months', '1 year', 'All')
        log_placeholder: Streamlit placeholder for live log display
        user_id: User identifier for multi-user storage
        theme: UI theme ('Dark' or 'Light')
    """
    # Reset session state
    st.session_state.logs = []
    st.session_state.endpoint_status = {}

    # Theme colors
    bg_color = "#0c0c0c" if theme == "Dark" else "#f0f2f6"
    text_color = "#00ff00" if theme == "Dark" else "#006400"

    def log_to_ui(message, status="info"):
        """Log message and update placeholder."""
        log_to_ui_util(message, status)
        if log_placeholder:
            log_content = "<br>".join(st.session_state.logs)
            log_placeholder.markdown(f"""
                <div style="background-color: {bg_color}; color: {text_color};
                     font-family: monospace; padding: 15px; height: 300px;
                     overflow-y: scroll; border: 1px solid #333; border-radius: 5px;
                     font-size: 12px; line-height: 1.5;">
                    {log_content}
                </div>
            """, unsafe_allow_html=True)

    log_to_ui(f"Starting fetch for {chain_name}: {contract_address} ({period}) by {user_id}", "info")

    # Get chain config
    chain_config = SUPPORTED_CHAINS.get(chain_name)
    if not chain_config:
        log_to_ui(f"Chain {chain_name} not found", "error")
        return

    # Calculate dates
    end_date_obj = datetime.now()
    days_map = {"3 months": 90, "6 months": 180, "1 year": 365}
    days = days_map.get(period, 365 * 3)
    start_date_obj = end_date_obj - timedelta(days=days)
    start_date_str = start_date_obj.strftime("%Y-%m-%d")
    end_date_str = end_date_obj.strftime("%Y-%m-%d")
    cg_days = str(days) if period != "All" else "max"

    # Initialize and run fetchers
    try:
        log_to_ui("Initializing API clients...", "info")

        # DefiLlama
        dl_fetcher = DefiLlamaFetcher(
            chain_name, contract_address, user_id, chain_config,
            log_callback=log_to_ui
        )
        dl_fetcher.fetch_all()

        # CoinGecko
        cg_fetcher = CoinGeckoFetcher(
            chain_name, contract_address, user_id, chain_config, cg_days,
            log_callback=log_to_ui
        )
        token_symbol, coin_id = cg_fetcher.fetch_all()

        # Nansen
        ns_fetcher = NansenFetcher(
            chain_name, contract_address, user_id, chain_config,
            start_date_str, end_date_str, token_symbol,
            log_callback=log_to_ui
        )
        ns_fetcher.fetch_all()

    except Exception as e:
        log_to_ui(f"Client init error: {str(e)}", "error")
        return

    # Summary
    log_to_ui("=" * 40, "info")
    total = len(ENDPOINT_MAPPING)
    done = sum(1 for v in st.session_state.endpoint_status.values() if "done" in v)
    log_to_ui(f"COMPLETED: {done}/{total} endpoints", "success")
    st.session_state.fetched_data['last_updated'] = datetime.now()
