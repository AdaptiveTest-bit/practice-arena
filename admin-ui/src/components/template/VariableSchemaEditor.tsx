import React from 'react'
import { Plus, Trash2, Settings2, HelpCircle } from 'lucide-react'

export interface VariableDefinition {
  name: string
  type: 'integer' | 'float' | 'string' | 'boolean' | 'array' | 'choice'
  min?: number
  max?: number
  choices?: string[]
  description?: string
  constraints?: string
}

interface VariableSchemaEditorProps {
  schema: Record<string, any>
  onChange: (schema: Record<string, any>) => void
}

const VARIABLE_TYPES = [
  { value: 'integer', label: 'Integer', icon: '#', hasRange: true },
  { value: 'float', label: 'Decimal', icon: '.0', hasRange: true },
  { value: 'string', label: 'Text', icon: 'Aa', hasRange: false },
  { value: 'boolean', label: 'Yes/No', icon: '✓', hasRange: false },
  { value: 'choice', label: 'Choice', icon: '▼', hasRange: false, hasChoices: true },
  { value: 'array', label: 'List', icon: '[]', hasRange: false },
]

export function VariableSchemaEditor({ schema, onChange }: VariableSchemaEditorProps) {
  // Convert schema object to array for editing
  const variables: VariableDefinition[] = React.useMemo(() => {
    if (!schema || typeof schema !== 'object') return []
    
    // Handle JSON Schema format
    if (schema.properties) {
      return Object.entries(schema.properties).map(([name, def]: [string, any]) => ({
        name,
        type: def.enum ? 'choice' : (def.type || 'string'),
        min: def.minimum,
        max: def.maximum,
        choices: def.enum,
        description: def.description,
        constraints: def.constraints,
      }))
    }
    
    // Handle direct format
    return Object.entries(schema).map(([name, def]: [string, any]) => ({
      name,
      type: def.type || 'string',
      min: def.min || def.minimum,
      max: def.max || def.maximum,
      choices: def.choices || def.enum,
      description: def.description,
      constraints: def.constraints,
    }))
  }, [schema])

  // Convert array back to schema object
  const updateSchema = (newVariables: VariableDefinition[]) => {
    const newSchema: Record<string, any> = {
      type: 'object',
      properties: {},
    }
    
    newVariables.forEach(v => {
      const prop: any = {
        type: v.type === 'choice' ? 'string' : v.type,
      }
      if (v.min !== undefined) prop.minimum = v.min
      if (v.max !== undefined) prop.maximum = v.max
      if (v.choices && v.choices.length > 0) prop.enum = v.choices
      if (v.description) prop.description = v.description
      if (v.constraints) prop.constraints = v.constraints
      
      newSchema.properties[v.name] = prop
    })
    
    onChange(newSchema)
  }

  const addVariable = () => {
    const newVar: VariableDefinition = {
      name: `var_${variables.length + 1}`,
      type: 'integer',
      min: 1,
      max: 100,
    }
    updateSchema([...variables, newVar])
  }

  const updateVariable = (index: number, field: keyof VariableDefinition, value: any) => {
    const updated = [...variables]
    updated[index] = { ...updated[index], [field]: value }
    updateSchema(updated)
  }

  const removeVariable = (index: number) => {
    updateSchema(variables.filter((_, i) => i !== index))
  }

  const addChoice = (varIndex: number) => {
    const updated = [...variables]
    const choices = updated[varIndex].choices || []
    updated[varIndex].choices = [...choices, '']
    updateSchema(updated)
  }

  const updateChoice = (varIndex: number, choiceIndex: number, value: string) => {
    const updated = [...variables]
    const choices = [...(updated[varIndex].choices || [])]
    choices[choiceIndex] = value
    updated[varIndex].choices = choices
    updateSchema(updated)
  }

  const removeChoice = (varIndex: number, choiceIndex: number) => {
    const updated = [...variables]
    updated[varIndex].choices = (updated[varIndex].choices || []).filter((_, i) => i !== choiceIndex)
    updateSchema(updated)
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Settings2 className="h-5 w-5 text-primary-600" />
          <h3 className="text-sm font-semibold text-gray-900">Variable Schema</h3>
          <span className="text-xs text-gray-500">({variables.length} variables)</span>
        </div>
        <button
          type="button"
          onClick={addVariable}
          className="btn btn-secondary flex items-center text-sm"
        >
          <Plus className="h-4 w-4 mr-1" />
          Add Variable
        </button>
      </div>

      {/* Help text */}
      <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <HelpCircle className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
        <p className="text-xs text-blue-700">
          Define variables for your template. Use <code className="bg-blue-100 px-1 rounded">{"{{variable_name}}"}</code> in 
          question patterns, solution steps, and hints. Variables will be generated based on these constraints.
        </p>
      </div>

      {/* Variables list */}
      {variables.length === 0 ? (
        <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
          <p className="text-gray-500 text-sm">No variables defined</p>
          <p className="text-gray-400 text-xs mt-1">Click "Add Variable" to create one</p>
        </div>
      ) : (
        <div className="space-y-3">
          {variables.map((variable, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 bg-white hover:border-primary-300 transition-colors"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center justify-center w-8 h-8 bg-primary-100 text-primary-700 rounded-md font-mono text-sm">
                    {VARIABLE_TYPES.find(t => t.value === variable.type)?.icon || '?'}
                  </span>
                  <div>
                    <code className="text-sm font-semibold text-gray-900">
                      {`{{${variable.name}}}`}
                    </code>
                    {variable.description && (
                      <p className="text-xs text-gray-500">{variable.description}</p>
                    )}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeVariable(index)}
                  className="text-gray-400 hover:text-danger-600 p-1"
                  title="Remove variable"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {/* Variable name */}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    value={variable.name}
                    onChange={(e) => updateVariable(index, 'name', e.target.value.replace(/[^a-zA-Z0-9_]/g, ''))}
                    className="input text-sm"
                    placeholder="variable_name"
                  />
                </div>

                {/* Type */}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Type
                  </label>
                  <select
                    value={variable.type}
                    onChange={(e) => updateVariable(index, 'type', e.target.value)}
                    className="input text-sm"
                  >
                    {VARIABLE_TYPES.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Min (for numeric types) */}
                {(variable.type === 'integer' || variable.type === 'float') && (
                  <>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Min
                      </label>
                      <input
                        type="number"
                        value={variable.min ?? ''}
                        onChange={(e) => updateVariable(index, 'min', e.target.value ? Number(e.target.value) : undefined)}
                        className="input text-sm"
                        placeholder="1"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Max
                      </label>
                      <input
                        type="number"
                        value={variable.max ?? ''}
                        onChange={(e) => updateVariable(index, 'max', e.target.value ? Number(e.target.value) : undefined)}
                        className="input text-sm"
                        placeholder="100"
                      />
                    </div>
                  </>
                )}

                {/* Choices for choice type */}
                {variable.type === 'choice' && (
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Choices
                    </label>
                    <div className="space-y-1">
                      {(variable.choices || []).map((choice, choiceIndex) => (
                        <div key={choiceIndex} className="flex gap-1">
                          <input
                            type="text"
                            value={choice}
                            onChange={(e) => updateChoice(index, choiceIndex, e.target.value)}
                            className="input text-sm flex-1"
                            placeholder={`Choice ${choiceIndex + 1}`}
                          />
                          <button
                            type="button"
                            onClick={() => removeChoice(index, choiceIndex)}
                            className="text-gray-400 hover:text-danger-600 p-1"
                          >
                            <Trash2 className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                      <button
                        type="button"
                        onClick={() => addChoice(index)}
                        className="text-xs text-primary-600 hover:text-primary-700"
                      >
                        + Add choice
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Description */}
              <div className="mt-3">
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Description (optional)
                </label>
                <input
                  type="text"
                  value={variable.description || ''}
                  onChange={(e) => updateVariable(index, 'description', e.target.value)}
                  className="input text-sm"
                  placeholder="What does this variable represent?"
                />
              </div>

              {/* Constraints (advanced) */}
              <div className="mt-3">
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Constraints (optional)
                </label>
                <input
                  type="text"
                  value={variable.constraints || ''}
                  onChange={(e) => updateVariable(index, 'constraints', e.target.value)}
                  className="input text-sm font-mono"
                  placeholder="e.g., number % 2 == 0 (must be even)"
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Schema preview (collapsed) */}
      <details className="text-xs">
        <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
          View JSON Schema
        </summary>
        <pre className="mt-2 p-3 bg-gray-50 rounded-lg overflow-x-auto text-gray-600">
          {JSON.stringify(schema, null, 2)}
        </pre>
      </details>
    </div>
  )
}
