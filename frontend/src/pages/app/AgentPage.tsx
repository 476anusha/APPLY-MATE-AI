import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Bot, Send, Plus, Loader2, Briefcase, FileText, Sparkles, MessageSquare } from 'lucide-react'
import { aiService } from '@/services/ai.service'
import { formatRelativeDate } from '@/utils/formatters'
import type { AIConversation, AIMessage } from '@/types'

const SUGGESTED_PROMPTS = [
  'Find Python developer jobs for freshers',
  'Analyze my resume and suggest improvements',
  'Generate a cover letter for a React developer role',
  'Prepare me for a technical interview',
  'What skills should I learn to get hired faster?',
  'Show me remote full-stack developer jobs',
]

export default function AgentPage() {
  const [activeConvId, setActiveConvId] = useState<string | null>(null)
  const [messages, setMessages] = useState<AIMessage[]>([])
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const { data: conversations, refetch: refetchConvs } = useQuery({
    queryKey: ['ai-conversations'],
    queryFn: aiService.getConversations,
  })

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startNewChat = () => {
    setActiveConvId(null)
    setMessages([])
  }

  const loadConversation = async (conv: AIConversation) => {
    setActiveConvId(conv.id)
    try {
      const msgs = await aiService.getMessages(conv.id)
      setMessages(msgs)
    } catch { setMessages([]) }
  }

  const sendMessage = async (text: string) => {
    if (!text.trim() || isSending) return
    const userMsg: AIMessage = { id: Date.now().toString(), role: 'user', content: text, created_at: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsSending(true)
    try {
      const res = await aiService.sendMessage(activeConvId, text)
      if (!activeConvId && res.conversation_id) { setActiveConvId(res.conversation_id); refetchConvs() }
      const asstMsg: AIMessage = { id: res.message.id, role: 'assistant', content: res.message.content, created_at: new Date().toISOString() }
      setMessages(prev => [...prev, asstMsg])
    } catch {
      setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', content: 'Sorry, I encountered an error. Please try again.', created_at: new Date().toISOString() }])
    } finally { setIsSending(false) }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input) }
  }

  return (
    <div className="flex h-[calc(100vh-10rem)] gap-0 -mx-4 md:-mx-8 overflow-hidden">
      {/* Left sidebar — conversations */}
      <div className="w-56 flex-shrink-0 border-r border-slate-800 flex flex-col bg-slate-900/50 hidden md:flex">
        <div className="p-3 border-b border-slate-800">
          <button onClick={startNewChat} className="w-full flex items-center gap-2 px-3 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-lg transition-colors">
            <Plus className="w-4 h-4" /> New Chat
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations?.map(conv => (
            <button key={conv.id} onClick={() => loadConversation(conv)} className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors ${activeConvId === conv.id ? 'bg-purple-600/20 text-purple-300' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}>
              <p className="truncate font-medium">{conv.title}</p>
              <p className="text-slate-500 mt-0.5">{formatRelativeDate(conv.created_at)}</p>
            </button>
          ))}
          {!conversations?.length && <p className="text-xs text-slate-600 text-center pt-4">No conversations yet</p>}
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat header */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800 bg-slate-900/50">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">ApplyMate AI Agent</p>
            <p className="text-xs text-green-400">● Online</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center mb-4 border border-purple-500/20">
                <Sparkles className="w-8 h-8 text-purple-400" />
              </div>
              <h2 className="text-lg font-bold text-white mb-2">Your AI Career Assistant</h2>
              <p className="text-slate-400 text-sm mb-6 max-w-xs">Ask me anything about jobs, resumes, interviews, or career advice.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-sm">
                {SUGGESTED_PROMPTS.map(prompt => (
                  <button key={prompt} onClick={() => sendMessage(prompt)} className="text-left px-3 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-purple-500/50 rounded-lg text-xs text-slate-300 transition-all">
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map(msg => (
              <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-purple-600' : 'bg-gradient-to-br from-purple-500 to-blue-500'}`}>
                  {msg.role === 'user' ? <span className="text-xs font-bold text-white">U</span> : <Bot className="w-4 h-4 text-white" />}
                </div>
                <div className={`max-w-[75%] rounded-xl px-4 py-2.5 text-sm ${msg.role === 'user' ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-200'}`}>
                  <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                </div>
              </div>
            ))
          )}
          {isSending && (
            <div className="flex gap-3">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-slate-800 rounded-xl px-4 py-3 flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="p-3 border-t border-slate-800 bg-slate-900/50">
          <div className="flex gap-2 items-end bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 focus-within:border-purple-500 transition-colors">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything… (Enter to send, Shift+Enter for new line)"
              rows={1}
              className="flex-1 bg-transparent text-white text-sm resize-none focus:outline-none placeholder:text-slate-500 max-h-32"
              style={{ minHeight: '24px' }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || isSending}
              className="flex-shrink-0 w-8 h-8 bg-purple-600 hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-lg flex items-center justify-center transition-colors"
            >
              {isSending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            </button>
          </div>
          <p className="text-xs text-slate-600 text-center mt-1.5">AI responses may be inaccurate. Always verify important information.</p>
        </div>
      </div>

      {/* Right panel — context */}
      <div className="w-56 flex-shrink-0 border-l border-slate-800 hidden lg:flex flex-col bg-slate-900/50 p-4 gap-4">
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Quick Actions</p>
          <div className="space-y-1.5">
            {[
              { icon: <FileText className="w-3.5 h-3.5" />, label: 'Analyze Resume', prompt: 'Analyze my resume and give me improvement suggestions' },
              { icon: <Briefcase className="w-3.5 h-3.5" />, label: 'Find Jobs', prompt: 'Find the best software developer jobs matching my skills' },
              { icon: <MessageSquare className="w-3.5 h-3.5" />, label: 'Interview Prep', prompt: 'Help me prepare for a software engineering interview' },
            ].map(a => (
              <button key={a.label} onClick={() => sendMessage(a.prompt)} className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-colors text-left">
                {a.icon} {a.label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Tips</p>
          <ul className="space-y-1.5 text-xs text-slate-500">
            <li>• Upload a resume for personalized advice</li>
            <li>• Add Gemini API key for full AI power</li>
            <li>• Ask me to track applications</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
