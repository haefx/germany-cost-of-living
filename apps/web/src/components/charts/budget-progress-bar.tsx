import { AlertTriangle } from "lucide-react";

import type { BudgetStatus } from "@/lib/api-types";
import { formatCurrency } from "@/lib/format";
import { cn } from "@/lib/utils";

/** A plain styled progress bar — deliberately not a charting-library
 * component. Over-budget state is communicated by icon + text, never by
 * color alone.
 */
export function BudgetProgressBar({ status }: { status: BudgetStatus }) {
  const limit = Number.parseFloat(status.budget.monthly_limit);
  const spent = Number.parseFloat(status.actual_spent);
  const ratio = limit > 0 ? Math.min(1, spent / limit) : 0;

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="flex items-center gap-1.5 font-medium text-[var(--color-ink)]">
          {status.is_over_budget ? (
            <AlertTriangle className="h-3.5 w-3.5 text-[var(--color-critical)]" aria-hidden="true" />
          ) : null}
          {status.category_name}
        </span>
        <span className="tabular-nums text-[var(--color-ink-secondary)]">
          {formatCurrency(status.actual_spent)} / {formatCurrency(status.budget.monthly_limit)}
        </span>
      </div>
      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={limit}
        aria-valuenow={spent}
        aria-label={`Budget ${status.category_name}`}
        className="h-2 overflow-hidden rounded-full bg-[var(--color-gridline)]"
      >
        <div
          className={cn(
            "h-full rounded-full",
            status.is_over_budget ? "bg-[var(--color-critical)]" : "bg-[var(--color-brand)]"
          )}
          style={{ width: `${ratio * 100}%` }}
        />
      </div>
      <p
        className={cn(
          "mt-1 text-xs",
          status.is_over_budget
            ? "font-medium text-[var(--color-critical)]"
            : "text-[var(--color-ink-muted)]"
        )}
      >
        {status.is_over_budget
          ? `Budget überschritten um ${formatCurrency(Math.abs(Number.parseFloat(status.remaining)))}`
          : `Verbleibend: ${formatCurrency(status.remaining)}`}
      </p>
    </div>
  );
}
