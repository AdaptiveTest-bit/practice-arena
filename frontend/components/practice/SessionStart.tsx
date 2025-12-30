/**
 * Session Start Component
 * Allows students to initiate a practice session
 */

'use client'

import React, { useState } from 'react'
import { usePracticeSession } from '@/lib/hooks/usePracticeSession'

export function SessionStart() {
  const { startSession, isSessionActive } = usePracticeSession()
  const [isLoading, setIsLoading] = useState(false)
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null)

  // Mock chapters - in real app, these would come from API
  const chapters = [
    { id: 1, name: 'Numbers & Place Value', level: 5 },
    { id: 2, name: 'Addition & Subtraction', level: 5 },
    { id: 3, name: 'Multiplication & Division', level: 5 },
    { id: 4, name: 'Fractions', level: 5 },
    { id: 5, name: 'Decimals', level: 5 },
  ]

  const handleStartSession = async (chapterId: number) => {
    setIsLoading(true)
    try {
      // Default student ID - in real app, this would come from auth context
      await startSession(1, chapterId)
    } catch (error) {
      console.error('Failed to start session:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isSessionActive) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Practice Arena</h1>
          <p className="text-lg text-gray-600">
            Master mathematics concepts through adaptive learning
          </p>
        </div>

        {/* Subtitle */}
        <div className="mb-8 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
          <p className="text-sm text-blue-900">
            Select a chapter to begin your personalized practice session. Questions will adapt
            to your skill level.
          </p>
        </div>

        {/* Chapter Selection */}
        <div className="space-y-3 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Choose a Chapter</h2>
          {chapters.map((chapter) => (
            <button
              key={chapter.id}
              onClick={() => setSelectedChapter(chapter.id)}
              className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                selectedChapter === chapter.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-semibold text-gray-900">{chapter.name}</p>
                  <p className="text-sm text-gray-500">Grade {chapter.level}</p>
                </div>
                {selectedChapter === chapter.id && (
                  <div className="text-blue-600">
                    <svg
                      className="w-6 h-6"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>

        {/* Start Button */}
        <button
          onClick={() => selectedChapter && handleStartSession(selectedChapter)}
          disabled={!selectedChapter || isLoading}
          className={`w-full py-4 px-6 rounded-lg font-bold text-white text-lg transition-all ${
            !selectedChapter || isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 active:scale-95'
          }`}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Starting Session...
            </span>
          ) : (
            'Start Practice Session'
          )}
        </button>

        {/* Features */}
        <div className="mt-12 grid grid-cols-3 gap-4 pt-8 border-t border-gray-200">
          <div className="text-center">
            <div className="text-2xl mb-2">🎯</div>
            <p className="text-sm font-medium text-gray-700">Adaptive</p>
            <p className="text-xs text-gray-500">Difficulty adjusts to you</p>
          </div>
          <div className="text-center">
            <div className="text-2xl mb-2">📊</div>
            <p className="text-sm font-medium text-gray-700">Tracked</p>
            <p className="text-xs text-gray-500">Progress saved</p>
          </div>
          <div className="text-center">
            <div className="text-2xl mb-2">💡</div>
            <p className="text-sm font-medium text-gray-700">Explained</p>
            <p className="text-xs text-gray-500">Learn from mistakes</p>
          </div>
        </div>
      </div>
    </div>
  )
}
