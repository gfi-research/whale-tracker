import { useQuery } from "@tanstack/react-query";
import { nansenClient } from "@/lib/nansen-client";
import type { MarketData } from "@/types/whale";

const STALE_TIME = 5 * 60 * 1000; // 5 minutes

/**
 * Fetch market screener data
 */
export function useMarketData() {
  return useQuery<MarketData[]>({
    queryKey: ["markets"],
    queryFn: () => nansenClient.fetchMarketData(),
    staleTime: STALE_TIME,
    gcTime: 10 * 60 * 1000,
  });
}
