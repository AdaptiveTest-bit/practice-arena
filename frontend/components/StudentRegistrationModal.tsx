'use client'

import React, { useState } from 'react'
import { useStudent } from '@/lib/studentContext'

interface StudentRegistrationModalProps {
  isOpen: boolean
  onClose: () => void
  chapter?: string
}

export function StudentRegistrationModal({
  isOpen,
  onClose,
  chapter = 'Ch1: The Fish Tale',
}: StudentRegistrationModalProps) {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { registerStudent } = useStudent()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (!name.trim()) {
        setError('Please enter your name')
        setLoading(false)
        return
      }

      await registerStudent(name, chapter)
      onClose()
    } catch (err) {
      setError('Failed to register. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 animate-in">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Practice Arena! 🎓</h2>
        <p className="text-gray-600 mb-6">Let's get started with your learning journey</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Your Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your name"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="chapter" className="block text-sm font-medium text-gray-700 mb-2">
              Chapter
            </label>
            <input
              id="chapter"
              type="text"
              value={chapter}
              disabled
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
            />
          </div>

          {error && <div className="text-red-600 text-sm font-medium">{error}</div>}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-indigo-700 transition disabled:opacity-50"
            >
              {loading ? 'Registering...' : 'Start Learning'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
