"use client";

import { useState, useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { BiasIndicator } from "./BiasIndicator";
import { CohortBadge } from "./CohortBadge";
import { AddressCell } from "./AddressCell";
import { TableSkeleton } from "./TableSkeleton";
import { formatCurrency, formatLeverage, formatPnl } from "@/lib/format";
import { WHALE_WALLETS } from "@/data/wallets";
import type { WalletPosition } from "@/types/whale";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";
import { cn } from "@/lib/utils";

type SortField = "perpEquity" | "positionValue" | "leverage" | "sumUpnl";
type SortDirection = "asc" | "desc";

interface WalletTableProps {
  walletPositions: WalletPosition[];
  isLoading: boolean;
  onRowClick: (address: string) => void;
}

export function WalletTable({ walletPositions, isLoading, onRowClick }: WalletTableProps) {
  const [sortField, setSortField] = useState<SortField>("perpEquity");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const sortedPositions = useMemo(() => {
    return [...walletPositions].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      const multiplier = sortDirection === "asc" ? 1 : -1;
      return (aVal - bVal) * multiplier;
    });
  }, [walletPositions, sortField, sortDirection]);

  const getWalletLabel = (address: string) => {
    return WHALE_WALLETS.find((w) => w.address === address)?.label || "";
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="h-4 w-4 ml-1" />;
    return sortDirection === "asc" ? (
      <ArrowUp className="h-4 w-4 ml-1" />
    ) : (
      <ArrowDown className="h-4 w-4 ml-1" />
    );
  };

  if (isLoading) {
    return <TableSkeleton rows={15} columns={7} />;
  }

  return (
    <div className="rounded-md border border-border">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead className="w-[220px]">Address</TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => handleSort("perpEquity")}
            >
              <div className="flex items-center">
                Perp Equity
                <SortIcon field="perpEquity" />
              </div>
            </TableHead>
            <TableHead>Perp Bias</TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => handleSort("positionValue")}
            >
              <div className="flex items-center">
                Position Value
                <SortIcon field="positionValue" />
              </div>
            </TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => handleSort("leverage")}
            >
              <div className="flex items-center">
                Leverage
                <SortIcon field="leverage" />
              </div>
            </TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => handleSort("sumUpnl")}
            >
              <div className="flex items-center">
                Sum uPnL
                <SortIcon field="sumUpnl" />
              </div>
            </TableHead>
            <TableHead>Size Cohort</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedPositions.map((wp) => (
            <TableRow
              key={wp.address}
              className="cursor-pointer"
              onClick={() => onRowClick(wp.address)}
            >
              <TableCell>
                <AddressCell
                  address={wp.address}
                  label={getWalletLabel(wp.address)}
                />
              </TableCell>
              <TableCell className="font-mono">
                {formatCurrency(wp.perpEquity, true)}
              </TableCell>
              <TableCell>
                <BiasIndicator bias={wp.perpBias} />
              </TableCell>
              <TableCell className="font-mono">
                {formatCurrency(wp.positionValue, true)}
              </TableCell>
              <TableCell className="font-mono">
                {formatLeverage(wp.leverage)}
              </TableCell>
              <TableCell
                className={cn(
                  "font-mono",
                  wp.sumUpnl >= 0 ? "text-bullish" : "text-bearish"
                )}
              >
                {formatPnl(wp.sumUpnl)}
              </TableCell>
              <TableCell>
                <CohortBadge cohort={wp.sizeCohort} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
