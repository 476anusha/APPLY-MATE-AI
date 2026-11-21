export const APPLICATION_STATUSES = [
  'Interested',
  'Saved',
  'Applied',
  'Assessment',
  'Interview Scheduled',
  'Interview Completed',
  'Offer Received',
  'Rejected',
  'Withdrawn',
] as const

export const STATUS_COLORS: Record<string, string> = {
  Interested: 'bg-slate-500 text-white',
  Saved: 'bg-blue-500 text-white',
  Applied: 'bg-indigo-500 text-white',
  Assessment: 'bg-yellow-500 text-black',
  'Interview Scheduled': 'bg-purple-500 text-white',
  'Interview Completed': 'bg-teal-500 text-white',
  'Offer Received': 'bg-green-500 text-white',
  Rejected: 'bg-red-500 text-white',
  Withdrawn: 'bg-gray-500 text-white',
}

export const STATUS_DOT_COLORS: Record<string, string> = {
  Interested: 'bg-slate-400',
  Saved: 'bg-blue-400',
  Applied: 'bg-indigo-400',
  Assessment: 'bg-yellow-400',
  'Interview Scheduled': 'bg-purple-400',
  'Interview Completed': 'bg-teal-400',
  'Offer Received': 'bg-green-400',
  Rejected: 'bg-red-400',
  Withdrawn: 'bg-gray-400',
}

export const EXPERIENCE_LEVELS = [
  { value: 'entry', label: 'Entry Level / Fresher' },
  { value: 'mid', label: 'Mid Level (2–5 years)' },
  { value: 'senior', label: 'Senior Level (5+ years)' },
  { value: 'lead', label: 'Lead / Principal' },
] as const

export const JOB_TYPES = [
  { value: 'full-time', label: 'Full Time' },
  { value: 'part-time', label: 'Part Time' },
  { value: 'contract', label: 'Contract' },
  { value: 'internship', label: 'Internship' },
] as const

export const WORK_TYPES = [
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'onsite', label: 'On-site' },
] as const

export const TONE_OPTIONS = [
  { value: 'professional', label: 'Professional' },
  { value: 'confident', label: 'Confident' },
  { value: 'enthusiastic', label: 'Enthusiastic' },
  { value: 'concise', label: 'Concise' },
] as const
