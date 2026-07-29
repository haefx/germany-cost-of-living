"use client";

import { Download, Save, Target, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { downloadAccountExport, useDeleteAccount } from "@/hooks/use-export";
import { useFinancialPreferences } from "@/hooks/use-financial-preferences";
import { useSession } from "@/hooks/use-session";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const { data: user } = useSession();
  const deleteAccount = useDeleteAccount();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const { savingsTargetMode, savingsTargetValue, setSavingsTarget } = useFinancialPreferences();
  const [targetMode, setTargetMode] = useState<"percent" | "amount" | null>(null);
  const [targetValue, setTargetValue] = useState<string | null>(null);
  const displayedTargetMode = targetMode ?? savingsTargetMode;
  const displayedTargetValue = targetValue ?? String(savingsTargetValue);

  async function handleDeleteAccount() {
    await deleteAccount.mutateAsync();
    // Hard navigation across the auth-state change (see login page).
    window.location.assign("/login");
  }

  return (
    <div className="flex max-w-2xl flex-col gap-4">
      <h1 className="text-lg font-semibold text-[var(--color-ink)]">{t("title")}</h1>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-4 w-4 text-[var(--color-secondary)]" />
            Finanzielle Ziele
          </CardTitle>
          <CardDescription>
            Lege deinen gewünschten monatlichen Sparbetrag oder eine Ziel-Sparquote fest. Das ist
            ein Sollwert und erzeugt keine Buchung.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-3">
          <div className="grid gap-2">
            <Label htmlFor="savings-target-mode">Ziel festlegen als</Label>
            <Select
              value={displayedTargetMode}
              onValueChange={(value) => setTargetMode(value as "percent" | "amount")}
            >
              <SelectTrigger id="savings-target-mode" className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="percent">Prozent der Einnahmen</SelectItem>
                <SelectItem value="amount">Fester Monatsbetrag</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="savings-target">
              {displayedTargetMode === "percent" ? "Ziel-Sparquote" : "Monatlicher Zielbetrag"}
            </Label>
            <div className="relative">
              <Input
                id="savings-target"
                className="w-48 pr-9"
                type="number"
                min="0"
                max={displayedTargetMode === "percent" ? "100" : undefined}
                step={displayedTargetMode === "percent" ? "1" : "0.01"}
                value={displayedTargetValue}
                onChange={(event) => setTargetValue(event.target.value)}
              />
              <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[var(--color-ink-muted)]">
                {displayedTargetMode === "percent" ? "%" : "€"}
              </span>
            </div>
          </div>
          <Button
            onClick={() => {
              setSavingsTarget(displayedTargetMode, Number(displayedTargetValue));
              setTargetValue(null);
              setTargetMode(null);
            }}
            disabled={
              !displayedTargetValue ||
              Number(displayedTargetValue) < 0 ||
              (displayedTargetMode === "percent" && Number(displayedTargetValue) > 100)
            }
          >
            <Save className="h-4 w-4" />
            Ziel speichern
          </Button>
          <p className="w-full text-xs text-[var(--color-ink-muted)]">
            Die Ist-Sparleistung umfasst nicht ausgegebenes Einkommen und Ausgaben der Kategorie „Sparen“. Das Ziel wird lokal in diesem Browser gespeichert.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("account")}</CardTitle>
          {user ? <CardDescription>{user.email}</CardDescription> : null}
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Button
            variant="secondary"
            className="w-fit"
            onClick={() => downloadAccountExport()}
          >
            <Download className="h-4 w-4" aria-hidden="true" />
            {t("exportAccount")}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("language")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-[var(--color-ink)]">{t("languageGerman")}</p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">{t("languageComingSoon")}</p>
        </CardContent>
      </Card>

      <Card className="border-[color-mix(in_srgb,var(--color-critical)_35%,white)]">
        <CardHeader>
          <CardTitle className="text-[var(--color-critical)]">{t("deleteAccount")}</CardTitle>
          <CardDescription>{t("deleteAccountWarning")}</CardDescription>
        </CardHeader>
        <CardContent>
          <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="destructive">
                <Trash2 className="h-4 w-4" aria-hidden="true" />
                {t("deleteAccount")}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t("deleteAccountConfirm")}</DialogTitle>
                <DialogDescription>{t("deleteAccountWarning")}</DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setDeleteDialogOpen(false)}
                >
                  {tCommon("cancel")}
                </Button>
                <Button
                  type="button"
                  variant="destructive"
                  onClick={handleDeleteAccount}
                  disabled={deleteAccount.isPending}
                >
                  {t("deleteAccountConfirm")}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    </div>
  );
}
