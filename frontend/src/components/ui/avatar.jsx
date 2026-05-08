import React from "react";
import { cn } from "../../lib/utils-cn";

const Avatar = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn(
    "relative flex shrink-0 overflow-hidden",
    "rounded-[var(--radius-sm)]",
    className
  )} {...props} />
));
Avatar.displayName = "Avatar";

const AvatarFallback = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn(
    "flex h-full w-full items-center justify-center",
    "bg-[var(--color-primary)] text-white font-bold text-[11px]",
    "font-[var(--font-heading)]",
    className
  )} {...props} />
));
AvatarFallback.displayName = "AvatarFallback";

export { Avatar, AvatarFallback };
