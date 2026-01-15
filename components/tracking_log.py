"""
Tracking Log / Endpoints Tab Component
Displays endpoint fetch status and log monitoring.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from config import SUPPORTED_CHAINS, SOURCE_ICONS
from constants.endpoints import ENDPOINT_MAPPING, SOURCE_DISPLAY_MAP
from data_handlers.storage import load_latest_json
from utils.validators import validate_contract_address


def get_endpoint_list():
    """Get the endpoint status list with sorting - auto-generated from ENDPOINT_MAPPING"""
    endpoints = []
    for name, (source, key) in ENDPOINT_MAPPING.items():
        source_display = SOURCE_DISPLAY_MAP.get(source, source.title())
        endpoints.append({
            "Endpoint": name,
            "Source": source_display,
            "Fetch Success": st.session_state.endpoint_status.get(key, "pending")
        })

    def get_sort_key(ep):
        status = ep["Fetch Success"]
        if "done" in status: return 0
        if "failed" in status: return 1
        if "⚠️" in status: return 2
        return 3

    return sorted(endpoints, key=get_sort_key)


def render_tab(fetch_callback, current_user: str, theme: str = "Dark"):
    """
    Render the Tracking Log / Endpoints tab.

    Args:
        fetch_callback: Function to call for fetching data
        current_user: Current user/token name
        theme: UI theme ('Dark' or 'Light')
    """
    st.header("Market Data Analysis")

    # Input section
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        chain = st.selectbox(
            "Chain",
            list(SUPPORTED_CHAINS.keys()),
            index=1  # Default to Solana
        )

    with col2:
        period = st.selectbox(
            "Period",
            ["3 months", "6 months", "1 year", "All"],
            index=0
        )

    with col3:
        contract_address = st.text_input(
            "Contract Address",
            placeholder="0x... or So11111111111111111111111111111111111111112",
            value="So11111111111111111111111111111111111111112"
        )

    # Fetch Button
    has_token_name = current_user and current_user != "anonymous"
    fetch_button = st.button("Fetch", type="primary", use_container_width=True, disabled=not has_token_name)

    if not has_token_name:
        st.warning("⚠️ Enter token name in sidebar before Fetch")

    st.markdown("---")

    # Check Phase State
    has_data = 'last_updated' in st.session_state.fetched_data

    # PHASE 2: Fetching in progress
    if fetch_button:
        if not validate_contract_address(contract_address, chain):
            st.error(f"Invalid contract address format for {chain}")
        else:
            st.subheader("📋 Log Monitoring")
            log_placeholder = st.empty()

            with st.spinner("Fetching data from multiple sources..."):
                fetch_callback(chain, contract_address, period, log_placeholder, current_user)

            st.rerun()

    # PHASE 3: Data Available
    elif has_data:
        left_status, right_panel = st.columns([2, 3])

        with left_status:
            st.subheader("Endpoints Fetching Status")
            endpoints = get_endpoint_list()

            # Header
            c1, c2, c3, c4 = st.columns([1, 0.5, 0.5, 1])
            c1.markdown("**Endpoint**")
            c2.markdown("**Source**")
            c3.markdown("**Status**")
            c4.markdown("**Action**")
            st.markdown('<hr style="margin: 0.1em 0; border-color: #333;">', unsafe_allow_html=True)

            for ep in endpoints:
                c1, c2, c3, c4 = st.columns([1, 0.5, 0.5, 1])
                c1.markdown(f"<div style='padding-top: 5px; font-size: 14px;'>{ep['Endpoint']}</div>", unsafe_allow_html=True)

                # Source Icon
                source_name = ep["Source"]
                icon_file = SOURCE_ICONS.get(source_name)
                if icon_file:
                    icon_path_full = Path(__file__).parent.parent / "assets" / icon_file
                    if icon_path_full.exists():
                        c2.image(str(icon_path_full), width=30)
                    else:
                        c2.markdown(f"<div style='padding-top: 5px; font-size: 12px;'>{source_name}</div>", unsafe_allow_html=True)
                else:
                    c2.markdown(f"<div style='padding-top: 5px; font-size: 12px;'>{source_name}</div>", unsafe_allow_html=True)

                c3.markdown(f"<div style='padding-top: 5px; font-size: 14px;'>{ep['Fetch Success']}</div>", unsafe_allow_html=True)

                if c4.button(":green[preview]", key=f"btn_{ep['Endpoint']}", use_container_width=True):
                    st.session_state.preview_endpoint = ep["Endpoint"]

                st.markdown('<hr style="margin: 0px 0; border-color: #333;">', unsafe_allow_html=True)

        with right_panel:
            st.subheader("📋 Log Monitoring")

            log_content = "<br>".join(st.session_state.logs)
            bg_color = "#0c0c0c" if theme == "Dark" else "#f0f2f6"
            text_color = "#00ff00" if theme == "Dark" else "#006400"

            st.markdown(f"""
                <div style="background-color: {bg_color}; color: {text_color}; font-family: monospace; padding: 15px; height: 300px; overflow-y: scroll; border: 1px solid #333; border-radius: 5px; font-size: 11px; line-height: 1.4;">
                    {log_content}
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Preview Area
            if st.session_state.preview_endpoint:
                endpoint_name = st.session_state.preview_endpoint
                if endpoint_name in ENDPOINT_MAPPING:
                    source, key = ENDPOINT_MAPPING[endpoint_name]
                    st.subheader(f"Preview: {endpoint_name}")

                    data = load_latest_json(source, chain, contract_address, key, current_user)
                    if data:
                        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                            st.dataframe(data["data"], use_container_width=True)
                        elif isinstance(data, dict) and "prices" in data and isinstance(data["prices"], list):
                            df = pd.DataFrame(data["prices"], columns=["Timestamp", "Price"])
                            df["Date"] = pd.to_datetime(df["Timestamp"], unit='ms')
                            st.dataframe(df[["Date", "Price"]], use_container_width=True)
                        elif isinstance(data, list):
                            st.dataframe(data, use_container_width=True)
                        else:
                            st.json(data)
                    else:
                        st.warning("No data found to preview.")

                    if st.button("Close Preview"):
                        st.session_state.preview_endpoint = None
                        st.rerun()

    # PHASE 1: Initial State
    else:
        st.info("Select chain and contract, then click Fetch to start analysis.")

    return chain, contract_address
