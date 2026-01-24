import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  Plus, Search, FlaskConical, CheckCircle, Clock, 
  AlertTriangle, Code, ChevronRight 
} from 'lucide-react'

/**
 * Formula List Page
 * 
 * Lists all custom formulas with filtering and search.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5002'

interface Formula {
  id: string
  name: string
  display_name: string
  category: string
  parameters: { name: string; type: string }[]
  return_type: string
  description: string
  status: 'DRAFT' | 'TESTING' | 'ACTIVE' | 'DEPRECATED'
  created_at: string
}

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'Number Theory', label: '🔢 Number Theory' },
  { value: 'Fractions', label: '🥧 Fractions' },
  { value: 'Geometry', label: '📐 Geometry' },
  { value: 'Algebra', label: '📊 Algebra' },
  { value: 'Statistics', label: '📈 Statistics' },
  { value: 'General', label: '⚙️ General' },
]

async function fetchFormulas(category?: string, status?: string, search?: string): Promise<Formula[]> {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (status) params.set('status', status)
  if (search) params.set('search', search)
  
  const res = await fetch(`${API_BASE}/api/admin/formulas?${params}`)
  if (!res.ok) throw new Error('Failed to fetch formulas')
  return res.json()
}

export function FormulaList() {
  const [category, setCategory] = useState('')
  const [status, setStatus] = useState('')
  const [search, setSearch] = useState('')
  
  const { data: formulas, isLoading, error } = useQuery({
    queryKey: ['formulas', category, status, search],
    queryFn: () => fetchFormulas(category, status, search)
  })
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'TESTING':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'DEPRECATED':
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      default:
        return <Code className="h-4 w-4 text-gray-600" />
    }
  }
  
  const getStatusBadge = (status: string) => {
    const styles = {
      ACTIVE: 'bg-green-100 text-green-800',
      TESTING: 'bg-yellow-100 text-yellow-800',
      DEPRECATED: 'bg-red-100 text-red-800',
      DRAFT: 'bg-gray-100 text-gray-800'
    }
    return styles[status as keyof typeof styles] || styles.DRAFT
  }
  
  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FlaskConical className="h-7 w-7 text-purple-600" />
            Formula Library
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Custom formulas for question templates
          </p>
        </div>
        
        <Link
          to="/formulas/new"
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Create Formula
        </Link>
      </div>
      
      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search formulas..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          
          {/* Category Filter */}
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            {CATEGORIES.map(c => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
          
          {/* Status Filter */}
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Status</option>
            <option value="ACTIVE">✅ Active</option>
            <option value="DRAFT">📝 Draft</option>
            <option value="TESTING">🧪 Testing</option>
            <option value="DEPRECATED">⚠️ Deprecated</option>
          </select>
        </div>
      </div>
      
      {/* Formula Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-10 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <p className="text-red-700">Failed to load formulas. Make sure the backend is running.</p>
        </div>
      ) : formulas?.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-12 text-center">
          <FlaskConical className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No formulas yet</h3>
          <p className="text-gray-600 mb-4">Create your first custom formula to get started.</p>
          <Link
            to="/formulas/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            <Plus className="h-4 w-4" />
            Create Formula
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {formulas?.map(formula => (
            <Link
              key={formula.id}
              to={`/formulas/${formula.id}/edit`}
              className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md hover:border-purple-300 transition-all group"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getStatusIcon(formula.status)}
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(formula.status)}`}>
                    {formula.status}
                  </span>
                </div>
                <span className="text-xs text-gray-500">{formula.category}</span>
              </div>
              
              <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-purple-700">
                {formula.display_name}
              </h3>
              
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {formula.description || 'No description'}
              </p>
              
              <div className="flex items-center justify-between">
                <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                  {formula.name}({formula.parameters.map(p => p.name).join(', ')})
                </code>
                <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-purple-600" />
              </div>
            </Link>
          ))}
        </div>
      )}
      
      {/* Stats */}
      {formulas && formulas.length > 0 && (
        <div className="mt-6 flex gap-4 text-sm text-gray-600">
          <span>
            <strong>{formulas.filter(f => f.status === 'ACTIVE').length}</strong> active
          </span>
          <span>
            <strong>{formulas.filter(f => f.status === 'DRAFT').length}</strong> drafts
          </span>
          <span>
            <strong>{formulas.length}</strong> total
          </span>
        </div>
      )}
    </div>
  )
}

export default FormulaList
