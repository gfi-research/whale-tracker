# Whale Tracker Dashboard - Codebase Summary

## Directory Structure

```
whale-website/
├── docs/                          # Project documentation
│   ├── project-overview-pdr.md    # Product requirements
│   ├── codebase-summary.md        # This file
│   ├── code-standards.md          # Coding conventions
│   └── system-architecture.md     # Architecture docs
├── plans/                         # Implementation planning
│   └── 20260119-1430-whale-tracker/
│       ├── plan.md                # Master implementation plan
│       ├── phase-01-project-setup.md
│       ├── phase-02-api-integration.md
│       ├── phase-03-wallet-table.md
│       ├── phase-04-market-view.md
│       ├── phase-05-polish-deploy.md
│       └── reports/               # Analysis reports
├── public/                        # Static assets
│   └── vite.svg                   # Vite logo
├── src/                           # Source code
│   ├── assets/                    # Asset files
│   │   └── react.svg              # React logo
│   ├── components/                # React components
│   │   └── ui/                    # shadcn/ui components
│   ├── data/                      # Static data files
│   │   └── wallets.ts             # Whale wallet data
│   ├── hooks/                     # Custom React hooks (reserved)
│   ├── lib/                       # Utility functions
│   │   └── utils.ts               # CN utility for class merging
│   ├── types/                     # TypeScript type definitions
│   │   └── whale.ts               # Domain types
│   ├── App.css                    # App-specific styles
│   ├── App.tsx                    # Main application component
│   ├── index.css                  # Global styles and CSS variables
│   └── main.tsx                   # Application entry point
├── dist/                          # Build output (generated)
├── node_modules/                  # Dependencies (generated)
├── .claude/                       # Claude Code configuration
├── eslint.config.js               # ESLint configuration
├── index.html                     # HTML entry point
├── package.json                   # Project dependencies and scripts
├── postcss.config.js              # PostCSS configuration
├── tailwind.config.ts             # Tailwind CSS configuration
├── tsconfig.json                  # TypeScript project references
├── tsconfig.app.json              # Application TypeScript config
├── tsconfig.node.json             # Node TypeScript config
└── vite.config.ts                 # Vite build configuration
```

---

## File Inventory

### Configuration Files

| File | Purpose | Key Settings |
|------|---------|--------------|
| `package.json` | Project manifest | Dependencies, scripts, metadata |
| `vite.config.ts` | Vite bundler config | React plugin, path aliases, dev server |
| `tailwind.config.ts` | Tailwind CSS config | Custom colors, fonts, animations |
| `tsconfig.json` | TypeScript references | Project reference structure |
| `tsconfig.app.json` | App TypeScript config | Strict mode, path aliases, JSX |
| `tsconfig.node.json` | Node TypeScript config | Node-specific settings |
| `eslint.config.js` | Linting rules | TypeScript + React rules |
| `postcss.config.js` | PostCSS plugins | Tailwind, Autoprefixer |
| `index.html` | HTML template | Root element, script entry |

### Source Files

| File | Purpose | Exports |
|------|---------|---------|
| `src/main.tsx` | Application bootstrap | Renders App to DOM |
| `src/App.tsx` | Root component | Main application shell |
| `src/App.css` | App component styles | Component-specific CSS |
| `src/index.css` | Global styles | CSS variables, base styles |
| `src/lib/utils.ts` | Utility functions | `cn()` class merger |
| `src/types/whale.ts` | Domain types | Type definitions for domain |
| `src/data/wallets.ts` | Wallet data | `WHALE_WALLETS`, `WALLET_COUNT` |

### UI Components (shadcn/ui)

| Component | File | Purpose |
|-----------|------|---------|
| Alert | `components/ui/alert.tsx` | Alert messages and notifications |
| Badge | `components/ui/badge.tsx` | Status labels and tags |
| Button | `components/ui/button.tsx` | Interactive buttons with variants |
| Card | `components/ui/card.tsx` | Container cards with header/content |
| Dialog | `components/ui/dialog.tsx` | Modal dialogs and overlays |
| ScrollArea | `components/ui/scroll-area.tsx` | Custom scrollable containers |
| Skeleton | `components/ui/skeleton.tsx` | Loading placeholder animations |
| Table | `components/ui/table.tsx` | Data table structure |
| Tabs | `components/ui/tabs.tsx` | Tab navigation interface |

---

## Key Dependencies

### Production Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | 19.2.0 | UI library |
| `react-dom` | 19.2.0 | React DOM renderer |
| `@tanstack/react-query` | 5.90.19 | Server state management |
| `recharts` | 3.6.0 | Charting library |
| `lucide-react` | 0.562.0 | Icon library |
| `clsx` | 2.1.1 | Conditional class joining |
| `tailwind-merge` | 3.4.0 | Tailwind class deduplication |
| `class-variance-authority` | 0.7.1 | Component variant management |

### Radix UI Primitives

| Package | Version | Used By |
|---------|---------|---------|
| `@radix-ui/react-alert-dialog` | 1.1.15 | Alert component |
| `@radix-ui/react-dialog` | 1.1.15 | Dialog component |
| `@radix-ui/react-label` | 2.1.8 | Form labels |
| `@radix-ui/react-scroll-area` | 1.2.10 | ScrollArea component |
| `@radix-ui/react-slot` | 1.2.4 | Button composition |
| `@radix-ui/react-tabs` | 1.1.13 | Tabs component |
| `@radix-ui/react-tooltip` | 1.2.8 | Tooltips |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `vite` | 7.2.4 | Build tool and dev server |
| `typescript` | 5.9.3 | Type checking |
| `tailwindcss` | 3.4.17 | Utility CSS framework |
| `eslint` | 9.39.1 | Code linting |
| `@vitejs/plugin-react` | 5.1.1 | React Vite integration |
| `autoprefixer` | 10.4.23 | CSS vendor prefixes |
| `tailwindcss-animate` | 1.0.7 | Animation utilities |

---

## Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                              │
├─────────────────────────────────────────────────────────────────┤
│  Static Data                │  API Data (Future)                 │
│  └── wallets.ts             │  └── Nansen API                    │
│      (210 wallets)          │      - /profiler/perp-positions    │
│                             │      - /profiler/address/pnl-summary│
│                             │      - /tgm/perp-screener          │
└──────────────┬──────────────┴──────────────┬────────────────────┘
               │                             │
               ▼                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     State Management                             │
├─────────────────────────────────────────────────────────────────┤
│  TanStack React Query                                            │
│  ├── 5-minute stale time                                         │
│  ├── Automatic background refetching                             │
│  └── Optimistic updates                                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      React Components                            │
├─────────────────────────────────────────────────────────────────┤
│  App.tsx                                                         │
│  ├── WalletTable (planned)                                       │
│  ├── MarketView (planned)                                        │
│  └── PositionModal (planned)                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Inventory

### Current Components (UI Primitives)

| Component | Status | Variants |
|-----------|--------|----------|
| Button | Ready | default, destructive, outline, secondary, ghost, link |
| Card | Ready | Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter |
| Badge | Ready | default, secondary, destructive, outline |
| Table | Ready | Table, TableHeader, TableBody, TableRow, TableHead, TableCell |
| Tabs | Ready | Tabs, TabsList, TabsTrigger, TabsContent |
| Dialog | Ready | Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle |
| Alert | Ready | Alert, AlertTitle, AlertDescription |
| Skeleton | Ready | Skeleton |
| ScrollArea | Ready | ScrollArea, ScrollBar |

### Planned Components (Application)

| Component | Priority | Purpose |
|-----------|----------|---------|
| WalletTable | P0 | Main wallet listing with sorting/filtering |
| WalletRow | P0 | Individual wallet row in table |
| MarketOverview | P0 | Aggregate market position view |
| TokenCard | P1 | Token-specific position summary |
| PositionModal | P1 | Detailed wallet position view |
| SentimentBadge | P1 | Bullish/bearish/neutral indicator |
| CohortFilter | P1 | Size tier filter controls |
| EntityFilter | P1 | Entity type filter controls |
| SearchInput | P2 | Wallet search functionality |

---

## Current Implementation Status

| Area | Status | Notes |
|------|--------|-------|
| Project Setup | Complete | Vite, TypeScript, ESLint configured |
| Tailwind CSS | Complete | Custom theme with sentiment colors |
| shadcn/ui | Complete | 9 components installed |
| Type Definitions | Complete | All domain types defined |
| Wallet Data | Complete | 210 wallets with metadata |
| Path Aliases | Complete | `@/*` maps to `./src/*` |
| Dark Mode | Ready | CSS variables configured |
| API Integration | Not Started | Hooks and services pending |
| Wallet Table | Not Started | Component implementation pending |
| Market View | Not Started | Component implementation pending |
| Position Modal | Not Started | Component implementation pending |

---

## NPM Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `vite` | Start development server (port 5173) |
| `build` | `tsc -b && vite build` | Type check and build for production |
| `lint` | `eslint .` | Run ESLint on all files |
| `preview` | `vite preview` | Preview production build locally |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-19 | Technical Writer | Initial documentation |
