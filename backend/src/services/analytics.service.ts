import api from './api'
import {
  DashboardStatsResponse,
  TimelineData,
  StatusData,
  SkillsData,
} from '@/types'

export const analyticsService = {
  async getDashboardStats(): Promise<DashboardStatsResponse> {
    const response = await api.get<DashboardStatsResponse>('/analytics/dashboard')
    return response.data
  },

  async getApplicationTimeline(days: number = 30): Promise<TimelineData[]> {
    const response = await api.get<TimelineData[]>('/analytics/timeline', {
      params: { days },
    })
    return response.data
  },

  async getApplicationsByStatus(): Promise<StatusData[]> {
    const response = await api.get<StatusData[]>('/analytics/by-status')
    return response.data
  },

  async getSkillsAnalytics(): Promise<SkillsData[]> {
    const response = await api.get<SkillsData[]>('/analytics/skills')
    return response.data
  },

  async getWeeklyReport(): Promise<{ report: string; highlights: string[] }> {
    const response = await api.get<{ report: string; highlights: string[] }>('/analytics/weekly-report')
    return response.data
  },
}
