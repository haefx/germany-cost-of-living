import { Home } from "lucide-react";
import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[var(--color-page)] px-4 py-12">
      <Link href="/" className="mb-8 flex items-center gap-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-md bg-[var(--color-brand)] text-white">
          <Home className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-base font-semibold text-[var(--color-ink)]">Haushaltsplaner</span>
      </Link>
      <div className="w-full max-w-sm">{children}</div>
    </div>
  );
}
