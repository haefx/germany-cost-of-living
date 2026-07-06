import type { components } from "@gcol/shared-types";

type Schemas = components["schemas"];

export type Category = Schemas["CategoryRead"];
export type CategoryCreate = Schemas["CategoryCreate"];
export type CategoryUpdate = Schemas["CategoryUpdate"];

export type IncomeEntry = Schemas["IncomeEntryRead"];
export type IncomeEntryCreate = Schemas["IncomeEntryCreate"];
export type IncomeEntryUpdate = Schemas["IncomeEntryUpdate"];

export type ExpenseEntry = Schemas["ExpenseEntryRead"];
export type ExpenseEntryCreate = Schemas["ExpenseEntryCreate"];
export type ExpenseEntryUpdate = Schemas["ExpenseEntryUpdate"];

export type RecurrenceRuleCreate = Schemas["RecurrenceRuleCreate"];

export type Budget = Schemas["BudgetRead"];
export type BudgetCreate = Schemas["BudgetCreate"];
export type BudgetUpdate = Schemas["BudgetUpdate"];
export type BudgetStatus = Schemas["BudgetStatusRead"];

export type SavingsGoal = Schemas["SavingsGoalRead"];
export type SavingsGoalCreate = Schemas["SavingsGoalCreate"];
export type SavingsGoalUpdate = Schemas["SavingsGoalUpdate"];
export type SavingsGoalProgress = Schemas["SavingsGoalProgressRead"];
export type SavingsGoalContribution = Schemas["SavingsGoalContributionRead"];
export type SavingsGoalContributionCreate = Schemas["SavingsGoalContributionCreate"];

export type CityComparison = Schemas["CityComparisonRead"];
export type DataSourceStatus = Schemas["DataSourceStatusRead"];
export type PlzLookupResponse = Schemas["PlzLookupResponse"];

export type Insight = Schemas["InsightRead"];
export type InsightsResponse = Schemas["InsightsResponse"];

export type User = Schemas["UserRead"];
export type UserCreate = Schemas["UserCreate"];
export type UserUpdate = Schemas["UserUpdate"];

export type CategoryKind = Category["kind"];
