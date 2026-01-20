# Whale Tracker Dashboard

A real-time dashboard for tracking smart money positions on the Hyperliquid perpetual exchange, powered by Nansen API data.

## Overview

Whale Tracker Dashboard provides visibility into the trading activity of 210 curated whale wallets, including retail traders, VCs, and market makers. The dashboard displays wallet positions, market aggregations, and detailed position analytics.

### Key Features

- **Wallet Table:** Track 210 whale wallets with sortable columns (equity, bias, leverage, PnL)
- **Market View:** Token-level aggregations showing smart money sentiment
- **Position Modal:** Detailed view of individual wallet positions
- **Real-time Data:** 5-minute cache with TanStack Query
- **Dark Mode:** Sentiment-aware color system (bullish/bearish indicators)

## Tech Stack

| Category | Technology |
|----------|------------|
| Frontend | React 19.2.0 + TypeScript 5.9.3 |
| Build | Vite 7.2.4 |
| Styling | Tailwind CSS 3.4.17 + shadcn/ui |
| State | TanStack React Query 5.90.19 |
| Charts | Recharts 3.6.0 |
| Icons | lucide-react 0.562.0 |

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
# Add your Nansen API key to .env

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
whale-website/
├── src/
│   ├── components/ui/    # shadcn/ui components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities (cn, API clients)
│   ├── types/            # TypeScript type definitions
│   ├── data/             # Static data (wallet addresses)
│   └── App.tsx           # Root component
├── docs/                 # Project documentation
├── plans/                # Planning documents
└── dist/                 # Build output
```

## Documentation

| Document | Description |
|----------|-------------|
| [Project Overview & PDR](docs/project-overview-pdr.md) | Goals, requirements, success criteria |
| [Codebase Summary](docs/codebase-summary.md) | File inventory, dependencies, data flow |
| [Code Standards](docs/code-standards.md) | TypeScript, React, styling conventions |
| [System Architecture](docs/system-architecture.md) | Architecture diagrams, API integration |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_NANSEN_API_KEY` | Nansen API key for data fetching |

## Domain Model

### Entity Types
- **Retail:** Individual traders
- **VCs:** Venture capital firms
- **MM:** Market makers

### Size Cohorts
- **Kraken:** $50M+ equity
- **Whale:** $10M+ equity
- **Shark:** $1M+ equity
- **Fish:** <$1M equity

### Perp Bias
- Extremely Bullish / Bullish / Neutral / Bearish / Extremely Bearish

## API Attribution

Data provided by [Nansen](https://nansen.ai). See [API constraints](docs/project-overview-pdr.md#api-constraints) for compliance requirements.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server (port 5173) |
| `npm run build` | Type-check and build for production |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview production build |

## License

Private - All rights reserved.
