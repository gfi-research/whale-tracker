# Phase 04: Market View

**Parent:** [plan.md](./plan.md)
**Dependencies:** Phase 01, Phase 02
**Docs:** [shadcn/ui Tabs](https://ui.shadcn.com/docs/components/tabs)

---

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-19 |
| Description | Build market tab with token aggregates and horizontal bars |
| Priority | MEDIUM |
| Implementation | ⬜ Pending |
| Review | ⬜ Pending |

---

## Key Insights

- MARKETS tab shows token-level aggregates
- Horizontal bars show Long vs Short split
- Columns: Token, Notional, Traders, Unrealized PnL
- Data from `/tgm/perp-screener` with `only_smart_money=true`
- Requires "Powered by Nansen" attribution

---

## Requirements

1. Market table with token rows
2. HorizontalBar component for Long/Short
3. Tabs navigation (WALLETS | MARKETS)
4. Market bias indicator per token
5. Attribution footer

---

## Architecture

```
src/components/
├── MarketTable.tsx           # Token aggregate table
├── HorizontalBar.tsx         # Long/Short progress bar
├── MarketBiasLabel.tsx       # Bullish/Bearish per token
├── DashboardTabs.tsx         # Tab navigation
└── AttributionFooter.tsx     # "Powered by Nansen"
```

---

## Related Code Files

| File | Purpose |
|------|---------|
| Screenshots | Visual reference for bars |
| `hooks/useMarketData.ts` | Data source |

---

## Implementation Steps

### 4.1 Create HorizontalBar Component

```typescript
// src/components/HorizontalBar.tsx

import { cn } from '@/lib/utils';

interface HorizontalBarProps {
  leftValue: number;
  rightValue: number;
  leftLabel?: string;
  rightLabel?: string;
  leftColor?: string;
  rightColor?: string;
  showLabels?: boolean;
}

export function HorizontalBar({
  leftValue,
  rightValue,
  leftLabel,
  rightLabel,
  leftColor = 'bg-bullish',
  rightColor = 'bg-bearish',
  showLabels = true,
}: HorizontalBarProps) {
  const total = leftValue + rightValue;
  const leftPercent = total > 0 ? (leftValue / total) * 100 : 50;
  const rightPercent = 100 - leftPercent;

  return (
    <div className="w-full">
      {showLabels && (
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>{leftLabel}</span>
          <span>{rightLabel}</span>
        </div>
      )}
      <div className="flex h-2 rounded-full overflow-hidden bg-muted">
        <div
          className={cn('transition-all', leftColor)}
          style={{ width: `${leftPercent}%` }}
        />
        <div
          className={cn('transition-all', rightColor)}
          style={{ width: `${rightPercent}%` }}
        />
      </div>
      {showLabels && (
        <div className="flex justify-between text-xs mt-1">
          <span className="text-bullish">{leftPercent.toFixed(0)}% LONG</span>
          <span className="text-bearish">{rightPercent.toFixed(0)}% SHORT</span>
        </div>
      )}
    </div>
  );
}
```

### 4.2 Create MarketBiasLabel Component

```typescript
// src/components/MarketBiasLabel.tsx

import { ArrowUp, ArrowDown } from 'lucide-react';
import { cn } from '@/lib/utils';

type MarketBias = 'Bullish' | 'Bearish' | 'Slightly Bullish' | 'Slightly Bearish' | 'Very Bullish' | 'Very Bearish';

function calculateMarketBias(longPercent: number): MarketBias {
  if (longPercent >= 70) return 'Very Bullish';
  if (longPercent >= 55) return 'Bullish';
  if (longPercent >= 45) return 'Slightly Bullish';
  if (longPercent <= 30) return 'Very Bearish';
  if (longPercent <= 45) return 'Bearish';
  return 'Slightly Bearish';
}

export function MarketBiasLabel({ longPercent }: { longPercent: number }) {
  const bias = calculateMarketBias(longPercent);
  const isBullish = bias.includes('Bullish');
  const Icon = isBullish ? ArrowUp : ArrowDown;

  return (
    <div className={cn(
      'flex items-center gap-1 text-sm',
      isBullish ? 'text-bullish' : 'text-bearish'
    )}>
      {bias}
      <Icon className="h-3 w-3" />
    </div>
  );
}
```

### 4.3 Create MarketTable Component

```typescript
// src/components/MarketTable.tsx

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { HorizontalBar } from './HorizontalBar';
import { MarketBiasLabel } from './MarketBiasLabel';
import { formatCurrency } from '@/lib/format';
import type { MarketData } from '@/types/market';

interface MarketTableProps {
  markets: MarketData[];
  isLoading: boolean;
}

export function MarketTable({ markets, isLoading }: MarketTableProps) {
  if (isLoading) {
    return <MarketTableSkeleton />;
  }

  // Sort by total notional descending
  const sortedMarkets = [...markets].sort(
    (a, b) => (b.notionalLong + b.notionalShort) - (a.notionalLong + a.notionalShort)
  );

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[200px]">Market</TableHead>
          <TableHead>Notional</TableHead>
          <TableHead>Traders</TableHead>
          <TableHead>Unrealized PnL</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {sortedMarkets.map((market) => {
          const totalNotional = market.notionalLong + market.notionalShort;
          const longPercent = totalNotional > 0
            ? (market.notionalLong / totalNotional) * 100
            : 50;

          const totalTraders = market.tradersLong + market.tradersShort;
          const tradersLongPercent = totalTraders > 0
            ? (market.tradersLong / totalTraders) * 100
            : 50;

          return (
            <TableRow key={market.token}>
              <TableCell>
                <div className="flex flex-col">
                  <span className="font-medium">{market.token}</span>
                  <MarketBiasLabel longPercent={longPercent} />
                </div>
              </TableCell>
              <TableCell className="min-w-[250px]">
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-bullish">{formatCurrency(market.notionalLong)}</span>
                    <span className="text-bearish">{formatCurrency(market.notionalShort)}</span>
                  </div>
                  <HorizontalBar
                    leftValue={market.notionalLong}
                    rightValue={market.notionalShort}
                    showLabels={false}
                  />
                </div>
              </TableCell>
              <TableCell className="min-w-[200px]">
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>{market.tradersLong}</span>
                    <span>{market.tradersShort}</span>
                  </div>
                  <HorizontalBar
                    leftValue={market.tradersLong}
                    rightValue={market.tradersShort}
                    showLabels={false}
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{tradersLongPercent.toFixed(0)}% LONG</span>
                    <span>{(100 - tradersLongPercent).toFixed(0)}% SHORT</span>
                  </div>
                </div>
              </TableCell>
              <TableCell className="min-w-[200px]">
                <HorizontalBar
                  leftValue={Math.max(0, market.unrealizedPnl)}
                  rightValue={Math.max(0, -market.unrealizedPnl)}
                  leftLabel="PROFIT"
                  rightLabel="LOSS"
                  leftColor="bg-bullish"
                  rightColor="bg-bearish"
                />
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
```

### 4.4 Create DashboardTabs Component

```typescript
// src/components/DashboardTabs.tsx

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { WalletTable } from './WalletTable';
import { MarketTable } from './MarketTable';
import { useAllWalletPositions } from '@/hooks/useWalletPositions';
import { useMarketData } from '@/hooks/useMarketData';

export function DashboardTabs() {
  const { wallets, isLoading: walletsLoading } = useAllWalletPositions();
  const { data: markets, isLoading: marketsLoading } = useMarketData();

  return (
    <Tabs defaultValue="wallets" className="w-full">
      <TabsList>
        <TabsTrigger value="wallets">
          WALLETS <span className="ml-2 text-muted-foreground">{wallets.length}</span>
        </TabsTrigger>
        <TabsTrigger value="markets">
          MARKETS <span className="ml-2 text-muted-foreground">{markets?.length || 0}</span>
        </TabsTrigger>
      </TabsList>

      <TabsContent value="wallets" className="mt-4">
        <WalletTable wallets={wallets} isLoading={walletsLoading} />
      </TabsContent>

      <TabsContent value="markets" className="mt-4">
        <MarketTable markets={markets || []} isLoading={marketsLoading} />
      </TabsContent>
    </Tabs>
  );
}
```

### 4.5 Create AttributionFooter Component

```typescript
// src/components/AttributionFooter.tsx

export function AttributionFooter() {
  return (
    <footer className="mt-8 py-4 border-t border-border text-center">
      <p className="text-sm text-muted-foreground">
        Powered by{' '}
        <a
          href="https://nansen.ai"
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline"
        >
          Nansen API
        </a>
      </p>
      <p className="text-xs text-muted-foreground mt-1">
        Data refreshes every 5 minutes
      </p>
    </footer>
  );
}
```

### 4.6 Update App.tsx

```typescript
// src/App.tsx

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardTabs } from '@/components/DashboardTabs';
import { AttributionFooter } from '@/components/AttributionFooter';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <header className="mb-8">
            <h1 className="text-3xl font-bold">Whale Tracker</h1>
            <p className="text-muted-foreground">
              Track smart money positions on Hyperliquid
            </p>
          </header>

          <DashboardTabs />

          <AttributionFooter />
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
```

---

## Todo List

- [ ] Create HorizontalBar component
- [ ] Create MarketBiasLabel component
- [ ] Create MarketTable component
- [ ] Create DashboardTabs component
- [ ] Create AttributionFooter component
- [ ] Update App.tsx with tabs
- [ ] Style to match screenshots

---

## Success Criteria

- [ ] Tabs switch between WALLETS and MARKETS
- [ ] Market table shows token aggregates
- [ ] Horizontal bars render correctly
- [ ] Bias labels show correct sentiment
- [ ] Attribution footer visible

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Bar rendering edge cases | Low | Handle zero values |
| Missing market data | Low | Show skeleton/empty state |

---

## Security Considerations

- External links have `noopener noreferrer`

---

## Next Steps

→ [Phase 05: Polish & Deploy](./phase-05-polish-deploy.md)
