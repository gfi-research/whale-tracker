"""
Wallet Profiler Tab Component
Analyze wallet addresses using Nansen Profiler API.
"""

import streamlit as st
from datetime import datetime, timedelta

from config import SUPPORTED_CHAINS
from api_clients.nansen_client import NansenClient
from data_handlers.storage import save_json


def render_tab(current_user: str):
    """
    Render the Wallet Profiler tab.

    Args:
        current_user: Current user/token name
    """
    st.header("Wallet Profiler (Nansen)")
    st.markdown("Analyze any wallet address using Nansen Profiler API")

    # Input section
    prof_col1, prof_col2 = st.columns([1, 3])

    with prof_col1:
        profiler_chain = st.selectbox(
            "Chain",
            list(SUPPORTED_CHAINS.keys()),
            index=0,
            key="profiler_chain"
        )

    with prof_col2:
        profiler_address = st.text_input(
            "Wallet Address",
            placeholder="0x... or wallet address",
            key="profiler_address"
        )

    # Date range selector
    st.markdown("**Date Range** (for endpoints that support date filter)")
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        prof_start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="prof_start")
    with date_col2:
        prof_end_date = st.date_input("End Date", value=datetime.now(), key="prof_end")

    start_date_str = prof_start_date.strftime("%Y-%m-%d")
    end_date_str = prof_end_date.strftime("%Y-%m-%d")

    st.markdown("---")

    call_labels = st.checkbox("Include Address Labels (500 credits per call)", value=False, key="call_labels")

    profiler_has_token = current_user and current_user != "anonymous"
    if not profiler_has_token:
        st.warning("⚠️ Enter token name in sidebar before Analyze")

    if st.button("Analyze Wallet", type="primary", use_container_width=True, key="profiler_btn", disabled=not profiler_has_token):
        if profiler_address:
            nansen_chain = SUPPORTED_CHAINS.get(profiler_chain, {}).get('nansen', 'ethereum')

            with st.spinner("Fetching wallet data from Nansen..."):
                try:
                    nansen = NansenClient()

                    # 1. Current Balances
                    st.subheader("1. Current Balances")
                    try:
                        balance_data = nansen.get_address_current_balance(profiler_address, nansen_chain)
                        if balance_data and 'data' in balance_data:
                            st.dataframe(balance_data['data'], use_container_width=True)
                        else:
                            st.json(balance_data)
                        save_json(balance_data, 'nansen', profiler_chain, profiler_address, 'profiler_current_balance', current_user)
                    except Exception as e:
                        st.error(f"Current Balance error: {e}")

                    st.markdown("---")

                    # 2. Historical Balances
                    st.subheader("2. Historical Balances")
                    try:
                        hist_balance_data = nansen.get_address_historical_balances(profiler_address, nansen_chain, start_date_str, end_date_str)
                        if hist_balance_data and 'data' in hist_balance_data:
                            st.dataframe(hist_balance_data['data'], use_container_width=True)
                        else:
                            st.json(hist_balance_data)
                        save_json(hist_balance_data, 'nansen', profiler_chain, profiler_address, 'profiler_historical_balances', current_user)
                    except Exception as e:
                        st.error(f"Historical Balances error: {e}")

                    st.markdown("---")

                    # 3. Transactions
                    st.subheader("3. Transactions")
                    try:
                        tx_data = nansen.get_address_transactions(profiler_address, nansen_chain, start_date_str, end_date_str)
                        if tx_data and 'data' in tx_data:
                            st.dataframe(tx_data['data'], use_container_width=True)
                        else:
                            st.json(tx_data)
                        save_json(tx_data, 'nansen', profiler_chain, profiler_address, 'profiler_transactions', current_user)
                    except Exception as e:
                        st.error(f"Transactions error: {e}")

                    st.markdown("---")

                    # 4. Counterparties
                    st.subheader("4. Counterparties")
                    try:
                        counter_data = nansen.get_address_counterparties(profiler_address, nansen_chain, start_date_str, end_date_str)
                        if counter_data and 'data' in counter_data:
                            st.dataframe(counter_data['data'], use_container_width=True)
                        else:
                            st.json(counter_data)
                        save_json(counter_data, 'nansen', profiler_chain, profiler_address, 'profiler_counterparties', current_user)
                    except Exception as e:
                        st.error(f"Counterparties error: {e}")

                    st.markdown("---")

                    # 5. Related Wallets
                    st.subheader("5. Related Wallets")
                    try:
                        related_data = nansen.get_address_related_wallets(profiler_address, nansen_chain)
                        if related_data and 'data' in related_data:
                            st.dataframe(related_data['data'], use_container_width=True)
                        else:
                            st.json(related_data)
                        save_json(related_data, 'nansen', profiler_chain, profiler_address, 'profiler_related_wallets', current_user)
                    except Exception as e:
                        st.error(f"Related Wallets error: {e}")

                    st.markdown("---")

                    # 6. PnL & Trade Performance
                    st.subheader("6. PnL & Trade Performance")
                    try:
                        pnl_data = nansen.get_address_pnl(profiler_address, nansen_chain, start_date_str, end_date_str)
                        if pnl_data and 'data' in pnl_data:
                            st.dataframe(pnl_data['data'], use_container_width=True)
                        else:
                            st.json(pnl_data)
                        save_json(pnl_data, 'nansen', profiler_chain, profiler_address, 'profiler_pnl', current_user)
                    except Exception as e:
                        st.error(f"PnL error: {e}")

                    st.markdown("---")

                    # 7. Address Labels (optional)
                    if call_labels:
                        st.subheader("7. Address Labels (500 credits)")
                        try:
                            labels_data = nansen.get_address_labels(profiler_address, nansen_chain)
                            if labels_data and isinstance(labels_data, list):
                                st.dataframe(labels_data, use_container_width=True)
                            elif labels_data:
                                st.json(labels_data)
                            else:
                                st.info("No labels found")
                            save_json(labels_data, 'nansen', profiler_chain, profiler_address, 'profiler_labels', current_user)
                        except Exception as e:
                            st.warning(f"Labels: {e}")
                        st.markdown("---")

                    # 8. Perp Positions (Hyperliquid)
                    st.subheader("8. Perp Positions (Hyperliquid)")
                    st.caption("Note: Only works with Hyperliquid wallet addresses")
                    try:
                        perp_pos_data = nansen.get_profiler_perp_positions(profiler_address)
                        if perp_pos_data and 'data' in perp_pos_data:
                            st.dataframe(perp_pos_data['data'], use_container_width=True)
                        elif perp_pos_data:
                            st.json(perp_pos_data)
                        else:
                            st.info("No perp positions found")
                        save_json(perp_pos_data, 'nansen', profiler_chain, profiler_address, 'profiler_perp_positions', current_user)
                    except Exception as e:
                        st.warning(f"Perp Positions: {e}")

                    st.markdown("---")

                    # 9. Perp Trades (Hyperliquid)
                    st.subheader("9. Perp Trades (Hyperliquid)")
                    st.caption("Note: Only works with Hyperliquid wallet addresses")
                    try:
                        perp_trades_data = nansen.get_profiler_perp_trades(profiler_address, start_date_str, end_date_str)
                        if perp_trades_data and 'data' in perp_trades_data:
                            st.dataframe(perp_trades_data['data'], use_container_width=True)
                        elif perp_trades_data:
                            st.json(perp_trades_data)
                        else:
                            st.info("No perp trades found")
                        save_json(perp_trades_data, 'nansen', profiler_chain, profiler_address, 'profiler_perp_trades', current_user)
                    except Exception as e:
                        st.warning(f"Perp Trades: {e}")

                    st.markdown("---")

                    # 10. Portfolio / DeFi Holdings
                    st.subheader("10. Portfolio / DeFi Holdings")
                    try:
                        portfolio_data = nansen.get_defi_holdings(profiler_address)
                        if portfolio_data:
                            if 'summary' in portfolio_data:
                                summary = portfolio_data['summary']
                                m1, m2, m3 = st.columns(3)
                                m1.metric("Total Value", f"${summary.get('total_value_usd', 0):,.2f}")
                                m2.metric("Total Assets", f"${summary.get('total_assets_usd', 0):,.2f}")
                                m3.metric("Total Debts", f"${summary.get('total_debts_usd', 0):,.2f}")

                                m4, m5, m6 = st.columns(3)
                                m4.metric("Total Rewards", f"${summary.get('total_rewards_usd', 0):,.2f}")
                                m5.metric("Token Count", summary.get('token_count', 0))
                                m6.metric("Protocol Count", summary.get('protocol_count', 0))

                            if 'protocols' in portfolio_data and portfolio_data['protocols']:
                                st.markdown("**Protocols:**")
                                st.dataframe(portfolio_data['protocols'], use_container_width=True)
                            else:
                                st.info("No active DeFi positions found")
                        else:
                            st.info("No DeFi holdings data")
                        save_json(portfolio_data, 'nansen', profiler_chain, profiler_address, 'profiler_portfolio', current_user)
                    except Exception as e:
                        st.warning(f"Portfolio: {e}")

                    st.success("Wallet analysis complete!")

                except Exception as e:
                    st.error(f"Error initializing Nansen client: {e}")
        else:
            st.warning("Please enter a wallet address")
