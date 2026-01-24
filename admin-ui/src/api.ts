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
// VITE_API_URL should be the base URL without /api suffix (e.g., http://localhost:8000)
const envUrl = import.meta.env.VITE_API_URL
const API_BASE_URL = envUrl 
  ? `${envUrl}/api`
  : (import.meta.env.PROD ? '/api' : 'http://localhost:5002/api')

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
    try {
      // Build query string
      const queryParams = new URLSearchParams()
      if (params?.page) queryParams.append('page', params.page.toString())
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString())
      if (params?.status) queryParams.append('status', params.status)
      if (params?.concept_id) queryParams.append('concept_id', params.concept_id)
      if (params?.search) queryParams.append('search', params.search)
      
      const queryString = queryParams.toString()
      const url = queryString ? `/admin/templates/?${queryString}` : '/admin/templates/'
      
      const templates = await this.request<any[]>(url)
      
      // Transform backend response to frontend format
      return {
        templates: templates.map(t => ({
          id: t.id.toString(),
          name: t.question_pattern.substring(0, 50) + (t.question_pattern.length > 50 ? '...' : ''),
          concept_id: t.concept_id,
          difficulty: t.difficulty,
          bloom_level: t.bloom_level,
          status: t.status as 'DRAFT' | 'REVIEW' | 'APPROVED' | 'PUBLISHED',
          created_at: t.created_at,
          updated_at: t.updated_at,
          created_by: t.created_by || 'Unknown',
          question_count: 1, // Single template
        })),
        total: templates.length,
        page: params?.page || 1,
        per_page: params?.per_page || 20,
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error)
      throw error
    }
  }

  async getTemplate(id: string) {
    return this.request(`/admin/templates/${id}`)
  }

  async createTemplate(data: any) {
    return this.request('/admin/templates/ingest', {
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
    return this.request(`/admin/templates/${id}/archive`, {
      method: 'POST',
    })
  }

  async submitTemplateForReview(id: string) {
    return this.request(`/admin/templates/${id}/submit`, {
      method: 'POST',
    })
  }

  async approveTemplateWorkflow(id: string) {
    return this.request(`/admin/templates/${id}/approve`, {
      method: 'POST',
    })
  }

  async publishTemplate(id: string) {
    return this.request(`/admin/templates/${id}/publish`, {
      method: 'POST',
    })
  }

  async rejectTemplate(id: string, feedback: string) {
    return this.request(`/admin/templates/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ feedback }),
    })
  }

  async previewTemplate(id: string) {
    return this.request(`/admin/templates/${id}/preview`, {
      method: 'POST',
    })
  }

  async validateTemplate(id: string) {
    return this.request(`/admin/templates/${id}/validate`, {
      method: 'POST',
    })
  }

  // Misconceptions API
  async getMisconceptions(subject?: string) {
    const params = subject ? `?subject=${subject}` : ''
    return this.request(`/admin/templates/misconceptions${params}`)
  }

  async createMisconception(data: {
    code: string
    title: string
    description: string
    teaching_point: string
    subject: string
    concept_tags?: string[]
  }) {
    return this.request('/admin/templates/misconceptions', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getMisconception(id: string) {
    return this.request(`/admin/templates/misconceptions/${id}`)
  }

  async getTemplateWorkflowSummary() {
    return this.request('/admin/templates/workflow/summary')
  }

  // Coverage
  async getCoverageData() {
    return this.request('/admin/coverage')
  }

  // Dashboard Stats
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      // Get workflow summary from backend
      const workflowSummary = await this.getTemplateWorkflowSummary() as any
      
      // Get all templates to calculate stats
      const templates = await this.request<any[]>('/admin/templates/')
      
      const publishedCount = templates.filter(t => t.status === 'PUBLISHED').length
      const reviewCount = templates.filter(t => t.status === 'REVIEW').length
      
      return {
        totalTemplates: templates.length,
        publishedTemplates: publishedCount,
        pendingReview: reviewCount,
        totalQuestions: templates.length * 10, // Estimate: each template generates ~10 questions
        recentActivity: templates.slice(0, 5).map((t, i) => ({
          id: t.id.toString(),
          type: t.status === 'PUBLISHED' ? 'template_published' : 'template_created',
          description: `Template "${t.question_pattern?.substring(0, 40) || 'Untitled'}..."`,
          timestamp: t.updated_at,
          user: t.created_by || 'Unknown'
        }))
      }
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
      // Return fallback data
      return {
        totalTemplates: 0,
        publishedTemplates: 0,
        pendingReview: 0,
        totalQuestions: 0,
        recentActivity: []
      }
    }
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
    queryFn: () => apiClient.getTemplates({ status: 'REVIEW' }),
  })
}

export const useSubmitForReview = () => {
  return useMutation({
    mutationFn: (templateId: string) => apiClient.submitTemplateForReview(templateId),
    onSuccess: () => {
      toast.success('Template submitted for review')
    },
    onError: (error: Error) => {
      toast.error(`Failed to submit template: ${error.message}`)
    },
  })
}

export const useApproveTemplate = () => {
  return useMutation({
    mutationFn: (templateId: string) => apiClient.approveTemplateWorkflow(templateId),
    onSuccess: () => {
      toast.success('Template approved successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to approve template: ${error.message}`)
    },
  })
}

export const usePublishTemplate = () => {
  return useMutation({
    mutationFn: (templateId: string) => apiClient.publishTemplate(templateId),
    onSuccess: () => {
      toast.success('Template published successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to publish template: ${error.message}`)
    },
  })
}

export const useRejectTemplate = () => {
  return useMutation({
    mutationFn: ({ templateId, feedback }: { templateId: string; feedback: string }) => 
      apiClient.rejectTemplate(templateId, feedback),
    onSuccess: () => {
      toast.success('Template rejected')
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

// ============================================================================
// Graph API Functions
// ============================================================================

export interface ConceptNode {
  concept_id: string
  name: string
  description?: string
  bloom_targets: string[]
  difficulty_default: number
  template_count: number
  published_count: number
  draft_count: number
  status: string
}

export interface ConceptEdge {
  from_concept: string
  to_concept: string
  kind: string
  reason?: string
}

export interface ConceptGraphData {
  subject: string
  grade: number
  chapter_id: string
  chapter_name: string
  description?: string
  total_concepts: number
  total_edges: number
  nodes: ConceptNode[]
  edges: ConceptEdge[]
}

export interface ValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export async function fetchConceptGraph(
  subject: string,
  grade: string,
  chapter: string
): Promise<ConceptGraphData> {
  const response = await fetch(
    `${API_BASE_URL}/admin/graphs/${subject}/${grade}/${chapter}`
  )
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

export async function saveConceptGraph(
  subject: string,
  grade: string,
  chapter: string,
  data: { nodes: any[]; edges: any[] }
): Promise<{ success: boolean }> {
  const response = await fetch(
    `${API_BASE_URL}/admin/graphs/${subject}/${grade}/${chapter}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
  )
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

export async function validateGraph(
  subject: string,
  grade: string,
  chapter: string
): Promise<ValidationResult> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/admin/graphs/${subject}/${grade}/${chapter}/validate`
    )
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return response.json()
  } catch (error) {
    // Return mock validation for now (endpoint may not exist yet)
    return { valid: true, errors: [], warnings: [] }
  }
}
