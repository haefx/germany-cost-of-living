"use client";

import { Download, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
import { useSession } from "@/hooks/use-session";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const { data: user } = useSession();
  const deleteAccount = useDeleteAccount();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

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
