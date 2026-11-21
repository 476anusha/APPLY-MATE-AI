import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { User } from '@/types'
import { authService } from '@/services/auth.service'

export interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  login(email: string, password: string): Promise<void>
  register(email: string, password: string, fullName: string): Promise<void>
  logout(): void
  refreshToken(): Promise<void>
  setUser: React.Dispatch<React.SetStateAction<User | null>>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('applymate_user')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch {
        return null
      }
    }
    return null
  })

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('applymate_access_token')
  })

  const [isLoading, setIsLoading] = useState<boolean>(true)

  const logout = useCallback(() => {
    localStorage.removeItem('applymate_access_token')
    localStorage.removeItem('applymate_refresh_token')
    localStorage.removeItem('applymate_user')
    setToken(null)
    setUser(null)
    authService.logout().catch(() => {})
  }, [])

  const refreshToken = useCallback(async () => {
    const rfToken = localStorage.getItem('applymate_refresh_token')
    if (!rfToken) {
      logout()
      return
    }
    try {
      const data = await authService.refreshToken(rfToken)
      localStorage.setItem('applymate_access_token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('applymate_refresh_token', data.refresh_token)
      }
      setToken(data.access_token)
    } catch {
      logout()
    }
  }, [logout])

  useEffect(() => {
    const initAuth = async () => {
      const accessToken = localStorage.getItem('applymate_access_token')
      if (accessToken) {
        setToken(accessToken)
        try {
          const userData = await authService.getMe()
          setUser(userData)
          localStorage.setItem('applymate_user', JSON.stringify(userData))
        } catch {
          // Attempt refresh
          await refreshToken()
        }
      }
      setIsLoading(false)
    }

    initAuth()

    const handleLogoutEvent = () => {
      logout()
    }

    window.addEventListener('auth:logout', handleLogoutEvent)
    return () => {
      window.removeEventListener('auth:logout', handleLogoutEvent)
    }
  }, [logout, refreshToken])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const tokenData = await authService.login(email, password)
      localStorage.setItem('applymate_access_token', tokenData.access_token)
      localStorage.setItem('applymate_refresh_token', tokenData.refresh_token)
      setToken(tokenData.access_token)

      const userData = await authService.getMe()
      setUser(userData)
      localStorage.setItem('applymate_user', JSON.stringify(userData))
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (email: string, password: string, fullName: string) => {
    setIsLoading(true)
    try {
      await authService.register(email, password, fullName)
      await login(email, password)
    } finally {
      setIsLoading(false)
    }
  }

  const isAuthenticated = !!token && !!user

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        refreshToken,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
