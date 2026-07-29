"use client";

import { useSyncExternalStore } from "react";

const STORAGE_KEY = "haushaltsplaner:financial-preferences";
const DEFAULT_TARGET_VALUE = 20;

export type SavingsTargetMode = "percent" | "amount";

function readSnapshot(): string {
  if (typeof window === "undefined") return `percent:${DEFAULT_TARGET_VALUE}`;

  try {
    const stored = JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? "{}");
    const mode: SavingsTargetMode = stored.savingsTargetMode === "amount" ? "amount" : "percent";
    const legacyRate = Number(stored.savingsTargetRate);
    const requestedValue = Number(stored.savingsTargetValue);
    const fallback = Number.isFinite(legacyRate) ? legacyRate : DEFAULT_TARGET_VALUE;
    const value = Number.isFinite(requestedValue) && requestedValue >= 0 ? requestedValue : fallback;
    return `${mode}:${mode === "percent" ? Math.min(100, value) : value}`;
  } catch {
    return `percent:${DEFAULT_TARGET_VALUE}`;
  }
}

function subscribe(onStoreChange: () => void) {
  window.addEventListener("storage", onStoreChange);
  window.addEventListener("financial-preferences-change", onStoreChange);
  return () => {
    window.removeEventListener("storage", onStoreChange);
    window.removeEventListener("financial-preferences-change", onStoreChange);
  };
}

export function useFinancialPreferences() {
  const snapshot = useSyncExternalStore(subscribe, readSnapshot, () => `percent:${DEFAULT_TARGET_VALUE}`);
  const [savingsTargetMode, rawValue] = snapshot.split(":") as [SavingsTargetMode, string];
  const savingsTargetValue = Number(rawValue);

  function setSavingsTarget(mode: SavingsTargetMode, value: number) {
    const nextValue = mode === "percent" ? Math.min(100, Math.max(0, value)) : Math.max(0, value);
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ savingsTargetMode: mode, savingsTargetValue: nextValue })
    );
    window.dispatchEvent(new Event("financial-preferences-change"));
  }

  return { savingsTargetMode, savingsTargetValue, setSavingsTarget };
}
