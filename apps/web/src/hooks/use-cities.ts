import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { CityComparison, DataSourceStatus, PlzLookupResponse } from "@/lib/api-types";
import { queryKeys } from "@/lib/query-keys";

export function useCityComparisons() {
  return useQuery<CityComparison[]>({
    queryKey: queryKeys.cities,
    queryFn: () => apiClient.get<CityComparison[]>("/api/cities"),
  });
}

export function useDataSources() {
  return useQuery<DataSourceStatus[]>({
    queryKey: queryKeys.dataSources,
    queryFn: () => apiClient.get<DataSourceStatus[]>("/api/data-sources"),
  });
}

export function usePlzLookup(postalCode: string) {
  return useQuery<PlzLookupResponse>({
    queryKey: ["plz", postalCode],
    queryFn: () => apiClient.get<PlzLookupResponse>(`/api/plz/${postalCode}`),
    enabled: /^\d{5}$/.test(postalCode),
    retry: false,
  });
}
