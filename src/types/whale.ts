export type EntityType = "retail" | "VCs" | "MM";

export type SizeCohort = "Kraken" | "Whale" | "Shark" | "Fish";

export type PerpBias =
  | "Extremely Bullish"
  | "Bullish"
  | "Neutral"
  | "Bearish"
  | "Extremely Bearish";

export interface WalletInfo {
  address: string;
  label: string;
  entity: EntityType;
  accountValue: number;
  roi: number;
  totalPnl: number;
}

export interface WalletPosition {
  address: string;
  perpEquity: number;
  perpBias: PerpBias;
  positionValue: number;
  leverage: number;
  sumUpnl: number;
  sizeCohort: SizeCohort;
}

export interface Position {
  token: string;
  direction: "long" | "short";
  entryPrice: number;
  markPrice: number;
  size: number;
  notional: number;
  leverage: number;
  liquidationPrice: number;
  marginUsed: number;
  unrealizedPnl: number;
}

export interface MarketData {
  token: string;
  longNotional: number;
  shortNotional: number;
  traderCount: number;
  unrealizedPnlProfit: number;
  unrealizedPnlLoss: number;
}

export interface NansenPerpPositionResponse {
  positions: {
    token: string;
    direction: string;
    entry_price: number;
    mark_price: number;
    size: number;
    notional: number;
    leverage: number;
    liquidation_price: number;
    margin_used: number;
    unrealized_pnl: number;
  }[];
  total_equity: number;
  total_unrealized_pnl: number;
}

export interface NansenPerpScreenerResponse {
  data: {
    token: string;
    long_notional: number;
    short_notional: number;
    trader_count: number;
    unrealized_pnl: number;
  }[];
}
