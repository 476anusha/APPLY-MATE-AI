import { AlertTriangle, RotateCcw } from 'lucide-react'
import { Button } from './button'
import { cn } from '@/lib/utils'

export interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({
  title = 'Something went wrong',
  message = 'We encountered an error while loading this data. Please try again.',
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 text-center rounded-2xl border border-rose-500/20 bg-rose-500/5 backdrop-blur-sm min-h-[240px]',
        className
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-400 mb-3.5 ring-1 ring-rose-500/20">
        <AlertTriangle className="h-6 w-6" />
      </div>
      <h3 className="text-base font-semibold text-rose-100 mb-1">{title}</h3>
      <p className="text-xs text-rose-300/80 max-w-sm mb-4 leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <Button onClick={onRetry} size="sm" variant="outline" className="border-rose-500/30 hover:bg-rose-500/10 text-rose-200">
          <RotateCcw className="mr-2 h-3.5 w-3.5" />
          Retry
        </Button>
      )}
    </div>
  )
}
