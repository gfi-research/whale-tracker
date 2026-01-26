# Whale Tracker Dashboard - API Endpoints Documentation

This document lists all API endpoints and parameters used in the Whale Tracker Dashboard.

---

## 1. Nansen API

**Base URL:** `https://api.nansen.ai`

**Authentication:**
```
Headers:
  apiKey: <NANSEN_API_KEY>
  Content-Type: application/json
  Accept: */*
```

### 1.1 Get Perp Leaderboard

Get perpetual trading leaderboard (top traders).

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /api/v1/perp-leaderboard` |
| **Cost** | 5 credits |
| **Use Case** | Fetch top whale traders by PnL |

**Request Payload:**
```json
{
  "date": {
    "from": "2024-01-01",    // YYYY-MM-DD format
    "to": "2024-01-31"       // YYYY-MM-DD format
  },
  "pagination": {
    "page": 1,
    "per_page": 50           // Max 100
  },
  "filters": {
    "account_value": {
      "min": 1000000         // Minimum account value in USD
    }
  },
  "order_by": [
    {
      "field": "total_pnl",  // Options: total_pnl, account_value, roi
      "direction": "DESC"    // ASC or DESC
    }
  ]
}
```

**Response Fields:**
- `trader_address` - Wallet address
- `trader_address_label` - Wallet label/name
- `account_value` - Account value in USD
- `total_pnl` - Total PnL
- `roi` - Return on investment

---

### 1.2 Get Wallet Positions (Profiler)

Get perpetual positions for a specific wallet address.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /api/v1/profiler/perp-positions` |
| **Cost** | 1 credit |
| **Use Case** | View individual whale's positions |

**Request Payload:**
```json
{
  "address": "0x...",        // Ethereum address
  "order_by": [
    {
      "field": "position_value_usd",
      "direction": "DESC"
    }
  ]
}
```

**Response Fields:**
- `margin_summary_account_value_usd` - Total account value
- `margin_summary_total_margin_used_usd` - Margin used
- `withdrawable_usd` - Withdrawable amount
- `margin_summary_total_net_liquidation_position_usd` - Net liquidation position
- `asset_positions[]` - Array of positions:
  - `position.token_symbol` - Token (BTC, ETH, etc.)
  - `position.size` - Position size (+ for Long, - for Short)
  - `position.position_value_usd` - Position value
  - `position.unrealized_pnl_usd` - Unrealized PnL
  - `position.entry_price_usd` - Entry price
  - `position.leverage_value` - Leverage multiplier
  - `position.leverage_type` - "cross" or "isolated"
  - `position.liquidation_price_usd` - Liquidation price
  - `position.return_on_equity` - ROE (decimal)

---

### 1.3 Get Token Positions (TGM)

Get all positions for a specific token across all traders.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /api/v1/tgm/perp-positions` |
| **Cost** | 5 credits |
| **Use Case** | Token position analysis, Long/Short ratio |

**Request Payload:**
```json
{
  "token_symbol": "BTC",     // Token symbol
  "label_type": "all_traders", // Options: all_traders, smart_money
  "pagination": {
    "page": 1,
    "per_page": 100          // Max 100
  },
  "filters": {
    "position_value_usd": {
      "min": 10000           // Minimum position value
    },
    "side": ["Long"]         // Optional: filter by side
  },
  "order_by": [
    {
      "field": "position_value_usd",
      "direction": "DESC"
    }
  ]
}
```

**Response Fields:**
- `address` - Trader wallet address
- `address_label` - Trader label
- `side` - "Long" or "Short"
- `position_value_usd` - Position value
- `leverage` - Leverage (e.g., "5X")
- `upnl_usd` - Unrealized PnL

---

## 2. Hyperliquid API

**Base URL:** `https://api.hyperliquid.xyz/info`

**Authentication:** None required (public API)

**Rate Limit:** ~4 requests/second recommended

---

### 2.1 Get Portfolio

Get user portfolio data including account value, PnL, and volume history.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /info` |
| **Cost** | Free |
| **Use Case** | Portfolio breakdown (Perp vs Spot) |

**Request Payload:**
```json
{
  "type": "portfolio",
  "user": "0x..."            // Ethereum address
}
```

**Response Structure:**
```json
[
  ["day", { "accountValueHistory": [[timestamp, value], ...], "pnlHistory": [...], "vlm": "..." }],
  ["perpDay", { ... }],
  ["week", { ... }],
  ["perpWeek", { ... }],
  ["month", { ... }],
  ["perpMonth", { ... }],
  ["allTime", { ... }],
  ["perpAllTime", { ... }]
]
```

**Period Options:**
- `day` / `perpDay` - 24 hours
- `week` / `perpWeek` - 7 days
- `month` / `perpMonth` - 30 days
- `allTime` / `perpAllTime` - All time

---

### 2.2 Get Open Orders

Get user's pending limit orders.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /info` |
| **Cost** | Free |
| **Use Case** | Show Order/Pos count per position |

**Request Payload:**
```json
{
  "type": "openOrders",
  "user": "0x..."            // Ethereum address
}
```

**Response Fields:**
```json
[
  {
    "coin": "BTC",           // Token symbol
    "limitPx": "50000.0",    // Limit price
    "oid": 123456,           // Order ID
    "side": "B",             // "B" (buy) or "A" (ask/sell)
    "sz": "0.1",             // Size
    "timestamp": 1706000000000
  }
]
```

---

### 2.3 Get User Fills

Get user's trade history (fills).

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /info` |
| **Cost** | Free |
| **Use Case** | Trading activity analysis |

**Request Payload:**
```json
{
  "type": "userFills",
  "user": "0x..."            // Ethereum address
}
```

**Response Fields:**
```json
[
  {
    "coin": "BTC",
    "side": "B",             // "B" (buy) or "A" (ask/sell)
    "dir": "Open Long",      // Direction: Open Long, Open Short, Close Long, Close Short
    "sz": "0.1",             // Size
    "px": "50000.0",         // Price
    "closedPnl": "0.0",      // Realized PnL (for closes)
    "time": 1706000000000,   // Timestamp in ms
    "fee": "5.0"             // Trading fee
  }
]
```

---

### 2.4 Get User Fills by Time

Get user's trade history within a specific time range.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /info` |
| **Cost** | Free |
| **Use Case** | Activity calendar, time-filtered analysis |

**Request Payload:**
```json
{
  "type": "userFillsByTime",
  "user": "0x...",           // Ethereum address
  "startTime": 1704067200000, // Start timestamp in ms
  "endTime": 1706745600000   // End timestamp in ms (optional)
}
```

**Note:** Returns max 2000 fills per request. Use pagination by adjusting `endTime` to oldest fill's timestamp - 1ms.

---

### 2.5 Get Clearinghouse State

Get user's current positions and account state.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /info` |
| **Cost** | Free |
| **Use Case** | Real-time position data |

**Request Payload:**
```json
{
  "type": "clearinghouseState",
  "user": "0x..."            // Ethereum address
}
```

**Response Fields:**
```json
{
  "assetPositions": [
    {
      "type": "oneWay",
      "position": {
        "coin": "BTC",
        "szi": "1000.0",           // Size (+ Long, - Short)
        "leverage": {
          "type": "cross",
          "value": 5
        },
        "entryPx": "91506.7",
        "positionValue": "90018000.0",
        "unrealizedPnl": "-1488767.29",
        "returnOnEquity": "-0.0813",
        "liquidationPx": null,
        "marginUsed": "18003600.0",
        "maxLeverage": 40
      }
    }
  ],
  "marginSummary": {
    "accountValue": "...",
    "totalMarginUsed": "...",
    "totalNtlPos": "..."
  }
}
```

---

## 3. API Credit Costs Summary (Nansen)

| Endpoint | Cost |
|----------|------|
| `/api/v1/perp-leaderboard` | 5 credits |
| `/api/v1/profiler/perp-positions` | 1 credit |
| `/api/v1/tgm/perp-positions` | 5 credits |
| `/api/v1/tgm/perp-screener` | 1 credit |

**Estimated costs for full dashboard:**
- Fetch 200 whale positions: ~200 credits
- Token position analysis (10 tokens): ~50 credits
- Total per session: ~250 credits

---

## 4. Environment Variables

```bash
# Required for Nansen API
NANSEN_API_KEY=your_api_key_here
```

For Streamlit Cloud, add to `secrets.toml`:
```toml
[API_KEYS]
NANSEN_API_KEY = "your_api_key_here"
```

---

## 5. Rate Limiting

### Nansen API
- No official rate limit documented
- Recommended: 1 request/second

### Hyperliquid API
- Rate limit: ~1200 requests/minute
- Recommended: 4 requests/second with exponential backoff on 429 errors

---

## 6. Data Structures

### TradeFill (Hyperliquid)
```python
@dataclass
class TradeFill:
    coin: str           # Token symbol
    side: str           # "B" (buy) or "A" (ask/sell)
    direction: str      # "Open Long", "Open Short", "Close Long", "Close Short"
    size: float         # Trade size
    price: float        # Execution price
    pnl: float          # Realized PnL
    timestamp: datetime # Trade time
    fee: float          # Trading fee
```

### PortfolioMetrics (Hyperliquid)
```python
@dataclass
class PortfolioMetrics:
    account_value: float
    pnl: float
    volume: float
```

---

*Last updated: January 2025*
