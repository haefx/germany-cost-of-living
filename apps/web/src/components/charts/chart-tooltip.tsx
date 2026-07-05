import { formatCurrency } from "@/lib/format";

interface TooltipEntry {
  name?: string | number;
  value?: number | string;
  color?: string;
}

interface ChartTooltipProps {
  active?: boolean;
  label?: string | number;
  payload?: TooltipEntry[];
}

/** Shared Recharts tooltip: white card, hairline border, currency formatting. */
export function CurrencyTooltip({ active, label, payload }: ChartTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="rounded-md border border-[var(--color-border)] bg-white px-3 py-2 text-xs shadow-md">
      {label !== undefined ? (
        <p className="mb-1 font-medium text-[var(--color-ink)]">{label}</p>
      ) : null}
      {payload.map((entry, index) => (
        <p key={index} className="flex items-center gap-2 text-[var(--color-ink-secondary)]">
          {entry.color ? (
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
          ) : null}
          {entry.name}: <span className="tabular-nums">{formatCurrency(entry.value ?? 0)}</span>
        </p>
      ))}
    </div>
  );
}
