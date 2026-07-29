"use client";

import { Info, Pencil, Plus, TrendingUp, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { Suspense, useState } from "react";

import { BudgetProgressBar } from "@/components/charts/budget-progress-bar";
import { useSelectedMonth } from "@/components/layout/month-selector";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useBudgetStatuses, useCreateBudget, useDeleteBudget } from "@/hooks/use-budgets";
import { useCategories } from "@/hooks/use-categories";
import {
  useAddContribution,
  useCreateSavingsGoal,
  useDeleteSavingsGoal,
  useSavingsGoals,
  useUpdateSavingsGoal,
} from "@/hooks/use-savings-goals";
import { formatCurrency, formatDate, monthParam } from "@/lib/format";
import {
  findSavingsGoalTemplate,
  SAVINGS_GOAL_TEMPLATES,
} from "@/lib/savings-goal-templates";
import {
  addMonthsToToday,
  compoundProjection,
  monthsToReachTarget,
} from "@/lib/savings-simulation";

function BudgetsTab() {
  const t = useTranslations("budgets");
  const tCommon = useTranslations("common");
  const { month, monthValue } = useSelectedMonth();

  const budgets = useBudgetStatuses(monthValue);
  const categories = useCategories();
  const createBudget = useCreateBudget();
  const deleteBudget = useDeleteBudget();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [categoryId, setCategoryId] = useState<string>("");
  const [limit, setLimit] = useState("");

  const expenseCategories = (categories.data ?? []).filter(
    (category) => category.kind === "expense" && !category.is_archived
  );

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await createBudget.mutateAsync({
      category_id: categoryId,
      monthly_limit: limit,
      effective_from: monthParam(new Date(month.getFullYear(), month.getMonth(), 1)),
    });
    setDialogOpen(false);
    setCategoryId("");
    setLimit("");
  }

  const statuses = budgets.data ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4" aria-hidden="true" />
              {t("add")}
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("add")}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="budget-category">{tCommon("category")}</Label>
                <Select value={categoryId} onValueChange={setCategoryId} required>
                  <SelectTrigger id="budget-category">
                    <SelectValue placeholder={tCommon("category")} />
                  </SelectTrigger>
                  <SelectContent>
                    {expenseCategories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="budget-limit">{t("monthlyLimit")} (€)</Label>
                <Input
                  id="budget-limit"
                  type="number"
                  inputMode="decimal"
                  min="0.01"
                  step="0.01"
                  required
                  value={limit}
                  onChange={(event) => setLimit(event.target.value)}
                />
              </div>
              <DialogFooter>
                <Button type="button" variant="secondary" onClick={() => setDialogOpen(false)}>
                  {tCommon("cancel")}
                </Button>
                <Button type="submit" disabled={createBudget.isPending || !categoryId}>
                  {tCommon("save")}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {budgets.isLoading ? (
        <p className="text-sm text-[var(--color-ink-muted)]">{tCommon("loading")}</p>
      ) : statuses.length === 0 ? (
        <p className="text-sm text-[var(--color-ink-muted)]">{t("empty")}</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {statuses.map((status) => (
            <Card key={status.budget.id}>
              <CardContent className="p-4">
                <BudgetProgressBar status={status} />
                <div className="mt-2 flex justify-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    aria-label={`Budget ${status.category_name} löschen`}
                    onClick={() => deleteBudget.mutate(status.budget.id)}
                  >
                    <Trash2 className="h-4 w-4 text-[var(--color-ink-muted)]" />
                    {tCommon("delete")}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function SavingsGoalsTab() {
  const t = useTranslations("savingsGoals");
  const tCommon = useTranslations("common");

  const goals = useSavingsGoals();
  const createGoal = useCreateSavingsGoal();
  const deleteGoal = useDeleteSavingsGoal();
  const addContribution = useAddContribution();
  const updateGoal = useUpdateSavingsGoal();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [templateKey, setTemplateKey] = useState("cash");
  const [name, setName] = useState("");
  const [targetAmount, setTargetAmount] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [contributionAmounts, setContributionAmounts] = useState<Record<string, string>>({});
  const [simulationYears, setSimulationYears] = useState<Record<string, number>>({});
  const [editGoal, setEditGoal] = useState<{
    id: string;
    name: string;
    targetAmount: string;
    targetDate: string;
    monthlyContribution: string;
  } | null>(null);
  const selectedTemplate = findSavingsGoalTemplate(templateKey) ?? SAVINGS_GOAL_TEMPLATES[0]!;

  function handleTemplateChange(key: string) {
    const previousTemplate = findSavingsGoalTemplate(templateKey);
    const nextTemplate = findSavingsGoalTemplate(key);
    setTemplateKey(key);
    if (
      nextTemplate &&
      (!name || name === previousTemplate?.suggestedName)
    ) {
      setName(nextTemplate.suggestedName);
    }
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await createGoal.mutateAsync({
      name,
      target_amount: targetAmount,
      target_date: targetDate || null,
      template_key: selectedTemplate.key,
      annual_return_min_pct: selectedTemplate.returnMin,
      annual_return_max_pct: selectedTemplate.returnMax,
    });
    setDialogOpen(false);
    setName("");
    setTargetAmount("");
    setTargetDate("");
    setTemplateKey("cash");
  }

  async function handleAddContribution(goalId: string) {
    const amount = contributionAmounts[goalId];
    if (!amount) return;
    await addContribution.mutateAsync({
      goalId,
      data: { amount, contributed_on: new Date().toISOString().slice(0, 10) },
    });
    setContributionAmounts((current) => ({ ...current, [goalId]: "" }));
  }

  async function handleEditGoal(event: React.FormEvent) {
    event.preventDefault();
    if (!editGoal) return;
    await updateGoal.mutateAsync({
      id: editGoal.id,
      data: {
        name: editGoal.name,
        target_amount: editGoal.targetAmount,
        target_date: editGoal.targetDate || null,
        monthly_contribution: editGoal.monthlyContribution || null,
      },
    });
    setEditGoal(null);
  }

  const progressList = goals.data ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4" aria-hidden="true" />
              {t("add")}
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("add")}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="goal-template">Vorlage / Planungsannahme</Label>
                <Select value={templateKey} onValueChange={handleTemplateChange}>
                  <SelectTrigger id="goal-template">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SAVINGS_GOAL_TEMPLATES.map((template) => (
                      <SelectItem key={template.key} value={template.key}>
                        {template.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="rounded-lg border border-[#cfe0f8] bg-[#f5f9ff] p-3">
                <div className="flex gap-2.5">
                  <Info className="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-brand)]" />
                  <div>
                    <p className="text-sm font-medium text-[var(--color-ink)]">
                      {selectedTemplate.returnMin !== null
                        ? `${selectedTemplate.returnMin}–${selectedTemplate.returnMax} % p. a.`
                        : "Keine Renditeannahme"}
                    </p>
                    <p className="mt-1 text-xs leading-5 text-[var(--color-ink-secondary)]">
                      {selectedTemplate.description}
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="goal-name">{tCommon("name")}</Label>
                <Input
                  id="goal-name"
                  required
                  maxLength={200}
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="goal-target">{t("targetAmount")} (€)</Label>
                  <Input
                    id="goal-target"
                    type="number"
                    inputMode="decimal"
                    min="0.01"
                    step="0.01"
                    required
                    value={targetAmount}
                    onChange={(event) => setTargetAmount(event.target.value)}
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="goal-date">{t("targetDate")}</Label>
                  <Input
                    id="goal-date"
                    type="date"
                    value={targetDate}
                    onChange={(event) => setTargetDate(event.target.value)}
                  />
                </div>
              </div>
              <DialogFooter>
                <p className="mr-auto max-w-xs text-[11px] leading-4 text-[var(--color-ink-muted)]">
                  Reine Information, keine Anlageberatung. Renditen sind nicht garantiert; Kosten,
                  Steuern und Inflation sind nicht berücksichtigt.
                </p>
                <Button type="button" variant="secondary" onClick={() => setDialogOpen(false)}>
                  {tCommon("cancel")}
                </Button>
                <Button type="submit" disabled={createGoal.isPending}>
                  {tCommon("save")}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
        <Dialog open={editGoal !== null} onOpenChange={(open) => !open && setEditGoal(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Sparziel bearbeiten</DialogTitle>
            </DialogHeader>
            {editGoal ? (
              <form onSubmit={handleEditGoal} className="grid gap-4">
                <div className="grid gap-1.5">
                  <Label htmlFor="edit-goal-name">Name</Label>
                  <Input
                    id="edit-goal-name"
                    required
                    value={editGoal.name}
                    onChange={(event) => setEditGoal({ ...editGoal, name: event.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="grid gap-1.5">
                    <Label htmlFor="edit-goal-target">Zielbetrag (€)</Label>
                    <Input
                      id="edit-goal-target"
                      type="number"
                      min="0.01"
                      step="0.01"
                      required
                      value={editGoal.targetAmount}
                      onChange={(event) =>
                        setEditGoal({ ...editGoal, targetAmount: event.target.value })
                      }
                    />
                  </div>
                  <div className="grid gap-1.5">
                    <Label htmlFor="edit-goal-date">Zieldatum</Label>
                    <Input
                      id="edit-goal-date"
                      type="date"
                      value={editGoal.targetDate}
                      onChange={(event) =>
                        setEditGoal({ ...editGoal, targetDate: event.target.value })
                      }
                    />
                  </div>
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor="edit-goal-rate">Monatliche Einzahlung (€)</Label>
                  <Input
                    id="edit-goal-rate"
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={editGoal.monthlyContribution}
                    onChange={(event) =>
                      setEditGoal({ ...editGoal, monthlyContribution: event.target.value })
                    }
                  />
                </div>
                <DialogFooter>
                  <Button type="button" variant="secondary" onClick={() => setEditGoal(null)}>
                    {tCommon("cancel")}
                  </Button>
                  <Button type="submit" disabled={updateGoal.isPending}>
                    {tCommon("save")}
                  </Button>
                </DialogFooter>
              </form>
            ) : null}
          </DialogContent>
        </Dialog>
      </div>

      {goals.isLoading ? (
        <p className="text-sm text-[var(--color-ink-muted)]">{tCommon("loading")}</p>
      ) : progressList.length === 0 ? (
        <p className="text-sm text-[var(--color-ink-muted)]">{t("empty")}</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {progressList.map((progress) => {
            const pct = Math.min(100, Number.parseFloat(progress.progress_pct));
            const startingCapital = Number(progress.current_amount);
            const monthlyContribution = Number(progress.goal.monthly_contribution ?? 0);
            const returnMin = Number(progress.goal.annual_return_min_pct ?? 0);
            const returnMax = Number(progress.goal.annual_return_max_pct ?? 0);
            const hasReturnAssumption =
              progress.goal.annual_return_min_pct !== null &&
              progress.goal.annual_return_max_pct !== null;
            const years = simulationYears[progress.goal.id] ?? 10;
            const lowProjection = compoundProjection(
              startingCapital,
              monthlyContribution,
              returnMin,
              years * 12
            );
            const highProjection = compoundProjection(
              startingCapital,
              monthlyContribution,
              returnMax,
              years * 12
            );
            const target = Number(progress.goal.target_amount);
            const earliestTargetMonth = hasReturnAssumption
              ? monthsToReachTarget(startingCapital, monthlyContribution, returnMax, target)
              : null;
            const latestTargetMonth = hasReturnAssumption
              ? monthsToReachTarget(startingCapital, monthlyContribution, returnMin, target)
              : null;
            return (
              <Card key={progress.goal.id}>
                <CardHeader className="flex-row items-center justify-between space-y-0">
                  <CardTitle>{progress.goal.name}</CardTitle>
                  <div className="flex">
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`${progress.goal.name} bearbeiten`}
                      onClick={() =>
                        setEditGoal({
                          id: progress.goal.id,
                          name: progress.goal.name,
                          targetAmount: String(progress.goal.target_amount),
                          targetDate: progress.goal.target_date ?? "",
                          monthlyContribution: progress.goal.monthly_contribution
                            ? String(progress.goal.monthly_contribution)
                            : "",
                        })
                      }
                    >
                      <Pencil className="h-4 w-4 text-[var(--color-ink-muted)]" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`${progress.goal.name} löschen`}
                      onClick={() => deleteGoal.mutate(progress.goal.id)}
                    >
                      <Trash2 className="h-4 w-4 text-[var(--color-ink-muted)]" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  {progress.goal.monthly_contribution ? (
                    <p className="text-sm text-[var(--color-ink-secondary)]">
                      Monatliche Einzahlung:{" "}
                      <strong className="font-semibold text-[var(--color-ink)]">
                        {formatCurrency(progress.goal.monthly_contribution)}
                      </strong>
                    </p>
                  ) : null}
                  {progress.goal.annual_return_min_pct !== null &&
                  progress.goal.annual_return_max_pct !== null ? (
                    <div className="flex items-center gap-2 rounded-md bg-[color-mix(in_srgb,var(--color-secondary)_7%,white)] px-3 py-2 text-xs text-[var(--color-ink-secondary)]">
                      <TrendingUp className="h-4 w-4 shrink-0 text-[var(--color-secondary)]" />
                      <span>
                        Illustrative Annahme:{" "}
                        <strong className="font-semibold text-[var(--color-ink)]">
                          {Number(progress.goal.annual_return_min_pct)}–
                          {Number(progress.goal.annual_return_max_pct)} % p. a.
                        </strong>
                      </span>
                    </div>
                  ) : null}
                  {hasReturnAssumption && monthlyContribution > 0 ? (
                    <div className="rounded-xl border border-[#e2dcf5] bg-gradient-to-br from-[#faf8ff] to-white p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--color-secondary)]">
                            Zinseszins-Simulation
                          </p>
                          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">
                            Startkapital + monatliche Einzahlungen
                          </p>
                        </div>
                        <Select
                          value={String(years)}
                          onValueChange={(value) =>
                            setSimulationYears((current) => ({
                              ...current,
                              [progress.goal.id]: Number(value),
                            }))
                          }
                        >
                          <SelectTrigger className="h-8 w-28 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {[5, 10, 15, 20, 30].map((value) => (
                              <SelectItem key={value} value={String(value)}>
                                {value} Jahre
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="mt-4 grid grid-cols-2 gap-3">
                        <div className="mini-stat">
                          <span>Eigene Einzahlungen</span>
                          <strong className="!text-base">
                            {formatCurrency(lowProjection.contributed)}
                          </strong>
                          <small className="text-[10px] leading-4 text-[var(--color-ink-muted)]">
                            {formatCurrency(startingCapital)} Start + {years * 12} ×{" "}
                            {formatCurrency(monthlyContribution)}
                          </small>
                        </div>
                        <div className="mini-stat">
                          <span>Möglicher Wert nach {years} J.</span>
                          <strong className="!text-base text-[var(--color-secondary)]">
                            {formatCurrency(lowProjection.futureValue)}–
                            {formatCurrency(highProjection.futureValue)}
                          </strong>
                        </div>
                      </div>
                      <div className="mt-3 flex items-center justify-between border-t border-[#ece7f8] pt-3 text-xs">
                        <span className="text-[var(--color-ink-muted)]">
                          Hypothetischer Zinseszinseffekt
                        </span>
                        <strong className="text-[var(--color-good-text)]">
                          +{formatCurrency(lowProjection.hypotheticalGrowth)}–
                          {formatCurrency(highProjection.hypotheticalGrowth)}
                        </strong>
                      </div>
                      <p className="mt-2 text-[10px] leading-4 text-[var(--color-ink-muted)]">
                        Jede der {years * 12} Monatsraten wird ab dem jeweiligen
                        Einzahlungszeitpunkt bis zum Ende des Zeitraums mitverzinst.
                      </p>
                      {earliestTargetMonth !== null && latestTargetMonth !== null ? (
                        <p className="mt-3 rounded-lg bg-white px-3 py-2 text-xs text-[var(--color-ink-secondary)]">
                          Zielkorridor: voraussichtlich zwischen{" "}
                          <strong>{formatDate(addMonthsToToday(earliestTargetMonth))}</strong> und{" "}
                          <strong>{formatDate(addMonthsToToday(latestTargetMonth))}</strong>
                        </p>
                      ) : null}
                      <p className="mt-3 text-[10px] leading-4 text-[var(--color-ink-muted)]">
                        Illustration bei gleichbleibender Rate und monatlicher Verzinsung. Keine
                        Garantie oder Anlageberatung; Kosten, Steuern und Inflation sind nicht
                        berücksichtigt.
                      </p>
                    </div>
                  ) : null}
                  <div>
                    <div className="mb-1 flex justify-between text-sm">
                      <span className="text-[var(--color-ink-secondary)]">{t("progress")}</span>
                      <span className="tabular-nums font-medium">
                        {formatCurrency(progress.current_amount)} /{" "}
                        {formatCurrency(progress.goal.target_amount)}
                      </span>
                    </div>
                    <div
                      role="progressbar"
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={pct}
                      aria-label={`${t("progress")} ${progress.goal.name}`}
                      className="h-2 overflow-hidden rounded-full bg-[var(--color-gridline)]"
                    >
                      <div
                        className="h-full rounded-full bg-[var(--color-secondary)]"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    {!hasReturnAssumption ? (
                      <p className="mt-1 text-xs text-[var(--color-ink-muted)]">
                        {progress.projected_completion_date
                          ? `${t("projectedCompletion")}: ${formatDate(progress.projected_completion_date)}`
                          : t("noProjection")}
                      </p>
                    ) : null}
                  </div>
                  <div className="flex items-end gap-2">
                    <div className="flex flex-1 flex-col gap-1">
                      <Label htmlFor={`contribution-${progress.goal.id}`} className="text-xs">
                        Sonderzahlung hinzufügen (€)
                      </Label>
                      <Input
                        id={`contribution-${progress.goal.id}`}
                        type="number"
                        inputMode="decimal"
                        min="0.01"
                        step="0.01"
                        value={contributionAmounts[progress.goal.id] ?? ""}
                        onChange={(event) =>
                          setContributionAmounts((current) => ({
                            ...current,
                            [progress.goal.id]: event.target.value,
                          }))
                        }
                      />
                    </div>
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => handleAddContribution(progress.goal.id)}
                      disabled={addContribution.isPending || !contributionAmounts[progress.goal.id]}
                    >
                      {tCommon("add")}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

function BudgetsPageContent() {
  const tBudgets = useTranslations("budgets");
  const tGoals = useTranslations("savingsGoals");

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-[var(--color-ink)]">
        {tBudgets("title")} & {tGoals("title")}
      </h1>
      <Tabs defaultValue="budgets">
        <TabsList>
          <TabsTrigger value="budgets">{tBudgets("title")}</TabsTrigger>
          <TabsTrigger value="goals">{tGoals("title")}</TabsTrigger>
        </TabsList>
        <TabsContent value="budgets">
          <BudgetsTab />
        </TabsContent>
        <TabsContent value="goals">
          <SavingsGoalsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function BudgetsPage() {
  return (
    <Suspense fallback={null}>
      <BudgetsPageContent />
    </Suspense>
  );
}
