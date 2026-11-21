import api from './api'
import { Resume, ResumeAnalysisResponse } from '@/types'

export const resumeService = {
  async uploadResume(file: File, title: string): Promise<Resume> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)

    const response = await api.post<Resume>('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getResumes(): Promise<Resume[]> {
    const response = await api.get<Resume[]>('/resumes')
    return response.data
  },

  async getResume(id: string): Promise<Resume> {
    const response = await api.get<Resume>(`/resumes/${id}`)
    return response.data
  },

  async deleteResume(id: string): Promise<{ success: boolean }> {
    const response = await api.delete<{ success: boolean }>(`/resumes/${id}`)
    return response.data
  },

  async analyzeResume(id: string): Promise<ResumeAnalysisResponse> {
    const response = await api.post<ResumeAnalysisResponse>(`/resumes/${id}/analyze`)
    return response.data
  },

  async getResumeAnalysis(id: string): Promise<ResumeAnalysisResponse> {
    const response = await api.get<ResumeAnalysisResponse>(`/resumes/${id}/analysis`)
    return response.data
  },

  async setDefaultResume(id: string): Promise<Resume> {
    const response = await api.post<Resume>(`/resumes/${id}/set-default`)
    return response.data
  },
}
