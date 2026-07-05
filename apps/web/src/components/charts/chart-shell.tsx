"use client";

import { useTranslations } from "next-intl";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface ChartShellProps {
  title: string;
  description?: string;
  isLoading?: boolean;
  isError?: boolean;
  isEmpty?: boolean;
  /** Plain-language summary of what the chart shows, for screen readers. */
  textSummary: string;
  children: React.ReactNode;
  headerAction?: React.ReactNode;
}

export function ChartShell({
  title,
  description,
  isLoading,
  isError,
  isEmpty,
  textSummary,
  children,
  headerAction,
}: ChartShellProps) {
  const t = useTranslations("charts");

  let body: React.ReactNode;
  if (isLoading) {
    body = <ChartMessage role="status">{t("loading")}</ChartMessage>;
  } else if (isError) {
    body = <ChartMessage role="alert">{t("error")}</ChartMessage>;
  } else if (isEmpty) {
    body = <ChartMessage>{t("empty")}</ChartMessage>;
  } else {
    body = (
      <>
        <p className="sr-only">
          {t("screenReaderSummaryPrefix")} {textSummary}
        </p>
        <div aria-hidden="true">{children}</div>
      </>
    );
  }

  return (
    <Card>
      <CardHeader className="flex-row items-start justify-between space-y-0">
        <div className="flex flex-col gap-1">
          <CardTitle>{title}</CardTitle>
          {description ? <CardDescription>{description}</CardDescription> : null}
        </div>
        {headerAction}
      </CardHeader>
      <CardContent>{body}</CardContent>
    </Card>
  );
}

function ChartMessage({
  children,
  role,
}: {
  children: React.ReactNode;
  role?: "status" | "alert";
}) {
  return (
    <div
      role={role}
      className="flex h-64 items-center justify-center text-sm text-[var(--color-ink-muted)]"
    >
      {children}
    </div>
  );
}
