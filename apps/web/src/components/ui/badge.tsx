import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        neutral: "bg-[var(--color-page)] text-[var(--color-ink-secondary)]",
        good: "bg-[color-mix(in_srgb,var(--color-good)_14%,white)] text-[var(--color-good-text)]",
        warning: "bg-[color-mix(in_srgb,var(--color-warning)_20%,white)] text-[#7a5200]",
        critical: "bg-[color-mix(in_srgb,var(--color-critical)_14%,white)] text-[var(--color-critical)]",
        brand: "bg-[color-mix(in_srgb,var(--color-brand)_14%,white)] text-[var(--color-brand-dark)]",
      },
    },
    defaultVariants: {
      variant: "neutral",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
