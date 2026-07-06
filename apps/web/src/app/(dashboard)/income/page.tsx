"use client";

import { Plus, Repeat, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { Suspense, useState } from "react";

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
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useCategories } from "@/hooks/use-categories";
import {
  useCreateIncomeEntry,
  useDeleteIncomeEntry,
  useIncomeEntries,
} from "@/hooks/use-income";
import { formatCurrency, formatDate } from "@/lib/format";
import { sumAmounts } from "@/lib/finance-aggregation";

function IncomeContent() {
  const t = useTranslations("income");
  const tCommon = useTranslations("common");
  const { monthValue } = useSelectedMonth();

  const income = useIncomeEntries(monthValue);
  const categories = useCategories();
  const createEntry = useCreateIncomeEntry();
  const deleteEntry = useDeleteIncomeEntry();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [formValues, setFormValues] = useState<EntryFormValues>(emptyEntryFormValues);

  const categoryNames = new Map(
    (categories.data ?? []).map((category) => [category.id, category.name])
  );

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await createEntry.mutateAsync({ ...entryFormToPayload(formValues), source: "manual" });
    setDialogOpen(false);
    setFormValues(emptyEntryFormValues());
  }

  const entries = income.data ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-[var(--color-ink)]">{t("title")}</h1>
          <p className="text-sm text-[var(--color-ink-secondary)]">
            Summe: <span className="font-medium tabular-nums">{formatCurrency(sumAmounts(entries))}</span>
          </p>
        </div>
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
                kind="income"
                idPrefix="income"
              />
              {createEntry.isError ? (
                <p role="alert" className="mt-3 text-sm text-[var(--color-critical)]">
                  {tCommon("error")}
                </p>
              ) : null}
              <DialogFooter>
                <Button type="button" variant="secondary" onClick={() => setDialogOpen(false)}>
                  {tCommon("cancel")}
                </Button>
                <Button type="submit" disabled={createEntry.isPending}>
                  {tCommon("save")}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          {income.isLoading ? (
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
                        <span className="flex items-center gap-2">
                          {entry.label}
                          {entry.is_recurring ? (
                            <Badge variant="brand" className="gap-1">
                              <Repeat className="h-3 w-3" aria-hidden="true" />
                              {t("recurring")}
                            </Badge>
                          ) : null}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[var(--color-ink-secondary)]">
                        {entry.category_id ? (categoryNames.get(entry.category_id) ?? "–") : "–"}
                      </td>
                      <td className="px-4 py-3 tabular-nums text-[var(--color-ink-secondary)]">
                        {formatDate(entry.entry_date)}
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums font-medium text-[var(--color-good-text)]">
                        {formatCurrency(entry.amount)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`${entry.label} löschen`}
                          onClick={() => deleteEntry.mutate(entry.id)}
                        >
                          <Trash2 className="h-4 w-4 text-[var(--color-ink-muted)]" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function IncomePage() {
  return (
    <Suspense fallback={null}>
      <IncomeContent />
    </Suspense>
  );
}
