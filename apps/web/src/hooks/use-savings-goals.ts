import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type {
  SavingsGoal,
  SavingsGoalContribution,
  SavingsGoalContributionCreate,
  SavingsGoalCreate,
  SavingsGoalProgress,
  SavingsGoalUpdate,
} from "@/lib/api-types";
import { queryKeys } from "@/lib/query-keys";

export function useSavingsGoals() {
  return useQuery<SavingsGoalProgress[]>({
    queryKey: queryKeys.savingsGoals,
    queryFn: () => apiClient.get<SavingsGoalProgress[]>("/api/savings-goals"),
  });
}

export function useCreateSavingsGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SavingsGoalCreate) =>
      apiClient.post<SavingsGoal>("/api/savings-goals", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.savingsGoals }),
  });
}

export function useUpdateSavingsGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: SavingsGoalUpdate }) =>
      apiClient.patch<SavingsGoal>(`/api/savings-goals/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.savingsGoals }),
  });
}

export function useDeleteSavingsGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/savings-goals/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.savingsGoals }),
  });
}

export function useAddContribution() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ goalId, data }: { goalId: string; data: SavingsGoalContributionCreate }) =>
      apiClient.post<SavingsGoalContribution>(
        `/api/savings-goals/${goalId}/contributions`,
        data
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.savingsGoals }),
  });
}

export function useDeleteContribution() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ goalId, contributionId }: { goalId: string; contributionId: string }) =>
      apiClient.delete(`/api/savings-goals/${goalId}/contributions/${contributionId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.savingsGoals }),
  });
}
