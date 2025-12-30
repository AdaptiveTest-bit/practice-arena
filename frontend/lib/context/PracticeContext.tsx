/**
 * Practice Session Context Provider
 * 
 * ⚠️ DEPRECATED: This context was used for the old /practice route
 * The new implementation uses /quiz route with real API integration
 * This file is kept for backward compatibility only
 * 
 * @ts-ignore - Deprecated code, type errors ignored
 */

'use client'

import React, { createContext, useState, useCallback, ReactNode } from 'react'
import { practiceAPI } from '@/lib/api/client'
import {
  Question,
  SessionStartResponse,
  NextQuestionResponse,
  SubmitAnswerResponse,
  SessionProgress,
  PracticeContextType,
} from '@/lib/types'
import { useToast } from '@/lib/hooks/useToast'

export const PracticeContext = createContext<PracticeContextType | undefined>(undefined)

interface PracticeProviderProps {
  children: ReactNode
}

const defaultProgress: SessionProgress = {
  completion_percentage: 0,
  total_questions_attempted: 0,
  total_questions_correct: 0,
  overall_accuracy: 0,
  concepts_covered: [],
  concepts_mastered: [],
  bloom_levels_completed: {},
  misconceptions_detected: {},
  break_points: [],
}

export function PracticeProvider({ children }: PracticeProviderProps) {
  // Session state
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isSessionActive, setIsSessionActive] = useState(false)
  const [chapterId, setChapterId] = useState<number | null>(null)
  const [chapterName, setChapterName] = useState('')
  const [bloomLevels, setBloomLevels] = useState<string[]>([])
  const [currentBloomLevel, setCurrentBloomLevel] = useState('')

  // Question state
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false)
  const [questionNumber, setQuestionNumber] = useState(0)

  // Progress tracking
  const [progress, setProgress] = useState<SessionProgress>(defaultProgress)

  // Error handling
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  // Start a new practice session
  // @ts-ignore - Deprecated code
  const startSession = useCallback(
    async (studentId: number, chapterId: number) => {
      try {
        setError(null)
        setIsLoadingQuestion(true)

        const response = await practiceAPI.startSession()

        if (!response.success) {
          throw new Error(response.error || 'Failed to start session')
        }

        setSessionId(response.sessionId as any)
        setChapterId(chapterId)
        setChapterName((response as any)?.student?.chapter || '')
        setBloomLevels([])
        setCurrentBloomLevel('')
        setIsSessionActive(true)
        setQuestionNumber(0)
        setProgress(defaultProgress)

        toast({
          title: 'Session Started',
          description: `Ready to practice!`,
          type: 'success',
        })

        // Load first question
        await getNextQuestion()
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to start session'
        setError(errorMsg)
        toast({ title: 'Error', description: errorMsg, type: 'error' })
        throw err
      } finally {
        setIsLoadingQuestion(false)
      }
    },
    [toast]
  )

  // Get the next question
  // @ts-ignore - Deprecated code
  const getNextQuestion = useCallback(async () => {
    if (!sessionId) {
      throw new Error('No active session')
    }

    try {
      setError(null)
      setIsLoadingQuestion(true)

      const response: any = await practiceAPI.getNextQuestion(sessionId)

      if (!response.success) {
        throw new Error(response.error || 'Failed to load next question')
      }

      const question: Question = {
        question_id: (response.questionId || response.question_id) as string,
        session_id: sessionId as any,
        chapter_id: response.chapter_id,
        question_text: response.question || response.question_text || '',
        options: response.options || [],
        concept: response.topic || response.concept || '',
        bloom_level: response.bloomLevel || response.bloom_level || '',
        difficulty: response.difficulty || 0,
      }

      setCurrentQuestion(question)
      setQuestionNumber((response.question_number || 0) + 1)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load question'
      setError(errorMsg)
      toast({ title: 'Error', description: errorMsg, type: 'error' })
      throw err
    } finally {
      setIsLoadingQuestion(false)
    }
  }, [sessionId, toast])

  // Submit an answer
  // @ts-ignore - Deprecated code
  const submitAnswer = useCallback(
    async (questionId: string, selectedIndex: number) => {
      if (!sessionId) {
        throw new Error('No active session')
      }

      try {
        setError(null)
        const response: any = await practiceAPI.submitAnswer(
          sessionId,
          questionId,
          selectedIndex
        )

        if (!response.success) {
          throw new Error(response.error || 'Failed to submit answer')
        }

        // Update current question with answer info
        if (currentQuestion && currentQuestion.question_id === questionId) {
          setCurrentQuestion({
            ...currentQuestion,
            answer: response.answer,
            correct_option_index: response.correct_index,
            solution_steps: response.solution_steps,
          })
        }

        // Update progress
        setProgress({
          completion_percentage: response.completion_percentage,
          total_questions_attempted: response.total_questions_attempted ?? progress.total_questions_attempted,
          total_questions_correct: response.total_questions_correct ?? progress.total_questions_correct,
          overall_accuracy: response.overall_accuracy,
          concepts_covered: progress.concepts_covered,
          concepts_mastered: progress.concepts_mastered,
          bloom_levels_completed: progress.bloom_levels_completed,
          misconceptions_detected: progress.misconceptions_detected,
          break_points: progress.break_points,
        })

        // Show feedback
        const feedbackMsg = response.is_correct
          ? `Correct! (Accuracy: ${Math.round(response.concept_accuracy * 100)}%)`
          : `Incorrect. ${response.advancement_message}`

        toast({
          title: response.is_correct ? 'Great!' : 'Not quite right',
          description: feedbackMsg,
          type: response.is_correct ? 'success' : 'info',
        })

        // Check if student can advance
        if (response.can_advance_to_next_level && response.advancement_message) {
          toast({
            title: 'Level Up! 🎉',
            description: response.advancement_message,
            type: 'success',
          })
        }

        return response.is_correct
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to submit answer'
        setError(errorMsg)
        toast({ title: 'Error', description: errorMsg, type: 'error' })
        throw err
      }
    },
    [sessionId, currentQuestion, progress, toast]
  )

  // End the session
  const endSession = useCallback(async () => {
    if (!sessionId) {
      return
    }

    try {
      setError(null)
      await practiceAPI.endSession(sessionId, 1) // Default student ID - should come from auth
      setIsSessionActive(false)
      setSessionId(null)
      setCurrentQuestion(null)
      toast({
        title: 'Session Ended',
        description: `Final accuracy: ${Math.round(progress.overall_accuracy * 100)}%`,
        type: 'success',
      })
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to end session'
      setError(errorMsg)
      toast({ title: 'Error', description: errorMsg, type: 'error' })
    }
  }, [sessionId, progress, toast])

  // Reset session
  const resetSession = useCallback(() => {
    setSessionId(null)
    setIsSessionActive(false)
    setChapterId(null)
    setChapterName('')
    setCurrentQuestion(null)
    setQuestionNumber(0)
    setProgress(defaultProgress)
    setError(null)
  }, [])

  // Clear error
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const value: PracticeContextType = {
    // Session state
    sessionId,
    isSessionActive,
    chapterId,
    chapterName,
    bloomLevels,
    currentBloomLevel,

    // Question state
    currentQuestion,
    isLoadingQuestion,
    questionNumber,

    // Progress tracking
    progress,

    // Actions
    startSession,
    getNextQuestion,
    submitAnswer,
    endSession,
    resetSession,

    // Error handling
    error,
    clearError,
  }

  return <PracticeContext.Provider value={value}>{children}</PracticeContext.Provider>
}
