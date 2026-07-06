"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { formatCurrency } from "@/lib/format";

import { CurrencyTooltip } from "./chart-tooltip";

export interface DonutSlice {
  id: string;
  name: string;
  value: number;
  color: string;
}

export function CategoryDonutChart({ slices, total }: { slices: DonutSlice[]; total: number }) {
  return (
    <div className="flex flex-col items-center gap-4 md:flex-row">
      <div className="relative h-64 w-full md:w-1/2">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={slices}
              dataKey="value"
              nameKey="name"
              innerRadius="62%"
              outerRadius="90%"
              paddingAngle={2}
              stroke="var(--color-surface)"
              strokeWidth={2}
            >
              {slices.map((slice) => (
                <Cell key={slice.id} fill={slice.color} />
              ))}
            </Pie>
            <Tooltip content={<CurrencyTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-semibold tabular-nums text-[var(--color-ink)]">
            {formatCurrency(total)}
          </span>
        </div>
      </div>
      <ul className="grid w-full grid-cols-1 gap-1.5 text-sm md:w-1/2">
        {slices.map((slice) => (
          <li key={slice.id} className="flex items-center justify-between gap-2">
            <span className="flex min-w-0 items-center gap-2">
              <span
                className="h-2.5 w-2.5 shrink-0 rounded-full"
                style={{ backgroundColor: slice.color }}
                aria-hidden="true"
              />
              <span className="truncate text-[var(--color-ink-secondary)]">{slice.name}</span>
            </span>
            <span className="tabular-nums text-[var(--color-ink)]">
              {formatCurrency(slice.value)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
