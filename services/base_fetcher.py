"""
Base fetcher class with common utilities for all data sources.
"""

import streamlit as st
from data_handlers.storage import save_json
from utils.logger import log_to_ui as log_to_ui_util


class BaseFetcher:
    """Base class for all API fetchers with common utilities."""

    def __init__(self, chain_name: str, contract_address: str, user_id: str,
                 chain_config: dict, log_callback=None):
        self.chain_name = chain_name
        self.contract_address = contract_address
        self.user_id = user_id
        self.chain_config = chain_config
        self.log_callback = log_callback

    def log(self, message: str, status: str = "info"):
        """Log message to UI."""
        log_to_ui_util(message, status)
        if self.log_callback:
            self.log_callback(message, status)

    def save(self, data, source: str, endpoint_key: str):
        """Save data to storage."""
        save_json(data, source, self.chain_name, self.contract_address,
                  endpoint_key, self.user_id)

    def update_status(self, key: str, success: bool = True):
        """Update endpoint status in session state."""
        status = "✅ done" if success else "❌ failed"
        st.session_state.endpoint_status[key] = status

    def skip_status(self, key: str):
        """Mark endpoint as skipped."""
        st.session_state.endpoint_status[key] = "⚠️ skip"

    def fetch_and_save(self, endpoint_key: str, fetch_func, *args,
                       source: str = "unknown", log_msg: str = None, **kwargs):
        """
        Generic fetch and save with error handling.

        Args:
            endpoint_key: Key to identify the endpoint
            fetch_func: Function to call for fetching data
            source: Data source name
            log_msg: Optional success message
        """
        try:
            data = fetch_func(*args, **kwargs)
            self.save(data, source, endpoint_key)
            self.update_status(endpoint_key, True)
            if log_msg:
                self.log(log_msg, "success")
            return data
        except Exception as e:
            self.update_status(endpoint_key, False)
            self.log(f"{endpoint_key} error: {str(e)[:50]}", "error")
            return None
