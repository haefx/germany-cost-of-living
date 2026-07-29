export interface CompoundProjection {
  futureValue: number;
  contributed: number;
  hypotheticalGrowth: number;
}

export function compoundProjection(
  startingCapital: number,
  monthlyContribution: number,
  annualReturnPct: number,
  months: number
): CompoundProjection {
  const safeMonths = Math.max(0, Math.floor(months));
  const monthlyRate = Math.pow(1 + annualReturnPct / 100, 1 / 12) - 1;
  const contributed = startingCapital + monthlyContribution * safeMonths;
  const futureValue =
    monthlyRate === 0
      ? contributed
      : startingCapital * Math.pow(1 + monthlyRate, safeMonths) +
        monthlyContribution * ((Math.pow(1 + monthlyRate, safeMonths) - 1) / monthlyRate);

  return {
    futureValue,
    contributed,
    hypotheticalGrowth: Math.max(0, futureValue - contributed),
  };
}

export function monthsToReachTarget(
  startingCapital: number,
  monthlyContribution: number,
  annualReturnPct: number,
  targetAmount: number,
  maxMonths = 1200
): number | null {
  if (startingCapital >= targetAmount) return 0;
  if (monthlyContribution <= 0 && annualReturnPct <= 0) return null;

  for (let month = 1; month <= maxMonths; month += 1) {
    if (
      compoundProjection(startingCapital, monthlyContribution, annualReturnPct, month)
        .futureValue >= targetAmount
    ) {
      return month;
    }
  }
  return null;
}

export function addMonthsToToday(months: number): Date {
  const today = new Date();
  return new Date(today.getFullYear(), today.getMonth() + months, 1);
}
