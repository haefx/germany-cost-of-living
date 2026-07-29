"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CurrencyTooltip } from "./chart-tooltip";

export interface MonthlyTotalsPoint {
  month: string;
  einnahmen: number;
  ausgaben: number;
}

export function IncomeExpenseTrendChart({ data }: { data: MonthlyTotalsPoint[] }) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="var(--color-gridline)" vertical={false} />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 12, fill: "var(--color-ink-muted)" }}
            axisLine={{ stroke: "var(--color-gridline)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "var(--color-ink-muted)" }}
            axisLine={false}
            tickLine={false}
            width={70}
            tickFormatter={(value: number) => `${Math.round(value)} €`}
          />
          <Tooltip content={<CurrencyTooltip />} />
          <Legend
            iconType="plainline"
            wrapperStyle={{ fontSize: 12 }}
            formatter={(value: string) => (
              <span style={{ color: "var(--color-ink-secondary)" }}>{value}</span>
            )}
          />
          <Line
            type="monotone"
            dataKey="einnahmen"
            name="Einnahmen"
            stroke="var(--color-series-2)"
            strokeWidth={2.6}
            dot={{ r: 3, fill: "white", strokeWidth: 2 }}
          />
          <Line
            type="monotone"
            dataKey="ausgaben"
            name="Ausgaben"
            stroke="var(--color-series-6)"
            strokeWidth={2.6}
            dot={{ r: 3, fill: "white", strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
