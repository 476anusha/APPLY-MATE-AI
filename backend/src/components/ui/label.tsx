import * as React from "react"
import { cn } from "@/lib/utils"

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, children, required, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn(
          "text-xs font-semibold text-slate-300 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-1",
          className
        )}
        {...props}
      >
        {children}
        {required && <span className="text-rose-400">*</span>}
      </label>
    )
  }
)
Label.displayName = "Label"

export { Label }
