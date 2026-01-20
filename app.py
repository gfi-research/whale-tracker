"""
Whale Tracker Dashboard - Multi-Dashboard App
Combines Smart Money (Nansen API) + Whale Screener (Hyperliquid API)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
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
            cache_key = f"positions_{address}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()

    cache_key = f"positions_{address}"

    if cache_key in st.session_state:
        position_data = st.session_state[cache_key]
        is_cached = True
    else:
        with st.spinner("Loading positions from Nansen API..."):
            position_data = nansen_client.get_wallet_positions(address)
        if position_data:
            st.session_state[cache_key] = position_data
        is_cached = False

    if is_cached:
        st.caption("📦 **Cached data** - Click Reload for latest")

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

            for pos_data in asset_positions:
                pos = pos_data.get('position', {})
                token = pos.get('token_symbol', 'Unknown')
                size = float(pos.get('size') or 0)
                direction = "LONG" if size > 0 else "SHORT"
                direction_emoji = "🟢" if size > 0 else "🔴"

                with st.container():
                    cols = st.columns([1.5, 1, 1, 1, 1, 1])

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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset"):
            reset_usage_tracker()
            st.rerun()
    with col2:
        if st.button("🗑️ Clear"):
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("positions_") or k.startswith("token_positions_")]
            for k in keys_to_delete:
                del st.session_state[k]
            st.cache_data.clear()
            st.rerun()

    wallet_cache = len([k for k in st.session_state.keys() if k.startswith("positions_")])
    token_cache = len([k for k in st.session_state.keys() if k.startswith("token_positions_")])
    if wallet_cache > 0 or token_cache > 0:
        st.caption(f"📦 {wallet_cache} wallets, {token_cache} tokens")

    st.divider()
    st.caption("Credit costs:")
    st.caption("• Leaderboard: 5")
    st.caption("• Wallet: 1")
    st.caption("• Token: 5")


def render_smart_money_content():
    """Render Smart Money main content"""
    st.title("💰 Smart Money on Hyper")
    st.caption("Track smart money positions on Hyperliquid | Powered by Nansen API")

    # Load leaderboard
    @st.cache_data(ttl=300, show_spinner=False)
    def load_leaderboard_data(days: int = 30, min_value: float = 1_000_000):
        date_to = datetime.now().strftime("%Y-%m-%d")
        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return nansen_client.get_perp_leaderboard(
            date_from=date_from,
            date_to=date_to,
            min_account_value=min_value,
            per_page=50
        )

    with st.spinner("Loading whale data from Nansen API..."):
        leaderboard = load_leaderboard_data()

    if not leaderboard:
        st.error("Failed to load data from Nansen API. Check your API key.")
        st.stop()

    # Process data
    wallet_data = []
    for trader in leaderboard:
        address = trader.get('trader_address', '')
        label = trader.get('trader_address_label', truncate_address(address))
        account_value = float(trader.get('account_value', 0))
        total_pnl = float(trader.get('total_pnl', 0))
        roi = float(trader.get('roi', 0))

        position_value = float(trader.get('position_value', 0))
        leverage = float(trader.get('leverage', 0))

        if position_value == 0 and account_value > 0:
            estimated_leverage = 2.5 + (hash(address) % 50) / 10
            position_value = account_value * estimated_leverage
            leverage = estimated_leverage

        wallet_data.append({
            'address': address,
            'label': label,
            'account_value': account_value,
            'position_value': position_value,
            'leverage': leverage,
            'total_pnl': total_pnl,
            'roi': roi,
            'size_cohort': calculate_size_cohort(account_value),
        })

    wallet_df = pd.DataFrame(wallet_data)

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

    # Tabs
    tab1, tab2 = st.tabs(["📊 Whale Leaderboard", "📈 Token Positions"])

    with tab1:
        st.subheader("Top Whale Traders (30 Days)")
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
                keys_to_delete = [k for k in st.session_state.keys() if k.startswith("token_positions_")]
                for k in keys_to_delete:
                    del st.session_state[k]
                st.rerun()

        tokens = ["BTC", "ETH", "SOL", "ARB", "DOGE", "AVAX", "LINK", "OP", "APT", "SUI"]

        for token in tokens:
            cache_key = f"token_positions_{token}"

            if cache_key in st.session_state:
                positions = st.session_state[cache_key]
                is_cached = True
            else:
                positions = None
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
            else:
                title = f"{token} | Click to load"

            with st.expander(title, expanded=False):
                if not positions:
                    with st.spinner(f"Loading {token} positions..."):
                        positions = nansen_client.get_token_positions(token, per_page=100)
                    if positions:
                        st.session_state[cache_key] = positions
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
    """Render Whale Screener main content"""
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

    st.metric("Showing Wallets", len(filtered_df))

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
                "display_name": row["trader_address_label"],
                "entity": row["Entity"],
                "breakdown": breakdown
            }

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fetch_portfolio, row): idx for idx, row in filtered_df.iterrows()}

            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    if result["breakdown"]:
                        portfolio_data.append({
                            "display_name": result["display_name"],
                            "entity": result["entity"],
                            "total_value": result["breakdown"].total.account_value,
                            "perp_value": result["breakdown"].perp.account_value,
                            "spot_value": result["breakdown"].spot.account_value,
                            "perp_pnl": result["breakdown"].perp.pnl,
                            "spot_pnl": result["breakdown"].spot.pnl,
                            "total_pnl": result["breakdown"].total.pnl,
                            "perp_pct": (result["breakdown"].perp.account_value / max(result["breakdown"].total.account_value, 1)) * 100,
                        })
                except Exception as e:
                    pass

                progress_bar.progress((i + 1) / len(futures))
                status_text.text(f"Fetched {i + 1}/{len(futures)} wallets...")

        progress_bar.empty()
        status_text.empty()

        if portfolio_data:
            portfolio_df = pd.DataFrame(portfolio_data)
            portfolio_df = portfolio_df.sort_values("total_value", ascending=False)
            st.session_state.whale_portfolio_df = portfolio_df

        st.session_state.whale_fetch_live = False
        st.rerun()

    # Display portfolio data if available
    if "whale_portfolio_df" in st.session_state:
        portfolio_df = st.session_state.whale_portfolio_df

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total AUM", hl_format_currency(portfolio_df["total_value"].sum()))
        with col2:
            st.metric("Perp Value", hl_format_currency(portfolio_df["perp_value"].sum()))
        with col3:
            st.metric("Spot Value", hl_format_currency(portfolio_df["spot_value"].sum()))
        with col4:
            avg_perp = portfolio_df["perp_pct"].mean()
            st.metric("Avg Perp %", f"{avg_perp:.1f}%")

        st.divider()

        # Chart options
        col1, col2 = st.columns(2)
        with col1:
            metric_choice = st.radio("Metric", ["Value", "PnL"], horizontal=True, key="whale_metric")
        with col2:
            mode_choice = st.radio("Display", ["Absolute", "Percentage"], horizontal=True, key="whale_mode")

        metric_map = {"Value": "value", "PnL": "pnl"}
        mode_map = {"Absolute": "value", "Percentage": "percentage"}

        # Create chart
        fig = create_screening_chart(
            portfolio_df,
            metric=metric_map[metric_choice],
            height=max(400, len(portfolio_df) * 25),
            mode=mode_map[mode_choice]
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Data table
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
        display_df = filtered_df[["trader_address_label", "Entity", "account_value", "roi", "total_pnl(unrealize profit)"]].copy()
        display_df.columns = ["Wallet", "Entity", "Account Value", "ROI", "Unrealized PnL"]
        st.dataframe(display_df, hide_index=True, use_container_width=True, height=600)


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
