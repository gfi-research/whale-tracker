import type { PerpBias, SizeCohort, Position } from "@/types/whale";

/**
 * Calculate perp bias based on long/short position value ratio
 */
export function calculatePerpBias(positions: Position[]): PerpBias {
  if (!positions || positions.length === 0) return "Neutral";

  const longValue = positions
    .filter((p) => p.direction === "long")
    .reduce((sum, p) => sum + Math.abs(p.notional), 0);

  const shortValue = positions
    .filter((p) => p.direction === "short")
    .reduce((sum, p) => sum + Math.abs(p.notional), 0);

  const totalValue = longValue + shortValue;
  if (totalValue === 0) return "Neutral";

  const longRatio = longValue / totalValue;

  if (longRatio >= 0.8) return "Extremely Bullish";
  if (longRatio >= 0.6) return "Bullish";
  if (longRatio <= 0.2) return "Extremely Bearish";
  if (longRatio <= 0.4) return "Bearish";
  return "Neutral";
}

/**
 * Calculate size cohort based on total equity
 */
export function calculateSizeCohort(equity: number): SizeCohort {
  if (equity >= 50_000_000) return "Kraken";
  if (equity >= 10_000_000) return "Whale";
  if (equity >= 1_000_000) return "Shark";
  return "Fish";
}

/**
 * Calculate weighted average leverage across positions
 */
export function calculateWeightedLeverage(positions: Position[]): number {
  if (!positions || positions.length === 0) return 0;

  const totalNotional = positions.reduce((sum, p) => sum + Math.abs(p.notional), 0);
  if (totalNotional === 0) return 0;

  const weightedSum = positions.reduce(
    (sum, p) => sum + p.leverage * Math.abs(p.notional),
    0
  );

  return weightedSum / totalNotional;
}

/**
 * Calculate total unrealized PnL across positions
 */
export function calculateTotalUnrealizedPnl(positions: Position[]): number {
  if (!positions || positions.length === 0) return 0;
  return positions.reduce((sum, p) => sum + p.unrealizedPnl, 0);
}

/**
 * Calculate total position value (absolute notional)
 */
export function calculatePositionValue(positions: Position[]): number {
  if (!positions || positions.length === 0) return 0;
  return positions.reduce((sum, p) => sum + Math.abs(p.notional), 0);
}

/**
 * Calculate market bias label based on long percentage
 */
export function calculateMarketBias(longNotional: number, shortNotional: number): string {
  const total = longNotional + shortNotional;
  if (total === 0) return "Neutral";

  const longPct = longNotional / total;

  if (longPct >= 0.7) return "Very Bullish";
  if (longPct >= 0.55) return "Bullish";
  if (longPct >= 0.45) return "Slightly Bullish";
  if (longPct <= 0.3) return "Very Bearish";
  if (longPct <= 0.45) return "Bearish";
  return "Slightly Bearish";
}
