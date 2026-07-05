"use client";

import { PiggyBank, TrendingDown, TrendingUp, Wallet } from "lucide-react";
import { useTranslations } from "next-intl";
import { Suspense } from "react";

import { BudgetProgressBar } from "@/components/charts/budget-progress-bar";
import {
  CategoryComparisonChart,
  type CategoryComparisonPoint,
} from "@/components/charts/category-comparison-chart";
import { CategoryDonutChart, type DonutSlice } from "@/components/charts/category-donut-chart";
import { ChartShell } from "@/components/charts/chart-shell";
import { assignSeriesColors } from "@/components/charts/chart-colors";
import { IncomeExpenseTrendChart } from "@/components/charts/income-expense-trend-chart";
import { SavingsProjectionChart } from "@/components/charts/savings-projection-chart";
import { InsightCard } from "@/components/insights/insight-card";
import { KpiCard } from "@/components/kpi/kpi-card";
import { useSelectedMonth } from "@/components/layout/month-selector";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useBudgetStatuses } from "@/hooks/use-budgets";
import { useCategories } from "@/hooks/use-categories";
import { useExpenseEntries } from "@/hooks/use-expenses";
import { useIncomeEntries } from "@/hooks/use-income";
import { useInsights } from "@/hooks/use-insights";
import { useMonthlyTotals } from "@/hooks/use-monthly-totals";
import type { Category, ExpenseEntry } from "@/lib/api-types";
import { groupExpensesByCategory, savingsRate, sumAmounts } from "@/lib/finance-aggregation";
import { formatCurrency, formatPercent, monthParam } from "@/lib/format";

const TREND_MONTHS = 6;
const PROJECTION_YEARS = 10;

function buildCategoryComparison(
  currentEntries: ExpenseEntry[],
  previousEntries: ExpenseEntry[],
  categories: Category[]
): CategoryComparisonPoint[] {
  const categoryNames = new Map(categories.map((category) => [category.id, category.name]));
  const current = groupExpensesByCategory(currentEntries);
  const previous = groupExpensesByCategory(previousEntries);
  const allKeys = new Set([...current.keys(), ...previous.keys()]);

  return [...allKeys]
    .map((key) => {
      const categoryId = current.get(key)?.categoryId ?? previous.get(key)?.categoryId ?? null;
      return {
        category: categoryId ? (categoryNames.get(categoryId) ?? "Unbekannt") : "Ohne Kategorie",
        aktuell: current.get(key)?.total ?? 0,
        vormonat: previous.get(key)?.total ?? 0,
      };
    })
    .sort((a, b) => b.aktuell - a.aktuell)
    .slice(0, 8);
}

function OverviewContent() {
  const t = useTranslations("overview");
  const tKpi = useTranslations("kpi");
  const { month, monthValue } = useSelectedMonth();
  const previousMonthValue = monthParam(new Date(month.getFullYear(), month.getMonth() - 1, 1));

  const income = useIncomeEntries(monthValue);
  const expenses = useExpenseEntries(monthValue);
  const previousExpenses = useExpenseEntries(previousMonthValue);
  const budgets = useBudgetStatuses(monthValue);
  const categories = useCategories();
  const insights = useInsights(monthValue);
  const trend = useMonthlyTotals(month, TREND_MONTHS);

  const totalIncome = sumAmounts(income.data ?? []);
  const totalExpenses = sumAmounts(expenses.data ?? []);
  const available = totalIncome - totalExpenses;
  const rate = savingsRate(totalIncome, totalExpenses);

  const categoryNames = new Map(
    (categories.data ?? []).map((category) => [category.id, category.name])
  );
  const expenseGroups = groupExpensesByCategory(expenses.data ?? []);
  const seriesColors = assignSeriesColors([...expenseGroups.keys()]);
  const donutSlices: DonutSlice[] = [...expenseGroups.entries()]
    .map(([key, group]) => ({
      id: key,
      name: group.categoryId
        ? (categoryNames.get(group.categoryId) ?? "Unbekannt")
        : "Ohne Kategorie",
      value: group.total,
      color: seriesColors.get(key) ?? "var(--color-series-8)",
    }))
    .sort((a, b) => b.value - a.value);

  const trendData = trend.totals.map((point) => ({
    month: point.label,
    einnahmen: point.income,
    ausgaben: point.expenses,
  }));

  const comparisonData = buildCategoryComparison(
    expenses.data ?? [],
    previousExpenses.data ?? [],
    categories.data ?? []
  );

  const projectionAmount = Math.max(0, available);
  const projectionData = Array.from({ length: PROJECTION_YEARS }, (_, index) => ({
    jahr: `${index + 1}`,
    eingezahlt: projectionAmount * 12 * (index + 1),
  }));

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-[var(--color-ink)]">{t("title")}</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label={tKpi("monthlyIncome")}
          value={formatCurrency(totalIncome)}
          icon={<Wallet className="h-4 w-4 text-[var(--color-good)]" aria-hidden="true" />}
        />
        <KpiCard
          label={tKpi("monthlyExpenses")}
          value={formatCurrency(totalExpenses)}
          icon={<TrendingDown className="h-4 w-4 text-[var(--color-critical)]" aria-hidden="true" />}
        />
        <KpiCard
          label={tKpi("available")}
          value={formatCurrency(available)}
          deltaTone={available >= 0 ? "good" : "critical"}
          delta={
            totalIncome > 0
              ? `${formatPercent((available / totalIncome) * 100)} der Einnahmen`
              : undefined
          }
          icon={<TrendingUp className="h-4 w-4 text-[var(--color-brand)]" aria-hidden="true" />}
        />
        <KpiCard
          label={tKpi("savingsRate")}
          value={rate !== null ? formatPercent(rate) : "–"}
          deltaTone={rate !== null && rate >= 0 ? "good" : "critical"}
          icon={<PiggyBank className="h-4 w-4 text-[var(--color-secondary)]" aria-hidden="true" />}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="flex flex-col gap-4 xl:col-span-2">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ChartShell
              title={t("expensesByCategory")}
              isLoading={expenses.isLoading || categories.isLoading}
              isError={expenses.isError}
              isEmpty={donutSlices.length === 0}
              textSummary={`Gesamtausgaben ${formatCurrency(totalExpenses)}, verteilt auf ${donutSlices.length} Kategorien. Größte Kategorie: ${donutSlices[0]?.name ?? "keine"}.`}
            >
              <CategoryDonutChart slices={donutSlices} total={totalExpenses} />
            </ChartShell>
            <ChartShell
              title={t("incomeVsExpenses")}
              description={t("last6Months")}
              isLoading={trend.isLoading}
              isError={trend.isError}
              isEmpty={trendData.every((point) => point.einnahmen === 0 && point.ausgaben === 0)}
              textSummary={`Einnahmen und Ausgaben der letzten ${TREND_MONTHS} Monate im Vergleich.`}
            >
              <IncomeExpenseTrendChart data={trendData} />
            </ChartShell>
          </div>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ChartShell
              title={t("categoryComparison")}
              description={t("thisMonthVsLast")}
              isLoading={expenses.isLoading || previousExpenses.isLoading}
              isError={expenses.isError || previousExpenses.isError}
              isEmpty={comparisonData.length === 0}
              textSummary="Vergleich der Ausgaben je Kategorie zwischen diesem und dem vorherigen Monat."
            >
              <CategoryComparisonChart data={comparisonData} />
            </ChartShell>
            <Card>
              <CardHeader>
                <CardTitle>{t("budgetProgress")}</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                {budgets.isLoading ? (
                  <p className="text-sm text-[var(--color-ink-muted)]">…</p>
                ) : (budgets.data ?? []).length === 0 ? (
                  <p className="text-sm text-[var(--color-ink-muted)]">
                    Noch keine Budgets festgelegt.
                  </p>
                ) : (
                  (budgets.data ?? []).map((status) => (
                    <BudgetProgressBar key={status.budget.id} status={status} />
                  ))
                )}
              </CardContent>
            </Card>
          </div>
          <ChartShell
            title={t("savingsProjection")}
            description={`Monatlich ${formatCurrency(projectionAmount)} zurückgelegt, Anlagehorizont ${PROJECTION_YEARS} Jahre, Wachstum 0 % (reine Einzahlungen). Illustratives Szenario, keine Finanz- oder Anlageberatung.`}
            isLoading={income.isLoading || expenses.isLoading}
            isError={income.isError || expenses.isError}
            isEmpty={projectionAmount <= 0}
            textSummary={`Bei ${formatCurrency(projectionAmount)} monatlicher Rücklage ergeben sich nach ${PROJECTION_YEARS} Jahren ${formatCurrency(projectionAmount * 12 * PROJECTION_YEARS)} an Einzahlungen.`}
          >
            <SavingsProjectionChart data={projectionData} />
          </ChartShell>
        </div>

        <div className="flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle>{t("insightsTitle")}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              {insights.isLoading ? (
                <p className="text-sm text-[var(--color-ink-muted)]">…</p>
              ) : (insights.data?.insights ?? []).length === 0 ? (
                <p className="text-sm text-[var(--color-ink-muted)]">{t("noInsights")}</p>
              ) : (
                (insights.data?.insights ?? []).map((insight, index) => (
                  <InsightCard key={`${insight.rule_key}-${index}`} insight={insight} />
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function OverviewPage() {
  return (
    <Suspense fallback={null}>
      <OverviewContent />
    </Suspense>
  );
}
