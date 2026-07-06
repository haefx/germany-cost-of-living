/**
 * Fixed-order categorical palette (validated for CVD-safe adjacent contrast).
 * Hues are assigned by a stable sort key (category id), never by rank or
 * filtered position, so a category keeps its color across charts and after
 * other categories are filtered out.
 */
export const CATEGORICAL_PALETTE = [
  "var(--color-series-1)",
  "var(--color-series-2)",
  "var(--color-series-3)",
  "var(--color-series-4)",
  "var(--color-series-5)",
  "var(--color-series-6)",
  "var(--color-series-7)",
  "var(--color-series-8)",
] as const;

export const MAX_DISTINCT_SERIES = CATEGORICAL_PALETTE.length;

export const STATUS_COLORS = {
  good: "var(--color-good)",
  warning: "var(--color-warning)",
  serious: "var(--color-serious)",
  critical: "var(--color-critical)",
} as const;

/** Assigns a stable color per id, in the order ids are first seen. Beyond
 * the 8 validated slots, later entries should be folded into "Andere"
 * rather than requesting a 9th generated hue.
 */
export function assignSeriesColors<T extends string>(ids: T[]): Map<T, string> {
  const colorById = new Map<T, string>();
  const sorted = [...ids].sort();
  sorted.forEach((id, index) => {
    colorById.set(id, CATEGORICAL_PALETTE[index % CATEGORICAL_PALETTE.length] as string);
  });
  return colorById;
}
