import { useQuery, useQueries } from "@tanstack/react-query";
import { WHALE_WALLETS } from "@/data/wallets";
import { nansenClient } from "@/lib/nansen-client";
import {
  calculatePerpBias,
  calculateSizeCohort,
  calculateWeightedLeverage,
  calculateTotalUnrealizedPnl,
  calculatePositionValue,
} from "@/lib/calculations";
import type { WalletPosition, Position } from "@/types/whale";

const STALE_TIME = 5 * 60 * 1000; // 5 minutes

/**
 * Fetch positions for a single wallet
 */
export function useWalletPositionsQuery(address: string) {
  return useQuery({
    queryKey: ["wallet", address, "positions"],
    queryFn: () => nansenClient.fetchWalletPositions(address),
    staleTime: STALE_TIME,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Compute wallet position summary from raw positions
 */
function computeWalletPosition(address: string, positions: Position[]): WalletPosition {
  const wallet = WHALE_WALLETS.find((w) => w.address === address);
  const perpEquity = wallet?.accountValue ?? 0;

  return {
    address,
    perpEquity,
    perpBias: calculatePerpBias(positions),
    positionValue: calculatePositionValue(positions),
    leverage: calculateWeightedLeverage(positions),
    sumUpnl: calculateTotalUnrealizedPnl(positions),
    sizeCohort: calculateSizeCohort(perpEquity),
  };
}

/**
 * Fetch positions for all wallets and compute summaries
 */
export function useAllWalletPositions() {
  const queries = useQueries({
    queries: WHALE_WALLETS.map((wallet) => ({
      queryKey: ["wallet", wallet.address, "positions"],
      queryFn: () => nansenClient.fetchWalletPositions(wallet.address),
      staleTime: STALE_TIME,
      gcTime: 10 * 60 * 1000,
    })),
    combine: (results) => {
      const isLoading = results.some((r) => r.isLoading);
      const isError = results.some((r) => r.isError);
      const loadingCount = results.filter((r) => r.isLoading).length;
      const loadedCount = results.filter((r) => r.isSuccess).length;

      const walletPositions: WalletPosition[] = results
        .map((result, index) => {
          const wallet = WHALE_WALLETS[index];
          const positions = result.data ?? [];
          return computeWalletPosition(wallet.address, positions);
        })
        .filter((wp) => wp.perpEquity > 0);

      return {
        data: walletPositions,
        isLoading,
        isError,
        loadingCount,
        loadedCount,
        totalCount: WHALE_WALLETS.length,
        progress: loadedCount / WHALE_WALLETS.length,
      };
    },
  });

  return queries;
}

/**
 * Get raw positions for a specific wallet (for modal display)
 */
export function useWalletDetailPositions(address: string | null) {
  return useQuery({
    queryKey: ["wallet", address, "positions"],
    queryFn: () => (address ? nansenClient.fetchWalletPositions(address) : Promise.resolve([])),
    enabled: Boolean(address),
    staleTime: STALE_TIME,
  });
}
