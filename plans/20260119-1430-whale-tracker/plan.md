# Whale Tracker Dashboard - Implementation Plan

**Created:** 2026-01-19
**Status:** READY FOR REVIEW
**Target:** `whale-website/`

---

## Overview

Build a whale tracking dashboard for Hyperliquid perp traders using Nansen API. Displays wallet positions, market sentiment, and aggregated analytics with pre-computed data from Nansen endpoints.

## Tech Stack

- **Frontend:** Vite + React 18 + TypeScript
- **UI:** shadcn/ui + Tailwind CSS (dark theme)
- **State:** TanStack Query (5min cache)
- **Charts:** Recharts (horizontal bars)
- **API:** Nansen REST API (direct calls)

## Key Constraints

- ✅ Use only redistributable Nansen endpoints
- 🚫 NO `/smart-money/perp-trades` (prohibited)
- ✅ Add "Powered by Nansen" attribution
- ✅ Leverage existing `crypto-compass` patterns

---

## Implementation Phases

| Phase | Name | Status | Progress | File |
|-------|------|--------|----------|------|
| 01 | Project Setup | ⬜ Pending | 0% | [phase-01-project-setup.md](./phase-01-project-setup.md) |
| 02 | API Integration | ⬜ Pending | 0% | [phase-02-api-integration.md](./phase-02-api-integration.md) |
| 03 | Wallet Table | ⬜ Pending | 0% | [phase-03-wallet-table.md](./phase-03-wallet-table.md) |
| 04 | Market View | ⬜ Pending | 0% | [phase-04-market-view.md](./phase-04-market-view.md) |
| 05 | Polish & Deploy | ⬜ Pending | 0% | [phase-05-polish-deploy.md](./phase-05-polish-deploy.md) |

---

## Data Flow

```
[210 Wallet Addresses]
        │
        ▼
┌─────────────────────────┐
│  Nansen API             │
│  /profiler/perp-positions│
│  /profiler/pnl-summary   │
│  /tgm/perp-screener      │
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  Calculations           │
│  - Perp Bias            │
│  - Size Cohort          │
│  - Market Aggregations  │
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  Dashboard UI           │
│  - Wallet Table         │
│  - Market Heatmap       │
│  - Position Modal       │
└─────────────────────────┘
```

---

## Key Components

1. **WalletTable** - Main table with sorting, 210 wallets
2. **MarketTable** - Token aggregates with Long/Short bars
3. **PositionModal** - Wallet position details
4. **BiasIndicator** - Bullish/Bearish badge
5. **CohortBadge** - Kraken/Whale/Shark icons

---

## Success Criteria

- [ ] Dashboard loads 210 wallets in <3s
- [ ] Wallet table sortable by all columns
- [ ] Market tab shows token aggregates
- [ ] Position modal displays details
- [ ] Nansen attribution visible
- [ ] Dark theme matches screenshots

---

## Related Documents

- [Brainstorm Report](./reports/brainstorm-260119-whale-tracking-system.md)
- [Nansen API Docs](https://docs.nansen.ai/api/hyperliquid-apis)
