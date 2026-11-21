import { Outlet, Link } from 'react-router-dom'
import { Sparkles, CheckCircle2 } from 'lucide-react'

const features = [
  'AI-powered resume optimization and ATS scoring',
  'Automated multi-platform job discovery and matching',
  'Instant tailored cover letters customized per role',
  'Intelligent interview question preparation and mock feedback',
  'Visual Kanban job application pipeline tracker',
]

export function AuthLayout() {
  return (
    <div className="flex min-h-screen w-full bg-slate-950 text-slate-100 font-sans">
      {/* Left side: Premium branding & feature highlights (visible on lg screens) */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between border-r border-slate-800/80 bg-gradient-to-br from-slate-950 via-purple-950/20 to-slate-900 p-12 relative overflow-hidden">
        {/* Glow effects */}
        <div className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-purple-600/15 blur-3xl" />
        <div className="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-indigo-600/15 blur-3xl" />

        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 shadow-lg shadow-purple-500/30">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-purple-200 bg-clip-text text-transparent">
                ApplyMate AI
              </span>
              <p className="text-xs text-slate-400 font-medium">Your Autonomous Career Co-pilot</p>
            </div>
          </Link>
        </div>

        <div className="relative z-10 max-w-lg my-auto py-12">
          <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-3 py-1 text-xs font-semibold text-purple-300 mb-6">
            <Sparkles className="h-3.5 w-3.5" />
            Accelerate Your Job Search
          </div>
          <h2 className="text-4xl font-extrabold tracking-tight text-white leading-tight mb-4">
            Apply Smarter. <br />
            <span className="bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Land 3x Faster.
            </span>
          </h2>
          <p className="text-sm text-slate-400 mb-8 leading-relaxed">
            Harness autonomous AI agents to parse resumes, uncover matching high-value opportunities, craft bespoke applications, and prepare for interviews.
          </p>

          <div className="space-y-3.5">
            {features.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-3 text-sm text-slate-300">
                <CheckCircle2 className="h-4.5 w-4.5 text-purple-400 shrink-0" />
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 text-xs text-slate-500">
          &copy; {new Date().getFullYear()} ApplyMate AI Inc. All rights reserved.
        </div>
      </div>

      {/* Right side: Form container */}
      <div className="flex flex-1 flex-col justify-center items-center p-6 md:p-12 lg:w-1/2">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center justify-center gap-2.5 mb-8">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white">ApplyMate AI</span>
          </div>

          <Outlet />
        </div>
      </div>
    </div>
  )
}
