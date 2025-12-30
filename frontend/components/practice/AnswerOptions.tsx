/**
 * Answer Options Component
 * Handles answer submission with visual feedback
 */

'use client'

import React, { useState, useRef } from 'react'

interface AnswerOptionsProps {
  questionId: string
  onSubmit: (selectedIndex: number, timeTaken: number) => Promise<boolean>
  isSubmitting?: boolean
  isAnswered?: boolean
  correctIndex?: number
}

export function AnswerOptions({
  questionId,
  onSubmit,
  isSubmitting = false,
  isAnswered = false,
  correctIndex,
}: AnswerOptionsProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const startTimeRef = useRef(Date.now())

  const handleSubmit = async () => {
    if (selectedIndex === null) {
      alert('Please select an option before submitting')
      return
    }

    const timeTaken = Math.floor((Date.now() - startTimeRef.current) / 1000)
    await onSubmit(selectedIndex, timeTaken)
  }

  const handleSelectOption = (index: number) => {
    if (!isAnswered && !isSubmitting) {
      setSelectedIndex(index)
    }
  }

  return (
    <div className="space-y-4 mt-8">
      {/* Selected Option Indicator */}
      {selectedIndex !== null && !isAnswered && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
          Selected: Option {String.fromCharCode(65 + selectedIndex)}
        </div>
      )}

      {/* Answer Feedback */}
      {isAnswered && correctIndex !== undefined && (
        <div
          className={`p-4 rounded-lg border-l-4 ${
            selectedIndex === correctIndex
              ? 'bg-green-50 border-green-500 text-green-900'
              : 'bg-red-50 border-red-500 text-red-900'
          }`}
        >
          {selectedIndex === correctIndex ? (
            <p className="font-semibold">✓ Correct!</p>
          ) : (
            <div>
              <p className="font-semibold">✗ Incorrect</p>
              <p className="text-sm mt-1">
                The correct answer is Option {String.fromCharCode(65 + correctIndex)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Submit Button */}
      {!isAnswered && (
        <button
          onClick={handleSubmit}
          disabled={isSubmitting || selectedIndex === null}
          className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all ${
            isSubmitting || selectedIndex === null
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 active:scale-95'
          }`}
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Submitting...
            </span>
          ) : (
            'Submit Answer'
          )}
        </button>
      )}

      {/* Next Question Button */}
      {isAnswered && (
        <button
          onClick={() => window.location.reload()}
          className="w-full py-3 px-6 rounded-lg font-semibold text-white bg-green-600 hover:bg-green-700 active:scale-95 transition-all"
        >
          Next Question
        </button>
      )}
    </div>
  )
}
