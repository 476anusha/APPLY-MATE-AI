import { cn } from '@/lib/utils'

export interface ScoreRingProps {
  score: number
  size?: number
  strokeWidth?: number
  label?: string
  showLabel?: boolean
  className?: string
}

export function ScoreRing({
  score,
  size = 80,
  strokeWidth = 7,
  label,
  showLabel = true,
  className,
}: ScoreRingProps) {
  const clampedScore = Math.max(0, Math.min(100, Math.round(score || 0)))
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (clampedScore / 100) * circumference

  let colorClass = 'text-rose-500'
  let strokeBgClass = 'stroke-rose-950/40'
  if (clampedScore >= 70) {
    colorClass = 'text-emerald-500'
    strokeBgClass = 'stroke-emerald-950/40'
  } else if (clampedScore >= 40) {
    colorClass = 'text-amber-500'
    strokeBgClass = 'stroke-amber-950/40'
  }

  return (
    <div className={cn('relative inline-flex flex-col items-center justify-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className={cn('text-slate-800', strokeBgClass)}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={cn('transition-all duration-700 ease-out', colorClass)}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-sm font-bold text-white tracking-tight">{clampedScore}%</span>
      </div>
      {showLabel && label && (
        <span className="mt-2 text-xs font-medium text-slate-400">{label}</span>
      )}
    </div>
  )
}
