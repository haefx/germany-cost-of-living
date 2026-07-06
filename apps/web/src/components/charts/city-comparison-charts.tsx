"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { CityComparison } from "@/lib/api-types";
import { formatPercent } from "@/lib/format";

import { CurrencyTooltip } from "./chart-tooltip";

export function CityDisposableIncomeChart({ cities }: { cities: CityComparison[] }) {
  const data = cities.map((city) => ({
    name: city.name,
    verfuegbar: Number.parseFloat(city.reference_disposable_income),
  }));

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 12, bottom: 0, left: 8 }}>
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
            dataKey="name"
            width={130}
            tick={{ fontSize: 12, fill: "var(--color-ink-secondary)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CurrencyTooltip />} cursor={{ fill: "var(--color-page)" }} />
          <Bar
            dataKey="verfuegbar"
            name="Verfügbares Einkommen"
            fill="var(--color-series-1)"
            radius={[0, 4, 4, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CityRentBurdenChart({ cities }: { cities: CityComparison[] }) {
  const data = [...cities]
    .sort((a, b) => Number.parseFloat(b.rent_burden_pct) - Number.parseFloat(a.rent_burden_pct))
    .map((city) => ({
      name: city.name,
      mietbelastung: Number.parseFloat(city.rent_burden_pct),
    }));

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 12, bottom: 0, left: 8 }}>
          <CartesianGrid stroke="var(--color-gridline)" horizontal={false} />
          <XAxis
            type="number"
            domain={[0, 60]}
            tick={{ fontSize: 12, fill: "var(--color-ink-muted)" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value: number) => `${value} %`}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={130}
            tick={{ fontSize: 12, fill: "var(--color-ink-secondary)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "var(--color-page)" }}
            content={({ active, label, payload }) =>
              active && payload && payload.length > 0 ? (
                <div className="rounded-md border border-[var(--color-border)] bg-white px-3 py-2 text-xs shadow-md">
                  <p className="font-medium">{label}</p>
                  <p className="text-[var(--color-ink-secondary)]">
                    Mietbelastung: {formatPercent(Number(payload[0]?.value ?? 0))}
                  </p>
                </div>
              ) : null
            }
          />
          <ReferenceLine
            x={30}
            stroke="var(--color-ink-muted)"
            strokeDasharray="4 4"
            label={{
              value: "30 %-Orientierung",
              position: "top",
              fontSize: 11,
              fill: "var(--color-ink-muted)",
            }}
          />
          <Bar
            dataKey="mietbelastung"
            name="Mietbelastung"
            fill="var(--color-series-5)"
            radius={[0, 4, 4, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CityCostCompositionChart({ cities }: { cities: CityComparison[] }) {
  const data = cities.map((city) => ({
    name: city.name,
    miete: Number.parseFloat(city.estimated_monthly_rent),
    nebenkosten: Number.parseFloat(city.utilities_month),
    lebensmittel: Number.parseFloat(city.groceries_month),
    mobilitaet: Number.parseFloat(city.transport_month),
  }));

  return (
    <div className="h-96">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 12, bottom: 40, left: 0 }}>
          <CartesianGrid stroke="var(--color-gridline)" vertical={false} />
          <XAxis
            dataKey="name"
            angle={-35}
            textAnchor="end"
            interval={0}
            tick={{ fontSize: 11, fill: "var(--color-ink-secondary)" }}
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
          <Legend
            wrapperStyle={{ fontSize: 12 }}
            formatter={(value: string) => (
              <span style={{ color: "var(--color-ink-secondary)" }}>{value}</span>
            )}
          />
          <Bar dataKey="miete" name="Kaltmiete" stackId="cost" fill="var(--color-series-1)" />
          <Bar dataKey="nebenkosten" name="Nebenkosten" stackId="cost" fill="var(--color-series-2)" />
          <Bar dataKey="lebensmittel" name="Lebensmittel" stackId="cost" fill="var(--color-series-3)" />
          <Bar
            dataKey="mobilitaet"
            name="Mobilität"
            stackId="cost"
            fill="var(--color-series-5)"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
