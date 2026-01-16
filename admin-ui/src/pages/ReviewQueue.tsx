import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, XCircle, Clock, Eye, MessageSquare, User } from 'lucide-react'
import toast from 'react-hot-toast'

interface ReviewItem {
  id: string
  template_id: string
  template_name: string
  concept_id: string
  submitted_by: string
  submitted_at: string
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  reviewed_by?: string
  reviewed_at?: string
  review_comments?: string
  template_data: {
    question_pattern: string
    difficulty: number
    estimated_time: number
  }
}

interface ReviewResponse {
  items: ReviewItem[]
  total: number
  page: number
  per_page: number
}

async function fetchReviewQueue(): Promise<ReviewResponse> {
  // Mock data - replace with actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        items: [
          {
            id: '1',
            template_id: '2',
            template_name: 'Multiples of a Number',
            concept_id: 'factors_multiples.find_multiples',
            submitted_by: 'Jane Smith',
            submitted_at: '2024-01-13T15:30:00Z',
            status: 'PENDING',
            template_data: {
              question_pattern: 'Find the first 5 multiples of {{number}}',
              difficulty: 3,
              estimated_time: 60
            }
          },
          {
            id: '2',
            template_id: '3',
            template_name: 'GCD Problems',
            concept_id: 'factors_multiples.gcd',
            submitted_by: 'Bob Johnson',
            submitted_at: '2024-01-12T09:15:00Z',
            status: 'PENDING',
            template_data: {
              question_pattern: 'Find the GCD of {{num1}} and {{num2}}',
              difficulty: 4,
              estimated_time: 90
            }
          },
          {
            id: '3',
            template_id: '4',
            template_name: 'Prime Factorization',
            concept_id: 'factors_multiples.prime_factors',
            submitted_by: 'Alice Brown',
            submitted_at: '2024-01-11T14:20:00Z',
            status: 'APPROVED',
            reviewed_by: 'John Doe',
            reviewed_at: '2024-01-14T10:00:00Z',
            review_comments: 'Good template, clear question pattern',
            template_data: {
              question_pattern: 'Find the prime factorization of {{number}}',
              difficulty: 3,
              estimated_time: 75
            }
          }
        ],
        total: 3,
        page: 1,
        per_page: 10
      })
    }, 500)
  })
}

async function approveTemplate(reviewId: string, comments?: string): Promise<void> {
  // Mock approve - replace with actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve()
    }, 500)
  })
}

async function rejectTemplate(reviewId: string, comments: string): Promise<void> {
  // Mock reject - replace with actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve()
    }, 500)
  })
}

export function ReviewQueue() {
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null)
  const [reviewComments, setReviewComments] = useState('')
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [reviewAction, setReviewAction] = useState<'approve' | 'reject' | null>(null)
  
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['review-queue'],
    queryFn: fetchReviewQueue,
  })

  const approveMutation = useMutation({
    mutationFn: ({ reviewId, comments }: { reviewId: string; comments?: string }) =>
      approveTemplate(reviewId, comments),
    onSuccess: () => {
      toast.success('Template approved successfully')
      queryClient.invalidateQueries({ queryKey: ['review-queue'] })
      setShowReviewModal(false)
      setReviewComments('')
      setReviewAction(null)
    },
    onError: () => {
      toast.error('Failed to approve template')
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ reviewId, comments }: { reviewId: string; comments: string }) =>
      rejectTemplate(reviewId, comments),
    onSuccess: () => {
      toast.success('Template rejected successfully')
      queryClient.invalidateQueries({ queryKey: ['review-queue'] })
      setShowReviewModal(false)
      setReviewComments('')
      setReviewAction(null)
    },
    onError: () => {
      toast.error('Failed to reject template')
    },
  })

  const handleApprove = (item: ReviewItem) => {
    setSelectedItem(item)
    setReviewAction('approve')
    setShowReviewModal(true)
  }

  const handleReject = (item: ReviewItem) => {
    setSelectedItem(item)
    setReviewAction('reject')
    setShowReviewModal(true)
  }

  const handleSubmitReview = () => {
    if (!selectedItem || !reviewAction) return

    if (reviewAction === 'approve') {
      approveMutation.mutate({
        reviewId: selectedItem.id,
        comments: reviewComments || undefined
      })
    } else {
      if (!reviewComments.trim()) {
        toast.error('Please provide comments for rejection')
        return
      }
      rejectMutation.mutate({
        reviewId: selectedItem.id,
        comments: reviewComments
      })
    }
  }

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      PENDING: 'badge-warning',
      APPROVED: 'badge-success',
      REJECTED: 'badge-danger',
    }
    return `badge ${statusStyles[status as keyof typeof statusStyles]}`
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <Clock className="h-4 w-4" />
      case 'APPROVED':
        return <CheckCircle className="h-4 w-4" />
      case 'REJECTED':
        return <XCircle className="h-4 w-4" />
      default:
        return null
    }
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
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
          <p className="text-danger-800">Error loading review queue</p>
        </div>
      </div>
    )
  }

  const pendingItems = data?.items.filter(item => item.status === 'PENDING') || []
  const completedItems = data?.items.filter(item => item.status !== 'PENDING') || []

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Review Queue</h1>
        <p className="text-gray-600">Review and approve submitted templates</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-warning-100">
              <Clock className="h-6 w-6 text-warning-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Review</p>
              <p className="text-2xl font-bold text-gray-900">{pendingItems.length}</p>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-success-100">
              <CheckCircle className="h-6 w-6 text-success-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-gray-900">
                {completedItems.filter(item => item.status === 'APPROVED').length}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-danger-100">
              <XCircle className="h-6 w-6 text-danger-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Rejected</p>
              <p className="text-2xl font-bold text-gray-900">
                {completedItems.filter(item => item.status === 'REJECTED').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pending Reviews */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Pending Review ({pendingItems.length})</h2>
        <div className="space-y-4">
          {pendingItems.map((item) => (
            <div key={item.id} className="card">
              <div className="p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{item.template_name}</h3>
                      <span className={getStatusBadge(item.status)}>
                        {getStatusIcon(item.status)}
                        <span className="ml-1">{item.status}</span>
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{item.concept_id}</p>
                    <div className="bg-gray-50 rounded p-3 mb-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Question Pattern:</p>
                      <p className="text-sm text-gray-900 font-mono">{item.template_data.question_pattern}</p>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <User className="h-4 w-4 mr-1" />
                        {item.submitted_by}
                      </div>
                      <div>
                        Difficulty: {'⭐'.repeat(item.template_data.difficulty)}
                      </div>
                      <div>
                        Time: {item.template_data.estimated_time}s
                      </div>
                      <div>
                        Submitted: {new Date(item.submitted_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button
                      onClick={() => handleApprove(item)}
                      className="btn btn-success flex items-center text-sm"
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(item)}
                      className="btn btn-danger flex items-center text-sm"
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        {pendingItems.length === 0 && (
          <div className="card">
            <div className="text-center py-8">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No templates pending review</p>
            </div>
          </div>
        )}
      </div>

      {/* Completed Reviews */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Reviews ({completedItems.length})</h2>
        <div className="space-y-4">
          {completedItems.map((item) => (
            <div key={item.id} className="card">
              <div className="p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{item.template_name}</h3>
                      <span className={getStatusBadge(item.status)}>
                        {getStatusIcon(item.status)}
                        <span className="ml-1">{item.status}</span>
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{item.concept_id}</p>
                    {item.review_comments && (
                      <div className="bg-gray-50 rounded p-3 mb-3">
                        <p className="text-sm font-medium text-gray-700 mb-1">Review Comments:</p>
                        <p className="text-sm text-gray-900">{item.review_comments}</p>
                      </div>
                    )}
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <User className="h-4 w-4 mr-1" />
                        {item.submitted_by}
                      </div>
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Reviewed by {item.reviewed_by}
                      </div>
                      <div>
                        {new Date(item.reviewed_at || item.submitted_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        {completedItems.length === 0 && (
          <div className="card">
            <div className="text-center py-8">
              <p className="text-gray-500">No completed reviews</p>
            </div>
          </div>
        )}
      </div>

      {/* Review Modal */}
      {showReviewModal && selectedItem && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-2">
                {reviewAction === 'approve' ? 'Approve Template' : 'Reject Template'}
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                {selectedItem.template_name}
              </p>
              
              {reviewAction === 'reject' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Comments (required for rejection)
                  </label>
                  <textarea
                    value={reviewComments}
                    onChange={(e) => setReviewComments(e.target.value)}
                    rows={4}
                    className="input"
                    placeholder="Please provide feedback for rejection..."
                  />
                </div>
              )}

              {reviewAction === 'approve' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Comments (optional)
                  </label>
                  <textarea
                    value={reviewComments}
                    onChange={(e) => setReviewComments(e.target.value)}
                    rows={4}
                    className="input"
                    placeholder="Add any comments or suggestions..."
                  />
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => {
                    setShowReviewModal(false)
                    setReviewComments('')
                    setReviewAction(null)
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitReview}
                  disabled={approveMutation.isLoading || rejectMutation.isLoading}
                  className={`btn ${reviewAction === 'approve' ? 'btn-success' : 'btn-danger'}`}
                >
                  {approveMutation.isLoading || rejectMutation.isLoading
                    ? 'Processing...'
                    : reviewAction === 'approve'
                    ? 'Approve'
                    : 'Reject'
                  }
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
