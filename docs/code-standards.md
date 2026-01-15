# Code Standards and Guidelines

**Project:** Hyperliquid Whale Screener Dashboard
**Last Updated:** January 2026

---

## Table of Contents

1. [Code Organization](#code-organization)
2. [Naming Conventions](#naming-conventions)
3. [Type Hints](#type-hints)
4. [Error Handling](#error-handling)
5. [Styling Guidelines](#styling-guidelines)
6. [Caching Strategy](#caching-strategy)
7. [Documentation Standards](#documentation-standards)

---

## Code Organization

### Directory Structure

```
demo-port/
├── app.py                  # Main entry point
├── requirements.txt        # Dependencies
├── wallet_address.txt      # Data file
├── docs/                   # Documentation
└── src/
    ├── api/                # External API clients
    ├── components/         # Reusable UI components
    └── utils/              # Utility functions
```

### Module Organization Principles

1. **Single Responsibility** - Each module handles one concern
   - `api/` - External data fetching
   - `components/` - Visualization components
   - `utils/` - Pure utility functions

2. **Import Order** (PEP 8)
   ```python
   # Standard library
   import time
   from datetime import datetime
   from pathlib import Path

   # Third-party
   import streamlit as st
   import pandas as pd
   import plotly.graph_objects as go

   # Local imports
   from src.api.hyperliquid import HyperliquidClient
   from src.utils.formatters import format_currency
   ```

3. **Constants at Top** - Define color palettes, config values after imports
   ```python
   # Color palette
   COLORS = {
       "perp": "#3bb5d3",
       "spot": "#7dd3fc",
       "background": "#1a2845",
   }
   ```

4. **Function Ordering**
   - Data loading functions first
   - Chart creation functions grouped by type
   - Main application logic last
   - `if __name__ == "__main__":` at end

---

## Naming Conventions

### Variables

| Type | Convention | Example |
|------|------------|---------|
| Constants | SCREAMING_SNAKE_CASE | `COLORS`, `HEATMAP_COLORSCALE` |
| Variables | snake_case | `wallet_address`, `portfolio_df` |
| DataFrames | suffix `_df` | `filtered_df`, `fills_df` |
| Figures | suffix `_fig` or `fig` | `fig`, `all_wallets_fig` |

### Functions

| Type | Convention | Example |
|------|------------|---------|
| Public functions | snake_case verb | `create_screening_chart()` |
| Helper functions | prefix `_` | `_extract_metrics()` |
| Data loaders | prefix `load_` | `load_wallet_addresses()` |
| Chart creators | prefix `create_` | `create_histogram()` |
| Formatters | prefix `format_` | `format_currency()` |

### Classes

| Type | Convention | Example |
|------|------------|---------|
| Data classes | PascalCase | `PortfolioMetrics`, `TradeFill` |
| Client classes | PascalCase + Client | `HyperliquidClient` |

### Files

| Type | Convention | Example |
|------|------------|---------|
| Python modules | snake_case | `hyperliquid.py`, `formatters.py` |
| Data files | snake_case | `wallet_address.txt` |
| Documentation | kebab-case | `code-standards.md` |

---

## Type Hints

### Required Type Hints

All functions must include type hints for parameters and return values:

```python
def create_screening_chart(
    df: pd.DataFrame,
    metric: str = "value",
    height: int = 800,
    mode: str = "value"
) -> go.Figure:
    """Create a stacked horizontal bar chart for all wallets."""
    ...
```

### Data Classes

Use `@dataclass` decorator for structured data:

```python
from dataclasses import dataclass

@dataclass
class PortfolioMetrics:
    """Portfolio metrics for a specific time period."""
    account_value: float
    pnl: float
    volume: float
```

### Optional Types

Use `Optional` from typing for nullable values:

```python
from typing import Optional, List

def get_portfolio(self, user_address: str) -> Optional[dict]:
    """Returns dict or None if error."""
    ...

def get_user_fills(self, user_address: str) -> List[TradeFill]:
    """Returns list, empty if no results."""
    ...
```

### Common Type Patterns

```python
# DataFrames
df: pd.DataFrame

# Plotly figures
fig: go.Figure

# Lists with specific types
fills: List[TradeFill]
wallets: List[str]

# Dictionaries
colors: dict[str, str]
period_data: dict

# Optional values
year: Optional[int] = None
```

---

## Error Handling

### API Error Handling

Wrap API calls in try-except blocks, return safe defaults:

```python
def get_portfolio(self, user_address: str) -> Optional[dict]:
    try:
        response = self.session.post(self.BASE_URL, json={...})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching portfolio: {e}")
        return None
```

### Data Processing Errors

Handle missing or malformed data gracefully:

```python
for fill in raw_fills:
    try:
        fills.append(TradeFill(
            coin=fill.get("coin", ""),
            size=float(fill.get("sz", 0)),
            ...
        ))
    except (ValueError, TypeError):
        continue  # Skip malformed records
```

### UI Error Handling

Display user-friendly error messages:

```python
if wallets_df is None:
    st.error("Could not load wallet addresses from wallet_address.txt")
    return

if not results:
    st.error("No data fetched. Try again.")
```

### Division by Zero

Prevent division by zero in calculations:

```python
# Using replacement
total = total.replace(0, 1)  # Avoid division by zero
perp_pct = df[perp_col].abs() / total * 100

# Using conditional
if total == 0:
    return "0%"
pct = (value / total) * 100
```

---

## Styling Guidelines

### Color Palette

```python
COLORS = {
    "perp": "#3bb5d3",       # Primary cyan - perpetual futures
    "spot": "#7dd3fc",       # Light blue - spot trading
    "background": "#1a2845", # Dark blue - main background
    "text": "#e2e8f0",       # Light gray - text color
    "grid": "#3a4556",       # Muted gray - grid lines
    "positive": "#22c55e",   # Green - profit/long
    "negative": "#e74c3c",   # Red - loss/short
}
```

### Heatmap Color Scale

```python
HEATMAP_COLORSCALE = [
    [0, "#1a2845"],      # Dark blue - lowest
    [0.25, "#1e3a5f"],   # Navy
    [0.5, "#3bb5d3"],    # Cyan
    [0.75, "#7dd3fc"],   # Light blue
    [1, "#e2e8f0"]       # Off-white - highest
]
```

### Activity Calendar Colors

```python
activity_colorscale = [
    [0, "#ef4444"],      # Bright red (short heavy)
    [0.20, "#f87171"],   # Red
    [0.40, "#fca5a5"],   # Light red
    [0.48, "#0f172a"],   # Dark (no activity)
    [0.52, "#0f172a"],   # Dark (no activity)
    [0.60, "#86efac"],   # Light green
    [0.80, "#4ade80"],   # Green
    [1, "#22c55e"]       # Bright green (long heavy)
]
```

### Chart Layout Standards

```python
fig.update_layout(
    # Transparent backgrounds for dark theme
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",

    # Consistent font
    font=dict(
        family="Inter, sans-serif",
        size=14,
        color=COLORS["text"]
    ),

    # Horizontal legend at top
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor="rgba(0,0,0,0)",
    ),

    # Hover label styling
    hoverlabel=dict(
        bgcolor=COLORS["background"],
        font_size=13,
        bordercolor=COLORS["perp"]
    ),
)
```

### Custom CSS

```css
/* Main app background */
.stApp { background-color: #1a2845; }

/* Sidebar background */
[data-testid="stSidebar"] { background-color: #1e2c42; }

/* Headings */
h1, h2, h3 { color: #e2e8f0 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #1e2c42;
    border: 1px solid #3a4556;
    border-radius: 8px;
    padding: 16px;
}

/* Primary button */
.stButton > button {
    background-color: #3bb5d3;
    color: #1a2845;
    border: none;
    font-weight: 600;
}
.stButton > button:hover { background-color: #7dd3fc; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background-color: #1e2c42;
    border-radius: 8px;
    color: #e2e8f0;
}
.stTabs [aria-selected="true"] {
    background-color: #3bb5d3;
    color: #1a2845;
}
```

---

## Caching Strategy

### When to Use Caching

1. **Static Data Loading** - CSV files that don't change during session
2. **Expensive Computations** - Complex DataFrame operations
3. **NOT for API calls** - Real-time data should be fetched fresh

### Cache Decorator Usage

```python
@st.cache_data
def load_wallet_addresses():
    """Load wallet addresses from CSV file.

    Cached because:
    - File doesn't change during session
    - Called multiple times (sidebar, main content)
    - Parsing is relatively expensive for 116 rows
    """
    csv_path = Path(__file__).parent / "wallet_address.txt"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        return df
    return None
```

### Cache Configuration

```python
# Default TTL (time-to-live) - data persists for session
@st.cache_data
def load_static_data(): ...

# With explicit TTL for data that should refresh
@st.cache_data(ttl=3600)  # 1 hour
def load_semi_static_data(): ...

# Clear cache when data changes
st.cache_data.clear()
```

### Session State for Dynamic Data

```python
# Store fetched API data in session state (not cache)
if results:
    st.session_state.portfolio_data = pd.DataFrame(results)

# Access later without re-fetching
if "portfolio_data" in st.session_state:
    portfolio_df = st.session_state.portfolio_data.copy()
```

---

## Documentation Standards

### Module Docstrings

```python
"""Hyperliquid API client for fetching portfolio data.

This module provides:
- HyperliquidClient class for API communication
- Data classes for type-safe portfolio handling
- Mock data generator for testing
"""
```

### Function Docstrings

```python
def create_screening_chart(
    df: pd.DataFrame,
    metric: str = "value",
    height: int = 800,
    mode: str = "value"
) -> go.Figure:
    """Create a stacked horizontal bar chart for all wallets.

    Args:
        df: DataFrame with wallet data containing columns:
            - display_name: Wallet label
            - perp_value, spot_value: Position values
            - total_value: Sum of perp + spot
        metric: One of "value", "pnl", or "volume"
        height: Chart height in pixels
        mode: "value" for absolute values, "percentage" for 100% stacked

    Returns:
        Plotly Figure object configured for dark theme display

    Example:
        >>> fig = create_screening_chart(portfolio_df, metric="value", mode="percentage")
        >>> st.plotly_chart(fig)
    """
```

### Class Docstrings

```python
@dataclass
class PortfolioMetrics:
    """Portfolio metrics for a specific time period.

    Attributes:
        account_value: Total account value in USD
        pnl: Profit and loss for the period
        volume: Trading volume for the period
    """
    account_value: float
    pnl: float
    volume: float
```

### Inline Comments

```python
# Use inline comments sparingly, for non-obvious logic:

# Rule 1: No activity -> dark (0.5 on color scale)
if total_val == 0:
    display_values[i, j] = 0.5

# Avoid division by zero by replacing zeros with 1
total = total.replace(0, 1)

# Convert milliseconds timestamp to Python datetime
timestamp=datetime.fromtimestamp(fill.get("time", 0) / 1000)
```

---

## Code Examples

### Complete Function Example

```python
@st.cache_data
def load_wallet_addresses() -> Optional[pd.DataFrame]:
    """Load wallet addresses from CSV file.

    Reads the wallet_address.txt CSV file containing whale wallet
    addresses with their labels, entity types, and baseline metrics.

    Returns:
        DataFrame with columns:
            - trader_address_label: Human-readable wallet name
            - Entity: Category (VCs, MM, retail)
            - trader_address: Ethereum address (0x...)
            - account_value: Account value from CSV
            - roi: Return on investment
            - total_pnl(unrealize profit): Unrealized PnL

        Returns None if file doesn't exist.
    """
    csv_path = Path(__file__).parent / "wallet_address.txt"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        return df
    return None
```

### Complete Data Class Example

```python
@dataclass
class TradeFill:
    """A single trade fill from Hyperliquid.

    Represents one executed trade with all associated metadata
    including pricing, sizing, and P&L information.

    Attributes:
        coin: Trading pair symbol (e.g., "BTC", "ETH")
        side: "B" (buy) or "A" (ask/sell)
        direction: Human-readable direction:
            - "Open Long": New long position
            - "Close Long": Exit long position
            - "Open Short": New short position
            - "Close Short": Exit short position
        size: Position size in base currency
        price: Execution price in USD
        pnl: Realized profit/loss from this trade
        timestamp: Trade execution time
        fee: Trading fee paid
    """
    coin: str
    side: str
    direction: str
    size: float
    price: float
    pnl: float
    timestamp: datetime
    fee: float
```
