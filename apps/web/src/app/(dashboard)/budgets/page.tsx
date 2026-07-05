"use client";

import { Plus, Trash2 } from "lucide-react";
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
} from "@/hooks/use-savings-goals";
import { formatCurrency, formatDate, monthParam } from "@/lib/format";

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

  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [targetAmount, setTargetAmount] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [contributionAmounts, setContributionAmounts] = useState<Record<string, string>>({});

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await createGoal.mutateAsync({
      name,
      target_amount: targetAmount,
      target_date: targetDate || null,
    });
    setDialogOpen(false);
    setName("");
    setTargetAmount("");
    setTargetDate("");
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
      </div>

      {goals.isLoading ? (
        <p className="text-sm text-[var(--color-ink-muted)]">{tCommon("loading")}</p>
      ) : progressList.length === 0 ? (
        <p className="text-sm text-[var(--color-ink-muted)]">{t("empty")}</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {progressList.map((progress) => {
            const pct = Math.min(100, Number.parseFloat(progress.progress_pct));
            return (
              <Card key={progress.goal.id}>
                <CardHeader className="flex-row items-center justify-between space-y-0">
                  <CardTitle>{progress.goal.name}</CardTitle>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`${progress.goal.name} löschen`}
                    onClick={() => deleteGoal.mutate(progress.goal.id)}
                  >
                    <Trash2 className="h-4 w-4 text-[var(--color-ink-muted)]" />
                  </Button>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
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
                    <p className="mt-1 text-xs text-[var(--color-ink-muted)]">
                      {progress.projected_completion_date
                        ? `${t("projectedCompletion")}: ${formatDate(progress.projected_completion_date)}`
                        : t("noProjection")}
                    </p>
                  </div>
                  <div className="flex items-end gap-2">
                    <div className="flex flex-1 flex-col gap-1">
                      <Label htmlFor={`contribution-${progress.goal.id}`} className="text-xs">
                        {t("addContribution")} (€)
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
