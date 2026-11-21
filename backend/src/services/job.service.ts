import api from './api'
import { Job, JobSearchParams, JobMatchResponse, PaginatedResponse } from '@/types'

export const jobService = {
  async searchJobs(params?: JobSearchParams): Promise<PaginatedResponse<Job>> {
    const response = await api.get<PaginatedResponse<Job>>('/jobs', { params })
    return response.data
  },

  async getJob(id: string): Promise<Job> {
    const response = await api.get<Job>(`/jobs/${id}`)
    return response.data
  },

  async matchJob(jobId: string, resumeId: string): Promise<JobMatchResponse> {
    const response = await api.post<JobMatchResponse>(`/jobs/${jobId}/match`, {
      resume_id: resumeId,
    })
    return response.data
  },
}
