import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { Save, Eye, Play, Plus, Trash2 } from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'

interface Template {
  id?: string
  name: string
  concept_id: string
  template_code: string
  question_pattern: string
  variable_schema: object
  answer_logic: string
  option_patterns: string[]
  difficulty: number
  bloom_level: string
  estimated_time: number
  status: 'DRAFT' | 'REVIEW' | 'APPROVED' | 'PUBLISHED'
  created_by?: string
}

interface Diagram {
  id?: string
  name: string
  diagram_type: string
  variables: object
  alt_text?: string
}

interface TemplateFormData extends Template {
  diagrams: Diagram[]
}

async function fetchTemplate(id: string): Promise<Template> {
  // Mock data - replace with actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: '1',
        name: 'Factors of a Number',
        concept_id: 'factors_multiples.find_factors',
        template_code: 'def generate():\n    number = random.randint(10, 50)\n    factors = get_factors(number)\n    return {"number": number, "factors": factors}',
        question_pattern: 'Find all factors of {{number}}',
        variable_schema: {
          type: 'object',
          properties: {
            number: { type: 'integer', minimum: 10, maximum: 50 }
          }
        },
        answer_logic: 'variables["factors"]',
        option_patterns: ['{{factors}}', '{{factors[:-1]}}', '{{factors[1:]}}', '{{factors[:2]}}'],
        difficulty: 2,
        bloom_level: 'UNDERSTAND',
        estimated_time: 45,
        status: 'DRAFT',
        created_by: 'John Doe'
      })
    }, 500)
  })
}

async function saveTemplate(template: TemplateFormData): Promise<Template> {
  // Mock save - replace with actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ ...template, id: template.id || Date.now().toString() })
    }, 1000)
  })
}

async function previewTemplate(template: Template): Promise<any> {
  // Mock preview - replace with actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        question: 'Find all factors of 24',
        options: ['1, 2, 3, 4, 6, 8, 12, 24', '2, 4, 6, 8, 12, 24', '1, 3, 4, 6, 8, 24', '1, 2, 4, 6, 12, 24'],
        diagrams: [
          {
            url: 'https://cdn.example.com/diagrams/factors_abc123.svg',
            name: 'Factors Diagram'
          }
        ]
      })
    }, 500)
  })
}

export function TemplateEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'edit' | 'preview'>('edit')
  const [previewData, setPreviewData] = useState<any>(null)
  const [isPreviewLoading, setIsPreviewLoading] = useState(false)

  const { data: template, isLoading } = useQuery({
    queryKey: ['template', id],
    queryFn: () => id ? fetchTemplate(id) : Promise.resolve({} as Template),
    enabled: !!id,
  })

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isDirty }
  } = useForm<TemplateFormData>({
    defaultValues: template || {
      name: '',
      concept_id: '',
      template_code: '',
      question_pattern: '',
      variable_schema: {},
      answer_logic: '',
      option_patterns: [],
      difficulty: 1,
      bloom_level: 'REMEMBER',
      estimated_time: 30,
      status: 'DRAFT',
      diagrams: []
    }
  })

  const saveMutation = useMutation({
    mutationFn: saveTemplate,
    onSuccess: (data) => {
      toast.success('Template saved successfully')
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      if (!id) {
        navigate(`/templates/${data.id}/edit`)
      }
    },
    onError: () => {
      toast.error('Failed to save template')
    },
  })

  const onSubmit = (data: TemplateFormData) => {
    saveMutation.mutate(data)
  }

  const handlePreview = async () => {
    setIsPreviewLoading(true)
    try {
      const formData = watch()
      const preview = await previewTemplate(formData)
      setPreviewData(preview)
      setActiveTab('preview')
    } catch (error) {
      toast.error('Failed to generate preview')
    } finally {
      setIsPreviewLoading(false)
    }
  }

  const addOptionPattern = () => {
    const current = watch('option_patterns') || []
    setValue('option_patterns', [...current, ''])
  }

  const removeOptionPattern = (index: number) => {
    const current = watch('option_patterns') || []
    setValue('option_patterns', current.filter((_, i) => i !== index))
  }

  const addDiagram = () => {
    const current = watch('diagrams') || []
    setValue('diagrams', [
      ...current,
      {
        name: '',
        diagram_type: 'factors',
        variables: {},
        alt_text: ''
      }
    ])
  }

  const removeDiagram = (index: number) => {
    const current = watch('diagrams') || []
    setValue('diagrams', current.filter((_, i) => i !== index))
  }

  if (isLoading && id) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {id ? 'Edit Template' : 'Create New Template'}
          </h1>
          <p className="text-gray-600">
            {id ? 'Modify your question template' : 'Create a new question template'}
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handlePreview}
            disabled={isPreviewLoading}
            className="btn btn-secondary flex items-center"
          >
            <Eye className="h-4 w-4 mr-2" />
            {isPreviewLoading ? 'Loading...' : 'Preview'}
          </button>
          <button
            onClick={handleSubmit(onSubmit)}
            disabled={saveMutation.isLoading || !isDirty}
            className="btn btn-primary flex items-center"
          >
            <Save className="h-4 w-4 mr-2" />
            {saveMutation.isLoading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('edit')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'edit'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Edit Template
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'preview'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Preview
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'edit' ? (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Information */}
          <div className="card">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Template Name *
                  </label>
                  <input
                    {...register('name', { required: 'Template name is required' })}
                    type="text"
                    className="input"
                    placeholder="e.g., Factors of a Number"
                  />
                  {errors.name && (
                    <p className="text-danger-600 text-sm mt-1">{errors.name.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Concept ID *
                  </label>
                  <input
                    {...register('concept_id', { required: 'Concept ID is required' })}
                    type="text"
                    className="input"
                    placeholder="e.g., factors_multiples.find_factors"
                  />
                  {errors.concept_id && (
                    <p className="text-danger-600 text-sm mt-1">{errors.concept_id.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty
                  </label>
                  <select {...register('difficulty')} className="input">
                    <option value={1}>Easy (1)</option>
                    <option value={2}>Medium (2)</option>
                    <option value={3}>Hard (3)</option>
                    <option value={4}>Expert (4)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bloom's Level
                  </label>
                  <select {...register('bloom_level')} className="input">
                    <option value="REMEMBER">Remember</option>
                    <option value="UNDERSTAND">Understand</option>
                    <option value="APPLY">Apply</option>
                    <option value="ANALYZE">Analyze</option>
                    <option value="EVALUATE">Evaluate</option>
                    <option value="CREATE">Create</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Estimated Time (seconds)
                  </label>
                  <input
                    {...register('estimated_time')}
                    type="number"
                    className="input"
                    placeholder="30"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select {...register('status')} className="input">
                    <option value="DRAFT">Draft</option>
                    <option value="REVIEW">Ready for Review</option>
                    <option value="APPROVED">Approved</option>
                    <option value="PUBLISHED">Published</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Template Content */}
          <div className="card">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Template Content</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Question Pattern *
                  </label>
                  <input
                    {...register('question_pattern', { required: 'Question pattern is required' })}
                    type="text"
                    className="input"
                    placeholder="e.g., Find all factors of {{number}}"
                  />
                  {errors.question_pattern && (
                    <p className="text-danger-600 text-sm mt-1">{errors.question_pattern.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Template Code (Python) *
                  </label>
                  <textarea
                    {...register('template_code', { required: 'Template code is required' })}
                    rows={8}
                    className="input font-mono text-sm"
                    placeholder="def generate():&#10;    number = random.randint(10, 50)&#10;    factors = get_factors(number)&#10;    return {&quot;number&quot;: number, &quot;factors&quot;: factors}"
                  />
                  {errors.template_code && (
                    <p className="text-danger-600 text-sm mt-1">{errors.template_code.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Answer Logic *
                  </label>
                  <input
                    {...register('answer_logic', { required: 'Answer logic is required' })}
                    type="text"
                    className="input font-mono text-sm"
                    placeholder="variables[&quot;factors&quot;]"
                  />
                  {errors.answer_logic && (
                    <p className="text-danger-600 text-sm mt-1">{errors.answer_logic.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Option Patterns */}
          <div className="card">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Option Patterns</h2>
                <button
                  type="button"
                  onClick={addOptionPattern}
                  className="btn btn-secondary flex items-center text-sm"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Add Option
                </button>
              </div>
              <div className="space-y-2">
                {(watch('option_patterns') || []).map((pattern: string, index: number) => (
                  <div key={index} className="flex gap-2">
                    <input
                      {...register(`option_patterns.${index}`)}
                      type="text"
                      className="input font-mono text-sm flex-1"
                      placeholder="e.g., {{factors}}"
                    />
                    <button
                      type="button"
                      onClick={() => removeOptionPattern(index)}
                      className="btn btn-danger text-sm"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Diagrams */}
          <div className="card">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Diagrams</h2>
                <button
                  type="button"
                  onClick={addDiagram}
                  className="btn btn-secondary flex items-center text-sm"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Add Diagram
                </button>
              </div>
              <div className="space-y-4">
                {(watch('diagrams') || []).map((diagram: Diagram, index: number) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-sm font-medium text-gray-900">Diagram {index + 1}</h3>
                      <button
                        type="button"
                        onClick={() => removeDiagram(index)}
                        className="btn btn-danger text-sm"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Name
                        </label>
                        <input
                          {...register(`diagrams.${index}.name`)}
                          type="text"
                          className="input"
                          placeholder="e.g., Factors Diagram"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Type
                        </label>
                        <select {...register(`diagrams.${index}.diagram_type`)} className="input">
                          <option value="factors">Factors</option>
                          <option value="multiples">Multiples</option>
                          <option value="gcd">GCD</option>
                          <option value="lcm">LCM</option>
                          <option value="divisibility">Divisibility</option>
                          <option value="prime_composite">Prime/Composite</option>
                          <option value="factor_pairs">Factor Pairs</option>
                          <option value="prime_factorization">Prime Factorization</option>
                        </select>
                      </div>
                    </div>
                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Alt Text
                      </label>
                      <input
                        {...register(`diagrams.${index}.alt_text`)}
                        type="text"
                        className="input"
                        placeholder="Accessibility description"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </form>
      ) : (
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Preview</h2>
            {previewData ? (
              <div className="space-y-4">
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {previewData.question}
                  </h3>
                  <div className="space-y-2">
                    {previewData.options?.map((option: string, index: number) => (
                      <div key={index} className="flex items-center">
                        <input
                          type="radio"
                          name="preview-option"
                          className="mr-2"
                          disabled
                        />
                        <label className="text-gray-700">{option}</label>
                      </div>
                    ))}
                  </div>
                  {previewData.diagrams?.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Diagrams:</h4>
                      <div className="space-y-2">
                        {previewData.diagrams.map((diagram: any, index: number) => (
                          <div key={index} className="border border-gray-200 rounded p-2">
                            <p className="text-sm text-gray-600">{diagram.name}</p>
                            <img
                              src={diagram.url}
                              alt={diagram.name}
                              className="mt-2 max-w-full h-auto"
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">Click "Preview" to see how your template will look</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
