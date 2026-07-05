import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Wallet,
  Receipt,
  Tags,
  PiggyBank,
  Building2,
  Database,
  Settings,
  ShieldCheck,
} from "lucide-react";

export interface NavItem {
  href: string;
  labelKey: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/", labelKey: "overview", icon: LayoutDashboard },
  { href: "/income", labelKey: "income", icon: Wallet },
  { href: "/expenses", labelKey: "expenses", icon: Receipt },
  { href: "/categories", labelKey: "categories", icon: Tags },
  { href: "/budgets", labelKey: "budgets", icon: PiggyBank },
  { href: "/city-comparison", labelKey: "cityComparison", icon: Building2 },
  { href: "/data-sources", labelKey: "dataSources", icon: Database },
  { href: "/settings", labelKey: "settings", icon: Settings },
  { href: "/privacy", labelKey: "privacy", icon: ShieldCheck },
];
