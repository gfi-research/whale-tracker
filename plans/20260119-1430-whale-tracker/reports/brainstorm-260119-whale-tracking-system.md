# Brainstorm Report: Whale Tracking System on Hyperliquid

**Date:** 2026-01-19
**Topic:** Architecture Analysis for Nansen-powered Whale Tracker
**Status:** ANALYSIS COMPLETE

---

## 1. Executive Summary

Your proposed approach is **architecturally sound** and leverages Nansen's pre-computed analytics effectively. However, there are **critical legal constraints** and **missing data gaps** that require attention before implementation.

**Key Findings:**
- 4/6 proposed endpoints are freely redistributable
- 2/6 have significant redistribution restrictions (smart-money endpoints)
- Existing codebase already has Nansen client + Hyperliquid integration ready
- Primary risk: Violating Nansen's Data Redistribution Policy

---

## 2. Endpoint-by-Endpoint Analysis

### 2.1 ALLOWED (No Restrictions) ✅

| Endpoint | Use Case | Redistribution |
|----------|----------|----------------|
| `/profiler/perp-positions` | Wallet positions, leverage, PnL, equity, margin | ✅ Allowed |
| `/profiler/perp-trades` | Historical trade data per wallet | ✅ Allowed |
| `/profiler/address/pnl-summary` | PnL cohort classification, win_rate | ✅ Allowed |

**These endpoints support:**
- Wallet List Table (Equity, Leverage, uPnL, Size Cohort)
- Position Details View
- PnL-based cohort classification (Extremely Profitable, etc.)

### 2.2 ALLOWED WITH ATTRIBUTION ✅ (attribution required)

| Endpoint | Use Case | Attribution |
|----------|----------|-------------|
| `/tgm/perp-screener` | Market-level smart money flows | Required: "Powered by Nansen" |
| `/tgm/perp-positions` | Token-level position aggregates | Required if showing SM data |

**These endpoints support:**
- Market Heatmap (Notional Long/Short by token)
- Token sentiment indicators (Bullish/Bearish based on SM flows)

### 2.3 PROHIBITED FOR REDISTRIBUTION 🚫

| Endpoint | Proposed Use | Issue |
|----------|--------------|-------|
| `/smart-money/perp-trades` | Real-time SM trade feed | **PROHIBITED** - Cannot display publicly |

**Critical:** Your proposed "Bước 3" uses `smart-money/perp-trades` which is explicitly **PROHIBITED** from redistribution. Displaying this data in a public dashboard violates Nansen ToS.

---

## 3. Proposed Architecture Assessment

### 3.1 What Works Well

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR PROPOSED FLOW - VALID COMPONENTS                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Wallet Classification                              │
│  ├── /profiler/address/pnl-summary ✅                       │
│  │   → realised_pnl_usd → Cohort (>$1M = Extremely Profit.) │
│  │   → win_rate → Display metric                            │
│  │                                                          │
│  ├── /profiler/perp-positions ✅                            │
│  │   → total_equity → Size Tag (Kraken/Whale/Shark)         │
│  │   → account_health → Risk indicator                      │
│                                                             │
│  Step 2: Position Tracking                                  │
│  ├── /profiler/perp-positions ✅                            │
│  │   → leverage_value (pre-computed)                        │
│  │   → unrealized_pnl_usd                                   │
│  │   → position_value_usd (Notional)                        │
│  │   → margin_used_usd                                      │
│                                                             │
│  Step 3: Market View                                        │
│  ├── /tgm/perp-screener ✅ (needs attribution)              │
│  │   → smart_money_volume                                   │
│  │   → smart_money_longs_count / shorts_count               │
│  │   → net_position_change                                  │
│  │                                                          │
│  └── /smart-money/perp-trades 🚫 BLOCKED                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 What Needs Modification

**Problem:** `/smart-money/perp-trades` cannot be displayed directly.

**Solution:** Replace with aggregated/transformed data:

```
ALTERNATIVE APPROACH FOR MARKET SENTIMENT
─────────────────────────────────────────
Option A: Use /tgm/perp-screener with only_smart_money=true
  → Returns aggregated SM volume, not individual trades
  → Shows which tokens SM is active in
  → Allowed with attribution

Option B: Build composite indicator (Nansen-approved approach)
  → Combine: perp-screener (30%) + funding rates (30%) + OI (40%)
  → Create custom "Whale Sentiment Score"
  → Significant transformation = redistribution allowed
```

---

## 4. Data Gap Analysis

### 4.1 Missing from Nansen API

| Feature Shown in Screenshot | Nansen Availability | Alternative |
|-----------------------------|---------------------|-------------|
| PERP BIAS (Bullish/Bearish) | Not directly provided | Calculate from position direction |
| Size-weighted sentiment | Not provided | Calculate: Σ(position_value × direction) |
| Wallet Labels/Names | `/label` endpoint (PROHIBITED) | Store custom labels locally |

### 4.2 Calculation Requirements

Despite leveraging Nansen, you'll still need to calculate:

```python
# 1. Perp Bias calculation (per wallet)
def calculate_perp_bias(positions):
    long_value = sum(p.position_value_usd for p in positions if p.size > 0)
    short_value = sum(abs(p.position_value_usd) for p in positions if p.size < 0)

    ratio = long_value / (long_value + short_value) if (long_value + short_value) > 0 else 0.5

    if ratio > 0.7: return "Extremely Bullish"
    if ratio > 0.55: return "Bullish"
    if ratio < 0.3: return "Extremely Bearish"
    if ratio < 0.45: return "Bearish"
    return "Neutral"

# 2. Market-level aggregation (for MARKETS tab)
def calculate_market_sentiment(token_positions):
    longs = sum(p.position_value_usd for p in token_positions if p.size > 0)
    shorts = sum(abs(p.position_value_usd) for p in token_positions if p.size < 0)

    return {
        "notional_long": longs,
        "notional_short": shorts,
        "long_pct": longs / (longs + shorts) * 100,
        "traders_long": len([p for p in token_positions if p.size > 0]),
        "traders_short": len([p for p in token_positions if p.size < 0])
    }
```

---

## 5. Recommended Architecture

### 5.1 Tech Stack (Leverage Existing)

```
RECOMMENDED STACK (from existing mvp/)
──────────────────────────────────────
Frontend: Vite + React 18 + TypeScript
  ├── shadcn/ui components (already configured in crypto-compass)
  ├── TanStack Query for data fetching
  ├── Recharts for visualizations
  └── Tailwind CSS with dark theme

Backend: Python API Layer
  ├── NansenClient (already in demo-port/api_clients/)
  ├── HyperliquidAPI (already in demo-port/src/api/)
  └── Extend for aggregation logic

Data:
  ├── Real-time: Nansen API
  ├── Cache: React Query (5min stale time)
  └── Historical: BigQuery (already configured)
```

### 5.2 Component Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    WHALE TRACKER DASHBOARD                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   WALLETS    │  │   MARKETS    │  │   LEADERBOARD   │  │
│  │    (186)     │  │    (216)     │  │                 │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  WALLET TABLE                                       │  │
│  │  ────────────────────────────────────────────────── │  │
│  │  Address | Equity | Bias | Position | Lev | uPnL   │  │
│  │  ────────────────────────────────────────────────── │  │
│  │  Data: /profiler/perp-positions (per wallet)       │  │
│  │  + /profiler/address/pnl-summary (win_rate, pnl)   │  │
│  │  Calc: Bias from position directions               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  MARKET HEATMAP                                     │  │
│  │  ────────────────────────────────────────────────── │  │
│  │  Token | Notional L/S | Traders | uPnL             │  │
│  │  ────────────────────────────────────────────────── │  │
│  │  Data: /tgm/perp-screener (with only_smart_money)  │  │
│  │  Attribution: "Powered by Nansen" required         │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
│  ⚠️  "Powered by Nansen API"                              │
└────────────────────────────────────────────────────────────┘
```

### 5.3 API Integration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA FLOW                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   [Wallet List - 116 addresses from existing file]          │
│                    │                                        │
│                    ▼                                        │
│   ┌────────────────────────────────────────┐               │
│   │  BATCH FETCH (parallel)                 │               │
│   │  ─────────────────────────────────────  │               │
│   │  For each wallet:                       │               │
│   │    /profiler/perp-positions            │               │
│   │    /profiler/address/pnl-summary       │               │
│   └────────────────────────────────────────┘               │
│                    │                                        │
│                    ▼                                        │
│   ┌────────────────────────────────────────┐               │
│   │  AGGREGATION LAYER (Backend)            │               │
│   │  ─────────────────────────────────────  │               │
│   │  - Calculate bias per wallet            │               │
│   │  - Assign size cohort                   │               │
│   │  - Aggregate by token                   │               │
│   └────────────────────────────────────────┘               │
│                    │                                        │
│                    ▼                                        │
│   ┌────────────────────────────────────────┐               │
│   │  MARKET DATA (Single call)              │               │
│   │  ─────────────────────────────────────  │               │
│   │  /tgm/perp-screener                    │               │
│   │    (only_smart_money=true)             │               │
│   └────────────────────────────────────────┘               │
│                    │                                        │
│                    ▼                                        │
│   [React Dashboard with 5min cache]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Risk Assessment

### 6.1 Legal/Compliance Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Violating smart-money redistribution | **HIGH** | Remove `/smart-money/perp-trades` usage |
| Missing attribution | Medium | Add "Powered by Nansen" footer |
| Rate limiting (4 req/sec) | Medium | Batch requests, use caching |
| API cost overruns | Medium | Monitor credit usage, optimize calls |

### 6.2 Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| N+1 query problem (116 wallets) | Medium | Batch API calls, aggressive caching |
| Data staleness | Low | 5min cache is acceptable for whale tracking |
| Missing wallet labels | Low | Build local label management system |

---

## 7. Implementation Phases

### Phase 1: Core Dashboard (MVP)
- [ ] Wallet table with equity, leverage, uPnL
- [ ] Position details modal
- [ ] Size cohort tagging (Kraken/Whale/Shark)
- [ ] Basic Nansen integration (perp-positions only)

### Phase 2: Analytics Layer
- [ ] PnL summary integration (win_rate, realized_pnl)
- [ ] Perp bias calculation
- [ ] Market aggregation view

### Phase 3: Market Intelligence
- [ ] Perp screener integration (with attribution)
- [ ] Token heatmap
- [ ] Composite sentiment indicator

### Phase 4: Advanced Features
- [ ] Custom wallet labels/notes
- [ ] Historical tracking (BigQuery)
- [ ] Alert system for large position changes

---

## 8. Specific Answers to Your Brief

### Q: Can I use `/profiler/address/pnl-summary` for cohort classification?
**A:** ✅ Yes. `realised_pnl_usd` and `win_rate` are available and redistributable.

### Q: Does Nansen provide leverage directly?
**A:** ✅ Yes. `/profiler/perp-positions` returns `leverage_value` pre-computed.

### Q: Can I use `/smart-money/perp-trades` for market sentiment?
**A:** 🚫 No. This endpoint is **PROHIBITED** from redistribution. Use `/tgm/perp-screener` with `only_smart_money=true` instead.

### Q: Do I need to calculate anything?
**A:** Partially. You need to calculate:
- Perp Bias (from position directions)
- Market aggregations (if not using perp-screener)
- Size cohort thresholds (but total_equity is provided)

---

## 9. Final Recommendation

**Proceed with modifications:**

1. **Remove** `/smart-money/perp-trades` from architecture
2. **Replace** with `/tgm/perp-screener` (only_smart_money=true)
3. **Add** Nansen attribution to UI
4. **Leverage** existing code from `demo-port/` and `crypto-compass/`
5. **Implement** backend aggregation layer for bias calculation

**Estimated complexity:** Medium
**API calls per refresh:** ~120 (116 wallets + market data)
**Nansen credits concern:** Monitor usage, consider caching strategy

---

## 10. Next Steps

1. Confirm you have Nansen API access with sufficient credits
2. Review existing NansenClient in `demo-port/api_clients/nansen_client.py`
3. Decide on frontend: extend crypto-compass or new project
4. Create implementation plan for Phase 1

---

*Report generated by Claude Code Brainstorm Agent*
