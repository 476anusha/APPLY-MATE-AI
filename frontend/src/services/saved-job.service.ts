import api from './api'
import { SavedJob } from '@/types'

export const savedJobService = {
  async getSavedJobs(): Promise<SavedJob[]> {
    const response = await api.get<SavedJob[]>('/saved-jobs')
    return response.data
  },

  async saveJob(jobId: string, notes?: string, category?: string): Promise<SavedJob> {
    const response = await api.post<SavedJob>('/saved-jobs', {
      job_id: jobId,
      notes,
      category,
    })
    return response.data
  },

  async removeSavedJob(id: string): Promise<{ success: boolean }> {
    const response = await api.delete<{ success: boolean }>(`/saved-jobs/${id}`)
    return response.data
  },
}
