import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'
import { Eye, EyeOff, Loader2, Briefcase, Check } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

const schema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
  terms: z.boolean().refine(v => v, 'You must accept the terms of service'),
}).refine(d => d.password === d.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
})
type FormData = z.infer<typeof schema>

function getStrength(pw: string): { level: number; label: string; color: string } {
  let score = 0
  if (pw.length >= 8) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[0-9]/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++
  if (score <= 1) return { level: score, label: 'Weak', color: 'bg-red-500' }
  if (score <= 2) return { level: score, label: 'Fair', color: 'bg-yellow-500' }
  if (score <= 3) return { level: score, label: 'Good', color: 'bg-blue-500' }
  return { level: score, label: 'Strong', color: 'bg-green-500' }
}

export default function RegisterPage() {
  const { register: authRegister } = useAuth()
  const navigate = useNavigate()
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [pwValue, setPwValue] = useState('')

  const { register, handleSubmit, formState: { errors, isSubmitting }, watch } = useForm<FormData>({
    resolver: zodResolver(schema),
  })
  const password = watch('password', '')

  const onSubmit = async (data: FormData) => {
    setError('')
    try {
      await authRegister(data.email, data.password, data.full_name)
      navigate('/app/dashboard')
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Registration failed. Please try again.')
    }
  }

  const strength = getStrength(password || '')

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 mb-8 justify-center">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Briefcase className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">ApplyMate AI</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-xl">
          <h1 className="text-2xl font-bold text-white mb-1">Create your account</h1>
          <p className="text-slate-400 text-sm mb-6">Start your AI-powered job search journey</p>

          {error && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded-lg text-red-400 text-sm">{error}</div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Full Name</label>
              <input {...register('full_name')} placeholder="Rahul Sharma" className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm" />
              {errors.full_name && <p className="mt-1 text-xs text-red-400">{errors.full_name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Email</label>
              <input {...register('email')} type="email" placeholder="you@example.com" className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm" />
              {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <input {...register('password')} type={showPw ? 'text' : 'password'} placeholder="Min. 8 characters" className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm pr-10" />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {password && (
                <div className="mt-2">
                  <div className="flex gap-1 mb-1">
                    {[1,2,3,4].map(i => (
                      <div key={i} className={`h-1 flex-1 rounded-full transition-all ${i <= strength.level ? strength.color : 'bg-slate-700'}`} />
                    ))}
                  </div>
                  <p className="text-xs text-slate-400">Strength: <span className="text-slate-200">{strength.label}</span></p>
                </div>
              )}
              {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Confirm Password</label>
              <input {...register('confirm_password')} type="password" placeholder="Repeat password" className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm" />
              {errors.confirm_password && <p className="mt-1 text-xs text-red-400">{errors.confirm_password.message}</p>}
            </div>

            <label className="flex items-start gap-2 cursor-pointer">
              <input {...register('terms')} type="checkbox" className="mt-0.5 w-4 h-4 rounded border-slate-600 bg-slate-800 accent-purple-500" />
              <span className="text-sm text-slate-400">
                I agree to the{' '}
                <a href="#" className="text-purple-400 hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-purple-400 hover:underline">Privacy Policy</a>
              </span>
            </label>
            {errors.terms && <p className="text-xs text-red-400">{errors.terms.message}</p>}

            <button type="submit" disabled={isSubmitting} className="w-full py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-60">
              {isSubmitting ? <><Loader2 className="w-4 h-4 animate-spin" />Creating account…</> : 'Create Account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-400">
            Already have an account?{' '}
            <Link to="/auth/login" className="text-purple-400 hover:text-purple-300 font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
