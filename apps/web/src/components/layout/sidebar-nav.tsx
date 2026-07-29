"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

import { NAV_ITEMS } from "./nav-items";

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const t = useTranslations("nav");
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1" aria-label="Hauptnavigation">
      {NAV_ITEMS.map((item) => {
        const isActive = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            aria-current={isActive ? "page" : undefined}
            className={cn(
              "flex min-h-12 items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-all",
              isActive
                ? "bg-gradient-to-r from-[#1b5188] to-[#215d9b] text-white shadow-[0_5px_14px_rgba(0,0,0,0.14)]"
                : "text-[#d7e4f2] hover:bg-white/7 hover:text-white"
            )}
          >
            <Icon className="h-[19px] w-[19px] shrink-0" strokeWidth={1.8} aria-hidden="true" />
            {t(item.labelKey)}
          </Link>
        );
      })}
    </nav>
  );
}
