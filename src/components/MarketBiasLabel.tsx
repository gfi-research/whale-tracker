import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { calculateMarketBias } from "@/lib/calculations";
import { cn } from "@/lib/utils";

interface MarketBiasLabelProps {
  longNotional: number;
  shortNotional: number;
  className?: string;
}

export function MarketBiasLabel({ longNotional, shortNotional, className }: MarketBiasLabelProps) {
  const bias = calculateMarketBias(longNotional, shortNotional);

  const isBullish = bias.includes("Bullish");
  const isBearish = bias.includes("Bearish");

  const Icon = isBullish ? TrendingUp : isBearish ? TrendingDown : Minus;
  const variant = isBullish ? "bullish" : isBearish ? "bearish" : "secondary";

  return (
    <Badge variant={variant} className={cn("gap-1", className)}>
      <Icon className="h-3 w-3" />
      <span>{bias}</span>
    </Badge>
  );
}
