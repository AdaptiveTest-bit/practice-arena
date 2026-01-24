# Question Quality Alignment Strategy

## Executive Summary

We have **multiple systems** generating and serving questions, now aligned with a **CDN-primary strategy** for scalability:

| System | Purpose | Quality Fields | Status |
|--------|---------|----------------|--------|
| **Legacy Generators** | Python code generation | `solution_steps`, `visual_hints`, `rich_html_content` | ✅ Rich (deprecated) |
| **QuestionTemplate** | DB template storage | `solution_pattern`, `hint_pattern`, `diagram_config` | ✅ Complete |
| **LeanTemplateEngine** | Template → Question | All quality fields rendered | ✅ Complete |
| **CDN DiagramService** | Diagram rendering | 8+ diagram types, extensible | ✅ Primary |
| **Session Service** | Serves to frontend | Expects all fields | ✅ Complete |

---

## 🎯 Strategic Decision: CDN-Primary Architecture

### Why CDN Diagrams Over Inline HTML?

| Criteria | Inline HTML (`rich_html_content`) | CDN SVG (`diagram_url`) | **Winner** |
|----------|-----------------------------------|-------------------------|------------|
| **Scalability** | ❌ Bloats DB & API responses | ✅ Lightweight URLs | CDN |
| **Browser Caching** | ❌ No caching | ✅ Cached SVGs | CDN |
| **Multi-class scaling** | ❌ Need Python code per class | ✅ JSON config per class | CDN |
| **Admin authoring** | ❌ Requires code | ✅ Visual config | CDN |
| **Security** | ⚠️ `dangerouslySetInnerHTML` | ✅ Safe `<img>` | CDN |
| **Performance** | ❌ Large payloads | ✅ Parallel loading | CDN |
| **Consistency** | ❌ Different per generator | ✅ Standardized renderers | CDN |

### Hybrid Approach

| Use Case | Approach |
|----------|----------|
| **New templates (all classes)** | CDN diagrams via `diagram_config` |
| **Complex interactive content** | Rich HTML pattern (rare cases) |
| **Legacy questions** | Keep inline HTML, migrate gradually |

## Current Architecture Gap

```
┌─────────────────────────────────────────────────────────────────────┐
│                        QUESTION QUALITY FLOW                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  LEGACY GENERATORS (factors_multiples.py) - DEPRECATED               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ ✅ solution_steps: ["Step 1...", "Step 2...", "Step 3..."]   │    │
│  │ ⚠️ rich_html_content: "<div class='diagram'>...</div>"      │    │
│  │ ✅ visual_hints: ["Hint 1", "Hint 2", "Hint 3"]             │    │
│  │ ✅ rich_narrative: "Story context..."                        │    │
│  │ ✅ misconception_info: [{type, why_wrong, teaching_point}]  │    │
│  │ 📌 Status: Works but not scalable for new classes           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                          ↓                                           │
│  SESSION SERVICE (service.py)                                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Expects: solution_steps, visual_hints, diagram_url          │    │
│  │ Returns: solution.steps, visualHints, diagramUrl            │    │
│  │ Fallback: richHtmlContent for legacy questions              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                          ↓                                           │
│  FRONTEND                                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Displays: FeedbackPanel, HintDrawer, RichQuestionContent    │    │
│  │ Primary: <img src={diagramUrl}> (CDN)                       │    │
│  │ Fallback: dangerouslySetInnerHTML (legacy)                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  TEMPLATE-BASED (PRIMARY ARCHITECTURE) ✅                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ QuestionTemplate (DB Model)                                  │    │
│  │ ✅ solution_pattern: Jinja2 template for steps              │    │
│  │ ✅ hint_pattern: Progressive hints template                  │    │
│  │ ✅ narrative_pattern: Story context template                 │    │
│  │ ✅ diagram_config: {type, variables} for CDN                │    │
│  │ ✅ misconceptions: Normalized, linked                        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                          ↓                                           │
│  LeanTemplateEngine                                                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ ✅ Generates: question, options, solution_steps             │    │
│  │ ✅ Generates: visual_hints, rich_narrative                  │    │
│  │ ✅ Generates: diagram_url via CDN service                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                          ↓                                           │
│  CDN DiagramService                                                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ ✅ 8+ diagram types: factors, multiples, gcd, lcm...        │    │
│  │ ✅ Extensible: Add new types per class                      │    │
│  │ ✅ Output: /static/diagrams/{hash}.svg → URL                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Scaling Roadmap: Multi-Class Support

### Current State: Class 5 Factors & Multiples

```
8 diagram types → 8 subtopics → ~40 templates
├── factors          ✅ Factor tree visualization
├── multiples        ✅ Multiples sequence
├── gcd              ✅ GCD via prime factorization
├── lcm              ✅ LCM via multiples list
├── divisibility     ✅ Division with quotient/remainder
├── prime_composite  ✅ Prime vs composite circle
├── factor_pairs     ✅ Factor pair grid
└── prime_factorization ✅ Factor tree breakdown
```

### Phase 1: Class 6 Algebra (Q2 2026)

```
New diagram types needed:
├── equation_balance     # x + 5 = 12 (balance scale visual)
├── number_line_variable # Variable positions on number line
├── expression_tree      # Expression hierarchy
└── coordinate_point     # (x, y) plotting
```

### Phase 2: Class 7 Geometry (Q3 2026)

```
New diagram types needed:
├── angle_diagram        # Angle measurement
├── triangle_types       # Equilateral/Isosceles/Scalene
├── quadrilateral        # Rectangle/Square/Parallelogram
├── area_visualization   # Grid-based area calculation
└── perimeter_trace      # Perimeter path highlighting
```

### Phase 3: Class 8+ Advanced (Q4 2026)

```
New diagram types needed:
├── linear_graph         # y = mx + c plotting
├── bar_chart            # Data visualization
├── pie_chart            # Percentage representation
├── histogram            # Frequency distribution
└── venn_diagram         # Set operations
```

### Extensibility Architecture

```
DiagramCDNService
├── math/
│   ├── arithmetic/           # Class 5
│   │   ├── factors.py
│   │   ├── multiples.py
│   │   ├── gcd_lcm.py
│   │   └── divisibility.py
│   ├── algebra/              # Class 6+
│   │   ├── equation.py
│   │   ├── expression.py
│   │   └── coordinate.py
│   ├── geometry/             # Class 7+
│   │   ├── angle.py
│   │   ├── shape.py
│   │   └── area.py
│   └── statistics/           # Class 8+
│       ├── bar_chart.py
│       ├── pie_chart.py
│       └── histogram.py
└── _render_{type}_svg()      # One method per diagram type
```

---

## What We Have (Existing Quality Features)

### 1. **Question Model** (`api/models/quiz.py`)
```python
class Question(BaseModel):
    solution_steps: List[str]          # ✅ Step-by-step solution
    rich_html_content: Optional[str]   # ✅ HTML diagram/visualization
    rich_narrative: Optional[str]      # ✅ Story context
    visual_hints: Optional[List[str]]  # ✅ Progressive hints
    misconception_info: Optional[List] # ✅ Per-option misconceptions
```

### 2. **Legacy Generator** (`generators/factors_multiples.py`)
```python
# Generates ALL quality fields:
question = Question(
    solution_steps=[
        f"Step 1: Evaluate the assertion - {assertion_text} - This is TRUE",
        f"Step 2: Evaluate the reason - {reason_text} - This is TRUE",
        f"Step 3: Check if reason explains assertion",
        f"Conclusion: Answer is A"
    ],
    rich_html_content=self._render_factors_diagram(target_number, factors),
    visual_hints=[
        f"Start by testing if 1 divides {target_number} evenly",
        f"Test 2, 3, 4, ... up to {target_number}",
        f"Your final list should have exactly {len(factors)} factors"
    ],
    rich_narrative=f"Let's find all the factors of {target_number}...",
)
```

### 3. **CDN Diagram Service** (`domain/cdn/diagram_service.py`) ✅ PRIMARY
```python
# 8+ diagram types supported (extensible):
SUPPORTED_DIAGRAM_TYPES = {
    # Class 5 - Factors & Multiples
    "factors", "multiples", "gcd", "lcm",
    "divisibility", "prime_composite",
    "factor_pairs", "prime_factorization",
    # Future: Class 6+ types added here
}

# Template config drives diagram generation:
diagram_config = {
    "type": "gcd",
    "variables": {"num1": "{{a}}", "num2": "{{b}}", "result": "{{gcd_result}}"}
}
```

### 4. **Template Model** (`db/models/templates.py`) ✅ COMPLETE
```python
class QuestionTemplate:
    template_code          # ✅ Variable generation code
    question_pattern       # ✅ Jinja2 question text
    variable_schema        # ✅ JSON variable rules
    answer_logic           # ✅ Correct answer computation
    option_patterns        # ✅ Option templates
    solution_pattern       # ✅ Jinja2 template for solution steps
    hint_pattern           # ✅ Jinja2 template for progressive hints
    narrative_pattern      # ✅ Jinja2 template for rich narrative
    diagram_config         # ✅ CDN diagram type + variable mappings
```

### 5. **Misconception System** (✅ COMPLETE)
```python
class Misconception:
    code: str              # Unique ID
    title: str             # Brief name
    description: str       # Detailed explanation
    teaching_point: str    # Remediation guidance

class TemplateOptionMisconception:
    template_id            # Links to template
    option_index           # Which wrong option
    misconception_id       # Links to misconception
    custom_explanation     # Template-specific override
```

---

## Alignment Strategy

### Phase 1: Schema Enhancement (Template Model)

Add quality fields to `QuestionTemplate`:

```python
# Add to QuestionTemplate model:
solution_pattern = Column(Text, comment="Jinja2 template for step-by-step solution")
solution_steps_schema = Column(JSON, comment="Schema for solution steps variables")
hint_pattern = Column(Text, comment="Jinja2 template for progressive hints")
narrative_pattern = Column(Text, comment="Jinja2 template for rich narrative")
diagram_config = Column(JSON, comment="Diagram type and variable mappings for CDN")
```

**Migration:** `alembic revision --autogenerate -m "add_quality_fields_to_templates"`

### Phase 2: Engine Enhancement (LeanTemplateEngine)

Update `generate_question()` to produce quality fields:

```python
async def generate_question(self, template_id: int) -> Dict[str, Any]:
    # ... existing generation ...
    
    # NEW: Generate solution steps
    if template.solution_pattern:
        solution_steps = self._render_solution_steps(template, variables)
    
    # NEW: Generate hints
    if template.hint_pattern:
        visual_hints = self._render_hints(template, variables)
    
    # NEW: Generate narrative
    if template.narrative_pattern:
        rich_narrative = self.template_renderer.render_pattern(
            template.narrative_pattern, variables
        )
    
    # NEW: Generate diagram via CDN
    if template.diagram_config:
        diagram_url = await self.cdn_service.render_diagram_dynamically(
            template.diagram_config['type'],
            self._extract_diagram_params(template.diagram_config, variables)
        )
    
    return {
        "payload": {
            # ... existing fields ...
            "solution_steps": solution_steps,
            "visual_hints": visual_hints,
            "rich_narrative": rich_narrative,
            "diagram_url": diagram_url,
        },
        "correct_index": correct_index,
        "variables": variables
    }
```

### Phase 3: Admin UI Enhancement

Add quality fields to template editor:

1. **Solution Builder** - Visual editor for solution steps pattern
2. **Hint Builder** - Progressive hint pattern editor
3. **Diagram Selector** - Pick CDN diagram type + variable mappings
4. **Live Preview** - Shows rendered solution/hints with sample variables

### Phase 4: Data Migration

Migrate existing legacy questions to templates:

```python
# Script: tools/migrate_legacy_to_templates.py
def migrate_generator_to_template(generator_output: Question) -> QuestionTemplate:
    return QuestionTemplate(
        concept_id=generator_output.meta.get('concept_id'),
        question_pattern=generator_output.question_text,
        solution_pattern="\n".join([
            f"Step {{{{i}}}}: {{{{step}}}}" 
            for i, step in enumerate(generator_output.solution_steps, 1)
        ]),
        # ... convert other fields
    )
```

---

## Implementation Priority

| Priority | Task | Impact | Effort | Status |
|----------|------|--------|--------|--------|
| **P0** | Add `solution_pattern` to QuestionTemplate | Enables solution steps | 2h | ✅ DONE |
| **P0** | Update LeanTemplateEngine to render solutions | End-to-end flow | 4h | ✅ DONE |
| **P0** | Add `diagram_config` to QuestionTemplate | CDN integration | 2h | ✅ DONE |
| **P1** | Add `hint_pattern` + `narrative_pattern` | Full quality | 3h | ✅ DONE |
| **P1** | Admin UI: Solution/Hint editors | Authoring UX | 6h | ✅ DONE |
| **P1** | Frontend: Support both `diagramUrl` + `richHtmlContent` | Hybrid display | 2h | ✅ DONE |
| **P2** | Migration script for legacy questions | Content reuse | 4h | 🔲 TODO |
| **P2** | Add diagram types for Class 6 Algebra | Scalability | 8h | 🔲 TODO |
| **P2** | Add diagram types for Class 7 Geometry | Scalability | 8h | 🔲 TODO |

---

## File Changes Completed

### Backend Changes ✅

| File | Change | Status |
|------|--------|--------|
| `db/models/templates.py` | Added `solution_pattern`, `hint_pattern`, `narrative_pattern`, `diagram_config` | ✅ |
| `domain/template_engine/lean_template_engine.py` | Added `_render_solution_steps()`, `_render_hints()`, `_render_narrative()`, `_generate_diagrams()` | ✅ |
| `api/admin/templates.py` | Updated Pydantic models for new fields | ✅ |
| `alembic/versions/edf6e4d85934_add_quality_fields_to_templates.py` | Schema migration applied | ✅ |

### Frontend Changes ✅

| File | Change | Status |
|------|--------|--------|
| `admin-ui/src/pages/TemplateEditor.tsx` | Added "Quality Content" section with solution/hint/narrative editors | ✅ |
| `admin-ui/src/api.ts` | Updated template types | ✅ |
| `frontend/components/FeedbackPanel.tsx` | Added solution steps, rich narrative, visual hints display | ✅ |
| `frontend/components/RichQuestionContent.tsx` | Supports both `diagramUrl` (CDN) and `richHtmlContent` (legacy) | ✅ |

---

## Frontend Diagram Rendering

### Component: `RichQuestionContent.tsx`

```tsx
// Hybrid approach: CDN preferred, legacy fallback
export const QuestionDiagram: FC<Props> = ({ diagramUrl, richHtmlContent }) => {
  // Prefer CDN URL (scalable, cached)
  if (diagramUrl) {
    return <img src={diagramUrl} alt="Diagram" className="max-w-full" />;
  }
  
  // Fallback to inline HTML (legacy)
  if (richHtmlContent) {
    return <div dangerouslySetInnerHTML={{ __html: richHtmlContent }} />;
  }
  
  return null;
};
```

---

## Adding New Diagram Types (For Scaling)

### Step 1: Add SVG Renderer

```python
# backend/domain/cdn/diagram_service.py

async def _render_equation_balance_svg(self, params: Dict) -> str:
    """Render equation balance for algebra (Class 6+)"""
    left = params.get("left_side", "x + 5")
    right = params.get("right_side", "12")
    
    svg = f'''
    <svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
      <text x="100" y="100" font-size="24">{left}</text>
      <text x="200" y="100" font-size="24">=</text>
      <text x="280" y="100" font-size="24">{right}</text>
      <!-- Balance beam visualization -->
    </svg>
    '''
    return svg
```

### Step 2: Register Type

```python
SUPPORTED_DIAGRAM_TYPES = {
    # ... existing types ...
    "equation_balance",  # NEW
}
```

### Step 3: Create Template with Config

```json
{
  "diagram_config": {
    "type": "equation_balance",
    "variables": {
      "left_side": "{{variable}} + {{constant}}",
      "right_side": "{{result}}"
    }
  }
}
```

---

## Recommended Next Steps

1. ~~Approve this strategy~~ ✅ APPROVED
2. ~~Run schema migration~~ ✅ DONE
3. ~~Update LeanTemplateEngine~~ ✅ DONE
4. ~~Update Admin UI~~ ✅ DONE
5. ~~Frontend alignment~~ ✅ DONE
6. **Migration script for legacy questions** 🔲 P2
7. **Add Class 6 diagram types** 🔲 P2 (when scaling)
8. **Add Class 7 diagram types** 🔲 P2 (when scaling)

---

## Appendix: Diagram Type Reference

| Class | Topic | Diagram Type | Status |
|-------|-------|--------------|--------|
| 5 | Factors & Multiples | `factors` | ✅ |
| 5 | Factors & Multiples | `multiples` | ✅ |
| 5 | Factors & Multiples | `gcd` | ✅ |
| 5 | Factors & Multiples | `lcm` | ✅ |
| 5 | Factors & Multiples | `divisibility` | ✅ |
| 5 | Factors & Multiples | `prime_composite` | ✅ |
| 5 | Factors & Multiples | `factor_pairs` | ✅ |
| 5 | Factors & Multiples | `prime_factorization` | ✅ |
| 6 | Algebra | `equation_balance` | 🔲 |
| 6 | Algebra | `number_line_variable` | 🔲 |
| 6 | Algebra | `expression_tree` | 🔲 |
| 7 | Geometry | `angle_diagram` | 🔲 |
| 7 | Geometry | `triangle_types` | 🔲 |
| 7 | Geometry | `area_visualization` | 🔲 |
| 8 | Statistics | `bar_chart` | 🔲 |
| 8 | Statistics | `pie_chart` | 🔲 |