# Codebase Summary

**Project:** Hyperliquid Whale Screener Dashboard
**Language:** Python 3.8+
**Framework:** Streamlit
**Total Lines of Code:** ~1,900 lines

---

## Project Structure Overview

```
demo-port/
├── app.py                          # Main application (1,602 lines)
├── requirements.txt                # Dependencies (6 lines)
├── wallet_address.txt              # Whale wallet data (117 lines, 116 wallets)
├── README.md                       # Project readme
├── docs/                           # Documentation
│   ├── project-overview-pdr.md     # Product requirements
│   ├── codebase-summary.md         # This file
│   ├── code-standards.md           # Coding standards
│   └── system-architecture.md      # Architecture docs
├── plans/
│   └── reports/
│       └── brainstorm-*.md         # Planning documents
└── src/
    ├── api/
    │   └── hyperliquid.py          # API client (238 lines)
    ├── components/
    │   └── charts.py               # Reusable charts (185 lines)
    └── utils/
        └── formatters.py           # Number formatting (47 lines)
```

---

## File Descriptions

### Root Files

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `app.py` | 65 KB | 1,602 | Main Streamlit application containing all dashboard views, charts, and UI logic |
| `requirements.txt` | 150 B | 6 | Python dependencies with minimum version constraints |
| `wallet_address.txt` | 12 KB | 117 | CSV file containing 116 whale wallet addresses with labels, entity types, and metrics |

### Source Modules

| File | Lines | Description |
|------|-------|-------------|
| `src/api/hyperliquid.py` | 238 | Hyperliquid API client with data classes and HTTP methods |
| `src/components/charts.py` | 185 | Reusable Plotly chart components (partially used, main charts in app.py) |
| `src/utils/formatters.py` | 47 | Number formatting utilities for currency and percentages |

---

## Module Responsibilities

### `app.py` - Main Application

**Primary Responsibilities:**
- Page configuration and custom CSS styling
- Sidebar controls (filters, time period, fetch button)
- Portfolio data fetching and state management
- All chart creation functions
- Data table rendering
- Session state handling

**Key Sections:**

| Section | Lines | Purpose |
|---------|-------|---------|
| Imports & Constants | 1-36 | Dependencies and color palette |
| Data Loading | 38-45 | `load_wallet_addresses()` - CSV parsing |
| Screening Chart | 48-179 | `create_screening_chart()` - Stacked bar charts |
| Heatmaps | 182-326 | Distribution heatmap generators |
| Histogram | 329-352 | `create_histogram()` - Distribution charts |
| Activity Calendar | 355-711 | GitHub-style activity heatmaps |
| All Wallets Heatmap | 714-944 | Combined wallet activity visualization |
| Page Config | 947-991 | Streamlit config and CSS |
| Main Function | 994-1602 | Core application logic and UI |

### `src/api/hyperliquid.py` - API Client

**Primary Responsibilities:**
- HTTP communication with Hyperliquid API
- Data class definitions for type safety
- Portfolio data parsing and transformation
- Trade fill fetching with pagination

**Classes:**

| Class | Purpose |
|-------|---------|
| `PortfolioMetrics` | Dataclass: account_value, pnl, volume |
| `PortfolioBreakdown` | Dataclass: total, perp, spot breakdown |
| `TradeFill` | Dataclass: individual trade record |
| `HyperliquidClient` | API client with session management |

**Methods:**

| Method | Purpose |
|--------|---------|
| `get_portfolio()` | Raw portfolio data fetch |
| `get_portfolio_breakdown()` | Parsed perp/spot breakdown |
| `get_user_fills()` | Recent trade fills (limit-based) |
| `get_user_fills_by_time()` | Trade fills by date range |
| `_extract_metrics()` | Helper to parse period data |

### `src/components/charts.py` - Chart Components

**Primary Responsibilities:**
- Reusable Plotly chart generation
- Consistent styling across charts
- Metric card data formatting

**Functions:**

| Function | Purpose |
|----------|---------|
| `create_portfolio_stacked_bar()` | Single-portfolio breakdown chart |
| `create_portfolio_metrics_cards()` | Metric card data dictionary |

### `src/utils/formatters.py` - Formatting Utilities

**Primary Responsibilities:**
- Currency formatting with K/M/B suffixes
- Percentage calculations
- Consistent number display

**Functions:**

| Function | Purpose |
|----------|---------|
| `format_currency()` | `$1.23M` style formatting |
| `format_number()` | `1.23M` style (no $ prefix) |
| `format_percentage()` | Calculate and format as `X.X%` |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────────────────────────────────────────┐   │
│  │   SIDEBAR   │     │                 MAIN CONTENT                     │   │
│  │             │     │                                                  │   │
│  │ ○ Filters   │     │  ┌────────────────────────────────────────────┐ │   │
│  │ ○ Time      │     │  │            SUMMARY METRICS                 │ │   │
│  │ ○ Fetch Btn │     │  │  Total Wallets | AUM | VCs | Retail        │ │   │
│  │             │     │  └────────────────────────────────────────────┘ │   │
│  └──────┬──────┘     │                                                  │   │
│         │            │  ┌────────────────────────────────────────────┐ │   │
│         │            │  │         PORTFOLIO BREAKDOWN                │ │   │
│         ▼            │  │    Stacked Bar Chart (Perp vs Spot)       │ │   │
│  ┌──────────────┐    │  └────────────────────────────────────────────┘ │   │
│  │  FETCH DATA  │    │                                                  │   │
│  │   Button     │────┼──►  ┌─────────────────────────────────────────┐ │   │
│  └──────────────┘    │     │          DISTRIBUTION MAPS              │ │   │
│                      │     │  Heatmaps: Value/Perp, Entity, PnL      │ │   │
│                      │     └─────────────────────────────────────────┘ │   │
│                      │                                                  │   │
│                      │  ┌────────────────────────────────────────────┐ │   │
│                      │  │          ACTIVITY CALENDAR                 │ │   │
│                      │  │   GitHub-style trade activity heatmap      │ │   │
│                      │  └────────────────────────────────────────────┘ │   │
│                      │                                                  │   │
│                      │  ┌────────────────────────────────────────────┐ │   │
│                      │  │           DETAILED DATA                    │ │   │
│                      │  │   Tables: Trades, Coins, Wallets           │ │   │
│                      │  └────────────────────────────────────────────┘ │   │
│                      └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐        ┌────────────────────────────────────────┐    │
│  │ wallet_address   │        │         st.session_state               │    │
│  │    .txt (CSV)    │        │                                        │    │
│  │                  │        │  ○ portfolio_data    (DataFrame)       │    │
│  │ 116 wallets      │        │  ○ activity_fills   (DataFrame)        │    │
│  │ Entity labels    │        │  ○ calendar_years   (List)             │    │
│  │ Account values   │        │  ○ activity_mode    (str)              │    │
│  │ ROI, PnL         │        │  ○ all_wallet_names (List)             │    │
│  └────────┬─────────┘        └──────────────────┬─────────────────────┘    │
│           │                                      │                          │
│           └──────────────┬───────────────────────┘                          │
│                          │                                                  │
│                          ▼                                                  │
│              ┌───────────────────────┐                                      │
│              │    HyperliquidClient  │                                      │
│              │                       │                                      │
│              │  get_portfolio()      │                                      │
│              │  get_portfolio_       │                                      │
│              │     breakdown()       │                                      │
│              │  get_user_fills()     │                                      │
│              │  get_user_fills_      │                                      │
│              │     by_time()         │                                      │
│              └───────────┬───────────┘                                      │
│                          │                                                  │
└──────────────────────────┼──────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL API                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌─────────────────────────────────┐                      │
│                    │   Hyperliquid Info API          │                      │
│                    │   https://api.hyperliquid.xyz   │                      │
│                    │                                 │                      │
│                    │   POST /info                    │                      │
│                    │   ├─ type: portfolio            │                      │
│                    │   ├─ type: userFills            │                      │
│                    │   └─ type: userFillsByTime      │                      │
│                    │                                 │                      │
│                    └─────────────────────────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Functions Reference

### Chart Functions (app.py)

| Function | Lines | Input | Output |
|----------|-------|-------|--------|
| `create_screening_chart()` | 48-179 | DataFrame, metric, height, mode | go.Figure |
| `create_value_perp_heatmap()` | 182-229 | DataFrame | go.Figure |
| `create_entity_perp_heatmap()` | 232-278 | DataFrame | go.Figure |
| `create_value_pnl_heatmap()` | 281-326 | DataFrame | go.Figure |
| `create_histogram()` | 329-352 | DataFrame, column, title, bins | go.Figure |
| `create_activity_calendar()` | 355-518 | DataFrame, year | go.Figure |
| `create_activity_calendar_range()` | 541-711 | DataFrame, from_year, to_year | go.Figure |
| `create_all_wallets_heatmap()` | 714-944 | DataFrame, years, wallet_names | go.Figure |

### API Methods (src/api/hyperliquid.py)

| Method | Lines | Input | Output |
|--------|-------|-------|--------|
| `get_portfolio()` | 47-66 | user_address | dict or None |
| `get_portfolio_breakdown()` | 68-110 | user_address, period | PortfolioBreakdown or None |
| `get_user_fills()` | 131-169 | user_address, limit | List[TradeFill] |
| `get_user_fills_by_time()` | 171-215 | user_address, start, end | List[TradeFill] |

### Utility Functions (src/utils/formatters.py)

| Function | Lines | Input | Output |
|----------|-------|-------|--------|
| `format_currency()` | 4-20 | value, decimals | str (`$1.23M`) |
| `format_number()` | 23-38 | value, decimals | str (`1.23M`) |
| `format_percentage()` | 41-46 | value, total | str (`50.0%`) |

---

## Dependencies Graph

```
app.py
├── streamlit (st)
├── pandas (pd)
├── numpy (np)
├── plotly.graph_objects (go)
├── plotly.express (px)
├── pathlib.Path
├── time
├── datetime
└── src/
    ├── api/hyperliquid
    │   ├── HyperliquidClient
    │   ├── get_mock_portfolio_breakdown
    │   └── TradeFill
    └── utils/formatters
        └── format_currency

src/api/hyperliquid.py
├── requests
├── typing (Optional, List)
├── dataclasses (dataclass)
└── datetime

src/components/charts.py
├── plotly.graph_objects (go)
├── plotly.subplots (make_subplots)
├── pandas (pd)
├── typing (Optional)
├── src/api/hyperliquid (PortfolioBreakdown)
└── src/utils/formatters (format_currency, format_percentage)

src/utils/formatters.py
└── (no dependencies - pure Python)
```

---

## Session State Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `portfolio_data` | pd.DataFrame | Cached portfolio breakdown for all fetched wallets |
| `activity_fills` | pd.DataFrame | Trade fills for activity calendar |
| `calendar_years` | List[int] | Selected year range for activity view |
| `activity_mode` | str | "single" or "all" wallet mode |
| `all_wallet_names` | List[str] | All wallet display names for heatmap |

---

## File Size Summary

| Category | Files | Total Lines |
|----------|-------|-------------|
| Application | 1 | 1,602 |
| API | 1 | 238 |
| Components | 1 | 185 |
| Utilities | 1 | 47 |
| Config | 2 | 123 |
| **Total** | **6** | **~2,200** |
