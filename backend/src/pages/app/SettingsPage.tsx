import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, User, Briefcase, CreditCard, Bell, Shield, Save } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

const TABS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'career', label: 'Career', icon: Briefcase },
  { id: 'subscription', label: 'Subscription', icon: CreditCard },
  { id: 'account', label: 'Account', icon: Shield },
]

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile')
  const { user } = useAuth()

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 text-sm mt-1">Manage your account and preferences</p>
      </div>

      {/* Tab nav */}
      <div className="flex gap-1 bg-slate-900 border border-slate-800 rounded-xl p-1">
        {TABS.map(tab => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex-1 justify-center ${activeTab === tab.id ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
            >
              <Icon className="w-4 h-4 hidden sm:block" />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Tab content */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        {activeTab === 'profile' && <ProfileTab user={user} />}
        {activeTab === 'career' && <CareerTab />}
        {activeTab === 'subscription' && <SubscriptionTab />}
        {activeTab === 'account' && <AccountTab />}
      </div>
    </div>
  )
}

function ProfileTab({ user }: { user: any }) {
  const [name, setName] = useState(user?.full_name ?? '')
  const [phone, setPhone] = useState('')
  const [location, setLocation] = useState('')
  const [bio, setBio] = useState('')
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-5">
      <h2 className="text-base font-semibold text-white">Profile Information</h2>
      {/* Avatar */}
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-xl font-bold">
          {(user?.full_name ?? 'U').split(' ').map((n: string) => n[0]).join('').slice(0, 2).toUpperCase()}
        </div>
        <button className="text-sm text-purple-400 hover:text-purple-300">Change photo</button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Full Name" value={name} onChange={setName} />
        <Field label="Email" value={user?.email ?? ''} onChange={() => {}} disabled />
        <Field label="Phone" value={phone} onChange={setPhone} placeholder="+91 9876543210" />
        <Field label="Location" value={location} onChange={setLocation} placeholder="Bangalore, India" />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1.5">Bio</label>
        <textarea value={bio} onChange={e => setBio(e.target.value)} rows={3} placeholder="A short description about yourself…" className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none" />
      </div>
      <button onClick={handleSave} className="flex items-center gap-2 px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-lg transition-colors">
        <Save className="w-4 h-4" /> {saved ? 'Saved!' : 'Save Changes'}
      </button>
    </div>
  )
}

function CareerTab() {
  const [expLevel, setExpLevel] = useState('')
  const [university, setUniversity] = useState('')
  const [gradYear, setGradYear] = useState('')
  const [skills, setSkills] = useState('')
  const [linkedin, setLinkedin] = useState('')
  const [github, setGithub] = useState('')
  const [portfolio, setPortfolio] = useState('')
  const [saved, setSaved] = useState(false)

  return (
    <div className="space-y-5">
      <h2 className="text-base font-semibold text-white">Career Information</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">Experience Level</label>
          <select value={expLevel} onChange={e => setExpLevel(e.target.value)} className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500">
            <option value="">Select level</option>
            <option value="entry">Entry Level / Fresher</option>
            <option value="mid">Mid Level (2–5 years)</option>
            <option value="senior">Senior Level (5+ years)</option>
          </select>
        </div>
        <Field label="University" value={university} onChange={setUniversity} placeholder="e.g. IIT Delhi" />
        <Field label="Graduation Year" value={gradYear} onChange={setGradYear} placeholder="e.g. 2025" />
        <Field label="Expected Salary (₹ LPA)" value={''} onChange={() => {}} placeholder="e.g. 10" />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1.5">Skills (comma-separated)</label>
        <input value={skills} onChange={e => setSkills(e.target.value)} placeholder="Python, React, SQL, AWS…" className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500" />
      </div>
      <div className="grid grid-cols-1 gap-4">
        <Field label="LinkedIn URL" value={linkedin} onChange={setLinkedin} placeholder="https://linkedin.com/in/yourname" />
        <Field label="GitHub URL" value={github} onChange={setGithub} placeholder="https://github.com/yourname" />
        <Field label="Portfolio URL" value={portfolio} onChange={setPortfolio} placeholder="https://yoursite.com" />
      </div>
      <button onClick={() => setSaved(true)} className="flex items-center gap-2 px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-lg transition-colors">
        <Save className="w-4 h-4" /> {saved ? 'Saved!' : 'Save Career Info'}
      </button>
    </div>
  )
}

function SubscriptionTab() {
  const PLANS = [
    { name: 'Free', price: '₹0/mo', features: ['2 resume uploads', '5 AI analyses/month', 'Job discovery', 'Basic tracker'], current: true },
    { name: 'Pro', price: '₹999/mo', features: ['10 resume uploads', '50 AI analyses/month', 'Resume tailoring', 'Cover letters', 'Interview prep'], recommended: true },
    { name: 'Premium', price: '₹2499/mo', features: ['Unlimited uploads', '200 AI analyses', 'Advanced agent', 'Priority support', 'Extended analytics'] },
  ]
  return (
    <div className="space-y-5">
      <h2 className="text-base font-semibold text-white">Subscription</h2>
      <div className="p-3 bg-blue-900/20 border border-blue-800/30 rounded-lg text-xs text-blue-300">
        Payment integration is in demo mode. Upgrade buttons will be functional with Stripe/Razorpay credentials.
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {PLANS.map(plan => (
          <div key={plan.name} className={`border rounded-xl p-4 space-y-3 ${plan.recommended ? 'border-purple-500 bg-purple-500/5' : 'border-slate-700 bg-slate-800/50'}`}>
            {plan.recommended && <span className="text-xs bg-purple-500 text-white px-2 py-0.5 rounded-full">Recommended</span>}
            <div>
              <h3 className="text-white font-semibold">{plan.name}</h3>
              <p className="text-purple-400 font-bold text-lg mt-0.5">{plan.price}</p>
            </div>
            <ul className="space-y-1">
              {plan.features.map(f => <li key={f} className="text-xs text-slate-400 flex items-start gap-1.5"><span className="text-green-400 mt-0.5">✓</span>{f}</li>)}
            </ul>
            {plan.current ? (
              <span className="block text-center text-xs text-green-400 font-medium py-1.5 border border-green-800 rounded-lg">Current Plan</span>
            ) : (
              <button className="w-full py-1.5 text-xs font-medium bg-purple-600/60 text-purple-200 rounded-lg cursor-not-allowed" disabled>Upgrade (Demo)</button>
            )}
          </div>
        ))}
      </div>
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">Usage This Month</h3>
        <div className="space-y-2">
          {[{ label: 'AI Analyses', used: 0, limit: 5 }, { label: 'Resume Uploads', used: 0, limit: 2 }].map(u => (
            <div key={u.label}>
              <div className="flex justify-between text-xs text-slate-400 mb-1"><span>{u.label}</span><span>{u.used} / {u.limit}</span></div>
              <div className="h-1.5 bg-slate-700 rounded-full"><div className="h-1.5 bg-purple-500 rounded-full" style={{ width: `${(u.used / u.limit) * 100}%` }} /></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function AccountTab() {
  const { logout } = useAuth()
  const [showDelete, setShowDelete] = useState(false)
  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-base font-semibold text-white mb-4">Change Password</h2>
        <div className="space-y-3">
          <Field label="Current Password" value={currentPw} onChange={setCurrentPw} type="password" />
          <Field label="New Password" value={newPw} onChange={setNewPw} type="password" />
          <button className="flex items-center gap-2 px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-lg transition-colors">
            <Save className="w-4 h-4" /> Update Password
          </button>
        </div>
      </div>
      <div className="border-t border-slate-800 pt-6">
        <h2 className="text-base font-semibold text-red-400 mb-2">Danger Zone</h2>
        <p className="text-sm text-slate-400 mb-4">Permanently delete your account and all data. This action cannot be undone.</p>
        {!showDelete ? (
          <button onClick={() => setShowDelete(true)} className="px-5 py-2 bg-red-900/30 hover:bg-red-900/50 border border-red-800 text-red-400 text-sm rounded-lg transition-colors">
            Delete Account
          </button>
        ) : (
          <div className="p-4 bg-red-900/20 border border-red-800 rounded-lg space-y-3">
            <p className="text-sm text-red-300 font-medium">Are you sure? This cannot be undone.</p>
            <div className="flex gap-2">
              <button onClick={() => setShowDelete(false)} className="px-4 py-1.5 bg-slate-800 text-slate-300 text-sm rounded-lg">Cancel</button>
              <button onClick={logout} className="px-4 py-1.5 bg-red-600 hover:bg-red-500 text-white text-sm rounded-lg">Yes, delete account</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function Field({ label, value, onChange, placeholder, disabled, type = 'text' }: { label: string; value: string; onChange: (v: string) => void; placeholder?: string; disabled?: boolean; type?: string }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-300 mb-1.5">{label}</label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
      />
    </div>
  )
}
