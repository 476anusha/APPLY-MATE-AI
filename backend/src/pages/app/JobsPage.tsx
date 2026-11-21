import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Search, Filter, MapPin, Clock, Briefcase, Heart, ExternalLink, Loader2, Wifi, WifiOff } from 'lucide-react'
import { jobService } from '@/services/job.service'
import { savedJobService } from '@/services/saved-job.service'
import { useDebounce } from '@/hooks/useDebounce'
import { formatSalary, formatRelativeDate } from '@/utils/formatters'
import { WORK_TYPES, EXPERIENCE_LEVELS, JOB_TYPES } from '@/utils/constants'
import type { Job } from '@/types'

export default function JobsPage() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [q, setQ] = useState('')
  const [workType, setWorkType] = useState<string[]>([])
  const [expLevel, setExpLevel] = useState('')
  const [page, setPage] = useState(1)
  const [showFilters, setShowFilters] = useState(false)
  const debouncedQ = useDebounce(q, 400)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['jobs', debouncedQ, workType, expLevel, page],
    queryFn: () => jobService.searchJobs({ q: debouncedQ, work_type: workType[0], experience_level: expLevel, page }),
    placeholderData: (prev) => prev,
  })

  const saveMutation = useMutation({
    mutationFn: (jobId: string) => savedJobService.saveJob(jobId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['saved-jobs'] }),
  })

  const toggleWorkType = (v: string) =>
    setWorkType(prev => prev.includes(v) ? prev.filter(x => x !== v) : [...prev, v])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Discover Jobs</h1>
        <p className="text-slate-400 text-sm mt-1">Find your perfect role from curated opportunities</p>
      </div>

      {/* Search + Filter bar */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            value={q}
            onChange={e => { setQ(e.target.value); setPage(1) }}
            placeholder="Search by title, company, or skill…"
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors ${showFilters ? 'bg-purple-600 border-purple-600 text-white' : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-purple-500'}`}
        >
          <Filter className="w-4 h-4" /> Filters
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Work Type</p>
            <div className="space-y-2">
              {WORK_TYPES.map(wt => (
                <label key={wt.value} className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={workType.includes(wt.value)} onChange={() => { toggleWorkType(wt.value); setPage(1) }} className="accent-purple-500 w-4 h-4" />
                  <span className="text-sm text-slate-300">{wt.label}</span>
                </label>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Experience Level</p>
            <div className="space-y-2">
              {EXPERIENCE_LEVELS.map(el => (
                <label key={el.value} className="flex items-center gap-2 cursor-pointer">
                  <input type="radio" name="exp" checked={expLevel === el.value} onChange={() => { setExpLevel(el.value); setPage(1) }} className="accent-purple-500 w-4 h-4" />
                  <span className="text-sm text-slate-300">{el.label}</span>
                </label>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Employment Type</p>
            <div className="space-y-2">
              {JOB_TYPES.map(jt => (
                <label key={jt.value} className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="accent-purple-500 w-4 h-4" />
                  <span className="text-sm text-slate-300">{jt.label}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="md:col-span-3 flex justify-end">
            <button onClick={() => { setWorkType([]); setExpLevel(''); setPage(1) }} className="text-sm text-slate-400 hover:text-white">Clear filters</button>
          </div>
        </div>
      )}

      {/* Demo notice */}
      {data?.is_demo && (
        <div className="flex items-center gap-2 px-4 py-2.5 bg-blue-900/20 border border-blue-800/30 rounded-lg text-xs text-blue-300">
          <WifiOff className="w-4 h-4 flex-shrink-0" />
          <span>{data.demo_notice}</span>
        </div>
      )}

      {/* Results info */}
      {!isLoading && data && (
        <p className="text-sm text-slate-400">{data.total} job{data.total !== 1 ? 's' : ''} found</p>
      )}

      {/* Job cards grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <JobCardSkeleton key={i} />)}
        </div>
      ) : isError ? (
        <div className="text-center py-16 text-slate-400">Failed to load jobs. Please try again.</div>
      ) : data?.items?.length === 0 ? (
        <div className="text-center py-16">
          <Briefcase className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No jobs found. Try adjusting your search or filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {data?.items?.map((job: Job) => (
            <JobCard key={job.id} job={job} onSave={() => saveMutation.mutate(job.id)} onView={() => navigate(`/app/jobs/${job.id}`)} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex justify-center gap-2">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-4 py-2 text-sm bg-slate-800 text-slate-300 rounded-lg disabled:opacity-40 hover:bg-slate-700">Previous</button>
          <span className="px-4 py-2 text-sm text-slate-400">{page} / {data.pages}</span>
          <button onClick={() => setPage(p => Math.min(data.pages, p + 1))} disabled={page === data.pages} className="px-4 py-2 text-sm bg-slate-800 text-slate-300 rounded-lg disabled:opacity-40 hover:bg-slate-700">Next</button>
        </div>
      )}
    </div>
  )
}

function JobCard({ job, onSave, onView }: { job: Job; onSave: () => void; onView: () => void }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold text-white text-sm leading-tight">{job.title}</h3>
          <p className="text-slate-400 text-xs mt-0.5">{job.company}</p>
        </div>
        <button onClick={onSave} className="text-slate-500 hover:text-red-400 transition-colors flex-shrink-0 mt-0.5">
          <Heart className="w-4 h-4" />
        </button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${job.work_type === 'remote' ? 'bg-green-500/15 text-green-400' : job.work_type === 'hybrid' ? 'bg-blue-500/15 text-blue-400' : 'bg-slate-500/15 text-slate-400'}`}>
          {job.work_type}
        </span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-400">{job.experience_level}</span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-400">{job.employment_type}</span>
      </div>
      <div className="flex items-center gap-3 text-xs text-slate-400">
        <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>
        <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{formatRelativeDate(job.posted_at)}</span>
      </div>
      {job.required_skills && job.required_skills.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {job.required_skills.slice(0, 4).map(s => (
            <span key={s} className="text-xs px-2 py-0.5 bg-slate-800 text-slate-300 rounded">{s}</span>
          ))}
          {job.required_skills.length > 4 && <span className="text-xs text-slate-500">+{job.required_skills.length - 4}</span>}
        </div>
      )}
      {(job.salary_min || job.salary_max) && (
        <p className="text-xs font-medium text-green-400">{formatSalary(job.salary_min, job.salary_max, job.salary_currency)}</p>
      )}
      <div className="flex gap-2 mt-auto pt-1">
        <button onClick={onView} className="flex-1 py-2 text-xs font-medium bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors">View Details</button>
        <a href={job.application_url} target="_blank" rel="noopener noreferrer" className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors">
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  )
}

function JobCardSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 animate-pulse space-y-3">
      <div className="h-4 bg-slate-700 rounded w-3/4" />
      <div className="h-3 bg-slate-700 rounded w-1/2" />
      <div className="flex gap-2"><div className="h-5 bg-slate-700 rounded-full w-16" /><div className="h-5 bg-slate-700 rounded-full w-14" /></div>
      <div className="h-3 bg-slate-700 rounded w-2/3" />
      <div className="flex gap-1"><div className="h-5 bg-slate-700 rounded w-14" /><div className="h-5 bg-slate-700 rounded w-14" /></div>
      <div className="h-8 bg-slate-700 rounded-lg" />
    </div>
  )
}
