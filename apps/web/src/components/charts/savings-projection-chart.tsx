"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CurrencyTooltip } from "./chart-tooltip";

export interface ProjectionPoint {
  jahr: string;
  eingezahlt: number;
  szenarioMin: number;
  szenarioMax: number;
}

export function SavingsProjectionChart({ data }: { data: ProjectionPoint[] }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="projection-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--color-series-5)" stopOpacity={0.18} />
              <stop offset="100%" stopColor="var(--color-series-5)" stopOpacity={0.015} />
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
          <Legend
            iconType="plainline"
            wrapperStyle={{ fontSize: 11 }}
            formatter={(value: string) => (
              <span style={{ color: "var(--color-ink-secondary)" }}>{value}</span>
            )}
          />
          <Area
            type="monotone"
            dataKey="szenarioMax"
            name="Szenario obere Spanne"
            stroke="var(--color-series-5)"
            strokeWidth={2}
            fill="url(#projection-fill)"
          />
          <Line
            type="monotone"
            dataKey="szenarioMin"
            name="Szenario untere Spanne"
            stroke="var(--color-series-1)"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="eingezahlt"
            name="Eigene Einzahlungen"
            stroke="var(--color-ink-muted)"
            strokeWidth={1.7}
            strokeDasharray="5 5"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
