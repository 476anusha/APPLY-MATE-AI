import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from '@/layouts/AppLayout'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

// Auth pages (small, load eagerly)
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/auth/ResetPasswordPage'

// Lazy-loaded app pages
const LandingPage = lazy(() => import('@/pages/landing/LandingPage'))
const DashboardPage = lazy(() => import('@/pages/app/DashboardPage'))
const ResumesPage = lazy(() => import('@/pages/app/ResumesPage'))
const JobsPage = lazy(() => import('@/pages/app/JobsPage'))
const JobDetailPage = lazy(() => import('@/pages/app/JobDetailPage'))
const AgentPage = lazy(() => import('@/pages/app/AgentPage'))
const TrackerPage = lazy(() => import('@/pages/app/TrackerPage'))
const SavedJobsPage = lazy(() => import('@/pages/app/SavedJobsPage'))
const InterviewPage = lazy(() => import('@/pages/app/InterviewPage'))
const AnalyticsPage = lazy(() => import('@/pages/app/AnalyticsPage'))
const SettingsPage = lazy(() => import('@/pages/app/SettingsPage'))

const PageLoader = () => (
  <div className="flex h-screen w-full items-center justify-center bg-slate-950">
    <LoadingSpinner size="lg" />
  </div>
)

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Landing */}
        <Route path="/" element={<LandingPage />} />

        {/* Auth routes */}
        <Route path="/auth/login" element={<LoginPage />} />
        <Route path="/auth/register" element={<RegisterPage />} />
        <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/auth/reset-password" element={<ResetPasswordPage />} />

        {/* Protected app routes */}
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<Navigate to="/app/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="resumes" element={<ResumesPage />} />
          <Route path="jobs" element={<JobsPage />} />
          <Route path="jobs/:id" element={<JobDetailPage />} />
          <Route path="agent" element={<AgentPage />} />
          <Route path="tracker" element={<TrackerPage />} />
          <Route path="saved" element={<SavedJobsPage />} />
          <Route path="interview" element={<InterviewPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
