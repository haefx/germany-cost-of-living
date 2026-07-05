"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useResetPassword } from "@/hooks/use-auth";

function ResetPasswordForm() {
  const t = useTranslations("auth");
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const resetPassword = useResetPassword();
  const [password, setPassword] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await resetPassword.mutateAsync({ token, password });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("resetPasswordTitle")}</CardTitle>
      </CardHeader>
      <CardContent>
        {resetPassword.isSuccess ? (
          <p className="text-sm text-[var(--color-good-text)]">{t("resetPasswordSuccess")}</p>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="password">{t("newPassword")}</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>
            {resetPassword.isError ? (
              <p role="alert" className="text-sm text-[var(--color-critical)]">
                {resetPassword.error instanceof Error ? resetPassword.error.message : t("registerError")}
              </p>
            ) : null}
            <Button type="submit" disabled={resetPassword.isPending || !token}>
              {t("resetPasswordSubmit")}
            </Button>
          </form>
        )}
        <p className="mt-4 text-center text-sm text-[var(--color-ink-secondary)]">
          <Link href="/login" className="text-[var(--color-brand)] hover:underline">
            {t("backToLogin")}
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordForm />
    </Suspense>
  );
}
