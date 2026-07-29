"use client";

import {
  ArrowUpRight,
  ClipboardList,
  Plus,
  ReceiptText,
  PiggyBank,
  TrendingDown,
  TrendingUp,
  Wallet,
} from "lucide-react";
import { useTranslations } from "next-intl";
import Link from "next/link";
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
import { useFinancialPreferences } from "@/hooks/use-financial-preferences";
import { useIncomeEntries } from "@/hooks/use-income";
import { useInsights } from "@/hooks/use-insights";
import { useMonthlyTotals } from "@/hooks/use-monthly-totals";
import { useSavingsGoals } from "@/hooks/use-savings-goals";
import type { Category, ExpenseEntry } from "@/lib/api-types";
import { groupExpensesByCategory, savingsRate, sumAmounts } from "@/lib/finance-aggregation";
import { formatCurrency, formatPercent, monthParam } from "@/lib/format";
import { compoundProjection } from "@/lib/savings-simulation";

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
  const savingsGoals = useSavingsGoals();
  const { savingsTargetMode, savingsTargetValue } = useFinancialPreferences();

  const totalIncome = sumAmounts(income.data ?? []);
  const totalExpenses = sumAmounts(expenses.data ?? []);
  const available = totalIncome - totalExpenses;
  const savingsCategoryIds = new Set(
    (categories.data ?? [])
      .filter(
        (category) =>
          category.kind === "expense" &&
          (category.icon === "piggy-bank" || category.name.trim().toLocaleLowerCase("de-DE") === "sparen")
      )
      .map((category) => category.id)
  );
  const savingsAmount = sumAmounts(
    (expenses.data ?? []).filter(
      (entry) => entry.category_id !== null && savingsCategoryIds.has(entry.category_id)
    )
  );
  const consumptionExpenses = Math.max(0, totalExpenses - savingsAmount);
  const consumptionRate = totalIncome > 0 ? (consumptionExpenses / totalIncome) * 100 : 0;
  const rate = savingsRate(totalIncome, savingsAmount);
  const savingsTargetAmount =
    savingsTargetMode === "percent"
      ? (totalIncome * savingsTargetValue) / 100
      : savingsTargetValue;

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

  const goalProgressList = savingsGoals.data ?? [];
  const totalMonthlyGoalContribution = goalProgressList.reduce(
    (sum, progress) => sum + Number(progress.goal.monthly_contribution ?? 0),
    0
  );
  const projectionData = Array.from({ length: PROJECTION_YEARS + 1 }, (_, index) => {
    const months = index * 12;
    return goalProgressList.reduce(
      (point, progress) => {
        const current = Number(progress.current_amount);
        const monthly = Number(progress.goal.monthly_contribution ?? 0);
        const minReturn = Number(progress.goal.annual_return_min_pct ?? 0);
        const maxReturn = Number(progress.goal.annual_return_max_pct ?? 0);
        const lower = compoundProjection(current, monthly, minReturn, months);
        const upper = compoundProjection(current, monthly, maxReturn, months);
        point.eingezahlt += lower.contributed;
        point.szenarioMin += lower.futureValue;
        point.szenarioMax += upper.futureValue;
        return point;
      },
      { jahr: index === 0 ? "Heute" : `${index} J.`, eingezahlt: 0, szenarioMin: 0, szenarioMax: 0 }
    );
  });

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--color-brand)]">
            Finanz-Cockpit
          </p>
          <h1 className="mt-1 text-2xl font-bold tracking-[-0.03em] text-[var(--color-ink)]">
            Deine Finanzen auf einen Blick
          </h1>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Cashflow, Budgets und Sparfortschritt für {new Intl.DateTimeFormat("de-DE", { month: "long", year: "numeric" }).format(month)}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/income" className="dashboard-action dashboard-action--secondary">
            <Plus className="h-4 w-4" /> Einnahme
          </Link>
          <Link href="/expenses" className="dashboard-action">
            <ReceiptText className="h-4 w-4" /> Ausgabe erfassen
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 2xl:grid-cols-4">
        <KpiCard
          label={tKpi("monthlyIncome")}
          value={formatCurrency(totalIncome)}
          subtitle="Gesamteinnahmen"
          tone="green"
          icon={<Wallet className="h-6 w-6" aria-hidden="true" />}
        />
        <KpiCard
          label={tKpi("monthlyExpenses")}
          value={formatCurrency(totalExpenses)}
          subtitle="Diesen Monat"
          tone="red"
          icon={<TrendingDown className="h-6 w-6" aria-hidden="true" />}
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
          tone="green"
          icon={<TrendingUp className="h-6 w-6" aria-hidden="true" />}
        />
        <KpiCard
          label="Gespart diesen Monat"
          value={
            savingsTargetMode === "amount"
              ? formatCurrency(savingsAmount)
              : rate !== null
                ? formatPercent(rate)
                : "–"
          }
          subtitle={
            rate === null
              ? `Keine Einnahmen · Monatsziel ${
                  savingsTargetMode === "amount"
                    ? formatCurrency(savingsTargetValue)
                    : formatPercent(savingsTargetValue)
                }`
              : `Sparquote ${formatPercent(rate)} · Monatsziel ${
                  savingsTargetMode === "amount"
                    ? formatCurrency(savingsTargetValue)
                    : formatPercent(savingsTargetValue)
                }`
          }
          delta={
            totalIncome > 0
              ? savingsAmount >= savingsTargetAmount
                ? "Sparziel erreicht"
                : savingsAmount === 0
                  ? "Noch keine Sparbuchung erfasst"
                  : `${formatCurrency(savingsTargetAmount - savingsAmount)} bis zum Ziel`
              : undefined
          }
          deltaTone={savingsAmount >= savingsTargetAmount ? "good" : "critical"}
          tone="purple"
          icon={<PiggyBank className="h-6 w-6" aria-hidden="true" />}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-8">
          <ChartShell
            title="Cashflow-Entwicklung"
            description="Einnahmen und Ausgaben · letzte 6 Monate"
            isLoading={trend.isLoading}
            isError={trend.isError}
            isEmpty={trendData.every((point) => point.einnahmen === 0 && point.ausgaben === 0)}
            textSummary={`Einnahmen und Ausgaben der letzten ${TREND_MONTHS} Monate im Vergleich.`}
            headerAction={
              <Link href="/expenses" className="module-link">
                Details <ArrowUpRight className="h-3.5 w-3.5" />
              </Link>
            }
          >
            <IncomeExpenseTrendChart data={trendData} />
          </ChartShell>
        </div>

        <Card className="overflow-hidden xl:col-span-4">
          <CardHeader className="border-b border-[var(--color-gridline)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-[var(--color-ink-muted)]">Monatsstatus</p>
                <CardTitle className="mt-1">Cashflow &amp; Ziele</CardTitle>
              </div>
              <span className={`cashflow-status ${available >= 0 ? "cashflow-status--good" : "cashflow-status--bad"}`}>
                <span className={`status-dot ${available >= 0 ? "status-dot--good" : "status-dot--bad"}`} />
                {available >= 0 ? "Positiver Cashflow" : "Negativer Cashflow"}
              </span>
            </div>
          </CardHeader>
          <CardContent className="grid gap-5 pt-5 md:pt-5">
            <div>
              <div className="mb-2 flex justify-between text-xs">
                <span className="text-[var(--color-ink-muted)]">Konsumquote</span>
                <strong>{totalIncome > 0 ? formatPercent(consumptionRate) : "–"}</strong>
              </div>
              <div className="dashboard-progress"><span style={{ width: `${Math.min(100, consumptionRate)}%` }} /></div>
            </div>
            <div>
              <div className="mb-2 flex justify-between text-xs">
                <span className="text-[var(--color-ink-muted)]">Sparziel</span>
                <strong>{savingsTargetAmount > 0 ? formatPercent(Math.min(100, (savingsAmount / savingsTargetAmount) * 100)) : "–"}</strong>
              </div>
              <div className="dashboard-progress dashboard-progress--purple"><span style={{ width: `${Math.min(100, savingsTargetAmount > 0 ? (savingsAmount / savingsTargetAmount) * 100 : 0)}%` }} /></div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="mini-stat">
                <span>Aktive Budgets</span>
                <strong>{(budgets.data ?? []).length}</strong>
              </div>
              <div className="mini-stat">
                <span>Belegte Kategorien</span>
                <strong>{donutSlices.length}</strong>
              </div>
            </div>
            <Link href="/budgets" className="dashboard-action w-full">
              Budgets &amp; Ziele verwalten <ArrowUpRight className="h-4 w-4" />
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-5">
          <ChartShell
            title={t("expensesByCategory")}
            description={`${donutSlices.length} Kategorien · ${formatCurrency(totalExpenses)} gesamt`}
            isLoading={expenses.isLoading || categories.isLoading}
            isError={expenses.isError}
            isEmpty={donutSlices.length === 0}
            textSummary={`Gesamtausgaben ${formatCurrency(totalExpenses)}, verteilt auf ${donutSlices.length} Kategorien.`}
          >
            <CategoryDonutChart slices={donutSlices} total={totalExpenses} />
          </ChartShell>
        </div>
        <div className="xl:col-span-7">
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
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <Card className="xl:col-span-5">
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>{t("budgetProgress")}</CardTitle>
            <Link href="/budgets" className="module-link">Alle Budgets <ArrowUpRight className="h-3.5 w-3.5" /></Link>
          </CardHeader>
          <CardContent className="flex min-h-64 flex-col gap-4">
            {budgets.isLoading ? <p className="text-sm text-[var(--color-ink-muted)]">…</p> :
            (budgets.data ?? []).length === 0 ? (
              <div className="flex flex-1 flex-col items-center justify-center text-center">
                <span className="mb-3 flex h-14 w-14 items-center justify-center rounded-xl bg-[var(--color-brand-light)] text-[var(--color-brand)]"><ClipboardList className="h-6 w-6" /></span>
                <p className="font-semibold">Noch keine Budgets festgelegt</p>
                <Link href="/budgets" className="module-link mt-3">Budget erstellen <ArrowUpRight className="h-3.5 w-3.5" /></Link>
              </div>
            ) : (budgets.data ?? []).slice(0, 5).map((status) => <BudgetProgressBar key={status.budget.id} status={status} />)}
          </CardContent>
        </Card>
        <div className="xl:col-span-4">
          <ChartShell
            title="Vermögensprojektion"
            description={`${goalProgressList.length} Sparziel${goalProgressList.length === 1 ? "" : "e"} · ${formatCurrency(totalMonthlyGoalContribution)} monatlich`}
            isLoading={savingsGoals.isLoading}
            isError={savingsGoals.isError}
            isEmpty={goalProgressList.length === 0}
            textSummary={`Aggregierte Entwicklung aller Sparziele über ${PROJECTION_YEARS} Jahre, getrennt nach Einzahlungen und illustrativer Renditespanne.`}
          >
            <SavingsProjectionChart data={projectionData} />
          </ChartShell>
        </div>
        <Card className="xl:col-span-3">
          <CardHeader><CardTitle>{t("insightsTitle")}</CardTitle></CardHeader>
          <CardContent className="flex max-h-[22rem] flex-col gap-3 overflow-y-auto">
            {insights.isLoading ? <p className="text-sm text-[var(--color-ink-muted)]">…</p> :
            (insights.data?.insights ?? []).length === 0 ? <p className="text-sm text-[var(--color-ink-muted)]">{t("noInsights")}</p> :
            (insights.data?.insights ?? []).map((insight, index) => <InsightCard key={`${insight.rule_key}-${index}`} insight={insight} />)}
          </CardContent>
        </Card>
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
