# Phase 01: Project Setup

**Parent:** [plan.md](./plan.md)
**Dependencies:** None
**Docs:** [Vite](https://vitejs.dev), [shadcn/ui](https://ui.shadcn.com)

---

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-19 |
| Description | Initialize Vite + React project with shadcn/ui |
| Priority | HIGH |
| Implementation | ⬜ Pending |
| Review | ⬜ Pending |

---

## Key Insights

- Copy Vite config from `crypto-compass`
- Reuse Tailwind config with bullish/bearish colors
- shadcn/ui already has Table, Tabs, Dialog, Badge components
- 210 wallet addresses in `demo-port/wallet_address.txt`

---

## Requirements

1. Initialize Vite + React + TypeScript project
2. Configure Tailwind with dark theme + sentiment colors
3. Install shadcn/ui base components
4. Set up project structure
5. Copy wallet addresses to project

---

## Architecture

```
whale-website/
├── src/
│   ├── components/
│   │   └── ui/           # shadcn components
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   ├── data/
│   │   └── wallets.ts    # 210 addresses
│   ├── App.tsx
│   └── main.tsx
├── .env.example
├── vite.config.ts
├── tailwind.config.ts
└── package.json
```

---

## Related Code Files

| File | Purpose |
|------|---------|
| `crypto-compass/vite.config.ts` | Reference config |
| `crypto-compass/tailwind.config.ts` | Theme colors |
| `demo-port/wallet_address.txt` | Wallet addresses |

---

## Implementation Steps

### 1.1 Initialize Vite Project
```bash
cd whale-website
npm create vite@latest . -- --template react-ts
npm install
```

### 1.2 Install Dependencies
```bash
npm install @tanstack/react-query tailwindcss postcss autoprefixer
npm install class-variance-authority clsx tailwind-merge lucide-react
npm install recharts
npx tailwindcss init -p
```

### 1.3 Configure shadcn/ui
```bash
npx shadcn@latest init
npx shadcn@latest add table tabs dialog badge scroll-area card
```

### 1.4 Configure Tailwind
Copy theme from crypto-compass, ensure:
- Dark mode enabled
- bullish/bearish colors defined
- Inter font family

### 1.5 Create Project Structure
```
mkdir -p src/{components/ui,hooks,lib,types,data}
```

### 1.6 Create Wallet Data File
Parse `demo-port/wallet_address.txt` → `src/data/wallets.ts`
```typescript
export interface WalletInfo {
  address: string;
  label: string;
  entity: string;
}
export const WHALE_WALLETS: WalletInfo[] = [...]
```

### 1.7 Environment Setup
```bash
# .env.example
VITE_NANSEN_API_KEY=your_api_key_here
```

---

## Todo List

- [ ] Initialize Vite project
- [ ] Install all dependencies
- [ ] Configure Tailwind with dark theme
- [ ] Initialize shadcn/ui
- [ ] Add required shadcn components
- [ ] Create folder structure
- [ ] Convert wallet addresses to TypeScript
- [ ] Create .env.example

---

## Success Criteria

- [ ] `npm run dev` starts without errors
- [ ] Dark theme renders correctly
- [ ] shadcn/ui components import successfully
- [ ] 210 wallet addresses available in code

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Vite version mismatch | Low | Pin versions from crypto-compass |
| Missing Tailwind colors | Low | Copy exact config |

---

## Security Considerations

- API key in .env (gitignored)
- No secrets in codebase

---

## Next Steps

→ [Phase 02: API Integration](./phase-02-api-integration.md)
