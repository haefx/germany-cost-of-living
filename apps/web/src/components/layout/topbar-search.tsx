"use client";

import { Search } from "lucide-react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useState } from "react";

/** Searches across income and expense labels/merchants/notes. Navigates to
 * the expenses page with the term in the URL (?q=...), which filters the
 * already-loaded list client-side — a real, working search over the data
 * that exists today, rather than a full-text backend search endpoint.
 */
export function TopbarSearch() {
  const t = useTranslations("topbar");
  const router = useRouter();
  const [value, setValue] = useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const params = new URLSearchParams();
    if (value.trim()) params.set("q", value.trim());
    router.push(`/expenses?${params.toString()}`);
  }

  return (
    <form onSubmit={handleSubmit} className="hidden max-w-sm flex-1 md:flex" role="search">
      <label htmlFor="topbar-search" className="sr-only">
        {t("searchPlaceholder")}
      </label>
      <div className="relative w-full">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-ink-muted)]"
          aria-hidden="true"
        />
        <input
          id="topbar-search"
          type="search"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder={t("searchPlaceholder")}
          className="h-9 w-full rounded-md border border-[var(--color-border)] bg-[var(--color-page)] pl-9 pr-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]"
        />
      </div>
    </form>
  );
}
