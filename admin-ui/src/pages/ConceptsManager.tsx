import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, Search, BookOpen, Edit2, Trash2, 
  RefreshCw, X, Network, ChevronRight 
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Concept {
  id: string
  name: string
  description?: string
  chapter: string
  grade: number
  subject: string
  is_prerequisite?: boolean
  taxonomy?: string
}

const SUBJECTS = [
  { value: '', label: 'All Subjects' },
  { value: 'math', label: '🔢 Math' },
  { value: 'science', label: '🔬 Science' },
  { value: 'english', label: '📖 English' },
]

const GRADES = [
  { value: '', label: 'All Grades' },
  { value: '3', label: 'Class 3' },
  { value: '4', label: 'Class 4' },
  { value: '5', label: 'Class 5' },
  { value: '6', label: 'Class 6' },
  { value: '7', label: 'Class 7' },
  { value: '8', label: 'Class 8' },
]

async function fetchConcepts(subject?: string, grade?: string, chapter?: string): Promise<{ concepts: Concept[], total: number }> {
  const params = new URLSearchParams()
  if (subject) params.append('subject', subject)
  if (grade) params.append('grade', grade)
  if (chapter) params.append('chapter', chapter)
  
  const res = await fetch(`${API_BASE}/api/concepts?${params}`)
  if (!res.ok) throw new Error('Failed to fetch concepts')
  return res.json()
}

async function createConcept(data: Partial<Concept>): Promise<Concept> {
  const res = await fetch(`${API_BASE}/api/admin/graphs/${data.subject}/${data.grade}/${data.chapter}/nodes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      concept_id: data.id,
      id: data.id,
      bloom_targets: ['remember', 'understand'],
      difficulty_default: 3,
      description: data.description || ''
    })
  })
  if (!res.ok) throw new Error('Failed to create concept')
  return res.json()
}

async function deleteConcept(subject: string, grade: number, chapter: string, conceptId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/admin/graphs/${subject}/${grade}/${chapter}/nodes/${conceptId}`, {
    method: 'DELETE'
  })
  if (!res.ok) throw new Error('Failed to delete concept')
}

export function ConceptsManager() {
  const queryClient = useQueryClient()
  const [subjectFilter, setSubjectFilter] = useState('math')
  const [gradeFilter, setGradeFilter] = useState('5')
  const [chapterFilter, setChapterFilter] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  
  const [formData, setFormData] = useState<Partial<Concept>>({
    id: '',
    name: '',
    description: '',
    chapter: 'factors_multiples',
    grade: 5,
    subject: 'math',
  })

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['concepts', subjectFilter, gradeFilter, chapterFilter],
    queryFn: () => fetchConcepts(subjectFilter || undefined, gradeFilter || undefined, chapterFilter || undefined)
  })

  const createMutation = useMutation({
    mutationFn: createConcept,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concepts'] })
      toast.success('Concept created!')
      handleCloseDialog()
    },
    onError: (err: Error) => {
      toast.error(`Failed to save: ${err.message}`)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: ({ subject, grade, chapter, conceptId }: { subject: string, grade: number, chapter: string, conceptId: string }) => 
      deleteConcept(subject, grade, chapter, conceptId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concepts'] })
      toast.success('Concept deleted!')
    },
    onError: (err: Error) => {
      toast.error(`Failed to delete: ${err.message}`)
    }
  })

  const concepts = data?.concepts || []

  const handleOpenDialog = () => {
    setFormData({
      id: '',
      name: '',
      description: '',
      chapter: 'factors_multiples',
      grade: 5,
      subject: 'math',
    })
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
  }

  const handleSave = () => {
    if (!formData.id || !formData.name) {
      toast.error('Concept ID and Name are required')
      return
    }
    createMutation.mutate(formData)
  }

  const handleDelete = (concept: Concept) => {
    if (window.confirm(`Delete concept "${concept.id}"?`)) {
      deleteMutation.mutate({
        subject: concept.subject,
        grade: concept.grade,
        chapter: concept.chapter,
        conceptId: concept.id
      })
    }
  }

  const filteredConcepts = concepts.filter((c) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return (
        c.id.toLowerCase().includes(query) ||
        c.name.toLowerCase().includes(query) ||
        c.description?.toLowerCase().includes(query)
      )
    }
    return true
  })

  // Group concepts by chapter
  const conceptsByChapter: Record<string, Concept[]> = {}
  filteredConcepts.forEach((c) => {
    if (!conceptsByChapter[c.chapter]) {
      conceptsByChapter[c.chapter] = []
    }
    conceptsByChapter[c.chapter].push(c)
  })

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BookOpen className="h-7 w-7 text-blue-600" />
            Concepts Manager
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Manage learning concepts for your curriculum
          </p>
        </div>
        
        <div className="flex gap-2">
          <Link
            to="/graph"
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
          >
            <Network className="h-4 w-4" />
            Graph View
          </Link>
          <button
            onClick={() => refetch()}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button
            onClick={handleOpenDialog}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Concept
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex gap-4 flex-wrap">
          <div className="flex-1 min-w-[200px] relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search concepts..."
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
          <select
            value={gradeFilter}
            onChange={(e) => setGradeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white"
          >
            {GRADES.map((g) => (
              <option key={g.value} value={g.value}>{g.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">Failed to load concepts. Make sure the backend is running.</p>
        </div>
      )}

      {/* Concepts Grid */}
      {!isLoading && !error && (
        <div className="space-y-6">
          {Object.keys(conceptsByChapter).length === 0 ? (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-12 text-center">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No concepts found</h3>
              <p className="text-gray-600 mb-4">
                {concepts.length === 0 
                  ? 'Add your first concept or use the Graph Builder to create a concept graph.'
                  : 'No results match your search.'
                }
              </p>
              <div className="flex justify-center gap-3">
                <button
                  onClick={handleOpenDialog}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4" />
                  Add Concept
                </button>
                <Link
                  to="/graph"
                  className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <Network className="h-4 w-4" />
                  Open Graph Builder
                </Link>
              </div>
            </div>
          ) : (
            Object.entries(conceptsByChapter).map(([chapter, chapterConcepts]) => (
              <div key={chapter} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="bg-gray-50 px-6 py-3 border-b flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">
                      {chapter.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <span className="text-sm text-gray-500">
                      ({chapterConcepts.length} concepts)
                    </span>
                  </div>
                  <Link 
                    to={`/graph?chapter=${chapter}`}
                    className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    View Graph <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>
                <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {chapterConcepts.map((c) => (
                    <div
                      key={c.id}
                      className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <code className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                            {c.id}
                          </code>
                        </div>
                        <div className="flex gap-1">
                          <button
                            onClick={() => handleDelete(c)}
                            className="p-1 text-gray-400 hover:text-red-600"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <h4 className="font-medium text-gray-900 mb-1">{c.name}</h4>
                      {c.description && (
                        <p className="text-sm text-gray-500 line-clamp-2">{c.description}</p>
                      )}
                      <div className="flex gap-2 mt-3">
                        <span className="text-xs px-2 py-0.5 bg-gray-100 rounded">
                          Grade {c.grade}
                        </span>
                        <span className="text-xs px-2 py-0.5 bg-gray-100 rounded">
                          {c.subject}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500">
        Total: {filteredConcepts.length} concepts
      </div>

      {/* Add Concept Modal */}
      {dialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold">Add New Concept</h2>
              <button onClick={handleCloseDialog} className="p-1 hover:bg-gray-100 rounded">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Concept ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.id}
                  onChange={(e) => setFormData({ ...formData, id: e.target.value.toLowerCase().replace(/\s/g, '_') })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., factors.identification"
                />
                <p className="text-xs text-gray-500 mt-1">Use dotted notation (e.g., factors.prime_factorization)</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., Factor Identification"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="What this concept covers..."
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Grade</label>
                  <select
                    value={formData.grade}
                    onChange={(e) => setFormData({ ...formData, grade: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
                  >
                    {[3, 4, 5, 6, 7, 8].map((g) => (
                      <option key={g} value={g}>Class {g}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Chapter</label>
                  <input
                    type="text"
                    value={formData.chapter}
                    onChange={(e) => setFormData({ ...formData, chapter: e.target.value.toLowerCase().replace(/\s/g, '_') })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="factors_multiples"
                  />
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
                disabled={createMutation.isPending || !formData.id || !formData.name}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Saving...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
