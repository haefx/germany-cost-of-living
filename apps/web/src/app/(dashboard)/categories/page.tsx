"use client";

import { Plus, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState } from "react";

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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  useCategories,
  useCreateCategory,
  useDeleteCategory,
} from "@/hooks/use-categories";
import type { CategoryKind } from "@/lib/api-types";

export default function CategoriesPage() {
  const t = useTranslations("categories");
  const tCommon = useTranslations("common");

  const categories = useCategories();
  const createCategory = useCreateCategory();
  const deleteCategory = useDeleteCategory();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [kind, setKind] = useState<CategoryKind>("expense");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    // Same default hue the backend would apply; custom color selection is
    // not part of this form yet.
    await createCategory.mutateAsync({ name, kind, color: "#3B82F6" });
    setDialogOpen(false);
    setName("");
  }

  const allCategories = categories.data ?? [];
  const expenseCategories = allCategories.filter((category) => category.kind === "expense");
  const incomeCategories = allCategories.filter((category) => category.kind === "income");

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-[var(--color-ink)]">{t("title")}</h1>
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
                <Label htmlFor="category-name">{tCommon("name")}</Label>
                <Input
                  id="category-name"
                  required
                  maxLength={100}
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="category-kind">{t("kind")}</Label>
                <Select value={kind} onValueChange={(value) => setKind(value as CategoryKind)}>
                  <SelectTrigger id="category-kind">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="expense">{t("expense")}</SelectItem>
                    <SelectItem value="income">{t("income")}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <DialogFooter>
                <Button type="button" variant="secondary" onClick={() => setDialogOpen(false)}>
                  {tCommon("cancel")}
                </Button>
                <Button type="submit" disabled={createCategory.isPending}>
                  {tCommon("save")}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CategoryList
          title={t("expense")}
          categories={expenseCategories}
          globalLabel={t("global")}
          customLabel={t("custom")}
          onDelete={(id) => deleteCategory.mutate(id)}
        />
        <CategoryList
          title={t("income")}
          categories={incomeCategories}
          globalLabel={t("global")}
          customLabel={t("custom")}
          onDelete={(id) => deleteCategory.mutate(id)}
        />
      </div>
    </div>
  );
}

function CategoryList({
  title,
  categories,
  globalLabel,
  customLabel,
  onDelete,
}: {
  title: string;
  categories: Array<{ id: string; name: string; color: string; user_id: string | null }>;
  globalLabel: string;
  customLabel: string;
  onDelete: (id: string) => void;
}) {
  return (
    <Card>
      <CardContent className="p-4">
        <h2 className="mb-3 text-sm font-semibold text-[var(--color-ink)]">{title}</h2>
        <ul className="flex flex-col gap-1">
          {categories.map((category) => (
            <li
              key={category.id}
              className="flex items-center justify-between rounded-md px-2 py-1.5 hover:bg-[var(--color-page)]"
            >
              <span className="flex items-center gap-2 text-sm text-[var(--color-ink)]">
                <span
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: category.color }}
                  aria-hidden="true"
                />
                {category.name}
                <Badge variant={category.user_id ? "brand" : "neutral"}>
                  {category.user_id ? customLabel : globalLabel}
                </Badge>
              </span>
              {category.user_id ? (
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`${category.name} löschen`}
                  onClick={() => onDelete(category.id)}
                >
                  <Trash2 className="h-4 w-4 text-[var(--color-ink-muted)]" />
                </Button>
              ) : null}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
