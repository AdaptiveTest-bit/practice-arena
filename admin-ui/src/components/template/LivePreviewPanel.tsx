import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Play, RefreshCw, CheckCircle, XCircle, Loader2, Eye, EyeOff, Copy, Check } from 'lucide-react'
import toast from 'react-hot-toast'

interface PreviewData {
  success: boolean
  template_id: number
  status: string
  question?: {
    question: string
    options: Array<{ label: string; id: string }>
    solution_steps?: string[]
    visual_hints?: string[]
    rich_narrative?: string
    diagram_url?: string
    richHtmlContent?: string
  }
  variables?: Record<string, any>
  correct_index?: number
  error?: string
  question_pattern?: string
}

interface LivePreviewPanelProps {
  templateId?: string | number
  templateData?: {
    question_pattern: string
    option_patterns: string[]
    solution_pattern?: string
    hint_pattern?: string
    narrative_pattern?: string
    diagram_config?: any
    variable_schema?: any
  }
  onPreviewGenerated?: (preview: PreviewData) => void
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002/api'

async function generatePreview(templateId: string | number): Promise<PreviewData> {
  const response = await fetch(`${API_BASE_URL}/admin/templates/${templateId}/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  
  return response.json()
}

export function LivePreviewPanel({ 
  templateId, 
  templateData,
  onPreviewGenerated 
}: LivePreviewPanelProps) {
  const [previewData, setPreviewData] = useState<PreviewData | null>(null)
  const [showSolution, setShowSolution] = useState(false)
  const [showVariables, setShowVariables] = useState(false)
  const [selectedOption, setSelectedOption] = useState<number | null>(null)
  const [copied, setCopied] = useState(false)

  const previewMutation = useMutation({
    mutationFn: () => {
      if (!templateId) throw new Error('Template ID required')
      return generatePreview(templateId)
    },
    onSuccess: (data) => {
      setPreviewData(data)
      setSelectedOption(null)
      setShowSolution(false)
      onPreviewGenerated?.(data)
      if (data.success) {
        toast.success('Preview generated successfully')
      }
    },
    onError: (error: Error) => {
      toast.error(`Preview failed: ${error.message}`)
    },
  })

  const handleCopyQuestion = async () => {
    if (previewData?.question?.question) {
      await navigator.clipboard.writeText(previewData.question.question)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleOptionSelect = (index: number) => {
    setSelectedOption(index)
    if (previewData?.correct_index !== undefined) {
      if (index === previewData.correct_index) {
        toast.success('Correct! ✓')
      } else {
        toast.error('Incorrect. Try again or view solution.')
      }
    }
  }

  if (!templateId) {
    return (
      <div className="p-6 text-center border-2 border-dashed border-gray-300 rounded-lg">
        <Eye className="h-8 w-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500">Save the template first to generate a preview</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with controls */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Eye className="h-5 w-5 text-primary-600" />
          <h3 className="text-sm font-semibold text-gray-900">Live Preview</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => previewMutation.mutate()}
            disabled={previewMutation.isLoading}
            className="btn btn-primary flex items-center text-sm"
          >
            {previewMutation.isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                Generating...
              </>
            ) : previewData ? (
              <>
                <RefreshCw className="h-4 w-4 mr-1" />
                Regenerate
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-1" />
                Generate Preview
              </>
            )}
          </button>
        </div>
      </div>

      {/* Preview content */}
      {previewData ? (
        <div className="space-y-4">
          {/* Status badge */}
          <div className="flex items-center gap-2">
            {previewData.success ? (
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700">
                <CheckCircle className="h-3 w-3 mr-1" />
                Preview generated from {previewData.status} template
              </span>
            ) : (
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700">
                <XCircle className="h-3 w-3 mr-1" />
                Generation failed
              </span>
            )}
          </div>

          {previewData.success && previewData.question ? (
            <>
              {/* Question card */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gradient-to-r from-primary-50 to-indigo-50 p-4">
                  <div className="flex justify-between items-start">
                    <h4 className="text-lg font-medium text-gray-900">
                      {previewData.question.question}
                    </h4>
                    <button
                      type="button"
                      onClick={handleCopyQuestion}
                      className="text-gray-400 hover:text-gray-600 p-1"
                      title="Copy question"
                    >
                      {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Rich narrative */}
                {previewData.question.rich_narrative && (
                  <div className="px-4 py-3 bg-blue-50 border-t border-blue-100">
                    <p className="text-sm text-blue-700 italic">
                      📖 {previewData.question.rich_narrative}
                    </p>
                  </div>
                )}

                {/* Options */}
                <div className="p-4 space-y-2">
                  {previewData.question.options?.map((option, index) => {
                    const isCorrect = index === previewData.correct_index
                    const isSelected = index === selectedOption
                    const showCorrectness = selectedOption !== null
                    
                    return (
                      <button
                        key={option.id || index}
                        type="button"
                        onClick={() => handleOptionSelect(index)}
                        className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                          showCorrectness
                            ? isCorrect
                              ? 'border-green-500 bg-green-50'
                              : isSelected
                                ? 'border-red-500 bg-red-50'
                                : 'border-gray-200 bg-white'
                            : isSelected
                              ? 'border-primary-500 bg-primary-50'
                              : 'border-gray-200 bg-white hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-sm font-semibold ${
                            showCorrectness && isCorrect
                              ? 'bg-green-600 text-white'
                              : showCorrectness && isSelected
                                ? 'bg-red-600 text-white'
                                : isSelected
                                  ? 'bg-primary-600 text-white'
                                  : 'bg-gray-100 text-gray-700'
                          }`}>
                            {String.fromCharCode(65 + index)}
                          </span>
                          <span className="text-sm text-gray-700">{option.label}</span>
                          {showCorrectness && isCorrect && (
                            <CheckCircle className="h-5 w-5 text-green-600 ml-auto" />
                          )}
                          {showCorrectness && isSelected && !isCorrect && (
                            <XCircle className="h-5 w-5 text-red-600 ml-auto" />
                          )}
                        </div>
                      </button>
                    )
                  })}
                </div>

                {/* Solution toggle */}
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={() => setShowSolution(!showSolution)}
                    className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
                  >
                    {showSolution ? (
                      <>
                        <EyeOff className="h-4 w-4" />
                        Hide Solution
                      </>
                    ) : (
                      <>
                        <Eye className="h-4 w-4" />
                        Show Solution
                      </>
                    )}
                  </button>
                </div>

                {/* Solution content */}
                {showSolution && (
                  <div className="p-4 border-t border-gray-200 space-y-4">
                    {/* Solution steps */}
                    {previewData.question.solution_steps && previewData.question.solution_steps.length > 0 && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <h5 className="text-sm font-semibold text-green-800 mb-2">📝 Solution Steps</h5>
                        <ol className="list-decimal list-inside space-y-1">
                          {previewData.question.solution_steps.map((step, index) => (
                            <li key={index} className="text-sm text-green-700">{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {/* Visual hints */}
                    {previewData.question.visual_hints && previewData.question.visual_hints.length > 0 && (
                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                        <h5 className="text-sm font-semibold text-amber-800 mb-2">💡 Hints</h5>
                        <ol className="list-decimal list-inside space-y-1">
                          {previewData.question.visual_hints.map((hint, index) => (
                            <li key={index} className="text-sm text-amber-700">{hint}</li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {/* Diagram */}
                    {previewData.question.diagram_url && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <h5 className="text-sm font-semibold text-blue-800 mb-2">🎨 Diagram</h5>
                        <img 
                          src={previewData.question.diagram_url} 
                          alt="Question diagram"
                          className="max-w-full h-auto rounded"
                        />
                      </div>
                    )}

                    {/* Rich HTML content (legacy) */}
                    {previewData.question.richHtmlContent && (
                      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
                        <h5 className="text-sm font-semibold text-indigo-800 mb-2">🎨 Visual Content</h5>
                        <div 
                          className="prose prose-sm max-w-none"
                          dangerouslySetInnerHTML={{ __html: previewData.question.richHtmlContent }}
                        />
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Variables used */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <button
                  type="button"
                  onClick={() => setShowVariables(!showVariables)}
                  className="w-full flex justify-between items-center p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <span className="text-sm font-medium text-gray-700">
                    Variables Used
                  </span>
                  <span className="text-xs text-gray-500">
                    {showVariables ? '▼' : '▶'}
                  </span>
                </button>
                {showVariables && previewData.variables && (
                  <div className="p-3 border-t border-gray-200">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {Object.entries(previewData.variables).map(([key, value]) => (
                        <div key={key} className="p-2 bg-gray-50 rounded">
                          <span className="text-xs font-mono text-gray-500">{key}</span>
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            /* Error state */
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <h4 className="text-sm font-semibold text-red-800 mb-2">Generation Error</h4>
              <p className="text-sm text-red-700">{previewData.error}</p>
              {previewData.question_pattern && (
                <div className="mt-3 p-2 bg-white rounded border border-red-100">
                  <span className="text-xs text-gray-500">Question pattern:</span>
                  <p className="text-sm font-mono text-gray-700">{previewData.question_pattern}</p>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        /* Empty state */
        <div className="p-8 text-center border-2 border-dashed border-gray-300 rounded-lg">
          <Play className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 mb-2">Click "Generate Preview" to see how your template looks</p>
          <p className="text-xs text-gray-400">
            This will generate a sample question with random variables
          </p>
        </div>
      )}
    </div>
  )
}
