"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin, useRegister } from "@/hooks/use-auth";

export default function RegisterPage() {
  const t = useTranslations("auth");
  const register = useRegister();
  const login = useLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await register.mutateAsync({ email, password });
      await login.mutateAsync({ email, password });
      // Hard navigation: see login page for why router.push is not safe
      // across an auth-state change.
      window.location.assign("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("registerError"));
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("registerTitle")}</CardTitle>
        <CardDescription>{t("registerSubtitle")}</CardDescription>
      </CardHeader>
      <CardContent>
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
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="password">{t("password")}</Label>
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
          {error ? (
            <p role="alert" className="text-sm text-[var(--color-critical)]">
              {error}
            </p>
          ) : null}
          <Button type="submit" disabled={register.isPending || login.isPending}>
            {t("registerButton")}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-[var(--color-ink-secondary)]">
          {t("haveAccount")}{" "}
          <Link href="/login" className="text-[var(--color-brand)] hover:underline">
            {t("loginButton")}
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
