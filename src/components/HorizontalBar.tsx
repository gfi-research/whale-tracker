import { cn } from "@/lib/utils";

interface HorizontalBarProps {
  leftValue: number;
  rightValue: number;
  leftLabel?: string;
  rightLabel?: string;
  leftColor?: string;
  rightColor?: string;
  showPercentages?: boolean;
  className?: string;
}

export function HorizontalBar({
  leftValue,
  rightValue,
  leftLabel,
  rightLabel,
  leftColor = "bg-bullish",
  rightColor = "bg-bearish",
  showPercentages = true,
  className,
}: HorizontalBarProps) {
  const total = leftValue + rightValue;
  const leftPct = total > 0 ? (leftValue / total) * 100 : 50;
  const rightPct = total > 0 ? (rightValue / total) * 100 : 50;

  return (
    <div className={cn("space-y-1", className)}>
      {(leftLabel || rightLabel) && (
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>{leftLabel}</span>
          <span>{rightLabel}</span>
        </div>
      )}
      <div className="flex h-2 rounded-full overflow-hidden bg-muted">
        <div
          className={cn("transition-all duration-300", leftColor)}
          style={{ width: `${leftPct}%` }}
        />
        <div
          className={cn("transition-all duration-300", rightColor)}
          style={{ width: `${rightPct}%` }}
        />
      </div>
      {showPercentages && (
        <div className="flex justify-between text-xs font-mono">
          <span className="text-bullish">{leftPct.toFixed(1)}%</span>
          <span className="text-bearish">{rightPct.toFixed(1)}%</span>
        </div>
      )}
    </div>
  );
}
