import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { HorizontalBar } from "./HorizontalBar";
import { MarketBiasLabel } from "./MarketBiasLabel";
import { TableSkeleton } from "./TableSkeleton";
import { formatCurrency, formatNumber } from "@/lib/format";
import type { MarketData } from "@/types/whale";

interface MarketTableProps {
  marketData: MarketData[];
  isLoading: boolean;
}

export function MarketTable({ marketData, isLoading }: MarketTableProps) {
  if (isLoading) {
    return <TableSkeleton rows={10} columns={5} />;
  }

  return (
    <div className="rounded-md border border-border">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead className="w-[200px]">Market</TableHead>
            <TableHead className="w-[250px]">Notional (Long/Short)</TableHead>
            <TableHead className="w-[200px]">Traders</TableHead>
            <TableHead className="w-[250px]">Unrealized PnL</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {marketData.map((market) => (
            <TableRow key={market.token}>
              <TableCell>
                <div className="flex flex-col gap-1">
                  <span className="font-medium text-lg">{market.token}</span>
                  <MarketBiasLabel
                    longNotional={market.longNotional}
                    shortNotional={market.shortNotional}
                  />
                </div>
              </TableCell>
              <TableCell>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{formatCurrency(market.longNotional, true)}</span>
                    <span>{formatCurrency(market.shortNotional, true)}</span>
                  </div>
                  <HorizontalBar
                    leftValue={market.longNotional}
                    rightValue={market.shortNotional}
                    showPercentages={false}
                  />
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm">
                    {formatNumber(market.traderCount, 0)} traders
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-bullish">
                      +{formatCurrency(market.unrealizedPnlProfit, true)}
                    </span>
                    <span className="text-bearish">
                      -{formatCurrency(market.unrealizedPnlLoss, true)}
                    </span>
                  </div>
                  <HorizontalBar
                    leftValue={market.unrealizedPnlProfit}
                    rightValue={market.unrealizedPnlLoss}
                    showPercentages={false}
                  />
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
