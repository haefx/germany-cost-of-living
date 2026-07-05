import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { IncomeEntry, IncomeEntryCreate, IncomeEntryUpdate } from "@/lib/api-types";
import { queryKeys } from "@/lib/query-keys";

export function useIncomeEntries(month?: string) {
  return useQuery<IncomeEntry[]>({
    queryKey: queryKeys.income(month),
    queryFn: () => apiClient.get<IncomeEntry[]>("/api/income", { month }),
  });
}

export function useCreateIncomeEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: IncomeEntryCreate) => apiClient.post<IncomeEntry>("/api/income", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["income"] }),
  });
}

export function useUpdateIncomeEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: IncomeEntryUpdate }) =>
      apiClient.patch<IncomeEntry>(`/api/income/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["income"] }),
  });
}

export function useDeleteIncomeEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/income/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["income"] }),
  });
}
