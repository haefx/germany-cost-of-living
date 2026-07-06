import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { InsightsResponse } from "@/lib/api-types";
import { queryKeys } from "@/lib/query-keys";

export function useInsights(month?: string) {
  return useQuery<InsightsResponse>({
    queryKey: queryKeys.insights(month),
    queryFn: () => apiClient.get<InsightsResponse>("/api/insights", { month }),
  });
}
