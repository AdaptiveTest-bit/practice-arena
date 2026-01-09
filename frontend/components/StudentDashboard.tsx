'use client'

import React, { useEffect, useState } from 'react'
import { useStudent } from '@/lib/studentContext'

interface StudentStats {
  success: boolean
  studentId: string
  name: string
  chapter: string
  currentBloomLevel: string
  attemptCount: number
  correctCount: number
  accuracyRate: number
  misconceptionsEncountered: string[]
}

export function StudentDashboard() {
  const { student } = useStudent()
  const [stats, setStats] = useState<StudentStats | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (student) {
      fetchStudentStats()
    }
  }, [student])

  const fetchStudentStats = async () => {
    if (!student) return

    setLoading(true)
    try {
      const response = await fetch(`/api/student/${student.studentId}/progress`)
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch student stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!student || !stats) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{stats.name}</h2>
          <p className="text-gray-600">{stats.chapter}</p>
        </div>
        <button
          onClick={fetchStudentStats}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
          <p className="text-sm text-gray-600 font-medium">Attempts</p>
          <p className="text-3xl font-bold text-blue-600">{stats.attemptCount}</p>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
          <p className="text-sm text-gray-600 font-medium">Correct</p>
          <p className="text-3xl font-bold text-green-600">{stats.correctCount}</p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
          <p className="text-sm text-gray-600 font-medium">Accuracy</p>
          <p className="text-3xl font-bold text-purple-600">
            {(stats.accuracyRate * 100).toFixed(1)}%
          </p>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
          <p className="text-sm text-gray-600 font-medium">Bloom Level</p>
          <p className="text-2xl font-bold text-orange-600">{stats.currentBloomLevel}</p>
        </div>
      </div>
    </div>
  )
}
