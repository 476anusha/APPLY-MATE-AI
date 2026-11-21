import { useToast } from "./use-toast"
import { Toast, ToastTitle, ToastDescription } from "./toast"

export function Toaster() {
  const { toasts, dismiss } = useToast()

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm pointer-events-none">
      {toasts.map(function ({ id, title, description, variant, action, ...props }) {
        return (
          <Toast key={id} variant={variant} onClose={() => dismiss(id)} {...props}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && (
                <ToastDescription>{description}</ToastDescription>
              )}
            </div>
            {action}
          </Toast>
        )
      })}
    </div>
  )
}
