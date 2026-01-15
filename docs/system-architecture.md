# System Architecture

**Project:** Hyperliquid Whale Screener Dashboard
**Last Updated:** January 2026

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Breakdown](#component-breakdown)
3. [Data Flow](#data-flow)
4. [State Management](#state-management)
5. [External Integrations](#external-integrations)
6. [Module Dependencies](#module-dependencies)

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                 CLIENT LAYER                                      │
│                              (Web Browser)                                        │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                        STREAMLIT RUNTIME                                    │ │
│  │                     (localhost:8501)                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                      PRESENTATION LAYER                              │  │ │
│  │  │  ┌──────────────┐  ┌──────────────────────────────────────────────┐ │  │ │
│  │  │  │   Sidebar    │  │              Main Content                     │ │  │ │
│  │  │  │              │  │                                               │ │  │ │
│  │  │  │ ○ Filters    │  │  ┌─────────────┐  ┌─────────────────────┐   │ │  │ │
│  │  │  │ ○ Time       │  │  │  Metrics    │  │  Stacked Bar Charts │   │ │  │ │
│  │  │  │ ○ Fetch Btn  │  │  └─────────────┘  └─────────────────────┘   │ │  │ │
│  │  │  │              │  │                                               │ │  │ │
│  │  │  │              │  │  ┌─────────────────────────────────────────┐ │ │  │ │
│  │  │  │              │  │  │         Distribution Heatmaps           │ │ │  │ │
│  │  │  │              │  │  └─────────────────────────────────────────┘ │ │  │ │
│  │  │  │              │  │                                               │ │  │ │
│  │  │  │              │  │  ┌─────────────────────────────────────────┐ │ │  │ │
│  │  │  │              │  │  │         Activity Calendars              │ │ │  │ │
│  │  │  │              │  │  └─────────────────────────────────────────┘ │ │  │ │
│  │  │  │              │  │                                               │ │  │ │
│  │  │  │              │  │  ┌─────────────────────────────────────────┐ │ │  │ │
│  │  │  │              │  │  │         Data Tables                     │ │ │  │ │
│  │  │  └──────────────┘  │  └─────────────────────────────────────────┘ │ │  │ │
│  │  │                    └──────────────────────────────────────────────┘ │  │ │
│  │  └─────────────────────────────────────────────────────────────────────┘  │ │
│  │                                    │                                       │ │
│  │                                    ▼                                       │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                       APPLICATION LAYER                              │  │ │
│  │  │                                                                      │  │ │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │  │ │
│  │  │  │   Chart Funcs   │  │   Data Funcs    │  │   State Manager     │  │  │ │
│  │  │  │                 │  │                 │  │                     │  │  │ │
│  │  │  │ create_*_chart  │  │ load_wallet_    │  │ st.session_state    │  │  │ │
│  │  │  │ create_*_heatmap│  │    addresses()  │  │ ○ portfolio_data    │  │  │ │
│  │  │  │ create_histogram│  │                 │  │ ○ activity_fills    │  │  │ │
│  │  │  │ create_activity │  │ @st.cache_data  │  │ ○ calendar_years    │  │  │ │
│  │  │  │    _calendar    │  │                 │  │ ○ activity_mode     │  │  │ │
│  │  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │  │ │
│  │  │                                    │                                 │  │ │
│  │  └────────────────────────────────────┼─────────────────────────────────┘  │ │
│  │                                       │                                    │ │
│  │                                       ▼                                    │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                         DATA LAYER                                   │  │ │
│  │  │                                                                      │  │ │
│  │  │  ┌─────────────────────────────────────────────────────────────┐   │  │ │
│  │  │  │                 src/api/hyperliquid.py                       │   │  │ │
│  │  │  │                                                              │   │  │ │
│  │  │  │  ┌────────────────┐  ┌────────────────────────────────────┐ │   │  │ │
│  │  │  │  │  Data Classes  │  │      HyperliquidClient             │ │   │  │ │
│  │  │  │  │                │  │                                    │ │   │  │ │
│  │  │  │  │ PortfolioMetrics│  │ ○ get_portfolio()                 │ │   │  │ │
│  │  │  │  │ PortfolioBreakdown│ │ ○ get_portfolio_breakdown()      │ │   │  │ │
│  │  │  │  │ TradeFill      │  │ ○ get_user_fills()                │ │   │  │ │
│  │  │  │  │                │  │ ○ get_user_fills_by_time()        │ │   │  │ │
│  │  │  │  └────────────────┘  └────────────────────────────────────┘ │   │  │ │
│  │  │  └─────────────────────────────────────────────────────────────┘   │  │ │
│  │  │                                                                      │  │ │
│  │  │  ┌─────────────────┐  ┌─────────────────────────────────────────┐  │  │ │
│  │  │  │ Local Storage   │  │      Utility Modules                     │  │  │ │
│  │  │  │                 │  │                                          │  │  │ │
│  │  │  │ wallet_address  │  │  src/utils/formatters.py                │  │  │ │
│  │  │  │   .txt (CSV)    │  │  ○ format_currency()                    │  │  │ │
│  │  │  │                 │  │  ○ format_number()                      │  │  │ │
│  │  │  │                 │  │  ○ format_percentage()                  │  │  │ │
│  │  │  └─────────────────┘  └─────────────────────────────────────────┘  │  │ │
│  │  └─────────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                          │
└───────────────────────────────────────┼──────────────────────────────────────────┘
                                        │
                                        │ HTTPS POST
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SERVICES                                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                     ┌────────────────────────────────────┐                       │
│                     │     Hyperliquid Info API           │                       │
│                     │   https://api.hyperliquid.xyz/info │                       │
│                     │                                    │                       │
│                     │   Endpoints:                       │                       │
│                     │   ○ type: portfolio                │                       │
│                     │   ○ type: userFills                │                       │
│                     │   ○ type: userFillsByTime          │                       │
│                     │                                    │                       │
│                     └────────────────────────────────────┘                       │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Presentation Layer Components

| Component | File Location | Purpose |
|-----------|---------------|---------|
| Page Config | `app.py:947-953` | Streamlit page settings, icon, layout |
| Custom CSS | `app.py:956-991` | Dark theme styling, component theming |
| Sidebar | `app.py:1003-1052` | Filters, time period selection, fetch button |
| Summary Metrics | `app.py:1067-1077` | Top-level wallet and AUM counts |
| Portfolio Chart | `app.py:1139-1148` | Stacked bar chart for perp/spot allocation |
| Distribution Maps | `app.py:1151-1230` | Heatmaps and histograms section |
| Activity Calendar | `app.py:1234-1573` | GitHub-style activity visualization |
| Data Tables | `app.py:1577-1597` | Detailed wallet data table |

### Application Layer Functions

| Function | Location | Input | Output | Purpose |
|----------|----------|-------|--------|---------|
| `load_wallet_addresses` | `app.py:38-45` | None | DataFrame | Load CSV wallet data |
| `create_screening_chart` | `app.py:48-179` | DataFrame | Figure | Stacked bar chart |
| `create_value_perp_heatmap` | `app.py:182-229` | DataFrame | Figure | Value vs Perp heatmap |
| `create_entity_perp_heatmap` | `app.py:232-278` | DataFrame | Figure | Entity vs Perp heatmap |
| `create_value_pnl_heatmap` | `app.py:281-326` | DataFrame | Figure | Value vs PnL heatmap |
| `create_histogram` | `app.py:329-352` | DataFrame | Figure | Distribution histogram |
| `create_activity_calendar` | `app.py:355-518` | DataFrame, year | Figure | Single year calendar |
| `create_activity_calendar_range` | `app.py:541-711` | DataFrame, years | Figure | Multi-year calendar |
| `create_all_wallets_heatmap` | `app.py:714-944` | DataFrame, years | Figure | All wallets activity |
| `create_activity_legend` | `app.py:521-538` | None | HTML | Calendar legend |

### Data Layer Components

| Component | File | Purpose |
|-----------|------|---------|
| `HyperliquidClient` | `src/api/hyperliquid.py` | API communication |
| `PortfolioMetrics` | `src/api/hyperliquid.py` | Data structure for metrics |
| `PortfolioBreakdown` | `src/api/hyperliquid.py` | Data structure for portfolio |
| `TradeFill` | `src/api/hyperliquid.py` | Data structure for trades |
| `format_currency` | `src/utils/formatters.py` | Currency formatting |
| `format_percentage` | `src/utils/formatters.py` | Percentage formatting |

---

## Data Flow

### Initial Load Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            INITIAL PAGE LOAD                                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │     main() called       │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │  load_wallet_addresses()│◄── @st.cache_data
                        │  Parse wallet_address   │
                        │       .txt (CSV)        │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Apply Filters from    │
                        │   Sidebar Selection     │
                        │   (Entity, Count, Sort) │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Display Summary       │
                        │   Metrics (from CSV)    │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Display CSV-based     │
                        │   Wallet Table          │
                        │   (no API call yet)     │
                        └─────────────────────────┘
```

### Fetch Portfolio Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FETCH LIVE DATA BUTTON CLICK                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │   User Clicks           │
                        │   "Fetch Live Data"     │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Create Progress Bar   │
                        │   Initialize Results    │
                        └────────────┬────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │   FOR EACH WALLET IN filtered_df│
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   HyperliquidClient.    │
                        │   get_portfolio_        │
                        │   breakdown(addr,period)│
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   POST to Hyperliquid   │
                        │   API /info             │
                        │   {type: "portfolio"}   │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Parse Response:       │
                        │   - Total metrics       │
                        │   - Perp metrics        │
                        │   - Spot (calculated)   │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Append to results[]   │
                        │   Sleep 50ms            │
                        │   Update progress       │
                        └────────────┬────────────┘
                                     │
                    └───────LOOP CONTINUES────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   st.session_state.     │
                        │   portfolio_data =      │
                        │   DataFrame(results)    │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Render All Charts     │
                        │   and Tables            │
                        └─────────────────────────┘
```

### Fetch Activity Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FETCH ACTIVITY BUTTON CLICK                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
            ┌───────────▼───────────┐   ┌──────────▼──────────┐
            │  Single Wallet Mode   │   │  All Wallets Mode   │
            └───────────┬───────────┘   └──────────┬──────────┘
                        │                           │
                        ▼                           ▼
            ┌───────────────────────┐   ┌───────────────────────┐
            │  get_user_fills_      │   │  FOR EACH WALLET:     │
            │  by_time(address,     │   │  get_user_fills_      │
            │  start_time, end_time)│   │  by_time()            │
            └───────────┬───────────┘   └───────────┬───────────┘
                        │                           │
                        ▼                           ▼
            ┌───────────────────────┐   ┌───────────────────────┐
            │  POST to API:         │   │  Aggregate all fills  │
            │  {type: "userFills    │   │  Add wallet column    │
            │   ByTime"}            │   │  to each fill         │
            └───────────┬───────────┘   └───────────┬───────────┘
                        │                           │
                        └───────────┬───────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  st.session_state.    │
                        │  activity_fills =     │
                        │  DataFrame(fills)     │
                        │                       │
                        │  st.session_state.    │
                        │  calendar_years = [...│
                        │  activity_mode =      │
                        │  "single" or "all"    │
                        └───────────┬───────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  Render Activity      │
                        │  Calendars and Tables │
                        └───────────────────────┘
```

---

## State Management

### Session State Variables

```python
st.session_state = {
    # Portfolio data from API fetch
    "portfolio_data": pd.DataFrame({
        "address": str,          # Wallet address
        "display_name": str,     # Label (max 40 chars)
        "entity": str,           # VCs, MM, retail
        "total_value": float,    # Account value USD
        "perp_value": float,     # Perp allocation USD
        "spot_value": float,     # Spot allocation USD
        "perp_pct": float,       # Perp percentage 0-100
        "total_pnl": float,      # Total PnL USD
        "perp_pnl": float,       # Perp PnL USD
        "spot_pnl": float,       # Spot PnL USD
        "total_volume": float,   # Trading volume USD
        "perp_volume": float,    # Perp volume USD
        "spot_volume": float,    # Spot volume USD
    }),

    # Activity calendar data
    "activity_fills": pd.DataFrame({
        "wallet": str,           # Wallet display name
        "coin": str,             # Trading pair
        "side": str,             # "B" or "A"
        "direction": str,        # "Open Long", etc.
        "size": float,           # Position size
        "price": float,          # Execution price
        "pnl": float,            # Realized PnL
        "timestamp": datetime,   # Trade time
        "fee": float,            # Trading fee
    }),

    # Calendar configuration
    "calendar_years": [2024, 2025],  # Selected year range
    "activity_mode": "all",          # "single" or "all"
    "all_wallet_names": [str, ...],  # All wallet names for heatmap
}
```

### State Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SESSION STATE LIFECYCLE                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Initial Load   │      │  Fetch Portfolio │      │  Fetch Activity  │
│                  │      │                  │      │                  │
│ session_state:   │      │ session_state:   │      │ session_state:   │
│ (empty)          │ ──►  │ + portfolio_data │ ──►  │ + activity_fills │
│                  │      │                  │      │ + calendar_years │
│                  │      │                  │      │ + activity_mode  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
        │                         │                         │
        │                         │                         │
        ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   CSV Table      │      │   All Charts     │      │   All Calendars  │
│   Displayed      │      │   Rendered       │      │   Rendered       │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

---

## External Integrations

### Hyperliquid Info API

| Property | Value |
|----------|-------|
| Base URL | `https://api.hyperliquid.xyz/info` |
| Method | POST |
| Content-Type | application/json |
| Authentication | None required |
| Rate Limiting | Implemented client-side (50ms delay) |

### API Request/Response Formats

**Portfolio Request:**
```json
{
    "type": "portfolio",
    "user": "0x621c5551678189b9a6c94d929924c225ff1d63ab"
}
```

**Portfolio Response (simplified):**
```json
[
    ["day", {
        "accountValueHistory": [[timestamp, "125000.50"], ...],
        "pnlHistory": [[timestamp, "8500.25"], ...],
        "vlm": "1250000.00"
    }],
    ["perpDay", {
        "accountValueHistory": [[timestamp, "95000.00"], ...],
        "pnlHistory": [[timestamp, "7200.00"], ...],
        "vlm": "1100000.00"
    }]
]
```

**User Fills Request:**
```json
{
    "type": "userFillsByTime",
    "user": "0x621c5551678189b9a6c94d929924c225ff1d63ab",
    "startTime": 1704067200000,
    "endTime": 1735689600000
}
```

**User Fills Response (simplified):**
```json
[
    {
        "coin": "BTC",
        "side": "B",
        "dir": "Open Long",
        "sz": "0.5",
        "px": "45000.00",
        "closedPnl": "0",
        "time": 1704067200000,
        "fee": "22.50"
    }
]
```

---

## Module Dependencies

### Import Dependency Graph

```
                                    app.py
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
      streamlit (st)           pandas (pd)               plotly.graph_objects
            │                  numpy (np)                plotly.express
            │                          │                          │
            │                          │                          │
            │            ┌─────────────┴─────────────┐            │
            │            │                           │            │
            │            ▼                           ▼            │
            │   src/api/hyperliquid          src/utils/formatters │
            │            │                           │            │
            │            │                           │            │
            │    ┌───────┴───────┐                   │            │
            │    │               │                   │            │
            │    ▼               ▼                   │            │
            │  requests      dataclasses             │            │
            │  datetime      typing                  │            │
            │                                        │            │
            └────────────────────┴────────────────────────────────┘


src/components/charts.py (partially used)
            │
            ├── plotly.graph_objects
            ├── plotly.subplots
            ├── pandas
            ├── typing
            ├── src/api/hyperliquid (PortfolioBreakdown)
            └── src/utils/formatters (format_currency, format_percentage)
```

### External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >= 1.31.0 | Web application framework |
| plotly | >= 5.18.0 | Interactive visualizations |
| pandas | >= 2.0.0 | Data manipulation |
| requests | >= 2.31.0 | HTTP client for API calls |
| python-dotenv | >= 1.0.0 | Environment configuration |
| numpy | (via pandas) | Numerical operations |

### Internal Dependencies

```
app.py
├── src/api/hyperliquid
│   ├── HyperliquidClient
│   ├── get_mock_portfolio_breakdown
│   └── TradeFill
└── src/utils/formatters
    └── format_currency

src/api/hyperliquid
├── requests.Session
├── dataclasses.dataclass
├── datetime.datetime
└── typing (Optional, List)

src/components/charts (currently minimal usage)
├── src/api/hyperliquid.PortfolioBreakdown
└── src/utils/formatters

src/utils/formatters
└── (no internal dependencies)
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DEPLOYMENT OPTIONS                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐     ┌─────────────────────────┐
│     Local Development   │     │    Cloud Deployment     │
│                         │     │                         │
│  ┌───────────────────┐  │     │  ┌───────────────────┐  │
│  │   Python 3.8+     │  │     │  │ Streamlit Cloud   │  │
│  │   Virtual Env     │  │     │  │ or                │  │
│  │                   │  │     │  │ Docker Container  │  │
│  │   streamlit run   │  │     │  │ or                │  │
│  │   app.py          │  │     │  │ Heroku/Railway    │  │
│  └───────────────────┘  │     │  └───────────────────┘  │
│           │             │     │           │             │
│           ▼             │     │           ▼             │
│  localhost:8501         │     │  https://app.domain    │
│                         │     │                         │
└─────────────────────────┘     └─────────────────────────┘
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │   Hyperliquid API       │
              │   (External Service)    │
              │                         │
              │   No authentication     │
              │   Public endpoints      │
              └─────────────────────────┘
```

---

## Security Considerations

| Consideration | Current State | Recommendation |
|---------------|---------------|----------------|
| API Keys | None required | N/A |
| User Data | Client-side only | Session data not persisted |
| Input Validation | Wallet addresses from CSV | Validate format if user input added |
| Rate Limiting | 50ms delay between calls | Consider exponential backoff |
| Error Exposure | Generic error messages | Appropriate for user-facing app |
