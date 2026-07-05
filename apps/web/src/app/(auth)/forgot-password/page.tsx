"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useForgotPassword } from "@/hooks/use-auth";

export default function ForgotPasswordPage() {
  const t = useTranslations("auth");
  const forgotPassword = useForgotPassword();
  const [email, setEmail] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await forgotPassword.mutateAsync(email);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("forgotPasswordTitle")}</CardTitle>
        <CardDescription>{t("forgotPasswordSubtitle")}</CardDescription>
      </CardHeader>
      <CardContent>
        {forgotPassword.isSuccess ? (
          <p className="text-sm text-[var(--color-good-text)]">{t("forgotPasswordSent")}</p>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">{t("email")}</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>
            <Button type="submit" disabled={forgotPassword.isPending}>
              {t("forgotPasswordSubmit")}
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
