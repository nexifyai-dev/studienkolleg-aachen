import React from "react";
import { cva } from "class-variance-authority";
import { cn } from "../../lib/utils-cn";

const badgeVariants = cva(
  "inline-flex items-center gap-1 font-semibold transition-colors whitespace-nowrap",
  {
    variants: {
      variant: {
        default: "bg-[var(--color-primary)] text-white",
        gold: "bg-[var(--color-accent-muted)] text-[var(--color-accent)] border border-[var(--color-accent)]/20",
        success: "bg-[var(--color-success-bg)] text-[var(--color-success)] border border-[var(--color-success-border)]",
        warning: "bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]",
        danger: "bg-[var(--color-danger-bg)] text-[var(--color-danger)] border border-[var(--color-danger-border)]",
        info: "bg-[var(--color-info-bg)] text-[var(--color-info)] border border-[var(--color-info-border)]",
        outline: "border border-[var(--color-divider)] text-[var(--color-text-secondary)] bg-transparent",
        muted: "bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]",
      },
      size: {
        xs: "text-[9px] px-1.5 py-0.5 rounded-[var(--radius-xs)]",
        sm: "text-[10px] px-2 py-0.5 rounded-[var(--radius-xs)]",
        default: "text-[11px] px-2.5 py-1 rounded-[var(--radius-sm)]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

const Badge = React.forwardRef(({ className, variant, size, ...props }, ref) => (
  <span ref={ref} className={cn(badgeVariants({ variant, size }), className)} {...props} />
));
Badge.displayName = "Badge";

export { Badge, badgeVariants };
