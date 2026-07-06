"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CurrencyTooltip } from "./chart-tooltip";

export interface CategoryComparisonPoint {
  category: string;
  aktuell: number;
  vormonat: number;
}

export function CategoryComparisonChart({ data }: { data: CategoryComparisonPoint[] }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 0, right: 12, bottom: 0, left: 8 }}
          barCategoryGap="30%"
        >
          <CartesianGrid stroke="var(--color-gridline)" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fontSize: 12, fill: "var(--color-ink-muted)" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value: number) => `${Math.round(value)} €`}
          />
          <YAxis
            type="category"
            dataKey="category"
            width={110}
            tick={{ fontSize: 12, fill: "var(--color-ink-secondary)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CurrencyTooltip />} cursor={{ fill: "var(--color-page)" }} />
          <Legend
            wrapperStyle={{ fontSize: 12 }}
            formatter={(value: string) => (
              <span style={{ color: "var(--color-ink-secondary)" }}>{value}</span>
            )}
          />
          <Bar dataKey="aktuell" name="Diesen Monat" fill="var(--color-series-1)" radius={[0, 4, 4, 0]} />
          <Bar dataKey="vormonat" name="Vormonat" fill="var(--color-gridline)" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
