import api from './api'
import { User, TokenResponse } from '@/types'

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
}

export const authService = {
  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', { email, password })
    return response.data
  },

  async register(email: string, password: string, fullName: string): Promise<User> {
    const response = await api.post<User>('/auth/register', {
      email,
      password,
      full_name: fullName,
    })
    return response.data
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout')
    } catch {
      // ignore
    } finally {
      localStorage.removeItem('applymate_access_token')
      localStorage.removeItem('applymate_refresh_token')
      localStorage.removeItem('applymate_user')
    }
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/forgot-password', { email })
    return response.data
  },

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/reset-password', {
      token,
      new_password: newPassword,
    })
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}
