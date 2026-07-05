"use client";

import { useTranslations } from "next-intl";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useDataSources } from "@/hooks/use-cities";
import { formatDate } from "@/lib/format";

export default function DataSourcesPage() {
  const t = useTranslations("dataSources");
  const tCommon = useTranslations("common");
  const sources = useDataSources();

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-lg font-semibold text-[var(--color-ink)]">{t("title")}</h1>
        <p className="text-sm text-[var(--color-ink-secondary)]">{t("subtitle")}</p>
      </div>

      {sources.isLoading ? (
        <p className="text-sm text-[var(--color-ink-muted)]">{tCommon("loading")}</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {(sources.data ?? []).map((source) => (
            <Card key={source.key}>
              <CardHeader className="flex-row items-start justify-between space-y-0">
                <div className="flex flex-col gap-1">
                  <CardTitle>{source.display_name}</CardTitle>
                  <CardDescription>
                    {source.is_live_integration ? t("liveIntegration") : t("referenceSnapshot")}
                  </CardDescription>
                </div>
                <Badge variant={source.is_stale ? "warning" : "good"}>
                  {source.is_stale ? t("stale") : t("current")}
                </Badge>
              </CardHeader>
              <CardContent>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                  <dt className="text-[var(--color-ink-muted)]">{t("lastPublished")}</dt>
                  <dd className="tabular-nums text-[var(--color-ink)]">
                    {source.last_published_at ? formatDate(source.last_published_at) : "–"}
                  </dd>
                  <dt className="text-[var(--color-ink-muted)]">{t("referenceYear")}</dt>
                  <dd className="tabular-nums text-[var(--color-ink)]">
                    {source.reference_year ?? "–"}
                  </dd>
                </dl>
                {source.license_note ? (
                  <div className="mt-3 border-t border-[var(--color-gridline)] pt-3">
                    <h3 className="text-xs font-medium text-[var(--color-ink-muted)]">
                      {t("license")}
                    </h3>
                    <p className="mt-1 text-xs text-[var(--color-ink-secondary)]">
                      {source.license_note}
                    </p>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
