import { Link } from 'react-router-dom'
import {
  Sparkles,
  ArrowRight,
  FileCheck2,
  Briefcase,
  FileText,
  KanbanSquare,
  MessageSquare,
  BarChart3,
  Check,
  Star,
  Play,
  Layers,
  Zap,
  Target,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const features = [
  {
    icon: FileCheck2,
    title: 'AI Resume Analysis',
    description:
      'Get instant ATS compatibility scores, section-by-section breakdown, and actionable suggestions to beat recruiter filters.',
  },
  {
    icon: Briefcase,
    title: 'Smart Job Matching',
    description:
      'Hybrid semantic matching aggregates high-signal opportunities across Adzuna, Remotive, and Arbeitnow tailored to your exact profile.',
  },
  {
    icon: FileText,
    title: 'Tailored Cover Letters',
    description:
      'Generate hyper-personalized, tone-aware cover letters directly aligning your experiences with the specific job specifications.',
  },
  {
    icon: KanbanSquare,
    title: 'Application Pipeline Tracker',
    description:
      'Organize your applications on a fluid drag-and-drop Kanban board with deadline alerts, salary trackers, and interview notes.',
  },
  {
    icon: MessageSquare,
    title: 'AI Interview Coach',
    description:
      'Practice with role-specific technical and behavioral questions generated directly from the job description with real-time feedback.',
  },
  {
    icon: BarChart3,
    title: 'Career & Market Analytics',
    description:
      'Track conversion rates from application to offer, uncover in-demand skill trends, and receive automated weekly career digests.',
  },
]

const steps = [
  {
    number: '01',
    title: 'Upload Your Resume',
    description:
      'Drop your existing resume in PDF or DOCX format. Our parser extracts your competencies, education, and achievements in seconds.',
  },
  {
    number: '02',
    title: 'Discover & Match Jobs',
    description:
      'Our intelligent AI matching engine curates the highest-affinity openings and pinpoints matching strengths and keyword gaps.',
  },
  {
    number: '03',
    title: 'Tailor, Apply & Track',
    description:
      'Generate customized cover letters and tailored resume points with one click, then manage the entire lifecycle through your tracker.',
  },
]

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for getting started and exploring core features.',
    features: [
      '2 Resume Uploads',
      '5 AI Analyses per month',
      'Basic Job Discovery',
      'Kanban Application Tracker',
      'Standard Cover Letter generation',
    ],
    cta: 'Get Started Free',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$19',
    period: 'per month',
    description: 'For active job seekers demanding maximum interview velocity.',
    features: [
      '10 Resume Uploads & Versions',
      '50 AI Analyses per month',
      'AI Resume Tailoring Engine',
      'Full Multi-source Job Match scoring',
      'AI Interview Question Generator & Practice Mode',
      'Weekly Automated Career Reports',
      'Priority Support',
    ],
    cta: 'Start 14-Day Free Trial',
    highlighted: true,
  },
  {
    name: 'Premium',
    price: '$39',
    period: 'per month',
    description: 'Autonomous AI power for ambitious senior engineers & executives.',
    features: [
      'Unlimited Resume Uploads',
      '200 AI Analyses per month',
      'Autonomous AI Agent Orchestrator',
      'Interactive Mock Interview Voice Simulator',
      'Custom Tone & Brand Voice Profiles',
      'Comprehensive Market Salary Analytics',
      '24/7 Dedicated Concierge Support',
    ],
    cta: 'Upgrade to Premium',
    highlighted: false,
  },
]

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Staff Frontend Engineer at Stripe',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=120&auto=format&fit=crop&q=80',
    quote:
      'ApplyMate completely changed the game for me. The AI resume feedback caught 4 critical ATS gaps that other scanners missed. Landed 3 top-tier interviews within 2 weeks!',
  },
  {
    name: 'Marcus Vance',
    role: 'Lead Cloud Architect at Snowflake',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&auto=format&fit=crop&q=80',
    quote:
      'The tailor resume and cover letter features saved me hours on every application without ever sounding generic or robotic. Truly a 10x career co-pilot.',
  },
  {
    name: 'Elena Rostova',
    role: 'Senior Product Manager at Figma',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop&q=80',
    quote:
      'The Kanban tracker paired with the interview preparation questions gave me tremendous confidence going into recruiter screens. It made the entire process painless.',
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-purple-600 selection:text-white">
      {/* Sticky Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-slate-800/70 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 shadow-md shadow-purple-500/30">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-purple-200 bg-clip-text text-transparent">
              ApplyMate AI
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#features" className="hover:text-white transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="hover:text-white transition-colors">
              How it Works
            </a>
            <a href="#pricing" className="hover:text-white transition-colors">
              Pricing
            </a>
            <a href="#testimonials" className="hover:text-white transition-colors">
              Testimonials
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link to="/auth/login">
              <Button variant="ghost" size="sm" className="text-slate-300">
                Log in
              </Button>
            </Link>
            <Link to="/auth/register">
              <Button size="sm" className="shadow-lg shadow-purple-600/25">
                Get Started
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-28 md:pt-32 md:pb-36">
        {/* Glow Backgrounds */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[800px] rounded-full bg-gradient-to-tr from-purple-600/20 via-indigo-600/15 to-transparent blur-3xl pointer-events-none" />

        <div className="relative mx-auto max-w-5xl px-6 text-center lg:px-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-4 py-1.5 text-xs font-semibold text-purple-300 mb-8 backdrop-blur-md">
            <Sparkles className="h-4 w-4 text-purple-400" />
            ApplyMate AI 2.0 is Live &bull; Powered by Gemini 1.5 Pro
          </div>

          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-6xl md:text-7xl leading-[1.1] mb-6">
            Apply Smarter. <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-purple-400 via-indigo-300 to-purple-500 bg-clip-text text-transparent">
              Land Faster.
            </span>
          </h1>

          <p className="mx-auto max-w-2xl text-base sm:text-lg text-slate-400 mb-10 leading-relaxed">
            The autonomous career copilot that scores resumes against ATS engines, discovers matching high-salary openings, generates bespoke applications, and coaches you to interview mastery.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/auth/register" className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto text-base px-8 h-12 shadow-xl shadow-purple-500/25">
                Get Started Free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <a href="#how-it-works" className="w-full sm:w-auto">
              <Button variant="outline" size="lg" className="w-full sm:w-auto text-base px-6 h-12 border-slate-700 bg-slate-900/60 hover:bg-slate-800">
                <Play className="mr-2 h-4 w-4 text-purple-400 fill-purple-400" />
                Watch How It Works
              </Button>
            </a>
          </div>

          {/* Social Proof metrics */}
          <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-6 border-t border-slate-800/80 pt-8 max-w-3xl mx-auto">
            <div>
              <div className="text-2xl font-bold text-white">94%</div>
              <div className="text-xs text-slate-500 mt-1">ATS Pass Rate</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">3.4x</div>
              <div className="text-xs text-slate-500 mt-1">More Interviews</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">15+ hrs</div>
              <div className="text-xs text-slate-500 mt-1">Saved Per Week</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">50,000+</div>
              <div className="text-xs text-slate-500 mt-1">Jobs Matched</div>
            </div>
          </div>

          {/* Product Mockup Preview */}
          <div className="mt-16 rounded-2xl border border-slate-800/80 bg-slate-900/50 p-2 sm:p-4 shadow-2xl backdrop-blur-xl ring-1 ring-white/10">
            <div className="rounded-xl overflow-hidden border border-slate-800 bg-slate-950 p-4 sm:p-8 text-left">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-rose-500/80" />
                  <div className="h-3 w-3 rounded-full bg-amber-500/80" />
                  <div className="h-3 w-3 rounded-full bg-emerald-500/80" />
                  <span className="text-xs text-slate-500 ml-2 font-mono">applymate-dashboard.app</span>
                </div>
                <Badge variant="secondary" className="bg-purple-900/30 text-purple-300 border-purple-500/30">
                  <Sparkles className="h-3 w-3 mr-1" /> AI Engine Active
                </Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/70">
                  <div className="text-xs text-slate-400">Target Match Score</div>
                  <div className="text-3xl font-extrabold text-emerald-400 mt-1">92%</div>
                  <div className="text-xs text-emerald-500/80 mt-1">&uarr; Senior Full Stack Engineer</div>
                </div>
                <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/70">
                  <div className="text-xs text-slate-400">Applications in Pipeline</div>
                  <div className="text-3xl font-extrabold text-white mt-1">24</div>
                  <div className="text-xs text-purple-400 mt-1">4 Interviews this week</div>
                </div>
                <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/70">
                  <div className="text-xs text-slate-400">AI Tailored Resumes</div>
                  <div className="text-3xl font-extrabold text-indigo-400 mt-1">12</div>
                  <div className="text-xs text-indigo-400 mt-1">100% ATS Optimized</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 border-t border-slate-800/80 bg-slate-950/40 relative">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <Badge variant="outline" className="border-purple-500/30 text-purple-400 mb-3">
              Full Suite Capabilities
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Engineered for the Modern Tech Professional
            </h2>
            <p className="mt-3 text-sm text-slate-400">
              Everything you need to navigate competitive recruitment pipelines with uncompromising quality.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => {
              const Icon = feature.icon
              return (
                <Card
                  key={idx}
                  className="group relative border-slate-800/80 bg-slate-900/40 p-6 hover:border-purple-500/40 hover:bg-slate-900/80 transition-all duration-300"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 text-purple-400 mb-5 group-hover:scale-110 group-hover:bg-purple-500/20 transition-all">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-base font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-xs leading-relaxed text-slate-400">{feature.description}</p>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 border-t border-slate-800/80 relative">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <Badge variant="outline" className="border-indigo-500/30 text-indigo-400 mb-3">
              Frictionless Process
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              How ApplyMate AI Works
            </h2>
            <p className="mt-3 text-sm text-slate-400">
              From zero to scheduled technical interviews in three streamlined phases.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, idx) => (
              <div
                key={idx}
                className="relative rounded-2xl border border-slate-800 bg-slate-900/40 p-8 backdrop-blur-sm"
              >
                <div className="text-4xl font-extrabold text-purple-500/30 mb-4 font-mono">
                  {step.number}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-xs leading-relaxed text-slate-400">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 border-t border-slate-800/80 bg-slate-950/60 relative">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <Badge variant="outline" className="border-purple-500/30 text-purple-400 mb-3">
              Simple, Transparent Pricing
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Invest in Your Career Acceleration
            </h2>
            <p className="mt-3 text-sm text-slate-400">
              Choose the tier that matches your current job search ambition. Cancel anytime.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {plans.map((plan, idx) => (
              <div
                key={idx}
                className={`relative flex flex-col justify-between rounded-3xl border p-8 transition-all duration-300 ${
                  plan.highlighted
                    ? 'border-purple-500 bg-gradient-to-b from-purple-950/40 via-slate-900/90 to-slate-900 shadow-2xl shadow-purple-500/20 ring-1 ring-purple-500'
                    : 'border-slate-800 bg-slate-900/40 hover:border-slate-700'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                    <span className="rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 px-3.5 py-1 text-[11px] font-bold text-white shadow-md uppercase tracking-wider">
                      Most Popular
                    </span>
                  </div>
                )}

                <div>
                  <h3 className="text-lg font-bold text-white">{plan.name}</h3>
                  <p className="text-xs text-slate-400 mt-1 min-h-[36px]">{plan.description}</p>

                  <div className="mt-6 flex items-baseline gap-1">
                    <span className="text-4xl font-extrabold text-white">{plan.price}</span>
                    <span className="text-xs text-slate-400">/{plan.period}</span>
                  </div>

                  <div className="mt-8 space-y-3">
                    {plan.features.map((feat, fidx) => (
                      <div key={fidx} className="flex items-center gap-2.5 text-xs text-slate-300">
                        <Check className="h-4 w-4 text-purple-400 shrink-0" />
                        <span>{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-10">
                  <Link to="/auth/register">
                    <Button
                      variant={plan.highlighted ? 'default' : 'outline'}
                      className="w-full"
                    >
                      {plan.cta}
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 border-t border-slate-800/80">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 mb-3">
              Success Stories
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Trusted by Ambitious Engineers
            </h2>
            <p className="mt-3 text-sm text-slate-400">
              See how job seekers use ApplyMate AI to secure career-defining offers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((test, idx) => (
              <Card key={idx} className="border-slate-800 bg-slate-900/40 p-6 flex flex-col justify-between">
                <div>
                  <div className="flex gap-1 text-amber-400 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-amber-400" />
                    ))}
                  </div>
                  <p className="text-xs leading-relaxed text-slate-300 italic mb-6">
                    &ldquo;{test.quote}&rdquo;
                  </p>
                </div>

                <div className="flex items-center gap-3 border-t border-slate-800/60 pt-4">
                  <img
                    src={test.avatar}
                    alt={test.name}
                    className="h-10 w-10 rounded-full object-cover ring-2 ring-purple-500/30"
                  />
                  <div>
                    <h4 className="text-xs font-semibold text-white">{test.name}</h4>
                    <p className="text-[11px] text-slate-400">{test.role}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="mx-auto max-w-5xl px-6 lg:px-8">
          <div className="relative rounded-3xl border border-purple-500/30 bg-gradient-to-r from-purple-950/60 via-slate-900 to-indigo-950/60 p-10 md:p-16 text-center shadow-2xl backdrop-blur-xl overflow-hidden">
            <div className="relative z-10">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl mb-4">
                Ready to Supercharge Your Job Search?
              </h2>
              <p className="mx-auto max-w-xl text-sm text-slate-300 mb-8 leading-relaxed">
                Join thousands of candidates who have streamlined their applications, bypassed ATS filters, and landed higher-paying offers with ApplyMate AI.
              </p>
              <Link to="/auth/register">
                <Button size="lg" className="px-8 shadow-xl shadow-purple-500/30">
                  Create Your Free Account
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-12">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-purple-600">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="text-base font-bold text-white">ApplyMate AI</span>
            </div>

            <p className="text-xs text-slate-500 text-center md:text-left">
              &copy; {new Date().getFullYear()} ApplyMate AI. All rights reserved.
            </p>

            <div className="flex items-center gap-6 text-xs text-slate-400">
              <a href="#" className="hover:text-white transition-colors">
                Privacy Policy
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Terms of Service
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Contact Support
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
