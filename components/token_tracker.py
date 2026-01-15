"""
Token Tracker Tab Component
Displays token analytics and visualizations.
"""

import streamlit as st

from data_handlers.storage import load_latest_json
from visualizations.charts import create_delta_balance_chart, create_holders_bar_chart
from visualizations.tables import create_flow_intelligence_table, create_transfers_table


def render_tab(chain: str, contract_address: str, current_user: str):
    """
    Render the Token Tracker tab.

    Args:
        chain: Selected blockchain
        contract_address: Token contract address
        current_user: Current user/token name
    """
    st.header("Token Tracker")

    if 'last_updated' not in st.session_state.fetched_data:
        st.info("Fetch data in 'Tracking log/Enpoints' tab to see visualizations.")
        return

    # Load Data
    coin_info = load_latest_json('coingecko', chain, contract_address, 'coin_info', current_user)
    dune_data = load_latest_json('dune', chain, contract_address, 'delta_balance', current_user)
    flow_data = load_latest_json('nansen', chain, contract_address, 'flow_intelligence', current_user)
    holders_data = load_latest_json('nansen', chain, contract_address, 'holders', current_user)
    transfers_data = load_latest_json('nansen', chain, contract_address, 'transfers', current_user)

    # 1. Token Summary
    if coin_info:
        c1, c2 = st.columns([1, 4])
        with c1:
            img_url = coin_info.get('image', {}).get('large')
            if img_url:
                st.image(img_url, width=100)
        with c2:
            st.subheader(f"{coin_info.get('name')} ({coin_info.get('symbol').upper()})")
            md = coin_info.get('market_data', {})
            m1, m2, m3 = st.columns(3)
            m1.metric("Price", f"${md.get('current_price', {}).get('usd', 0)}")
            m2.metric("Market Cap", f"${md.get('market_cap', {}).get('usd', 0):,}")
            m3.metric("Volume (24h)", f"${md.get('total_volume', {}).get('usd', 0):,}")

    st.markdown("---")

    # 2. Delta Balance Change
    st.subheader("Delta Balance Change (Dune)")
    if dune_data:
        fig_dune = create_delta_balance_chart(dune_data)
        st.plotly_chart(fig_dune, use_container_width=True)
    else:
        st.info("No Dune data available")

    st.markdown("---")

    # 3. Token Flow Intelligence
    st.subheader("Token Flow Intelligence (Nansen)")
    if flow_data:
        net_df, avg_df, wallet_df = create_flow_intelligence_table(flow_data)
        if net_df is not None:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Net Flow (USD)**")
                st.dataframe(net_df, use_container_width=True)
            with c2:
                st.markdown("**Avg Flow (USD)**")
                st.dataframe(avg_df, use_container_width=True)
            with c3:
                st.markdown("**Wallet Count**")
                st.dataframe(wallet_df, use_container_width=True)
        else:
            st.warning("Flow Intelligence data format invalid. Please fetch again.")
    else:
        st.info("No Flow Intelligence data available")

    st.markdown("---")

    # 4. Token Holders
    st.subheader("Token Holders (Nansen)")
    if holders_data:
        fig_holders = create_holders_bar_chart(holders_data)
        if fig_holders:
            st.plotly_chart(fig_holders, use_container_width=True)
        else:
            st.info("No Holders data available (invalid format)")
    else:
        st.info("No Holders data available")

    st.markdown("---")

    # 5. Last Token Transfer
    st.subheader("Last Token Transfer (Nansen)")
    if transfers_data:
        transfers_df = create_transfers_table(transfers_data)
        if not transfers_df.empty:
            st.dataframe(transfers_df, use_container_width=True)
        else:
            st.info("No Transfers data available (invalid format)")
    else:
        st.info("No Transfers data available")
