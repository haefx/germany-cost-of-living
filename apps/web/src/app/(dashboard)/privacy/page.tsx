"use client";

import { useTranslations } from "next-intl";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const SECTIONS = [
  { titleKey: "whatIsStored", textKey: "whatIsStoredText" },
  { titleKey: "whyStored", textKey: "whyStoredText" },
  { titleKey: "retention", textKey: "retentionText" },
  { titleKey: "automationTitle", textKey: "automationText" },
  { titleKey: "exportTitle", textKey: "exportText" },
] as const;

export default function PrivacyPage() {
  const t = useTranslations("privacy");

  return (
    <div className="flex max-w-2xl flex-col gap-4">
      <h1 className="text-lg font-semibold text-[var(--color-ink)]">{t("title")}</h1>
      {SECTIONS.map((section) => (
        <Card key={section.titleKey}>
          <CardHeader>
            <CardTitle>{t(section.titleKey)}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-[var(--color-ink-secondary)]">{t(section.textKey)}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
