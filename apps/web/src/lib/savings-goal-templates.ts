export interface SavingsGoalTemplate {
  key: string;
  label: string;
  suggestedName: string;
  returnMin: number | null;
  returnMax: number | null;
  description: string;
}

export const SAVINGS_GOAL_TEMPLATES: SavingsGoalTemplate[] = [
  {
    key: "cash",
    label: "Klassisches Sparziel",
    suggestedName: "",
    returnMin: null,
    returnMax: null,
    description: "Ohne Renditeannahme – geeignet für Urlaub, Auto oder Notgroschen.",
  },
  {
    key: "overnight",
    label: "Tagesgeld / Geldmarkt",
    suggestedName: "Liquiditätsreserve",
    returnMin: 1,
    returnMax: 3,
    description: "Illustrative Spanne für risikoarme, liquide Rücklagen.",
  },
  {
    key: "balanced",
    label: "Ausgewogenes Portfolio",
    suggestedName: "Langfristiger Vermögensaufbau",
    returnMin: 3,
    returnMax: 5,
    description: "Illustrative langfristige Planungsannahme für ein gemischtes Portfolio.",
  },
  {
    key: "global-equity",
    label: "Globaler Aktienindex (z. B. MSCI World)",
    suggestedName: "Globaler Aktienindex",
    returnMin: 4,
    returnMax: 7,
    description: "Illustrative langfristige Spanne; zwischenzeitlich sind deutliche Verluste möglich.",
  },
];

export function findSavingsGoalTemplate(key: string) {
  return SAVINGS_GOAL_TEMPLATES.find((template) => template.key === key);
}
