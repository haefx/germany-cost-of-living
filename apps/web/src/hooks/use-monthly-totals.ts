import { useQueries } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { ExpenseEntry, IncomeEntry } from "@/lib/api-types";
import {
  previousMonthsOf,
  shortMonthLabel,
  sumAmounts,
} from "@/lib/finance-aggregation";
import { monthParam } from "@/lib/format";

export interface MonthlyTotals {
  month: Date;
  label: string;
  income: number;
  expenses: number;
}

/** Fetches income+expense entries for the selected month and its
 * predecessors in parallel and reduces them to per-month totals — the data
 * behind the trend charts.
 */
export function useMonthlyTotals(selectedMonth: Date, monthCount: number) {
  const months = previousMonthsOf(selectedMonth, monthCount);

  const results = useQueries({
    queries: months.flatMap((month) => {
      const param = monthParam(month);
      return [
        {
          queryKey: ["income", param],
          queryFn: () => apiClient.get<IncomeEntry[]>("/api/income", { month: param }),
          staleTime: 30_000,
        },
        {
          queryKey: ["expenses", param],
          queryFn: () => apiClient.get<ExpenseEntry[]>("/api/expenses", { month: param }),
          staleTime: 30_000,
        },
      ];
    }),
  });

  const isLoading = results.some((result) => result.isLoading);
  const isError = results.some((result) => result.isError);

  const totals: MonthlyTotals[] = months.map((month, index) => {
    const incomeResult = results[index * 2];
    const expenseResult = results[index * 2 + 1];
    return {
      month,
      label: shortMonthLabel(month),
      income: sumAmounts((incomeResult?.data as IncomeEntry[] | undefined) ?? []),
      expenses: sumAmounts((expenseResult?.data as ExpenseEntry[] | undefined) ?? []),
    };
  });

  return { totals, isLoading, isError };
}
