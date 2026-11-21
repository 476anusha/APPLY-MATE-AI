import api from './api'
import { AIConversation, AIMessage, CoverLetter } from '@/types'

export interface ChatResponse {
  message: AIMessage
  conversation_id: string
}

export interface CoverLetterResponse {
  id?: string
  content: string
  title: string
}

export interface TailorResumeResponse {
  tailored_resume: Record<string, unknown>
  diff_summary: string[]
  match_score_before: number
  match_score_after: number
  suggestions: string[]
}

export interface InterviewPrepResponse {
  job_title?: string
  technical_questions: Array<{ question: string; answer: string; tip?: string }>
  behavioral_questions: Array<{ question: string; answer: string; tip?: string }>
  project_questions?: Array<{ question: string; answer: string; tip?: string }>
  coding_challenges?: Array<{ title: string; description: string; solution: string }>
}

export const aiService = {
  async getConversations(): Promise<AIConversation[]> {
    const response = await api.get<AIConversation[]>('/ai/conversations')
    return response.data
  },

  async createConversation(title?: string): Promise<AIConversation> {
    const response = await api.post<AIConversation>('/ai/conversations', { title })
    return response.data
  },

  async getMessages(conversationId: string): Promise<AIMessage[]> {
    const response = await api.get<AIMessage[]>(`/ai/conversations/${conversationId}/messages`)
    return response.data
  },

  /**
   * Send a message. When conversationId is empty/null, use /ai/chat which
   * auto-creates a conversation. Otherwise send to the specific conversation.
   */
  async sendMessage(conversationId: string | null, message: string): Promise<ChatResponse> {
    if (!conversationId) {
      // No active conversation — use /ai/chat which auto-creates one
      const response = await api.post<ChatResponse>('/ai/chat', {
        message,
        conversation_id: null,
      })
      return response.data
    }
    // Existing conversation
    const response = await api.post<ChatResponse>(
      `/ai/conversations/${conversationId}/messages`,
      { message }
    )
    return response.data
  },

  async generateCoverLetter(
    jobId: string,
    resumeId?: string,
    tone: 'professional' | 'enthusiastic' | 'concise' | 'creative' = 'professional'
  ): Promise<CoverLetter> {
    const response = await api.post<CoverLetter>('/ai/cover-letter', {
      job_id: jobId,
      resume_id: resumeId,
      tone,
    })
    return response.data
  },

  async tailorResume(jobId: string, resumeId: string): Promise<TailorResumeResponse> {
    const response = await api.post<TailorResumeResponse>('/ai/tailor-resume', {
      job_id: jobId,
      resume_id: resumeId,
    })
    return response.data
  },

  async getInterviewPrep(jobId: string): Promise<InterviewPrepResponse> {
    const response = await api.post<InterviewPrepResponse>(`/ai/interview-prep/${jobId}`)
    return response.data
  },
}
