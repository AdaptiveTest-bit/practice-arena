/**
 * API Types for Practice Engine Integration
 */

export interface Question {
  question_id: string
  session_id: number
  chapter_id?: number
  question_text: string
  options: string[]
  concept: string
  bloom_level: string
  difficulty: number
  correct_option_index?: number
  answer?: string
  solution_steps?: string[]
}

export interface SessionStartResponse {
  success: boolean
  sessionId: string
  error?: string
}

export interface NextQuestionResponse {
  success: boolean
  questionId: string
  chapter: string
  chapterName: string
  topic: string
  logicalTrap: string
  dataRepresentation: string
  question: string
  options: string[]
  correctOptionIndex?: number
  error?: string
}

export interface SubmitAnswerResponse {
  success: boolean
  isCorrect: boolean
  correctIndex: number
  solutionSteps: string[]
  answer: string
  // Optional fields that might come from adaptive service
  sessionId?: string
  questionId?: string
}

export interface SessionProgress {
  completion_percentage: number
  total_questions_attempted: number
  total_questions_correct: number
  overall_accuracy: number
  concepts_covered: string[]
  concepts_mastered: string[]
  bloom_levels_completed: Record<string, { status: string; accuracy: number }>
  misconceptions_detected: Record<string, number>
  break_points: BreakPoint[]
}

export interface BreakPoint {
  concept: string
  bloom_level: string
  accuracy: number
  total_questions: number
  correct_answers: number
  timestamp?: string
}

export interface PracticeContextType {
  // Session state
  sessionId: string | null
  isSessionActive: boolean
  chapterId: number | null
  chapterName: string
  
  // Question state
  currentQuestion: Question | null
  isLoadingQuestion: boolean
  questionNumber: number
  
  // Progress tracking
  progress: SessionProgress | null
  bloomLevels: string[]
  currentBloomLevel: string
  
  // Actions
  startSession: (studentId: number, chapterId: number) => Promise<void>
  getNextQuestion: () => Promise<void>
  submitAnswer: (questionId: string, selectedIndex: number, timeTaken?: number) => Promise<boolean>
  endSession: () => Promise<void>
  resetSession: () => void
  
  // Error handling
  error: string | null
  clearError: () => void
}

export interface SubmitAnswerRequest {
  question_id: string
  selected_index: number
  time_taken_seconds?: number
}
