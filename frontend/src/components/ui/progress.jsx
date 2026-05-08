import React from "react";
import { cn } from "../../lib/utils-cn";

const Progress = React.forwardRef(({ className, value = 0, max = 100, variant = "default", ...props }, ref) => {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const barColors = {
    default: "bg-[var(--color-primary)]",
    gold: "bg-[var(--color-accent)]",
    success: "bg-[var(--color-success)]",
    warning: "bg-[var(--color-warning)]",
    danger: "bg-[var(--color-danger)]",
  };
  return (
    <div
      ref={ref}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemax={max}
      className={cn(
        "relative h-1.5 w-full overflow-hidden bg-[var(--color-surface-sunken)]",
        "rounded-[var(--radius-full)]",
        className
      )}
      {...props}
    >
      <div
        className={cn(
          "h-full transition-all duration-500 ease-out",
          "rounded-[var(--radius-full)]",
          barColors[variant] || barColors.default
        )}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
});
Progress.displayName = "Progress";

export { Progress };
