"use client";

import { LogOut, User as UserIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useLogout } from "@/hooks/use-auth";
import { useSession as useSessionQuery } from "@/hooks/use-session";

export function UserMenu() {
  const t = useTranslations("topbar");
  const router = useRouter();
  const { data: user } = useSessionQuery();
  const logout = useLogout();
  // Read the clock once per mount (not per render): render purity, and the
  // remaining-hours figure doesn't need to tick live.
  const [now] = useState(() => Date.now());

  async function handleLogout() {
    await logout.mutateAsync();
    router.push("/login");
  }

  if (!user) return null;

  const hoursRemaining = user.demo_expires_at
    ? Math.max(0, Math.round((new Date(user.demo_expires_at).getTime() - now) / 3_600_000))
    : null;

  return (
    <div className="flex items-center gap-2">
      {user.is_demo ? (
        <Badge variant="brand" className="hidden sm:inline-flex">
          {hoursRemaining !== null
            ? t("demoStatusWithTime", { hours: hoursRemaining })
            : t("demoStatus")}
        </Badge>
      ) : (
        <span className="hidden text-xs text-[var(--color-ink-secondary)] sm:inline">
          {t("accountStatus", { email: user.email })}
        </span>
      )}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" aria-label="Benutzermenü öffnen">
            <UserIcon className="h-5 w-5" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>{user.email}</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onSelect={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Abmelden
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
