# Universal Template Schema
## Single Format for All Content Creation Paths

**Date:** 18 January 2026  
**Status:** ✅ IMPLEMENTED  
**Purpose:** Define the standard template format that serves as the "drop point" for all content creation methods.

---

## 🚀 Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Pydantic Schema | ✅ Complete | `backend/domain/template_engine/universal_schema.py` |
| Template Ingestor | ✅ Complete | `backend/domain/template_engine/ingestor.py` |
| API Routes | ✅ Complete | `backend/api/routes/templates.py` |
| Test Generation | ✅ Complete | Validates 80% success rate before storing |

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/admin/templates/universal/ingest` | Ingest single template |
| `POST` | `/api/admin/templates/universal/ingest/batch` | Ingest multiple templates |
| `POST` | `/api/admin/templates/universal/preview` | Preview generation without saving |
| `POST` | `/api/admin/templates/universal/import/file` | Import from JSON/YAML file |
| `POST` | `/api/admin/templates/universal/validate` | Validate without saving |
| `GET` | `/api/admin/templates/universal/schema` | Get schema definition & example |
| `GET` | `/api/admin/templates/universal/functions` | List available formula functions |

---

## 🎯 Design Principle

> **"One schema to rule them all"** - Manual creation, LLM generation, and file imports all produce the same format.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Manual UI  ─────┐                                             │
│                   │                                             │
│   LLM Agent  ─────┼──────▶  TEMPLATE JSON  ──────▶  Ingestor   │
│                   │         (Universal)            (Validate)   │
│   File Import ────┘                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Complete Template Schema

```typescript
interface UniversalTemplate {
  // ============================================================
  // SECTION 1: IDENTITY
  // ============================================================
  
  /** Unique identifier (auto-generated if not provided) */
  id?: string;
  
  /** Human-readable name for admin UI */
  name: string;
  
  /** Concept from knowledge graph */
  concept_id: string;
  
  /** Question type determines rendering & validation */
  question_type: QuestionType;
  
  // ============================================================
  // SECTION 2: QUESTION DEFINITION
  // ============================================================

  
  /** The question pattern with {{variables}} */
  question_pattern: string;
  
  /** For multi-part questions (Case Study, A-R) */
  parts?: QuestionPart[];
  
  /** Answer options */
  options: OptionDefinition[];
  
  /** Difficulty 1-4 */
  difficulty: 1 | 2 | 3 | 4;
  
  // ============================================================
  // SECTION 3: VARIABLES
  // ============================================================
  
  /** Variable definitions - the heart of template system */
  variables: VariableSchema;
  
  // ============================================================
  // SECTION 4: SOLUTION & HINTS
  // ============================================================
  
  /** Step-by-step solution pattern */
  solution: SolutionDefinition;
  
  /** Progressive hints */
  hints?: string[];
  
  // ============================================================
  // SECTION 5: VISUAL
  // ============================================================
  
  /** Diagram configuration */
  diagram?: DiagramConfig;
  
  /** LaTeX rendering needed? */
  requires_latex: boolean;
  
  // ============================================================
  // SECTION 6: METADATA
  // ============================================================
  
  /** Creation source */
  source: 'MANUAL' | 'LLM_BATCH' | 'FILE_IMPORT';
  
  /** Workflow status */
  status: 'DRAFT' | 'REVIEW' | 'APPROVED' | 'PUBLISHED';
  
  /** Tags for filtering */
  tags: string[];
  
  /** Word problem variations (if applicable) */
  variations?: WordVariation[];
}

// ============================================================
// SUB-TYPES
// ============================================================

type QuestionType = 
  | 'MCQ'                // Standard multiple choice
  | 'MCQ_MULTI'          // Multiple correct answers
  | 'FILL_BLANK'         // Fill in the blank
  | 'TRUE_FALSE'         // True/False
  | 'ASSERTION_REASON'   // A-R type (CBSE pattern)
  | 'CASE_STUDY'         // Multi-part with context
  | 'MATCH_FOLLOWING'    // Match columns
  | 'ORDERING'           // Arrange in order
  | 'NUMERIC'            // Direct numeric answer

interface OptionDefinition {
  /** Option pattern with {{variables}} */
  pattern: string;
  
  /** Is this the correct answer? */
  is_correct: boolean;
  
  /** For MCQ_MULTI, can have multiple correct */
  
  /** Misconception ID if wrong */
  misconception_id?: string;
  
  /** Why student might choose this (for wrong options) */
  student_thinking?: string;
  
  /** Remediation hint */
  remediation?: string;
}

interface VariableSchema {
  /** Base variables - randomly generated */
  base: Record<string, BaseVariable>;
  
  /** Computed variables - derived from base */
  computed: Record<string, ComputedVariable>;
  
  /** Constraints to ensure valid questions */
  constraints: string[];
}

interface BaseVariable {
  /** Variable type */
  type: 'integer' | 'float' | 'string' | 'boolean';
  
  /** For enum: list of possible values */
  enum?: (number | string)[];
  
  /** For range: min value */
  minimum?: number;
  
  /** For range: max value */
  maximum?: number;
  
  /** Description for content writers */
  description?: string;
}

interface ComputedVariable {
  /** Formula using base variables and functions */
  formula: string;
  
  /** Expected return type */
  type?: 'integer' | 'float' | 'string' | 'boolean' | 'list' | 'tuple';
  
  /** Description */
  description?: string;
}

interface SolutionDefinition {
  /** Solution steps with {{variables}} */
  steps: SolutionStep[];
  
  /** Additional computed variables needed for solution */
  computed_vars?: Record<string, string>;
}

interface SolutionStep {
  /** Step number */
  number: number;
  
  /** Step text */
  text: string;
  
  /** LaTeX for this step (optional) */
  latex?: string;
  
  /** Explanation for why this step */
  explanation?: string;
}

interface DiagramConfig {
  /** Diagram type from library */
  type: string;
  
  /** Parameters passed to diagram generator */
  parameters: Record<string, string>;
  
  /** Custom SVG template (if not using library) */
  custom_svg?: string;
}

interface WordVariation {
  /** Variation ID */
  id: string;
  
  /** Context category */
  context: string;
  
  /** Question pattern (replaces main question_pattern) */
  question_pattern: string;
  
  /** Answer pattern */
  answer_pattern: string;
  
  /** Status */
  status: 'DRAFT' | 'APPROVED';
}

interface QuestionPart {
  /** Part type */
  type: 'assertion' | 'reason' | 'context' | 'sub_question';
  
  /** Part label (e.g., "A", "R", "i", "ii") */
  label?: string;
  
  /** Part pattern */
  pattern: string;
  
  /** Is this part true/correct? (for A-R) */
  is_true?: boolean;
  
  /** Sub-question options (for case study) */
  options?: OptionDefinition[];
}
```

---

## 📝 Example: Quadratic Equations (Your 20 Questions)

### Example 1: Standard MCQ (Find Roots)

```json
{
  "name": "Quadratic - Find Roots by Factorization",
  "concept_id": "math.class10.quadratic.solve_factorization",
  "question_type": "MCQ",
  
  "question_pattern": "Find the roots of x² − {{sum}}x + {{product}} = 0",
  
  "variables": {
    "base": {
      "root1": { "type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] },
      "root2": { "type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
    },
    "computed": {
      "sum": { "formula": "root1 + root2" },
      "product": { "formula": "root1 * root2" }
    },
    "constraints": [
      "root1 < root2",
      "root1 != root2"
    ]
  },
  
  "options": [
    {
      "pattern": "{{root1}}, {{root2}}",
      "is_correct": true
    },
    {
      "pattern": "{{root1}}, {{-root2}}",
      "is_correct": false,
      "misconception_id": "SIGN_ERROR",
      "student_thinking": "Forgot that both roots should be positive for positive product"
    },
    {
      "pattern": "{{sum}}, {{product}}",
      "is_correct": false,
      "misconception_id": "SUM_PRODUCT_CONFUSION",
      "student_thinking": "Confused sum/product of roots with the roots themselves"
    },
    {
      "pattern": "{{root1 + 1}}, {{root2 - 1}}",
      "is_correct": false,
      "misconception_id": "FACTORIZATION_ERROR",
      "student_thinking": "Made arithmetic error in factorization"
    }
  ],
  
  "difficulty": 2,
  "requires_latex": true,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "We need two numbers whose sum is {{sum}} and product is {{product}}" },
      { "number": 2, "text": "Think: What two numbers multiply to {{product}}?" },
      { "number": 3, "text": "{{root1}} × {{root2}} = {{product}} ✓" },
      { "number": 4, "text": "{{root1}} + {{root2}} = {{sum}} ✓" },
      { "number": 5, "text": "Therefore, x² − {{sum}}x + {{product}} = (x − {{root1}})(x − {{root2}})" },
      { "number": 6, "text": "Roots are x = {{root1}} and x = {{root2}}" }
    ]
  },
  
  "hints": [
    "Think about what two numbers add up to {{sum}}",
    "Those same numbers should multiply to give {{product}}",
    "Try listing factor pairs of {{product}}"
  ],
  
  "source": "LLM_BATCH",
  "status": "DRAFT",
  "tags": ["quadratic", "factorization", "roots"]
}
```

### Example 2: Nature of Roots (Discriminant)

```json
{
  "name": "Quadratic - Nature of Roots",
  "concept_id": "math.class10.quadratic.nature_of_roots",
  "question_type": "MCQ",
  
  "question_pattern": "Find the nature of roots of the equation x² − {{b}}x + {{c}} = 0",
  
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [2, 3, 4, 5, 6] },
      "c": { "type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
    },
    "computed": {
      "discriminant": { "formula": "b*b - 4*1*c" },
      "nature": { "formula": "nature_of_roots(1, -b, c)" },
      "nature_text": { 
        "formula": "'two distinct real roots' if discriminant > 0 else ('two equal real roots' if discriminant == 0 else 'no real roots (imaginary)')" 
      }
    },
    "constraints": []
  },
  
  "options": [
    {
      "pattern": "{{nature_text}}",
      "is_correct": true
    },
    {
      "pattern": "two distinct real roots",
      "is_correct": false,
      "misconception_id": "DISCRIMINANT_CALC_ERROR",
      "student_thinking": "Made calculation error in discriminant"
    },
    {
      "pattern": "two equal real roots",
      "is_correct": false,
      "misconception_id": "DISCRIMINANT_CONDITION_ERROR",
      "student_thinking": "Confused conditions: D=0 means equal, not D>0"
    },
    {
      "pattern": "no real roots",
      "is_correct": false,
      "misconception_id": "NEGATIVE_DISCRIMINANT_ERROR",
      "student_thinking": "Thought negative coefficient means imaginary roots"
    }
  ],
  
  "difficulty": 2,
  "requires_latex": true,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "For ax² + bx + c = 0, discriminant D = b² − 4ac" },
      { "number": 2, "text": "Here a = 1, b = −{{b}}, c = {{c}}", "latex": "a = 1, b = -{{b}}, c = {{c}}" },
      { "number": 3, "text": "D = (−{{b}})² − 4(1)({{c}}) = {{b}}² − 4×{{c}}", "latex": "D = (-{{b}})^2 - 4(1)({{c}}) = {{b}}^2 - 4 \\times {{c}}" },
      { "number": 4, "text": "D = {{b*b}} − {{4*c}} = {{discriminant}}" },
      { "number": 5, "text": "Since D {{'>0' if discriminant > 0 else ('=0' if discriminant == 0 else '<0')}}, the equation has {{nature_text}}" }
    ]
  },
  
  "source": "LLM_BATCH",
  "status": "DRAFT",
  "tags": ["quadratic", "discriminant", "nature-of-roots"]
}
```

### Example 3: Word Problem (Consecutive Integers)

```json
{
  "name": "Quadratic - Consecutive Integers Product",
  "concept_id": "math.class10.quadratic.word_problems",
  "question_type": "MCQ",
  
  "question_pattern": "{{variation_pattern}}",
  
  "variables": {
    "base": {
      "n": { "type": "integer", "enum": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20] }
    },
    "computed": {
      "n_plus_1": { "formula": "n + 1" },
      "product": { "formula": "n * (n + 1)" }
    },
    "constraints": []
  },
  
  "options": [
    {
      "pattern": "{{n}} and {{n_plus_1}}",
      "is_correct": true
    },
    {
      "pattern": "{{n - 1}} and {{n}}",
      "is_correct": false,
      "misconception_id": "OFF_BY_ONE",
      "student_thinking": "Made off-by-one error in calculation"
    },
    {
      "pattern": "{{n}} and {{n + 2}}",
      "is_correct": false,
      "misconception_id": "NON_CONSECUTIVE",
      "student_thinking": "Found factors but not consecutive ones"
    },
    {
      "pattern": "{{n - 2}} and {{n + 1}}",
      "is_correct": false,
      "misconception_id": "RANDOM_FACTORS",
      "student_thinking": "Found numbers that multiply to product but aren't consecutive"
    }
  ],
  
  "difficulty": 3,
  "requires_latex": false,
  
  "variations": [
    {
      "id": "var_base",
      "context": "abstract",
      "question_pattern": "The product of two consecutive positive integers is {{product}}. Find the integers.",
      "answer_pattern": "{{n}} and {{n_plus_1}}",
      "status": "APPROVED"
    },
    {
      "id": "var_age",
      "context": "age",
      "question_pattern": "Rahul's current age multiplied by his age next year equals {{product}}. How old is Rahul?",
      "answer_pattern": "Rahul is {{n}} years old",
      "status": "APPROVED"
    },
    {
      "id": "var_dimensions",
      "context": "geometry",
      "question_pattern": "A rectangular plot has length 1m more than its width. If the area is {{product}} sq.m, find the dimensions.",
      "answer_pattern": "Width = {{n}}m, Length = {{n_plus_1}}m",
      "status": "APPROVED"
    },
    {
      "id": "var_pages",
      "context": "books",
      "question_pattern": "Two consecutive pages in a book have page numbers whose product is {{product}}. Find the page numbers.",
      "answer_pattern": "Pages {{n}} and {{n_plus_1}}",
      "status": "APPROVED"
    }
  ],
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Let the consecutive integers be n and (n+1)" },
      { "number": 2, "text": "Given: n(n+1) = {{product}}" },
      { "number": 3, "text": "n² + n − {{product}} = 0" },
      { "number": 4, "text": "Using quadratic formula or factorization:" },
      { "number": 5, "text": "n = {{n}} (taking positive value)" },
      { "number": 6, "text": "The integers are {{n}} and {{n_plus_1}}" }
    ]
  },
  
  "source": "LLM_BATCH",
  "status": "DRAFT",
  "tags": ["quadratic", "word-problem", "consecutive-integers"]
}
```

### Example 4: Assertion-Reason

```json
{
  "name": "Quadratic - Assertion Reason (Discriminant)",
  "concept_id": "math.class10.quadratic.assertion_reason",
  "question_type": "ASSERTION_REASON",
  
  "question_pattern": "",
  
  "parts": [
    {
      "type": "assertion",
      "label": "A",
      "pattern": "The equation x² − {{b}}x + {{c}} = 0 has two real and distinct roots.",
      "is_true": "{{discriminant > 0}}"
    },
    {
      "type": "reason",
      "label": "R",
      "pattern": "The discriminant of the equation is {{discriminant_sign}}.",
      "is_true": true
    }
  ],
  
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [5, 6, 7, 8] },
      "c": { "type": "integer", "enum": [1, 2, 3, 4, 5, 6] }
    },
    "computed": {
      "discriminant": { "formula": "b*b - 4*c" },
      "discriminant_sign": { "formula": "'positive' if discriminant > 0 else ('zero' if discriminant == 0 else 'negative')" },
      "assertion_true": { "formula": "discriminant > 0" },
      "correct_option": { 
        "formula": "'a' if (assertion_true and discriminant > 0) else ('c' if (not assertion_true and discriminant > 0) else 'd')" 
      }
    },
    "constraints": []
  },
  
  "options": [
    {
      "pattern": "Both A and R are true and R is the correct explanation of A",
      "is_correct": "{{correct_option == 'a'}}"
    },
    {
      "pattern": "Both A and R are true but R is not the correct explanation of A",
      "is_correct": "{{correct_option == 'b'}}"
    },
    {
      "pattern": "A is true but R is false",
      "is_correct": "{{correct_option == 'c'}}"
    },
    {
      "pattern": "A is false but R is true",
      "is_correct": "{{correct_option == 'd'}}"
    }
  ],
  
  "difficulty": 3,
  "requires_latex": true,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "For the equation x² − {{b}}x + {{c}} = 0:" },
      { "number": 2, "text": "a = 1, b = −{{b}}, c = {{c}}" },
      { "number": 3, "text": "Discriminant D = b² − 4ac = {{b}}² − 4({{c}}) = {{discriminant}}" },
      { "number": 4, "text": "Since D = {{discriminant}} is {{discriminant_sign}}:" },
      { "number": 5, "text": "Assertion is {{'TRUE' if assertion_true else 'FALSE'}} (D {{'>0' if discriminant > 0 else '≤0'}} means {{'distinct real roots' if discriminant > 0 else 'not distinct real roots'}})" },
      { "number": 6, "text": "Reason is TRUE (discriminant is indeed {{discriminant_sign}})" },
      { "number": 7, "text": "R correctly explains A. Answer: {{correct_option | upper}}" }
    ]
  },
  
  "source": "LLM_BATCH",
  "status": "DRAFT",
  "tags": ["quadratic", "assertion-reason", "discriminant"]
}
```

### Example 5: Case Study (Projectile)

```json
{
  "name": "Quadratic - Case Study (Projectile Motion)",
  "concept_id": "math.class10.quadratic.applications.projectile",
  "question_type": "CASE_STUDY",
  
  "question_pattern": "",
  
  "parts": [
    {
      "type": "context",
      "pattern": "{{context_variation}}\n\nThe path of the ball is modeled by the equation h = −x² + {{b}}x, where h is the height (in meters) and x is the horizontal distance (in meters)."
    },
    {
      "type": "sub_question",
      "label": "i",
      "pattern": "At what horizontal distance does the ball reach maximum height?",
      "options": [
        { "pattern": "{{max_x}} m", "is_correct": true },
        { "pattern": "{{max_x + 1}} m", "is_correct": false, "misconception_id": "VERTEX_CALC_ERROR" },
        { "pattern": "{{b}} m", "is_correct": false, "misconception_id": "COEFFICIENT_CONFUSION" },
        { "pattern": "{{landing_x}} m", "is_correct": false, "misconception_id": "CONFUSED_MAX_WITH_LANDING" }
      ]
    },
    {
      "type": "sub_question",
      "label": "ii",
      "pattern": "What is the maximum height reached by the ball?",
      "options": [
        { "pattern": "{{max_height}} m", "is_correct": true },
        { "pattern": "{{b}} m", "is_correct": false, "misconception_id": "USED_COEFFICIENT" },
        { "pattern": "{{max_height - 1}} m", "is_correct": false, "misconception_id": "CALCULATION_ERROR" },
        { "pattern": "{{max_x}} m", "is_correct": false, "misconception_id": "CONFUSED_X_WITH_HEIGHT" }
      ]
    },
    {
      "type": "sub_question",
      "label": "iii",
      "pattern": "At what horizontal distance does the ball hit the ground?",
      "options": [
        { "pattern": "{{landing_x}} m", "is_correct": true },
        { "pattern": "{{max_x}} m", "is_correct": false, "misconception_id": "GAVE_VERTEX_NOT_ROOT" },
        { "pattern": "{{landing_x + 2}} m", "is_correct": false, "misconception_id": "ARITHMETIC_ERROR" },
        { "pattern": "{{b - 1}} m", "is_correct": false, "misconception_id": "RANDOM_ANSWER" }
      ]
    }
  ],
  
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [4, 6, 8, 10] },
      "context_type": { "type": "string", "enum": ["football", "cricket", "javelin"] }
    },
    "computed": {
      "max_x": { "formula": "b / 2", "description": "x-coordinate of vertex: -b/2a = -b/2(-1) = b/2" },
      "max_height": { "formula": "(b * b) / 4", "description": "y at vertex: -(b/2)² + b(b/2) = b²/4" },
      "landing_x": { "formula": "b", "description": "Non-zero root: -x² + bx = 0 → x(b-x) = 0 → x = b" },
      "context_variation": {
        "formula": "{'football': 'In a football match, a player kicks the ball which follows a parabolic path.', 'cricket': 'A cricket ball is hit by a batsman and follows a curved trajectory.', 'javelin': 'An athlete throws a javelin in a sports competition.'}[context_type]"
      }
    },
    "constraints": []
  },
  
  "difficulty": 4,
  "requires_latex": true,
  
  "diagram": {
    "type": "parabola",
    "parameters": {
      "a": "-1",
      "b": "{{b}}",
      "c": "0",
      "highlight_vertex": "true",
      "highlight_zeros": "true",
      "labels": {
        "vertex": "({{max_x}}, {{max_height}})",
        "zero1": "(0, 0)",
        "zero2": "({{landing_x}}, 0)"
      }
    }
  },
  
  "solution": {
    "steps": [
      { "number": 1, "text": "The equation h = −x² + {{b}}x is a downward parabola (coefficient of x² is negative)" },
      { "number": 2, "text": "Maximum height occurs at vertex: x = −b/2a = −{{b}}/2(−1) = {{max_x}}" },
      { "number": 3, "text": "Maximum height h = −({{max_x}})² + {{b}}({{max_x}}) = −{{max_x * max_x}} + {{b * max_x}} = {{max_height}} m" },
      { "number": 4, "text": "Ball hits ground when h = 0: −x² + {{b}}x = 0" },
      { "number": 5, "text": "x(−x + {{b}}) = 0 → x = 0 or x = {{b}}" },
      { "number": 6, "text": "x = {{landing_x}} m (the non-zero root)" }
    ]
  },
  
  "source": "LLM_BATCH",
  "status": "DRAFT",
  "tags": ["quadratic", "case-study", "projectile", "vertex", "parabola"]
}
```

---

## 🔄 Template Ingestor

The single entry point for all templates:

```python
# backend/domain/template_engine/ingestor.py

from typing import Dict, Any, List
from pydantic import ValidationError
import json

class TemplateIngestor:
    """
    Universal template ingestion - validates and stores templates
    regardless of their source (manual, LLM, file import).
    """
    
    def __init__(self, formula_library, db):
        self.formulas = formula_library
        self.db = db
    
    def ingest(self, template: Dict[str, Any], source: str = 'MANUAL') -> Dict:
        """
        Main entry point - validate and store a template.
        
        Args:
            template: Template in universal schema format
            source: 'MANUAL' | 'LLM_BATCH' | 'FILE_IMPORT'
        
        Returns:
            Stored template with ID and validation results
        """
        # Step 1: Schema validation
        validation = self._validate_schema(template)
        if not validation['valid']:
            return {'success': False, 'errors': validation['errors']}
        
        # Step 2: Formula validation
        formula_check = self._validate_formulas(template)
        if not formula_check['valid']:
            return {'success': False, 'errors': formula_check['errors']}
        
        # Step 3: Test generation (generate 10 questions to verify)
        test_result = self._test_generation(template, count=10)
        if not test_result['valid']:
            return {'success': False, 'errors': test_result['errors']}
        
        # Step 4: Store template
        template['source'] = source
        template['status'] = 'DRAFT' if source != 'MANUAL' else template.get('status', 'DRAFT')
        template['validation'] = {
            'test_generations': test_result['count'],
            'validated_at': datetime.utcnow().isoformat()
        }
        
        stored = self.db.templates.save(template)
        
        return {
            'success': True,
            'template_id': stored['id'],
            'status': stored['status'],
            'test_generations': test_result['count'],
            'warnings': validation.get('warnings', [])
        }
    
    def ingest_batch(self, templates: List[Dict], source: str = 'LLM_BATCH') -> Dict:
        """Ingest multiple templates at once."""
        results = []
        for template in templates:
            result = self.ingest(template, source)
            results.append({
                'name': template.get('name', 'Unknown'),
                **result
            })
        
        return {
            'total': len(templates),
            'success': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
    
    def _validate_schema(self, template: Dict) -> Dict:
        """Validate template matches universal schema."""
        errors = []
        warnings = []
        
        # Required fields
        required = ['name', 'concept_id', 'question_type', 'variables', 'options']
        for field in required:
            if field not in template:
                errors.append(f"Missing required field: {field}")
        
        # Question pattern or parts required
        if 'question_pattern' not in template and 'parts' not in template:
            errors.append("Either 'question_pattern' or 'parts' is required")
        
        # Validate options
        if 'options' in template:
            correct_count = sum(1 for o in template['options'] if o.get('is_correct'))
            if correct_count == 0:
                errors.append("At least one correct option required")
            if template.get('question_type') == 'MCQ' and correct_count > 1:
                warnings.append("MCQ should have exactly one correct answer")
        
        # Validate variables
        if 'variables' in template:
            if 'base' not in template['variables'] and 'computed' not in template['variables']:
                errors.append("Variables must have 'base' or 'computed'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_formulas(self, template: Dict) -> Dict:
        """Validate all formulas/computed variables are executable."""
        errors = []
        
        computed = template.get('variables', {}).get('computed', {})
        for var_name, var_def in computed.items():
            formula = var_def.get('formula', var_def) if isinstance(var_def, dict) else var_def
            try:
                # Try to compile the formula
                compile(formula, '<string>', 'eval')
                
                # Check if required functions exist
                for func in self._extract_function_calls(formula):
                    if not self.formulas.has_function(func):
                        errors.append(f"Unknown function '{func}' in variable '{var_name}'")
            except SyntaxError as e:
                errors.append(f"Invalid formula for '{var_name}': {e}")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _test_generation(self, template: Dict, count: int = 10) -> Dict:
        """Generate test questions to verify template works."""
        errors = []
        generated = 0
        
        try:
            from .variable_generator import VariableGenerator
            from .renderer import TemplateRenderer
            
            generator = VariableGenerator(self.formulas)
            renderer = TemplateRenderer()
            
            for i in range(count):
                try:
                    # Generate variables
                    variables = generator.generate(template['variables'])
                    
                    # Render question
                    if 'question_pattern' in template:
                        question = renderer.render(template['question_pattern'], variables)
                    
                    # Render options
                    options = []
                    for opt in template['options']:
                        rendered = renderer.render(opt['pattern'], variables)
                        options.append(rendered)
                    
                    # Check for duplicates
                    if len(options) != len(set(options)):
                        errors.append(f"Generation {i+1}: Duplicate options detected")
                        continue
                    
                    generated += 1
                    
                except Exception as e:
                    errors.append(f"Generation {i+1} failed: {str(e)}")
            
            # Require at least 80% success rate
            if generated < count * 0.8:
                errors.append(f"Only {generated}/{count} generations succeeded")
                return {'valid': False, 'errors': errors, 'count': generated}
            
            return {'valid': True, 'errors': [], 'count': generated}
            
        except Exception as e:
            return {'valid': False, 'errors': [str(e)], 'count': 0}
    
    def _extract_function_calls(self, formula: str) -> List[str]:
        """Extract function names from formula string."""
        import re
        return re.findall(r'(\w+)\s*\(', formula)
```

---

## 🎨 Single Upload UI

```tsx
// admin-ui/src/pages/TemplateUpload.tsx

/**
 * Universal Template Upload
 * Single entry point for all template creation methods
 */

export default function TemplateUpload() {
  const [mode, setMode] = useState<'manual' | 'llm' | 'file'>('manual')
  
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">📥 Add Templates</h1>
      <p className="text-gray-600 mb-6">
        Choose how you want to create templates. All methods produce the same format.
      </p>
      
      {/* Mode Selector */}
      <div className="flex gap-4 mb-8">
        <ModeButton 
          active={mode === 'manual'} 
          onClick={() => setMode('manual')}
          icon="✍️"
          title="Manual Entry"
          description="Use the form editor"
        />
        <ModeButton 
          active={mode === 'llm'} 
          onClick={() => setMode('llm')}
          icon="🤖"
          title="LLM Generate"
          description="Paste questions, AI converts"
        />
        <ModeButton 
          active={mode === 'file'} 
          onClick={() => setMode('file')}
          icon="📁"
          title="File Import"
          description="Upload JSON/YAML"
        />
      </div>
      
      {/* Mode-specific UI */}
      {mode === 'manual' && <ManualEditor />}
      {mode === 'llm' && <LLMGenerator />}
      {mode === 'file' && <FileImporter />}
      
      {/* Common: Preview & Submit */}
      <TemplatePreview />
    </div>
  )
}

function LLMGenerator() {
  const [questions, setQuestions] = useState('')
  const [chapter, setChapter] = useState('')
  const [grade, setGrade] = useState(10)
  const [generating, setGenerating] = useState(false)
  const [preview, setPreview] = useState<any>(null)
  
  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const response = await fetch('/api/admin/batch/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_type: 'import_questions',
          input_data: { 
            questions: questions.split('\n').filter(q => q.trim()),
            chapter,
            grade
          }
        })
      })
      const job = await response.json()
      
      // Poll for results
      await pollJobCompletion(job.job_id, setPreview)
    } finally {
      setGenerating(false)
    }
  }
  
  return (
    <div className="space-y-4">
      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
        <p className="text-sm text-yellow-800">
          💡 <strong>Tip:</strong> Paste your questions below (one per line). 
          The AI will convert them to templates. Estimated cost: $0.02-0.05 per question.
        </p>
      </div>
      
      <textarea
        value={questions}
        onChange={(e) => setQuestions(e.target.value)}
        rows={12}
        className="w-full p-4 border rounded-lg font-mono text-sm"
        placeholder={`1. Find the roots of x² − 7x + 10 = 0
2. Solve: 2x² − 5x − 3 = 0  
3. For what value of k will x² − 2kx + 9 = 0 have equal roots?
4. The product of two consecutive positive integers is 1320. Find them.
5. Find the nature of roots of x² − 4x + 5 = 0`}
      />
      
      <div className="grid grid-cols-2 gap-4">
        <select 
          value={chapter} 
          onChange={(e) => setChapter(e.target.value)}
          className="p-2 border rounded-lg"
        >
          <option value="">Select Chapter</option>
          <option value="quadratic_equations">Quadratic Equations</option>
          <option value="arithmetic_progressions">Arithmetic Progressions</option>
          {/* ... more chapters */}
        </select>
        
        <select
          value={grade}
          onChange={(e) => setGrade(Number(e.target.value))}
          className="p-2 border rounded-lg"
        >
          {[1,2,3,4,5,6,7,8,9,10,11,12].map(g => (
            <option key={g} value={g}>Class {g}</option>
          ))}
        </select>
      </div>
      
      <button
        onClick={handleGenerate}
        disabled={generating || !questions.trim()}
        className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
      >
        {generating ? '🔄 Generating...' : '🤖 Generate Templates'}
      </button>
      
      {/* Preview generated templates */}
      {preview && (
        <div className="mt-8">
          <h3 className="font-semibold mb-4">Generated Templates (Review Required)</h3>
          {preview.templates.map((t, i) => (
            <TemplateCard key={i} template={t} />
          ))}
        </div>
      )}
    </div>
  )
}
```

---

## 📊 Summary

### The Drop Point Principle

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   "How it's created doesn't matter.                            │
│    What matters is it matches the Universal Schema."           │
│                                                                 │
│   ┌─────────────┐                                               │
│   │ Manual UI   │──┐                                            │
│   └─────────────┘  │     ┌──────────────────┐                  │
│                    │     │                  │                  │
│   ┌─────────────┐  ├────▶│ Universal JSON   │────▶ Ingestor   │
│   │ LLM Batch   │──┤     │                  │      (Validate)  │
│   └─────────────┘  │     └──────────────────┘         │        │
│                    │                                  ▼        │
│   ┌─────────────┐  │                             Database      │
│   │ File Upload │──┘                                           │
│   └─────────────┘                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### What You Get

| Feature | Manual | LLM Batch | File Import |
|---------|--------|-----------|-------------|
| Same JSON format | ✅ | ✅ | ✅ |
| Schema validation | ✅ | ✅ | ✅ |
| Formula validation | ✅ | ✅ | ✅ |
| Test generation | ✅ | ✅ | ✅ |
| Status tracking | ✅ | ✅ | ✅ |
| Misconceptions | Manual | Auto-generated | Manual |
| Variations | Manual | Auto-generated | Manual |
| Cost | $0 | ~$0.03/template | $0 |

Would you like me to implement any of these components?
