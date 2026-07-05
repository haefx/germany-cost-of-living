"use client";

import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { useTranslations } from "next-intl";

import { Badge } from "@/components/ui/badge";
import { useDataSources } from "@/hooks/use-cities";

export function DataFreshnessBadge() {
  const t = useTranslations("topbar");
  const { data } = useDataSources();

  if (!data || data.length === 0) return null;

  const isStale = data.some((source) => source.is_stale);

  return (
    <Badge variant={isStale ? "warning" : "good"} className="hidden items-center gap-1 sm:inline-flex">
      {isStale ? (
        <AlertTriangle className="h-3 w-3" aria-hidden="true" />
      ) : (
        <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
      )}
      {isStale ? t("dataFreshnessStale") : t("dataFreshnessOk")}
    </Badge>
  );
}
