"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { useSession } from "@/hooks/use-session";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { data: user, isLoading } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user === null) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

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
