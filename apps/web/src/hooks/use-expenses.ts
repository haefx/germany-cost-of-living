import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { ExpenseEntry, ExpenseEntryCreate, ExpenseEntryUpdate } from "@/lib/api-types";
import { queryKeys } from "@/lib/query-keys";

export function useExpenseEntries(month?: string) {
  return useQuery<ExpenseEntry[]>({
    queryKey: queryKeys.expenses(month),
    queryFn: () => apiClient.get<ExpenseEntry[]>("/api/expenses", { month }),
  });
}

export function useCreateExpenseEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ExpenseEntryCreate) => apiClient.post<ExpenseEntry>("/api/expenses", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["insights"] });
    },
  });
}

export function useUpdateExpenseEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ExpenseEntryUpdate }) =>
      apiClient.patch<ExpenseEntry>(`/api/expenses/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["insights"] });
    },
  });
}

export function useDeleteExpenseEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/expenses/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["insights"] });
    },
  });
}
