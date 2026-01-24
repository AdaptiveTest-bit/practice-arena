# LLM Batch Tools Specification
## One-Time Batch Processing for Content Acceleration

**Date:** 18 January 2026  
**Principle:** Manual-first system, LLM as optional batch accelerator

---

## 🎯 Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   "LLM generates DRAFTS, Humans APPROVE and PUBLISH"           │
│                                                                 │
│   ✅ System works 100% without LLM                              │
│   ✅ LLM output always goes to DRAFT queue                      │
│   ✅ Human review required before production                    │
│   ✅ Batch processing = cost-efficient                          │
│   ✅ No runtime LLM dependency                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Batch Tool #1: Question Bank Importer

### Purpose
Convert a bank of sample questions (like your 19 Quadratic Equations) into template drafts.

### Input
```yaml
# Input: questions.yaml or paste in UI
chapter: "Quadratic Equations"
grade: 10
subject: "Mathematics"
questions:
  - text: "Find the roots of x² − 7x + 10 = 0"
    type: "MCQ"
    answer: "2, 5"
    
  - text: "For what value of k will x² − 2kx + 9 = 0 have equal roots?"
    type: "MCQ"
    answer: "k = ±3"
    
  - text: "The product of two consecutive positive integers is 1320. Find them."
    type: "WORD_PROBLEM"
    answer: "36, 37"
```

### LLM Prompt
```
You are a math education template designer. Convert these questions into template format.

For each question, generate:
1. question_pattern: Replace specific numbers with variables like {{a}}, {{b}}, {{c}}
2. variable_schema: Define ranges/enums for each variable
3. computed_variables: Formulas to calculate answers (use: gcd, lcm, factors, discriminant, solve_quadratic, etc.)
4. option_patterns: Correct answer + 3 distractors with misconception tags
5. solution_steps: Step-by-step solution with variables
6. constraints: Ensure valid questions (e.g., discriminant >= 0 for real roots)

Available formulas: [list from formula library]

Output as JSON matching this schema: [template schema]
```

### Output → Draft Queue
```json
{
  "status": "DRAFT",
  "source": "LLM_BATCH_IMPORT",
  "batch_id": "batch_20260118_quad_eq",
  "templates": [
    {
      "concept_id": "math.class10.quadratic.solve_factorization",
      "question_pattern": "Find the roots of x² − {{sum}}x + {{product}} = 0",
      "variable_schema": {
        "base": {
          "root1": { "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] },
          "root2": { "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
        },
        "computed": {
          "sum": "root1 + root2",
          "product": "root1 * root2"
        },
        "constraints": ["root1 < root2"]
      },
      "options": [...],
      "llm_confidence": 0.92,
      "needs_review": ["variable_ranges", "misconceptions"]
    }
  ]
}
```

### UI Flow
```
┌─────────────────────────────────────────────────────────────────┐
│  📥 BATCH IMPORT: Question Bank → Templates                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Paste Questions                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. Find the roots of x² − 7x + 10 = 0                      ││
│  │ 2. Solve: 2x² − 5x − 3 = 0                                 ││
│  │ 3. Find the roots of x² + 3x − 10 = 0                      ││
│  │ ...                                                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Step 2: Select Chapter & Metadata                              │
│  Chapter: [Quadratic Equations ▼]  Grade: [10 ▼]               │
│                                                                 │
│  Step 3: Generate Templates                                     │
│  [🤖 Generate with LLM] ← One-time batch call                  │
│                                                                 │
│  Estimated Cost: $0.45 for 19 questions                        │
│  Estimated Time: ~30 seconds                                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Step 4: Review Drafts                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ☐ Template 1: Factorization (confidence: 92%)    [Review]  ││
│  │ ☐ Template 2: Quadratic Formula (confidence: 88%) [Review] ││
│  │ ⚠️ Template 3: Nature of Roots (confidence: 75%)  [Review] ││
│  │ ...                                                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [Approve Selected]  [Edit & Approve]  [Reject]                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Batch Tool #2: Word Problem Variation Generator

### Purpose
Take one base word problem, generate 10-20 context variations while keeping math structure.

### Input
```yaml
base_problem: "The product of two consecutive positive integers is {{product}}. Find the integers."
variables:
  product: [132, 156, 182, 210, 240, 272, 306, 342]
contexts_needed: 10
```

### LLM Prompt
```
Generate 10 word problem variations that have IDENTICAL mathematical structure to:
"The product of two consecutive positive integers is {{product}}. Find the integers."

Requirements:
- Each variation must solve to: n(n+1) = {{product}}
- Use different real-world contexts (age, dimensions, sports, money, etc.)
- Keep {{product}} as the only variable
- Suitable for Class 10 students (age 15-16)
- Each problem should be 1-2 sentences

Output format:
[
  {
    "context": "age",
    "problem": "Rahul's age (in years) multiplied by his age next year equals {{product}}. How old is Rahul?",
    "answer_format": "Rahul is {{n}} years old"
  },
  ...
]
```

### Output → Variation Bank
```json
{
  "base_template_id": "tmpl_consecutive_integers",
  "variations": [
    {
      "id": "var_001",
      "context": "age",
      "question_pattern": "Rahul's age multiplied by his age next year equals {{product}}. How old is Rahul?",
      "answer_pattern": "Rahul is {{n}} years old",
      "status": "DRAFT"
    },
    {
      "id": "var_002", 
      "context": "dimensions",
      "question_pattern": "A rectangular garden has length 1 meter more than its width. If the area is {{product}} sq meters, find the dimensions.",
      "answer_pattern": "Width = {{n}}m, Length = {{n_plus_1}}m",
      "status": "DRAFT"
    },
    {
      "id": "var_003",
      "context": "sports",
      "question_pattern": "In a cricket match, a batsman scored runs in two consecutive overs. If the product of runs is {{product}}, find runs in each over.",
      "answer_pattern": "{{n}} and {{n_plus_1}} runs",
      "status": "DRAFT"
    }
  ]
}
```

### How It's Used (Runtime)
```python
# At question generation time (NO LLM call)
def generate_word_problem(template_id, difficulty):
    template = get_template(template_id)
    
    # Pick a random approved variation
    variation = random.choice(template.approved_variations)
    
    # Pick variable values
    product = random.choice(template.variable_schema['product']['enum'])
    n, n_plus_1 = consecutive_integers_product(product)
    
    # Render
    question = variation.question_pattern.replace('{{product}}', str(product))
    answer = variation.answer_pattern.replace('{{n}}', str(n)).replace('{{n_plus_1}}', str(n_plus_1))
    
    return Question(text=question, answer=answer, ...)
```

---

## 📦 Batch Tool #3: Solution Step Generator

### Purpose
Generate pedagogically-sound step-by-step solutions for template patterns.

### Input
```yaml
template_id: "tmpl_quadratic_formula"
question_pattern: "Solve {{a}}x² + {{b}}x + {{c}} = 0 using quadratic formula"
answer: "roots from solve_quadratic(a, b, c)"
grade: 10
```

### LLM Prompt
```
Generate a step-by-step solution template for this question type:
"Solve {{a}}x² + {{b}}x + {{c}} = 0 using quadratic formula"

Requirements:
- Use variables {{a}}, {{b}}, {{c}} that will be replaced at runtime
- Use computed variables like {{discriminant}}, {{root1}}, {{root2}}
- Each step should be clear for a Class 10 student
- Include the mathematical reasoning
- Use LaTeX notation where appropriate: {{latex:...}}

Output format:
{
  "steps": [
    {
      "text": "Step 1: Identify coefficients: a = {{a}}, b = {{b}}, c = {{c}}",
      "explanation": "Compare with standard form ax² + bx + c = 0"
    },
    ...
  ],
  "computed_vars_needed": ["discriminant", "sqrt_discriminant", "root1", "root2"]
}
```

### Output → Solution Library
```json
{
  "template_id": "tmpl_quadratic_formula",
  "solution": {
    "steps": [
      {
        "number": 1,
        "text": "Identify coefficients: a = {{a}}, b = {{b}}, c = {{c}}",
        "latex": null
      },
      {
        "number": 2,
        "text": "Calculate discriminant: D = b² - 4ac = {{b}}² - 4({{a}})({{c}}) = {{discriminant}}",
        "latex": "D = b^2 - 4ac = {{b}}^2 - 4({{a}})({{c}}) = {{discriminant}}"
      },
      {
        "number": 3,
        "text": "Since D = {{discriminant}} {{discriminant_condition}}, the equation has {{nature_of_roots}}",
        "latex": null
      },
      {
        "number": 4,
        "text": "Apply quadratic formula: x = (-b ± √D) / 2a",
        "latex": "x = \\frac{-b \\pm \\sqrt{D}}{2a}"
      },
      {
        "number": 5,
        "text": "x = (-{{b}} ± √{{discriminant}}) / 2({{a}})",
        "latex": "x = \\frac{-{{b}} \\pm \\sqrt{{{discriminant}}}}{2({{a}})}"
      },
      {
        "number": 6,
        "text": "x₁ = {{root1}}, x₂ = {{root2}}",
        "latex": "x_1 = {{root1}}, x_2 = {{root2}}"
      }
    ],
    "computed_vars": {
      "discriminant": "b*b - 4*a*c",
      "discriminant_condition": "'> 0' if discriminant > 0 else ('= 0' if discriminant == 0 else '< 0')",
      "nature_of_roots": "nature_of_roots(a, b, c)",
      "root1": "solve_quadratic(a, b, c)[0]",
      "root2": "solve_quadratic(a, b, c)[1]"
    },
    "status": "DRAFT"
  }
}
```

---

## 📦 Batch Tool #4: Diagram SVG Generator

### Purpose
Generate SVG templates for mathematical diagrams with variable placeholders.

### Input
```yaml
diagram_type: "parabola_graph"
description: "Graph of y = ax² + bx + c showing vertex and x-intercepts"
variables:
  - a: "coefficient of x²"
  - b: "coefficient of x"
  - c: "constant"
  - vertex_x: "x-coordinate of vertex"
  - vertex_y: "y-coordinate of vertex"
  - root1: "first x-intercept"
  - root2: "second x-intercept"
```

### LLM Prompt
```
Generate an SVG template for a parabola graph with these requirements:

1. Canvas: 400x300 pixels
2. Show coordinate axes with labels
3. Draw parabola for y = ax² + bx + c (a < 0, opens downward)
4. Mark and label:
   - Vertex at ({{vertex_x}}, {{vertex_y}})
   - X-intercepts at ({{root1}}, 0) and ({{root2}}, 0)
5. Use placeholders {{variable}} that will be replaced at runtime
6. Style: Clean, educational, suitable for Class 10
7. Include grid lines

Output: Complete SVG code with variable placeholders
```

### Output → Diagram Library
```svg
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <!-- Grid -->
  <g stroke="#eee" stroke-width="1">
    <line x1="0" y1="150" x2="400" y2="150"/>
    <line x1="200" y1="0" x2="200" y2="300"/>
    <!-- More grid lines -->
  </g>
  
  <!-- Axes -->
  <g stroke="#333" stroke-width="2">
    <line x1="0" y1="150" x2="400" y2="150"/> <!-- X-axis -->
    <line x1="200" y1="0" x2="200" y2="300"/> <!-- Y-axis -->
    <text x="390" y="165" font-size="12">x</text>
    <text x="205" y="15" font-size="12">y</text>
  </g>
  
  <!-- Parabola path - computed at runtime -->
  <path d="{{parabola_path}}" fill="none" stroke="#2563eb" stroke-width="2"/>
  
  <!-- Vertex -->
  <circle cx="{{vertex_x_px}}" cy="{{vertex_y_px}}" r="5" fill="#dc2626"/>
  <text x="{{vertex_label_x}}" y="{{vertex_label_y}}" font-size="11">
    ({{vertex_x}}, {{vertex_y}})
  </text>
  
  <!-- X-intercepts -->
  <circle cx="{{root1_px}}" cy="150" r="4" fill="#16a34a"/>
  <text x="{{root1_label_x}}" y="170" font-size="11">({{root1}}, 0)</text>
  
  <circle cx="{{root2_px}}" cy="150" r="4" fill="#16a34a"/>
  <text x="{{root2_label_x}}" y="170" font-size="11">({{root2}}, 0)</text>
  
  <!-- Equation label -->
  <text x="10" y="25" font-size="12" fill="#333">
    y = {{a}}x² + {{b}}x + {{c}}
  </text>
</svg>
```

---

## 📦 Batch Tool #5: Misconception Tagger

### Purpose
Given correct answer and distractors, generate misconception explanations.

### Input
```yaml
question: "Find the sum of roots of 2x² + 5x - 3 = 0"
correct_answer: "-5/2"
distractors:
  - "5/2"
  - "-3/2"
  - "3/2"
```

### LLM Prompt
```
For this question about sum of roots of a quadratic equation:
Question: "Find the sum of roots of 2x² + 5x - 3 = 0"
Correct: -5/2 (using -b/a = -5/2)

Explain why a student might choose each wrong answer:

Distractor 1: "5/2"
Distractor 2: "-3/2"
Distractor 3: "3/2"

Format:
{
  "distractors": [
    {
      "value": "5/2",
      "misconception_id": "sign_error_sum_roots",
      "misconception_name": "Forgot negative sign in -b/a",
      "explanation": "Student used b/a instead of -b/a"
    },
    ...
  ]
}
```

### Output → Misconception Bank
```json
{
  "question_type": "sum_of_roots",
  "distractors": [
    {
      "value": "5/2",
      "misconception_id": "QUAD_SUM_SIGN_ERROR",
      "misconception_name": "Sign error in sum formula",
      "student_thinking": "Used b/a instead of -b/a",
      "remediation_hint": "Remember: Sum of roots = -b/a (note the negative sign)"
    },
    {
      "value": "-3/2",
      "misconception_id": "QUAD_SUM_PRODUCT_CONFUSION",
      "misconception_name": "Confused sum with product formula",
      "student_thinking": "Used c/a (product formula) instead of -b/a",
      "remediation_hint": "Sum = -b/a, Product = c/a. Don't mix them up!"
    },
    {
      "value": "3/2",
      "misconception_id": "QUAD_SUM_WRONG_COEFF",
      "misconception_name": "Used wrong coefficients",
      "student_thinking": "Used -c/a instead of -b/a",
      "remediation_hint": "In -b/a, 'b' is the coefficient of x, not the constant"
    }
  ]
}
```

---

## 🔧 Backend Implementation

### Batch Job Service

```python
# backend/domain/batch/llm_batch_service.py

from enum import Enum
from typing import List, Dict, Any
import asyncio
from datetime import datetime

class BatchJobType(Enum):
    IMPORT_QUESTIONS = "import_questions"
    GENERATE_VARIATIONS = "generate_variations"
    GENERATE_SOLUTIONS = "generate_solutions"
    GENERATE_DIAGRAMS = "generate_diagrams"
    TAG_MISCONCEPTIONS = "tag_misconceptions"

class BatchJobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEW_PENDING = "review_pending"

class LLMBatchService:
    """
    Handles one-time batch LLM jobs for content generation.
    All outputs go to DRAFT status requiring human review.
    """
    
    def __init__(self, llm_client, template_repo, config):
        self.llm = llm_client
        self.templates = template_repo
        self.config = config
        
    async def create_batch_job(
        self,
        job_type: BatchJobType,
        input_data: Dict[str, Any],
        created_by: str
    ) -> str:
        """Create a new batch job and return job_id."""
        job = BatchJob(
            id=generate_uuid(),
            type=job_type,
            status=BatchJobStatus.PENDING,
            input_data=input_data,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        await self.save_job(job)
        return job.id
    
    async def process_import_questions(self, job_id: str):
        """
        Process a question bank import job.
        Converts raw questions to template drafts.
        """
        job = await self.get_job(job_id)
        job.status = BatchJobStatus.PROCESSING
        await self.save_job(job)
        
        try:
            questions = job.input_data['questions']
            chapter = job.input_data['chapter']
            grade = job.input_data['grade']
            
            # Build prompt
            prompt = self._build_import_prompt(questions, chapter, grade)
            
            # Single LLM call for all questions (batch efficiency)
            response = await self.llm.complete(
                model=self.config.batch_model,  # Use cost-effective model
                prompt=prompt,
                max_tokens=4000,
                temperature=0.3  # Lower for consistency
            )
            
            # Parse response
            templates = self._parse_template_response(response)
            
            # Save as drafts
            for template in templates:
                template['status'] = 'DRAFT'
                template['source'] = 'LLM_BATCH'
                template['batch_job_id'] = job_id
                template['needs_review'] = True
                await self.templates.save_draft(template)
            
            job.status = BatchJobStatus.REVIEW_PENDING
            job.output_data = {
                'templates_created': len(templates),
                'template_ids': [t['id'] for t in templates]
            }
            job.completed_at = datetime.utcnow()
            
        except Exception as e:
            job.status = BatchJobStatus.FAILED
            job.error = str(e)
        
        await self.save_job(job)
    
    async def process_variations(self, job_id: str):
        """Generate word problem variations."""
        job = await self.get_job(job_id)
        job.status = BatchJobStatus.PROCESSING
        await self.save_job(job)
        
        try:
            base_problem = job.input_data['base_problem']
            count = job.input_data.get('count', 10)
            contexts = job.input_data.get('contexts', [])
            
            prompt = self._build_variation_prompt(base_problem, count, contexts)
            
            response = await self.llm.complete(
                model=self.config.batch_model,
                prompt=prompt,
                max_tokens=2000
            )
            
            variations = self._parse_variations(response)
            
            # Save to variation bank
            for var in variations:
                var['status'] = 'DRAFT'
                var['base_template_id'] = job.input_data['template_id']
                await self.templates.save_variation(var)
            
            job.status = BatchJobStatus.REVIEW_PENDING
            job.output_data = {'variations_created': len(variations)}
            
        except Exception as e:
            job.status = BatchJobStatus.FAILED
            job.error = str(e)
        
        await self.save_job(job)
    
    def estimate_cost(self, job_type: BatchJobType, input_data: Dict) -> Dict:
        """Estimate cost before running job."""
        token_estimates = {
            BatchJobType.IMPORT_QUESTIONS: lambda d: len(d.get('questions', [])) * 500,
            BatchJobType.GENERATE_VARIATIONS: lambda d: d.get('count', 10) * 200,
            BatchJobType.GENERATE_SOLUTIONS: lambda d: 400,
            BatchJobType.GENERATE_DIAGRAMS: lambda d: 800,
            BatchJobType.TAG_MISCONCEPTIONS: lambda d: len(d.get('distractors', [])) * 150,
        }
        
        estimated_tokens = token_estimates[job_type](input_data)
        cost_per_1k = 0.002  # GPT-4o-mini pricing
        
        return {
            'estimated_tokens': estimated_tokens,
            'estimated_cost_usd': estimated_tokens * cost_per_1k / 1000,
            'model': self.config.batch_model
        }
```

### API Endpoints

```python
# backend/api/routes/batch.py

from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List

router = APIRouter(prefix="/api/admin/batch", tags=["Batch LLM"])

@router.post("/jobs")
async def create_batch_job(
    request: BatchJobRequest,
    background_tasks: BackgroundTasks,
    service: LLMBatchService = Depends()
):
    """
    Create a new batch LLM job.
    Returns immediately with job_id; processing happens in background.
    """
    # Estimate cost first
    estimate = service.estimate_cost(request.job_type, request.input_data)
    
    # Create job
    job_id = await service.create_batch_job(
        job_type=request.job_type,
        input_data=request.input_data,
        created_by=request.user_id
    )
    
    # Queue for background processing
    background_tasks.add_task(
        service.process_job,
        job_id
    )
    
    return {
        "job_id": job_id,
        "status": "pending",
        "estimate": estimate,
        "message": "Job queued. Check /jobs/{job_id} for status."
    }

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, service: LLMBatchService = Depends()):
    """Get status of a batch job."""
    job = await service.get_job(job_id)
    return {
        "id": job.id,
        "type": job.type,
        "status": job.status,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "output": job.output_data,
        "error": job.error
    }

@router.get("/jobs/{job_id}/drafts")
async def get_job_drafts(job_id: str, service: LLMBatchService = Depends()):
    """Get draft templates created by a batch job."""
    return await service.get_drafts_for_job(job_id)

@router.post("/jobs/{job_id}/drafts/{draft_id}/approve")
async def approve_draft(
    job_id: str,
    draft_id: str,
    edits: Optional[Dict] = None,
    service: LLMBatchService = Depends()
):
    """Approve a draft template (optionally with edits)."""
    return await service.approve_draft(draft_id, edits)

@router.post("/jobs/{job_id}/drafts/{draft_id}/reject")
async def reject_draft(
    job_id: str,
    draft_id: str,
    reason: str,
    service: LLMBatchService = Depends()
):
    """Reject a draft template."""
    return await service.reject_draft(draft_id, reason)

@router.post("/estimate")
async def estimate_job_cost(
    request: BatchJobRequest,
    service: LLMBatchService = Depends()
):
    """Get cost estimate without creating job."""
    return service.estimate_cost(request.job_type, request.input_data)
```

---

## 🎨 Admin UI: Batch Tools Page

```tsx
// admin-ui/src/pages/BatchTools.tsx

import React, { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Upload, Wand2, FileText, Image, Tag, Clock, CheckCircle, XCircle } from 'lucide-react'

const BATCH_TOOLS = [
  {
    id: 'import_questions',
    name: '📥 Import Question Bank',
    description: 'Convert sample questions to template drafts',
    icon: Upload,
    estimatedCost: '$0.02-0.05 per question'
  },
  {
    id: 'generate_variations',
    name: '📝 Generate Variations',
    description: 'Create word problem variations from base template',
    icon: Wand2,
    estimatedCost: '$0.01 per variation'
  },
  {
    id: 'generate_solutions',
    name: '📖 Generate Solutions',
    description: 'Auto-generate step-by-step solutions',
    icon: FileText,
    estimatedCost: '$0.01 per template'
  },
  {
    id: 'generate_diagrams',
    name: '🎨 Generate Diagrams',
    description: 'Create SVG diagram templates',
    icon: Image,
    estimatedCost: '$0.05 per diagram'
  },
  {
    id: 'tag_misconceptions',
    name: '🏷️ Tag Misconceptions',
    description: 'Generate misconception tags for distractors',
    icon: Tag,
    estimatedCost: '$0.005 per option'
  }
]

export default function BatchTools() {
  const [selectedTool, setSelectedTool] = useState<string | null>(null)
  const [inputData, setInputData] = useState<any>({})
  
  const estimateMutation = useMutation({
    mutationFn: (data: any) => fetch('/api/admin/batch/estimate', {
      method: 'POST',
      body: JSON.stringify(data)
    }).then(r => r.json())
  })
  
  const createJobMutation = useMutation({
    mutationFn: (data: any) => fetch('/api/admin/batch/jobs', {
      method: 'POST',
      body: JSON.stringify(data)
    }).then(r => r.json())
  })
  
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">🤖 LLM Batch Tools</h1>
        <p className="text-gray-600 mt-1">
          One-time batch processing for content acceleration. 
          All outputs go to <span className="font-semibold">draft queue</span> for human review.
        </p>
      </div>
      
      {/* Tool Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {BATCH_TOOLS.map(tool => (
          <button
            key={tool.id}
            onClick={() => setSelectedTool(tool.id)}
            className={`p-4 rounded-xl border-2 text-left transition-all ${
              selectedTool === tool.id 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-3 mb-2">
              <tool.icon className="h-6 w-6 text-blue-600" />
              <span className="font-semibold">{tool.name}</span>
            </div>
            <p className="text-sm text-gray-600">{tool.description}</p>
            <p className="text-xs text-green-600 mt-2">{tool.estimatedCost}</p>
          </button>
        ))}
      </div>
      
      {/* Tool-Specific Input */}
      {selectedTool === 'import_questions' && (
        <ImportQuestionsForm 
          onSubmit={createJobMutation.mutate}
          onEstimate={estimateMutation.mutate}
        />
      )}
      
      {selectedTool === 'generate_variations' && (
        <VariationsForm 
          onSubmit={createJobMutation.mutate}
          onEstimate={estimateMutation.mutate}
        />
      )}
      
      {/* Job History */}
      <JobHistory />
    </div>
  )
}

function ImportQuestionsForm({ onSubmit, onEstimate }) {
  const [questions, setQuestions] = useState('')
  const [chapter, setChapter] = useState('')
  const [grade, setGrade] = useState(10)
  const [estimate, setEstimate] = useState(null)
  
  const handleEstimate = async () => {
    const parsed = parseQuestions(questions)
    const result = await onEstimate({
      job_type: 'import_questions',
      input_data: { questions: parsed, chapter, grade }
    })
    setEstimate(result)
  }
  
  return (
    <div className="bg-white rounded-xl border p-6">
      <h2 className="text-lg font-semibold mb-4">📥 Import Questions</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Paste Questions</label>
          <textarea
            value={questions}
            onChange={(e) => setQuestions(e.target.value)}
            rows={10}
            className="w-full p-3 border rounded-lg font-mono text-sm"
            placeholder={`1. Find the roots of x² − 7x + 10 = 0
2. Solve: 2x² − 5x − 3 = 0
3. The product of two consecutive integers is 132. Find them.`}
          />
          <p className="text-xs text-gray-500 mt-1">
            One question per line. Include answer if known.
          </p>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Chapter</label>
            <input
              value={chapter}
              onChange={(e) => setChapter(e.target.value)}
              className="w-full p-2 border rounded-lg"
              placeholder="Quadratic Equations"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Grade</label>
            <select
              value={grade}
              onChange={(e) => setGrade(Number(e.target.value))}
              className="w-full p-2 border rounded-lg"
            >
              {[1,2,3,4,5,6,7,8,9,10,11,12].map(g => (
                <option key={g} value={g}>Class {g}</option>
              ))}
            </select>
          </div>
        </div>
        
        {/* Cost Estimate */}
        {estimate && (
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-green-800">Estimated Cost:</span>
              <span className="text-xl font-bold text-green-600">
                ${estimate.estimated_cost_usd.toFixed(3)}
              </span>
            </div>
            <p className="text-xs text-green-600 mt-1">
              ~{estimate.estimated_tokens} tokens using {estimate.model}
            </p>
          </div>
        )}
        
        <div className="flex gap-3">
          <button
            onClick={handleEstimate}
            className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            💰 Estimate Cost
          </button>
          <button
            onClick={() => onSubmit({
              job_type: 'import_questions',
              input_data: { questions: parseQuestions(questions), chapter, grade }
            })}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            🚀 Start Import
          </button>
        </div>
      </div>
    </div>
  )
}

function JobHistory() {
  const { data: jobs } = useQuery({
    queryKey: ['batchJobs'],
    queryFn: () => fetch('/api/admin/batch/jobs').then(r => r.json())
  })
  
  return (
    <div className="mt-8">
      <h2 className="text-lg font-semibold mb-4">📋 Recent Jobs</h2>
      <div className="bg-white rounded-xl border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm">Job</th>
              <th className="px-4 py-3 text-left text-sm">Status</th>
              <th className="px-4 py-3 text-left text-sm">Output</th>
              <th className="px-4 py-3 text-left text-sm">Created</th>
              <th className="px-4 py-3 text-left text-sm">Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobs?.map(job => (
              <tr key={job.id} className="border-t">
                <td className="px-4 py-3">{job.type}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={job.status} />
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {job.output?.templates_created && `${job.output.templates_created} templates`}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {new Date(job.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3">
                  {job.status === 'review_pending' && (
                    <a href={`/batch/jobs/${job.id}/review`} className="text-blue-600 hover:underline">
                      Review Drafts →
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

---

## 📊 Cost Summary

| Batch Operation | Typical Size | Cost | Frequency |
|-----------------|--------------|------|-----------|
| Import 1 chapter (20 Qs) | 1 call | $0.40 | Once per chapter |
| Generate 10 variations | 1 call | $0.02 | Per word problem |
| Generate solution | 1 call | $0.01 | Per template |
| Generate diagram | 1 call | $0.05 | Per diagram type |
| Tag misconceptions | 1 call | $0.01 | Per template |

### Monthly Budget Estimate

| Scale | Templates/Month | LLM Cost | Human Hours |
|-------|-----------------|----------|-------------|
| **Startup** | 50 | $5 | 10 hrs |
| **Growth** | 200 | $20 | 30 hrs |
| **Scale** | 500 | $50 | 60 hrs |

---

## ✅ Key Principles Recap

1. **Manual-First**: System works without LLM
2. **Batch-Only**: No runtime LLM calls
3. **Draft Queue**: All LLM output requires human review
4. **Cost Transparent**: Show estimate before running
5. **Audit Trail**: Track who approved what

Would you like me to implement any of these batch tools?
