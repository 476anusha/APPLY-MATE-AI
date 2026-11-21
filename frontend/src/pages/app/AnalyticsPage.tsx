import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, Legend } from 'recharts'
import { TrendingUp, Briefcase, Bookmark, CalendarCheck, Gift, XCircle, Loader2, Bot } from 'lucide-react'
import { analyticsService } from '@/services/analytics.service'
import { formatDate } from '@/utils/formatters'

const STATUS_PIE_COLORS: Record<string, string> = {
  Interested: '#64748b', Saved: '#3b82f6', Applied: '#6366f1',
  Assessment: '#eab308', 'Interview Scheduled': '#a855f7',
  'Interview Completed': '#14b8a6', 'Offer Received': '#22c55e',
  Rejected: '#ef4444', Withdrawn: '#6b7280',
}

export default function AnalyticsPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({ queryKey: ['dashboard-stats'], queryFn: analyticsService.getDashboardStats })
  const { data: timeline, isLoading: timelineLoading } = useQuery({ queryKey: ['analytics-timeline'], queryFn: () => analyticsService.getApplicationTimeline(30) })
  const { data: skills } = useQuery({ queryKey: ['analytics-skills'], queryFn: analyticsService.getSkillsAnalytics })
  const { data: report, isLoading: reportLoading } = useQuery({ queryKey: ['weekly-report'], queryFn: analyticsService.getWeeklyReport })

  const statCards = [
    { label: 'Total Applications', value: stats?.total_applications ?? 0, icon: <Briefcase className="w-5 h-5 text-purple-400" />, color: 'purple' },
    { label: 'Saved Jobs', value: stats?.total_saved ?? 0, icon: <Bookmark className="w-5 h-5 text-blue-400" />, color: 'blue' },
    { label: 'Interviews', value: stats?.total_interviews ?? 0, icon: <CalendarCheck className="w-5 h-5 text-teal-400" />, color: 'teal' },
    { label: 'Offers Received', value: stats?.total_offers ?? 0, icon: <Gift className="w-5 h-5 text-green-400" />, color: 'green' },
    { label: 'Rejections', value: stats?.total_rejections ?? 0, icon: <XCircle className="w-5 h-5 text-red-400" />, color: 'red' },
    { label: 'Conversion Rate', value: `${stats?.conversion_rate ?? 0}%`, icon: <TrendingUp className="w-5 h-5 text-yellow-400" />, color: 'yellow' },
  ]

  // Build status pie from stats
  const statusPieData = stats ? [
    { name: 'Applied', value: stats.total_applications - stats.total_saved },
    { name: 'Interviews', value: stats.total_interviews },
    { name: 'Offers', value: stats.total_offers },
    { name: 'Rejected', value: stats.total_rejections },
  ].filter(d => d.value > 0) : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-slate-400 text-sm mt-1">Your job search performance at a glance</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {statsLoading ? Array.from({ length: 6 }).map((_, i) => <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-4 animate-pulse h-20" />) :
          statCards.map(c => (
            <div key={c.label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <div className="mb-2">{c.icon}</div>
              <div className="text-xl font-bold text-white">{c.value}</div>
              <div className="text-xs text-slate-400 mt-0.5 leading-tight">{c.label}</div>
            </div>
          ))
        }
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Applications over time */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">Applications Over Time (30 days)</h2>
          {timelineLoading ? <div className="h-48 animate-pulse bg-slate-800 rounded" /> : (
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={timeline ?? []} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={d => d.slice(5)} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} allowDecimals={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
                <Area type="monotone" dataKey="count" stroke="#8b5cf6" fill="url(#areaGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Status breakdown */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">Applications by Status</h2>
          {statusPieData.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-slate-500 text-sm">No application data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={statusPieData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                  {statusPieData.map((entry, i) => (
                    <Cell key={i} fill={STATUS_PIE_COLORS[entry.name] ?? '#6b7280'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
                <Legend iconType="circle" iconSize={8} formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 11 }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Skills in demand */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">Top Skills in Demand</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={skills ?? []} layout="vertical" margin={{ top: 0, right: 10, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} domain={[0, 100]} />
              <YAxis type="category" dataKey="skill" tick={{ fill: '#94a3b8', fontSize: 11 }} width={80} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }} />
              <Bar dataKey="demand" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* AI Weekly Report */}
        <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/20 border border-purple-800/30 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Bot className="w-4 h-4 text-purple-400" />
            <h2 className="text-sm font-semibold text-white">AI Weekly Report</h2>
            <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full">AI</span>
          </div>
          {reportLoading ? (
            <div className="space-y-2">
              {[1,2,3].map(i => <div key={i} className="h-3 bg-slate-700 rounded animate-pulse" />)}
            </div>
          ) : (
            <p className="text-sm text-slate-300 leading-relaxed">{report?.report ?? 'Start tracking applications to get your personalized weekly AI report.'}</p>
          )}
          {report && <p className="text-xs text-slate-500 mt-3">AI insights available above.</p>}
        </div>
      </div>
    </div>
  )
}
