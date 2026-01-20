# Whale Tracker Dashboard - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT (Browser)                         │
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐    │
│  │ Wallet Table  │  │ Market View   │  │Position Modal │    │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘    │
│          └──────────────────┼──────────────────┘            │
│                             │                               │
│                   ┌─────────▼─────────┐                     │
│                   │   React Query     │                     │
│                   │   (5min cache)    │                     │
│                   └─────────┬─────────┘                     │
│                             │                               │
│                   ┌─────────▼─────────┐                     │
│                   │   API Service     │                     │
│                   └─────────┬─────────┘                     │
└─────────────────────────────┼───────────────────────────────┘
                              │ HTTPS
┌─────────────────────────────▼───────────────────────────────┐
│                       Nansen API                            │
│  /profiler/perp-positions  |  /tgm/perp-screener           │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Action → React Component → useQuery() → Cache Check
                                               │
                     ┌─────────────────────────┴─────────────┐
                     │ Cache Hit                 Cache Miss  │
                     ▼                                       ▼
              Return Cached Data              API Service → Nansen API
                                                               │
                                              Transform (snake→camel)
                                                               │
                                              Update Cache → Re-render
```

### Data Transformation

```typescript
// API Response (snake_case)           // Domain Model (camelCase)
{ entry_price: number }          →     { entryPrice: number }
{ unrealized_pnl: number }       →     { unrealizedPnl: number }
```

## State Management

### React Query Config

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,    // 5 minutes
      gcTime: 10 * 60 * 1000,      // 10 minutes
      refetchOnWindowFocus: true,
      retry: 3,
    },
  },
});
```

### Query Keys

```typescript
const queryKeys = {
  wallets: ["wallets"],
  wallet: (address: string) => ["wallets", address],
  walletPositions: (address: string) => ["wallets", address, "positions"],
  markets: ["markets"],
};
```

### State Categories

| Category | Management | Source |
|----------|------------|--------|
| Server State | React Query | Nansen API |
| UI State | useState | User interactions |
| Static Data | Import | wallets.ts |

## API Integration

### Endpoints

| Feature | Endpoint | Attribution |
|---------|----------|-------------|
| Wallet Positions | `/profiler/perp-positions` | None |
| Wallet PnL | `/profiler/address/pnl-summary` | None |
| Market Screener | `/tgm/perp-screener` | Required |

### Client Config

```typescript
const apiClient = {
  baseURL: import.meta.env.VITE_NANSEN_API_URL,
  headers: {
    Authorization: `Bearer ${import.meta.env.VITE_NANSEN_API_KEY}`,
  },
  timeout: 10000,
};
```

## Component Hierarchy

```
App
├── Header (Logo, Tabs)
├── MainContent
│   ├── WalletTableTab
│   │   ├── FilterBar
│   │   ├── WalletTable (sortable, 210 rows)
│   │   └── Pagination
│   └── MarketViewTab
│       ├── SentimentSummary
│       └── TokenGrid
├── PositionModal (Dialog)
└── Footer (Nansen Attribution)
```

## Build Pipeline

```bash
npm run dev      # Development server (localhost:5173)
npm run build    # tsc -b && vite build → dist/
npm run preview  # Preview production build
```

### Deployment

| Platform | Config |
|----------|--------|
| Vercel | Zero-config |
| Netlify | `_redirects` for SPA |
| Static Host | Serve `dist/` |

## Security

### Environment Variables

```bash
# .env.local (DO NOT COMMIT)
VITE_NANSEN_API_KEY=xxx

# .env.example (SAFE TO COMMIT)
VITE_NANSEN_API_KEY=your_api_key_here
```

### Best Practices

| Concern | Mitigation |
|---------|------------|
| API Key Exposure | Backend proxy in production |
| XSS | React auto-escaping |
| Rate Limiting | 5min cache, request throttling |

### Production Recommendation

```
Browser → Backend Proxy → Nansen API
              │
        API key stored server-side
```

## Performance

| Strategy | Implementation |
|----------|---------------|
| Caching | React Query 5min stale time |
| Code Splitting | Vendor, query, charts chunks |
| Virtual Scrolling | For wallet table (210 rows) |
| Lazy Loading | Modal content |
