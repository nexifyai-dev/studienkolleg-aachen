import React from "react";
import { cn } from "../../lib/utils-cn";

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn(
    "bg-[var(--color-surface)] border border-[var(--color-divider)] overflow-hidden",
    "rounded-[var(--radius-md)]",
    "shadow-[var(--shadow-card)]",
    className
  )} {...props} />
));
Card.displayName = "Card";

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn(
    "flex flex-col gap-1 px-5 pt-5 pb-3",
    className
  )} {...props} />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3 ref={ref} className={cn(
    "text-sm font-bold text-[var(--color-text-primary)] leading-tight tracking-tight",
    "font-[var(--font-heading)]",
    className
  )} {...props} />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p ref={ref} className={cn(
    "text-xs text-[var(--color-text-secondary)] leading-relaxed",
    className
  )} {...props} />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("px-5 pb-5", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn(
    "flex items-center px-5 py-3 border-t border-[var(--color-divider-subtle)]",
    className
  )} {...props} />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };
