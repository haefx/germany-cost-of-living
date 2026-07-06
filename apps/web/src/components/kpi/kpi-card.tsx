import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string;
  delta?: string;
  deltaTone?: "good" | "critical" | "neutral";
  icon?: React.ReactNode;
}

export function KpiCard({ label, value, delta, deltaTone = "neutral", icon }: KpiCardProps) {
  return (
    <div className="rounded-lg border border-[var(--color-border)] bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-[var(--color-ink-secondary)]">{label}</span>
        {icon}
      </div>
      <p className="mt-2 text-2xl font-semibold tabular-nums text-[var(--color-ink)]">{value}</p>
      {delta ? (
        <p
          className={cn(
            "mt-1 text-xs font-medium",
            deltaTone === "good" && "text-[var(--color-good-text)]",
            deltaTone === "critical" && "text-[var(--color-critical)]",
            deltaTone === "neutral" && "text-[var(--color-ink-secondary)]"
          )}
        >
          {delta}
        </p>
      ) : null}
    </div>
  );
}
