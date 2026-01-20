import type { Position, MarketData } from "@/types/whale";
import { WHALE_WALLETS } from "@/data/wallets";

// Common tokens traded on Hyperliquid
const TOKENS = ["BTC", "ETH", "SOL", "ARB", "DOGE", "AVAX", "LINK", "OP", "APT", "SUI"];

// Generate deterministic random based on address
function seededRandom(seed: string): () => number {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    const char = seed.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return () => {
    hash = Math.sin(hash) * 10000;
    return hash - Math.floor(hash);
  };
}

/**
 * Generate mock positions for a wallet
 */
export function generateMockPositions(address: string): Position[] {
  const random = seededRandom(address);
  const wallet = WHALE_WALLETS.find((w) => w.address === address);
  const accountValue = wallet?.accountValue ?? 1_000_000;

  // Number of positions (1-5)
  const numPositions = Math.floor(random() * 5) + 1;
  const positions: Position[] = [];

  for (let i = 0; i < numPositions; i++) {
    const token = TOKENS[Math.floor(random() * TOKENS.length)];
    const direction = random() > 0.45 ? "long" : "short";
    const leverage = Math.floor(random() * 20) + 1;
    const notionalPct = (random() * 0.4 + 0.1) / numPositions; // 10-50% of account per position
    const notional = accountValue * notionalPct;
    const size = notional / (token === "BTC" ? 95000 : token === "ETH" ? 3200 : 100);

    // Prices based on token
    const basePrice =
      token === "BTC" ? 95000 :
      token === "ETH" ? 3200 :
      token === "SOL" ? 180 :
      token === "ARB" ? 0.85 :
      token === "DOGE" ? 0.32 :
      token === "AVAX" ? 35 :
      token === "LINK" ? 22 :
      token === "OP" ? 1.8 :
      token === "APT" ? 8.5 : 3.2;

    const priceVariance = (random() - 0.5) * 0.1;
    const entryPrice = basePrice * (1 + priceVariance);
    const markPrice = basePrice * (1 + (random() - 0.5) * 0.05);

    // Calculate PnL
    const priceDiff = direction === "long"
      ? markPrice - entryPrice
      : entryPrice - markPrice;
    const unrealizedPnl = (priceDiff / entryPrice) * notional;

    // Liquidation price
    const liquidationDistance = 1 / leverage;
    const liquidationPrice = direction === "long"
      ? entryPrice * (1 - liquidationDistance)
      : entryPrice * (1 + liquidationDistance);

    positions.push({
      token,
      direction,
      entryPrice,
      markPrice,
      size: Math.abs(size),
      notional: Math.abs(notional),
      leverage,
      liquidationPrice,
      marginUsed: notional / leverage,
      unrealizedPnl,
    });
  }

  return positions;
}

/**
 * Generate mock market data
 */
export function generateMockMarketData(): MarketData[] {
  const marketData: MarketData[] = [];

  for (const token of TOKENS) {
    // Aggregate across all wallets
    let longNotional = 0;
    let shortNotional = 0;
    let longTraders = 0;
    let shortTraders = 0;
    let unrealizedPnlProfit = 0;
    let unrealizedPnlLoss = 0;

    for (const wallet of WHALE_WALLETS) {
      const positions = generateMockPositions(wallet.address);
      const tokenPositions = positions.filter((p) => p.token === token);

      for (const pos of tokenPositions) {
        if (pos.direction === "long") {
          longNotional += pos.notional;
          longTraders++;
        } else {
          shortNotional += pos.notional;
          shortTraders++;
        }

        if (pos.unrealizedPnl > 0) {
          unrealizedPnlProfit += pos.unrealizedPnl;
        } else {
          unrealizedPnlLoss += Math.abs(pos.unrealizedPnl);
        }
      }
    }

    if (longNotional > 0 || shortNotional > 0) {
      marketData.push({
        token,
        longNotional,
        shortNotional,
        traderCount: longTraders + shortTraders,
        unrealizedPnlProfit,
        unrealizedPnlLoss,
      });
    }
  }

  // Sort by total notional
  return marketData.sort(
    (a, b) => b.longNotional + b.shortNotional - (a.longNotional + a.shortNotional)
  );
}
