import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Loader2, Briefcase, Trash2, Edit3, LayoutList, Columns } from 'lucide-react'
import { applicationService } from '@/services/application.service'
import { APPLICATION_STATUSES, STATUS_COLORS } from '@/utils/constants'
import { formatRelativeDate } from '@/utils/formatters'
import { getStatusColor } from '@/utils/helpers'
import type { Application, ApplicationStatus } from '@/types'

// Demo applications shown when backend has no data yet
const DEMO_APPLICATIONS: Application[] = [
  { id: 'demo-1', user_id: 'usr', company: 'Google', job_title: 'Software Engineer III', status: 'Interview Scheduled', job_url: '#', applied_date: new Date(Date.now() - 5 * 86400000).toISOString(), created_at: new Date(Date.now() - 5 * 86400000).toISOString() },
  { id: 'demo-2', user_id: 'usr', company: 'Microsoft', job_title: 'Full Stack Developer', status: 'Applied', job_url: '#', applied_date: new Date(Date.now() - 3 * 86400000).toISOString(), created_at: new Date(Date.now() - 3 * 86400000).toISOString() },
  { id: 'demo-3', user_id: 'usr', company: 'Razorpay', job_title: 'Backend Engineer', status: 'Applied', job_url: '#', applied_date: new Date(Date.now() - 7 * 86400000).toISOString(), created_at: new Date(Date.now() - 7 * 86400000).toISOString() },
  { id: 'demo-4', user_id: 'usr', company: 'Swiggy', job_title: 'React Developer', status: 'Assessment', job_url: '#', applied_date: new Date(Date.now() - 2 * 86400000).toISOString(), created_at: new Date(Date.now() - 2 * 86400000).toISOString() },
  { id: 'demo-5', user_id: 'usr', company: 'Zomato', job_title: 'SDE-2 Backend', status: 'Interested', job_url: '#', created_at: new Date().toISOString() },
  { id: 'demo-6', user_id: 'usr', company: 'Atlassian', job_title: 'Platform Engineer', status: 'Offer Received', job_url: '#', applied_date: new Date(Date.now() - 14 * 86400000).toISOString(), created_at: new Date(Date.now() - 14 * 86400000).toISOString() },
  { id: 'demo-7', user_id: 'usr', company: 'Paytm', job_title: 'DevOps Engineer', status: 'Rejected', job_url: '#', applied_date: new Date(Date.now() - 10 * 86400000).toISOString(), created_at: new Date(Date.now() - 10 * 86400000).toISOString() },
]

function buildDemoKanban(): Record<string, Application[]> {
  const kanban: Record<string, Application[]> = {}
  APPLICATION_STATUSES.forEach(s => { kanban[s] = [] })
  DEMO_APPLICATIONS.forEach(a => { if (kanban[a.status]) kanban[a.status].push(a) })
  return kanban
}

export default function TrackerPage() {
  const qc = useQueryClient()
  const [view, setView] = useState<'kanban' | 'table'>('kanban')
  const [showAdd, setShowAdd] = useState(false)
  const [editApp, setEditApp] = useState<Application | null>(null)

  const { data: kanbanRaw, isLoading } = useQuery({
    queryKey: ['applications-kanban'],
    queryFn: applicationService.getKanbanBoard,
  })

  const { data: applicationsRaw } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationService.getApplications(),
  })

  // Use demo data when backend returns empty board
  const totalReal = Object.values(kanbanRaw ?? {}).flat().length
  const kanban = totalReal > 0 ? kanbanRaw! : buildDemoKanban()
  const applications = (applicationsRaw && applicationsRaw.length > 0) ? applicationsRaw : DEMO_APPLICATIONS

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      applicationService.updateStatus(id, status as ApplicationStatus),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications-kanban'] })
      qc.invalidateQueries({ queryKey: ['applications'] })
      qc.invalidateQueries({ queryKey: ['dashboard-stats'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => applicationService.deleteApplication(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications-kanban'] })
      qc.invalidateQueries({ queryKey: ['applications'] })
    },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Application Tracker</h1>
          <p className="text-slate-400 text-sm mt-1">Track every job application in one place</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex bg-slate-800 border border-slate-700 rounded-lg p-1">
            <button onClick={() => setView('kanban')} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${view === 'kanban' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}>
              <Columns className="w-3.5 h-3.5" /> Kanban
            </button>
            <button onClick={() => setView('table')} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${view === 'table' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}>
              <LayoutList className="w-3.5 h-3.5" /> Table
            </button>
          </div>
          <button onClick={() => setShowAdd(true)} className="flex items-center gap-1.5 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-lg transition-colors">
            <Plus className="w-4 h-4" /> Add Application
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 text-purple-400 animate-spin" /></div>
      ) : view === 'kanban' ? (
        <KanbanView kanban={kanban ?? {}} onStatusChange={(id, status) => statusMutation.mutate({ id, status })} onDelete={(id) => deleteMutation.mutate(id)} />
      ) : (
        <TableView applications={applications ?? []} onStatusChange={(id, status) => statusMutation.mutate({ id, status })} onDelete={(id) => deleteMutation.mutate(id)} />
      )}

      {showAdd && <AddApplicationModal onClose={() => setShowAdd(false)} onSuccess={() => { setShowAdd(false); qc.invalidateQueries({ queryKey: ['applications-kanban'] }); qc.invalidateQueries({ queryKey: ['applications'] }) }} />}
    </div>
  )
}

function KanbanView({ kanban, onStatusChange, onDelete }: { kanban: Record<string, Application[]>; onStatusChange: (id: string, status: string) => void; onDelete: (id: string) => void }) {
  const statuses = APPLICATION_STATUSES
  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {statuses.map(status => {
        const apps = kanban[status] ?? []
        return (
          <div key={status} className="flex-shrink-0 w-64">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${STATUS_COLORS[status]?.split(' ')[0] ?? 'bg-slate-500'}`} />
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wide">{status}</span>
              </div>
              <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">{apps.length}</span>
            </div>
            <div className="space-y-2 min-h-32">
              {apps.map(app => (
                <KanbanCard key={app.id} app={app} onStatusChange={onStatusChange} onDelete={onDelete} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function KanbanCard({ app, onStatusChange, onDelete }: { app: Application; onStatusChange: (id: string, s: string) => void; onDelete: (id: string) => void }) {
  return (
    <div className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-lg p-3 group transition-colors">
      <p className="text-sm font-medium text-white leading-tight">{app.job_title}</p>
      <p className="text-xs text-slate-400 mt-0.5">{app.company}</p>
      {app.applied_date && <p className="text-xs text-slate-500 mt-1">Applied {formatRelativeDate(app.applied_date)}</p>}
      <div className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <select
          value={app.status}
          onChange={e => onStatusChange(app.id, e.target.value)}
          className="text-xs bg-slate-800 border border-slate-700 text-slate-300 rounded px-1.5 py-1 flex-1"
        >
          {APPLICATION_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <button onClick={() => onDelete(app.id)} className="p-1 text-slate-500 hover:text-red-400 transition-colors">
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}

function TableView({ applications, onStatusChange, onDelete }: { applications: Application[]; onStatusChange: (id: string, status: string) => void; onDelete: (id: string) => void }) {
  if (applications.length === 0) return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl flex flex-col items-center justify-center py-16">
      <Briefcase className="w-12 h-12 text-slate-600 mb-3" />
      <p className="text-slate-400">No applications yet. Add your first one!</p>
    </div>
  )
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-800">
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">Company</th>
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">Position</th>
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">Status</th>
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wide hidden md:table-cell">Applied</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {applications.map(app => (
            <tr key={app.id} className="hover:bg-slate-800/40 transition-colors">
              <td className="px-4 py-3 font-medium text-white">{app.company}</td>
              <td className="px-4 py-3 text-slate-300">{app.job_title}</td>
              <td className="px-4 py-3">
                <select
                  value={app.status}
                  onChange={e => onStatusChange(app.id, e.target.value)}
                  className="text-xs bg-slate-800 border border-slate-700 text-slate-300 rounded px-2 py-1"
                >
                  {APPLICATION_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </td>
              <td className="px-4 py-3 text-slate-400 text-xs hidden md:table-cell">
                {app.applied_date ? formatRelativeDate(app.applied_date) : '—'}
              </td>
              <td className="px-4 py-3">
                <button onClick={() => onDelete(app.id)} className="text-slate-500 hover:text-red-400 transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function AddApplicationModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [company, setCompany] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [jobUrl, setJobUrl] = useState('')
  const [status, setStatus] = useState<ApplicationStatus>('Interested')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await applicationService.createApplication({ company, job_title: jobTitle, job_url: jobUrl, status })
      onSuccess()
    } catch { } finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <h2 className="text-lg font-bold text-white mb-4">Add Application</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Company *</label>
            <input value={company} onChange={e => setCompany(e.target.value)} required placeholder="e.g. Google" className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Job Title *</label>
            <input value={jobTitle} onChange={e => setJobTitle(e.target.value)} required placeholder="e.g. Software Engineer" className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Job URL</label>
            <input value={jobUrl} onChange={e => setJobUrl(e.target.value)} type="url" placeholder="https://..." className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Status</label>
            <select value={status} onChange={e => setStatus(e.target.value as ApplicationStatus)} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500">
              {APPLICATION_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm rounded-lg transition-colors">Cancel</button>
            <button type="submit" disabled={loading} className="flex-1 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-lg flex items-center justify-center gap-2 disabled:opacity-60">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null} Add
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
