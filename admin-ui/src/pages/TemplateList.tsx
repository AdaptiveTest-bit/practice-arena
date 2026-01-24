import React, { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus, Search, Filter, Edit, Eye, Trash2, X, Send, CheckCircle, XCircle, Play, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { useTemplates, apiClient } from '../api'

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
  question_pattern?: string
}

interface Filters {
  status?: string
  concept_id?: string
  difficulty?: string
  search?: string
}

interface PreviewData {
  success: boolean
  question?: any
  variables?: any
  error?: string
}

export function TemplateList() {
  const [filters, setFilters] = useState<Filters>({})
  const [searchTerm, setSearchTerm] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<any | null>(null)
  const [showViewModal, setShowViewModal] = useState(false)
  const [previewData, setPreviewData] = useState<PreviewData | null>(null)
  const [isLoadingPreview, setIsLoadingPreview] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading, error, refetch } = useTemplates(filters)

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

  const handleDelete = async (id: string, status: string) => {
    if (status === 'PUBLISHED') {
      toast.error('Cannot delete published templates. Archive them instead.')
      return
    }
    if (window.confirm('Are you sure you want to archive this template?')) {
      try {
        await apiClient.deleteTemplate(id)
        toast.success('Template archived')
        refetch()
      } catch (error) {
        toast.error('Failed to archive template')
      }
    }
  }

  const handleSubmitForReview = async (id: string) => {
    try {
      await apiClient.submitTemplateForReview(id)
      toast.success('Template submitted for review')
      refetch()
    } catch (error: any) {
      toast.error(error.message || 'Failed to submit template')
    }
  }

  const handleApprove = async (id: string) => {
    try {
      await apiClient.approveTemplateWorkflow(id)
      toast.success('Template approved')
      refetch()
    } catch (error: any) {
      toast.error(error.message || 'Failed to approve template')
    }
  }

  const handlePublish = async (id: string) => {
    try {
      await apiClient.publishTemplate(id)
      toast.success('Template published!')
      refetch()
    } catch (error: any) {
      toast.error(error.message || 'Failed to publish template')
    }
  }

  const handleViewTemplate = async (id: string) => {
    try {
      const template = await apiClient.getTemplate(id)
      setSelectedTemplate(template)
      setPreviewData(null) // Reset preview when opening new template
      setShowViewModal(true)
    } catch (error) {
      toast.error('Failed to load template details')
    }
  }

  const handleGeneratePreview = async (id: string) => {
    setIsLoadingPreview(true)
    try {
      const preview = await apiClient.previewTemplate(id) as PreviewData
      setPreviewData(preview)
      if (!preview.success) {
        toast.error('Preview generation failed: ' + (preview.error || 'Unknown error'))
      }
    } catch (error: any) {
      toast.error('Failed to generate preview')
      setPreviewData({ success: false, error: error.message || 'Failed to generate preview' })
    } finally {
      setIsLoadingPreview(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusStyles: Record<string, string> = {
      DRAFT: 'bg-gray-100 text-gray-800',
      REVIEW: 'bg-yellow-100 text-yellow-800',
      APPROVED: 'bg-blue-100 text-blue-800',
      PUBLISHED: 'bg-green-100 text-green-800',
      ARCHIVED: 'bg-gray-100 text-gray-500',
    }
    return `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status] || statusStyles.DRAFT}`
  }

  const getDifficultyLabel = (difficulty: number) => {
    const labels: Record<number, string> = {
      1: '🟢 Easy',
      2: '🟡 Medium', 
      3: '🟠 Hard',
      4: '🔴 Expert',
      5: '⚫ Master'
    }
    return labels[difficulty] || `Level ${difficulty}`
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
                  Template
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
                  Updated
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Author
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data?.templates.map((template: any) => (
                <tr key={template.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="max-w-xs">
                      <div className="text-sm font-medium text-gray-900 truncate" title={template.name}>
                        {template.name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {template.bloom_level} • ID: {template.id}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 font-mono text-xs">
                      {template.concept_id.split('.').pop()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm">
                      {getDifficultyLabel(template.difficulty)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getStatusBadge(template.status)}>
                      {template.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(template.updated_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {template.created_by}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-1">
                      {/* View Button */}
                      <button
                        onClick={() => handleViewTemplate(template.id)}
                        className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      
                      {/* Edit Button - only for non-published */}
                      {template.status !== 'PUBLISHED' && (
                        <Link
                          to={`/templates/${template.id}/edit`}
                          className="p-1 text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded"
                          title="Edit Template"
                        >
                          <Edit className="h-4 w-4" />
                        </Link>
                      )}
                      
                      {/* Workflow Actions */}
                      {template.status === 'DRAFT' && (
                        <button
                          onClick={() => handleSubmitForReview(template.id)}
                          className="p-1 text-yellow-600 hover:text-yellow-900 hover:bg-yellow-50 rounded"
                          title="Submit for Review"
                        >
                          <Send className="h-4 w-4" />
                        </button>
                      )}
                      
                      {template.status === 'REVIEW' && (
                        <button
                          onClick={() => handleApprove(template.id)}
                          className="p-1 text-green-600 hover:text-green-900 hover:bg-green-50 rounded"
                          title="Approve"
                        >
                          <CheckCircle className="h-4 w-4" />
                        </button>
                      )}
                      
                      {template.status === 'APPROVED' && (
                        <button
                          onClick={() => handlePublish(template.id)}
                          className="p-1 text-green-600 hover:text-green-900 hover:bg-green-50 rounded"
                          title="Publish"
                        >
                          <CheckCircle className="h-4 w-4" />
                        </button>
                      )}
                      
                      {/* Delete/Archive - only for non-published */}
                      {template.status !== 'PUBLISHED' && (
                        <button
                          onClick={() => handleDelete(template.id, template.status)}
                          className="p-1 text-red-600 hover:text-red-900 hover:bg-red-50 rounded"
                          title="Archive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
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

      {/* View Template Modal */}
      {showViewModal && selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold">Template Details</h2>
              <button
                onClick={() => setShowViewModal(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[70vh]">
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">ID</label>
                  <p className="text-sm font-mono">{selectedTemplate.id}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">Concept ID</label>
                  <p className="text-sm font-mono">{selectedTemplate.concept_id}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">Question Pattern</label>
                  <pre className="text-sm bg-gray-50 p-3 rounded-lg whitespace-pre-wrap font-mono">
                    {selectedTemplate.question_pattern}
                  </pre>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Difficulty</label>
                    <p className="text-sm">{getDifficultyLabel(selectedTemplate.difficulty)}</p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Bloom Level</label>
                    <p className="text-sm">{selectedTemplate.bloom_level}</p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Status</label>
                    <p><span className={getStatusBadge(selectedTemplate.status)}>{selectedTemplate.status}</span></p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Estimated Time</label>
                    <p className="text-sm">{selectedTemplate.estimated_time} seconds</p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Created By</label>
                    <p className="text-sm">{selectedTemplate.created_by || 'Unknown'}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Created At</label>
                    <p className="text-sm">{new Date(selectedTemplate.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Updated At</label>
                    <p className="text-sm">{new Date(selectedTemplate.updated_at).toLocaleString()}</p>
                  </div>
                </div>
                {selectedTemplate.validation_errors && selectedTemplate.validation_errors.length > 0 && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Validation Errors</label>
                    <ul className="text-sm text-red-600 list-disc pl-4">
                      {selectedTemplate.validation_errors.map((err: string, i: number) => (
                        <li key={i}>{err}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Live Preview Section */}
                <div className="border-t pt-4 mt-4">
                  <div className="flex items-center justify-between mb-3">
                    <label className="text-xs font-medium text-gray-500 uppercase">Live Preview</label>
                    <button
                      onClick={() => handleGeneratePreview(selectedTemplate.id)}
                      disabled={isLoadingPreview}
                      className="inline-flex items-center px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      {isLoadingPreview ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-1" />
                          Generate Preview
                        </>
                      )}
                    </button>
                  </div>

                  {previewData && (
                    <div className={`p-4 rounded-lg ${previewData.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                      {previewData.success ? (
                        <div className="space-y-3">
                          <div>
                            <label className="text-xs font-medium text-green-700">Generated Question:</label>
                            <p className="text-sm mt-1 whitespace-pre-wrap">
                              {previewData.question?.question_text || previewData.question?.question || 'No question text'}
                            </p>
                          </div>
                          {previewData.question?.options && (
                            <div>
                              <label className="text-xs font-medium text-green-700">Options:</label>
                              <ul className="list-disc pl-5 mt-1 space-y-1">
                                {previewData.question.options.map((opt: any, i: number) => (
                                  <li key={i} className={`text-sm ${opt.is_correct ? 'text-green-700 font-medium' : ''}`}>
                                    {opt.text || opt} {opt.is_correct && '✓'}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {previewData.variables && Object.keys(previewData.variables).length > 0 && (
                            <div>
                              <label className="text-xs font-medium text-green-700">Variables Used:</label>
                              <pre className="text-xs bg-green-100 p-2 rounded mt-1">
                                {JSON.stringify(previewData.variables, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div>
                          <label className="text-xs font-medium text-red-700">Preview Error:</label>
                          <p className="text-sm text-red-600 mt-1">{previewData.error}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {!previewData && (
                    <p className="text-sm text-gray-500 italic">Click "Generate Preview" to see a sample question generated from this template.</p>
                  )}
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 p-4 border-t bg-gray-50">
              {selectedTemplate.status === 'DRAFT' && (
                <button
                  onClick={() => { handleSubmitForReview(selectedTemplate.id); setShowViewModal(false); }}
                  className="btn btn-warning"
                >
                  Submit for Review
                </button>
              )}
              {selectedTemplate.status !== 'PUBLISHED' && (
                <Link
                  to={`/templates/${selectedTemplate.id}/edit`}
                  className="btn btn-primary"
                >
                  Edit Template
                </Link>
              )}
              <button
                onClick={() => setShowViewModal(false)}
                className="btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
