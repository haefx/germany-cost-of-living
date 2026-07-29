import type { ExpenseEntry, IncomeEntry } from "@/lib/api-types";

export function sumAmounts(entries: Array<{ amount: string }>): number {
  return entries.reduce((total, entry) => {
    const amount = Number.parseFloat(entry.amount);
    return Number.isFinite(amount) ? total + amount : total;
  }, 0);
}

export function groupExpensesByCategory(
  entries: ExpenseEntry[]
): Map<string, { categoryId: string | null; total: number }> {
  const groups = new Map<string, { categoryId: string | null; total: number }>();
  for (const entry of entries) {
    const key = entry.category_id ?? "uncategorized";
    const existing = groups.get(key);
    const parsedAmount = Number.parseFloat(entry.amount);
    const amount = Number.isFinite(parsedAmount) ? parsedAmount : 0;
    if (existing) {
      existing.total += amount;
    } else {
      groups.set(key, { categoryId: entry.category_id ?? null, total: amount });
    }
  }
  return groups;
}

export function savingsRate(totalIncome: number, savingsAmount: number): number | null {
  if (totalIncome <= 0) return null;
  return (savingsAmount / totalIncome) * 100;
}

export function previousMonthsOf(month: Date, count: number): Date[] {
  return Array.from(
    { length: count },
    (_, index) => new Date(month.getFullYear(), month.getMonth() - (count - 1) + index, 1)
  );
}

const shortMonthFormatter = new Intl.DateTimeFormat("de-DE", { month: "short" });

export function shortMonthLabel(date: Date): string {
  return shortMonthFormatter.format(date);
}

export type { ExpenseEntry, IncomeEntry };
