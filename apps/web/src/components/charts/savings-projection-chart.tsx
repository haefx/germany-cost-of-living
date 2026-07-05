"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CurrencyTooltip } from "./chart-tooltip";

export interface ProjectionPoint {
  jahr: string;
  eingezahlt: number;
}

/** Deposits-only projection (0% growth by default per the product's
 * financial-scenario rules): what accumulates if the chosen monthly amount
 * is simply set aside. All assumptions are rendered next to the chart by
 * the caller, not hidden here.
 */
export function SavingsProjectionChart({ data }: { data: ProjectionPoint[] }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="projection-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--color-series-5)" stopOpacity={0.25} />
              <stop offset="100%" stopColor="var(--color-series-5)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--color-gridline)" vertical={false} />
          <XAxis
            dataKey="jahr"
            tick={{ fontSize: 12, fill: "var(--color-ink-muted)" }}
            axisLine={{ stroke: "var(--color-gridline)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "var(--color-ink-muted)" }}
            axisLine={false}
            tickLine={false}
            width={80}
            tickFormatter={(value: number) => `${Math.round(value).toLocaleString("de-DE")} €`}
          />
          <Tooltip content={<CurrencyTooltip />} />
          <Area
            type="monotone"
            dataKey="eingezahlt"
            name="Eingezahlt"
            stroke="var(--color-series-5)"
            strokeWidth={2}
            fill="url(#projection-fill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
