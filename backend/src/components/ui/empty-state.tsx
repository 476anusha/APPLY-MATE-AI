import React from 'react'
import { LucideIcon, Inbox } from 'lucide-react'
import { Button } from './button'
import { cn } from '@/lib/utils'

export interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
  className?: string
  children?: React.ReactNode
}

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  actionLabel,
  onAction,
  className,
  children,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 backdrop-blur-sm min-h-[280px]',
        className
      )}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-500/10 text-purple-400 mb-4 ring-1 ring-purple-500/20">
        <Icon className="h-7 w-7" />
      </div>
      <h3 className="text-base font-semibold text-white mb-1.5">{title}</h3>
      {description && (
        <p className="text-xs text-slate-400 max-w-sm mb-5 leading-relaxed">
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm" variant="default">
          {actionLabel}
        </Button>
      )}
      {children}
    </div>
  )
}
