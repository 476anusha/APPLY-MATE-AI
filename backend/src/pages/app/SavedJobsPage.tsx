import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bookmark, ExternalLink, Trash2, ArrowRight, Loader2, Heart } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { savedJobService } from '@/services/saved-job.service'
import { applicationService } from '@/services/application.service'
import { formatSalary, formatRelativeDate } from '@/utils/formatters'
import type { SavedJob } from '@/types'

export default function SavedJobsPage() {
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: savedJobs, isLoading } = useQuery({
    queryKey: ['saved-jobs'],
    queryFn: savedJobService.getSavedJobs,
  })

  const removeMutation = useMutation({
    mutationFn: (id: string) => savedJobService.removeSavedJob(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['saved-jobs'] }),
  })

  const trackMutation = useMutation({
    mutationFn: (sj: SavedJob) =>
      applicationService.createApplication({
        company: sj.job?.company ?? sj.company ?? 'Unknown Company',
        job_title: sj.job?.title ?? sj.title ?? 'Unknown Position',
        job_url: sj.job?.application_url ?? sj.apply_url,
        job_id: sj.job?.id ?? sj.job_id,
        status: 'Interested',
      }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['applications'] }); navigate('/app/tracker') },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Saved Jobs</h1>
        <p className="text-slate-400 text-sm mt-1">Jobs you've bookmarked for later</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-5 animate-pulse h-48" />
          ))}
        </div>
      ) : !savedJobs?.length ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
            <Bookmark className="w-8 h-8 text-slate-600" />
          </div>
          <h3 className="text-white font-semibold mb-2">No saved jobs yet</h3>
          <p className="text-slate-400 text-sm mb-4">Browse jobs and save the ones that interest you</p>
          <button
            onClick={() => navigate('/app/jobs')}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-lg transition-colors"
          >
            Browse Jobs <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {savedJobs.map((sj: SavedJob) => {
            // Support both nested sj.job and flat API response fields
            const jobTitle = sj.job?.title ?? sj.title ?? 'Unknown Position'
            const jobCompany = sj.job?.company ?? sj.company ?? 'Unknown Company'
            const jobLocation = sj.job?.location ?? sj.location ?? ''
            const jobWorkType = sj.job?.work_type ?? sj.work_type ?? ''
            const jobExpLevel = sj.job?.experience_level ?? ''
            const jobSalaryMin = sj.job?.salary_min ?? sj.salary_min
            const jobSalaryMax = sj.job?.salary_max ?? sj.salary_max
            const jobApplyUrl = sj.job?.application_url ?? sj.apply_url ?? '#'

            return (
              <div key={sj.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col gap-3 hover:border-slate-700 transition-colors">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-semibold text-white text-sm">{jobTitle}</h3>
                    <p className="text-slate-400 text-xs mt-0.5">{jobCompany}</p>
                  </div>
                  <button
                    onClick={() => removeMutation.mutate(sj.id)}
                    className="text-slate-500 hover:text-red-400 transition-colors flex-shrink-0"
                  >
                    <Heart className="w-4 h-4 fill-current text-red-400" />
                  </button>
                </div>

                <div className="flex flex-wrap gap-1.5">
                  {jobWorkType && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${jobWorkType === 'remote' ? 'bg-green-500/15 text-green-400' : 'bg-slate-700 text-slate-400'}`}>
                      {jobWorkType}
                    </span>
                  )}
                  {jobExpLevel && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-400">{jobExpLevel}</span>
                  )}
                </div>

                {jobLocation && <p className="text-xs text-slate-400">{jobLocation}</p>}
                {(jobSalaryMin || jobSalaryMax) && (
                  <p className="text-xs font-medium text-green-400">{formatSalary(jobSalaryMin, jobSalaryMax)}</p>
                )}
                {sj.notes && <p className="text-xs text-slate-400 italic border-l-2 border-slate-700 pl-2">{sj.notes}</p>}
                <p className="text-xs text-slate-500">Saved {formatRelativeDate(sj.created_at)}</p>

                <div className="flex gap-2 mt-auto pt-1">
                  <button
                    onClick={() => trackMutation.mutate(sj)}
                    disabled={trackMutation.isPending}
                    className="flex-1 py-1.5 text-xs font-medium bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors flex items-center justify-center gap-1 disabled:opacity-60"
                  >
                    <ArrowRight className="w-3.5 h-3.5" /> Add to Tracker
                  </button>
                  <a
                    href={jobApplyUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
