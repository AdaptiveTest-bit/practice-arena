# Content Generation Strategy V2
## Hybrid Human + LLM + Rules Architecture

**Date:** 18 January 2026  
**Status:** Strategic Planning  
**Scope:** K-12 CBSE/ICSE Content at Scale

---

## 🎯 Core Philosophy

> **"Content writers define WHAT, LLM helps with HOW, Rules ensure QUALITY"**

### The Trinity Model:

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│     CONTENT WRITER          LLM ASSISTANT         RULE ENGINE        │
│     ─────────────          ──────────────         ───────────        │
│                                                                      │
│     • Concept expertise    • Code generation     • Validation        │
│     • Pedagogy intent      • Diagram SVG         • Test coverage     │
│     • Misconception IDs    • LaTeX rendering     • Edge cases        │
│     • Difficulty curve     • Word variations     • Consistency       │
│                                                                      │
│            │                      │                     │            │
│            └──────────────────────┼─────────────────────┘            │
│                                   │                                  │
│                                   ▼                                  │
│                        ┌─────────────────┐                          │
│                        │    TEMPLATE     │                          │
│                        │  (Validated &   │                          │
│                        │   Publishable)  │                          │
│                        └─────────────────┘                          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Question Type Coverage Matrix

Based on CBSE Class 10 Quadratic Equations analysis:

| Question Type | Generation Method | LLM Role | Human Role |
|---------------|-------------------|----------|------------|
| **Standard MCQ** (Find roots) | Template + Formula | None | Define formula |
| **Fill-in-blank** | Template | None | Pattern only |
| **Multi-step solution** | Template + Steps | Generate steps | Validate |
| **Word Problems** | Template + Variations | Generate variations | Approve bank |
| **Assertion-Reason** | Template + Logic | Generate reasoning | Define assertions |
| **Case Study** | Composite Template | Generate context | Structure |
| **Diagram-based** | Template + SVG | Generate SVG | Validate visual |
| **Proof-based** | Step Template | Generate proof | Verify math |

---

## 🏗️ Architecture Components

### Component 1: Question Type Registry

```typescript
interface QuestionType {
  id: string;                    // "MCQ" | "FILL_BLANK" | "ASSERTION_REASON" | "CASE_STUDY" | "DIAGRAM"
  name: string;
  
  // Structure
  parts: QuestionPart[];         // Multi-part for case study
  requires_diagram: boolean;
  requires_latex: boolean;
  
  // Generation
  llm_assisted: boolean;         // Does this type benefit from LLM?
  llm_prompts: LLMPrompt[];      // Pre-defined prompts for this type
  
  // Validation
  validators: Validator[];       // Rules to check
}

// Examples:
const QUESTION_TYPES = {
  MCQ_STANDARD: {
    parts: [{ type: 'question' }, { type: 'options', count: 4 }],
    requires_latex: true,
    llm_assisted: false,  // Pure template
  },
  
  ASSERTION_REASON: {
    parts: [
      { type: 'assertion', label: 'A' },
      { type: 'reason', label: 'R' },
      { type: 'options', count: 4, fixed: true }  // Standard 4 options
    ],
    llm_assisted: true,  // LLM helps generate valid A-R pairs
  },
  
  CASE_STUDY: {
    parts: [
      { type: 'context', max_words: 100 },  // The scenario
      { type: 'sub_question', count: '3-5' }
    ],
    requires_diagram: true,  // Often has graph/image
    llm_assisted: true,
  },
  
  WORD_PROBLEM: {
    parts: [{ type: 'story' }, { type: 'question' }, { type: 'options', count: 4 }],
    llm_assisted: true,  // LLM generates story variations
  }
};
```

### Component 2: Formula Library (Extended)

Current formulas are insufficient. Here's what we need for Class 10 Algebra:

```python
# backend/domain/template_engine/math_formulas.py

class AlgebraFormulas:
    """Extended formula library for Class 10+ content."""
    
    # ========== QUADRATIC EQUATIONS ==========
    
    @staticmethod
    def discriminant(a: int, b: int, c: int) -> int:
        """Calculate discriminant: b² - 4ac"""
        return b * b - 4 * a * c
    
    @staticmethod
    def nature_of_roots(a: int, b: int, c: int) -> str:
        """Determine nature of roots based on discriminant."""
        d = b * b - 4 * a * c
        if d > 0:
            return "real_distinct"
        elif d == 0:
            return "real_equal"
        else:
            return "imaginary"
    
    @staticmethod
    def solve_quadratic(a: int, b: int, c: int) -> tuple:
        """
        Solve ax² + bx + c = 0
        Returns (root1, root2, is_rational)
        """
        d = b * b - 4 * a * c
        if d < 0:
            return (None, None, False)
        
        sqrt_d = d ** 0.5
        if sqrt_d == int(sqrt_d):  # Perfect square
            r1 = (-b + int(sqrt_d)) / (2 * a)
            r2 = (-b - int(sqrt_d)) / (2 * a)
            return (r1, r2, True)
        else:
            # Return symbolic form for LaTeX
            return (f"(-{b}+√{d})/{2*a}", f"(-{b}-√{d})/{2*a}", False)
    
    @staticmethod
    def quadratic_from_roots(r1: int, r2: int) -> tuple:
        """
        Form equation from roots.
        Returns (a, b, c) for x² + bx + c = 0
        """
        return (1, -(r1 + r2), r1 * r2)
    
    @staticmethod
    def sum_of_roots(a: int, b: int, c: int) -> str:
        """Return -b/a as fraction or integer."""
        from math import gcd
        g = gcd(abs(b), abs(a))
        num, den = -b // g, a // g
        return num if den == 1 else f"{num}/{den}"
    
    @staticmethod
    def product_of_roots(a: int, b: int, c: int) -> str:
        """Return c/a as fraction or integer."""
        from math import gcd
        g = gcd(abs(c), abs(a))
        num, den = c // g, a // g
        return num if den == 1 else f"{num}/{den}"
    
    @staticmethod
    def k_for_equal_roots(a_expr: str, b_coeff: int, c: int) -> list:
        """
        Find k such that discriminant = 0.
        For equations like x² - 2kx + 9 = 0
        Returns possible values of k.
        """
        # b² - 4ac = 0
        # (2k)² - 4(1)(9) = 0
        # 4k² = 36
        # k = ±3
        # This needs symbolic solving - delegate to content writer
        pass
    
    # ========== WORD PROBLEM HELPERS ==========
    
    @staticmethod
    def consecutive_integers_product(product: int) -> tuple:
        """Find n such that n(n+1) = product."""
        import math
        # n² + n - product = 0
        d = 1 + 4 * product
        sqrt_d = math.sqrt(d)
        if sqrt_d == int(sqrt_d):
            n = (-1 + int(sqrt_d)) // 2
            if n * (n + 1) == product:
                return (n, n + 1)
        return (None, None)
    
    @staticmethod
    def consecutive_squares_sum(target: int) -> tuple:
        """Find n such that n² + (n+1)² = target."""
        # 2n² + 2n + 1 = target
        # 2n² + 2n + (1 - target) = 0
        import math
        a, b, c = 2, 2, 1 - target
        d = b * b - 4 * a * c
        if d >= 0:
            sqrt_d = math.sqrt(d)
            if sqrt_d == int(sqrt_d):
                n = (-b + int(sqrt_d)) // (2 * a)
                if n > 0 and n * n + (n + 1) ** 2 == target:
                    return (n, n + 1)
        return (None, None)
    
    @staticmethod
    def rectangle_from_area(area: int, length_formula: str) -> tuple:
        """
        Given area and relation between length/breadth.
        E.g., length = 2*breadth + 1
        Returns (length, breadth)
        """
        # This needs symbolic - content writer provides specific values
        pass


class GeometryFormulas:
    """Geometry helpers for coordinate geometry, mensuration."""
    
    @staticmethod
    def parabola_vertex(a: int, b: int, c: int) -> tuple:
        """
        For y = ax² + bx + c, find vertex (h, k).
        h = -b/2a, k = f(h)
        """
        h = -b / (2 * a)
        k = a * h * h + b * h + c
        return (h, k)
    
    @staticmethod
    def parabola_zeros(a: int, b: int, c: int) -> tuple:
        """Find x-intercepts of parabola."""
        d = b * b - 4 * a * c
        if d < 0:
            return (None, None)
        import math
        sqrt_d = math.sqrt(d)
        return ((-b + sqrt_d) / (2 * a), (-b - sqrt_d) / (2 * a))
    
    @staticmethod
    def max_height_projectile(a: int, b: int) -> float:
        """
        For h = ax² + bx (projectile), find max height.
        Vertex at x = -b/2a, height = f(x)
        """
        x = -b / (2 * a)
        return a * x * x + b * x
```

### Component 3: LaTeX Rendering Support

```typescript
// frontend/lib/latex.ts

/**
 * LaTeX utilities for math rendering in questions.
 */

// Common LaTeX patterns for templates
export const LATEX_PATTERNS = {
  // Quadratic equation
  quadratic: (a: number, b: number, c: number) => {
    const aStr = a === 1 ? '' : a === -1 ? '-' : `${a}`;
    const bStr = b > 0 ? `+ ${b}` : b < 0 ? `- ${Math.abs(b)}` : '';
    const cStr = c > 0 ? `+ ${c}` : c < 0 ? `- ${Math.abs(c)}` : '';
    return `${aStr}x^2 ${bStr}x ${cStr} = 0`;
  },
  
  // Fraction
  fraction: (num: number, den: number) => `\\frac{${num}}{${den}}`,
  
  // Square root
  sqrt: (n: number) => `\\sqrt{${n}}`,
  
  // Quadratic formula result
  quadraticRoot: (b: number, d: number, a: number, sign: '+' | '-') => {
    return `\\frac{${-b} ${sign} \\sqrt{${d}}}{${2 * a}}`;
  },
  
  // Sum/Product of roots
  sumOfRoots: (a: number, b: number) => `\\frac{${-b}}{${a}}`,
  productOfRoots: (a: number, c: number) => `\\frac{${c}}{${a}}`,
};

// Render LaTeX in question text
export function renderMathInText(text: string): string {
  // Replace {{latex:...}} with rendered math
  return text.replace(/\{\{latex:(.+?)\}\}/g, (_, latex) => {
    return `$${latex}$`;  // For MathJax/KaTeX
  });
}
```

### Component 4: Diagram Generation System

```typescript
// Types of diagrams needed for K-12

interface DiagramType {
  id: string;
  name: string;
  generator: 'SVG_TEMPLATE' | 'LLM_GENERATED' | 'CHART_JS' | 'GEOGEBRA';
  parameters: DiagramParam[];
}

const DIAGRAM_TYPES: DiagramType[] = [
  // ========== NUMBER THEORY (Class 5-6) ==========
  {
    id: 'factor_tree',
    name: 'Factor Tree',
    generator: 'SVG_TEMPLATE',
    parameters: [{ name: 'number', type: 'integer' }]
  },
  {
    id: 'venn_diagram',
    name: 'Venn Diagram (Factors/Multiples)',
    generator: 'SVG_TEMPLATE',
    parameters: [{ name: 'set_a', type: 'array' }, { name: 'set_b', type: 'array' }]
  },
  {
    id: 'number_line',
    name: 'Number Line',
    generator: 'SVG_TEMPLATE',
    parameters: [{ name: 'start', type: 'integer' }, { name: 'end', type: 'integer' }, { name: 'marks', type: 'array' }]
  },
  
  // ========== ALGEBRA (Class 8-10) ==========
  {
    id: 'parabola',
    name: 'Parabola Graph',
    generator: 'CHART_JS',  // Or custom SVG
    parameters: [{ name: 'a', type: 'number' }, { name: 'b', type: 'number' }, { name: 'c', type: 'number' }]
  },
  {
    id: 'linear_graph',
    name: 'Linear Equation Graph',
    generator: 'CHART_JS',
    parameters: [{ name: 'm', type: 'number' }, { name: 'c', type: 'number' }]
  },
  
  // ========== GEOMETRY (Class 6-10) ==========
  {
    id: 'triangle',
    name: 'Triangle with Labels',
    generator: 'SVG_TEMPLATE',
    parameters: [{ name: 'sides', type: 'array' }, { name: 'angles', type: 'array' }]
  },
  {
    id: 'circle_geometry',
    name: 'Circle with Chord/Tangent',
    generator: 'SVG_TEMPLATE',
    parameters: [{ name: 'radius', type: 'number' }, { name: 'elements', type: 'array' }]
  },
  {
    id: 'coordinate_plane',
    name: 'Coordinate Geometry',
    generator: 'CHART_JS',
    parameters: [{ name: 'points', type: 'array' }, { name: 'lines', type: 'array' }]
  },
  
  // ========== DATA (Class 8-10) ==========
  {
    id: 'histogram',
    name: 'Histogram',
    generator: 'CHART_JS',
    parameters: [{ name: 'data', type: 'array' }, { name: 'bins', type: 'array' }]
  },
  {
    id: 'pie_chart',
    name: 'Pie Chart',
    generator: 'CHART_JS',
    parameters: [{ name: 'values', type: 'array' }, { name: 'labels', type: 'array' }]
  },
  {
    id: 'ogive',
    name: 'Cumulative Frequency Curve',
    generator: 'CHART_JS',
    parameters: [{ name: 'class_marks', type: 'array' }, { name: 'cf', type: 'array' }]
  }
];
```

### Component 5: LLM Integration Points

```typescript
// Where LLM adds value vs where it doesn't

interface LLMIntegrationPoint {
  task: string;
  when_to_use: string;
  prompt_template: string;
  human_review: boolean;
  cost_per_call: 'LOW' | 'MEDIUM' | 'HIGH';
}

const LLM_INTEGRATION_POINTS: LLMIntegrationPoint[] = [
  // ========== HIGH VALUE (Use LLM) ==========
  {
    task: 'Word Problem Variations',
    when_to_use: 'Content writer has base problem, needs 10 variations',
    prompt_template: `
      Base problem: "{{base_problem}}"
      Generate 10 variations with different contexts (sports, shopping, travel, etc.)
      Keep the mathematical structure identical.
      Variables to preserve: {{variables}}
    `,
    human_review: true,  // Review before adding to bank
    cost_per_call: 'LOW'  // ~$0.01 per call
  },
  
  {
    task: 'Misconception Reasoning',
    when_to_use: 'Generate why a wrong answer is chosen',
    prompt_template: `
      Correct answer: {{correct}}
      Wrong answer: {{wrong}}
      Concept: {{concept}}
      Explain in 1 sentence why a student might choose the wrong answer.
    `,
    human_review: false,  // Low risk
    cost_per_call: 'LOW'
  },
  
  {
    task: 'SVG Diagram Generation',
    when_to_use: 'Content writer describes diagram, LLM generates SVG',
    prompt_template: `
      Generate an SVG diagram for a math question.
      Description: {{description}}
      Variables to include: {{variables}}
      Style: Clean, educational, suitable for Class {{grade}}
      Size: 400x300 pixels
    `,
    human_review: true,
    cost_per_call: 'MEDIUM'  // ~$0.05 per call
  },
  
  {
    task: 'Solution Step Generation',
    when_to_use: 'Auto-generate step-by-step solution',
    prompt_template: `
      Question: {{question}}
      Answer: {{answer}}
      Concept: {{concept}}
      Generate a step-by-step solution suitable for Class {{grade}} student.
      Each step should be clear and educational.
    `,
    human_review: true,  # Math accuracy critical
    cost_per_call: 'LOW'
  },
  
  {
    task: 'Case Study Context',
    when_to_use: 'Generate real-world context for multi-part question',
    prompt_template: `
      Mathematical concept: {{concept}}
      Sub-questions: {{sub_questions}}
      Generate a real-world scenario (150 words max) that naturally leads to these questions.
      Make it relatable for Class {{grade}} students.
      Include any necessary data/values.
    `,
    human_review: true,
    cost_per_call: 'LOW'
  },
  
  // ========== LOW VALUE (Don't use LLM) ==========
  {
    task: 'Number Generation',
    when_to_use: 'NEVER - Use deterministic formulas',
    prompt_template: '',
    human_review: false,
    cost_per_call: 'LOW'
  },
  
  {
    task: 'Option Shuffling',
    when_to_use: 'NEVER - Use code',
    prompt_template: '',
    human_review: false,
    cost_per_call: 'LOW'
  },
  
  {
    task: 'Simple Calculations',
    when_to_use: 'NEVER - Use formulas',
    prompt_template: '',
    human_review: false,
    cost_per_call: 'LOW'
  }
];
```

---

## 🔄 Content Writer Workflow

### Workflow for Different Question Types:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTENT WRITER WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STEP 1: Choose Question Type                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ○ MCQ (Standard)        ○ Fill in Blank      ○ True/False          │   │
│  │ ○ Assertion-Reason      ○ Case Study         ○ Match the Following │   │
│  │ ○ Word Problem          ○ Diagram-based      ○ Proof/Derivation    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  STEP 2: Define Core Template (Human)                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Question: Find the roots of {{a}}x² + {{b}}x + {{c}} = 0            │   │
│  │ Concept: math.class10.algebra.quadratic.solve                       │   │
│  │ Difficulty: Medium                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  STEP 3: Define Variables (Human + Formula Library)                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Base: a ∈ [1,2,3], b ∈ [-5,-4,...,5], c ∈ [-10,...,10]             │   │
│  │ Constraint: b² - 4ac ≥ 0 (real roots only)                          │   │
│  │ Computed: roots = solve_quadratic(a, b, c)                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  STEP 4: Request LLM Assistance (Optional)                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [🤖 Generate Word Problem Variations]                               │   │
│  │ [🤖 Create SVG Diagram]                                             │   │
│  │ [🤖 Write Solution Steps]                                           │   │
│  │ [🤖 Generate Assertion-Reason Pairs]                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  STEP 5: Review & Validate                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ✓ 100 test generations passed                                       │   │
│  │ ✓ All roots are real numbers                                        │   │
│  │ ✓ No duplicate options                                              │   │
│  │ ✓ Misconceptions tagged correctly                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  STEP 6: Publish                                                           │
│  [Save as Draft]  [Submit for Review]  [Publish to Production]            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Cost-Benefit Analysis

### LLM Usage Economics:

| Task | Calls/Month | Cost/Call | Monthly Cost | Value |
|------|-------------|-----------|--------------|-------|
| Word problem variations | 500 | $0.01 | $5 | HIGH |
| Solution step generation | 1000 | $0.01 | $10 | HIGH |
| SVG diagram generation | 200 | $0.05 | $10 | HIGH |
| Case study context | 100 | $0.02 | $2 | HIGH |
| Misconception reasoning | 500 | $0.005 | $2.50 | MEDIUM |
| **Total** | | | **~$30/month** | |

### What NOT to use LLM for (saves money):

| Task | Alternative | Savings |
|------|-------------|---------|
| Number generation | Deterministic formulas | 100% |
| Basic calculations | Python functions | 100% |
| Option generation | Template engine | 100% |
| Validation | Rule engine | 100% |
| Equation rendering | LaTeX templates | 100% |

---

## 🛠️ Implementation Phases (Revised)

### Phase 1: Extended Formula Library (Week 1)
- [ ] Add `AlgebraFormulas` class (quadratic, polynomials)
- [ ] Add `GeometryFormulas` class (coordinate, mensuration)
- [ ] Add `StatisticsFormulas` class (mean, median, mode)
- [ ] LaTeX rendering support in frontend
- [ ] Test with 50 Class 10 templates

### Phase 2: Question Type System (Week 2)
- [ ] Question type registry (MCQ, A-R, Case Study, etc.)
- [ ] Multi-part question support
- [ ] Assertion-Reason template type
- [ ] Case study with sub-questions

### Phase 3: LLM Integration Layer (Week 3)
- [ ] LLM service wrapper (OpenAI/Claude)
- [ ] Word problem variation generator
- [ ] Solution step generator
- [ ] SVG diagram generator (with review UI)

### Phase 4: Diagram System (Week 4)
- [ ] SVG template library (10 core diagrams)
- [ ] Chart.js integration for graphs
- [ ] Diagram preview in template editor
- [ ] LLM-assisted diagram creation

### Phase 5: Validation & QA (Week 5)
- [ ] 1000+ generation test for each template
- [ ] Cross-concept validation
- [ ] Difficulty calibration
- [ ] Content review workflow

---

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| Question types supported | 8+ (MCQ, A-R, Case Study, Word, Diagram, Fill, Match, Proof) |
| Grades covered | Class 1-12 |
| Templates per concept | 10+ |
| Generation accuracy | 99.9% valid questions |
| Content writer productivity | 20 templates/day |
| LLM cost per template | < $0.10 |
| Time to create new concept | < 1 hour |

---

## 🔑 Key Decisions

1. **LLM for creativity, not computation** - Never use LLM for math calculations
2. **Human review for LLM outputs** - Especially for diagrams and word problems
3. **Template-first, LLM-assisted** - Core generation is deterministic
4. **Misconceptions are non-negotiable** - Every wrong option has a reason
5. **LaTeX is mandatory for Class 8+** - Proper math rendering

---

## Appendix: Question Type Templates

### A. Standard MCQ (Class 10 Quadratic)

```yaml
type: MCQ_STANDARD
concept: math.class10.algebra.quadratic.solve
question: "Find the roots of {{latex:quadratic(a,b,c)}}"
variables:
  base:
    a: { enum: [1, 2, 3] }
    b: { range: [-10, 10] }
    c: { range: [-20, 20] }
  constraints:
    - "discriminant(a, b, c) >= 0"  # Real roots
    - "discriminant(a, b, c) != 0"  # Distinct roots
  computed:
    roots: "solve_quadratic(a, b, c)"
    discriminant: "discriminant(a, b, c)"
options:
  correct: "{{roots[0]}}, {{roots[1]}}"
  distractors:
    - formula: "{{-b/a}}, {{c/a}}"  # Sum/product confused
      misconception: "confuses_sum_product_with_roots"
    - formula: "{{b/2a}}, {{-c/a}}"  # Formula error
      misconception: "quadratic_formula_error"
    - formula: "{{roots[0]}}, {{-roots[1]}}"  # Sign error
      misconception: "sign_error_in_roots"
solution:
  steps:
    - "Using quadratic formula: x = {{latex:quadraticFormula}}"
    - "Here a = {{a}}, b = {{b}}, c = {{c}}"
    - "Discriminant = {{discriminant}}"
    - "x = {{latex:quadraticRoot(b, discriminant, a, '+')}}"
    - "x = {{latex:quadraticRoot(b, discriminant, a, '-')}}"
    - "Roots: {{roots[0]}} and {{roots[1]}}"
```

### B. Assertion-Reason (Nature of Roots)

```yaml
type: ASSERTION_REASON
concept: math.class10.algebra.quadratic.nature_of_roots
variables:
  base:
    a: { enum: [1] }
    b: { enum: [-4, -3, -2, 2, 3, 4] }
    c: { range: [1, 10] }
  computed:
    discriminant: "discriminant(a, b, c)"
    nature: "nature_of_roots(a, b, c)"
    d_positive: "discriminant > 0"
    d_zero: "discriminant == 0"
    d_negative: "discriminant < 0"
parts:
  assertion:
    text: "The equation {{latex:quadratic(a,b,c)}} has {{nature_text}} roots."
    is_true: true  # Always true based on computation
  reason:
    text: "The discriminant of the equation is {{discriminant_sign}}."
    is_true: true
  relationship: "CORRECT_EXPLANATION"  # R explains A
options:
  - value: "a"
    text: "Both A and R are true and R is the correct explanation of A"
    is_correct: true
  - value: "b"
    text: "Both A and R are true but R is not the correct explanation of A"
    is_correct: false
  - value: "c"
    text: "A is true but R is false"
    is_correct: false
  - value: "d"
    text: "A is false but R is true"
    is_correct: false
```

### C. Case Study (Projectile Motion)

```yaml
type: CASE_STUDY
concept: math.class10.algebra.quadratic.applications
context:
  template: |
    {{context_intro}}
    The path of {{object}} is modeled by the equation:
    h = {{latex:polynomial(a, b, 0)}}
    where h is the height (in meters) and x is the horizontal distance (in meters).
  llm_assist: true  # LLM generates context_intro variations
variables:
  base:
    a: { enum: [-1, -2] }  # Always negative (parabola opens down)
    b: { enum: [4, 6, 8, 10] }
    object: { enum: ["a football", "a cricket ball", "a javelin"] }
  computed:
    max_height: "parabola_vertex(a, b, 0)[1]"
    max_distance_x: "parabola_vertex(a, b, 0)[0]"
    landing_x: "parabola_zeros(a, b, 0)[0]"  # Non-zero root
sub_questions:
  - question: "At what horizontal distance does the {{object}} reach maximum height?"
    answer: "{{max_distance_x}} meters"
    type: "SHORT_ANSWER"
  - question: "What is the maximum height reached?"
    answer: "{{max_height}} meters"
    type: "SHORT_ANSWER"
  - question: "At what horizontal distance does the {{object}} hit the ground?"
    answer: "{{landing_x}} meters"
    type: "SHORT_ANSWER"
diagram:
  type: "parabola"
  parameters:
    a: "{{a}}"
    b: "{{b}}"
    c: 0
    highlight_vertex: true
    highlight_zeros: true
```

### D. Word Problem (Consecutive Integers)

```yaml
type: WORD_PROBLEM
concept: math.class10.algebra.quadratic.word_problems
question:
  base: "The product of two consecutive positive integers is {{product}}. Find the integers."
  llm_variations: true  # Generate context variations
  variation_prompt: |
    Rewrite this problem with different real-world contexts:
    - Age problem (father-son)
    - Rectangle dimensions
    - Sports scoring
    Keep mathematical structure: n(n+1) = {{product}}
variables:
  base:
    product: { enum: [132, 156, 182, 210, 240, 272, 306, 342, 380, 420, 462, 506, 552, 600] }
    # These are carefully chosen: n(n+1) for n = 11,12,13,14,15,16,17,18,19,20,21,22,23,24
  computed:
    n: "consecutive_integers_product(product)[0]"
    n_plus_1: "consecutive_integers_product(product)[1]"
options:
  correct: "{{n}} and {{n_plus_1}}"
  distractors:
    - formula: "{{n-1}} and {{n}}"
      misconception: "off_by_one_error"
    - formula: "{{n}} and {{n+2}}"
      misconception: "non_consecutive"
    - formula: "{{product // 10}} and {{product // (product // 10)}}"
      misconception: "factor_confusion"
solution:
  llm_assist: false  # Use template
  steps:
    - "Let the consecutive integers be n and (n+1)"
    - "Given: n(n+1) = {{product}}"
    - "n² + n - {{product}} = 0"
    - "Solving: n = {{n}}"
    - "Therefore, integers are {{n}} and {{n_plus_1}}"
```

---

## Next Steps

1. **Review this strategy** with content team
2. **Prioritize question types** for immediate implementation
3. **Build LaTeX support** (critical for Class 8+)
4. **Create 5 pilot templates** for Class 10 Quadratic Equations
5. **Measure content writer productivity** before/after

Would you like me to start implementing any specific component?
