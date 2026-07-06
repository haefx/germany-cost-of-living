import { Suspense } from "react";

import { DataFreshnessBadge } from "./data-freshness-badge";
import { MobileNavDrawer } from "./mobile-nav-drawer";
import { MonthSelector } from "./month-selector";
import { TopbarSearch } from "./topbar-search";
import { UserMenu } from "./user-menu";

export function Topbar() {
  return (
    <header className="flex h-16 items-center gap-3 border-b border-[var(--color-border)] bg-white px-4 md:px-6">
      <MobileNavDrawer />
      <Suspense fallback={<div className="hidden max-w-sm flex-1 md:block" />}>
        <TopbarSearch />
      </Suspense>
      <div className="ml-auto flex items-center gap-3">
        <Suspense fallback={null}>
          <MonthSelector />
        </Suspense>
        <DataFreshnessBadge />
        <UserMenu />
      </div>
    </header>
  );
}
