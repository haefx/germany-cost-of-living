import { Home } from "lucide-react";
import Link from "next/link";

import { SidebarNav } from "./sidebar-nav";

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-[var(--color-border)] bg-white md:flex md:flex-col">
      <Link href="/" className="flex items-center gap-2 px-5 py-5">
        <span className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--color-brand)] text-white">
          <Home className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-semibold text-[var(--color-ink)]">Haushaltsplaner</span>
      </Link>
      <div className="flex-1 overflow-y-auto px-3">
        <SidebarNav />
      </div>
    </aside>
  );
}
