import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus, Search, Filter, Edit, Eye, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { useTemplates, useDeleteTemplate } from '../api'

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

interface Filters {
  status?: string
  concept_id?: string
  difficulty?: string
  search?: string
}

async function fetchTemplates(filters: Filters, page: number = 1): Promise<TemplatesResponse> {
  // Mock data for now - replace with actual API call
  const mockTemplates: Template[] = [
    {
      id: '1',
      name: 'Factors of a Number',
      concept_id: 'factors_multiples.find_factors',
      difficulty: 2,
      bloom_level: 'UNDERSTAND',
      status: 'PUBLISHED',
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
      status: 'REVIEW',
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
      status: 'DRAFT',
      created_at: '2024-01-12T09:15:00Z',
      updated_at: '2024-01-12T09:15:00Z',
      created_by: 'Bob Johnson',
      question_count: 15,
    },
  ]

  // Apply filters
  let filteredTemplates = mockTemplates
  if (filters.status) {
    filteredTemplates = filteredTemplates.filter(t => t.status === filters.status)
  }
  if (filters.search) {
    filteredTemplates = filteredTemplates.filter(t => 
      t.name.toLowerCase().includes(filters.search!.toLowerCase())
    )
  }

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        templates: filteredTemplates,
        total: filteredTemplates.length,
        page,
        per_page: 10,
      })
    }, 500)
  })
}

async function deleteTemplate(id: string): Promise<void> {
  // Mock delete - replace with actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve()
    }, 500)
  })
}

export function TemplateList() {
  const [filters, setFilters] = useState<Filters>({})
  const [searchTerm, setSearchTerm] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useTemplates(filters)

  const deleteMutation = useDeleteTemplate()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setFilters({ ...filters, search: searchTerm })
  }

  const handleFilterChange = (key: keyof Filters, value: string) => {
    const newFilters = { ...filters }
    if (value === '') {
      delete newFilters[key]
    } else {
      newFilters[key] = value
    }
    setFilters(newFilters)
  }

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this template?')) {
      deleteMutation.mutate(id)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      DRAFT: 'badge-gray',
      REVIEW: 'badge-warning',
      APPROVED: 'badge-blue',
      PUBLISHED: 'badge-success',
      ARCHIVED: 'badge-gray',
    }
    return `badge ${statusStyles[status as keyof typeof statusStyles]}`
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
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
          <p className="text-danger-800">Error loading templates</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Templates</h1>
          <p className="text-gray-600">Manage your question templates</p>
        </div>
        <Link
          to="/templates/new"
          className="btn btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Template
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="card mb-6">
        <div className="p-4">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search templates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
            </div>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="btn btn-secondary flex items-center"
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </button>
            <button type="submit" className="btn btn-primary">
              Search
            </button>
          </form>

          {showFilters && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="input"
                >
                  <option value="">All Statuses</option>
                  <option value="DRAFT">Draft</option>
                  <option value="REVIEW">In Review</option>
                  <option value="APPROVED">Approved</option>
                  <option value="PUBLISHED">Published</option>
                  <option value="ARCHIVED">Archived</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Difficulty
                </label>
                <select
                  value={filters.difficulty || ''}
                  onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                  className="input"
                >
                  <option value="">All Levels</option>
                  <option value="1">Easy</option>
                  <option value="2">Medium</option>
                  <option value="3">Hard</option>
                  <option value="4">Expert</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Concept
                </label>
                <select
                  value={filters.concept_id || ''}
                  onChange={(e) => handleFilterChange('concept_id', e.target.value)}
                  className="input"
                >
                  <option value="">All Concepts</option>
                  <option value="factors_multiples.find_factors">Factors</option>
                  <option value="factors_multiples.find_multiples">Multiples</option>
                  <option value="factors_multiples.gcd">GCD</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Concept
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Difficulty
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Questions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created By
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data?.templates.map((template: any) => (
                <tr key={template.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {template.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {template.bloom_level}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {template.concept_id}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">
                      {'⭐'.repeat(template.difficulty)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getStatusBadge(template.status)}>
                      {template.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {template.question_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {template.created_by}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <Link
                        to={`/templates/${template.id}/edit`}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        <Edit className="h-4 w-4" />
                      </Link>
                      <Link
                        to={`/templates/${template.id}/preview`}
                        className="text-gray-600 hover:text-gray-900"
                      >
                        <Eye className="h-4 w-4" />
                      </Link>
                      <button
                        onClick={() => handleDelete(template.id)}
                        className="text-danger-600 hover:text-danger-900"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data?.templates.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No templates found</p>
          </div>
        )}
      </div>
    </div>
  )
}
