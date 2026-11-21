import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { STATUS_COLORS } from './constants'
export { getInitials, formatDate, formatRelativeDate, formatSalary, formatFileSize, truncate, getScoreColor, greeting } from './formatters'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getStatusColor(status: string): string {
  return STATUS_COLORS[status] ?? 'bg-slate-500 text-white'
}

export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
