import React from 'react'
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'
import { Card } from './card'
import { cn } from '@/lib/utils'

export interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  description?: string
  trend?: {
    value: number
    isPositive?: boolean
    label?: string
  }
  colorVariant?: 'purple' | 'blue' | 'emerald' | 'amber'
  className?: string
}

export function StatCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  colorVariant = 'purple',
  className,
}: StatCardProps) {
  const iconVariants = {
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  }

  return (
    <Card className={cn('relative overflow-hidden border-slate-800/80 bg-slate-900/60 p-5 hover:border-slate-700/80 transition-all duration-300', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400">{title}</p>
          <h3 className="mt-2 text-2xl font-bold tracking-tight text-white">{value}</h3>
          {description && (
            <p className="mt-1 text-xs text-slate-500">{description}</p>
          )}
          {trend && (
            <div className="mt-2.5 flex items-center gap-1.5 text-xs">
              <span
                className={cn(
                  'inline-flex items-center font-medium',
                  trend.isPositive !== false ? 'text-emerald-400' : 'text-rose-400'
                )}
              >
                {trend.isPositive !== false ? (
                  <TrendingUp className="mr-1 h-3.5 w-3.5" />
                ) : (
                  <TrendingDown className="mr-1 h-3.5 w-3.5" />
                )}
                {Math.abs(trend.value)}%
              </span>
              <span className="text-slate-500">{trend.label || 'vs last month'}</span>
            </div>
          )}
        </div>
        <div className={cn('flex h-11 w-11 items-center justify-center rounded-xl border', iconVariants[colorVariant])}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </Card>
  )
}
