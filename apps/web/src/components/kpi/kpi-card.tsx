import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string;
  subtitle?: string;
  delta?: string;
  deltaTone?: "good" | "critical" | "neutral";
  tone?: "green" | "red" | "blue" | "purple";
  icon?: React.ReactNode;
}

export function KpiCard({
  label,
  value,
  subtitle,
  delta,
  deltaTone = "neutral",
  tone = "blue",
  icon,
}: KpiCardProps) {
  return (
    <div className={`kpi-card kpi-card--${tone}`}>
      <div className="kpi-card__accent" />
      <div className="kpi-card__icon">{icon}</div>
      <div className="min-w-0">
        <span className="text-sm font-medium text-[var(--color-ink-secondary)]">{label}</span>
        <p className="mt-1 text-[1.65rem] font-bold leading-tight tracking-[-0.025em] tabular-nums text-[var(--color-ink)]">{value}</p>
        {subtitle ? <p className="mt-1 text-xs text-[var(--color-ink-muted)]">{subtitle}</p> : null}
        {delta ? (
          <p className={cn(
            "mt-1 text-xs font-medium",
            deltaTone === "good" && "text-[var(--color-good-text)]",
            deltaTone === "critical" && "text-[var(--color-critical)]",
            deltaTone === "neutral" && "text-[var(--color-ink-secondary)]"
          )}>{delta}</p>
        ) : null}
      </div>
    </div>
  );
}
