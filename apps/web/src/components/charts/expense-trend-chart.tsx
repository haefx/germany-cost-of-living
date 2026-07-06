"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CurrencyTooltip } from "./chart-tooltip";

export interface ExpenseTrendPoint {
  month: string;
  ausgaben: number;
}

export function ExpenseTrendChart({ data }: { data: ExpenseTrendPoint[] }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 0 }} barCategoryGap="25%">
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
          <Tooltip content={<CurrencyTooltip />} cursor={{ fill: "var(--color-page)" }} />
          <Bar
            dataKey="ausgaben"
            name="Ausgaben"
            fill="var(--color-series-1)"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
