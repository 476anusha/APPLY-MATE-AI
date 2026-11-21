import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Loader2, ChevronDown, ChevronRight, Lightbulb, Mic, MessageSquare, Code, Briefcase } from 'lucide-react'
import { aiService } from '@/services/ai.service'

const DEMO_JOBS = [
  { id: 'demo-001', title: 'Python Backend Developer', company: 'TechCorp Solutions' },
  { id: 'demo-002', title: 'React Frontend Developer', company: 'Innovate Labs' },
  { id: 'demo-003', title: 'Full Stack Engineer', company: 'StartupX' },
  { id: 'demo-004', title: 'Data Scientist', company: 'Analytics Pro' },
]

export default function InterviewPage() {
  const [selectedJobId, setSelectedJobId] = useState('')
  const [prep, setPrep] = useState<any>(null)
  const [practiceMode, setPracticeMode] = useState(false)
  const [practiceIndex, setPracticeIndex] = useState(0)
  const [userAnswer, setUserAnswer] = useState('')

  const { mutate: generatePrep, isPending: isLoading } = useMutation({
    mutationFn: (jobId: string) => aiService.getInterviewPrep(jobId),
    onSuccess: (data) => setPrep(data),
  })

  const allTechnical = prep?.technical_questions ?? []
  const allBehavioral = prep?.behavioral_questions ?? []
  const allProject = prep?.project_questions ?? []
  const allCoding = prep?.coding_challenges ?? []
  const practiceQuestions = [...allTechnical, ...allBehavioral, ...allProject]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Interview Preparation</h1>
        <p className="text-slate-400 text-sm mt-1">AI-generated questions and answers tailored to your target role</p>
      </div>

      {/* Job selector */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-white">Select a Job</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {DEMO_JOBS.map(j => (
            <button
              key={j.id}
              onClick={() => setSelectedJobId(j.id)}
              className={`flex items-start gap-3 p-3 rounded-lg border text-left transition-all ${selectedJobId === j.id ? 'border-purple-500 bg-purple-500/10' : 'border-slate-700 bg-slate-800 hover:border-slate-600'}`}
            >
              <Briefcase className={`w-4 h-4 mt-0.5 flex-shrink-0 ${selectedJobId === j.id ? 'text-purple-400' : 'text-slate-500'}`} />
              <div>
                <p className={`text-sm font-medium ${selectedJobId === j.id ? 'text-purple-300' : 'text-white'}`}>{j.title}</p>
                <p className="text-xs text-slate-400">{j.company}</p>
              </div>
            </button>
          ))}
        </div>
        <button
          onClick={() => selectedJobId && generatePrep(selectedJobId)}
          disabled={!selectedJobId || isLoading}
          className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {isLoading ? <><Loader2 className="w-4 h-4 animate-spin" />Generating…</> : <><Lightbulb className="w-4 h-4" />Generate Questions</>}
        </button>
      </div>

      {prep && (
        <>
          {/* Practice mode toggle */}
          <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-xl px-5 py-4">
            <div>
              <p className="text-sm font-semibold text-white">Practice Mode</p>
              <p className="text-xs text-slate-400 mt-0.5">Answer questions one by one, then reveal the suggested answer</p>
            </div>
            <button onClick={() => { setPracticeMode(!practiceMode); setPracticeIndex(0); setUserAnswer('') }} className={`w-11 h-6 rounded-full transition-colors relative ${practiceMode ? 'bg-purple-600' : 'bg-slate-700'}`}>
              <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${practiceMode ? 'translate-x-5' : 'translate-x-0.5'}`} />
            </button>
          </div>

          {practiceMode ? (
            <PracticeMode
              questions={practiceQuestions}
              index={practiceIndex}
              onNext={() => { setPracticeIndex(i => Math.min(i + 1, practiceQuestions.length - 1)); setUserAnswer('') }}
              onPrev={() => { setPracticeIndex(i => Math.max(i - 1, 0)); setUserAnswer('') }}
              userAnswer={userAnswer}
              onAnswerChange={setUserAnswer}
            />
          ) : (
            <div className="space-y-4">
              <QSection title="Technical Questions" icon={<Code className="w-4 h-4" />} questions={allTechnical} />
              <QSection title="Behavioral Questions" icon={<MessageSquare className="w-4 h-4" />} questions={allBehavioral} />
              <QSection title="Project Questions" icon={<Mic className="w-4 h-4" />} questions={allProject} />
              <QSection title="Coding Challenges" icon={<Code className="w-4 h-4" />} questions={allCoding} />
            </div>
          )}

          {/* Tips */}
          {prep.tips && prep.tips.length > 0 && (
            <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border border-blue-800/30 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2"><Lightbulb className="w-4 h-4 text-yellow-400" /> Interview Tips</h3>
              <ul className="space-y-1.5">
                {prep.tips.map((tip: string, i: number) => (
                  <li key={i} className="text-sm text-slate-300 flex items-start gap-2"><span className="text-purple-400 mt-0.5">•</span>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {!prep && !isLoading && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Mic className="w-12 h-12 text-slate-600 mb-3" />
          <p className="text-slate-400">Select a job and generate questions to start preparing</p>
        </div>
      )}
    </div>
  )
}

function QSection({ title, icon, questions }: { title: string; icon: React.ReactNode; questions: any[] }) {
  if (!questions.length) return null
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2 text-purple-400">{icon}<span className="text-white">{title}</span></h2>
      <div className="space-y-3">
        {questions.map((q: any, i: number) => <QItem key={i} q={q} />)}
      </div>
    </div>
  )
}

function QItem({ q }: { q: any }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-slate-800 rounded-lg overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-start justify-between gap-3 px-4 py-3 text-left hover:bg-slate-800/50 transition-colors">
        <p className="text-sm text-slate-200 font-medium">{q.question}</p>
        {open ? <ChevronDown className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" /> : <ChevronRight className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />}
      </button>
      {open && (
        <div className="px-4 pb-3 border-t border-slate-800 pt-3 bg-slate-800/30">
          <p className="text-sm text-slate-300 leading-relaxed">{q.answer || q.suggested_answer}</p>
          {q.tip && (
            <p className="text-xs text-yellow-400 mt-2 flex items-start gap-1"><span>💡</span>{q.tip}</p>
          )}
        </div>
      )}
    </div>
  )
}

function PracticeMode({ questions, index, onNext, onPrev, userAnswer, onAnswerChange }: any) {
  const [revealed, setRevealed] = useState(false)
  const q = questions[index]
  if (!q) return null
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-400">Question {index + 1} of {questions.length}</span>
        <div className="flex gap-1">{questions.map((_: any, i: number) => <div key={i} className={`w-2 h-2 rounded-full ${i === index ? 'bg-purple-500' : i < index ? 'bg-green-500' : 'bg-slate-600'}`} />)}</div>
      </div>
      <p className="text-base font-medium text-white">{q.question}</p>
      <textarea
        value={userAnswer}
        onChange={e => onAnswerChange(e.target.value)}
        placeholder="Type your answer here…"
        rows={4}
        className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder:text-slate-500"
      />
      {!revealed ? (
        <button onClick={() => setRevealed(true)} className="text-sm text-purple-400 hover:text-purple-300 font-medium">Reveal suggested answer →</button>
      ) : (
        <div className="p-4 bg-green-900/20 border border-green-800/30 rounded-lg">
          <p className="text-xs font-semibold text-green-400 mb-1.5">Suggested Answer</p>
          <p className="text-sm text-slate-300">{q.answer || q.suggested_answer}</p>
        </div>
      )}
      <div className="flex gap-3">
        <button onClick={onPrev} disabled={index === 0} className="flex-1 py-2 bg-slate-800 text-slate-300 text-sm rounded-lg disabled:opacity-40">← Previous</button>
        <button onClick={() => { setRevealed(false); onNext() }} disabled={index === questions.length - 1} className="flex-1 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm rounded-lg disabled:opacity-40">Next →</button>
      </div>
    </div>
  )
}
