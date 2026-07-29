"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { formatMonth, monthParam } from "@/lib/format";

/** The selected month lives in the URL (?month=YYYY-MM-01), not client
 * state — shareable, and readable directly by server components.
 */
export function useSelectedMonth(): { month: Date; monthValue: string } {
  const searchParams = useSearchParams();
  const raw = searchParams.get("month");
  const isValidMonth = raw ? /^\d{4}-(0[1-9]|1[0-2])-01$/.test(raw) : false;
  const candidate = isValidMonth ? new Date(`${raw}T00:00:00`) : new Date();
  const month = Number.isNaN(candidate.getTime()) ? new Date() : candidate;
  return { month, monthValue: monthParam(month) };
}

export function MonthSelector() {
  const router = useRouter();
  const pathname = usePathname();
  const { month, monthValue } = useSelectedMonth();

  function navigateToMonth(offset: number) {
    const next = new Date(month.getFullYear(), month.getMonth() + offset, 1);
    const params = new URLSearchParams();
    params.set("month", monthParam(next));
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="flex items-center gap-1 rounded-md border border-[var(--color-border)] bg-white px-1">
      <Button
        variant="ghost"
        size="icon"
        aria-label="Vorheriger Monat"
        onClick={() => navigateToMonth(-1)}
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>
      <span className="min-w-[9rem] text-center text-sm font-medium capitalize" data-testid="month-label">
        {formatMonth(month)}
      </span>
      <Button variant="ghost" size="icon" aria-label="Nächster Monat" onClick={() => navigateToMonth(1)}>
        <ChevronRight className="h-4 w-4" />
      </Button>
      <span className="sr-only">{monthValue}</span>
    </div>
  );
}
