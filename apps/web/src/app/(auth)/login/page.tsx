"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin, useStartDemo } from "@/hooks/use-auth";

export default function LoginPage() {
  const t = useTranslations("auth");
  const router = useRouter();
  const login = useLogin();
  const startDemo = useStartDemo();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    try {
      await login.mutateAsync({ email, password });
      router.push("/");
    } catch {
      // error is surfaced via login.error below
    }
  }

  async function handleDemo() {
    await startDemo.mutateAsync();
    router.push("/");
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("loginTitle")}</CardTitle>
        <CardDescription>{t("loginSubtitle")}</CardDescription>
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
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>
          {login.isError ? (
            <p role="alert" className="text-sm text-[var(--color-critical)]">
              {login.error instanceof Error ? login.error.message : t("loginError")}
            </p>
          ) : null}
          <Button type="submit" disabled={login.isPending}>
            {t("loginButton")}
          </Button>
        </form>
        <div className="mt-3 text-right text-sm">
          <Link href="/forgot-password" className="text-[var(--color-brand)] hover:underline">
            {t("forgotPassword")}
          </Link>
        </div>
        <div className="mt-6 border-t border-[var(--color-border)] pt-4">
          <Button
            type="button"
            variant="secondary"
            className="w-full"
            onClick={handleDemo}
            disabled={startDemo.isPending}
          >
            {t("tryDemo")}
          </Button>
        </div>
        <p className="mt-4 text-center text-sm text-[var(--color-ink-secondary)]">
          {t("noAccount")}{" "}
          <Link href="/register" className="text-[var(--color-brand)] hover:underline">
            {t("registerButton")}
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
