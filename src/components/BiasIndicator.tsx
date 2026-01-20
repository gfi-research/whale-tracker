import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { PerpBias } from "@/types/whale";
import { cn } from "@/lib/utils";

interface BiasIndicatorProps {
  bias: PerpBias;
  className?: string;
}

const biasConfig: Record<PerpBias, { variant: "bullish" | "bearish" | "secondary"; icon: typeof TrendingUp }> = {
  "Extremely Bullish": { variant: "bullish", icon: TrendingUp },
  "Bullish": { variant: "bullish", icon: TrendingUp },
  "Neutral": { variant: "secondary", icon: Minus },
  "Bearish": { variant: "bearish", icon: TrendingDown },
  "Extremely Bearish": { variant: "bearish", icon: TrendingDown },
};

export function BiasIndicator({ bias, className }: BiasIndicatorProps) {
  const config = biasConfig[bias];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className={cn("gap-1", className)}>
      <Icon className="h-3 w-3" />
      <span>{bias}</span>
    </Badge>
  );
}
