import api from './api'
import { Application, ApplicationNote, ApplicationStatus } from '@/types'

export interface CreateApplicationPayload {
  job_id?: string
  job_title: string
  company: string
  location?: string
  job_url?: string
  salary?: string
  status?: ApplicationStatus
  applied_at?: string
  notes?: string
}

export interface UpdateApplicationPayload {
  job_title?: string
  company?: string
  location?: string
  job_url?: string
  salary?: string
  status?: ApplicationStatus
  applied_at?: string
  interview_date?: string
  offer_amount?: number
  offer_deadline?: string
}

export const applicationService = {
  async getApplications(filters?: Record<string, unknown>): Promise<Application[]> {
    const response = await api.get<Application[]>('/applications', { params: filters })
    return response.data
  },

  async getApplication(id: string): Promise<Application> {
    const response = await api.get<Application>(`/applications/${id}`)
    return response.data
  },

  async createApplication(data: CreateApplicationPayload): Promise<Application> {
    const response = await api.post<Application>('/applications', data)
    return response.data
  },

  async updateApplication(id: string, data: UpdateApplicationPayload): Promise<Application> {
    const response = await api.patch<Application>(`/applications/${id}`, data)
    return response.data
  },

  async updateStatus(id: string, status: ApplicationStatus): Promise<Application> {
    const response = await api.patch<Application>(`/applications/${id}/status`, { status })
    return response.data
  },

  async deleteApplication(id: string): Promise<{ success: boolean }> {
    const response = await api.delete<{ success: boolean }>(`/applications/${id}`)
    return response.data
  },

  async addNote(applicationId: string, content: string): Promise<ApplicationNote> {
    const response = await api.post<ApplicationNote>(`/applications/${applicationId}/notes`, {
      content,
    })
    return response.data
  },

  async getKanbanBoard(): Promise<Record<ApplicationStatus, Application[]>> {
    const response = await api.get<Record<ApplicationStatus, Application[]>>('/applications/kanban')
    return response.data
  },
}
