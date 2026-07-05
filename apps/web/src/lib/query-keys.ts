export const queryKeys = {
  session: ["session"] as const,
  categories: ["categories"] as const,
  income: (month?: string) => ["income", month] as const,
  expenses: (month?: string) => ["expenses", month] as const,
  budgets: (month?: string) => ["budgets", month] as const,
  savingsGoals: ["savings-goals"] as const,
  cities: ["cities"] as const,
  dataSources: ["data-sources"] as const,
  insights: (month?: string) => ["insights", month] as const,
};
