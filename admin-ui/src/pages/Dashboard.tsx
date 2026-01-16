import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileText, Users, CheckCircle, Clock, TrendingUp } from 'lucide-react'
import { useDashboardStats } from '../api'

interface DashboardStats {
  totalTemplates: number
  publishedTemplates: number
  pendingReview: number
  totalQuestions: number
  recentActivity: Array<{
    id: string
    type: string
    description: string
    timestamp: string
    user: string
  }>
}

export function Dashboard() {
  const { data: stats, isLoading, error } = useDashboardStats()

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-danger-50 border border-danger-200 rounded-md p-4">
          <p className="text-danger-800">Error loading dashboard data</p>
        </div>
      </div>
    )
  }

  const statCards = [
    {
      title: 'Total Templates',
      value: stats?.totalTemplates || 0,
      icon: FileText,
      color: 'primary',
      change: '+2 this week',
    },
    {
      title: 'Published',
      value: stats?.publishedTemplates || 0,
      icon: CheckCircle,
      color: 'success',
      change: '+5 this week',
    },
    {
      title: 'Pending Review',
      value: stats?.pendingReview || 0,
      icon: Clock,
      color: 'warning',
      change: '-3 this week',
    },
    {
      title: 'Total Questions',
      value: stats?.totalQuestions || 0,
      icon: TrendingUp,
      color: 'primary',
      change: '+50 this week',
    },
  ]

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your template management system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.title} className="card p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg bg-${stat.color}-100`}>
                  <Icon className={`h-6 w-6 text-${stat.color}-600`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-xs text-gray-500">{stat.change}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              {stats?.recentActivity.map((activity: any) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-primary-600 rounded-full mt-2"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{activity.description}</p>
                    <p className="text-xs text-gray-500">
                      {activity.user} • {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <a
                href="/templates/new"
                className="block w-full text-center btn btn-primary"
              >
                Create New Template
              </a>
              <a
                href="/review"
                className="block w-full text-center btn btn-secondary"
              >
                Review Pending Templates
              </a>
              <a
                href="/coverage"
                className="block w-full text-center btn btn-secondary"
              >
                View Coverage Dashboard
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
