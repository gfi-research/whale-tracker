# Phase 03: Wallet Table

**Parent:** [plan.md](./plan.md)
**Dependencies:** Phase 01, Phase 02
**Docs:** [shadcn/ui Table](https://ui.shadcn.com/docs/components/table)

---

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-19 |
| Description | Build main wallet table with sorting and position modal |
| Priority | HIGH |
| Implementation | ⬜ Pending |
| Review | ⬜ Pending |

---

## Key Insights

- Table columns match screenshot: Address, Perp Equity, Perp Bias, Position Value, Leverage, Sum uPnL, Size Cohort
- Sortable by clicking column headers
- Click row to open position detail modal
- Address shows truncated with copy button
- Bias uses colored badges (green/red)
- Cohort shows icon + label

---

## Requirements

1. Sortable data table with 210 rows
2. Column formatting (currency, percentage)
3. BiasIndicator component (colored badge)
4. CohortBadge component (icon + label)
5. PositionModal for row click
6. Loading skeleton state

---

## Architecture

```
src/components/
├── WalletTable.tsx           # Main table
├── WalletTableRow.tsx        # Row with click handler
├── BiasIndicator.tsx         # Bullish/Bearish badge
├── CohortBadge.tsx           # Kraken/Whale/Shark
├── PositionModal.tsx         # Detail dialog
├── AddressCell.tsx           # Truncated + copy
└── TableSkeleton.tsx         # Loading state
```

---

## Related Code Files

| File | Purpose |
|------|---------|
| `crypto-compass/src/components/TokenTable.tsx` | Table pattern |
| `crypto-compass/src/components/ui/table.tsx` | shadcn table |

---

## Implementation Steps

### 3.1 Create BiasIndicator Component

```typescript
// src/components/BiasIndicator.tsx

import { Badge } from '@/components/ui/badge';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { PerpBias } from '@/lib/calculations';

const biasConfig = {
  'Extremely Bullish': { icon: ArrowUp, class: 'bg-bullish text-bullish-foreground' },
  'Bullish': { icon: ArrowUp, class: 'bg-bullish/70 text-bullish-foreground' },
  'Neutral': { icon: Minus, class: 'bg-neutral text-neutral-foreground' },
  'Bearish': { icon: ArrowDown, class: 'bg-bearish/70 text-bearish-foreground' },
  'Extremely Bearish': { icon: ArrowDown, class: 'bg-bearish text-bearish-foreground' },
};

export function BiasIndicator({ bias }: { bias: PerpBias }) {
  const config = biasConfig[bias];
  const Icon = config.icon;

  return (
    <Badge className={cn('gap-1', config.class)}>
      <Icon className="h-3 w-3" />
      {bias}
    </Badge>
  );
}
```

### 3.2 Create CohortBadge Component

```typescript
// src/components/CohortBadge.tsx

import { Badge } from '@/components/ui/badge';
import { Fish, Waves, Ship, Anchor } from 'lucide-react';
import type { SizeCohort } from '@/lib/calculations';

const cohortConfig = {
  Kraken: { icon: Anchor, class: 'bg-purple-500/20 text-purple-400' },
  Whale: { icon: Ship, class: 'bg-blue-500/20 text-blue-400' },
  Shark: { icon: Waves, class: 'bg-cyan-500/20 text-cyan-400' },
  Fish: { icon: Fish, class: 'bg-gray-500/20 text-gray-400' },
};

export function CohortBadge({ cohort }: { cohort: SizeCohort }) {
  const config = cohortConfig[cohort];
  const Icon = config.icon;

  return (
    <Badge variant="outline" className={config.class}>
      <Icon className="h-3 w-3 mr-1" />
      {cohort}
    </Badge>
  );
}
```

### 3.3 Create AddressCell Component

```typescript
// src/components/AddressCell.tsx

import { useState } from 'react';
import { Copy, Check, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

function truncateAddress(address: string) {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

export function AddressCell({ address, label }: { address: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex flex-col">
        {label && <span className="text-sm font-medium">{label}</span>}
        <span className="text-xs text-muted-foreground font-mono">
          {truncateAddress(address)}
        </span>
      </div>
      <Button variant="ghost" size="icon" className="h-6 w-6" onClick={handleCopy}>
        {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6"
        onClick={(e) => {
          e.stopPropagation();
          window.open(`https://hyperliquid.xyz/address/${address}`, '_blank');
        }}
      >
        <ExternalLink className="h-3 w-3" />
      </Button>
    </div>
  );
}
```

### 3.4 Create PositionModal Component

```typescript
// src/components/PositionModal.tsx

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { formatCurrency, formatPercent } from '@/lib/format';
import type { PerpPosition } from '@/types/nansen';

interface PositionModalProps {
  open: boolean;
  onClose: () => void;
  wallet: {
    address: string;
    label: string;
    positions: PerpPosition[];
  } | null;
}

export function PositionModal({ open, onClose, wallet }: PositionModalProps) {
  if (!wallet) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>{wallet.label || wallet.address}</DialogTitle>
        </DialogHeader>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Token</TableHead>
              <TableHead>Side</TableHead>
              <TableHead className="text-right">Size</TableHead>
              <TableHead className="text-right">Entry Price</TableHead>
              <TableHead className="text-right">Leverage</TableHead>
              <TableHead className="text-right">uPnL</TableHead>
              <TableHead className="text-right">Liq. Price</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {wallet.positions.map((pos, i) => {
              const size = parseFloat(pos.size);
              const isLong = size > 0;

              return (
                <TableRow key={i}>
                  <TableCell className="font-medium">{pos.token_symbol}</TableCell>
                  <TableCell>
                    <span className={isLong ? 'text-bullish' : 'text-bearish'}>
                      {isLong ? 'LONG' : 'SHORT'}
                    </span>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {Math.abs(size).toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(parseFloat(pos.entry_price_usd))}
                  </TableCell>
                  <TableCell className="text-right">
                    {pos.leverage_value}x
                  </TableCell>
                  <TableCell className={`text-right ${
                    parseFloat(pos.unrealized_pnl_usd) >= 0 ? 'text-bullish' : 'text-bearish'
                  }`}>
                    {formatCurrency(parseFloat(pos.unrealized_pnl_usd))}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(parseFloat(pos.liquidation_price_usd))}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </DialogContent>
    </Dialog>
  );
}
```

### 3.5 Create WalletTable Component

```typescript
// src/components/WalletTable.tsx

import { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ArrowUpDown } from 'lucide-react';
import { AddressCell } from './AddressCell';
import { BiasIndicator } from './BiasIndicator';
import { CohortBadge } from './CohortBadge';
import { PositionModal } from './PositionModal';
import { formatCurrency } from '@/lib/format';
import type { WalletData } from '@/types/wallet';

type SortField = 'equity' | 'positionValue' | 'leverage' | 'unrealizedPnl';
type SortDir = 'asc' | 'desc';

export function WalletTable({ wallets, isLoading }: { wallets: WalletData[]; isLoading: boolean }) {
  const [sortField, setSortField] = useState<SortField>('equity');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [selectedWallet, setSelectedWallet] = useState<WalletData | null>(null);

  const sortedWallets = useMemo(() => {
    return [...wallets].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      return sortDir === 'desc' ? bVal - aVal : aVal - bVal;
    });
  }, [wallets, sortField, sortDir]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(sortDir === 'desc' ? 'asc' : 'desc');
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const SortHeader = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <TableHead
      className="cursor-pointer hover:bg-muted/50"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-1">
        {children}
        <ArrowUpDown className="h-3 w-3" />
      </div>
    </TableHead>
  );

  if (isLoading) {
    return <TableSkeleton />;
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Address</TableHead>
            <SortHeader field="equity">Perp Equity</SortHeader>
            <TableHead>Perp Bias</TableHead>
            <SortHeader field="positionValue">Position Value</SortHeader>
            <SortHeader field="leverage">Leverage</SortHeader>
            <SortHeader field="unrealizedPnl">Sum uPnL</SortHeader>
            <TableHead>Size Cohort</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedWallets.map((wallet) => (
            <TableRow
              key={wallet.address}
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => setSelectedWallet(wallet)}
            >
              <TableCell>
                <AddressCell address={wallet.address} label={wallet.label} />
              </TableCell>
              <TableCell className="font-mono">
                {formatCurrency(wallet.equity)}
              </TableCell>
              <TableCell>
                <BiasIndicator bias={wallet.bias} />
              </TableCell>
              <TableCell className="font-mono">
                {formatCurrency(wallet.positionValue)}
              </TableCell>
              <TableCell className="font-mono">
                {wallet.leverage.toFixed(2)}x
              </TableCell>
              <TableCell className={`font-mono ${
                wallet.unrealizedPnl >= 0 ? 'text-bullish' : 'text-bearish'
              }`}>
                {formatCurrency(wallet.unrealizedPnl)}
              </TableCell>
              <TableCell>
                <CohortBadge cohort={wallet.sizeCohort} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <PositionModal
        open={!!selectedWallet}
        onClose={() => setSelectedWallet(null)}
        wallet={selectedWallet}
      />
    </>
  );
}
```

### 3.6 Create Format Utilities

```typescript
// src/lib/format.ts

export function formatCurrency(value: number): string {
  if (Math.abs(value) >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(2)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `$${(value / 1_000).toFixed(2)}K`;
  }
  return `$${value.toFixed(2)}`;
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}
```

---

## Todo List

- [ ] Create BiasIndicator component
- [ ] Create CohortBadge component
- [ ] Create AddressCell component
- [ ] Create PositionModal component
- [ ] Create WalletTable component
- [ ] Create format utilities
- [ ] Create TableSkeleton
- [ ] Wire up with hooks

---

## Success Criteria

- [ ] Table displays 210 wallets
- [ ] Sorting works on all numeric columns
- [ ] Clicking row opens modal
- [ ] Modal shows all positions
- [ ] Copy address works
- [ ] Loading skeleton displays

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Slow render with 210 rows | Medium | Virtual scrolling if needed |
| Modal performance | Low | Lazy load position data |

---

## Security Considerations

- No sensitive data exposed
- External links open in new tab

---

## Next Steps

→ [Phase 04: Market View](./phase-04-market-view.md)
