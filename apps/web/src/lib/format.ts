const currencyFormatter = new Intl.NumberFormat("de-DE", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const percentFormatter = new Intl.NumberFormat("de-DE", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const dateFormatter = new Intl.DateTimeFormat("de-DE", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

const monthFormatter = new Intl.DateTimeFormat("de-DE", {
  month: "long",
  year: "numeric",
});

export function formatCurrency(value: number | string): string {
  const numeric = typeof value === "string" ? Number.parseFloat(value) : value;
  if (Number.isNaN(numeric)) return "–";
  return currencyFormatter.format(numeric);
}

export function formatPercent(value: number | string): string {
  const numeric = typeof value === "string" ? Number.parseFloat(value) : value;
  if (Number.isNaN(numeric)) return "–";
  return `${percentFormatter.format(numeric)} %`;
}

export function formatDate(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return dateFormatter.format(date);
}

export function formatMonth(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return monthFormatter.format(date);
}

export function monthParam(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  return `${year}-${month}-01`;
}
