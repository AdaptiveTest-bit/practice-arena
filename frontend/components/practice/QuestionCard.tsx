/**
 * Question Card Component
 * Displays the current question with metadata
 */

'use client'

import React from 'react'
import { Question } from '@/lib/types'

interface QuestionCardProps {
  question: Question | null
  questionNumber: number
  isLoading?: boolean
}

export function QuestionCard({ question, questionNumber, isLoading }: QuestionCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-10 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!question) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-500">No question loaded. Start a session to begin.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      {/* Metadata */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div className="flex gap-4 text-sm">
          <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-blue-800">
            {question.concept}
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full bg-purple-100 text-purple-800">
            {question.bloom_level}
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full bg-amber-100 text-amber-800">
            Difficulty: {question.difficulty}
          </span>
        </div>
        <span className="text-xs font-semibold text-gray-500">
          Question {questionNumber}
        </span>
      </div>

      {/* Question Text */}
      <h2 className="text-2xl font-bold text-gray-900 mb-8 leading-relaxed">
        {question.question_text}
      </h2>

      {/* Options */}
      <div className="space-y-3" id="question-options">
        {question.options.map((option, index) => (
          <label
            key={index}
            className="flex items-start p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-all"
          >
            <input
              type="radio"
              name="answer"
              value={index}
              className="mt-1 w-5 h-5 text-blue-600"
              data-option-index={index}
            />
            <span className="ml-4 text-lg text-gray-700">{option}</span>
          </label>
        ))}
      </div>

      {/* Solution Display (if available) */}
      {question.answer && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
            <p className="text-sm font-semibold text-green-900 mb-2">Correct Answer:</p>
            <p className="text-gray-700 mb-3">{question.answer}</p>
            
            {question.solution_steps && question.solution_steps.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-green-900 mb-2">Solution Steps:</p>
                <ol className="list-decimal list-inside space-y-1">
                  {question.solution_steps.map((step, idx) => (
                    <li key={idx} className="text-sm text-gray-700">
                      {step}
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
