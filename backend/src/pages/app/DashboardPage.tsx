import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { Briefcase, Upload, Bot, TrendingUp, CalendarCheck, Gift, Bookmark, ArrowRight, Loader2, AlertCircle } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { analyticsService } from '@/services/analytics.service'
import { applicationService } from '@/services/application.service'
import { greeting, formatRelativeDate } from '@/utils/formatters'
import { getStatusColor } from '@/utils/helpers'

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: analyticsService.getDashboardStats,
  })

  const { data: applications, isLoading: appsLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationService.getApplications(),
  })

  const recentApps = applications?.slice(0, 5) ?? []

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          {greeting()}, {user?.full_name?.split(' ')[0] ?? 'there'} 👋
        </h1>
        <p className="text-slate-400 mt-1 text-sm">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statsLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-5 animate-pulse">
              <div className="h-4 bg-slate-700 rounded w-2/3 mb-3" />
              <div className="h-8 bg-slate-700 rounded w-1/3" />
            </div>
          ))
        ) : (
          <>
            <StatCard icon={<Briefcase className="w-5 h-5 text-purple-400" />} label="Total Applications" value={stats?.total_applications ?? 0} color="purple" />
            <StatCard icon={<CalendarCheck className="w-5 h-5 text-blue-400" />} label="Interviews" value={stats?.total_interviews ?? 0} color="blue" />
            <StatCard icon={<Gift className="w-5 h-5 text-green-400" />} label="Offers" value={stats?.total_offers ?? 0} color="green" />
            <StatCard icon={<Bookmark className="w-5 h-5 text-yellow-400" />} label="Saved Jobs" value={stats?.total_saved ?? 0} color="yellow" />
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-base font-semibold text-white mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <QuickAction icon={<Upload className="w-4 h-4" />} title="Upload Resume" desc="Add or update your resume" onClick={() => navigate('/app/resumes')} />
            <QuickAction icon={<Briefcase className="w-4 h-4" />} title="Search Jobs" desc="Discover matching opportunities" onClick={() => navigate('/app/jobs')} />
            <QuickAction icon={<Bot className="w-4 h-4" />} title="Open AI Agent" desc="Let AI handle the heavy lifting" onClick={() => navigate('/app/agent')} badge="AI" />
          </div>
        </div>

        {/* Recent Applications */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-white">Recent Applications</h2>
            <Link to="/app/tracker" className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          {appsLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-12 bg-slate-800 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : recentApps.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <Briefcase className="w-10 h-10 text-slate-600 mb-3" />
              <p className="text-slate-400 text-sm">No applications yet</p>
              <Link to="/app/jobs" className="mt-3 text-xs text-purple-400 hover:text-purple-300">
                Browse jobs to get started →
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {recentApps.map(app => (
                <div key={app.id} className="flex items-center justify-between py-2.5 px-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors">
                  <div>
                    <p className="text-sm font-medium text-white">{app.job_title}</p>
                    <p className="text-xs text-slate-400">{app.company} · {formatRelativeDate(app.created_at)}</p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getStatusColor(app.status)}`}>
                    {app.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* AI Insight Card */}
      <div className="bg-gradient-to-br from-purple-900/40 to-blue-900/30 border border-purple-800/30 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
            <Bot className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-sm font-semibold text-white">AI Career Insight</h3>
              <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full">AI</span>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              {stats?.total_applications
                ? `You've tracked ${stats.total_applications} application${stats.total_applications !== 1 ? 's' : ''}. ${stats.total_interviews > 0 ? `Your ${stats.total_interviews} interview${stats.total_interviews !== 1 ? 's' : ''} show${stats.total_interviews === 1 ? 's' : ''} a ${stats.conversion_rate}% conversion rate — great progress!` : 'Keep applying consistently to increase your interview chances.'} Use the AI Agent to tailor your resume and generate cover letters.`
                : 'Upload your resume and start tracking applications to get personalized AI insights. The AI Agent can help you find matching jobs, analyze your profile, and prepare for interviews.'}
            </p>
            <Link to="/app/agent" className="mt-3 inline-flex items-center gap-1 text-xs text-purple-400 hover:text-purple-300 font-medium">
              Open AI Agent <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-8 h-8 rounded-lg bg-${color}-500/10 flex items-center justify-center`}>{icon}</div>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-xs text-slate-400 mt-0.5">{label}</div>
    </div>
  )
}

function QuickAction({ icon, title, desc, onClick, badge }: { icon: React.ReactNode; title: string; desc: string; onClick: () => void; badge?: string }) {
  return (
    <button onClick={onClick} className="w-full flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors text-left group">
      <div className="w-8 h-8 bg-purple-500/10 rounded-lg flex items-center justify-center text-purple-400 group-hover:bg-purple-500/20 transition-colors">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white">{title}</span>
          {badge && <span className="text-xs bg-purple-500/20 text-purple-400 px-1.5 py-0.5 rounded">{badge}</span>}
        </div>
        <p className="text-xs text-slate-400 truncate">{desc}</p>
      </div>
      <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
    </button>
  )
}
