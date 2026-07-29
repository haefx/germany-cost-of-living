"use client";

import { AlertTriangle, ChevronDown, Info, OctagonAlert } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState } from "react";

import type { Insight } from "@/lib/api-types";
import { formatCurrency } from "@/lib/format";
import { cn } from "@/lib/utils";

const SEVERITY_ICONS = {
  info: Info,
  warning: AlertTriangle,
  critical: OctagonAlert,
} as const;

const SEVERITY_STYLES = {
  info: "text-[var(--color-brand-dark)]",
  warning: "text-[#7a5200]",
  critical: "text-[var(--color-critical)]",
} as const;

export function InsightCard({ insight }: { insight: Insight }) {
  const t = useTranslations("insights");
  const [expanded, setExpanded] = useState(false);
  const severity = (insight.severity as keyof typeof SEVERITY_ICONS) ?? "info";
  const Icon = SEVERITY_ICONS[severity] ?? Info;

  const hasSavingsRange =
    insight.estimated_savings_max !== null && Number.parseFloat(insight.estimated_savings_max) > 0;

  return (
    <div className="rounded-xl border border-[var(--color-gridline)] bg-[#f9fbfe] p-3.5">
      <div className="flex items-start gap-3">
        <Icon
          className={cn("mt-0.5 h-4 w-4 shrink-0", SEVERITY_STYLES[severity])}
          aria-hidden="true"
        />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-[var(--color-ink)]">{insight.title}</p>
          <p className="mt-1 text-sm text-[var(--color-ink-secondary)]">{insight.explanation}</p>
          {hasSavingsRange ? (
            <p className="mt-2 text-xs font-medium text-[var(--color-good-text)]">
              {t("estimatedSavings")}:{" "}
              {insight.estimated_savings_min !== null &&
              insight.estimated_savings_min !== insight.estimated_savings_max
                ? `${formatCurrency(insight.estimated_savings_min)} – ${formatCurrency(insight.estimated_savings_max ?? 0)}`
                : formatCurrency(insight.estimated_savings_max ?? 0)}
            </p>
          ) : null}
          <button
            type="button"
            onClick={() => setExpanded((value) => !value)}
            aria-expanded={expanded}
            className="mt-2 flex items-center gap-1 text-xs font-medium text-[var(--color-brand)] hover:underline"
          >
            <ChevronDown
              className={cn("h-3 w-3 transition-transform", expanded && "rotate-180")}
              aria-hidden="true"
            />
            Details
          </button>
          {expanded ? (
            <dl className="mt-2 flex flex-col gap-2 border-t border-[var(--color-gridline)] pt-2 text-xs text-[var(--color-ink-secondary)]">
              <div>
                <dt className="font-medium text-[var(--color-ink)]">{t("suggestedAction")}</dt>
                <dd>{insight.suggested_action}</dd>
              </div>
              {insight.assumptions.length > 0 ? (
                <div>
                  <dt className="font-medium text-[var(--color-ink)]">{t("assumptions")}</dt>
                  <dd>
                    <ul className="list-disc pl-4">
                      {insight.assumptions.map((assumption, index) => (
                        <li key={index}>{assumption}</li>
                      ))}
                    </ul>
                  </dd>
                </div>
              ) : null}
              <div>
                <dt className="font-medium text-[var(--color-ink)]">{t("confidence")}</dt>
                <dd className="capitalize">{insight.confidence}</dd>
              </div>
              <p className="text-[var(--color-ink-muted)]">{insight.disclaimer}</p>
            </dl>
          ) : null}
        </div>
      </div>
    </div>
  );
}
