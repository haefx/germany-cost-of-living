"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

import { ChartShell } from "@/components/charts/chart-shell";
import {
  CityCostCompositionChart,
  CityDisposableIncomeChart,
  CityRentBurdenChart,
} from "@/components/charts/city-comparison-charts";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCityComparisons, usePlzLookup } from "@/hooks/use-cities";
import { formatCurrency } from "@/lib/format";

export default function CityComparisonPage() {
  const t = useTranslations("cityComparison");
  const cities = useCityComparisons();
  const [plz, setPlz] = useState("");
  const plzLookup = usePlzLookup(plz);

  const cityList = cities.data ?? [];
  const referenceYear = cityList[0]?.year;

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-lg font-semibold text-[var(--color-ink)]">{t("title")}</h1>
        <p className="text-sm text-[var(--color-ink-secondary)]">
          {t("subtitle")}
          {referenceYear ? ` Referenzjahr: ${referenceYear}.` : ""}
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-2 p-4 sm:flex-row sm:items-end sm:gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="plz-input">{t("plzLookup")}</Label>
            <Input
              id="plz-input"
              inputMode="numeric"
              pattern="\d{5}"
              maxLength={5}
              placeholder="z. B. 10115"
              className="w-40"
              value={plz}
              onChange={(event) => setPlz(event.target.value.replace(/\D/g, ""))}
            />
          </div>
          <div aria-live="polite" className="pb-2 text-sm">
            {plzLookup.data?.found ? (
              <span className="font-medium text-[var(--color-ink)]">
                {plzLookup.data.city}, {plzLookup.data.state}
              </span>
            ) : plzLookup.data && !plzLookup.data.found ? (
              <span className="text-[var(--color-ink-secondary)]">{t("plzNotFound")}</span>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <ChartShell
        title={t("disposableIncome")}
        description={t("referenceHousehold")}
        isLoading={cities.isLoading}
        isError={cities.isError}
        isEmpty={cityList.length === 0}
        textSummary={`Verfügbares Einkommen eines Referenzhaushalts in ${cityList.length} Städten. Höchster Wert: ${cityList[0]?.name ?? ""} mit ${formatCurrency(cityList[0]?.reference_disposable_income ?? 0)}.`}
      >
        <CityDisposableIncomeChart cities={cityList} />
      </ChartShell>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <ChartShell
          title={t("rentBurden")}
          description="Anteil der geschätzten Kaltmiete am geschätzten Nettoeinkommen. 30 % ist ein gebräuchlicher Orientierungswert, keine gesetzliche Schwelle."
          isLoading={cities.isLoading}
          isError={cities.isError}
          isEmpty={cityList.length === 0}
          textSummary="Mietbelastungsquote je Stadt mit einer 30-Prozent-Orientierungslinie."
        >
          <CityRentBurdenChart cities={cityList} />
        </ChartShell>
        <ChartShell
          title={t("costComposition")}
          isLoading={cities.isLoading}
          isError={cities.isError}
          isEmpty={cityList.length === 0}
          textSummary="Zusammensetzung der monatlichen Lebenshaltungskosten je Stadt aus Kaltmiete, Nebenkosten, Lebensmitteln und Mobilität."
        >
          <CityCostCompositionChart cities={cityList} />
        </ChartShell>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <caption className="sr-only">{t("title")}</caption>
              <thead>
                <tr className="border-b border-[var(--color-gridline)] text-left text-xs text-[var(--color-ink-muted)]">
                  <th scope="col" className="px-4 py-3 font-medium">Stadt</th>
                  <th scope="col" className="px-4 py-3 text-right font-medium">{t("medianGross")}</th>
                  <th scope="col" className="px-4 py-3 text-right font-medium">{t("estimatedRent")}</th>
                  <th scope="col" className="px-4 py-3 text-right font-medium">{t("rentBurden")}</th>
                  <th scope="col" className="px-4 py-3 text-right font-medium">{t("disposableIncome")}</th>
                </tr>
              </thead>
              <tbody>
                {cityList.map((city) => (
                  <tr key={city.city_id} className="border-b border-[var(--color-gridline)] last:border-0">
                    <th scope="row" className="px-4 py-3 text-left font-medium text-[var(--color-ink)]">
                      {city.name}
                      <span className="block text-xs font-normal text-[var(--color-ink-muted)]">
                        {city.state}
                      </span>
                    </th>
                    <td className="px-4 py-3 text-right tabular-nums">{formatCurrency(city.median_gross)}</td>
                    <td className="px-4 py-3 text-right tabular-nums">
                      {formatCurrency(city.estimated_monthly_rent)}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums">{city.rent_burden_pct} %</td>
                    <td className="px-4 py-3 text-right tabular-nums font-medium">
                      {formatCurrency(city.reference_disposable_income)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
