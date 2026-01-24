import React, { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { 
  Save, Eye, CheckCircle, AlertCircle, Copy, 
  BookOpen, Sparkles, ChevronRight, ChevronDown, RefreshCw,
  Code, FileText, Calculator, Image, List, HelpCircle, Lightbulb
} from 'lucide-react'
import toast from 'react-hot-toast'

const API_BASE = import.meta.env.VITE_API_URL || ''

// Types
interface ValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}

interface PreviewQuestion {
  success: boolean
  question: string
  options: string[]
  correct_answer: string | string[] | null
  variables: Record<string, any>
  error: string | null
}

// Rule Book Content
const RULE_BOOK = {
  structure: {
    title: "1. Template Structure",
    icon: FileText,
    content: `Every template MUST have:

{
  "name": "Descriptive name",
  "concept_id": "math.class5.topic",
  "question_type": "MCQ",
  "question_pattern": "Text {{var}}",
  "variables": { ... },
  "options": [ ... ],
  "difficulty": 1-5,
  "solution": { ... }
}

Optional: tags, hints, estimated_time`
  },
  variables: {
    title: "2. Variables & Formulas",
    icon: Calculator,
    content: `BASE (random values):
"base": {
  "a": { "type": "integer", "min": 1, "max": 10 },
  "b": { "type": "integer", "enum": [2, 4, 6] }
}

COMPUTED (formulas):
"computed": {
  "sum": { "formula": "a + b" },
  "gcd_val": { "formula": "gcd(a, b)" }
}

Functions: gcd, lcm, factors, pow, abs, min, max, sqrt`
  },
  questionTypes: {
    title: "3. Question Types",
    icon: List,
    content: `MCQ:
"options": [
  { "pattern": "{{answer}}", "is_correct": true },
  { "pattern": "{{wrong}}", "is_correct": false }
]

FILL_BLANK:
"answer_field": "{{answer}}"

TRUE_FALSE, CASE_STUDY, MATCH_FOLLOWING`
  },
  diagram: {
    title: "4. Diagrams (SVG)",
    icon: Image,
    content: `"diagram": {
  "type": "custom_svg",
  "parameters": {
    "svg_template": "<svg>{{var}}</svg>"
  }
}

Use {{var}} directly in svg_template.
Variables from template are auto-substituted.`
  },
  solution: {
    title: "5. Solution & Hints",
    icon: Lightbulb,
    content: `"solution": {
  "steps": [
    { "number": 1, "text": "Step {{a}}" }
  ]
}

"hints": ["Hint 1", "Hint 2"]`
  },
  examples: {
    title: "6. Load Examples",
    icon: Code,
    content: `Click examples in header:
• MCQ Basic
• MCQ + Diagram  
• Fill Blank
• Case Study
• Match Following`
  }
}

// Example Templates
const EXAMPLE_TEMPLATES = {
  mcq_basic: {
    name: "MCQ Basic",
    template: `{
  "name": "GCD Question",
  "concept_id": "math.class5.gcd",
  "question_type": "MCQ",
  "question_pattern": "Find the GCD of {{a}} and {{b}}.",
  "variables": {
    "base": {
      "a": { "type": "integer", "min": 12, "max": 48 },
      "b": { "type": "integer", "min": 12, "max": 48 }
    },
    "computed": {
      "gcd_result": { "formula": "gcd(a, b)" },
      "wrong1": { "formula": "lcm(a, b)" }
    },
    "constraints": ["a != b"]
  },
  "options": [
    { "pattern": "{{gcd_result}}", "is_correct": true },
    { "pattern": "{{wrong1}}", "is_correct": false },
    { "pattern": "{{gcd_result + 1}}", "is_correct": false }
  ],
  "difficulty": 2,
  "solution": {
    "steps": [
      { "number": 1, "text": "Find common factors" },
      { "number": 2, "text": "GCD = {{gcd_result}}" }
    ]
  },
  "tags": ["gcd", "class5"]
}`
  },
  mcq_diagram: {
    name: "MCQ + Diagram",
    template: `{
  "name": "Triangle Area",
  "concept_id": "math.class7.geometry",
  "question_type": "MCQ",
  "question_pattern": "Find the area of the triangle shown below.",
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [6, 8, 10] },
      "h": { "type": "integer", "enum": [4, 5, 6] }
    },
    "computed": {
      "area": { "formula": "(b * h) / 2" },
      "wrong1": { "formula": "b * h" },
      "wrong2": { "formula": "b + h" }
    }
  },
  "diagram": {
    "type": "custom_svg",
    "parameters": {
      "svg_template": "<svg width='280' height='180' viewBox='0 0 300 200' xmlns='http://www.w3.org/2000/svg'><polygon points='50,180 250,180 150,30' fill='#DBEAFE' stroke='#2563EB' stroke-width='3'/><line x1='150' y1='30' x2='150' y2='180' stroke='#DC2626' stroke-width='2' stroke-dasharray='5,5'/><text x='150' y='195' text-anchor='middle' font-size='14' font-weight='bold'>{{b}} cm</text><text x='165' y='110' fill='#DC2626' font-size='14' font-weight='bold'>{{h}} cm</text></svg>"
    }
  },
  "options": [
    { "pattern": "{{area}} cm²", "is_correct": true },
    { "pattern": "{{wrong1}} cm²", "is_correct": false },
    { "pattern": "{{wrong2}} cm²", "is_correct": false }
  ],
  "difficulty": 2,
  "tags": ["triangle", "area", "geometry"]
}`
  },
  fill_blank: {
    name: "Fill Blank",
    template: `{
  "name": "Prime Factorization",
  "concept_id": "math.class5.prime",
  "question_type": "FILL_BLANK",
  "question_pattern": "If {{number}} = 2^{{p2}} × 3^{{p3}}, then {{p2}} + {{p3}} = ___",
  "variables": {
    "base": {
      "p2": { "type": "integer", "enum": [1, 2, 3] },
      "p3": { "type": "integer", "enum": [1, 2] }
    },
    "computed": {
      "number": { "formula": "pow(2, p2) * pow(3, p3)" },
      "answer": { "formula": "p2 + p3" }
    }
  },
  "answer_field": "{{answer}}",
  "options": [
    { "pattern": "{{answer}}", "is_correct": true }
  ],
  "difficulty": 2,
  "tags": ["prime", "fill-blank"]
}`
  },
  case_study: {
    name: "Case Study",
    template: `{
  "name": "Projectile Motion",
  "concept_id": "math.class10.quadratic",
  "question_type": "CASE_STUDY",
  "parts": [
    {
      "type": "context",
      "pattern": "Ball height: h = -x² + {{b}}x meters"
    },
    {
      "type": "sub_question",
      "label": "i",
      "pattern": "Maximum height distance?",
      "options": [
        { "pattern": "{{max_x}} m", "is_correct": true },
        { "pattern": "{{b}} m", "is_correct": false }
      ]
    }
  ],
  "variables": {
    "base": { "b": { "type": "integer", "enum": [4, 6, 8] } },
    "computed": { "max_x": { "formula": "b / 2" } }
  },
  "difficulty": 4,
  "tags": ["case-study"]
}`
  },
  match_following: {
    name: "Match Following",
    template: `{
  "name": "Factor Count Match",
  "concept_id": "math.class5.factors",
  "question_type": "MATCH_FOLLOWING",
  "question_pattern": "Match numbers with factor count:",
  "left_column": [
    { "id": "L1", "pattern": "{{n1}}" },
    { "id": "L2", "pattern": "{{n2}}" }
  ],
  "right_column": [
    { "id": "R1", "pattern": "{{f1}} factors" },
    { "id": "R2", "pattern": "{{f2}} factors" }
  ],
  "correct_matches": [
    { "left": "L1", "right": "R1" },
    { "left": "L2", "right": "R2" }
  ],
  "variables": {
    "base": {
      "n1": { "type": "integer", "enum": [6, 8, 10] },
      "n2": { "type": "integer", "enum": [7, 11, 13] }
    },
    "computed": {
      "f1": { "formula": "factor_count(n1)" },
      "f2": { "formula": "factor_count(n2)" }
    }
  },
  "difficulty": 2,
  "tags": ["match", "factors"]
}`
  }
}

// Helper Functions
function resolveTemplateValue(value: any, variables: Record<string, any>): any {
  if (typeof value === 'string') {
    return value.replace(/\{\{([^}]+)\}\}/g, (fullMatch, expression) => {
      const trimmed = expression.trim()
      if (variables[trimmed] !== undefined) return String(variables[trimmed])
      try {
        let evalExpr = trimmed
        for (const [varName, varValue] of Object.entries(variables)) {
          evalExpr = evalExpr.replace(new RegExp(`\\b${varName}\\b`, 'g'), String(varValue))
        }
        if (/^[\d\s+\-*/.()]+$/.test(evalExpr)) {
          const result = Function(`"use strict"; return (${evalExpr})`)()
          return String(Math.round(result * 100) / 100)
        }
      } catch { /* ignore */ }
      return fullMatch
    })
  }
  return value
}

function sanitizeSvg(svg: string): string {
  return svg
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/\s+on\w+\s*=\s*["'][^"']*["']/gi, '')
    .replace(/javascript\s*:/gi, '')
}

// Diagram Preview Component
interface DiagramPreviewProps {
  diagramConfig: { type: string; parameters: Record<string, any> }
  variables: Record<string, any>
}

function DiagramPreview({ diagramConfig, variables }: DiagramPreviewProps) {
  // For custom_svg, render synchronously
  if (diagramConfig.type === 'custom_svg') {
    const svgTemplate = diagramConfig.parameters?.svg_template || ''
    if (!svgTemplate) {
      return <div className="bg-yellow-50 border border-yellow-200 rounded p-2 text-yellow-700 text-xs">No svg_template provided</div>
    }
    let resolvedSvg = sanitizeSvg(resolveTemplateValue(svgTemplate, variables))
    
    // Ensure SVG has width/height for proper rendering
    if (!resolvedSvg.includes('width=') && !resolvedSvg.includes('height=')) {
      resolvedSvg = resolvedSvg.replace('<svg', '<svg width="100%" height="auto" style="max-width:280px"')
    }
    
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex justify-center items-center min-h-[120px]">
        <div 
          className="svg-container"
          style={{ width: '100%', maxWidth: '280px' }}
          dangerouslySetInnerHTML={{ __html: resolvedSvg }} 
        />
      </div>
    )
  }

  // For other diagram types
  return (
    <div className="bg-gray-50 border border-gray-200 rounded p-2 text-gray-500 text-xs">
      Diagram type "{diagramConfig.type}" - use custom_svg for inline diagrams
    </div>
  )
}

// Rule Book Sidebar
function RuleBookSidebar() {
  const [expanded, setExpanded] = useState<string | null>('structure')
  const sections = Object.entries(RULE_BOOK).map(([key, data]) => ({ key, ...data }))

  return (
    <div className="h-full flex flex-col bg-slate-50">
      <div className="p-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="flex items-center gap-2"><BookOpen size={20}/><h2 className="font-bold">Rule Book</h2></div>
        <p className="text-indigo-200 text-xs mt-1">Template writing guide</p>
      </div>
      <div className="flex-1 overflow-y-auto p-2">
        {sections.map(({ key, title, icon: Icon, content }) => (
          <div key={key} className="mb-1">
            <button
              onClick={() => setExpanded(expanded === key ? null : key)}
              className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-left text-sm ${expanded === key ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-gray-100 text-gray-700'}`}
            >
              <Icon size={16} className={expanded === key ? 'text-indigo-500' : 'text-gray-400'}/>
              <span className="flex-1 font-medium">{title}</span>
              {expanded === key ? <ChevronDown size={16}/> : <ChevronRight size={16}/>}
            </button>
            {expanded === key && (
              <div className="mt-1 mx-1 p-3 bg-white rounded-lg border shadow-sm">
                <pre className="whitespace-pre-wrap font-mono text-xs text-gray-600 leading-relaxed">{content}</pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// Main Component
export function UniversalTemplateEditor() {
  const [jsonInput, setJsonInput] = useState('')
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [previewQuestions, setPreviewQuestions] = useState<PreviewQuestion[]>([])
  const [currentDiagramConfig, setCurrentDiagramConfig] = useState<{ type: string; parameters: Record<string, any> } | null>(null)
  const validateJson = useCallback((json: string): ValidationResult => {
    try {
      const parsed = JSON.parse(json)
      const errors: string[] = []
      const warnings: string[] = []
      if (!parsed.name) errors.push('Missing: name')
      if (!parsed.concept_id) errors.push('Missing: concept_id')
      if (!parsed.question_type) errors.push('Missing: question_type')
      if (!parsed.question_pattern && !parsed.parts) errors.push('Missing: question_pattern or parts')
      if (!parsed.variables) errors.push('Missing: variables')
      if (!parsed.options && !['CASE_STUDY', 'FILL_BLANK'].includes(parsed.question_type)) errors.push('Missing: options')
      if (!parsed.solution) warnings.push('Recommended: solution')
      if (!parsed.difficulty) warnings.push('Recommended: difficulty')
      return { valid: errors.length === 0, errors, warnings }
    } catch (e) {
      return { valid: false, errors: [`Invalid JSON: ${(e as Error).message}`], warnings: [] }
    }
  }, [])

  const previewMutation = useMutation({
    mutationFn: async (template: any) => {
      const response = await fetch(`${API_BASE}/api/admin/templates/universal/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template, count: 3 })
      })
      if (!response.ok) throw new Error('Preview failed')
      return response.json()
    },
    onSuccess: (data) => {
      setPreviewQuestions(Array.isArray(data) ? data : (data.questions || []))
      toast.success('Preview generated!')
    },
    onError: () => toast.error('Preview failed')
  })

  const saveMutation = useMutation({
    mutationFn: async (template: any) => {
      const response = await fetch(`${API_BASE}/api/admin/templates/universal/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(template)
      })
      if (!response.ok) throw new Error('Save failed')
      return response.json()
    },
    onSuccess: (data) => toast.success(`Saved! ID: ${data.template_id}`),
    onError: () => toast.error('Save failed')
  })

  const handleValidate = () => {
    const result = validateJson(jsonInput)
    setValidationResult(result)
    result.valid ? toast.success('Valid!') : toast.error(`${result.errors.length} error(s)`)
  }

  const handlePreview = () => {
    const v = validateJson(jsonInput)
    if (!v.valid) { setValidationResult(v); toast.error('Fix errors first'); return }
    const parsed = JSON.parse(jsonInput)
    // Capture diagram config at preview time
    if (parsed.diagram) {
      setCurrentDiagramConfig(parsed.diagram)
    } else {
      setCurrentDiagramConfig(null)
    }
    previewMutation.mutate(parsed)
  }

  const handleSave = () => {
    const v = validateJson(jsonInput)
    if (!v.valid) { setValidationResult(v); toast.error('Fix errors first'); return }
    saveMutation.mutate(JSON.parse(jsonInput))
  }

  const loadExample = (key: string) => {
    const ex = EXAMPLE_TEMPLATES[key as keyof typeof EXAMPLE_TEMPLATES]
    if (ex) { setJsonInput(ex.template); setValidationResult(null); setPreviewQuestions([]); setCurrentDiagramConfig(null); toast.success(`Loaded: ${ex.name}`) }
  }

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between shadow-sm">
        <div>
          <h1 className="text-lg font-bold text-gray-900">Template Editor</h1>
          <p className="text-gray-500 text-xs">Single editor • Complete question templates</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden md:flex items-center gap-1 mr-2 px-2 py-1 bg-gray-100 rounded-lg">
            <span className="text-xs text-gray-500 mr-1">Examples:</span>
            {Object.entries(EXAMPLE_TEMPLATES).map(([k, { name }]) => (
              <button key={k} onClick={() => loadExample(k)} className="px-2 py-1 text-xs bg-white hover:bg-indigo-50 rounded border hover:border-indigo-300">{name}</button>
            ))}
          </div>
          <button onClick={handleValidate} className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center gap-1.5"><CheckCircle size={16}/>Validate</button>
          <button onClick={handlePreview} disabled={previewMutation.isPending} className="px-3 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-1.5 disabled:opacity-50"><Eye size={16}/>{previewMutation.isPending ? '...' : 'Preview'}</button>
          <button onClick={handleSave} disabled={saveMutation.isPending} className="px-3 py-2 text-sm bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-1.5 disabled:opacity-50"><Save size={16}/>{saveMutation.isPending ? '...' : 'Save'}</button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-64 flex-shrink-0 border-r"><RuleBookSidebar/></div>

        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
            <span className="text-sm text-gray-300">Template JSON</span>
            <div className="flex gap-3">
              <button onClick={() => { try { setJsonInput(JSON.stringify(JSON.parse(jsonInput), null, 2)) } catch { /* ignore */ } }} className="text-xs text-indigo-400 hover:text-indigo-300">Format</button>
              <button onClick={() => { navigator.clipboard.writeText(jsonInput); toast.success('Copied!') }} className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"><Copy size={12}/>Copy</button>
            </div>
          </div>
          <textarea
            value={jsonInput}
            onChange={(e) => { setJsonInput(e.target.value); setValidationResult(null) }}
            className="flex-1 w-full font-mono text-sm p-4 bg-gray-900 text-green-400 resize-none focus:outline-none"
            placeholder="Write template JSON here... See Rule Book on left, or click Example above."
            spellCheck={false}
          />
          {validationResult && (
            <div className="border-t border-gray-700 bg-gray-800 p-3 max-h-28 overflow-y-auto">
              {validationResult.errors.map((e, i) => <div key={i} className="flex items-center gap-2 text-red-400 text-sm mb-1"><AlertCircle size={14}/>{e}</div>)}
              {validationResult.warnings.map((w, i) => <div key={i} className="flex items-center gap-2 text-yellow-400 text-sm mb-1"><AlertCircle size={14}/>{w}</div>)}
              {validationResult.valid && <div className="flex items-center gap-2 text-green-400 text-sm"><CheckCircle size={14}/>Valid!</div>}
            </div>
          )}
        </div>

        <div className="w-80 flex-shrink-0 border-l bg-white overflow-y-auto">
          <div className="p-4 border-b bg-gradient-to-r from-purple-50 to-indigo-50">
            <div className="flex items-center gap-2"><Sparkles size={18} className="text-purple-500"/><h2 className="font-semibold">Preview</h2></div>
          </div>
          <div className="p-4">
            {previewQuestions.length === 0 ? (
              <div className="text-center py-16 text-gray-400"><Eye size={40} className="mx-auto mb-3 opacity-30"/><p className="text-sm">Click Preview to see results</p></div>
            ) : (
              <div className="space-y-4">
                {previewQuestions.map((q, idx) => (
                  <div key={idx} className="bg-gray-50 rounded-xl border p-4">
                    <div className="text-xs font-semibold text-indigo-600 mb-2">Question {idx + 1}</div>
                    {currentDiagramConfig && q.variables && <div className="mb-3"><DiagramPreview diagramConfig={currentDiagramConfig} variables={q.variables}/></div>}
                    <p className="text-gray-900 font-medium mb-3 text-sm whitespace-pre-wrap">{q.question}</p>
                    {q.options?.map((opt, i) => {
                      const isCorrect = opt === q.correct_answer
                      return (
                        <div key={i} className={`flex items-center gap-2 p-2 rounded text-xs mb-1 ${isCorrect ? 'bg-green-100 border border-green-300' : 'bg-white border'}`}>
                          <span className={`w-5 h-5 flex items-center justify-center rounded-full text-xs ${isCorrect ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>{String.fromCharCode(65+i)}</span>
                          <span className="flex-1">{opt}</span>
                          {isCorrect && <CheckCircle size={14} className="text-green-500"/>}
                        </div>
                      )
                    })}
                    {q.variables && <details className="mt-2"><summary className="text-xs text-gray-500 cursor-pointer">Variables</summary><div className="mt-1 p-2 bg-gray-100 rounded text-xs font-mono">{Object.entries(q.variables).map(([k,v])=><div key={k}>{k}={String(v)}</div>)}</div></details>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default UniversalTemplateEditor
