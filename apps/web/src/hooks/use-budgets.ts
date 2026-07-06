import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { Budget, BudgetCreate, BudgetStatus, BudgetUpdate } from "@/lib/api-types";
import { queryKeys } from "@/lib/query-keys";

export function useBudgetStatuses(month?: string) {
  return useQuery<BudgetStatus[]>({
    queryKey: queryKeys.budgets(month),
    queryFn: () => apiClient.get<BudgetStatus[]>("/api/budgets", { month }),
  });
}

export function useCreateBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BudgetCreate) => apiClient.post<Budget>("/api/budgets", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["budgets"] }),
  });
}

export function useUpdateBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BudgetUpdate }) =>
      apiClient.patch<Budget>(`/api/budgets/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["budgets"] }),
  });
}

export function useDeleteBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/budgets/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["budgets"] }),
  });
}
