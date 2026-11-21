// All TypeScript interfaces for ApplyMate AI
// Updated to match backend API + TanStack Query v5

export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  avatar_url?: string   // convenience alias from profile
}

export interface UserProfile {
  id: string
  user_id: string
  phone?: string
  avatar_url?: string
  location?: string
  education?: string
  university?: string
  graduation_year?: number
  experience_level?: string
  preferred_roles?: string[]
  preferred_locations?: string[]
  expected_salary_min?: number
  expected_salary_max?: number
  skills?: string[]
  linkedin_url?: string
  github_url?: string
  portfolio_url?: string
  bio?: string
}

export interface Resume {
  id: string
  user_id?: string
  title: string
  file_name: string
  file_url: string
  file_type?: string
  file_size: number
  is_default: boolean    // was is_primary — use is_default
  is_primary?: boolean   // backward-compat alias
  is_parsed?: boolean
  parse_status?: 'pending' | 'processing' | 'completed' | 'failed'
  overall_score?: number
  parsed_skills?: string[]
  created_at: string
  updated_at?: string
  extracted_data?: ExtractedResumeData
  parsed_data?: ExtractedResumeData  // backward-compat alias
  analysis?: ResumeAnalysisResponse
}

export interface ExtractedResumeData {
  id?: string
  resume_id?: string
  full_name?: string
  email?: string
  phone?: string
  location?: string   // convenience field (not in DB, may come from bio)
  summary?: string
  education?: EducationEntry[]
  experience?: ExperienceEntry[]
  projects?: ProjectEntry[]
  technical_skills?: string[]
  skills?: string[]          // alias returned by API
  soft_skills?: string[]
  certifications?: (CertificationEntry | string)[]
  achievements?: string[]
  languages?: string[]
  overall_score?: number
  ats_score?: number
  section_scores?: Record<string, number>
  strengths?: string[]
  weaknesses?: string[]
  suggestions?: string[]
  improvements?: string[]    // alias
  missing_keywords?: string[]
  raw_text?: string
}

export interface ResumeAnalysisResponse {
  resume_id: string
  score?: number
  overall_score?: number  // alias for score
  summary?: string
  strengths?: string[]
  improvements?: string[]
  weaknesses?: string[]    // alias for improvements
  suggestions?: string[]   // alias for improvements
  missing_keywords?: string[]
  section_scores?: Record<string, number>
  ats_compatibility?: {
    score?: number
    keywords_found?: string[]
    keywords_missing?: string[]
    missing_keywords?: string[]
    formatting_issues?: string[]
  }
}

export interface EducationEntry {
  degree?: string
  university?: string
  institution?: string    // alias used by AI
  field_of_study?: string
  year?: number
  gpa?: string
  start_date?: string
  end_date?: string
}

export interface ExperienceEntry {
  title: string
  company: string
  duration?: string
  location?: string
  start_date?: string
  end_date?: string
  current?: boolean
  is_current?: boolean
  description?: string
  bullets?: string[]
  highlights?: string[]  // alias
}

export interface ProjectEntry {
  name?: string
  title?: string         // alias used by AI
  description: string
  tech_stack?: string[]
  technologies?: string[]  // alias
  url?: string
  link?: string           // alias
}

export interface CertificationEntry {
  name: string
  issuer?: string
  year?: number
}

export interface Job {
  id: string
  external_id: string
  provider: string
  title: string
  company: string
  company_logo_url?: string
  location: string
  is_remote: boolean
  work_type: 'remote' | 'hybrid' | 'onsite'
  employment_type: 'full-time' | 'part-time' | 'contract' | 'internship'
  experience_level: 'entry' | 'mid' | 'senior' | 'lead'
  salary_min?: number
  salary_max?: number
  salary_currency?: string
  description: string
  responsibilities?: string[]
  requirements?: string[]
  required_skills?: string[]
  preferred_skills?: string[]
  application_url: string
  apply_url?: string    // alias
  deadline?: string
  posted_at: string
  is_active: boolean
  is_demo?: boolean
  match_score?: number
}

export interface JobMatch {
  job_id: string
  resume_id?: string
  overall_score: number
  skill_score: number
  experience_score: number
  education_score: number
  keyword_score: number
  matched_skills: string[]
  missing_skills: string[]
  explanation: string
  recommendations: string[]
  is_demo?: boolean
}

export interface SavedJob {
  id: string
  job_id: string
  job?: Job             // may not always be populated
  notes?: string
  category?: string
  created_at: string
  // Flattened job info (from API)
  title?: string
  company?: string
  location?: string
  employment_type?: string
  work_type?: string
  salary_min?: number
  salary_max?: number
  apply_url?: string
  skills_required?: string[]
  is_demo?: boolean
}

export type ApplicationStatus =
  | 'Interested'
  | 'Saved'
  | 'Applied'
  | 'Assessment'
  | 'Interview Scheduled'
  | 'Interview Completed'
  | 'Offer Received'
  | 'Rejected'
  | 'Withdrawn'

export interface Application {
  id: string
  user_id: string
  job_id?: string
  job?: Job
  company: string
  job_title: string
  job_url?: string
  status: ApplicationStatus
  applied_date?: string
  deadline?: string
  interview_date?: string
  follow_up_date?: string
  recruiter_name?: string
  recruiter_email?: string
  salary_offered?: number
  notes?: ApplicationNote[]
  created_at: string
  updated_at?: string
}

export interface ApplicationNote {
  id: string
  application_id: string
  content: string
  created_at: string
}

export interface CoverLetter {
  id: string
  user_id: string
  job_id?: string
  resume_id?: string
  content: string
  tone?: string
  job_title?: string
  company_name?: string
  created_at: string
  updated_at?: string
}

export interface AIConversation {
  id: string
  title: string
  is_active: boolean
  created_at: string
}

export interface AIMessage {
  id: string
  conversation_id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: Record<string, unknown>
  created_at: string
}

export interface Notification {
  id: string
  type: string
  title: string
  message: string
  is_read: boolean
  action_url?: string
  created_at: string
}

export interface DashboardStats {
  total_applications: number
  total_saved: number
  total_interviews: number
  total_offers: number
  total_rejections: number
  pending_applications: number
  conversion_rate: number
}

export interface AnalyticsData {
  dashboard_stats: DashboardStats
  applications_by_status: Record<string, number>
  applications_over_time: Array<{ date: string; count: number }>
  top_companies: Array<{ company: string; count: number }>
  match_score_distribution: Array<{ range: string; count: number }>
  weekly_report?: string
}

export interface SubscriptionPlan {
  id: string
  name: string
  price_monthly: number
  price_yearly: number
  features: string[]
  limits: Record<string, number>
  recommended?: boolean
}

export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
  is_demo?: boolean
  demo_notice?: string
}

// ── Auth ────────────────────────────────────────────────────────────────────
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// ── Jobs ────────────────────────────────────────────────────────────────────
export interface JobSearchParams {
  q?: string
  location?: string
  work_type?: string
  experience_level?: string
  employment_type?: string
  salary_min?: number
  salary_max?: number
  page?: number
  size?: number
}

export interface JobMatchResponse {
  overall_score: number
  skill_score: number
  experience_score: number
  education_score: number
  keyword_score: number
  matched_skills: string[]
  missing_skills: string[]
  explanation: string
  recommendations: string[]
  is_demo?: boolean
}

// ── Analytics ───────────────────────────────────────────────────────────────
export interface DashboardStatsResponse extends DashboardStats {
  applications_by_status?: Record<string, number>
  recent_activity?: Array<{ type: string; message: string; date: string }>
}

export interface TimelineData {
  date: string
  count: number
  status?: string
}

export interface StatusData {
  status: string
  count: number
  percentage?: number
}

export interface SkillsData {
  skill: string
  match_count: number
  gap_count: number
}
