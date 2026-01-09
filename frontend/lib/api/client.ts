/**
 * API Client for Practice Engine Integration
 */

import axios, { AxiosInstance } from 'axios'
import {
  SessionStartResponse,
  NextQuestionResponse,
  SubmitAnswerResponse,
  SubmitAnswerRequest,
} from '@/lib/types'

export interface SessionCompletionResponse {
  success: boolean
  isComplete: boolean
  completionAnalysis: {
    difficulty_mastery: Record<number, { accuracy: number; attempts: number; mastered: boolean; status: string }>
    bloom_mastery: Record<string, { accuracy: number; attempts: number; mastered: boolean; status: string }>
    concept_mastery: Record<string, { accuracy: number; attempts: number; mastered: boolean; status: string }>
    problem_misconceptions: Array<{ type: string; count: number }>
  }
  sessionSummary: {
    questions_answered: number
    accuracy_overall: number
    concepts_mastered: string[]
    concepts_in_progress: string[]
    time_spent_minutes: number
  }
  nextRecommendation: string
}

class PracticeAPIClient {
  private client: AxiosInstance

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log('[API] Response:', response.config?.url, response.status)
        return response
      },
      (error) => {
        let errorMessage = 'Unknown error'
        let status = null
        let isNetwork = false

        if (error.response) {
          // Server responded with error status
          status = error.response.status
          errorMessage = error.response.data?.error || error.response.statusText || error.message
        } else if (error.request) {
          // Request made but no response
          isNetwork = true
          errorMessage = `Network error - Cannot connect to ${baseURL}. Is the backend server running?`
        } else {
          // Error in request setup
          errorMessage = error.message
        }

        const errorInfo = {
          message: errorMessage,
          status,
          code: error.code,
          isNetwork,
          url: error.config?.url,
          baseURL,
        }

        console.error('[API] Error:', errorMessage, errorInfo)
        
        // Log to window for debugging
        if (typeof window !== 'undefined') {
          (window as any).__lastApiError = errorInfo
        }
        
        throw new Error(errorMessage)
      }
    )

    // Log configuration in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[PracticeAPIClient] Configured with baseURL:', baseURL)
    }
  }

  /**
   * Start a new practice session
   */
  async startSession(): Promise<SessionStartResponse> {
    const response = await this.client.post<any>(
      '/api/practice/session/start',
      {
        student_id: 1,
        chapter_id: 1,
        class_level: 5,
        subject: 'Mathematics',
      }
    )
    
    // Transform snake_case to camelCase
    return {
      success: response.data.success,
      sessionId: String(response.data.session_id),
    }
  }

  /**
   * Get the next question for the student
   */
  async getNextQuestion(
    sessionId: string,
    chapter?: string
  ): Promise<NextQuestionResponse> {
    const response = await this.client.post<any>(
      `/api/practice/session/${sessionId}/next-question`,
      {
        ...(chapter && { chapter })
      }
    )
    
    // Transform snake_case to camelCase
    const data = response.data
    return {
      success: data.success,
      questionId: data.question_id,
      chapter: chapter || 'unknown',
      chapterName: chapter || 'Chapter',
      topic: data.concept,
      logicalTrap: '',
      dataRepresentation: '',
      question: data.question_text,
      options: data.options || [],
      correctOptionIndex: undefined,
    }
  }

  /**
   * Submit an answer and get feedback
   */
  async submitAnswer(
    sessionId: string,
    questionId: string,
    selectedIndex: number
  ): Promise<SubmitAnswerResponse> {
    const response = await this.client.post<any>(
      `/api/practice/session/${sessionId}/submit-answer`,
      {
        question_id: questionId,
        selected_index: selectedIndex
      }
    )
    
    // Transform snake_case to camelCase
    const data = response.data
    return {
      success: data.success,
      isCorrect: data.is_correct,
      correctIndex: data.correct_index || 0,
      solutionSteps: data.solution_steps || [],
      answer: data.answer || '',
      sessionId: String(data.session_id),
      questionId: data.question_id,
    }
  }

  /**
   * Check if session is complete (mastery achieved)
   */
  async checkSessionCompletion(sessionId: string): Promise<SessionCompletionResponse> {
    const response = await this.client.get<SessionCompletionResponse>(
      `/api/practice/session/${sessionId}/check-completion`
    )
    return response.data
  }

  /**
   * Get session progress
   */
  async getSessionProgress(sessionId: number): Promise<SessionStartResponse> {
    const response = await this.client.get<SessionStartResponse>(
      `/api/practice/session/${sessionId}/stats`
    )
    return response.data
  }

  /**
   * End the current session
   */
  async endSession(sessionId: string | number, studentId: number): Promise<{ success: boolean }> {
    const response = await this.client.delete(`/api/practice/session/${sessionId}`)
    return { success: true }
  }
}

export const practiceAPI = new PracticeAPIClient()
