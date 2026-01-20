# Whale Tracker Dashboard - Code Standards

## TypeScript Conventions

### Strict Mode

```json
{
  "strict": true,
  "noUnusedLocals": true,
  "noUnusedParameters": true,
  "noFallthroughCasesInSwitch": true
}
```

### Type Guidelines

```typescript
// Use `type` for unions
export type EntityType = "retail" | "VCs" | "MM";
export type SizeCohort = "Kraken" | "Whale" | "Shark" | "Fish";

// Use `interface` for objects
export interface WalletInfo {
  address: string;
  label: string;
  entity: EntityType;
}

// Use type-only imports
import type { WalletInfo } from "@/types/whale";
```

### Naming Conventions

| Category | Convention | Example |
|----------|------------|---------|
| Types/Interfaces | PascalCase | `WalletPosition` |
| Constants | SCREAMING_SNAKE_CASE | `WHALE_WALLETS` |
| Functions/Variables | camelCase | `formatCurrency` |
| Props | PascalCase + Props | `ButtonProps` |
| Files | kebab-case | `wallet-table.tsx` |

## React Patterns

### forwardRef Components

```typescript
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant }), className)} {...props} />
  )
);
Button.displayName = "Button";
```

### Component File Structure

1. Imports (external, then internal)
2. Type definitions
3. Variant definitions (CVA)
4. Component implementation
5. Display name
6. Exports

### CVA Variants

```typescript
const buttonVariants = cva("inline-flex items-center justify-center", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground",
      destructive: "bg-destructive text-destructive-foreground",
    },
    size: { default: "h-10 px-4", sm: "h-9 px-3" },
  },
  defaultVariants: { variant: "default", size: "default" },
});
```

## Styling Conventions

### Tailwind Class Order

1. Layout (display, position)
2. Sizing (width, height, padding)
3. Typography (font, text)
4. Visual (background, border)
5. Interactive (hover, focus)

### CSS Variables

```css
:root {
  --primary: 198 93% 59%;
  --bullish: 142 76% 45%;
  --bearish: 0 84% 60%;
}
```

### cn() Utility

```typescript
import { cn } from "@/lib/utils";

<div className={cn("base-classes", variant === "primary" && "primary-classes", className)} />
```

## Import Organization

```typescript
// 1. React
import * as React from "react";

// 2. External libraries
import { cva } from "class-variance-authority";

// 3. Internal aliases
import { cn } from "@/lib/utils";
import type { WalletInfo } from "@/types/whale";

// 4. Relative imports
import { formatCurrency } from "../utils/formatters";
```

**Path Alias:** Use `@/` for src imports, avoid deep relative paths.

## Error Handling

```typescript
// React Query error handling
const { data, error } = useQuery({
  queryKey: ["wallet", address],
  queryFn: () => fetchWalletPositions(address),
  retry: 3,
});

if (error) return <Alert variant="destructive">{error.message}</Alert>;

// Type guards
function isValidWallet(data: unknown): data is WalletInfo {
  return typeof data === "object" && data !== null && "address" in data;
}
```

## Code Quality

### ESLint

- No unused variables/imports
- React Hooks rules
- TypeScript recommended rules

### Pre-commit

```bash
npm run lint && npm run build
```
