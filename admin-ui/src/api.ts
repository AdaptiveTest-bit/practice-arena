import React from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'

// Type definitions
interface Template {
  id: string
  name: string
  concept_id: string
  difficulty: number
  bloom_level: string
  status: 'DRAFT' | 'REVIEW' | 'APPROVED' | 'PUBLISHED' | 'ARCHIVED'
  created_at: string
  updated_at: string
  created_by: string
  question_count: number
}

interface TemplatesResponse {
  templates: Template[]
  total: number
  page: number
  per_page: number
}

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

// API client for the admin UI
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? '/api' : 'http://localhost:8000/api')

class ApiClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Templates
  async getTemplates(params?: {
    page?: number
    per_page?: number
    status?: string
    concept_id?: string
    search?: string
  }): Promise<TemplatesResponse> {
    // Mock data - replace with actual API call
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockTemplates: Template[] = [
          {
            id: '1',
            name: 'Factors of a Number',
            concept_id: 'factors_multiples.find_factors',
            difficulty: 2,
            bloom_level: 'UNDERSTAND',
            status: 'PUBLISHED' as const,
            created_at: '2024-01-14T10:00:00Z',
            updated_at: '2024-01-14T10:00:00Z',
            created_by: 'John Doe',
            question_count: 25,
          },
          {
            id: '2',
            name: 'Multiples of a Number',
            concept_id: 'factors_multiples.find_multiples',
            difficulty: 3,
            bloom_level: 'APPLY',
            status: 'REVIEW' as const,
            created_at: '2024-01-13T15:30:00Z',
            updated_at: '2024-01-13T15:30:00Z',
            created_by: 'Jane Smith',
            question_count: 20,
          },
          {
            id: '3',
            name: 'GCD Problems',
            concept_id: 'factors_multiples.gcd',
            difficulty: 4,
            bloom_level: 'ANALYZE',
            status: 'DRAFT' as const,
            created_at: '2024-01-12T09:15:00Z',
            updated_at: '2024-01-12T09:15:00Z',
            created_by: 'Bob Johnson',
            question_count: 15,
          },
        ]

        // Apply filters
        let filteredTemplates = mockTemplates
        if (params?.status) {
          filteredTemplates = filteredTemplates.filter(t => t.status === params.status)
        }
        if (params?.search) {
          filteredTemplates = filteredTemplates.filter(t => 
            t.name.toLowerCase().includes(params.search!.toLowerCase())
          )
        }

        resolve({
          templates: filteredTemplates,
          total: filteredTemplates.length,
          page: 1,
          per_page: 10,
        })
      }, 500)
    })
  }

  async getTemplate(id: string) {
    return this.request(`/admin/templates/${id}`)
  }

  async createTemplate(data: any) {
    return this.request('/admin/templates', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateTemplate(id: string, data: any) {
    return this.request(`/admin/templates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteTemplate(id: string) {
    return this.request(`/admin/templates/${id}`, {
      method: 'DELETE',
    })
  }

  async previewTemplate(data: any) {
    return this.request('/admin/templates/preview', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Review Queue
  async getReviewQueue() {
    return this.request('/admin/review-queue')
  }

  async approveTemplate(reviewId: string, comments?: string) {
    return this.request(`/admin/review-queue/${reviewId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    })
  }

  async rejectTemplate(reviewId: string, comments: string) {
    return this.request(`/admin/review-queue/${reviewId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    })
  }

  // Coverage
  async getCoverageData() {
    return this.request('/admin/coverage')
  }

  // Dashboard Stats
  async getDashboardStats(): Promise<DashboardStats> {
    // Mock data - replace with actual API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          totalTemplates: 45,
          publishedTemplates: 32,
          pendingReview: 8,
          totalQuestions: 1250,
          recentActivity: [
            {
              id: '1',
              type: 'template_created',
              description: 'Created new factors template',
              timestamp: '2024-01-14T10:30:00Z',
              user: 'John Doe'
            },
            {
              id: '2',
              type: 'template_approved',
              description: 'Approved multiples template',
              timestamp: '2024-01-14T09:45:00Z',
              user: 'Jane Smith'
            },
            {
              id: '3',
              type: 'template_reviewed',
              description: 'Reviewed GCD template',
              timestamp: '2024-01-14T08:20:00Z',
              user: 'Bob Johnson'
            }
          ]
        })
      }, 1000)
    })
  }
}

export const apiClient = new ApiClient(API_BASE_URL)

// React Query hooks
export const useTemplates = (params?: {
  page?: number
  per_page?: number
  status?: string
  concept_id?: string
  search?: string
}) => {
  return useQuery({
    queryKey: ['templates', params],
    queryFn: () => apiClient.getTemplates(params),
  })
}

export const useTemplate = (id: string) => {
  return useQuery({
    queryKey: ['template', id],
    queryFn: () => apiClient.getTemplate(id),
    enabled: !!id,
  })
}

export const useCreateTemplate = () => {
  return useMutation({
    mutationFn: (data: any) => apiClient.createTemplate(data),
    onSuccess: () => {
      toast.success('Template created successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to create template: ${error.message}`)
    },
  })
}

export const useUpdateTemplate = () => {
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => 
      apiClient.updateTemplate(id, data),
    onSuccess: () => {
      toast.success('Template updated successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to update template: ${error.message}`)
    },
  })
}

export const useDeleteTemplate = () => {
  return useMutation({
    mutationFn: (id: string) => apiClient.deleteTemplate(id),
    onSuccess: () => {
      toast.success('Template deleted successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete template: ${error.message}`)
    },
  })
}

export const usePreviewTemplate = () => {
  return useMutation({
    mutationFn: (data: any) => apiClient.previewTemplate(data),
    onError: (error: Error) => {
      toast.error(`Failed to preview template: ${error.message}`)
    },
  })
}

export const useReviewQueue = () => {
  return useQuery({
    queryKey: ['review-queue'],
    queryFn: () => apiClient.getReviewQueue(),
  })
}

export const useApproveTemplate = () => {
  return useMutation({
    mutationFn: ({ reviewId, comments }: { reviewId: string; comments?: string }) => 
      apiClient.approveTemplate(reviewId, comments),
    onSuccess: () => {
      toast.success('Template approved successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to approve template: ${error.message}`)
    },
  })
}

export const useRejectTemplate = () => {
  return useMutation({
    mutationFn: ({ reviewId, comments }: { reviewId: string; comments: string }) => 
      apiClient.rejectTemplate(reviewId, comments),
    onSuccess: () => {
      toast.success('Template rejected successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to reject template: ${error.message}`)
    },
  })
}

export const useCoverageData = () => {
  return useQuery({
    queryKey: ['coverage-data'],
    queryFn: () => apiClient.getCoverageData(),
  })
}

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => apiClient.getDashboardStats(),
  })
}
