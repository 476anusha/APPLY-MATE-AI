import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, MapPin, Clock, Briefcase, ExternalLink, Heart, Plus, FileText, Bot, Loader2 } from 'lucide-react'
import { jobService } from '@/services/job.service'
import { savedJobService } from '@/services/saved-job.service'
import { applicationService } from '@/services/application.service'
import { formatSalary, formatRelativeDate } from '@/utils/formatters'
import type { Job } from '@/types'

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: job, isLoading, isError } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobService.getJob(id!),
    enabled: !!id,
  })

  const saveMutation = useMutation({
    mutationFn: () => savedJobService.saveJob(id!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['saved-jobs'] }),
  })

  const trackMutation = useMutation({
    mutationFn: () =>
      applicationService.createApplication({
        company: job!.company,
        job_title: job!.title,
        job_url: job!.application_url,
        job_id: job!.id,
        status: 'Interested',
      }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['applications'] }); navigate('/app/tracker') },
  })

  if (isLoading) return (
    <div className="flex items-center justify-center min-h-96">
      <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
    </div>
  )

  if (isError || !job) return (
    <div className="text-center py-16">
      <p className="text-slate-400">Job not found.</p>
      <button onClick={() => navigate('/app/jobs')} className="mt-4 text-purple-400 hover:text-purple-300 text-sm">← Back to jobs</button>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back */}
      <button onClick={() => navigate(-1)} className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to jobs
      </button>

      {/* Header card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h1 className="text-xl font-bold text-white mb-1">{job.title}</h1>
            <p className="text-slate-300 font-medium">{job.company}</p>
            <div className="flex flex-wrap gap-3 mt-3 text-sm text-slate-400">
              <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4" />{job.location}</span>
              <span className="flex items-center gap-1.5"><Clock className="w-4 h-4" />{formatRelativeDate(job.posted_at)}</span>
              <span className="flex items-center gap-1.5"><Briefcase className="w-4 h-4" />{job.employment_type}</span>
            </div>
          </div>
          <div className="flex flex-col gap-2 items-end">
            {(job.salary_min || job.salary_max) && (
              <p className="text-green-400 font-semibold text-sm">{formatSalary(job.salary_min, job.salary_max)}</p>
            )}
            <div className="flex gap-1.5 flex-wrap justify-end">
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${job.work_type === 'remote' ? 'bg-green-500/15 text-green-400' : 'bg-blue-500/15 text-blue-400'}`}>{job.work_type}</span>
              <span className="text-xs px-2.5 py-1 rounded-full bg-purple-500/15 text-purple-400">{job.experience_level}</span>
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-2 mt-5 pt-5 border-t border-slate-800">
          <button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          >
            <Heart className="w-4 h-4" /> Save Job
          </button>
          <button
            onClick={() => trackMutation.mutate()}
            disabled={trackMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" /> Add to Tracker
          </button>
          <button
            onClick={() => navigate(`/app/agent?action=cover-letter&jobId=${job.id}`)}
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          >
            <FileText className="w-4 h-4" /> Cover Letter
          </button>
          <button
            onClick={() => navigate(`/app/agent?action=tailor&jobId=${job.id}`)}
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          >
            <Bot className="w-4 h-4" /> Tailor Resume
          </button>
          <a
            href={job.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-4 py-2 text-sm bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-colors ml-auto"
          >
            Apply Now <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-white mb-4">Job Description</h2>
            <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{job.description}</div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Required Skills */}
          {job.required_skills && job.required_skills.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-white mb-3">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.required_skills.map(s => (
                  <span key={s} className="text-xs px-2.5 py-1 bg-blue-500/10 text-blue-300 border border-blue-500/20 rounded-full">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Preferred Skills */}
          {job.preferred_skills && job.preferred_skills.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-white mb-3">Nice to Have</h3>
              <div className="flex flex-wrap gap-2">
                {job.preferred_skills.map(s => (
                  <span key={s} className="text-xs px-2.5 py-1 bg-slate-700 text-slate-300 rounded-full">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Quick Stats */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-white">Job Details</h3>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between"><dt className="text-slate-400">Source</dt><dd className="text-slate-300 capitalize">{job.provider === 'demo' ? 'Demo listing' : job.provider}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-400">Type</dt><dd className="text-slate-300 capitalize">{job.employment_type}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-400">Work</dt><dd className="text-slate-300 capitalize">{job.work_type}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-400">Level</dt><dd className="text-slate-300 capitalize">{job.experience_level}</dd></div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}
