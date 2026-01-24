import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, Search, AlertCircle, Edit2, Trash2, 
  RefreshCw, X, Tag, Lightbulb 
} from 'lucide-react'
import toast from 'react-hot-toast'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Misconception {
  id?: number
  code: string
  title: string
  description: string
  teaching_point: string
  subject: string
  concept_tags: string[]
}

const SUBJECTS = [
  { value: '', label: 'All Subjects' },
  { value: 'math', label: '🔢 Math' },
  { value: 'science', label: '🔬 Science' },
  { value: 'english', label: '📖 English' },
]

async function fetchMisconceptions(subject?: string): Promise<{ misconceptions: Misconception[] }> {
  const params = subject ? `?subject=${subject}` : ''
  const res = await fetch(`${API_BASE}/api/admin/templates/misconceptions${params}`)
  if (!res.ok) throw new Error('Failed to fetch misconceptions')
  return res.json()
}

async function createMisconception(data: Misconception): Promise<Misconception> {
  const res = await fetch(`${API_BASE}/api/admin/templates/misconceptions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!res.ok) throw new Error('Failed to create misconception')
  return res.json()
}

async function deleteMisconception(code: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/admin/templates/misconceptions/${code}`, {
    method: 'DELETE'
  })
  if (!res.ok) throw new Error('Failed to delete misconception')
}

async function fetchConcepts(): Promise<{ concepts: { id: string }[] }> {
  const res = await fetch(`${API_BASE}/api/concepts`)
  if (!res.ok) return { concepts: [] }
  return res.json()
}

export function MisconceptionsManager() {
  const queryClient = useQueryClient()
  const [subjectFilter, setSubjectFilter] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingMisconception, setEditingMisconception] = useState<Misconception | null>(null)
  const [tagInput, setTagInput] = useState('')
  
  const [formData, setFormData] = useState<Misconception>({
    code: '',
    title: '',
    description: '',
    teaching_point: '',
    subject: 'math',
    concept_tags: [],
  })

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['misconceptions', subjectFilter],
    queryFn: () => fetchMisconceptions(subjectFilter || undefined)
  })

  const { data: conceptsData } = useQuery({
    queryKey: ['concepts'],
    queryFn: fetchConcepts
  })

  const createMutation = useMutation({
    mutationFn: createMisconception,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['misconceptions'] })
      toast.success(editingMisconception ? 'Misconception updated!' : 'Misconception created!')
      handleCloseDialog()
    },
    onError: (err: Error) => {
      toast.error(`Failed to save: ${err.message}`)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: deleteMisconception,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['misconceptions'] })
      toast.success('Misconception deleted!')
    },
    onError: (err: Error) => {
      toast.error(`Failed to delete: ${err.message}`)
    }
  })

  const misconceptions = data?.misconceptions || []
  const availableConcepts = conceptsData?.concepts?.map(c => c.id) || []

  const handleOpenDialog = (misconception?: Misconception) => {
    if (misconception) {
      setEditingMisconception(misconception)
      setFormData({
        ...misconception,
        concept_tags: misconception.concept_tags || [],
      })
    } else {
      setEditingMisconception(null)
      setFormData({
        code: '',
        title: '',
        description: '',
        teaching_point: '',
        subject: 'math',
        concept_tags: [],
      })
    }
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingMisconception(null)
    setTagInput('')
  }

  const handleSave = () => {
    if (!formData.code || !formData.title) {
      toast.error('Code and Title are required')
      return
    }
    createMutation.mutate(formData)
  }

  const handleDelete = (code: string) => {
    if (window.confirm(`Delete misconception "${code}"?`)) {
      deleteMutation.mutate(code)
    }
  }

  const addTag = () => {
    if (tagInput && !formData.concept_tags.includes(tagInput)) {
      setFormData({ ...formData, concept_tags: [...formData.concept_tags, tagInput] })
      setTagInput('')
    }
  }

  const removeTag = (tag: string) => {
    setFormData({ ...formData, concept_tags: formData.concept_tags.filter(t => t !== tag) })
  }

  const filteredMisconceptions = misconceptions.filter((m) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return (
        m.code.toLowerCase().includes(query) ||
        m.title.toLowerCase().includes(query) ||
        m.description?.toLowerCase().includes(query)
      )
    }
    return true
  })

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <AlertCircle className="h-7 w-7 text-orange-600" />
            Misconceptions Manager
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Manage common student misconceptions for targeted feedback
          </p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => refetch()}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button
            onClick={() => handleOpenDialog()}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Misconception
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by code, title, description..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <select
            value={subjectFilter}
            onChange={(e) => setSubjectFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white"
          >
            {SUBJECTS.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">Failed to load misconceptions. Make sure the backend is running.</p>
        </div>
      )}

      {/* Table */}
      {!isLoading && !error && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subject</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Teaching Point</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tags</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredMisconceptions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    {misconceptions.length === 0 
                      ? 'No misconceptions found. Add one to get started!'
                      : 'No results match your search.'
                    }
                  </td>
                </tr>
              ) : (
                filteredMisconceptions.map((m) => (
                  <tr key={m.code} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        {m.code}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{m.title}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {m.subject}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {m.teaching_point}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1 flex-wrap">
                        {(m.concept_tags || []).slice(0, 2).map((tag) => (
                          <span key={tag} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                            {tag}
                          </span>
                        ))}
                        {(m.concept_tags || []).length > 2 && (
                          <span className="text-xs text-gray-500">+{m.concept_tags.length - 2}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleOpenDialog(m)}
                        className="p-1 text-gray-500 hover:text-blue-600 mr-2"
                        title="Edit"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(m.code)}
                        className="p-1 text-gray-500 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500">
        Total: {filteredMisconceptions.length} misconceptions
      </div>

      {/* Add/Edit Modal */}
      {dialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold">
                {editingMisconception ? 'Edit Misconception' : 'Add New Misconception'}
              </h2>
              <button onClick={handleCloseDialog} className="p-1 hover:bg-gray-100 rounded">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 overflow-y-auto max-h-[60vh]">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Code <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase().replace(/\s/g, '_') })}
                  disabled={!!editingMisconception}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-100"
                  placeholder="e.g., FACTORS_VS_MULTIPLES"
                />
                <p className="text-xs text-gray-500 mt-1">Unique identifier (uppercase, underscores)</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., Confuses factors with multiples"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Detailed explanation of the misconception"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                  <Lightbulb className="h-4 w-4 text-yellow-500" />
                  Teaching Point
                </label>
                <textarea
                  value={formData.teaching_point}
                  onChange={(e) => setFormData({ ...formData, teaching_point: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="How to help the student overcome this misconception"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <select
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
                >
                  <option value="math">Math</option>
                  <option value="science">Science</option>
                  <option value="english">English</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                  <Tag className="h-4 w-4" />
                  Concept Tags
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                    list="concept-suggestions"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="Type concept and press Enter"
                  />
                  <datalist id="concept-suggestions">
                    {availableConcepts.map((c) => (
                      <option key={c} value={c} />
                    ))}
                  </datalist>
                  <button
                    onClick={addTag}
                    className="px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {formData.concept_tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm"
                    >
                      {tag}
                      <button onClick={() => removeTag(tag)} className="hover:text-blue-900">
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 p-6 border-t bg-gray-50">
              <button
                onClick={handleCloseDialog}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={createMutation.isPending || !formData.code || !formData.title}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Saving...' : editingMisconception ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

