# Phase 05: Polish & Deploy

**Parent:** [plan.md](./plan.md)
**Dependencies:** Phase 01-04
**Docs:** [Vite Deploy](https://vitejs.dev/guide/static-deploy.html)

---

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-19 |
| Description | Final polish, error handling, and deployment |
| Priority | MEDIUM |
| Implementation | ⬜ Pending |
| Review | ⬜ Pending |

---

## Key Insights

- Need proper error boundaries
- Loading states for all data
- Responsive design for mobile
- Dark theme CSS variables
- Deploy to Vercel/Netlify

---

## Requirements

1. Error boundary component
2. Global error handling
3. Responsive table design
4. Loading skeletons
5. CSS theme polish
6. Build optimization
7. Deploy configuration

---

## Architecture

```
src/
├── components/
│   ├── ErrorBoundary.tsx
│   ├── TableSkeleton.tsx
│   └── RefreshButton.tsx
├── styles/
│   └── index.css           # Theme variables
└── App.tsx
```

---

## Implementation Steps

### 5.1 Create Error Boundary

```typescript
// src/components/ErrorBoundary.tsx

import { Component, ErrorInfo, ReactNode } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert variant="destructive" className="m-4">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription className="mt-2">
            {this.state.error?.message || 'An unexpected error occurred'}
          </AlertDescription>
          <Button
            variant="outline"
            size="sm"
            className="mt-4"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reload Page
          </Button>
        </Alert>
      );
    }

    return this.props.children;
  }
}
```

### 5.2 Create Loading Skeletons

```typescript
// src/components/TableSkeleton.tsx

import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export function WalletTableSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Address</TableHead>
          <TableHead>Perp Equity</TableHead>
          <TableHead>Perp Bias</TableHead>
          <TableHead>Position Value</TableHead>
          <TableHead>Leverage</TableHead>
          <TableHead>Sum uPnL</TableHead>
          <TableHead>Size Cohort</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {Array.from({ length: 10 }).map((_, i) => (
          <TableRow key={i}>
            <TableCell><Skeleton className="h-8 w-32" /></TableCell>
            <TableCell><Skeleton className="h-4 w-20" /></TableCell>
            <TableCell><Skeleton className="h-6 w-28" /></TableCell>
            <TableCell><Skeleton className="h-4 w-24" /></TableCell>
            <TableCell><Skeleton className="h-4 w-12" /></TableCell>
            <TableCell><Skeleton className="h-4 w-20" /></TableCell>
            <TableCell><Skeleton className="h-6 w-20" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function MarketTableSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Market</TableHead>
          <TableHead>Notional</TableHead>
          <TableHead>Traders</TableHead>
          <TableHead>Unrealized PnL</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {Array.from({ length: 8 }).map((_, i) => (
          <TableRow key={i}>
            <TableCell><Skeleton className="h-10 w-24" /></TableCell>
            <TableCell><Skeleton className="h-8 w-48" /></TableCell>
            <TableCell><Skeleton className="h-8 w-40" /></TableCell>
            <TableCell><Skeleton className="h-8 w-40" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

### 5.3 Update CSS Theme

```css
/* src/index.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 4%;
    --foreground: 0 0% 95%;
    --card: 0 0% 6%;
    --card-foreground: 0 0% 95%;
    --popover: 0 0% 6%;
    --popover-foreground: 0 0% 95%;
    --primary: 142 71% 45%;
    --primary-foreground: 0 0% 100%;
    --secondary: 0 0% 14%;
    --secondary-foreground: 0 0% 95%;
    --muted: 0 0% 14%;
    --muted-foreground: 0 0% 64%;
    --accent: 0 0% 14%;
    --accent-foreground: 0 0% 95%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;
    --border: 0 0% 18%;
    --input: 0 0% 18%;
    --ring: 142 71% 45%;
    --radius: 0.5rem;

    /* Sentiment colors */
    --bullish: 142 71% 45%;
    --bullish-foreground: 0 0% 100%;
    --bearish: 0 84% 60%;
    --bearish-foreground: 0 0% 100%;
    --neutral: 0 0% 50%;
    --neutral-foreground: 0 0% 100%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: hsl(var(--muted));
}

::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 0.5);
}

/* Table row hover */
.hover-row:hover {
  background: hsl(var(--muted) / 0.5);
}
```

### 5.4 Add Refresh Button

```typescript
// src/components/RefreshButton.tsx

import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

export function RefreshButton() {
  const queryClient = useQueryClient();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await queryClient.invalidateQueries();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleRefresh}
      disabled={isRefreshing}
    >
      <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
      Refresh
    </Button>
  );
}
```

### 5.5 Configure Build

```typescript
// vite.config.ts

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: false,
  },
});
```

### 5.6 Create Deploy Config (Vercel)

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

### 5.7 Create Environment Template

```bash
# .env.example
VITE_NANSEN_API_KEY=your_nansen_api_key_here
```

---

## Todo List

- [ ] Create ErrorBoundary component
- [ ] Create loading skeletons
- [ ] Update CSS theme variables
- [ ] Add refresh button
- [ ] Configure Vite build
- [ ] Create vercel.json
- [ ] Test responsive design
- [ ] Test error states
- [ ] Run production build
- [ ] Deploy to Vercel

---

## Success Criteria

- [ ] Error boundary catches errors gracefully
- [ ] Loading skeletons display during fetch
- [ ] Dark theme matches screenshots
- [ ] Responsive on mobile/tablet
- [ ] Production build succeeds
- [ ] Deployed and accessible

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| CORS in production | Medium | Add proxy if needed |
| API key exposure | High | Use server-side proxy |
| Build failures | Low | Test locally first |

---

## Security Considerations

- API key should use backend proxy in production
- No sensitive data in client bundle
- CSP headers recommended

---

## Next Steps

→ Production deployment complete!
