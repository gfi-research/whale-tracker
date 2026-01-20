"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { WalletTable } from "./WalletTable";
import { MarketTable } from "./MarketTable";
import { PositionModal } from "./PositionModal";
import { AttributionFooter } from "./AttributionFooter";
import { useAllWalletPositions } from "@/hooks/useWalletPositions";
import { useMarketData } from "@/hooks/useMarketData";
import { useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Wallet, BarChart3, AlertCircle } from "lucide-react";
import { formatCurrency } from "@/lib/format";
import { WALLET_COUNT } from "@/data/wallets";

export function Dashboard() {
  const [selectedAddress, setSelectedAddress] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const {
    data: walletPositions,
    isLoading: walletsLoading,
    isError: walletsError,
    progress,
  } = useAllWalletPositions();

  const {
    data: marketData,
    isLoading: marketsLoading,
    isError: marketsError,
  } = useMarketData();

  const handleRowClick = (address: string) => {
    setSelectedAddress(address);
    setModalOpen(true);
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["wallet"] });
    queryClient.invalidateQueries({ queryKey: ["markets"] });
  };

  // Calculate summary stats
  const totalEquity = walletPositions?.reduce((sum, w) => sum + w.perpEquity, 0) ?? 0;
  const totalPositionValue = walletPositions?.reduce((sum, w) => sum + w.positionValue, 0) ?? 0;
  const bullishCount = walletPositions?.filter((w) =>
    w.perpBias.includes("Bullish")
  ).length ?? 0;
  const bearishCount = walletPositions?.filter((w) =>
    w.perpBias.includes("Bearish")
  ).length ?? 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Whale Tracker
            </h1>
            <p className="text-muted-foreground mt-1">
              Track smart money positions on Hyperliquid
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={walletsLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${walletsLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {/* Error Alert */}
        {(walletsError || marketsError) && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Failed to fetch some data. Showing cached or mock data.
            </AlertDescription>
          </Alert>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Tracked Wallets</CardDescription>
              <CardTitle className="text-2xl">{WALLET_COUNT}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                {walletsLoading
                  ? `Loading... ${Math.round(progress * 100)}%`
                  : `${walletPositions?.length ?? 0} with positions`}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Equity</CardDescription>
              <CardTitle className="text-2xl">
                {formatCurrency(totalEquity, true)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                Across all tracked wallets
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Position Value</CardDescription>
              <CardTitle className="text-2xl">
                {formatCurrency(totalPositionValue, true)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                Total open positions
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Market Sentiment</CardDescription>
              <CardTitle className="text-2xl flex items-center gap-2">
                <span className="text-bullish">{bullishCount}</span>
                <span className="text-muted-foreground">/</span>
                <span className="text-bearish">{bearishCount}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                Bullish / Bearish wallets
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="wallets" className="space-y-4">
          <TabsList>
            <TabsTrigger value="wallets" className="gap-2">
              <Wallet className="h-4 w-4" />
              Wallets
            </TabsTrigger>
            <TabsTrigger value="markets" className="gap-2">
              <BarChart3 className="h-4 w-4" />
              Markets
            </TabsTrigger>
          </TabsList>

          <TabsContent value="wallets" className="space-y-4">
            <WalletTable
              walletPositions={walletPositions ?? []}
              isLoading={walletsLoading}
              onRowClick={handleRowClick}
            />
          </TabsContent>

          <TabsContent value="markets" className="space-y-4">
            <MarketTable
              marketData={marketData ?? []}
              isLoading={marketsLoading}
            />
          </TabsContent>
        </Tabs>

        {/* Position Modal */}
        <PositionModal
          address={selectedAddress}
          open={modalOpen}
          onOpenChange={setModalOpen}
        />

        {/* Attribution Footer */}
        <AttributionFooter />
      </div>
    </div>
  );
}
