import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useWalletDetailPositions } from "@/hooks/useWalletPositions";
import { WHALE_WALLETS } from "@/data/wallets";
import { formatCurrency, formatLeverage, formatPnl, truncateAddress } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { Position } from "@/types/whale";

interface PositionModalProps {
  address: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function PositionModal({ address, open, onOpenChange }: PositionModalProps) {
  const { data: positions, isLoading } = useWalletDetailPositions(address);
  const wallet = address ? WHALE_WALLETS.find((w) => w.address === address) : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {wallet?.label || "Wallet Positions"}
          </DialogTitle>
          <DialogDescription className="font-mono">
            {address ? truncateAddress(address, 8) : ""}
          </DialogDescription>
        </DialogHeader>

        <div className="overflow-auto flex-1">
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !positions || positions.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No open positions
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Token</TableHead>
                  <TableHead>Side</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Entry Price</TableHead>
                  <TableHead>Mark Price</TableHead>
                  <TableHead>Leverage</TableHead>
                  <TableHead>Liq. Price</TableHead>
                  <TableHead>uPnL</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {positions.map((pos: Position, index: number) => (
                  <TableRow key={`${pos.token}-${index}`}>
                    <TableCell className="font-medium">{pos.token}</TableCell>
                    <TableCell>
                      <Badge
                        variant={pos.direction === "long" ? "bullish" : "bearish"}
                      >
                        {pos.direction.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono">
                      {pos.size.toFixed(4)}
                    </TableCell>
                    <TableCell className="font-mono">
                      {formatCurrency(pos.entryPrice)}
                    </TableCell>
                    <TableCell className="font-mono">
                      {formatCurrency(pos.markPrice)}
                    </TableCell>
                    <TableCell className="font-mono">
                      {formatLeverage(pos.leverage)}
                    </TableCell>
                    <TableCell className="font-mono text-yellow-500">
                      {formatCurrency(pos.liquidationPrice)}
                    </TableCell>
                    <TableCell
                      className={cn(
                        "font-mono",
                        pos.unrealizedPnl >= 0 ? "text-bullish" : "text-bearish"
                      )}
                    >
                      {formatPnl(pos.unrealizedPnl, false)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>

        {positions && positions.length > 0 && (
          <div className="pt-4 border-t border-border flex justify-between text-sm">
            <span className="text-muted-foreground">
              {positions.length} position{positions.length !== 1 ? "s" : ""}
            </span>
            <span
              className={cn(
                "font-mono font-medium",
                positions.reduce((sum: number, p: Position) => sum + p.unrealizedPnl, 0) >= 0
                  ? "text-bullish"
                  : "text-bearish"
              )}
            >
              Total uPnL:{" "}
              {formatPnl(
                positions.reduce((sum: number, p: Position) => sum + p.unrealizedPnl, 0),
                false
              )}
            </span>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
