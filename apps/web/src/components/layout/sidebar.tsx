import { Home } from "lucide-react";
import Link from "next/link";

import { SidebarNav } from "./sidebar-nav";

export function Sidebar() {
  return (
    <aside className="hidden w-[244px] shrink-0 bg-[#062543] text-white shadow-[6px_0_24px_rgba(4,31,57,0.08)] md:flex md:flex-col">
      <Link href="/" className="flex h-20 items-center gap-3 px-6">
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[#10d0c7] to-[#00a8bf] text-white shadow-[0_8px_20px_rgba(4,199,194,0.25)]">
          <Home className="h-5 w-5" strokeWidth={2.2} aria-hidden="true" />
        </span>
        <span className="text-[15px] font-semibold tracking-[-0.01em] text-white">Haushaltsplaner</span>
      </Link>
      <div className="flex-1 overflow-y-auto px-3 py-3">
        <SidebarNav />
      </div>
    </aside>
  );
}
