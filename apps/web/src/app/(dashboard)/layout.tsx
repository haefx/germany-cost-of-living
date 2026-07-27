"use client";

import { useEffect } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { useSession } from "@/hooks/use-session";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { data: user, isPending } = useSession();

  useEffect(() => {
    if (!isPending && !user) {
      // The API is the authority on session validity. A hard navigation also
      // clears any prefetched dashboard state after an expired/revoked cookie.
      // Treat query errors like an absent user so auth failures can never
      // leave the dashboard on an endless loading screen.
      window.location.replace("/login");
    }
  }, [isPending, user]);

  if (isPending || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-[var(--color-ink-secondary)]">
        Wird geladen …
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[var(--color-page)]">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
