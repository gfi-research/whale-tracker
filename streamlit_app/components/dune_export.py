"""
Dune Export Tab Component
Execute SQL queries on Dune Analytics and save to BigQuery.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from api_clients.dune_client import DuneClient
from data_handlers.storage import save_dune_to_bigquery


def render_tab(current_user: str):
    """
    Render the Dune Export tab.

    Args:
        current_user: Current user/token name
    """
    st.header("Dune Export")
    st.markdown("Execute raw SQL queries on Dune Analytics and auto-save to BigQuery/GCS")

    # Export name
    dune_export_name = st.text_input(
        "Export Name",
        placeholder="Enter export name (e.g., etf_flows, corn_transactions)...",
        key="dune_export_name"
    )

    # SQL Editor
    st.subheader("SQL Editor")

    sample_sql = """-- Example: Get ETH transactions
SELECT
    block_time,
    hash,
    "from",
    "to",
    value / 1e18 as eth_value
FROM ethereum.transactions
WHERE block_time >= CURRENT_TIMESTAMP - INTERVAL '1' hour
LIMIT 100"""

    dune_sql = st.text_area(
        "Enter your Dune SQL query:",
        value=sample_sql,
        height=300,
        key="dune_sql_editor",
        help="Write your raw SQL query. Use Dune's table schemas. Remember to add LIMIT!"
    )

    st.markdown("""
        <style>
        textarea[data-testid="stTextArea"] {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
            font-size: 13px !important;
            line-height: 1.4 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Check requirements
    dune_has_token = current_user and current_user != "anonymous"
    dune_has_export_name = dune_export_name and dune_export_name.strip()
    can_execute = dune_has_token and dune_has_export_name

    if not dune_has_token:
        st.warning("Enter token name in sidebar before executing")
    elif not dune_has_export_name:
        st.warning("Enter export name before executing")

    execute_btn = st.button(
        "Execute & Save",
        type="primary",
        use_container_width=True,
        disabled=not can_execute,
        key="dune_execute_btn"
    )

    # Initialize session state
    if 'dune_results' not in st.session_state:
        st.session_state.dune_results = None
    if 'dune_df' not in st.session_state:
        st.session_state.dune_df = None

    # Execute query
    if execute_btn:
        if dune_sql.strip():
            with st.spinner("Executing query on Dune Analytics..."):
                try:
                    dune = DuneClient()
                    results = dune.run_sql(dune_sql)
                    st.session_state.dune_results = results

                    if results.get('rows'):
                        df = pd.DataFrame(results['rows'])
                        st.session_state.dune_df = df
                        st.success(f"Query executed! {len(df)} rows returned.")

                        with st.spinner("Saving to BigQuery..."):
                            rows_data = results.get('rows', [])
                            export_name_clean = dune_export_name.strip().replace(' ', '_')

                            bq_result = save_dune_to_bigquery(
                                rows_data,
                                export_name=export_name_clean,
                                user_id=current_user
                            )

                            if bq_result and isinstance(bq_result, str):
                                st.success(f"✅ BigQuery: {bq_result} ({len(rows_data)} rows)")
                            elif bq_result and isinstance(bq_result, dict) and bq_result.get('error'):
                                st.error(f"❌ BigQuery Error: {bq_result['error']}")
                    else:
                        st.session_state.dune_df = pd.DataFrame()
                        st.info("Query executed but returned no results.")

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.dune_results = None
                    st.session_state.dune_df = None
        else:
            st.warning("Please enter a SQL query")

    # Display results
    if st.session_state.dune_df is not None and not st.session_state.dune_df.empty:
        st.markdown("---")
        st.subheader("Query Results")

        if st.session_state.dune_results:
            meta = st.session_state.dune_results.get('metadata', {})
            if meta:
                with st.expander("Query Metadata"):
                    st.json(meta)

        st.dataframe(st.session_state.dune_df, use_container_width=True)

        csv_data = st.session_state.dune_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv_data,
            file_name=f"{dune_export_name or 'dune_export'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="dune_download_csv"
        )
