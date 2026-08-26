"use client";

import { Download, Info, Pencil, Plus, Repeat, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { CsvImportDialog } from "@/components/forms/csv-import-dialog";
import {
  EntryFormFields,
  emptyEntryFormValues,
  entryFormToPayload,
  type EntryFormValues,
} from "@/components/forms/entry-form-fields";
import { useSelectedMonth } from "@/components/layout/month-selector";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useCategories } from "@/hooks/use-categories";
import {
  useCreateExpenseEntry,
  useDeleteExpenseEntry,
  useExpenseEntries,
  useUpdateExpenseEntry,
} from "@/hooks/use-expenses";
import { downloadCsvExport } from "@/hooks/use-export";
import { useCreateSavingsGoal } from "@/hooks/use-savings-goals";
import { sumAmounts } from "@/lib/finance-aggregation";
import { formatCurrency, formatDate } from "@/lib/format";
import type { ExpenseEntry, ExpenseEntryUpdate } from "@/lib/api-types";
import {
  findSavingsGoalTemplate,
  SAVINGS_GOAL_TEMPLATES,
} from "@/lib/savings-goal-templates";

function ExpensesContent() {
  const t = useTranslations("expenses");
  const tCommon = useTranslations("common");
  const { monthValue } = useSelectedMonth();
  const searchParams = useSearchParams();
  const searchTerm = (searchParams.get("q") ?? "").toLowerCase();

  const expenses = useExpenseEntries(monthValue);
  const categories = useCategories();
  const createEntry = useCreateExpenseEntry();
  const updateEntry = useUpdateExpenseEntry();
  const deleteEntry = useDeleteExpenseEntry();
  const createGoal = useCreateSavingsGoal();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [formValues, setFormValues] = useState<EntryFormValues>(emptyEntryFormValues);
  const [editingEntry, setEditingEntry] = useState<ExpenseEntry | null>(null);
  const [editFormValues, setEditFormValues] = useState<EntryFormValues>(emptyEntryFormValues);
  const [trackAsGoal, setTrackAsGoal] = useState(false);
  const [goalTarget, setGoalTarget] = useState("");
  const [goalDate, setGoalDate] = useState("");
  const [goalTemplate, setGoalTemplate] = useState("cash");

  const categoryNames = new Map(
    (categories.data ?? []).map((category) => [category.id, category.name])
  );
  const selectedCategory = (categories.data ?? []).find(
    (category) => category.id === formValues.categoryId
  );
  const isSavingsCategory =
    selectedCategory?.icon === "piggy-bank" ||
    selectedCategory?.name.trim().toLocaleLowerCase("de-DE") === "sparen";

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const entry = await createEntry.mutateAsync({
      ...entryFormToPayload(formValues),
      is_planned: false,
    });
    if (trackAsGoal && isSavingsCategory && goalTarget) {
      const template = findSavingsGoalTemplate(goalTemplate) ?? SAVINGS_GOAL_TEMPLATES[0]!;
      try {
        await createGoal.mutateAsync({
          name: formValues.label,
          target_amount: goalTarget,
          target_date: goalDate || null,
          template_key: template.key,
          annual_return_min_pct: template.returnMin,
          annual_return_max_pct: template.returnMax,
          monthly_contribution: formValues.amount,
          contribution_start_date: formValues.entryDate,
          linked_expense_id: entry.id,
        });
      } catch (error) {
        await deleteEntry.mutateAsync(entry.id);
        throw error;
      }
    }
    setDialogOpen(false);
    setFormValues(emptyEntryFormValues());
    setTrackAsGoal(false);
    setGoalTarget("");
    setGoalDate("");
    setGoalTemplate("cash");
  }

  function openEditDialog(entry: ExpenseEntry) {
    updateEntry.reset();
    setEditingEntry(entry);
    setEditFormValues({
      label: entry.label,
      amount: entry.source_amount ?? entry.amount,
      entryDate: entry.source_entry_date ?? entry.entry_date,
      categoryId: entry.category_id,
      isRecurring: entry.is_recurring,
      frequency: entry.recurrence?.frequency ?? "monthly",
    });
  }

  async function handleEditSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!editingEntry) return;

    const originalEntryDate = editingEntry.source_entry_date ?? editingEntry.entry_date;
    const entryDateChanged = editFormValues.entryDate !== originalEntryDate;
    const recurrenceChanged =
      editFormValues.isRecurring &&
      (!editingEntry.is_recurring ||
        entryDateChanged ||
        editFormValues.frequency !== editingEntry.recurrence?.frequency);
    const data: ExpenseEntryUpdate = {
      label: editFormValues.label,
      amount: editFormValues.amount,
      category_id: editFormValues.categoryId,
      is_recurring: editFormValues.isRecurring,
      recurrence: recurrenceChanged
          ? {
            frequency: editFormValues.frequency,
            interval_count: editingEntry.recurrence?.interval_count ?? 1,
            start_date: entryDateChanged
              ? editFormValues.entryDate
              : (editingEntry.recurrence?.start_date ?? editFormValues.entryDate),
            end_date: editingEntry.recurrence?.end_date ?? null,
          }
        : null,
    };

    // Later-month recurring rows carry an occurrence date. Keep the original
    // entry date unless the date field was intentionally changed.
    if (!editingEntry.is_recurring || entryDateChanged) {
      data.entry_date = editFormValues.entryDate;
    }
    if (editFormValues.isRecurring && !recurrenceChanged) {
      delete data.recurrence;
    }

    await updateEntry.mutateAsync({ id: editingEntry.id, data });
    setEditingEntry(null);
  }

  const allEntries = expenses.data ?? [];
  const entries = searchTerm
    ? allEntries.filter((entry) =>
        [entry.label, entry.merchant ?? "", entry.notes ?? ""]
          .join(" ")
          .toLowerCase()
          .includes(searchTerm)
      )
    : allEntries;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold text-[var(--color-ink)]">{t("title")}</h1>
          <p className="text-sm text-[var(--color-ink-secondary)]">
            Summe:{" "}
            <span className="font-medium tabular-nums">{formatCurrency(sumAmounts(entries))}</span>
            {searchTerm ? ` – Filter: „${searchTerm}“` : ""}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={() => downloadCsvExport("expenses")}>
            <Download className="h-4 w-4" aria-hidden="true" />
            {t("exportCsv")}
          </Button>
          <CsvImportDialog entity="expenses" />
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
              <form onSubmit={handleSubmit}>
                <EntryFormFields
                  values={formValues}
                  onChange={setFormValues}
                  categories={categories.data ?? []}
                  kind="expense"
                  idPrefix="expense"
                />
                {isSavingsCategory ? (
                  <div className="mt-4 rounded-lg border border-[var(--color-border)] bg-[#f8faff] p-3">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <Label htmlFor="track-savings-goal">Als Sparziel verfolgen</Label>
                        <p className="mt-1 text-xs text-[var(--color-ink-muted)]">
                          Übernimmt diesen Betrag als monatliche Einzahlung.
                        </p>
                      </div>
                      <Switch
                        id="track-savings-goal"
                        checked={trackAsGoal}
                        onCheckedChange={(checked) => {
                          setTrackAsGoal(checked);
                          if (checked) {
                            setFormValues({
                              ...formValues,
                              isRecurring: true,
                              frequency: "monthly",
                            });
                          }
                        }}
                      />
                    </div>
                    {trackAsGoal ? (
                      <div className="mt-4 grid gap-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="grid gap-1.5">
                            <Label htmlFor="linked-goal-target">Zielbetrag (€)</Label>
                            <Input
                              id="linked-goal-target"
                              type="number"
                              min="0.01"
                              step="0.01"
                              required
                              value={goalTarget}
                              onChange={(event) => setGoalTarget(event.target.value)}
                            />
                          </div>
                          <div className="grid gap-1.5">
                            <Label htmlFor="linked-goal-date">Zieldatum</Label>
                            <Input
                              id="linked-goal-date"
                              type="date"
                              value={goalDate}
                              onChange={(event) => setGoalDate(event.target.value)}
                            />
                          </div>
                        </div>
                        <div className="grid gap-1.5">
                          <Label htmlFor="linked-goal-template">Planungsannahme</Label>
                          <Select value={goalTemplate} onValueChange={setGoalTemplate}>
                            <SelectTrigger id="linked-goal-template"><SelectValue /></SelectTrigger>
                            <SelectContent>
                              {SAVINGS_GOAL_TEMPLATES.map((template) => (
                                <SelectItem key={template.key} value={template.key}>
                                  {template.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <p className="flex gap-2 text-[11px] leading-4 text-[var(--color-ink-muted)]">
                          <Info className="h-3.5 w-3.5 shrink-0" />
                          Monatliche Rate und Sonderzahlungen werden getrennt geführt. Renditeangaben
                          sind illustrative Informationen, keine Anlageberatung.
                        </p>
                      </div>
                    ) : null}
                  </div>
                ) : null}
                {createEntry.isError ? (
                  <p role="alert" className="mt-3 text-sm text-[var(--color-critical)]">
                    {tCommon("error")}
                  </p>
                ) : null}
                <DialogFooter>
                  <Button type="button" variant="secondary" onClick={() => setDialogOpen(false)}>
                    {tCommon("cancel")}
                  </Button>
                  <Button type="submit" disabled={createEntry.isPending || createGoal.isPending}>
                    {tCommon("save")}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          {expenses.isLoading ? (
            <p className="p-6 text-sm text-[var(--color-ink-muted)]">{tCommon("loading")}</p>
          ) : entries.length === 0 ? (
            <p className="p-6 text-sm text-[var(--color-ink-muted)]">{t("empty")}</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--color-gridline)] text-left text-xs text-[var(--color-ink-muted)]">
                    <th scope="col" className="px-4 py-3 font-medium">{t("label")}</th>
                    <th scope="col" className="px-4 py-3 font-medium">{tCommon("category")}</th>
                    <th scope="col" className="px-4 py-3 font-medium">{tCommon("date")}</th>
                    <th scope="col" className="px-4 py-3 text-right font-medium">{tCommon("amount")}</th>
                    <th scope="col" className="px-4 py-3 text-right font-medium">
                      <span className="sr-only">{tCommon("actions")}</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((entry) => (
                    <tr key={entry.id} className="border-b border-[var(--color-gridline)] last:border-0">
                      <td className="px-4 py-3 font-medium text-[var(--color-ink)]">
                        <span className="flex flex-wrap items-center gap-2">
                          {entry.label}
                          {entry.is_recurring ? (
                            <Badge variant="brand" className="gap-1">
                              <Repeat className="h-3 w-3" aria-hidden="true" />
                              {t("recurring")}
                            </Badge>
                          ) : null}
                          {entry.is_planned ? <Badge variant="neutral">{t("planned")}</Badge> : null}
                        </span>
                        {entry.merchant ? (
                          <span className="mt-0.5 block text-xs text-[var(--color-ink-muted)]">
                            {entry.merchant}
                          </span>
                        ) : null}
                      </td>
                      <td className="px-4 py-3 text-[var(--color-ink-secondary)]">
                        {entry.category_id ? (categoryNames.get(entry.category_id) ?? "–") : "–"}
                      </td>
                      <td className="px-4 py-3 tabular-nums text-[var(--color-ink-secondary)]">
                        {formatDate(entry.entry_date)}
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums font-medium text-[var(--color-ink)]">
                        {formatCurrency(entry.amount)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="inline-flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            aria-label={`${tCommon("edit")}: ${entry.label}`}
                            onClick={() => openEditDialog(entry)}
                          >
                            <Pencil className="h-4 w-4 text-[var(--color-ink-muted)]" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            aria-label={`${entry.label} löschen`}
                            onClick={() => deleteEntry.mutate(entry.id)}
                          >
                            <Trash2 className="h-4 w-4 text-[var(--color-ink-muted)]" />
                          </Button>
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog
        open={editingEntry !== null}
        onOpenChange={(open) => {
          if (!open) setEditingEntry(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("edit")}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditSubmit}>
            <EntryFormFields
              values={editFormValues}
              onChange={setEditFormValues}
              categories={categories.data ?? []}
              kind="expense"
              idPrefix="expense-edit"
            />
            {updateEntry.isError ? (
              <p role="alert" className="mt-3 text-sm text-[var(--color-critical)]">
                {tCommon("error")}
              </p>
            ) : null}
            <DialogFooter>
              <Button type="button" variant="secondary" onClick={() => setEditingEntry(null)}>
                {tCommon("cancel")}
              </Button>
              <Button type="submit" disabled={updateEntry.isPending}>
                {tCommon("save")}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default function ExpensesPage() {
  return (
    <Suspense fallback={null}>
      <ExpensesContent />
    </Suspense>
  );
}
