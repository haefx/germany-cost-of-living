"use client";

import { useTranslations } from "next-intl";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import type { Category, CategoryKind, RecurrenceRuleCreate } from "@/lib/api-types";

export interface EntryFormValues {
  label: string;
  amount: string;
  entryDate: string;
  categoryId: string | null;
  isRecurring: boolean;
  frequency: RecurrenceRuleCreate["frequency"];
}

export const NO_CATEGORY = "none";

interface EntryFormFieldsProps {
  values: EntryFormValues;
  onChange: (values: EntryFormValues) => void;
  categories: Category[];
  kind: CategoryKind;
  idPrefix: string;
}

export function EntryFormFields({
  values,
  onChange,
  categories,
  kind,
  idPrefix,
}: EntryFormFieldsProps) {
  const t = useTranslations("common");
  const tIncome = useTranslations("income");

  const selectableCategories = categories.filter(
    (category) => category.kind === kind && !category.is_archived
  );

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor={`${idPrefix}-label`}>{tIncome("label")}</Label>
        <Input
          id={`${idPrefix}-label`}
          required
          maxLength={200}
          value={values.label}
          onChange={(event) => onChange({ ...values, label: event.target.value })}
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`${idPrefix}-amount`}>{t("amount")} (€)</Label>
          <Input
            id={`${idPrefix}-amount`}
            type="number"
            inputMode="decimal"
            min="0.01"
            step="0.01"
            required
            value={values.amount}
            onChange={(event) => onChange({ ...values, amount: event.target.value })}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`${idPrefix}-date`}>{t("date")}</Label>
          <Input
            id={`${idPrefix}-date`}
            type="date"
            required
            value={values.entryDate}
            onChange={(event) => onChange({ ...values, entryDate: event.target.value })}
          />
        </div>
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor={`${idPrefix}-category`}>{t("category")}</Label>
        <Select
          value={values.categoryId ?? NO_CATEGORY}
          onValueChange={(value) =>
            onChange({ ...values, categoryId: value === NO_CATEGORY ? null : value })
          }
        >
          <SelectTrigger id={`${idPrefix}-category`}>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={NO_CATEGORY}>Ohne Kategorie</SelectItem>
            {selectableCategories.map((category) => (
              <SelectItem key={category.id} value={category.id}>
                {category.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center justify-between rounded-md border border-[var(--color-border)] px-3 py-2.5">
        <Label htmlFor={`${idPrefix}-recurring`} className="cursor-pointer">
          {tIncome("recurring")}
        </Label>
        <Switch
          id={`${idPrefix}-recurring`}
          checked={values.isRecurring}
          onCheckedChange={(checked) => onChange({ ...values, isRecurring: checked })}
        />
      </div>
      {values.isRecurring ? (
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`${idPrefix}-frequency`}>Intervall</Label>
          <Select
            value={values.frequency}
            onValueChange={(value) =>
              onChange({ ...values, frequency: value as EntryFormValues["frequency"] })
            }
          >
            <SelectTrigger id={`${idPrefix}-frequency`}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="weekly">Wöchentlich</SelectItem>
              <SelectItem value="monthly">Monatlich</SelectItem>
              <SelectItem value="yearly">Jährlich</SelectItem>
            </SelectContent>
          </Select>
        </div>
      ) : null}
    </div>
  );
}

export function emptyEntryFormValues(): EntryFormValues {
  const today = new Date().toISOString().slice(0, 10);
  return {
    label: "",
    amount: "",
    entryDate: today,
    categoryId: null,
    isRecurring: false,
    frequency: "monthly",
  };
}

export function entryFormToPayload(values: EntryFormValues) {
  return {
    label: values.label,
    amount: values.amount,
    entry_date: values.entryDate,
    category_id: values.categoryId,
    is_recurring: values.isRecurring,
    recurrence: values.isRecurring
      ? {
          frequency: values.frequency,
          interval_count: 1,
          start_date: values.entryDate,
        }
      : null,
  };
}
