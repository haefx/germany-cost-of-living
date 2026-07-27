"use client";

import { useEffect } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { useSession } from "@/hooks/use-session";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { data: user, isLoading } = useSession();

  useEffect(() => {
    if (!isLoading && user === null) {
      // The API is the authority on session validity. A hard navigation also
      // clears any prefetched dashboard state after an expired/revoked cookie.
      window.location.replace("/login");
    }
  }, [isLoading, user]);

  if (isLoading || !user) {
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
