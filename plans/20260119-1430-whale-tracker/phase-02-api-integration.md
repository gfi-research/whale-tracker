# Phase 02: API Integration

**Parent:** [plan.md](./plan.md)
**Dependencies:** Phase 01
**Docs:** [Nansen API](https://docs.nansen.ai/api/hyperliquid-apis)

---

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-19 |
| Description | Create Nansen API client and React Query hooks |
| Priority | HIGH |
| Implementation | ⬜ Pending |
| Review | ⬜ Pending |

---

## Key Insights

- Nansen API uses POST requests with JSON body
- API key in header: `apiKey: YOUR_KEY`
- `/profiler/perp-positions` - per wallet, no pagination
- `/tgm/perp-screener` - market data, needs date range
- Rate limit: ~4 req/sec, use batching

---

## Requirements

1. TypeScript Nansen API client
2. Type definitions for API responses
3. React Query hooks with caching
4. Batch fetching for 210 wallets
5. Calculation utilities (bias, cohort)

---

## Architecture

```
src/
├── lib/
│   ├── nansen-client.ts    # API client class
│   └── calculations.ts      # Bias, cohort logic
├── hooks/
│   ├── useWalletPositions.ts
│   ├── useMarketData.ts
│   └── useWalletPnl.ts
└── types/
    └── nansen.ts            # API response types
```

---

## Related Code Files

| File | Purpose |
|------|---------|
| `demo-port/api_clients/nansen_client.py` | Reference implementation |
| `crypto-compass/src/hooks/useCryptoData.ts` | Query patterns |

---

## Implementation Steps

### 2.1 Create Type Definitions

```typescript
// src/types/nansen.ts

export interface PerpPosition {
  token_symbol: string;
  size: string;              // negative = short
  entry_price_usd: string;
  leverage_value: number;
  leverage_type: string;
  position_value_usd: string;
  unrealized_pnl_usd: string;
  margin_used_usd: string;
  liquidation_price_usd: string;
  return_on_equity: string;
}

export interface PerpPositionsResponse {
  data: {
    asset_positions: Array<{
      position: PerpPosition;
      position_type: string;
    }>;
    margin_summary_account_value_usd: string;
    margin_summary_total_margin_used_usd: string;
    withdrawable_usd: string;
    timestamp: number;
  };
}

export interface PnlSummaryResponse {
  data: {
    realised_pnl_usd: number;
    win_rate: number;
    total_trades: number;
    // ... other fields
  };
}

export interface PerpScreenerItem {
  token_symbol: string;
  buy_sell_pressure: number;
  buy_volume: number;
  sell_volume: number;
  volume: number;
  open_interest: number;
  mark_price: number;
  funding: number;
  trader_count: number;
  // Smart money fields (when only_smart_money=true)
  smart_money_volume?: number;
  smart_money_longs_count?: number;
  smart_money_shorts_count?: number;
  current_smart_money_position_longs_usd?: number;
  current_smart_money_position_shorts_usd?: number;
  net_position_change?: number;
}
```

### 2.2 Create Nansen Client

```typescript
// src/lib/nansen-client.ts

const NANSEN_BASE_URL = 'https://api.nansen.ai/api/v1';

class NansenClient {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  private async request<T>(endpoint: string, data: object): Promise<T> {
    const response = await fetch(`${NANSEN_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'apiKey': this.apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`Nansen API error: ${response.status}`);
    }
    return response.json();
  }

  async getPerpPositions(address: string) {
    return this.request<PerpPositionsResponse>('/profiler/perp-positions', {
      address,
    });
  }

  async getPnlSummary(address: string, chain: string = 'hyperliquid') {
    return this.request<PnlSummaryResponse>('/profiler/address/pnl-summary', {
      address,
      chain,
    });
  }

  async getPerpScreener(onlySmartMoney: boolean = true) {
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    return this.request<{ data: PerpScreenerItem[] }>('/tgm/perp-screener', {
      date: {
        from: weekAgo.toISOString(),
        to: now.toISOString(),
      },
      only_smart_money: onlySmartMoney,
      pagination: { page: 1, per_page: 100 },
    });
  }
}

export const nansenClient = new NansenClient(
  import.meta.env.VITE_NANSEN_API_KEY
);
```

### 2.3 Create Calculation Utilities

```typescript
// src/lib/calculations.ts

import { PerpPosition } from '@/types/nansen';

export type PerpBias =
  | 'Extremely Bullish'
  | 'Bullish'
  | 'Neutral'
  | 'Bearish'
  | 'Extremely Bearish';

export type SizeCohort = 'Kraken' | 'Whale' | 'Shark' | 'Fish';

export function calculatePerpBias(positions: PerpPosition[]): PerpBias {
  let longValue = 0;
  let shortValue = 0;

  for (const pos of positions) {
    const size = parseFloat(pos.size);
    const value = Math.abs(parseFloat(pos.position_value_usd));

    if (size > 0) longValue += value;
    else shortValue += value;
  }

  const total = longValue + shortValue;
  if (total === 0) return 'Neutral';

  const ratio = longValue / total;

  if (ratio >= 0.8) return 'Extremely Bullish';
  if (ratio >= 0.6) return 'Bullish';
  if (ratio <= 0.2) return 'Extremely Bearish';
  if (ratio <= 0.4) return 'Bearish';
  return 'Neutral';
}

export function calculateSizeCohort(totalEquityUsd: number): SizeCohort {
  if (totalEquityUsd >= 50_000_000) return 'Kraken';
  if (totalEquityUsd >= 10_000_000) return 'Whale';
  if (totalEquityUsd >= 1_000_000) return 'Shark';
  return 'Fish';
}

export function aggregatePositions(positions: PerpPosition[]) {
  let totalPositionValue = 0;
  let totalUnrealizedPnl = 0;
  let weightedLeverage = 0;

  for (const pos of positions) {
    const value = Math.abs(parseFloat(pos.position_value_usd));
    totalPositionValue += value;
    totalUnrealizedPnl += parseFloat(pos.unrealized_pnl_usd);
    weightedLeverage += pos.leverage_value * value;
  }

  return {
    totalPositionValue,
    totalUnrealizedPnl,
    avgLeverage: totalPositionValue > 0
      ? weightedLeverage / totalPositionValue
      : 0,
  };
}
```

### 2.4 Create React Query Hooks

```typescript
// src/hooks/useWalletPositions.ts

import { useQueries, useQuery } from '@tanstack/react-query';
import { nansenClient } from '@/lib/nansen-client';
import { WHALE_WALLETS } from '@/data/wallets';
import { calculatePerpBias, calculateSizeCohort, aggregatePositions } from '@/lib/calculations';

export function useAllWalletPositions() {
  const queries = useQueries({
    queries: WHALE_WALLETS.map((wallet) => ({
      queryKey: ['perp-positions', wallet.address],
      queryFn: () => nansenClient.getPerpPositions(wallet.address),
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
    })),
  });

  const isLoading = queries.some((q) => q.isLoading);
  const isError = queries.some((q) => q.isError);

  const wallets = queries.map((query, index) => {
    const wallet = WHALE_WALLETS[index];
    const data = query.data?.data;

    if (!data) {
      return {
        ...wallet,
        equity: 0,
        bias: 'Neutral' as const,
        positionValue: 0,
        leverage: 0,
        unrealizedPnl: 0,
        sizeCohort: 'Fish' as const,
        positions: [],
      };
    }

    const positions = data.asset_positions.map((ap) => ap.position);
    const equity = parseFloat(data.margin_summary_account_value_usd);
    const agg = aggregatePositions(positions);

    return {
      ...wallet,
      equity,
      bias: calculatePerpBias(positions),
      positionValue: agg.totalPositionValue,
      leverage: agg.avgLeverage,
      unrealizedPnl: agg.totalUnrealizedPnl,
      sizeCohort: calculateSizeCohort(equity),
      positions,
    };
  });

  return { wallets, isLoading, isError };
}
```

```typescript
// src/hooks/useMarketData.ts

import { useQuery } from '@tanstack/react-query';
import { nansenClient } from '@/lib/nansen-client';

export function useMarketData() {
  return useQuery({
    queryKey: ['perp-screener'],
    queryFn: () => nansenClient.getPerpScreener(true),
    staleTime: 5 * 60 * 1000,
    select: (data) => {
      return data.data.map((item) => ({
        token: item.token_symbol,
        notionalLong: item.current_smart_money_position_longs_usd || 0,
        notionalShort: Math.abs(item.current_smart_money_position_shorts_usd || 0),
        tradersLong: item.smart_money_longs_count || 0,
        tradersShort: item.smart_money_shorts_count || 0,
        unrealizedPnl: item.net_position_change || 0,
        markPrice: item.mark_price,
        funding: item.funding,
      }));
    },
  });
}
```

---

## Todo List

- [ ] Create types/nansen.ts
- [ ] Create lib/nansen-client.ts
- [ ] Create lib/calculations.ts
- [ ] Create hooks/useWalletPositions.ts
- [ ] Create hooks/useMarketData.ts
- [ ] Test API calls with real key
- [ ] Verify rate limiting behavior

---

## Success Criteria

- [ ] API client fetches data successfully
- [ ] Bias calculation returns correct values
- [ ] Cohort tagging works for all thresholds
- [ ] React Query caches responses for 5min

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| 210 parallel requests | Medium | Batch with delay |
| API rate limiting | Medium | Use staleTime caching |
| CORS issues | Medium | Proxy if needed |

---

## Security Considerations

- API key only in env, never in code
- No logging of API key

---

## Next Steps

→ [Phase 03: Wallet Table](./phase-03-wallet-table.md)
