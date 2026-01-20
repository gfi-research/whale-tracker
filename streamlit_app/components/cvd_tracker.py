"""
CVD Tracker Component - Orderbook CVD Dashboard
Real-time orderbook and CVD tracking across multiple exchanges.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from collections import deque

from streamlit_elements import elements, mui, html, nivo, dashboard
from orderbook_sync import OrderbookEngineSync


def init_session_state():
    """Initialize CVD-related session state variables."""
    if 'cvd_engine' not in st.session_state:
        st.session_state.cvd_engine = None
    if 'cvd_running' not in st.session_state:
        st.session_state.cvd_running = False
    if 'cvd_active_symbol' not in st.session_state:
        st.session_state.cvd_active_symbol = "BTC/USDT"
    if 'cvd_chart_history' not in st.session_state:
        st.session_state.cvd_chart_history = _create_empty_history()


def _create_empty_history():
    """Create empty chart history structure."""
    return {
        'timestamps': deque(maxlen=100),
        'prices': {},
        'imbalance': {},
        'cvd_5m': {},
        'cvd_1h': {},
        'cvd_12h': {},
        'cvd_24h': {}
    }


def init_engine_if_needed(target_symbol):
    """Initialize the engine only if the symbol has changed or engine is missing."""
    if st.session_state.cvd_engine is None or st.session_state.cvd_engine.symbol != target_symbol:
        with st.spinner(f"Initializing exchanges for {target_symbol}..."):
            engine = OrderbookEngineSync(
                ['binance', 'coinbase', 'bybit', 'hyperliquid'],
                target_symbol,
                depth=30
            )
            engine.init()
            st.session_state.cvd_engine = engine
            st.session_state.cvd_chart_history = _create_empty_history()


def update_chart_history(data):
    """Append new data point to chart history."""
    history = st.session_state.cvd_chart_history
    now = datetime.now().strftime("%H:%M:%S")
    history['timestamps'].append(now)

    for r in data:
        ex_id = r['id']

        # Initialize deques if not present
        if ex_id not in history['prices']:
            history['prices'][ex_id] = deque(maxlen=100)
            history['imbalance'][ex_id] = deque(maxlen=20)
            history['cvd_5m'][ex_id] = deque(maxlen=100)
            history['cvd_1h'][ex_id] = deque(maxlen=100)
            history['cvd_12h'][ex_id] = deque(maxlen=100)
            history['cvd_24h'][ex_id] = deque(maxlen=100)

        history['prices'][ex_id].append(r['price'])
        history['imbalance'][ex_id].append(r['imbalance'])
        history['cvd_5m'][ex_id].append(r['cvd_5m'])
        history['cvd_1h'][ex_id].append(r['cvd_1h'])
        history['cvd_12h'][ex_id].append(r['cvd_12h'])
        history['cvd_24h'][ex_id].append(r['cvd_24h'])


def build_chart_data(cvd_key):
    """Build Nivo line chart data for a specific CVD window."""
    history = st.session_state.cvd_chart_history
    timestamps = list(history['timestamps'])

    if not timestamps:
        return [], []

    price_data = []
    cvd_data = []

    for ex_id, prices in history['prices'].items():
        cvd_list = list(history[cvd_key].get(ex_id, []))
        if cvd_list:
            # Use min to prevent index out of bounds
            data_len = min(len(timestamps), len(cvd_list))
            cvd_data.append({
                "id": ex_id.upper(),
                "data": [{"x": timestamps[i], "y": round(cvd_list[i], 2)} for i in range(data_len)]
            })

    return price_data, cvd_data


def _render_market_overview(data):
    """Render market overview table with sparklines."""
    cols = st.columns([1.2, 1, 1.2, 3, 1.2, 1.2])
    cols[0].markdown("**Exchange**")
    cols[1].markdown("**Price**")
    cols[2].markdown("**Imbalance**")
    cols[3].markdown("**Imbalance History (20)**")
    cols[4].markdown("**CVD 5m**")
    cols[5].markdown("**CVD 1h**")

    for r in data:
        ex_id = r['id']
        imbal_hist = list(st.session_state.cvd_chart_history['imbalance'].get(ex_id, []))

        c = st.columns([1.2, 1, 1.2, 3, 1.2, 1.2])
        c[0].write(ex_id.upper())
        c[1].write(f"{r['price']:.4f}")
        c[2].write(f"{r['imbalance']:.2f}")

        # Sparkline
        if imbal_hist:
            colors = ['#0ECB81' if v >= 0 else '#F6465D' for v in imbal_hist]
            fig = go.Figure(go.Bar(
                x=list(range(len(imbal_hist))),
                y=imbal_hist,
                marker_color=colors,
                showlegend=False
            ))
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                height=35,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(visible=False, fixedrange=True),
                yaxis=dict(visible=False, fixedrange=True),
                dragmode=False,
                bargap=0.1
            )
            c[3].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
        else:
            c[3].write("-")

        c[4].write(f"{r['cvd_5m']:.2f}")
        c[5].write(f"{r['cvd_1h']:.2f}")


def _get_nivo_theme():
    """Get Nivo chart theme configuration."""
    return {
        "textColor": "#eaecef",
        "axis": {
            "domain": {"line": {"stroke": "#777777", "strokeWidth": 1}},
            "ticks": {
                "line": {"stroke": "#777777", "strokeWidth": 1},
                "text": {"fill": "#eaecef"}
            },
            "legend": {"text": {"fill": "#eaecef"}}
        },
        "grid": {"line": {"stroke": "#444444"}},
        "legends": {"text": {"fill": "#eaecef"}},
        "tooltip": {
            "container": {"background": "#1e2329", "color": "#eaecef", "fontSize": 12}
        },
        "crosshair": {
            "line": {"stroke": "#eaecef", "strokeWidth": 1, "strokeOpacity": 0.35}
        }
    }


def render_dashboard(data, ohlcv_data=None):
    """Render the full CVD dashboard."""
    if not data:
        st.warning("Waiting for data...")
        return

    update_chart_history(data)

    # Market Overview Table
    _render_market_overview(data)
    st.divider()

    # Dashboard Grid
    with elements("dashboard"):
        layout = [
            dashboard.Item("cvd_5m", 0, 0, 6, 4, isDraggable=True, isResizable=True),
            dashboard.Item("cvd_1h", 6, 0, 6, 4, isDraggable=True, isResizable=True),
            dashboard.Item("cvd_12h", 0, 4, 6, 4, isDraggable=True, isResizable=True),
            dashboard.Item("cvd_24h", 6, 4, 6, 4, isDraggable=True, isResizable=True),
            dashboard.Item("agg_ob", 0, 8, 6, 5, isDraggable=True, isResizable=True),
            dashboard.Item("price_chart", 0, 14, 12, 4, isDraggable=True, isResizable=True),
        ]

        for i, r in enumerate(data):
            layout.append(dashboard.Item(
                f"ob_{r['id']}", 6 + (i % 2) * 3, 8 + (i // 2) * 3, 3, 3,
                isDraggable=False, isResizable=False
            ))

        with dashboard.Grid(layout):
            # CVD Time-Series Charts
            for timeframe, key in [("CVD 5m", "cvd_5m"), ("CVD 1h", "cvd_1h"),
                                   ("CVD 12h", "cvd_12h"), ("CVD 24h", "cvd_24h")]:
                with mui.Paper(key=key, sx={"padding": 2}):
                    mui.Typography(timeframe, variant="h6")
                    price_data, cvd_data = build_chart_data(key)

                    if not cvd_data:
                        mui.Typography("Collecting data...", variant="body2")
                    else:
                        with html.div(style={"height": 280}):
                            nivo.Line(
                                data=cvd_data,
                                margin={"top": 20, "right": 110, "bottom": 40, "left": 60},
                                xScale={"type": "point"},
                                yScale={"type": "linear", "min": "auto", "max": "auto",
                                        "stacked": False, "reverse": False},
                                axisTop=None, axisRight=None,
                                axisBottom={"tickSize": 5, "tickPadding": 5, "tickRotation": -45},
                                axisLeft={"tickSize": 5, "tickPadding": 5, "tickRotation": 0},
                                enableGridY=False, enableGridX=False, enablePoints=False,
                                useMesh=True, animate=False,
                                colors=["#FCD535", "#0052FF", "#965F2D"],
                                legends=[{
                                    "anchor": "bottom-right", "direction": "column",
                                    "justify": False, "translateX": 100, "translateY": 0,
                                    "itemsSpacing": 0, "itemDirection": "left-to-right",
                                    "itemWidth": 80, "itemHeight": 20, "itemOpacity": 0.75,
                                    "symbolSize": 12, "symbolShape": "circle",
                                    "symbolBorderColor": "rgba(0, 0, 0, .5)"
                                }],
                                theme=_get_nivo_theme()
                            )

            # Aggregated Orderbook
            with mui.Paper(key="agg_ob", sx={"padding": 2, "overflow": "auto", "backgroundColor": "#0b0e11"}):
                mui.Typography("Aggregated Orderbook", variant="h6",
                              sx={"color": "#eaecef", "marginBottom": 1})

                agg_bids, agg_asks = {}, {}
                for r in data:
                    for b in r['bids'][:15]:
                        agg_bids[b[0]] = agg_bids.get(b[0], 0) + b[1]
                    for a in r['asks'][:15]:
                        agg_asks[a[0]] = agg_asks.get(a[0], 0) + a[1]

                sorted_bids = sorted(agg_bids.items(), key=lambda x: x[0], reverse=True)[:10]
                sorted_asks = list(reversed(sorted(agg_asks.items(), key=lambda x: x[0])[:10]))

                with html.div(style={"fontFamily": "monospace", "fontSize": "14px"}):
                    with html.div(style={"display": "flex", "justifyContent": "space-between",
                                        "color": "#848e9c", "padding": "4px 8px",
                                        "borderBottom": "1px solid #2b3139"}):
                        html.span("Price (USDT)")
                        html.span("Amount")
                        html.span("Total")

                    for price, vol in sorted_asks:
                        with html.div(style={"display": "flex", "justifyContent": "space-between",
                                            "color": "#f6465d", "padding": "3px 8px"}):
                            html.span(f"{price:.4f}")
                            html.span(f"{vol:.4f}")
                            html.span(f"{price * vol:.2f}")

                    if sorted_bids and sorted_asks:
                        spread = sorted_asks[-1][0] - sorted_bids[0][0]
                        with html.div(style={"display": "flex", "justifyContent": "center",
                                            "color": "#eaecef", "padding": "5px",
                                            "backgroundColor": "#1e2329", "fontWeight": "bold"}):
                            html.span(f"Spread: {spread:.2f}")

                    for price, vol in sorted_bids:
                        with html.div(style={"display": "flex", "justifyContent": "space-between",
                                            "color": "#0ecb81", "padding": "3px 8px"}):
                            html.span(f"{price:.4f}")
                            html.span(f"{vol:.4f}")
                            html.span(f"{price * vol:.2f}")

            # Individual Exchange Orderbooks
            for r in data:
                with mui.Paper(key=f"ob_{r['id']}", sx={"padding": 1, "overflow": "auto",
                                                        "backgroundColor": "#0b0e11"}):
                    mui.Typography(f"{r['id'].upper()}", variant="subtitle2",
                                  sx={"color": "#eaecef", "fontWeight": "bold"})

                    bids = r['bids'][:5]
                    asks = list(reversed(r['asks'][:5]))

                    with html.div(style={"fontFamily": "monospace", "fontSize": "11px"}):
                        for a in asks:
                            with html.div(style={"display": "flex", "justifyContent": "space-between",
                                                "color": "#f6465d", "padding": "1px 2px"}):
                                html.span(f"{a[0]:.2f}")
                                html.span(f"{a[1]:.4f}")
                        for b in bids:
                            with html.div(style={"display": "flex", "justifyContent": "space-between",
                                                "color": "#0ecb81", "padding": "1px 2px"}):
                                html.span(f"{b[0]:.2f}")
                                html.span(f"{b[1]:.4f}")

            # Price Chart
            with mui.Paper(key="price_chart", sx={"padding": 1, "overflow": "hidden",
                                                   "backgroundColor": "#0b0e11"}):
                if ohlcv_data:
                    dates = [datetime.fromtimestamp(x[0]/1000) for x in ohlcv_data['data']]
                    opens = [x[1] for x in ohlcv_data['data']]
                    highs = [x[2] for x in ohlcv_data['data']]
                    lows = [x[3] for x in ohlcv_data['data']]
                    closes = [x[4] for x in ohlcv_data['data']]

                    fig = go.Figure(data=[go.Candlestick(
                        x=dates, open=opens, high=highs, low=lows, close=closes,
                        increasing_line_color='#0ECB81', decreasing_line_color='#F6465D'
                    )])
                    fig.update_layout(
                        title=dict(text=f"Price History ({ohlcv_data['exchange'].upper()})",
                                  font=dict(color="#eaecef", size=14)),
                        template="plotly_dark",
                        xaxis_rangeslider_visible=False,
                        margin=dict(t=30, b=10, l=10, r=10),
                        paper_bgcolor="#0b0e11", plot_bgcolor="#0b0e11",
                        font=dict(family="sans-serif", size=10, color="#eaecef"),
                        autosize=True
                    )

                    plot_html = fig.to_html(include_plotlyjs='cdn', full_html=False,
                                           config={'displayModeBar': False, 'responsive': True})
                    html.div(dangerouslySetInnerHTML={"__html": plot_html},
                            style={"height": "100%", "width": "100%"})
                else:
                    mui.Typography("Loading Price Data...", variant="subtitle1",
                                  sx={"color": "#eaecef"})


def render_tab():
    """Main entry point for CVD Tracker tab."""
    st.header("CVD Tracker (Orderbook CVD)")

    # Inputs
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        cvd_symbol = st.text_input("Symbol", value=st.session_state.cvd_active_symbol, key="cvd_sym")
    with c2:
        cvd_refresh = st.slider("Refresh (s)", 1, 10, 2, key="cvd_ref")
    with c3:
        st.write("")  # Spacer
        st.write("")  # Spacer
        col_run, col_stop = st.columns(2)
        if col_run.button("Run", key="cvd_run", use_container_width=True):
            st.session_state.cvd_running = True
            st.session_state.cvd_active_symbol = cvd_symbol
        if col_stop.button("Stop", key="cvd_stop", use_container_width=True):
            st.session_state.cvd_running = False
            st.rerun()

    st.markdown("---")

    if st.session_state.cvd_running:
        init_engine_if_needed(st.session_state.cvd_active_symbol)

        # Show initialization errors if any
        if st.session_state.cvd_engine and st.session_state.cvd_engine.errors:
            with st.expander("Connection Errors", expanded=True):
                for ex, err in st.session_state.cvd_engine.errors.items():
                    st.warning(f"⚠️ {ex.upper()}: {err}")

        @st.fragment(run_every=cvd_refresh)
        def dashboard_container():
            if st.session_state.cvd_engine:
                data = st.session_state.cvd_engine.fetch_all()
                ohlcv_data = st.session_state.cvd_engine.fetch_candle_history()
                render_dashboard(data, ohlcv_data)

        dashboard_container()
    else:
        st.info("Enter a symbol (e.g. BTC/USDT) and click 'Run' to start monitoring.")
