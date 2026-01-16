/**
 * Progress Bar Component
 * Displays student progress metrics
 */

'use client'

import React from 'react'
import { SessionProgress } from '@/lib/types'

interface ProgressBarProps {
  progress: SessionProgress | null
  title?: string
}

export function ProgressBar({ progress, title = 'Progress' }: ProgressBarProps) {
  if (!progress) {
    return null
  }

  const accuracy = Math.round(progress.overall_accuracy * 100)
  const completion = Math.round(progress.completion_percentage * 100)

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>

      {/* Completion Progress */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Session Completion</span>
          <span className="text-sm font-semibold text-gray-900">{completion}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${completion}%` }}
          ></div>
        </div>
      </div>

      {/* Accuracy Progress */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Accuracy</span>
          <span className="text-sm font-semibold text-gray-900">{accuracy}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              accuracy >= 80
                ? 'bg-green-500'
                : accuracy >= 60
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
            style={{ width: `${accuracy}%` }}
          ></div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 rounded p-4">
          <p className="text-xs text-gray-500 mb-1">Questions Attempted</p>
          <p className="text-2xl font-bold text-gray-900">
            {progress.total_questions_attempted}
          </p>
        </div>
        <div className="bg-gray-50 rounded p-4">
          <p className="text-xs text-gray-500 mb-1">Correct Answers</p>
          <p className="text-2xl font-bold text-green-600">
            {progress.total_questions_correct}
          </p>
        </div>
      </div>

      {/* Concepts Covered */}
      {progress.concepts_covered.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm font-semibold text-gray-700 mb-3">Concepts Covered</p>
          <div className="flex flex-wrap gap-2">
            {progress.concepts_covered.map((concept) => (
              <span
                key={concept}
                className="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-100 text-blue-800"
              >
                {concept}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Concepts Mastered */}
      {progress.concepts_mastered && progress.concepts_mastered.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-semibold text-gray-700 mb-3">Concepts Mastered 🎉</p>
          <div className="flex flex-wrap gap-2">
            {progress.concepts_mastered.map((concept) => (
              <span
                key={concept}
                className="inline-flex items-center px-2 py-1 rounded text-xs bg-green-100 text-green-800"
              >
                ✓ {concept}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
