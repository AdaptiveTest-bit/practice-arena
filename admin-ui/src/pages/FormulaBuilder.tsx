import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  Save, Play, CheckCircle, XCircle, Plus, Trash2, 
  Code, BookOpen, FlaskConical, Sparkles, AlertTriangle, RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

/**
 * Formula Builder
 * 
 * Allows content writers to create custom formulas for use in templates.
 * Features:
 * - Code editor with syntax highlighting hints
 * - Parameter definition
 * - Test case runner
 * - Live preview
 * - Publish workflow
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5002'

// ============================================================
// TYPES
// ============================================================

interface FormulaParameter {
  name: string
  type: 'integer' | 'float' | 'string' | 'list' | 'boolean'
  description: string
  default_value?: any
}

interface TestCase {
  input: any[]
  expected: any
}

interface TestResult {
  index: number
  input: any[]
  expected: any
  actual: any
  passed: boolean
  error: string | null
}

interface Formula {
  id?: string
  name: string
  display_name: string
  category: string
  parameters: FormulaParameter[]
  return_type: string
  code: string
  description: string
  example_usage: string
  test_cases: TestCase[]
  status: 'DRAFT' | 'TESTING' | 'ACTIVE' | 'DEPRECATED'
}

const CATEGORIES = [
  { value: 'Number Theory', label: '🔢 Number Theory' },
  { value: 'Fractions', label: '🥧 Fractions' },
  { value: 'Geometry', label: '📐 Geometry' },
  { value: 'Algebra', label: '📊 Algebra' },
  { value: 'Statistics', label: '📈 Statistics' },
  { value: 'General', label: '⚙️ General' },
]

const PARAM_TYPES = [
  { value: 'integer', label: 'Integer' },
  { value: 'float', label: 'Float' },
  { value: 'string', label: 'String' },
  { value: 'list', label: 'List' },
  { value: 'boolean', label: 'Boolean' },
]

const RETURN_TYPES = [
  { value: 'integer', label: 'Integer' },
  { value: 'float', label: 'Float' },
  { value: 'boolean', label: 'Boolean' },
  { value: 'string', label: 'String' },
  { value: 'list', label: 'List' },
  { value: 'tuple', label: 'Tuple' },
  { value: 'any', label: 'Any' },
]

// ============================================================
// API FUNCTIONS
// ============================================================

async function fetchFormula(id: string): Promise<Formula> {
  const res = await fetch(`${API_BASE}/api/admin/formulas/${id}`)
  if (!res.ok) throw new Error('Failed to fetch formula')
  return res.json()
}

async function saveFormula(formula: Formula): Promise<Formula> {
  const url = formula.id 
    ? `${API_BASE}/api/admin/formulas/${formula.id}`
    : `${API_BASE}/api/admin/formulas`
  
  const res = await fetch(url, {
    method: formula.id ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formula)
  })
  
  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || 'Failed to save formula')
  }
  return res.json()
}

async function validateFormula(id: string): Promise<{ is_valid: boolean; error: string | null; test_results: TestResult[] }> {
  const res = await fetch(`${API_BASE}/api/admin/formulas/${id}/validate`, {
    method: 'POST'
  })
  if (!res.ok) throw new Error('Validation failed')
  return res.json()
}

async function publishFormula(id: string): Promise<Formula> {
  const res = await fetch(`${API_BASE}/api/admin/formulas/${id}/publish`, {
    method: 'POST'
  })
  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || 'Failed to publish')
  }
  return res.json()
}

async function testCodePreview(code: string, functionName: string, testInput: any[]): Promise<{ success: boolean; result: any; error: string | null }> {
  const res = await fetch(`${API_BASE}/api/admin/formulas/preview/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code,
      function_name: functionName,
      test_input: testInput
    })
  })
  return res.json()
}

async function reloadFormulasIntoEngine(): Promise<{ success: boolean; count: number; message: string }> {
  const res = await fetch(`${API_BASE}/api/admin/formulas/reload`, {
    method: 'POST'
  })
  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || 'Failed to reload formulas')
  }
  return res.json()
}

// ============================================================
// HELPER FUNCTIONS
// ============================================================

function generateFunctionTemplate(name: string, params: FormulaParameter[]): string {
  const paramList = params.map(p => p.name).join(', ')
  return `def ${name}(${paramList}):
    """
    ${params.map(p => `${p.name}: ${p.description}`).join('\n    ')}
    """
    # Your code here
    result = None
    return result`
}

// ============================================================
// MAIN COMPONENT
// ============================================================

export function FormulaBuilder() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  // Form state
  const [formula, setFormula] = useState<Formula>({
    name: '',
    display_name: '',
    category: 'General',
    parameters: [],
    return_type: 'any',
    code: '',
    description: '',
    example_usage: '',
    test_cases: [],
    status: 'DRAFT'
  })
  
  // UI state
  const [testResults, setTestResults] = useState<TestResult[]>([])
  const [liveTestInput, setLiveTestInput] = useState<string>('')
  const [liveTestResult, setLiveTestResult] = useState<{ success: boolean; result: any; error: string | null } | null>(null)
  const [isTestingLive, setIsTestingLive] = useState(false)
  
  // Fetch existing formula
  const { data: existingFormula, isLoading } = useQuery({
    queryKey: ['formula', id],
    queryFn: () => id ? fetchFormula(id) : Promise.resolve(null),
    enabled: !!id
  })
  
  useEffect(() => {
    if (existingFormula) {
      setFormula(existingFormula)
    }
  }, [existingFormula])
  
  // Mutations
  const saveMutation = useMutation({
    mutationFn: saveFormula,
    onSuccess: (data) => {
      toast.success('Formula saved!')
      queryClient.invalidateQueries({ queryKey: ['formulas'] })
      if (!id && data.id) {
        navigate(`/formulas/${data.id}/edit`)
      }
      setFormula(data)
    },
    onError: (err: Error) => toast.error(err.message)
  })
  
  const validateMutation = useMutation({
    mutationFn: () => validateFormula(formula.id!),
    onSuccess: (data) => {
      setTestResults(data.test_results || [])
      if (data.is_valid) {
        toast.success('All tests passed! ✅')
      } else {
        toast.error(data.error || 'Some tests failed')
      }
    },
    onError: (err: Error) => toast.error(err.message)
  })
  
  const publishMutation = useMutation({
    mutationFn: () => publishFormula(formula.id!),
    onSuccess: (data) => {
      toast.success('Formula published! 🎉')
      setFormula(data)
      queryClient.invalidateQueries({ queryKey: ['formulas'] })
    },
    onError: (err: Error) => toast.error(err.message)
  })
  
  const reloadMutation = useMutation({
    mutationFn: reloadFormulasIntoEngine,
    onSuccess: (data) => {
      toast.success(`${data.count} formulas loaded into template engine! 🔄`)
    },
    onError: (err: Error) => toast.error(err.message)
  })
  
  // Handlers
  const handleAddParameter = () => {
    setFormula(prev => ({
      ...prev,
      parameters: [...prev.parameters, { name: '', type: 'integer', description: '' }]
    }))
  }
  
  const handleRemoveParameter = (index: number) => {
    setFormula(prev => ({
      ...prev,
      parameters: prev.parameters.filter((_, i) => i !== index)
    }))
  }
  
  const handleParameterChange = (index: number, field: keyof FormulaParameter, value: any) => {
    setFormula(prev => ({
      ...prev,
      parameters: prev.parameters.map((p, i) => 
        i === index ? { ...p, [field]: value } : p
      )
    }))
  }
  
  const handleAddTestCase = () => {
    setFormula(prev => ({
      ...prev,
      test_cases: [...prev.test_cases, { input: [], expected: null }]
    }))
  }
  
  const handleRemoveTestCase = (index: number) => {
    setFormula(prev => ({
      ...prev,
      test_cases: prev.test_cases.filter((_, i) => i !== index)
    }))
  }
  
  const handleTestCaseChange = (index: number, field: 'input' | 'expected', value: string) => {
    try {
      const parsed = JSON.parse(value)
      setFormula(prev => ({
        ...prev,
        test_cases: prev.test_cases.map((tc, i) =>
          i === index ? { ...tc, [field]: parsed } : tc
        )
      }))
    } catch {
      // Keep as string if not valid JSON
    }
  }
  
  const handleGenerateTemplate = () => {
    if (formula.name && formula.parameters.length > 0) {
      setFormula(prev => ({
        ...prev,
        code: generateFunctionTemplate(prev.name, prev.parameters)
      }))
    }
  }
  
  const handleLiveTest = async () => {
    if (!formula.code || !formula.name || !liveTestInput) return
    
    setIsTestingLive(true)
    try {
      const input = JSON.parse(liveTestInput)
      const result = await testCodePreview(formula.code, formula.name, Array.isArray(input) ? input : [input])
      setLiveTestResult(result)
    } catch (err: any) {
      setLiveTestResult({ success: false, result: null, error: err.message })
    } finally {
      setIsTestingLive(false)
    }
  }
  
  if (isLoading && id) {
    return (
      <div className="p-6 max-w-5xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FlaskConical className="h-7 w-7 text-purple-600" />
            {id ? 'Edit Formula' : '🧮 Create Custom Formula'}
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Define reusable formulas for question templates
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Status Badge */}
          {formula.status && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              formula.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
              formula.status === 'TESTING' ? 'bg-yellow-100 text-yellow-800' :
              formula.status === 'DEPRECATED' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {formula.status}
            </span>
          )}
          
          {/* Save Button */}
          <button
            onClick={() => saveMutation.mutate(formula)}
            disabled={saveMutation.isPending || !formula.name || !formula.code}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Save className="h-4 w-4" />
            {saveMutation.isPending ? 'Saving...' : 'Save'}
          </button>
          
          {/* Validate Button */}
          {formula.id && (
            <button
              onClick={() => validateMutation.mutate()}
              disabled={validateMutation.isPending}
              className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Play className="h-4 w-4" />
              Run Tests
            </button>
          )}
          
          {/* Publish Button */}
          {formula.id && formula.status !== 'ACTIVE' && (
            <button
              onClick={() => publishMutation.mutate()}
              disabled={publishMutation.isPending || formula.test_cases.length === 0}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Sparkles className="h-4 w-4" />
              Publish
            </button>
          )}
          
          {/* Reload Engine Button - shown for ACTIVE formulas */}
          {formula.status === 'ACTIVE' && (
            <button
              onClick={() => reloadMutation.mutate()}
              disabled={reloadMutation.isPending}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
              title="Load this formula into the template engine"
            >
              <RefreshCw className={`h-4 w-4 ${reloadMutation.isPending ? 'animate-spin' : ''}`} />
              {reloadMutation.isPending ? 'Loading...' : 'Reload Engine'}
            </button>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-6">
        {/* Left Column: Definition */}
        <div className="space-y-6">
          {/* Basic Info */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-blue-600" />
              Formula Definition
            </h2>
            
            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Function Name *
                </label>
                <input
                  type="text"
                  value={formula.name}
                  onChange={(e) => setFormula(prev => ({ ...prev, name: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '_') }))}
                  placeholder="add_fractions"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">lowercase, underscores only</p>
              </div>
              
              {/* Display Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Display Name *
                </label>
                <input
                  type="text"
                  value={formula.display_name}
                  onChange={(e) => setFormula(prev => ({ ...prev, display_name: e.target.value }))}
                  placeholder="Add Two Fractions"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={formula.category}
                  onChange={(e) => setFormula(prev => ({ ...prev, category: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {CATEGORIES.map(c => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                  ))}
                </select>
              </div>
              
              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formula.description}
                  onChange={(e) => setFormula(prev => ({ ...prev, description: e.target.value }))}
                  rows={2}
                  placeholder="Adds two fractions and returns simplified result"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>
          
          {/* Parameters */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                📥 Parameters
              </h2>
              <button
                onClick={handleAddParameter}
                className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 flex items-center gap-1"
              >
                <Plus className="h-4 w-4" />
                Add
              </button>
            </div>
            
            {formula.parameters.length === 0 ? (
              <p className="text-gray-500 text-sm">No parameters defined</p>
            ) : (
              <div className="space-y-3">
                {formula.parameters.map((param, i) => (
                  <div key={i} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                    <input
                      type="text"
                      value={param.name}
                      onChange={(e) => handleParameterChange(i, 'name', e.target.value)}
                      placeholder="name"
                      className="w-24 px-2 py-1 border rounded font-mono text-sm"
                    />
                    <select
                      value={param.type}
                      onChange={(e) => handleParameterChange(i, 'type', e.target.value)}
                      className="w-24 px-2 py-1 border rounded text-sm"
                    >
                      {PARAM_TYPES.map(t => (
                        <option key={t.value} value={t.value}>{t.label}</option>
                      ))}
                    </select>
                    <input
                      type="text"
                      value={param.description}
                      onChange={(e) => handleParameterChange(i, 'description', e.target.value)}
                      placeholder="Description"
                      className="flex-1 px-2 py-1 border rounded text-sm"
                    />
                    <button
                      onClick={() => handleRemoveParameter(i)}
                      className="p-1 text-red-500 hover:bg-red-100 rounded"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {/* Return Type */}
            <div className="mt-4 pt-4 border-t">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Return Type
              </label>
              <select
                value={formula.return_type}
                onChange={(e) => setFormula(prev => ({ ...prev, return_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                {RETURN_TYPES.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
        
        {/* Right Column: Code & Testing */}
        <div className="space-y-6">
          {/* Code Editor */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Code className="h-5 w-5 text-purple-600" />
                Python Code
              </h2>
              <button
                onClick={handleGenerateTemplate}
                disabled={!formula.name}
                className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
              >
                Generate Template
              </button>
            </div>
            
            <textarea
              value={formula.code}
              onChange={(e) => setFormula(prev => ({ ...prev, code: e.target.value }))}
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm bg-gray-900 text-green-400"
              placeholder={`def ${formula.name || 'my_function'}(a, b):
    # Available: math.gcd, math.lcm, math.sqrt, etc.
    result = a + b
    return result`}
              style={{ tabSize: 4 }}
            />
            
            <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-sm text-amber-800 flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Available:</strong> math.gcd, math.lcm, math.sqrt, math.floor, math.ceil, 
                  abs, min, max, sum, len, sorted, range, list, tuple
                </span>
              </p>
            </div>
          </div>
          
          {/* Live Test */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4">⚡ Quick Test</h2>
            
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={liveTestInput}
                onChange={(e) => setLiveTestInput(e.target.value)}
                placeholder='[1, 2, 1, 3] or {"a": 1, "b": 2}'
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
              />
              <button
                onClick={handleLiveTest}
                disabled={isTestingLive || !formula.code}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {isTestingLive ? '...' : 'Run'}
              </button>
            </div>
            
            {liveTestResult && (
              <div className={`p-3 rounded-lg ${liveTestResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                {liveTestResult.success ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="font-mono">{JSON.stringify(liveTestResult.result)}</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <XCircle className="h-5 w-5 text-red-600" />
                    <span className="text-red-700">{liveTestResult.error}</span>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Test Cases */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">🧪 Test Cases</h2>
              <button
                onClick={handleAddTestCase}
                className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 flex items-center gap-1"
              >
                <Plus className="h-4 w-4" />
                Add Test
              </button>
            </div>
            
            {formula.test_cases.length === 0 ? (
              <p className="text-gray-500 text-sm">Add test cases to validate your formula</p>
            ) : (
              <div className="space-y-3">
                {formula.test_cases.map((tc, i) => {
                  const result = testResults[i]
                  return (
                    <div key={i} className={`p-3 rounded-lg border ${
                      result?.passed ? 'bg-green-50 border-green-200' :
                      result?.passed === false ? 'bg-red-50 border-red-200' :
                      'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        {result?.passed === true && <CheckCircle className="h-4 w-4 text-green-600" />}
                        {result?.passed === false && <XCircle className="h-4 w-4 text-red-600" />}
                        <span className="text-sm font-medium">Test {i + 1}</span>
                        <button
                          onClick={() => handleRemoveTestCase(i)}
                          className="ml-auto p-1 text-red-500 hover:bg-red-100 rounded"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="text-xs text-gray-500">Input (JSON array)</label>
                          <input
                            type="text"
                            value={JSON.stringify(tc.input)}
                            onChange={(e) => handleTestCaseChange(i, 'input', e.target.value)}
                            className="w-full px-2 py-1 border rounded font-mono text-xs"
                            placeholder="[1, 2, 3]"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Expected (JSON)</label>
                          <input
                            type="text"
                            value={JSON.stringify(tc.expected)}
                            onChange={(e) => handleTestCaseChange(i, 'expected', e.target.value)}
                            className="w-full px-2 py-1 border rounded font-mono text-xs"
                            placeholder="6"
                          />
                        </div>
                      </div>
                      {result?.error && (
                        <p className="mt-2 text-xs text-red-600">{result.error}</p>
                      )}
                      {result && !result.passed && result.actual !== null && (
                        <p className="mt-2 text-xs text-amber-600">
                          Got: {JSON.stringify(result.actual)}
                        </p>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
            
            {/* Example Usage */}
            <div className="mt-4 pt-4 border-t">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Example Usage
              </label>
              <input
                type="text"
                value={formula.example_usage}
                onChange={(e) => setFormula(prev => ({ ...prev, example_usage: e.target.value }))}
                placeholder="add_fractions(1, 2, 1, 3) → (5, 6)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FormulaBuilder
