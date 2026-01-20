/**
 * Format number as currency (USD)
 */
export function formatCurrency(value: number, compact = false): string {
  if (compact) {
    if (Math.abs(value) >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(2)}B`;
    }
    if (Math.abs(value) >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(2)}M`;
    }
    if (Math.abs(value) >= 1_000) {
      return `$${(value / 1_000).toFixed(2)}K`;
    }
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format number as percentage
 */
export function formatPercentage(value: number, decimals = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format leverage (e.g., 5.2x)
 */
export function formatLeverage(value: number): string {
  return `${value.toFixed(1)}x`;
}

/**
 * Format PnL with color indicator prefix
 */
export function formatPnl(value: number, compact = true): string {
  const prefix = value >= 0 ? "+" : "";
  return `${prefix}${formatCurrency(value, compact)}`;
}

/**
 * Truncate Ethereum address
 */
export function truncateAddress(address: string, chars = 4): string {
  if (!address) return "";
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`;
}

/**
 * Format large numbers with abbreviations
 */
export function formatNumber(value: number, decimals = 2): string {
  if (Math.abs(value) >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(decimals)}B`;
  }
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(decimals)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(decimals)}K`;
  }
  return value.toFixed(decimals);
}

/**
 * Get Hyperliquid explorer URL for address
 */
export function getHyperliquidUrl(address: string): string {
  return `https://app.hyperliquid.xyz/explorer/address/${address}`;
}
