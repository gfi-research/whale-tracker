"""
Whale Tracker Dashboard - Multi-Dashboard App
Combines Smart Money (Nansen API) + Whale Screener (Hyperliquid API)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Nansen imports
from nansen_client import NansenClient, get_usage_tracker, reset_usage_tracker
from utils import (
    calculate_perp_bias,
    calculate_size_cohort,
    format_currency,
    truncate_address,
)

# Hyperliquid imports
from src.api.hyperliquid import HyperliquidClient, get_mock_portfolio_breakdown, TradeFill
from src.utils.formatters import format_currency as hl_format_currency

# Color palette - synced with whale-tracker
COLORS = {
    "perp": "#3bb5d3",
    "spot": "#7dd3fc",
    "background": "#1a2845",
    "text": "#e2e8f0",
    "grid": "#3a4556",
    "green": "#22c55e",
    "red": "#ef4444",
}

# Heatmap color scale
HEATMAP_COLORSCALE = [
    [0, "#1a2845"],
    [0.25, "#1e3a5f"],
    [0.5, "#3bb5d3"],
    [0.75, "#7dd3fc"],
    [1, "#e2e8f0"]
]

# Page config
st.set_page_config(
    page_title="Whale Tracker",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with synced background
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COLORS['background']};
    }}
    .main .block-container {{
        background-color: {COLORS['background']};
    }}
    [data-testid="stSidebar"] {{
        background-color: #0f172a;
    }}
    .metric-card {{
        background-color: #1e293b;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #334155;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 24px;
        color: {COLORS['text']};
    }}
    div[data-testid="stMetricLabel"] {{
        color: #94a3b8;
    }}
    h1, h2, h3, .stMarkdown {{
        color: {COLORS['text']};
    }}
    .stExpander {{
        background-color: #1e293b;
        border: 1px solid #334155;
    }}
</style>
""", unsafe_allow_html=True)


# ==================== SMART MONEY (NANSEN) DASHBOARD ====================

@st.cache_resource
def get_nansen_client():
    return NansenClient()

nansen_client = get_nansen_client()


# ==================== PERSISTENT CACHING ====================
# Cache persists until user manually clicks Reload/Fetch button

@st.cache_data(show_spinner=False)
def cached_get_wallet_positions(address: str):
    """Cache wallet positions from Nansen API (persists until manual reload)."""
    return nansen_client.get_wallet_positions(address)


@st.cache_data(show_spinner=False)
def cached_get_open_orders(address: str):
    """Cache open orders from Hyperliquid API (persists until manual reload)."""
    try:
        hl_client = HyperliquidClient()
        return hl_client.get_open_orders(address)
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def cached_get_portfolio_breakdown(address: str, period: str = "day"):
    """Cache portfolio breakdown from Hyperliquid API (persists until manual reload)."""
    try:
        hl_client = HyperliquidClient()
        return hl_client.get_portfolio_breakdown(address, period)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def cached_get_user_fills(address: str, start_time: datetime, end_time: datetime = None):
    """Cache user fills from Hyperliquid API (persists until manual reload)."""
    try:
        hl_client = HyperliquidClient()
        return hl_client.get_user_fills_by_time(address, start_time, end_time)
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def cached_get_token_positions(token_symbol: str, per_page: int = 100, min_position_value: float = 10000):
    """Cache token positions from Nansen API (persists until manual reload)."""
    return nansen_client.get_token_positions(token_symbol, per_page=per_page, min_position_value=min_position_value)


@st.dialog("Position Details", width="large")
def show_position_dialog(wallet_data: dict):
    """Display wallet positions in a modal dialog"""
    address = wallet_data.get('address', '')
    label = wallet_data.get('label', truncate_address(address))

    st.markdown(f"### {label}")

    col_addr, col_reload = st.columns([4, 1])
    with col_addr:
        st.caption(f"`{address}`")
    with col_reload:
        if st.button("🔄 Reload", key=f"reload_{address}", help="Fetch latest data"):
            # Clear persistent cache for this address
            cached_get_wallet_positions.clear()
            cached_get_open_orders.clear()
            st.rerun()

    # Use persistent cache (survives tab switches)
    with st.spinner("Loading positions..."):
        position_data = cached_get_wallet_positions(address)

    st.caption("📦 **Cached** - Click Reload for latest")

    if position_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            account_value = position_data.get('margin_summary_account_value_usd') or 0
            st.metric("Account Value", format_currency(float(account_value), compact=True))
        with col2:
            total_margin = position_data.get('margin_summary_total_margin_used_usd') or 0
            st.metric("Margin Used", format_currency(float(total_margin), compact=True))
        with col3:
            withdrawable = position_data.get('withdrawable_usd') or 0
            st.metric("Withdrawable", format_currency(float(withdrawable), compact=True))
        with col4:
            net_liq = position_data.get('margin_summary_total_net_liquidation_position_usd') or 0
            st.metric("Net Liq Position", format_currency(float(net_liq), compact=True))

        st.divider()

        asset_positions = position_data.get('asset_positions', [])
        if asset_positions:
            st.markdown("#### Open Positions")

            # Fetch open orders from Hyperliquid API (persistent cache)
            open_orders = cached_get_open_orders(address)

            # Count orders per coin
            orders_by_coin = {}
            for order in open_orders:
                coin = order.get('coin', '')
                orders_by_coin[coin] = orders_by_coin.get(coin, 0) + 1

            for pos_data in asset_positions:
                pos = pos_data.get('position', {})
                token = pos.get('token_symbol', 'Unknown')
                size = float(pos.get('size') or 0)
                direction = "LONG" if size > 0 else "SHORT"
                direction_emoji = "🟢" if size > 0 else "🔴"

                with st.container():
                    cols = st.columns([1.5, 1, 1, 1, 1, 1, 0.8])

                    with cols[0]:
                        st.markdown(f"**{token}** {direction_emoji} {direction}")
                        leverage = pos.get('leverage_value', 1)
                        lev_type = pos.get('leverage_type', 'cross')
                        st.caption(f"{leverage}x {lev_type}")

                    with cols[1]:
                        entry = float(pos.get('entry_price_usd') or 0)
                        st.markdown("**Entry**")
                        st.markdown(f"${entry:,.4f}")

                    with cols[2]:
                        position_value = float(pos.get('position_value_usd') or 0)
                        st.markdown("**Value**")
                        st.markdown(format_currency(position_value, compact=True))

                    with cols[3]:
                        margin = float(pos.get('margin_used_usd') or 0)
                        st.markdown("**Margin**")
                        st.markdown(format_currency(margin, compact=True))

                    with cols[4]:
                        upnl = float(pos.get('unrealized_pnl_usd') or 0)
                        roe = float(pos.get('return_on_equity') or 0) * 100
                        st.markdown("**uPnL**")
                        if upnl >= 0:
                            st.markdown(f":green[+{format_currency(upnl, compact=True)}]")
                        else:
                            st.markdown(f":red[{format_currency(upnl, compact=True)}]")
                        st.caption(f"ROE: {roe:+.1f}%")

                    with cols[5]:
                        liq_price = float(pos.get('liquidation_price_usd') or 0)
                        st.markdown("**Liq Price**")
                        st.markdown(f"${liq_price:,.2f}")

                    with cols[6]:
                        order_count = orders_by_coin.get(token, 0)
                        st.markdown("**Order/Pos**")
                        if order_count > 0:
                            st.markdown(f":blue[{order_count}]")
                        else:
                            st.markdown("0")

                    st.divider()
        else:
            st.info("No open positions")
    else:
        st.error("Failed to fetch position data from API")

    tracker = get_usage_tracker()
    if is_cached:
        st.caption(f"💰 **0 credits** (cached) | Session total: {tracker.total_credits_used} credits")
    else:
        st.caption(f"💰 **1 credit** used | Session total: {tracker.total_credits_used} credits")


def render_smart_money_sidebar():
    """Render Smart Money sidebar"""
    st.header("📊 API Usage")
    tracker = get_usage_tracker()
    summary = tracker.get_summary()

    st.metric("Credits Used", summary['total_credits_used'])
    st.metric("API Calls", summary['total_calls'])
    st.metric("Success Rate", f"{(summary['successful_calls'] / max(summary['total_calls'], 1)) * 100:.0f}%")

    if summary['total_calls'] > 0:
        st.metric("Avg Response", f"{summary['avg_response_time_ms']:.0f}ms")

    st.divider()

    # Show whale data status
    if st.session_state.get('whale_positions_loaded', False):
        whale_count = len(st.session_state.get('whale_wallet_data', []))
        st.success(f"✅ {whale_count} whales loaded")

        if st.button("🔄 Refetch All Whales", type="secondary"):
            st.session_state.whale_positions_loaded = False
            st.session_state.whale_wallet_data = []
            st.session_state.whale_all_positions = []
            reset_usage_tracker()
            st.rerun()
    else:
        st.warning("⏳ Whale data not loaded")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset"):
            reset_usage_tracker()
            st.rerun()
    with col2:
        if st.button("🗑️ Clear"):
            # Clear session state flags
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("positions_") or k.startswith("token_positions_") or k.startswith("loaded_")]
            for k in keys_to_delete:
                del st.session_state[k]
            # Clear persistent cache
            st.cache_data.clear()
            st.rerun()

    loaded_tokens = len([k for k in st.session_state.keys() if k.startswith("loaded_")])
    if loaded_tokens > 0:
        st.caption(f"📦 {loaded_tokens} tokens cached")

    st.divider()
    st.caption("Credit costs:")
    st.caption("• Wallet position: 1")
    st.caption("• Full fetch (229): ~229")


def render_smart_money_content():
    """Render Smart Money main content"""
    st.title("💰 Smart Money on Hyper")
    st.caption("Track smart money positions on Hyperliquid | Powered by Nansen API")

    # Load wallet addresses from wallet_address.txt (229 wallets)
    def load_whale_wallet_list():
        """Load wallet list from wallet_address.txt"""
        csv_path = Path(__file__).parent / "wallet_address.txt"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            return df
        return None

    whale_list = load_whale_wallet_list()
    if whale_list is None:
        st.error("Failed to load wallet_address.txt")
        st.stop()

    # Fetch positions for all wallets from wallet_address.txt
    @st.cache_data(ttl=600, show_spinner=False)
    def fetch_all_whale_positions(_wallet_addresses: tuple):
        """Fetch positions for all 229 wallets - costs 229 credits"""
        all_wallet_data = []
        all_positions = []

        for address, label in _wallet_addresses:
            position_data = nansen_client.get_wallet_positions(address)

            if position_data:
                account_value = float(position_data.get('margin_summary_account_value_usd') or 0)
                total_margin = float(position_data.get('margin_summary_total_margin_used_usd') or 0)

                asset_positions = position_data.get('asset_positions', [])
                wallet_positions = []
                wallet_upnl = 0
                wallet_position_value = 0

                for pos_data in asset_positions:
                    pos = pos_data.get('position', {})
                    token = pos.get('token_symbol', 'Unknown')
                    size = float(pos.get('size') or 0)
                    position_value = float(pos.get('position_value_usd') or 0)
                    upnl = float(pos.get('unrealized_pnl_usd') or 0)
                    leverage = float(pos.get('leverage_value') or 1)
                    entry_price = float(pos.get('entry_price_usd') or 0)

                    side = "Long" if size > 0 else "Short"

                    wallet_positions.append({
                        'token': token,
                        'side': side,
                        'size': abs(size),
                        'position_value': position_value,
                        'upnl': upnl,
                        'leverage': leverage,
                        'entry_price': entry_price,
                    })

                    all_positions.append({
                        'address': address,
                        'label': label,
                        'token': token,
                        'side': side,
                        'position_value': position_value,
                        'upnl': upnl,
                    })

                    wallet_upnl += upnl
                    wallet_position_value += position_value

                # Calculate wallet leverage
                wallet_leverage = wallet_position_value / max(account_value, 1) if account_value > 0 else 0

                all_wallet_data.append({
                    'address': address,
                    'label': label,
                    'account_value': account_value,
                    'position_value': wallet_position_value,
                    'leverage': wallet_leverage,
                    'total_pnl': wallet_upnl,
                    'positions': wallet_positions,
                    'position_count': len(wallet_positions),
                })

        return all_wallet_data, all_positions

    # Convert to tuple for caching (list is not hashable)
    wallet_addresses = tuple(
        (row['trader_address'], row['trader_address_label'])
        for _, row in whale_list.iterrows()
    )

    # Check if we need to fetch (button or first load)
    if 'whale_positions_loaded' not in st.session_state:
        st.session_state.whale_positions_loaded = False

    # Show fetch button if not loaded
    if not st.session_state.whale_positions_loaded:
        st.warning(f"📊 Ready to fetch positions for **{len(wallet_addresses)} wallets** from wallet_address.txt")
        st.caption(f"⚠️ This will cost approximately **{len(wallet_addresses)} credits** (1 credit per wallet)")

        if st.button("🚀 Fetch All Whale Positions", type="primary"):
            with st.spinner(f"Fetching positions for {len(wallet_addresses)} wallets... (this may take a while)"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Fetch with progress tracking
                all_wallet_data = []
                all_positions = []

                for idx, (address, label) in enumerate(wallet_addresses):
                    position_data = nansen_client.get_wallet_positions(address)

                    if position_data:
                        account_value = float(position_data.get('margin_summary_account_value_usd') or 0)
                        asset_positions = position_data.get('asset_positions', [])
                        wallet_upnl = 0
                        wallet_position_value = 0
                        wallet_positions = []

                        for pos_data in asset_positions:
                            pos = pos_data.get('position', {})
                            token = pos.get('token_symbol', 'Unknown')
                            size = float(pos.get('size') or 0)
                            position_value = float(pos.get('position_value_usd') or 0)
                            upnl = float(pos.get('unrealized_pnl_usd') or 0)
                            leverage = float(pos.get('leverage_value') or 1)

                            side = "Long" if size > 0 else "Short"

                            wallet_positions.append({
                                'token': token,
                                'side': side,
                                'position_value': position_value,
                                'upnl': upnl,
                                'leverage': leverage,
                            })

                            all_positions.append({
                                'address': address,
                                'label': label,
                                'token': token,
                                'side': side,
                                'position_value': position_value,
                                'upnl': upnl,
                            })

                            wallet_upnl += upnl
                            wallet_position_value += position_value

                        wallet_leverage = wallet_position_value / max(account_value, 1) if account_value > 0 else 0

                        all_wallet_data.append({
                            'address': address,
                            'label': label,
                            'account_value': account_value,
                            'position_value': wallet_position_value,
                            'leverage': wallet_leverage,
                            'total_pnl': wallet_upnl,
                            'positions': wallet_positions,
                            'position_count': len(wallet_positions),
                        })

                    progress_bar.progress((idx + 1) / len(wallet_addresses))
                    status_text.text(f"Fetched {idx + 1}/{len(wallet_addresses)} wallets...")

                progress_bar.empty()
                status_text.empty()

                st.session_state.whale_wallet_data = all_wallet_data
                st.session_state.whale_all_positions = all_positions
                st.session_state.whale_positions_loaded = True
                st.rerun()

        st.stop()

    # Get cached data
    all_wallet_data = st.session_state.get('whale_wallet_data', [])
    all_positions = st.session_state.get('whale_all_positions', [])

    if not all_wallet_data:
        st.error("No wallet data loaded. Please fetch again.")
        if st.button("🔄 Reset and Fetch Again"):
            st.session_state.whale_positions_loaded = False
            st.rerun()
        st.stop()

    # Create DataFrame from fetched data
    wallet_df = pd.DataFrame(all_wallet_data)

    # Add size cohort and ROI
    wallet_df['size_cohort'] = wallet_df['account_value'].apply(calculate_size_cohort)
    wallet_df['roi'] = (wallet_df['total_pnl'] / wallet_df['account_value'].replace(0, 1) * 100).round(2)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tracked Whales", len(wallet_df))
    with col2:
        total_position = wallet_df['position_value'].sum()
        st.metric("Total Position", format_currency(total_position, compact=True))
    with col3:
        total_pnl = wallet_df['total_pnl'].sum()
        st.metric("Total PnL", format_currency(total_pnl, compact=True))
    with col4:
        avg_leverage = wallet_df['leverage'].mean()
        st.metric("Avg Leverage", f"{avg_leverage:.2f}x")

    st.divider()

    # ==================== EXTREMELY PROFITABLE POSITIONING ====================
    # Calculate from REAL data (all_positions from 229 wallets)

    token_summary = {}
    profit_wallets = 0
    loss_wallets = 0

    if all_positions:
        positions_df = pd.DataFrame(all_positions)

        # Calculate token summary from real data
        token_summary = {}
        for token in positions_df['token'].unique():
            token_positions = positions_df[positions_df['token'] == token]
            long_positions = token_positions[token_positions['side'] == 'Long']
            short_positions = token_positions[token_positions['side'] == 'Short']

            total_long_value = long_positions['position_value'].sum()
            total_short_value = short_positions['position_value'].sum()
            total_long_upnl = long_positions['upnl'].sum()
            total_short_upnl = short_positions['upnl'].sum()
            total_value = total_long_value + total_short_value
            long_pct = (total_long_value / max(total_value, 1)) * 100

            token_summary[token] = {
                'long_value': total_long_value,
                'short_value': total_short_value,
                'long_pct': long_pct,
                'upnl': total_long_upnl + total_short_upnl,
                'long_count': len(long_positions),
                'short_count': len(short_positions),
            }

        # Count wallets in profit vs loss (by wallet, not by position)
        wallet_pnl = wallet_df.groupby('address')['total_pnl'].sum() if 'address' in wallet_df.columns else wallet_df['total_pnl']
        profit_wallets = len(wallet_df[wallet_df['total_pnl'] > 0])
        loss_wallets = len(wallet_df[wallet_df['total_pnl'] <= 0])

    if token_summary:
        # Calculate overall positioning
        total_long = sum(t['long_value'] for t in token_summary.values())
        total_short = sum(t['short_value'] for t in token_summary.values())
        overall_long_pct = (total_long / max(total_long + total_short, 1)) * 100
        # Use actual wallet count from wallet_df (229 wallets from wallet_address.txt)
        total_wallets = len(wallet_df)
        profit_pct = (profit_wallets / max(profit_wallets + loss_wallets, 1)) * 100

        # Determine sentiment
        if overall_long_pct >= 70:
            sentiment = "VERY BULLISH"
            sentiment_color = "#22c55e"
        elif overall_long_pct >= 55:
            sentiment = "SLIGHTLY BULLISH"
            sentiment_color = "#22c55e"
        elif overall_long_pct >= 45:
            sentiment = "NEUTRAL"
            sentiment_color = "#9ca3af"
        elif overall_long_pct >= 30:
            sentiment = "SLIGHTLY BEARISH"
            sentiment_color = "#ef4444"
        else:
            sentiment = "VERY BEARISH"
            sentiment_color = "#ef4444"

        def get_token_sentiment(long_pct):
            if long_pct >= 70:
                return "Very Bullish", "#166534"
            elif long_pct >= 55:
                return "Bullish", "#166534"
            elif long_pct >= 45:
                return "Neutral", "#374151"
            elif long_pct >= 30:
                return "Bit Bearish", "#92400e"
            else:
                return "Bearish", "#991b1b"

        # Layout: Left sidebar | Center chart | Right token cards
        col_left, col_center, col_right = st.columns([1, 2, 1.5])

        with col_left:
            # Extremely Profitable card - using native Streamlit
            st.markdown("### 🐋 Extremely Profitable")
            if overall_long_pct >= 50:
                st.markdown(f":green[{sentiment}] ↗")
            else:
                st.markdown(f":red[{sentiment}] ↘")

            st.caption("NOTIONAL")
            notional_cols = st.columns(2)
            with notional_cols[0]:
                st.markdown(f":green[{format_currency(total_long, compact=True)}]")
            with notional_cols[1]:
                st.markdown(f":red[{format_currency(total_short, compact=True)}]")
            st.progress(overall_long_pct / 100)
            st.caption(f"{overall_long_pct:.0f}% LONG | {100-overall_long_pct:.0f}% SHORT")

            st.caption("UNREALIZED PNL")
            pnl_cols = st.columns(2)
            with pnl_cols[0]:
                st.markdown(f":green[{profit_pct:.1f}%]")
            with pnl_cols[1]:
                st.markdown(f":red[{100-profit_pct:.1f}%]")
            st.progress(profit_pct / 100)
            st.caption(f"{profit_pct:.0f}% IN PROFIT | {100-profit_pct:.0f}% IN LOSS")

        with col_center:
            st.markdown("### Extremely Profitable Positioning")
            st.caption(f"Current positions - {sentiment}")
            if overall_long_pct >= 50:
                st.markdown(f"## :green[{overall_long_pct:.1f}% Long]")
            else:
                st.markdown(f"## :red[{overall_long_pct:.1f}% Long]")

            # Stats
            stat_cols = st.columns(2)
            with stat_cols[0]:
                st.metric("WALLETS", total_wallets)
            with stat_cols[1]:
                st.metric("MARKETS", len(token_summary))

        with col_right:
            # Sort tokens by UPNL
            sorted_tokens = sorted(token_summary.items(), key=lambda x: abs(x[1]['upnl']), reverse=True)

            # Display all tokens in grid
            for idx, (token, data) in enumerate(sorted_tokens[:8]):
                sentiment_label, bg_color = get_token_sentiment(data['long_pct'])
                upnl = data['upnl']
                upnl_str = f"+{format_currency(upnl, compact=True)}" if upnl >= 0 else format_currency(upnl, compact=True)

                if idx < 2:
                    # Larger cards for top 2
                    if idx == 0:
                        top_cols = st.columns(2)
                    with top_cols[idx]:
                        if data['long_pct'] >= 50:
                            st.success(f"**💎 {token}**\n\n{upnl_str} UPNL\n\n{sentiment_label}")
                        else:
                            st.error(f"**💎 {token}**\n\n{upnl_str} UPNL\n\n{sentiment_label}")
                else:
                    # Smaller cards for rest
                    if idx == 2 or idx == 4 or idx == 6:
                        small_cols = st.columns(2)
                    col_idx = (idx - 2) % 2
                    with small_cols[col_idx]:
                        if data['long_pct'] >= 50:
                            st.success(f"💎 **{token}** | {upnl_str} | {sentiment_label}")
                        elif data['long_pct'] >= 40:
                            st.warning(f"💎 **{token}** | {upnl_str} | {sentiment_label}")
                        else:
                            st.error(f"💎 **{token}** | {upnl_str} | {sentiment_label}")
    else:
        st.info("📊 No open positions found. Wallets may not have any active perp positions.")

    st.divider()

    # Tabs
    tab1, tab2 = st.tabs(["📊 Whale Leaderboard", "📈 Token Positions"])

    with tab1:
        st.subheader(f"Whale Traders ({len(wallet_df)} wallets from wallet_address.txt)")
        st.caption("Click 👁️ to view real-time positions")

        for idx, row in wallet_df.iterrows():
            with st.container():
                cols = st.columns([4, 2, 1.5, 2, 2, 1.5, 1])

                with cols[0]:
                    st.markdown(f"**{row['label']}**")
                    st.caption(f"{row['size_cohort']} | `{truncate_address(row['address'])}`")

                with cols[1]:
                    st.markdown("**Position Value**")
                    st.markdown(format_currency(row['position_value'], compact=True))

                with cols[2]:
                    st.markdown("**Leverage**")
                    st.markdown(f"{row['leverage']:.2f}x")

                with cols[3]:
                    pnl = row['total_pnl']
                    st.markdown("**Total PnL**")
                    if pnl >= 0:
                        st.markdown(f":green[+{format_currency(pnl, compact=True)}]")
                    else:
                        st.markdown(f":red[{format_currency(pnl, compact=True)}]")

                with cols[4]:
                    roi = row['roi']
                    st.markdown("**ROI**")
                    if roi >= 0:
                        st.markdown(f":green[+{roi:.1f}%]")
                    else:
                        st.markdown(f":red[{roi:.1f}%]")

                with cols[5]:
                    st.markdown("**Cohort**")
                    st.markdown(row['size_cohort'])

                with cols[6]:
                    if st.button("👁️", key=f"view_{idx}", help="View positions"):
                        show_position_dialog(row.to_dict())

                st.divider()

    with tab2:
        st.subheader("Token Position Analysis")

        col_title, col_reload = st.columns([4, 1])
        with col_title:
            st.caption("Click on token to expand positions")
        with col_reload:
            if st.button("🔄 Reload All", key="reload_all_tokens"):
                # Clear loaded flags
                keys_to_delete = [k for k in st.session_state.keys() if k.startswith("loaded_")]
                for k in keys_to_delete:
                    del st.session_state[k]
                # Clear persistent cache for token positions
                cached_get_token_positions.clear()
                st.rerun()

        # Get tokens from token_summary (sorted by UPNL), fallback to default list
        if token_summary:
            # Sort by absolute UPNL value (highest first)
            tokens = sorted(token_summary.keys(), key=lambda t: abs(token_summary[t]['upnl']), reverse=True)
        else:
            tokens = ["BTC", "ETH", "SOL", "ARB", "DOGE", "AVAX", "LINK", "OP", "APT", "SUI"]

        for token in tokens:
            # Check session state for UI state (whether user has loaded this token)
            loaded_key = f"loaded_{token}"
            is_loaded = st.session_state.get(loaded_key, False)
            positions = None

            if is_loaded:
                # Use persistent cache (survives tab switches)
                positions = cached_get_token_positions(token)
                is_cached = True
            else:
                is_cached = False

            if positions:
                long_positions = [p for p in positions if p.get('side') == 'Long']
                short_positions = [p for p in positions if p.get('side') == 'Short']
                total_long = sum(float(p.get('position_value_usd') or 0) for p in long_positions)
                total_short = sum(float(p.get('position_value_usd') or 0) for p in short_positions)
                total_value = total_long + total_short
                ratio = total_long / max(total_value, 1) * 100
                bias_icon = "🟢" if ratio > 55 else "🔴" if ratio < 45 else "⚪"
                cache_icon = "📦" if is_cached else ""
                title = f"{token} | {format_currency(total_value, compact=True)} | {bias_icon} L:{ratio:.0f}% {cache_icon}"
            elif token in token_summary:
                # Use token_summary data to show UPNL and sentiment
                ts = token_summary[token]
                upnl = ts['upnl']
                long_pct = ts['long_pct']
                # Determine sentiment based on long_pct
                if long_pct >= 70:
                    sentiment = "Very Bullish"
                elif long_pct >= 55:
                    sentiment = "Bullish"
                elif long_pct >= 45:
                    sentiment = "Neutral"
                elif long_pct >= 30:
                    sentiment = "Bit Bearish"
                else:
                    sentiment = "Bearish"
                upnl_str = f"+{format_currency(upnl, compact=True)}" if upnl >= 0 else format_currency(upnl, compact=True)
                title = f"💎 {token} | {upnl_str} UPNL | {sentiment}"
            else:
                title = f"{token} | Click to load"

            with st.expander(title, expanded=False):
                if not positions:
                    with st.spinner(f"Loading {token} positions..."):
                        positions = cached_get_token_positions(token)
                    if positions:
                        st.session_state[loaded_key] = True
                    else:
                        st.warning(f"No positions found for {token}")
                        continue

                long_positions = [p for p in positions if p.get('side') == 'Long']
                short_positions = [p for p in positions if p.get('side') == 'Short']
                total_long = sum(float(p.get('position_value_usd') or 0) for p in long_positions)
                total_short = sum(float(p.get('position_value_usd') or 0) for p in short_positions)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Long", format_currency(total_long, compact=True), f"{len(long_positions)} traders")
                with col2:
                    st.metric("Short", format_currency(total_short, compact=True), f"{len(short_positions)} traders")
                with col3:
                    ratio = total_long / max(total_long + total_short, 1) * 100
                    bias = "Bullish" if ratio > 55 else "Bearish" if ratio < 45 else "Neutral"
                    st.metric("Long %", f"{ratio:.1f}%", bias)
                with col4:
                    st.metric("Status", "📦 Cached" if is_cached else "🔴 Live")

                st.divider()

                for idx, pos in enumerate(positions[:20]):
                    side = pos.get('side', 'Unknown')
                    side_emoji = "🟢" if side == "Long" else "🔴"
                    address = pos.get('address') or ''
                    label = pos.get('address_label') or truncate_address(address)
                    position_value = float(pos.get('position_value_usd') or 0)
                    leverage_str = pos.get('leverage') or '1X'
                    try:
                        leverage_val = float(str(leverage_str).replace('X', '').replace('x', ''))
                    except:
                        leverage_val = 1.0
                    upnl = float(pos.get('upnl_usd') or 0)

                    cols = st.columns([4, 2, 1.5, 2, 1])

                    with cols[0]:
                        st.markdown(f"**{label}**")
                        st.caption(f"{side_emoji} {side} | `{truncate_address(address)}`")

                    with cols[1]:
                        st.markdown("**Position Value**")
                        st.markdown(format_currency(position_value, compact=True))

                    with cols[2]:
                        st.markdown("**Leverage**")
                        st.markdown(f"{leverage_val:.2f}x")

                    with cols[3]:
                        st.markdown("**uPnL**")
                        if upnl >= 0:
                            st.markdown(f":green[+{format_currency(upnl, compact=True)}]")
                        else:
                            st.markdown(f":red[{format_currency(upnl, compact=True)}]")

                    with cols[4]:
                        if st.button("👁️", key=f"{token}_view_{idx}", help="View wallet"):
                            show_position_dialog({'address': address, 'label': label})

                if len(positions) > 20:
                    st.caption(f"Showing 20 of {len(positions)} positions")

    # Footer
    st.markdown("---")
    tracker = get_usage_tracker()
    st.markdown(f"Data: [Nansen](https://nansen.ai) | Session: **{tracker.total_credits_used}** credits | Built with Streamlit")


# ==================== WHALE SCREENER (HYPERLIQUID) DASHBOARD ====================

def load_wallet_addresses():
    """Load wallet addresses from CSV file."""
    csv_path = Path(__file__).parent / "wallet_address.txt"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        return df
    return None


def create_screening_chart(df: pd.DataFrame, metric: str = "value", height: int = 800, mode: str = "value"):
    """Create a stacked horizontal bar chart for all wallets."""
    if metric == "value":
        perp_col, spot_col, label = "perp_value", "spot_value", "Account Value"
    elif metric == "pnl":
        perp_col, spot_col, label = "perp_pnl", "spot_pnl", "PnL"
    else:
        perp_col, spot_col, label = "perp_volume", "spot_volume", "Volume"

    fig = go.Figure()

    if mode == "percentage":
        df = df.copy()
        total = df[perp_col].abs() + df[spot_col].abs()
        total = total.replace(0, 1)
        perp_pct = (df[perp_col].abs() / total * 100).round(1)
        spot_pct = (df[spot_col].abs() / total * 100).round(1)

        fig.add_trace(go.Bar(
            name="Perp",
            y=df["display_name"],
            x=perp_pct,
            orientation="h",
            marker=dict(color=COLORS["perp"]),
        ))

        fig.add_trace(go.Bar(
            name="Spot",
            y=df["display_name"],
            x=spot_pct,
            orientation="h",
            marker=dict(color=COLORS["spot"]),
        ))

        title_text = f"Portfolio Allocation (Perp vs Spot %)"
        x_range = [0, 100]
    else:
        fig.add_trace(go.Bar(
            name="Perp",
            y=df["display_name"],
            x=df[perp_col],
            orientation="h",
            marker=dict(color=COLORS["perp"]),
            hovertemplate="<b>%{y}</b><br>Perp: %{x:$,.0f}<extra></extra>",
        ))

        fig.add_trace(go.Bar(
            name="Spot",
            y=df["display_name"],
            x=df[spot_col],
            orientation="h",
            marker=dict(color=COLORS["spot"]),
            hovertemplate="<b>%{y}</b><br>Spot: %{x:$,.0f}<extra></extra>",
        ))

        title_text = f"Portfolio Breakdown by {label}"
        x_range = None

    fig.update_layout(
        barmode="stack",
        height=height,
        margin=dict(l=250, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text"]),
        title=dict(text=title_text, font=dict(size=18, color=COLORS["text"]), x=0.5),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor=COLORS["grid"], zeroline=False, range=x_range),
        yaxis=dict(showgrid=False, autorange="reversed", tickfont=dict(size=10)),
    )

    return fig


def create_value_perp_heatmap(df: pd.DataFrame):
    """Create heatmap: Account Value (X) vs Perp % (Y)"""
    value_bins = [0, 1e6, 5e6, 10e6, 50e6, 100e6, float('inf')]
    value_labels = ['<$1M', '$1-5M', '$5-10M', '$10-50M', '$50-100M', '>$100M']

    perp_bins = [0, 20, 40, 60, 80, 100.1]
    perp_labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']

    df['value_bin'] = pd.cut(df['total_value'], bins=value_bins, labels=value_labels)
    df['perp_bin'] = pd.cut(df['perp_pct'], bins=perp_bins, labels=perp_labels)

    heatmap_data = df.groupby(['perp_bin', 'value_bin'], observed=True).size().unstack(fill_value=0)
    heatmap_data = heatmap_data.reindex(index=perp_labels, columns=value_labels, fill_value=0)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=value_labels,
        y=perp_labels,
        colorscale=HEATMAP_COLORSCALE,
        hovertemplate="Value: %{x}<br>Perp %: %{y}<br>Wallets: %{z}<extra></extra>",
        text=heatmap_data.values,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
    ))

    fig.update_layout(
        title=dict(text="Distribution: Account Value vs Perp Allocation", font=dict(size=18, color=COLORS["text"]), x=0.5),
        xaxis_title="Account Value",
        yaxis_title="Perp Allocation %",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text"]),
        xaxis=dict(tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
    )
    return fig


def create_entity_perp_heatmap(df: pd.DataFrame):
    """Create heatmap: Entity Type (X) vs Perp % (Y), color = Total AUM"""
    perp_bins = [0, 20, 40, 60, 80, 100.1]
    perp_labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']

    df['perp_bin'] = pd.cut(df['perp_pct'], bins=perp_bins, labels=perp_labels)
    heatmap_data = df.groupby(['perp_bin', 'entity'], observed=True)['total_value'].sum().unstack(fill_value=0)
    entities = df['entity'].unique().tolist()
    heatmap_data = heatmap_data.reindex(index=perp_labels, columns=sorted(entities), fill_value=0)

    display_text = (heatmap_data / 1e6).round(1).astype(str) + 'M'
    display_text = display_text.replace('0.0M', '-')

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=sorted(entities),
        y=perp_labels,
        colorscale=HEATMAP_COLORSCALE,
        hovertemplate="Entity: %{x}<br>Perp %: %{y}<br>AUM: $%{z:,.0f}<extra></extra>",
        text=display_text.values,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
    ))

    fig.update_layout(
        title=dict(text="Distribution: Entity Type vs Perp Allocation (AUM)", font=dict(size=18, color=COLORS["text"]), x=0.5),
        xaxis_title="Entity Type",
        yaxis_title="Perp Allocation %",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text"]),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
    )
    return fig


def create_value_pnl_heatmap(df: pd.DataFrame):
    """Create heatmap: Account Value (X) vs PnL (Y)"""
    value_bins = [0, 1e6, 5e6, 10e6, 50e6, 100e6, float('inf')]
    value_labels = ['<$1M', '$1-5M', '$5-10M', '$10-50M', '$50-100M', '>$100M']

    pnl_bins = [-float('inf'), -1e6, -100e3, 0, 100e3, 1e6, 10e6, float('inf')]
    pnl_labels = ['<-$1M', '-$1M to -$100K', '-$100K to $0', '$0 to $100K', '$100K to $1M', '$1M to $10M', '>$10M']

    df['value_bin'] = pd.cut(df['total_value'], bins=value_bins, labels=value_labels)
    df['pnl_bin'] = pd.cut(df['total_pnl'], bins=pnl_bins, labels=pnl_labels)

    heatmap_data = df.groupby(['pnl_bin', 'value_bin'], observed=True).size().unstack(fill_value=0)
    heatmap_data = heatmap_data.reindex(index=pnl_labels, columns=value_labels, fill_value=0)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=value_labels,
        y=pnl_labels,
        colorscale=HEATMAP_COLORSCALE,
        hovertemplate="Value: %{x}<br>PnL: %{y}<br>Wallets: %{z}<extra></extra>",
        text=heatmap_data.values,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
    ))

    fig.update_layout(
        title=dict(text="Distribution: Account Value vs PnL", font=dict(size=18, color=COLORS["text"]), x=0.5),
        xaxis_title="Account Value",
        yaxis_title="PnL Range",
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text"]),
        xaxis=dict(tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    return fig


def create_histogram(df: pd.DataFrame, column: str, title: str, bins: int = 20):
    """Create a histogram for distribution analysis."""
    fig = go.Figure(data=go.Histogram(
        x=df[column],
        nbinsx=bins,
        marker=dict(color=COLORS["perp"], line=dict(color=COLORS["spot"], width=1)),
        hovertemplate=f"{title}: %{{x}}<br>Count: %{{y}}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=f"Distribution of {title}", font=dict(size=16, color=COLORS["text"]), x=0.5),
        xaxis_title=title,
        yaxis_title="Number of Wallets",
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text"]),
        xaxis=dict(showgrid=True, gridcolor=COLORS["grid"]),
        yaxis=dict(showgrid=True, gridcolor=COLORS["grid"]),
        bargap=0.1,
    )
    return fig


def create_activity_legend():
    """Create legend for activity calendar with 4 trade types."""
    return """
    <div style="display: flex; align-items: center; gap: 15px; margin: 10px 0; flex-wrap: wrap;">
        <span style="color: #22c55e;">🟢 Open Long</span>
        <span style="color: #3b82f6;">🔵 Close Long</span>
        <span style="color: #ef4444;">🔴 Open Short</span>
        <span style="color: #eab308;">🟠 Close Short</span>
        <span style="color: #6b7280;">⬛ No activity</span>
    </div>
    """


def render_date_details_popup(fills_df: pd.DataFrame, selected_date: str):
    """Render popup showing detailed transaction info for a specific date."""
    if fills_df is None or len(fills_df) == 0:
        st.warning(f"No data available for {selected_date}")
        return

    fills_df = fills_df.copy()
    fills_df['date'] = pd.to_datetime(fills_df['timestamp']).dt.date
    fills_df['volume'] = fills_df['size'] * fills_df['price']
    selected_date_obj = pd.to_datetime(selected_date).date()
    day_fills = fills_df[fills_df['date'] == selected_date_obj]

    if len(day_fills) == 0:
        st.info(f"📅 **{selected_date}** - No trades on this date")
        return

    total_volume = day_fills['volume'].sum()

    def format_vol(v):
        if v >= 1_000_000:
            return f"${v/1_000_000:.2f}M"
        elif v >= 1_000:
            return f"${v/1_000:.1f}K"
        else:
            return f"${v:.0f}"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 12px; padding: 20px; margin-bottom: 16px; border: 1px solid #3b82f6;">
        <h3 style="margin: 0; color: #f1f5f9; font-size: 20px;">📅 Transaction Details: {selected_date}</h3>
        <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 14px;">{len(day_fills)} trades | Total Volume: {format_vol(total_volume)}</p>
    </div>
    """, unsafe_allow_html=True)

    open_long_vol = day_fills[day_fills['direction'] == 'Open Long']['volume'].sum()
    close_long_vol = day_fills[day_fills['direction'] == 'Close Long']['volume'].sum()
    open_short_vol = day_fills[day_fills['direction'] == 'Open Short']['volume'].sum()
    close_short_vol = day_fills[day_fills['direction'] == 'Close Short']['volume'].sum()
    day_pnl = day_fills['pnl'].sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📊 Total Volume", format_vol(total_volume))
    with col2:
        st.metric("🟢 Open Long", format_vol(open_long_vol))
    with col3:
        st.metric("🔵 Close Long", format_vol(close_long_vol))
    with col4:
        st.metric("🔴 Open Short", format_vol(open_short_vol))
    with col5:
        st.metric("🟠 Close Short", format_vol(close_short_vol))

    st.metric("💰 Day PnL", hl_format_currency(day_pnl))

    if 'wallet' in day_fills.columns:
        st.markdown("### 👛 Wallets with Activity")
        wallet_summary = day_fills.groupby('wallet').agg({
            'coin': 'count',
            'volume': 'sum',
            'pnl': 'sum',
            'direction': lambda x: list(x.value_counts().head(2).index)
        }).reset_index()
        wallet_summary.columns = ['Wallet', 'Trades', 'Volume', 'PnL', 'Top Directions']
        wallet_summary = wallet_summary.sort_values('Volume', ascending=False)
        wallet_summary['Volume'] = wallet_summary['Volume'].apply(lambda x: format_vol(x))
        wallet_summary['PnL'] = wallet_summary['PnL'].apply(lambda x: hl_format_currency(x))
        wallet_summary['Top Directions'] = wallet_summary['Top Directions'].apply(lambda x: ', '.join(x))
        st.dataframe(wallet_summary, hide_index=True, use_container_width=True)

    st.markdown("### 🪙 Trading Pairs")
    coin_summary = day_fills.groupby('coin').agg({
        'direction': 'count',
        'volume': 'sum',
        'pnl': 'sum',
        'size': 'sum'
    }).reset_index()
    coin_summary.columns = ['Coin', 'Trades', 'Volume', 'PnL', 'Total Size']
    coin_summary = coin_summary.sort_values('Volume', ascending=False)
    coin_summary['Volume'] = coin_summary['Volume'].apply(lambda x: format_vol(x))
    coin_summary['PnL'] = coin_summary['PnL'].apply(lambda x: hl_format_currency(x))
    coin_summary['Total Size'] = coin_summary['Total Size'].apply(lambda x: f"{x:,.4f}")
    st.dataframe(coin_summary, hide_index=True, use_container_width=True)


def create_activity_calendar_range(fills_df: pd.DataFrame, from_date, to_date):
    """Create a single combined activity calendar heatmap for a date range."""
    if isinstance(from_date, int):
        start_date = datetime(from_date, 1, 1)
    elif hasattr(from_date, 'year'):
        start_date = datetime(from_date.year, from_date.month, from_date.day)
    else:
        start_date = from_date

    if isinstance(to_date, int):
        end_date = datetime(to_date, 12, 31)
    elif hasattr(to_date, 'year'):
        end_date = datetime(to_date.year, to_date.month, to_date.day)
    else:
        end_date = to_date

    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    total_days = (end_date - start_date).days + 1
    num_weeks = (total_days // 7) + 2
    num_days = 7

    open_long_volume = np.zeros((num_days, num_weeks))
    close_long_volume = np.zeros((num_days, num_weeks))
    open_short_volume = np.zeros((num_days, num_weeks))
    close_short_volume = np.zeros((num_days, num_weeks))

    date_to_coords = {}
    coords_to_date = {}  # Reverse mapping for hover text
    for d in all_dates:
        day_of_week = d.dayofweek
        week_of_range = (d - start_date).days // 7
        if week_of_range < num_weeks:
            date_to_coords[d.date()] = (day_of_week, week_of_range)
            coords_to_date[(day_of_week, week_of_range)] = d.date()

    if len(fills_df) > 0:
        fills_df = fills_df.copy()
        fills_df['date'] = pd.to_datetime(fills_df['timestamp']).dt.date
        fills_df['volume'] = fills_df['size'] * fills_df['price']

        for _, row in fills_df.iterrows():
            trade_date = row['date']
            if trade_date in date_to_coords:
                day_idx, week_idx = date_to_coords[trade_date]
                direction = row['direction']
                trade_volume = row['volume']
                if direction == 'Open Long':
                    open_long_volume[day_idx, week_idx] += trade_volume
                elif direction == 'Close Long':
                    close_long_volume[day_idx, week_idx] += trade_volume
                elif direction == 'Open Short':
                    open_short_volume[day_idx, week_idx] += trade_volume
                elif direction == 'Close Short':
                    close_short_volume[day_idx, week_idx] += trade_volume

    activity_colorscale = [
        [0.00, "#fca5a5"], [0.10, "#fca5a5"],
        [0.10, "#ef4444"], [0.20, "#ef4444"],
        [0.20, "#fde047"], [0.30, "#fde047"],
        [0.30, "#eab308"], [0.40, "#eab308"],
        [0.40, "#0a0a0a"], [0.50, "#0a0a0a"],
        [0.50, "#93c5fd"], [0.60, "#93c5fd"],
        [0.60, "#3b82f6"], [0.70, "#3b82f6"],
        [0.70, "#86efac"], [0.80, "#86efac"],
        [0.80, "#22c55e"], [1.00, "#22c55e"],
    ]

    display_values = np.full((num_days, num_weeks), 0.45)
    volume_data = {}

    for i in range(num_days):
        for j in range(num_weeks):
            ol = open_long_volume[i, j]
            cl = close_long_volume[i, j]
            os = open_short_volume[i, j]
            cs = close_short_volume[i, j]
            total_volume = ol + cl + os + cs

            volume_data[(i, j)] = {'ol': ol, 'cl': cl, 'os': os, 'cs': cs, 'total': total_volume}

            if total_volume == 0:
                display_values[i, j] = 0.45
            else:
                max_volume = max(ol, cl, os, cs)
                is_strong = (max_volume / total_volume) > 0.5
                if ol == max_volume:
                    display_values[i, j] = 0.90 if is_strong else 0.75
                elif cl == max_volume:
                    display_values[i, j] = 0.65 if is_strong else 0.55
                elif cs == max_volume:
                    display_values[i, j] = 0.35 if is_strong else 0.25
                else:
                    display_values[i, j] = 0.15 if is_strong else 0.05

    hover_text = []
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def format_volume(v):
        if v >= 1_000_000:
            return f"${v/1_000_000:.2f}M"
        elif v >= 1_000:
            return f"${v/1_000:.1f}K"
        else:
            return f"${v:.0f}"

    for day_idx in range(num_days):
        row_text = []
        for week_idx in range(num_weeks):
            # Use the reverse mapping to get the correct date
            date_key = (day_idx, week_idx)
            if date_key in coords_to_date:
                date = coords_to_date[date_key]
                vd = volume_data.get((day_idx, week_idx), {'ol': 0, 'cl': 0, 'os': 0, 'cs': 0, 'total': 0})
                ol, cl, os, cs, total_volume = vd['ol'], vd['cl'], vd['os'], vd['cs'], vd['total']

                if total_volume > 0:
                    activities = {'Open Long': (ol, '🟢'), 'Close Long': (cl, '🔵'), 'Open Short': (os, '🔴'), 'Close Short': (cs, '🟠')}
                    dominant_type = max(activities.items(), key=lambda x: x[1][0])
                    dominant_name = dominant_type[0]
                    dominant_volume = dominant_type[1][0]
                    dominant_emoji = dominant_type[1][1]
                    dominant_pct = (dominant_volume / total_volume * 100) if total_volume > 0 else 0
                    star_marker = "⭐ " if total_volume > 10_000_000 else ""
                    row_text.append(f"<b>{star_marker}{date.strftime('%Y-%m-%d')}</b><br>{dominant_emoji} {dominant_name}: {format_volume(dominant_volume)} ({dominant_pct:.0f}%)<br><b>Total Volume: {format_volume(total_volume)}</b>")
                else:
                    row_text.append(f"{date.strftime('%Y-%m-%d')}<br>No activity")
            else:
                row_text.append("")
        hover_text.append(row_text)

    month_labels = []
    month_positions = []
    from_year = start_date.year
    to_year = end_date.year
    for year in range(from_year, to_year + 1):
        for m in range(1, 13):
            try:
                first_day = datetime(year, m, 1)
                if start_date <= first_day <= end_date:
                    week_pos = (first_day - start_date).days // 7
                    label = f"{first_day.strftime('%b')}" if from_year == to_year else f"{first_day.strftime('%b %Y')}"
                    month_labels.append(label)
                    month_positions.append(week_pos)
            except:
                pass

    fig = go.Figure(data=go.Heatmap(
        z=display_values,
        x=list(range(num_weeks)),
        y=day_names,
        colorscale=activity_colorscale,
        showscale=False,
        hoverinfo='text',
        text=hover_text,
        xgap=2,
        ygap=2,
    ))

    date_format = '%d/%m/%Y'
    title_text = f"Key Activity Calendar: {start_date.strftime(date_format)} - {end_date.strftime(date_format)}"

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=18, color=COLORS["text"]), x=0.5),
        height=250,
        margin=dict(l=50, r=20, t=60, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text"]),
        xaxis=dict(tickmode='array', tickvals=month_positions, ticktext=month_labels, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False, autorange='reversed'),
    )
    return fig


def create_all_wallets_heatmap(fills_df: pd.DataFrame, from_date=None, to_date=None, all_wallet_names: list = None):
    """Create a combined heatmap showing all wallets' activity for a date range."""
    if from_date is None:
        start_date = datetime(datetime.now().year, 1, 1)
    elif isinstance(from_date, int):
        start_date = datetime(from_date, 1, 1)
    elif hasattr(from_date, 'year'):
        start_date = datetime(from_date.year, from_date.month, from_date.day)
    else:
        start_date = from_date

    if to_date is None:
        end_date = datetime.now()
    elif isinstance(to_date, int):
        end_date = datetime(to_date, 12, 31)
    elif hasattr(to_date, 'year'):
        end_date = datetime(to_date.year, to_date.month, to_date.day)
    else:
        end_date = to_date

    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')

    if all_wallet_names is not None:
        fills_df = fills_df.copy() if len(fills_df) > 0 else pd.DataFrame()
        if len(fills_df) > 0:
            fills_df['date'] = pd.to_datetime(fills_df['timestamp']).dt.date
            fills_df['volume'] = fills_df['size'] * fills_df['price']
            wallet_volumes = fills_df.groupby('wallet')['volume'].sum()
            wallets_with_activity = wallet_volumes.sort_values(ascending=False).index.tolist()
            wallets_without_activity = [w for w in all_wallet_names if w not in wallets_with_activity]
            wallets = wallets_with_activity + wallets_without_activity
        else:
            wallets = all_wallet_names
    else:
        if len(fills_df) == 0 or 'wallet' not in fills_df.columns:
            return None
        fills_df = fills_df.copy()
        fills_df['date'] = pd.to_datetime(fills_df['timestamp']).dt.date
        fills_df['volume'] = fills_df['size'] * fills_df['price']
        wallet_volumes = fills_df.groupby('wallet')['volume'].sum().sort_values(ascending=False)
        wallets = wallet_volumes.index.tolist()

    num_days_total = len(all_dates)
    num_wallets = len(wallets)

    open_long_volume = np.zeros((num_wallets, num_days_total))
    close_long_volume = np.zeros((num_wallets, num_days_total))
    open_short_volume = np.zeros((num_wallets, num_days_total))
    close_short_volume = np.zeros((num_wallets, num_days_total))

    date_to_idx = {d.date(): i for i, d in enumerate(all_dates)}

    if len(fills_df) > 0 and 'volume' not in fills_df.columns:
        fills_df['volume'] = fills_df['size'] * fills_df['price']

    for wallet_idx, wallet in enumerate(wallets):
        if len(fills_df) > 0:
            wallet_fills = fills_df[fills_df['wallet'] == wallet]
            for _, row in wallet_fills.iterrows():
                trade_date = row['date']
                if trade_date in date_to_idx:
                    day_idx = date_to_idx[trade_date]
                    direction = row['direction']
                    trade_volume = row['volume']
                    if direction == 'Open Long':
                        open_long_volume[wallet_idx, day_idx] += trade_volume
                    elif direction == 'Close Long':
                        close_long_volume[wallet_idx, day_idx] += trade_volume
                    elif direction == 'Open Short':
                        open_short_volume[wallet_idx, day_idx] += trade_volume
                    elif direction == 'Close Short':
                        close_short_volume[wallet_idx, day_idx] += trade_volume

    activity_colorscale = [
        [0.0, "#ef4444"], [0.2, "#ef4444"],
        [0.2, "#eab308"], [0.4, "#eab308"],
        [0.4, "#0a0a0a"], [0.6, "#0a0a0a"],
        [0.6, "#3b82f6"], [0.8, "#3b82f6"],
        [0.8, "#22c55e"], [1.0, "#22c55e"]
    ]

    display_values = np.full((num_wallets, num_days_total), 0.5)
    volume_data = {}

    def format_volume(v):
        if v >= 1_000_000:
            return f"${v/1_000_000:.2f}M"
        elif v >= 1_000:
            return f"${v/1_000:.1f}K"
        else:
            return f"${v:.0f}"

    for i in range(num_wallets):
        for j in range(num_days_total):
            ol = open_long_volume[i, j]
            cl = close_long_volume[i, j]
            os = open_short_volume[i, j]
            cs = close_short_volume[i, j]
            total_volume = ol + cl + os + cs

            volume_data[(i, j)] = {'ol': ol, 'cl': cl, 'os': os, 'cs': cs, 'total': total_volume}

            if total_volume == 0:
                display_values[i, j] = 0.5
            else:
                max_volume = max(ol, cl, os, cs)
                if ol == max_volume:
                    display_values[i, j] = 0.9
                elif cl == max_volume:
                    display_values[i, j] = 0.7
                elif cs == max_volume:
                    display_values[i, j] = 0.3
                else:
                    display_values[i, j] = 0.1

    hover_text = []
    for wallet_idx, wallet in enumerate(wallets):
        row_text = []
        for day_idx, date in enumerate(all_dates):
            vd = volume_data.get((wallet_idx, day_idx), {'ol': 0, 'cl': 0, 'os': 0, 'cs': 0, 'total': 0})
            ol, cl, os, cs, total_volume = vd['ol'], vd['cl'], vd['os'], vd['cs'], vd['total']

            if total_volume > 0:
                activities = {'Open Long': (ol, '🟢'), 'Close Long': (cl, '🔵'), 'Open Short': (os, '🔴'), 'Close Short': (cs, '🟠')}
                dominant_type = max(activities.items(), key=lambda x: x[1][0])
                dominant_name = dominant_type[0]
                dominant_volume = dominant_type[1][0]
                dominant_emoji = dominant_type[1][1]
                dominant_pct = (dominant_volume / total_volume * 100) if total_volume > 0 else 0
                row_text.append(f"<b>{wallet[:25]}</b><br><b>{date.strftime('%b %d, %Y')}</b><br>{dominant_emoji} {dominant_name}: {format_volume(dominant_volume)} ({dominant_pct:.0f}%)<br><b>Total Volume: {format_volume(total_volume)}</b>")
            else:
                row_text.append(f"<b>{wallet[:25]}</b><br><b>{date.strftime('%b %d, %Y')}</b><br><span style='color:#64748b'>No activity</span>")
        hover_text.append(row_text)

    wallet_labels = [w[:32] + "..." if len(w) > 35 else w for w in wallets]

    month_labels = []
    month_positions = []
    from_year = start_date.year
    to_year = end_date.year
    for year in range(from_year, to_year + 1):
        for m in range(1, 13):
            try:
                first_day = datetime(year, m, 1)
                if start_date <= first_day <= end_date:
                    day_idx = (first_day - start_date).days
                    label = f"{first_day.strftime('%b')}" if from_year == to_year else f"{first_day.strftime('%b %y')}"
                    month_labels.append(label)
                    month_positions.append(day_idx + 15)
            except:
                pass

    fig = go.Figure(data=go.Heatmap(
        z=display_values,
        x=list(range(num_days_total)),
        y=wallet_labels,
        colorscale=activity_colorscale,
        showscale=False,
        hoverinfo='text',
        text=hover_text,
        xgap=1,
        ygap=3,
        hoverongaps=False,
    ))

    row_height = 28
    chart_height = max(500, num_wallets * row_height + 120)

    date_format = '%d/%m/%Y'
    title_text = f"<b>📊 Trading Activity Heatmap: {start_date.strftime(date_format)} - {end_date.strftime(date_format)}</b>"

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=20, color="#f1f5f9", family="Inter, sans-serif"), x=0.5, y=0.98),
        height=chart_height,
        margin=dict(l=280, r=30, t=80, b=60),
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter, sans-serif", color="#e2e8f0"),
        xaxis=dict(tickmode='array', tickvals=month_positions, ticktext=month_labels, showgrid=True, gridcolor="rgba(51, 65, 85, 0.3)", zeroline=False, side='top', tickfont=dict(size=10, color="#94a3b8")),
        yaxis=dict(showgrid=True, gridcolor="rgba(51, 65, 85, 0.2)", zeroline=False, tickfont=dict(size=11, color="#cbd5e1")),
        hoverlabel=dict(bgcolor="#1e293b", bordercolor="#334155", font=dict(size=13, color="#f1f5f9", family="Inter, sans-serif")),
    )
    return fig


@st.dialog("Wallet Activity Details", width="large")
def show_wallet_activity_dialog(wallet_name: str, fills_df: pd.DataFrame, from_date, to_date):
    """Display detailed wallet activity in a modal dialog"""
    if fills_df is None or len(fills_df) == 0:
        st.warning("No activity data available")
        return

    # Filter for this wallet
    wallet_fills = fills_df[fills_df['wallet'] == wallet_name].copy()

    if len(wallet_fills) == 0:
        st.info(f"No trades found for **{wallet_name}** in the selected period")
        return

    # Calculate volume
    wallet_fills['volume'] = wallet_fills['size'] * wallet_fills['price']

    # Header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 12px; padding: 20px; margin-bottom: 16px; border: 1px solid #3b82f6;">
        <h2 style="margin: 0; color: #f1f5f9; font-size: 22px;">👛 {wallet_name}</h2>
        <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 14px;">
            {from_date.strftime('%d/%m/%Y')} - {to_date.strftime('%d/%m/%Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Summary metrics
    total_trades = len(wallet_fills)
    total_volume = wallet_fills['volume'].sum()
    total_pnl = wallet_fills['pnl'].sum()
    total_fees = wallet_fills['fee'].sum()

    def format_vol(v):
        if v >= 1_000_000:
            return f"${v/1_000_000:.2f}M"
        elif v >= 1_000:
            return f"${v/1_000:.1f}K"
        else:
            return f"${v:.0f}"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Trades", f"{total_trades:,}")
    with col2:
        st.metric("💵 Volume", format_vol(total_volume))
    with col3:
        pnl_color = "🟢" if total_pnl >= 0 else "🔴"
        st.metric(f"{pnl_color} Realized PnL", hl_format_currency(total_pnl))
    with col4:
        st.metric("💸 Total Fees", format_vol(total_fees))

    st.divider()

    # Trade type breakdown
    open_long = len(wallet_fills[wallet_fills['direction'] == 'Open Long'])
    close_long = len(wallet_fills[wallet_fills['direction'] == 'Close Long'])
    open_short = len(wallet_fills[wallet_fills['direction'] == 'Open Short'])
    close_short = len(wallet_fills[wallet_fills['direction'] == 'Close Short'])

    open_long_vol = wallet_fills[wallet_fills['direction'] == 'Open Long']['volume'].sum()
    close_long_vol = wallet_fills[wallet_fills['direction'] == 'Close Long']['volume'].sum()
    open_short_vol = wallet_fills[wallet_fills['direction'] == 'Open Short']['volume'].sum()
    close_short_vol = wallet_fills[wallet_fills['direction'] == 'Close Short']['volume'].sum()

    st.markdown("### 📈 Trade Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🟢 Open Long", f"{open_long:,}", help=f"Volume: {format_vol(open_long_vol)}")
    with col2:
        st.metric("🔵 Close Long", f"{close_long:,}", help=f"Volume: {format_vol(close_long_vol)}")
    with col3:
        st.metric("🔴 Open Short", f"{open_short:,}", help=f"Volume: {format_vol(open_short_vol)}")
    with col4:
        st.metric("🟠 Close Short", f"{close_short:,}", help=f"Volume: {format_vol(close_short_vol)}")

    st.divider()

    # Activity Calendar for this wallet
    st.markdown("### 📅 Activity Calendar")
    st.markdown(create_activity_legend(), unsafe_allow_html=True)

    wallet_calendar_fig = create_activity_calendar_range(wallet_fills, from_date, to_date)
    st.plotly_chart(wallet_calendar_fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # Two columns: Top Coins and PnL by Coin
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🪙 Top Coins by Trades")
        coin_trades = wallet_fills.groupby('coin').agg({
            'size': 'count',
            'volume': 'sum',
            'pnl': 'sum'
        }).reset_index()
        coin_trades.columns = ['Coin', 'Trades', 'Volume', 'PnL']
        coin_trades = coin_trades.sort_values('Trades', ascending=False).head(10)
        coin_trades['Volume'] = coin_trades['Volume'].apply(format_vol)
        coin_trades['PnL'] = coin_trades['PnL'].apply(lambda x: hl_format_currency(x))
        st.dataframe(coin_trades, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("### 📊 Daily Activity")
        wallet_fills['date'] = pd.to_datetime(wallet_fills['timestamp']).dt.date
        daily_activity = wallet_fills.groupby('date').agg({
            'size': 'count',
            'volume': 'sum',
            'pnl': 'sum'
        }).reset_index()
        daily_activity.columns = ['Date', 'Trades', 'Volume', 'PnL']
        daily_activity = daily_activity.sort_values('Date', ascending=False).head(10)
        daily_activity['Date'] = daily_activity['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        daily_activity['Volume'] = daily_activity['Volume'].apply(format_vol)
        daily_activity['PnL'] = daily_activity['PnL'].apply(lambda x: hl_format_currency(x))
        st.dataframe(daily_activity, hide_index=True, use_container_width=True)

    st.divider()

    # Recent trades
    st.markdown("### 📜 Recent Trades")
    recent_trades = wallet_fills.sort_values('timestamp', ascending=False).head(50).copy()
    recent_trades['timestamp'] = recent_trades['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    recent_trades['size'] = recent_trades['size'].apply(lambda x: f"{x:,.4f}")
    recent_trades['price'] = recent_trades['price'].apply(lambda x: f"${x:,.2f}")
    recent_trades['volume'] = recent_trades['volume'].apply(format_vol)
    recent_trades['pnl'] = recent_trades['pnl'].apply(lambda x: hl_format_currency(x))
    recent_trades['fee'] = recent_trades['fee'].apply(lambda x: f"${x:,.4f}")

    display_cols = ['timestamp', 'coin', 'direction', 'side', 'size', 'price', 'volume', 'pnl', 'fee']
    recent_trades = recent_trades[display_cols]
    recent_trades.columns = ['Time', 'Coin', 'Direction', 'Side', 'Size', 'Price', 'Volume', 'PnL', 'Fee']

    st.dataframe(recent_trades, hide_index=True, use_container_width=True, height=400)


def render_whale_screener_sidebar():
    """Render Whale Screener sidebar"""
    st.header("🐋 Whale Screener")
    st.caption("Hyperliquid Portfolio Analysis")

    st.divider()

    # Load wallet data
    wallets_df = load_wallet_addresses()
    if wallets_df is not None:
        st.metric("Wallets Loaded", len(wallets_df))

        # Entity filter
        entities = ["All"] + sorted(wallets_df["Entity"].unique().tolist())
        selected_entity = st.selectbox("Filter by Entity", entities, key="whale_entity_filter")

        st.divider()

        if st.button("🔄 Fetch Live Data", type="primary", key="whale_fetch"):
            st.session_state.whale_fetch_live = True

        st.divider()
        st.caption("Data source: Hyperliquid API")
    else:
        st.warning("No wallet data found")


def render_whale_screener_content():
    """Render Whale Screener main content with all sections from Greedy68"""
    st.title("🐋 Whale Screener")
    st.caption("Hyperliquid Portfolio Breakdown - Perp vs Spot Analysis")

    wallets_df = load_wallet_addresses()
    if wallets_df is None:
        st.error("Failed to load wallet addresses")
        return

    # Filter by entity
    selected_entity = st.session_state.get("whale_entity_filter", "All")
    if selected_entity != "All":
        filtered_df = wallets_df[wallets_df["Entity"] == selected_entity]
    else:
        filtered_df = wallets_df

    filtered_df = filtered_df.copy()
    filtered_df["display_name"] = filtered_df["trader_address_label"].str[:40]

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Wallets", len(filtered_df))
    with col2:
        # Handle account_value column - might be string with commas or numeric
        if "account_value" in filtered_df.columns:
            try:
                if filtered_df["account_value"].dtype == object:
                    total_value = filtered_df["account_value"].str.replace(",", "").astype(float).sum()
                else:
                    total_value = filtered_df["account_value"].sum()
            except Exception:
                total_value = 0
        else:
            total_value = 0
        st.metric("Total AUM", hl_format_currency(total_value))
    with col3:
        st.metric("VCs", len(filtered_df[filtered_df["Entity"] == "VCs"]) if "Entity" in filtered_df.columns else 0)
    with col4:
        st.metric("Retail", len(filtered_df[filtered_df["Entity"] == "retail"]) if "Entity" in filtered_df.columns else 0)

    st.divider()

    # Check if we should fetch live data
    if st.session_state.get("whale_fetch_live", False):
        st.info("Fetching live portfolio data from Hyperliquid API...")

        hl_client = HyperliquidClient()
        portfolio_data = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        def fetch_portfolio(row):
            address = row["trader_address"]
            breakdown = hl_client.get_portfolio_breakdown(address, period="allTime")
            return {
                "address": address,
                "display_name": row["display_name"],
                "entity": row["Entity"],
                "breakdown": breakdown
            }

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_portfolio, row): idx for idx, row in filtered_df.iterrows()}

            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    if result["breakdown"] and result["breakdown"].total.account_value > 0:
                        portfolio_data.append({
                            "address": result["address"],
                            "display_name": result["display_name"],
                            "entity": result["entity"],
                            "total_value": result["breakdown"].total.account_value,
                            "perp_value": result["breakdown"].perp.account_value,
                            "spot_value": result["breakdown"].spot.account_value,
                            "perp_pnl": result["breakdown"].perp.pnl,
                            "spot_pnl": result["breakdown"].spot.pnl,
                            "total_pnl": result["breakdown"].total.pnl,
                            "perp_pct": (result["breakdown"].perp.account_value / max(result["breakdown"].total.account_value, 1)) * 100,
                            "total_volume": result["breakdown"].total.volume,
                            "perp_volume": result["breakdown"].perp.volume,
                            "spot_volume": result["breakdown"].spot.volume,
                        })
                except Exception:
                    pass

                progress_bar.progress((i + 1) / len(futures))
                status_text.text(f"Fetched {i + 1}/{len(futures)} wallets ({len(portfolio_data)} with data)")

        progress_bar.empty()
        status_text.empty()

        if portfolio_data:
            portfolio_df = pd.DataFrame(portfolio_data)
            portfolio_df = portfolio_df.sort_values("total_value", ascending=False)
            st.session_state.whale_portfolio_df = portfolio_df
            st.success(f"✅ Fetched data for {len(portfolio_data)} wallets")
        else:
            st.error("❌ No data fetched. Try again.")

        st.session_state.whale_fetch_live = False
        st.rerun()

    # Display portfolio data if available
    if "whale_portfolio_df" in st.session_state and len(st.session_state.whale_portfolio_df) > 0:
        portfolio_df = st.session_state.whale_portfolio_df.copy()

        # ==================== SECTION 1: Portfolio Breakdown ====================
        st.subheader("📊 Portfolio Breakdown")
        col_title, col_toggle = st.columns([3, 1])
        with col_toggle:
            chart_mode = st.toggle("Show as %", value=True, help="Toggle between absolute values and percentage allocation")

        chart_height = max(400, len(portfolio_df) * 25)
        display_mode = "percentage" if chart_mode else "value"
        fig = create_screening_chart(portfolio_df, metric="value", height=chart_height, mode=display_mode)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.divider()

        # ==================== SECTION 2: Distribution Maps ====================
        st.subheader("🗺️ Distribution Maps")

        # Value vs Perp % Heatmap
        st.markdown("#### Account Value vs Perp Allocation")
        st.caption("Heatmap showing how many wallets fall into each Value/Perp% bucket")

        col1, col2 = st.columns([2, 1])
        with col1:
            fig = create_value_perp_heatmap(portfolio_df.copy())
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col2:
            st.markdown("##### 📈 Insights")
            high_perp = len(portfolio_df[portfolio_df['perp_pct'] > 80])
            low_perp = len(portfolio_df[portfolio_df['perp_pct'] < 20])
            whales_high_perp = len(portfolio_df[(portfolio_df['total_value'] > 10e6) & (portfolio_df['perp_pct'] > 80)])

            st.metric("High Perp (>80%)", high_perp)
            st.metric("Low Perp (<20%)", low_perp)
            st.metric("Whales >$10M + High Perp", whales_high_perp)

        # Histograms
        col1, col2 = st.columns(2)
        with col1:
            fig = create_histogram(portfolio_df, "perp_pct", "Perp %", bins=10)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with col2:
            fig = create_histogram(portfolio_df, "total_value", "Account Value ($)", bins=15)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.divider()

        # Entity Distribution
        st.markdown("#### 🏢 Entity Type vs Perp Allocation")
        st.caption("Heatmap showing total AUM by entity type and Perp% range")

        col1, col2 = st.columns([2, 1])
        with col1:
            fig = create_entity_perp_heatmap(portfolio_df.copy())
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col2:
            st.markdown("##### 🏢 Entity Summary")
            entity_summary = portfolio_df.groupby('entity').agg({
                'total_value': 'sum',
                'perp_pct': 'mean',
                'address': 'count'
            }).round(1)
            entity_summary.columns = ['Total AUM', 'Avg Perp %', 'Count']
            entity_summary['Total AUM'] = entity_summary['Total AUM'].apply(lambda x: hl_format_currency(x))
            entity_summary['Avg Perp %'] = entity_summary['Avg Perp %'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(entity_summary, use_container_width=True)

        st.divider()

        # Value vs PnL
        st.markdown("#### 💰 Account Value vs PnL")
        st.caption("Heatmap showing wallet distribution by value and profitability")

        col1, col2 = st.columns([2, 1])
        with col1:
            fig = create_value_pnl_heatmap(portfolio_df.copy())
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col2:
            st.markdown("##### 💰 PnL Summary")
            profitable = len(portfolio_df[portfolio_df['total_pnl'] > 0])
            losing = len(portfolio_df[portfolio_df['total_pnl'] < 0])
            total_pnl = portfolio_df['total_pnl'].sum()
            avg_pnl = portfolio_df['total_pnl'].mean()

            st.metric("Profitable Wallets", profitable)
            st.metric("Losing Wallets", losing)
            st.metric("Total PnL", hl_format_currency(total_pnl))
            st.metric("Avg PnL", hl_format_currency(avg_pnl))

        # PnL histogram
        fig = create_histogram(portfolio_df, "total_pnl", "PnL ($)", bins=20)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.divider()

        # ==================== SECTION 3: Key Activity Calendar ====================
        st.subheader("📅 Key Activity Calendar")
        st.caption("GitHub-style heatmap showing trading activity over time")

        # Wallet selector for activity
        col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
        with col1:
            wallet_options = ["📊 All Wallets"] + portfolio_df["display_name"].tolist()
            selected_wallet = st.selectbox("Select Wallet", wallet_options, key="activity_wallet")
        with col2:
            from_date = st.date_input("From Date", value=datetime(datetime.now().year, 1, 1), min_value=datetime(2020, 1, 1), max_value=datetime.now(), key="from_date_input")
        with col3:
            to_date = st.date_input("To Date", value=datetime.now(), min_value=datetime(2020, 1, 1), max_value=datetime.now(), key="to_date_input")
        with col4:
            st.write("")
            fetch_activity = st.button("🔄 Fetch Activity", type="primary", key="fetch_activity_btn")

        if from_date > to_date:
            st.error("⚠️ 'From Date' must be <= 'To Date'")

        # Legend
        st.markdown(create_activity_legend(), unsafe_allow_html=True)

        if fetch_activity and from_date <= to_date:
            is_all_wallets = selected_wallet == "📊 All Wallets"
            from_year = from_date.year
            to_year = to_date.year
            year_range = list(range(from_year, to_year + 1))
            date_label = f"{from_date.strftime('%d/%m/%Y')} - {to_date.strftime('%d/%m/%Y')}"

            if is_all_wallets:
                # Fetch from all wallets
                all_wallets_df = filtered_df.copy()
                total_wallets = len(all_wallets_df)

                progress_bar = st.progress(0)
                status_text = st.empty()

                all_fills = []
                start_time = datetime(from_date.year, from_date.month, from_date.day)
                end_time = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59)

                wallet_list = [(row["trader_address"], row["display_name"]) for _, row in all_wallets_df.iterrows()]

                fetch_stats = {'success': 0, 'empty': 0, 'failed': 0, 'total_trades': 0}

                client = HyperliquidClient()
                max_retries = 3

                status_text.text(f"🔄 Sequential fetching for reliability ({total_wallets} wallets)...")

                for idx, (wallet_address, wallet_name) in enumerate(wallet_list):
                    wallet_fills = []

                    for attempt in range(max_retries):
                        try:
                            fills = client.get_user_fills_paginated(wallet_address, start_time, end_time, max_fills=10000)
                            if fills:
                                wallet_fills = fills
                                break
                            if attempt < max_retries - 1:
                                time.sleep(0.5)
                        except Exception:
                            if attempt < max_retries - 1:
                                time.sleep((attempt + 1) * 1.0)

                    if wallet_fills:
                        fetch_stats['success'] += 1
                        fetch_stats['total_trades'] += len(wallet_fills)
                        for f in wallet_fills:
                            all_fills.append({
                                'wallet': wallet_name,
                                'coin': f.coin,
                                'side': f.side,
                                'direction': f.direction,
                                'size': f.size,
                                'price': f.price,
                                'pnl': f.pnl,
                                'timestamp': f.timestamp,
                                'fee': f.fee
                            })
                    else:
                        fetch_stats['empty'] += 1

                    completed = idx + 1
                    progress_bar.progress(completed / total_wallets)
                    status_text.text(f"🔄 {completed}/{total_wallets} | ✅ {fetch_stats['success']} with data | ⚪ {fetch_stats['empty']} empty | 📊 {fetch_stats['total_trades']} trades")

                progress_bar.empty()
                status_text.empty()

                st.session_state.calendar_years = year_range
                st.session_state.calendar_from_date = from_date
                st.session_state.calendar_to_date = to_date
                st.session_state.activity_mode = "all"
                st.session_state.all_wallet_names = all_wallets_df["display_name"].tolist()

                if all_fills:
                    st.session_state.activity_fills = pd.DataFrame(all_fills)
                    st.success(f"✅ Found {len(all_fills)} trades across all wallets in {date_label}")
                else:
                    st.warning(f"No trades found for {date_label}")
                    st.session_state.activity_fills = pd.DataFrame()
            else:
                # Fetch single wallet
                wallet_row = portfolio_df[portfolio_df["display_name"] == selected_wallet].iloc[0]
                wallet_address = wallet_row["address"]

                max_retries = 3
                status_placeholder = st.empty()
                fills = []

                for attempt in range(max_retries):
                    retry_text = f" (retry {attempt})" if attempt > 0 else ""
                    with status_placeholder.container():
                        with st.spinner(f"Fetching trades for {selected_wallet} ({date_label}){retry_text}..."):
                            client = HyperliquidClient()
                            start_time = datetime(from_date.year, from_date.month, from_date.day)
                            end_time = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59)

                            try:
                                fills = client.get_user_fills_paginated(wallet_address, start_time, end_time, max_fills=10000)
                                if fills:
                                    break
                                if attempt < max_retries - 1:
                                    time.sleep(0.5)
                            except Exception:
                                if attempt < max_retries - 1:
                                    time.sleep(0.5)

                status_placeholder.empty()

                st.session_state.calendar_years = year_range
                st.session_state.calendar_from_date = from_date
                st.session_state.calendar_to_date = to_date
                st.session_state.activity_mode = "single"

                if fills:
                    fills_df = pd.DataFrame([{
                        'wallet': selected_wallet,
                        'coin': f.coin,
                        'side': f.side,
                        'direction': f.direction,
                        'size': f.size,
                        'price': f.price,
                        'pnl': f.pnl,
                        'timestamp': f.timestamp,
                        'fee': f.fee
                    } for f in fills])

                    st.session_state.activity_fills = fills_df
                    st.success(f"✅ Found {len(fills)} trades in {date_label}")
                else:
                    st.warning(f"No trades found for {date_label} after {max_retries} attempts")
                    st.session_state.activity_fills = pd.DataFrame()

        # Display calendar if data exists
        if "activity_fills" in st.session_state:
            fills_df = st.session_state.activity_fills
            cal_from_date = st.session_state.get("calendar_from_date", datetime(datetime.now().year, 1, 1))
            cal_to_date = st.session_state.get("calendar_to_date", datetime.now())

            fig = create_activity_calendar_range(fills_df, cal_from_date, cal_to_date)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"main_calendar_{cal_from_date}_{cal_to_date}")

            # Date selector for viewing details
            if len(fills_df) > 0:
                fills_df_temp = fills_df.copy()
                fills_df_temp['date'] = pd.to_datetime(fills_df_temp['timestamp']).dt.date
                available_dates = sorted(fills_df_temp['date'].unique(), reverse=True)

                st.markdown("### 🔍 View Date Details")
                col1, col2 = st.columns([3, 1])
                with col1:
                    date_options = ["Select a date..."] + [d.strftime('%Y-%m-%d') for d in available_dates]
                    selected_date_str = st.selectbox("Select date to view details", options=date_options, key="date_detail_selector", label_visibility="collapsed")

                if selected_date_str != "Select a date...":
                    st.divider()
                    render_date_details_popup(fills_df, selected_date_str)

            if len(fills_df) > 0:
                st.divider()

                # Summary stats
                open_long = len(fills_df[fills_df['direction'] == 'Open Long'])
                close_long = len(fills_df[fills_df['direction'] == 'Close Long'])
                open_short = len(fills_df[fills_df['direction'] == 'Open Short'])
                close_short = len(fills_df[fills_df['direction'] == 'Close Short'])
                total_pnl = fills_df['pnl'].sum()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Trades", len(fills_df))
                with col2:
                    st.metric("Realized PnL", hl_format_currency(total_pnl))

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🟢 Open Long", f"{open_long:,}")
                with col2:
                    st.metric("🔵 Close Long", f"{close_long:,}")
                with col3:
                    st.metric("🔴 Open Short", f"{open_short:,}")
                with col4:
                    st.metric("🟠 Close Short", f"{close_short:,}")

                # ==================== LINE CHART: Long/Short Volume ====================
                st.divider()
                st.markdown("### 📈 Long/Short Volume Over Time")

                # Prepare data for line chart
                chart_df = fills_df.copy()
                chart_df['date'] = pd.to_datetime(chart_df['timestamp']).dt.date
                chart_df['volume'] = chart_df['size'] * chart_df['price']

                # Coin selector for chart
                available_coins = sorted(chart_df['coin'].unique().tolist())
                top_coins = chart_df.groupby('coin')['volume'].sum().nlargest(5).index.tolist()

                col_coin, col_agg = st.columns([2, 1])
                with col_coin:
                    chart_coin = st.selectbox(
                        "Select Coin",
                        options=["All Coins"] + available_coins,
                        index=0 if "BTC" not in available_coins else available_coins.index("BTC") + 1,
                        key="volume_chart_coin"
                    )
                with col_agg:
                    agg_type = st.radio("Aggregation", ["Daily", "Weekly"], horizontal=True, key="volume_agg_type")

                # Filter by coin
                if chart_coin != "All Coins":
                    coin_df = chart_df[chart_df['coin'] == chart_coin]
                else:
                    coin_df = chart_df

                if len(coin_df) > 0:
                    # Aggregate by date
                    coin_df['is_long'] = coin_df['direction'].isin(['Open Long', 'Close Long'])

                    if agg_type == "Weekly":
                        coin_df['period'] = pd.to_datetime(coin_df['date']).dt.to_period('W').dt.start_time
                    else:
                        coin_df['period'] = pd.to_datetime(coin_df['date'])

                    # Calculate Long and Short volumes
                    long_vol = coin_df[coin_df['is_long']].groupby('period')['volume'].sum()
                    short_vol = coin_df[~coin_df['is_long']].groupby('period')['volume'].sum()

                    # Create DataFrame for chart
                    volume_chart_data = pd.DataFrame({
                        'Long Volume': long_vol,
                        'Short Volume': short_vol
                    }).fillna(0)

                    if len(volume_chart_data) > 0:
                        # Display line chart
                        st.line_chart(
                            volume_chart_data,
                            color=["#22c55e", "#ef4444"],
                            use_container_width=True
                        )

                        # Summary for selected coin
                        total_long = volume_chart_data['Long Volume'].sum()
                        total_short = volume_chart_data['Short Volume'].sum()
                        net_volume = total_long - total_short
                        long_pct = (total_long / (total_long + total_short) * 100) if (total_long + total_short) > 0 else 0

                        def fmt_vol(v):
                            if abs(v) >= 1e9:
                                return f"${v/1e9:.2f}B"
                            elif abs(v) >= 1e6:
                                return f"${v/1e6:.2f}M"
                            elif abs(v) >= 1e3:
                                return f"${v/1e3:.1f}K"
                            return f"${v:.0f}"

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("🟢 Total Long", fmt_vol(total_long))
                        with col2:
                            st.metric("🔴 Total Short", fmt_vol(total_short))
                        with col3:
                            net_color = "🟢" if net_volume >= 0 else "🔴"
                            st.metric(f"{net_color} Net Volume", fmt_vol(net_volume))
                        with col4:
                            bias = "LONG" if long_pct > 55 else ("SHORT" if long_pct < 45 else "NEUTRAL")
                            st.metric("📊 Long %", f"{long_pct:.1f}% ({bias})")
                    else:
                        st.info(f"No volume data for {chart_coin}")
                else:
                    st.info(f"No trades found for {chart_coin}")

                # Show all wallets heatmap if in all mode
                is_all_mode = st.session_state.get("activity_mode", "single") == "all"
                if is_all_mode and 'wallet' in fills_df.columns:
                    st.divider()
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; padding: 24px; margin: 16px 0; border: 1px solid #334155;">
                        <h2 style="margin: 0; color: #f1f5f9; font-size: 24px;">👛 All Wallets Activity</h2>
                        <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 14px;">Each row represents a wallet • Columns are days • Hover for details</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Wallet detail selector
                    wallet_list_sorted = fills_df.groupby('wallet')['pnl'].sum().sort_values(ascending=False).index.tolist()
                    col_select, col_btn = st.columns([3, 1])
                    with col_select:
                        detail_wallet = st.selectbox(
                            "🔍 Select wallet to view details",
                            options=["Select a wallet..."] + wallet_list_sorted,
                            key="detail_wallet_selector"
                        )
                    with col_btn:
                        st.write("")  # Spacing
                        view_detail_btn = st.button("📊 View Details", type="primary", key="view_wallet_detail_btn", disabled=(detail_wallet == "Select a wallet..."))

                    if view_detail_btn and detail_wallet != "Select a wallet...":
                        show_wallet_activity_dialog(detail_wallet, fills_df, cal_from_date, cal_to_date)

                    all_wallet_names = st.session_state.get("all_wallet_names", None)
                    all_wallets_fig = create_all_wallets_heatmap(fills_df.copy(), cal_from_date, cal_to_date, all_wallet_names)
                    if all_wallets_fig:
                        st.plotly_chart(all_wallets_fig, use_container_width=True, config={"displayModeBar": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"], "displaylogo": False}, key=f"all_wallets_heatmap_{cal_from_date}_{cal_to_date}")

                st.divider()

                # Recent trades table
                st.markdown("### 📜 Recent Trades")
                recent_df = fills_df.sort_values('timestamp', ascending=False).head(100).copy()
                recent_df['timestamp'] = recent_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                recent_df['size'] = recent_df['size'].apply(lambda x: f"{x:,.4f}")
                recent_df['price'] = recent_df['price'].apply(lambda x: f"${x:,.2f}")
                recent_df['pnl'] = recent_df['pnl'].apply(lambda x: hl_format_currency(x))
                recent_df['fee'] = recent_df['fee'].apply(lambda x: f"${x:,.4f}")

                if is_all_mode and 'wallet' in recent_df.columns:
                    display_cols = ['timestamp', 'wallet', 'coin', 'direction', 'size', 'price', 'pnl', 'fee']
                    recent_df = recent_df[display_cols]
                    recent_df.columns = ['Time', 'Wallet', 'Coin', 'Direction', 'Size', 'Price', 'Realized PnL', 'Fee']
                else:
                    display_cols = ['timestamp', 'coin', 'direction', 'size', 'price', 'pnl', 'fee']
                    recent_df = recent_df[display_cols]
                    recent_df.columns = ['Time', 'Coin', 'Direction', 'Size', 'Price', 'Realized PnL', 'Fee']

                st.dataframe(recent_df, hide_index=True, use_container_width=True, height=400)

                # Trade breakdown by coin
                st.divider()
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 🪙 Activity by Coin")
                    coin_activity = fills_df.groupby('coin').agg({'size': 'count', 'pnl': 'sum'}).reset_index()
                    coin_activity.columns = ['Coin', 'Trades', 'PnL']
                    coin_activity = coin_activity.sort_values('Trades', ascending=False).head(10)
                    coin_activity['PnL'] = coin_activity['PnL'].apply(lambda x: hl_format_currency(x))
                    st.dataframe(coin_activity, hide_index=True, use_container_width=True)

                if is_all_mode and 'wallet' in fills_df.columns:
                    with col2:
                        st.markdown("### 👛 Activity by Wallet")
                        wallet_activity = fills_df.groupby('wallet').agg({'size': 'count', 'pnl': 'sum'}).reset_index()
                        wallet_activity.columns = ['Wallet', 'Trades', 'PnL']
                        wallet_activity = wallet_activity.sort_values('Trades', ascending=False)
                        wallet_activity_display = wallet_activity.head(10).copy()
                        wallet_activity_display['PnL'] = wallet_activity_display['PnL'].apply(lambda x: hl_format_currency(x))
                        st.dataframe(wallet_activity_display, hide_index=True, use_container_width=True)
        else:
            st.info("👆 Select a wallet and click 'Fetch Activity' to view trading calendar")

        # Detailed table at the bottom
        st.divider()
        st.subheader("📋 Detailed Data")
        table_df = portfolio_df[["display_name", "entity", "total_value", "perp_value", "spot_value", "perp_pct", "total_pnl"]].copy()
        table_df.columns = ["Wallet", "Entity", "Total Value", "Perp Value", "Spot Value", "Perp %", "PnL"]
        table_df["Total Value"] = table_df["Total Value"].apply(lambda x: hl_format_currency(x))
        table_df["Perp Value"] = table_df["Perp Value"].apply(lambda x: hl_format_currency(x))
        table_df["Spot Value"] = table_df["Spot Value"].apply(lambda x: hl_format_currency(x))
        table_df["Perp %"] = table_df["Perp %"].apply(lambda x: f"{x:.1f}%")
        table_df["PnL"] = table_df["PnL"].apply(lambda x: hl_format_currency(x))

        st.dataframe(table_df, hide_index=True, use_container_width=True, height=400)

    else:
        st.info("👆 Click 'Fetch Live Data' in the sidebar to load real-time Perp/Spot breakdown")

        st.subheader("📋 Loaded Wallets (from CSV)")
        # Only select columns that exist in the DataFrame
        desired_cols = ["trader_address_label", "Entity", "account_value", "roi", "total_pnl(unrealize profit)"]
        display_cols = ["Wallet", "Entity", "Account Value", "ROI", "Unrealized PnL"]
        available_cols = [col for col in desired_cols if col in filtered_df.columns]
        available_display_cols = [display_cols[i] for i, col in enumerate(desired_cols) if col in filtered_df.columns]

        if available_cols:
            display_df = filtered_df[available_cols].copy()
            display_df.columns = available_display_cols
            st.dataframe(display_df, hide_index=True, use_container_width=True, height=600)
        else:
            st.warning("No data available to display")


# ==================== TOKEN TRACKER DASHBOARD ====================

def render_token_tracker_sidebar():
    """Render the Token Tracker sidebar controls."""
    st.header("📊 Token Tracker")
    st.caption("Track token metrics across chains")

    st.divider()

    # User Input (for BigQuery dataset naming)
    token_name = st.text_input(
        "Token Name",
        placeholder="Enter token name...",
        value="",
        key="token_tracker_name"
    )
    if token_name:
        st.session_state.current_user = token_name
    else:
        st.session_state.current_user = "anonymous"

    st.divider()
    st.info("💡 Enter a token name to track metrics")


def render_token_tracker_content():
    """Render the Token Tracker main content with tabs."""
    from config import SUPPORTED_CHAINS
    from components import (
        cvd_tracker, tracking_log, token_tracker,
        profiler, dune_export, social_listening
    )
    from services import fetch_all_data

    # Initialize session state for Token Tracker
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'fetched_data' not in st.session_state:
        st.session_state.fetched_data = {}
    if 'endpoint_status' not in st.session_state:
        st.session_state.endpoint_status = {}
    if 'preview_endpoint' not in st.session_state:
        st.session_state.preview_endpoint = None
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    # CVD Tracker Session State
    cvd_tracker.init_session_state()

    current_user = st.session_state.get('current_user', 'anonymous')

    st.title("📊 Token Tracker")
    st.caption("Track token metrics across multiple chains and data sources")

    # Token Tracker Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Tracking Log", "🎯 Token Tracker", "👤 Profiler",
        "📊 Dune Export", "📱 Social Listening", "📈 CVD Tracker"
    ])

    # Store chain/contract from tab1 for use in tab2
    chain = "Solana"
    contract_address = ""

    with tab1:
        chain, contract_address = tracking_log.render_tab(
            fetch_callback=fetch_all_data,
            current_user=current_user,
            theme="Dark"
        )

    with tab2:
        token_tracker.render_tab(chain, contract_address, current_user)

    with tab3:
        profiler.render_tab(current_user)

    with tab4:
        dune_export.render_tab(current_user)

    with tab5:
        social_listening.render_tab()

    with tab6:
        cvd_tracker.render_tab()


# ==================== MAIN APP ====================

def main():
    """Main application entry point with sidebar navigation"""

    # Initialize active dashboard
    if 'active_dashboard' not in st.session_state:
        st.session_state.active_dashboard = "💰 Smart Money on Hyper"

    # Sidebar navigation
    with st.sidebar:
        st.image("https://hyperliquid.xyz/favicon.ico", width=40)
        st.title("Whale Tracker")

        dashboard_choice = st.radio(
            "Dashboard",
            ["💰 Smart Money on Hyper", "🐋 Whale Screener", "📊 Token Tracker"],
            index=["💰 Smart Money on Hyper", "🐋 Whale Screener", "📊 Token Tracker"].index(
                st.session_state.active_dashboard
            ) if st.session_state.active_dashboard in ["💰 Smart Money on Hyper", "🐋 Whale Screener", "📊 Token Tracker"] else 0,
            key="dashboard_nav"
        )
        st.session_state.active_dashboard = dashboard_choice

        st.divider()

        # Show appropriate sidebar content
        if dashboard_choice == "💰 Smart Money on Hyper":
            render_smart_money_sidebar()
        elif dashboard_choice == "🐋 Whale Screener":
            render_whale_screener_sidebar()
        else:
            render_token_tracker_sidebar()

    # Main content
    if st.session_state.active_dashboard == "💰 Smart Money on Hyper":
        render_smart_money_content()
    elif st.session_state.active_dashboard == "🐋 Whale Screener":
        render_whale_screener_content()
    else:
        render_token_tracker_content()


if __name__ == "__main__":
    main()
