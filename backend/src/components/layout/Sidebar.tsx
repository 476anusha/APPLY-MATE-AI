import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  Bot,
  KanbanSquare,
  Bookmark,
  MessageSquare,
  BarChart3,
  Settings,
  Sparkles,
  X,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

const navItems = [
  { name: 'Dashboard', to: '/app/dashboard', icon: LayoutDashboard },
  { name: 'Resume', to: '/app/resumes', icon: FileText },
  { name: 'Jobs', to: '/app/jobs', icon: Briefcase },
  { name: 'AI Agent', to: '/app/agent', icon: Bot, badge: 'AI' },
  { name: 'Tracker', to: '/app/tracker', icon: KanbanSquare },
  { name: 'Saved Jobs', to: '/app/saved', icon: Bookmark },
  { name: 'Interview Prep', to: '/app/interview', icon: MessageSquare },
  { name: 'Analytics', to: '/app/analytics', icon: BarChart3 },
  { name: 'Settings', to: '/app/settings', icon: Settings },
]

export function Sidebar({ isOpen = false, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
        />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-800/80 bg-slate-950/95 backdrop-blur-xl transition-transform duration-300 ease-in-out lg:static lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-6 border-b border-slate-800/60">
          <NavLink to="/app/dashboard" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 shadow-md shadow-purple-500/25">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-purple-200 bg-clip-text text-transparent">
                ApplyMate AI
              </span>
              <span className="text-[10px] font-medium text-slate-500 -mt-1 tracking-wider uppercase">
                Career Co-pilot
              </span>
            </div>
          </NavLink>

          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Navigation
          </div>
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'group flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-gradient-to-r from-purple-600/20 to-indigo-600/10 text-purple-300 border border-purple-500/20 shadow-sm'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <Icon
                        className={cn(
                          'h-4.5 w-4.5 transition-colors',
                          isActive ? 'text-purple-400' : 'text-slate-400 group-hover:text-slate-200'
                        )}
                      />
                      <span>{item.name}</span>
                    </div>
                    {item.badge && (
                      <Badge
                        variant="default"
                        className="bg-purple-500/20 text-purple-300 border-purple-500/30 text-[10px] px-1.5 py-0"
                      >
                        {item.badge}
                      </Badge>
                    )}
                  </>
                )}
              </NavLink>
            )
          })}
        </div>

        {/* Subscription Plan Card */}
        <div className="p-4 border-t border-slate-800/60">
          <div className="rounded-xl border border-purple-500/20 bg-gradient-to-br from-purple-900/30 via-slate-900/60 to-indigo-900/20 p-3.5 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-purple-300">Free Tier</span>
              <Badge variant="outline" className="border-purple-500/30 text-[10px] text-purple-400 px-1.5 py-0">
                Active
              </Badge>
            </div>
            <p className="text-[11px] text-slate-400 mb-2.5">
              5 AI analyses remaining this month.
            </p>
            <NavLink
              to="/app/settings?tab=subscription"
              className="block w-full text-center rounded-lg bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 py-1.5 text-xs font-medium transition-colors"
            >
              Upgrade to Pro
            </NavLink>
          </div>
        </div>
      </aside>
    </>
  )
}
