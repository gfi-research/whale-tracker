import type { Position, MarketData, NansenPerpPositionResponse, NansenPerpScreenerResponse } from "@/types/whale";
import { generateMockPositions, generateMockMarketData } from "./mock-data";

const NANSEN_API_URL = "https://api.nansen.ai";

/**
 * Nansen API client for fetching whale positions
 */
class NansenClient {
  private apiKey: string | null;

  constructor() {
    this.apiKey = process.env.NEXT_PUBLIC_NANSEN_API_KEY || null;
  }

  private get headers() {
    return {
      "Content-Type": "application/json",
      ...(this.apiKey && { Authorization: `Bearer ${this.apiKey}` }),
    };
  }

  /**
   * Check if API key is configured
   */
  get isConfigured(): boolean {
    return Boolean(this.apiKey);
  }

  /**
   * Transform Nansen API response to internal Position type
   */
  private transformPositions(response: NansenPerpPositionResponse): Position[] {
    return response.positions.map((p) => ({
      token: p.token,
      direction: p.direction as "long" | "short",
      entryPrice: p.entry_price,
      markPrice: p.mark_price,
      size: p.size,
      notional: p.notional,
      leverage: p.leverage,
      liquidationPrice: p.liquidation_price,
      marginUsed: p.margin_used,
      unrealizedPnl: p.unrealized_pnl,
    }));
  }

  /**
   * Transform Nansen screener response to internal MarketData type
   */
  private transformMarketData(response: NansenPerpScreenerResponse): MarketData[] {
    return response.data.map((d) => ({
      token: d.token,
      longNotional: d.long_notional,
      shortNotional: d.short_notional,
      traderCount: d.trader_count,
      unrealizedPnlProfit: d.unrealized_pnl > 0 ? d.unrealized_pnl : 0,
      unrealizedPnlLoss: d.unrealized_pnl < 0 ? Math.abs(d.unrealized_pnl) : 0,
    }));
  }

  /**
   * Fetch positions for a single wallet
   */
  async fetchWalletPositions(address: string): Promise<Position[]> {
    // Use mock data if no API key
    if (!this.isConfigured) {
      // Simulate network delay
      await new Promise((resolve) => setTimeout(resolve, 100));
      return generateMockPositions(address);
    }

    try {
      const response = await fetch(`${NANSEN_API_URL}/profiler/perp-positions`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ address }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: NansenPerpPositionResponse = await response.json();
      return this.transformPositions(data);
    } catch (error) {
      console.error(`Failed to fetch positions for ${address}:`, error);
      // Fallback to mock data on error
      return generateMockPositions(address);
    }
  }

  /**
   * Fetch market screener data
   */
  async fetchMarketData(): Promise<MarketData[]> {
    // Use mock data if no API key
    if (!this.isConfigured) {
      await new Promise((resolve) => setTimeout(resolve, 200));
      return generateMockMarketData();
    }

    try {
      const response = await fetch(`${NANSEN_API_URL}/tgm/perp-screener`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ only_smart_money: true }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: NansenPerpScreenerResponse = await response.json();
      return this.transformMarketData(data);
    } catch (error) {
      console.error("Failed to fetch market data:", error);
      // Fallback to mock data on error
      return generateMockMarketData();
    }
  }
}

// Singleton instance
export const nansenClient = new NansenClient();
