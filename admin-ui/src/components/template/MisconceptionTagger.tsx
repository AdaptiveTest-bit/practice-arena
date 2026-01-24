import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, Link2, Unlink, Search, BookOpen, Plus } from 'lucide-react'

export interface MisconceptionMapping {
  option_index: number
  misconception_id?: number
  misconception_code?: string
  custom_explanation?: string
}

export interface Misconception {
  id: number
  code: string
  title: string
  description: string
  teaching_point: string
  subject: string
  concept_tags?: string[]
}

interface MisconceptionTaggerProps {
  options: string[]
  correctOptionIndex: number
  mappings: MisconceptionMapping[]
  onChange: (mappings: MisconceptionMapping[]) => void
  conceptId?: string
}

// Fetch misconceptions from API
async function fetchMisconceptions(subject?: string): Promise<Misconception[]> {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002/api'
  try {
    const params = subject ? `?subject=${subject}` : ''
    const response = await fetch(`${API_BASE_URL}/admin/misconceptions${params}`)
    if (!response.ok) throw new Error('Failed to fetch misconceptions')
    return response.json()
  } catch {
    // Return mock data for development
    return [
      {
        id: 1,
        code: 'ARITHMETIC_ERROR',
        title: 'Basic Arithmetic Error',
        description: 'Student makes computation mistakes',
        teaching_point: 'Review basic arithmetic operations',
        subject: 'math',
      },
      {
        id: 2,
        code: 'OPPOSITE_CONFUSION',
        title: 'Opposite Operation Confusion',
        description: 'Student confuses GCD with LCM or similar opposites',
        teaching_point: 'Clarify the difference between related concepts',
        subject: 'math',
      },
      {
        id: 3,
        code: 'INCOMPLETE_REASONING',
        title: 'Incomplete Reasoning',
        description: 'Student only considers part of the problem',
        teaching_point: 'Encourage checking all aspects of the problem',
        subject: 'math',
      },
      {
        id: 4,
        code: 'CONSTRAINT_VIOLATION',
        title: 'Constraint Violation',
        description: 'Student ignores important constraints in the problem',
        teaching_point: 'Review problem constraints carefully',
        subject: 'math',
      },
      {
        id: 5,
        code: 'ONLY_SMALL_FACTORS',
        title: 'Only Considers Small Factors',
        description: 'Student only finds factors up to a certain point',
        teaching_point: 'Factors come in pairs - check systematically',
        subject: 'math',
      },
      {
        id: 6,
        code: 'FORGETS_ONE',
        title: 'Forgets 1 as Factor',
        description: 'Student forgets that 1 is always a factor',
        teaching_point: '1 and the number itself are always factors',
        subject: 'math',
      },
    ]
  }
}

export function MisconceptionTagger({
  options,
  correctOptionIndex,
  mappings,
  onChange,
  conceptId,
}: MisconceptionTaggerProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeOptionIndex, setActiveOptionIndex] = useState<number | null>(null)

  // Extract subject from concept_id (e.g., "math.class5.factors" -> "math")
  const subject = conceptId?.split('.')[0]

  const { data: misconceptions = [], isLoading } = useQuery({
    queryKey: ['misconceptions', subject],
    queryFn: () => fetchMisconceptions(subject),
  })

  const getMapping = (optionIndex: number): MisconceptionMapping | undefined => {
    return mappings.find(m => m.option_index === optionIndex)
  }

  const getMisconception = (mapping?: MisconceptionMapping): Misconception | undefined => {
    if (!mapping) return undefined
    return misconceptions.find(
      m => m.id === mapping.misconception_id || m.code === mapping.misconception_code
    )
  }

  const setMapping = (optionIndex: number, misconception: Misconception | null, customExplanation?: string) => {
    const newMappings = mappings.filter(m => m.option_index !== optionIndex)
    
    if (misconception) {
      newMappings.push({
        option_index: optionIndex,
        misconception_id: misconception.id,
        misconception_code: misconception.code,
        custom_explanation: customExplanation,
      })
    }
    
    onChange(newMappings)
    setActiveOptionIndex(null)
  }

  const updateCustomExplanation = (optionIndex: number, explanation: string) => {
    const newMappings = mappings.map(m => 
      m.option_index === optionIndex 
        ? { ...m, custom_explanation: explanation }
        : m
    )
    onChange(newMappings)
  }

  const filteredMisconceptions = misconceptions.filter(m => 
    searchQuery === '' ||
    m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-5 w-5 text-amber-600" />
        <h3 className="text-sm font-semibold text-gray-900">Misconception Tagging</h3>
        <span className="text-xs text-gray-500">
          ({mappings.length} of {options.length - 1} incorrect options tagged)
        </span>
      </div>

      {/* Help text */}
      <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
        <p className="text-xs text-amber-700">
          Tag each incorrect option with a misconception. This helps provide targeted feedback 
          when students select wrong answers and enables analytics on common mistakes.
        </p>
      </div>

      {/* Options list */}
      <div className="space-y-3">
        {options.map((option, index) => {
          const isCorrect = index === correctOptionIndex
          const mapping = getMapping(index)
          const misconception = getMisconception(mapping)
          const isActive = activeOptionIndex === index

          return (
            <div
              key={index}
              className={`border rounded-lg overflow-hidden ${
                isCorrect 
                  ? 'border-green-300 bg-green-50' 
                  : mapping 
                    ? 'border-amber-300 bg-amber-50'
                    : 'border-gray-200 bg-white'
              }`}
            >
              {/* Option header */}
              <div className="flex items-center gap-3 p-3">
                <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold ${
                  isCorrect 
                    ? 'bg-green-600 text-white' 
                    : 'bg-gray-200 text-gray-700'
                }`}>
                  {String.fromCharCode(65 + index)}
                </span>
                
                <div className="flex-1">
                  <p className="text-sm font-mono text-gray-700">{option || '(empty)'}</p>
                </div>

                {isCorrect ? (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-600 text-white">
                    ✓ Correct
                  </span>
                ) : mapping ? (
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-amber-600 text-white">
                      <Link2 className="h-3 w-3 mr-1" />
                      {misconception?.code || 'Tagged'}
                    </span>
                    <button
                      type="button"
                      onClick={() => setMapping(index, null)}
                      className="text-gray-400 hover:text-danger-600 p-1"
                      title="Remove tag"
                    >
                      <Unlink className="h-4 w-4" />
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setActiveOptionIndex(isActive ? null : index)}
                    className="btn btn-secondary text-xs flex items-center"
                  >
                    <Plus className="h-3 w-3 mr-1" />
                    Tag Misconception
                  </button>
                )}
              </div>

              {/* Misconception details (if tagged) */}
              {!isCorrect && mapping && misconception && (
                <div className="px-3 pb-3 border-t border-amber-200">
                  <div className="mt-2 p-2 bg-white rounded border border-amber-100">
                    <div className="flex items-start gap-2">
                      <BookOpen className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-xs font-semibold text-gray-900">{misconception.title}</p>
                        <p className="text-xs text-gray-600 mt-1">{misconception.description}</p>
                        <p className="text-xs text-amber-700 mt-1">
                          <strong>Teaching point:</strong> {misconception.teaching_point}
                        </p>
                      </div>
                    </div>
                    
                    {/* Custom explanation */}
                    <div className="mt-2">
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Custom explanation (optional)
                      </label>
                      <input
                        type="text"
                        value={mapping.custom_explanation || ''}
                        onChange={(e) => updateCustomExplanation(index, e.target.value)}
                        className="input text-xs"
                        placeholder="Add template-specific explanation..."
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Misconception picker (if active) */}
              {isActive && !isCorrect && (
                <div className="px-3 pb-3 border-t border-gray-200 bg-gray-50">
                  <div className="mt-3">
                    {/* Search */}
                    <div className="relative mb-3">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="input text-sm pl-9"
                        placeholder="Search misconceptions..."
                      />
                    </div>

                    {/* Misconceptions list */}
                    {isLoading ? (
                      <div className="text-center py-4">
                        <p className="text-sm text-gray-500">Loading misconceptions...</p>
                      </div>
                    ) : (
                      <div className="max-h-48 overflow-y-auto space-y-2">
                        {filteredMisconceptions.map(m => (
                          <button
                            key={m.id}
                            type="button"
                            onClick={() => setMapping(index, m)}
                            className="w-full text-left p-2 rounded border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                          >
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono bg-gray-100 px-1.5 py-0.5 rounded">
                                {m.code}
                              </span>
                              <span className="text-sm font-medium text-gray-900">{m.title}</span>
                            </div>
                            <p className="text-xs text-gray-600 mt-1 line-clamp-2">{m.description}</p>
                          </button>
                        ))}
                        {filteredMisconceptions.length === 0 && (
                          <p className="text-center text-sm text-gray-500 py-4">
                            No misconceptions found
                          </p>
                        )}
                      </div>
                    )}

                    {/* Cancel button */}
                    <button
                      type="button"
                      onClick={() => setActiveOptionIndex(null)}
                      className="mt-2 text-xs text-gray-500 hover:text-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Coverage stats */}
      {options.length > 1 && (
        <div className={`p-3 rounded-lg border ${
          mappings.length === options.length - 1 
            ? 'bg-green-50 border-green-200 text-green-700'
            : 'bg-gray-50 border-gray-200 text-gray-600'
        }`}>
          <div className="flex items-center justify-between text-xs">
            <span>Misconception coverage:</span>
            <span className="font-semibold">
              {mappings.length} / {options.length - 1} incorrect options tagged
              {mappings.length === options.length - 1 && ' ✓'}
            </span>
          </div>
          <div className="mt-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-amber-500 transition-all"
              style={{ width: `${(mappings.length / Math.max(options.length - 1, 1)) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
