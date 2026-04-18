import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default:
          "border border-slate-700 bg-slate-900 text-slate-50 hover:bg-slate-800",
        secondary:
          "border border-slate-700 bg-slate-800 text-slate-100 hover:bg-slate-700",
        destructive:
          "border border-red-700 bg-red-900/50 text-red-200 hover:bg-red-900/75",
        success:
          "border border-emerald-700 bg-emerald-900/50 text-emerald-200 hover:bg-emerald-900/75",
        warning:
          "border border-amber-700 bg-amber-900/50 text-amber-200 hover:bg-amber-900/75",
        info:
          "border border-blue-700 bg-blue-900/50 text-blue-200 hover:bg-blue-900/75",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }


