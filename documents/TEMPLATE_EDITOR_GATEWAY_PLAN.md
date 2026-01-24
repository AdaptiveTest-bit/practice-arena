# Template Editor Gateway Plan
## One UI to Rule All Content Creation

**Goal:** Content team can add concepts, define formulas, and create question templates - all from the Admin UI, zero codebase changes.

---

## 🎯 Vision

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEMPLATE EDITOR GATEWAY                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. CONCEPT MANAGER        2. FORMULA BUILDER      3. TEMPLATE      │
│  ┌─────────────────┐      ┌─────────────────┐     EDITOR           │
│  │ + Add Concept   │      │ + Create Formula│     ┌─────────────┐  │
│  │ • Parent Node   │      │ • Name          │     │ Question    │  │
│  │ • Prerequisites │      │ • Parameters    │     │ Options     │  │
│  │ • Difficulty    │      │ • Python Code   │     │ Solution    │  │
│  │ • Tags          │      │ • Test Cases    │     │ Variables   │  │
│  └─────────────────┘      └─────────────────┘     └─────────────┘  │
│           │                       │                      │          │
│           └───────────────────────┴──────────────────────┘          │
│                              │                                      │
│                    ┌─────────▼─────────┐                           │
│                    │  PREVIEW & TEST   │                           │
│                    │  Generate 10 Qs   │                           │
│                    │  Validate All     │                           │
│                    └───────────────────┘                           │
│                              │                                      │
│                    ┌─────────▼─────────┐                           │
│                    │     PUBLISH       │                           │
│                    │  → Live in App    │                           │
│                    └───────────────────┘                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Features Breakdown

### Feature 1: Concept Manager (Add to Graph)

**What:** Add new concepts to the knowledge graph directly from UI

```typescript
interface ConceptDefinition {
  id: string;                    // Auto-generated: math.class5.fractions.addition
  name: string;                  // "Fraction Addition"
  
  // Graph Position
  parent_concept_id: string;     // Where in graph? "math.class5.fractions"
  prerequisites: string[];       // ["math.class5.fractions.basics"]
  
  // Metadata
  grade: number;                 // 5
  subject: string;               // "mathematics"
  chapter: string;               // "Fractions"
  difficulty_range: [number, number]; // [1, 4]
  
  // Learning Objectives
  bloom_levels: string[];        // ["UNDERSTAND", "APPLY"]
  learning_outcomes: string[];   // ["Add fractions with same denominator"]
  
  // Tags for search
  tags: string[];                // ["fractions", "addition", "same-denominator"]
}
```

**UI:**
```
┌─────────────────────────────────────────────────────────────┐
│  📚 Add New Concept                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Concept Name: [Fraction Addition____________]              │
│                                                             │
│  📍 Position in Graph:                                      │
│  Subject: [Mathematics ▼]  Grade: [Class 5 ▼]              │
│  Chapter: [Fractions   ▼]                                  │
│                                                             │
│  Parent Concept: [math.class5.fractions      ▼]            │
│  Prerequisites:  [+ Add prerequisite___________]            │
│    ✓ math.class5.fractions.basics                          │
│    ✓ math.class5.fractions.comparison                      │
│                                                             │
│  🎯 Learning Objectives:                                    │
│  [+ Add learning outcome]                                   │
│    • Add fractions with same denominator                   │
│    • Simplify the result                                   │
│                                                             │
│  Difficulty Range: [1]──●────[4]                           │
│                                                             │
│  Tags: [fractions] [addition] [+ add tag]                  │
│                                                             │
│  [Cancel]                              [Create Concept →]  │
└─────────────────────────────────────────────────────────────┘
```

---

### Feature 2: Formula Builder (Custom Functions)

**What:** Content writers define reusable formulas that become available in templates

```typescript
interface CustomFormula {
  id: string;                    // Auto-generated UUID
  name: string;                  // "add_fractions"
  display_name: string;          // "Add Fractions"
  
  // Definition
  parameters: FormulaParam[];    // [{name: "n1", type: "integer"}, ...]
  return_type: string;           // "tuple" | "integer" | "boolean" | "list"
  
  // The actual code (sandboxed Python)
  code: string;                  // "return (n1*d2 + n2*d1, d1*d2)"
  
  // Documentation
  description: string;           // "Adds two fractions, returns (num, den)"
  example_usage: string;         // "add_fractions(1, 2, 1, 3) → (5, 6)"
  
  // Validation
  test_cases: TestCase[];        // [{input: [1,2,1,3], expected: [5,6]}]
  
  // Metadata
  category: string;              // "Fractions" | "Number Theory" | "Geometry"
  created_by: string;
  status: "DRAFT" | "ACTIVE";
}

interface FormulaParam {
  name: string;
  type: "integer" | "float" | "string" | "list" | "boolean";
  description: string;
  default_value?: any;
}
```

**UI:**
```
┌─────────────────────────────────────────────────────────────┐
│  🧮 Formula Builder                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Formula Name: [add_fractions________________]              │
│  Display Name: [Add Two Fractions____________]              │
│  Category:     [Fractions ▼]                               │
│                                                             │
│  📥 Parameters:                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Name     │ Type    │ Description                    │   │
│  ├──────────┼─────────┼────────────────────────────────┤   │
│  │ n1       │ integer │ Numerator of first fraction    │   │
│  │ d1       │ integer │ Denominator of first fraction  │   │
│  │ n2       │ integer │ Numerator of second fraction   │   │
│  │ d2       │ integer │ Denominator of second fraction │   │
│  └─────────────────────────────────────────────────────┘   │
│  [+ Add Parameter]                                          │
│                                                             │
│  📤 Return Type: [Tuple (num, den) ▼]                      │
│                                                             │
│  💻 Code (Python):                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ from math import gcd                                │   │
│  │                                                     │   │
│  │ def add_fractions(n1, d1, n2, d2):                 │   │
│  │     num = n1 * d2 + n2 * d1                        │   │
│  │     den = d1 * d2                                  │   │
│  │     g = gcd(num, den)                              │   │
│  │     return (num // g, den // g)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🧪 Test Cases:                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Input: (1, 2, 1, 3)  │ Expected: (5, 6)  │ ✅ Pass │   │
│  │ Input: (1, 4, 1, 4)  │ Expected: (1, 2)  │ ✅ Pass │   │
│  │ Input: (2, 3, 1, 6)  │ Expected: (5, 6)  │ ✅ Pass │   │
│  └─────────────────────────────────────────────────────┘   │
│  [+ Add Test Case]                                          │
│                                                             │
│  [Run Tests]  [Save as Draft]  [Publish Formula →]         │
└─────────────────────────────────────────────────────────────┘
```

---

### Feature 3: Enhanced Template Editor

**What:** Use concepts from graph + formulas from library to create templates

```
┌─────────────────────────────────────────────────────────────────────┐
│  ✨ Create Template                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 📍 CONCEPT (from graph)                                     │   │
│  │ ┌─────────────────────────────────────────────────────────┐ │   │
│  │ │ Search concepts... [fraction addition_______] 🔍        │ │   │
│  │ │                                                         │ │   │
│  │ │ 📂 Mathematics > Class 5 > Fractions                   │ │   │
│  │ │   ├─ ✓ Fraction Basics                                 │ │   │
│  │ │   ├─ ✓ Fraction Comparison                             │ │   │
│  │ │   └─ 📌 Fraction Addition  ← SELECTED                  │ │   │
│  │ │       └─ Fraction Subtraction                          │ │   │
│  │ └─────────────────────────────────────────────────────────┘ │   │
│  │                                                             │   │
│  │ [+ Create New Concept]  (opens Concept Manager)            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 📝 QUESTION                                                 │   │
│  │                                                             │   │
│  │ Question Pattern:                                           │   │
│  │ ┌─────────────────────────────────────────────────────────┐ │   │
│  │ │ What is {{n1}}/{{d1}} + {{n2}}/{{d2}}?                 │ │   │
│  │ └─────────────────────────────────────────────────────────┘ │   │
│  │                                                             │   │
│  │ Detected Variables: [n1] [d1] [n2] [d2]                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🔢 VARIABLES                                                │   │
│  │                                                             │   │
│  │ ┌─ Base Variables ─────────────────────────────────────┐   │   │
│  │ │                                                       │   │   │
│  │ │ n1: [Enum ▼] Values: [1, 2, 3, 5______]              │   │   │
│  │ │ d1: [Enum ▼] Values: [2, 3, 4, 6______]              │   │   │
│  │ │ n2: [Enum ▼] Values: [1, 2, 3, 5______]              │   │   │
│  │ │ d2: [Enum ▼] Values: [2, 3, 4, 6______]              │   │   │
│  │ │                                                       │   │   │
│  │ │ Constraint: [d1 == d2] (same denominator)            │   │   │
│  │ └───────────────────────────────────────────────────────┘   │   │
│  │                                                             │   │
│  │ ┌─ Computed Variables ─────────────────────────────────┐   │   │
│  │ │                                                       │   │   │
│  │ │ [+ Add Computed Variable]                            │   │   │
│  │ │                                                       │   │   │
│  │ │ ┌─────────────────────────────────────────────────┐  │   │   │
│  │ │ │ Name: [result_num_______]                       │  │   │   │
│  │ │ │                                                 │  │   │   │
│  │ │ │ Formula: [Use Formula ▼] OR [Write Custom ▼]   │  │   │   │
│  │ │ │                                                 │  │   │   │
│  │ │ │ ┌─ Available Formulas ───────────────────────┐ │  │   │   │
│  │ │ │ │ 🧮 add_fractions(n1, d1, n2, d2)[0]       │ │  │   │   │
│  │ │ │ │ 🧮 gcd(a, b)                              │ │  │   │   │
│  │ │ │ │ 🧮 lcm(a, b)                              │ │  │   │   │
│  │ │ │ │ 🧮 factors(n)                             │ │  │   │   │
│  │ │ │ │ [+ Create New Formula]                    │ │  │   │   │
│  │ │ │ └────────────────────────────────────────────┘ │  │   │   │
│  │ │ │                                                 │  │   │   │
│  │ │ │ OR write custom:                               │  │   │   │
│  │ │ │ ┌─────────────────────────────────────────┐   │  │   │   │
│  │ │ │ │ n1 + n2  (when d1 == d2)               │   │  │   │   │
│  │ │ │ └─────────────────────────────────────────┘   │  │   │   │
│  │ │ └─────────────────────────────────────────────────┘  │   │   │
│  │ │                                                       │   │   │
│  │ │ ┌─────────────────────────────────────────────────┐  │   │   │
│  │ │ │ Name: [result_den_______]                       │  │   │   │
│  │ │ │ Formula: [d1] (denominator stays same)          │  │   │   │
│  │ │ └─────────────────────────────────────────────────┘  │   │   │
│  │ └───────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🎯 OPTIONS                                                  │   │
│  │                                                             │   │
│  │ A. ✓ {{result_num}}/{{result_den}}  ← CORRECT              │   │
│  │ B.   {{n1 + n2}}/{{d1 + d2}}        ← Wrong: added dens    │   │
│  │ C.   {{n1 * n2}}/{{d1}}             ← Wrong: multiplied    │   │
│  │ D.   {{n1}}/{{d1 * d2}}             ← Wrong: random        │   │
│  │                                                             │   │
│  │ [+ Add Distractor with Misconception]                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ✅ SOLUTION                                                 │   │
│  │                                                             │   │
│  │ Step 1: Since denominators are same ({{d1}}), add numerators│   │
│  │ Step 2: {{n1}} + {{n2}} = {{result_num}}                   │   │
│  │ Step 3: Keep denominator: {{result_den}}                   │   │
│  │ Answer: {{result_num}}/{{result_den}}                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 👁️ LIVE PREVIEW                           [🔄 Regenerate] │   │
│  │                                                             │   │
│  │ Q: What is 1/4 + 2/4?                                      │   │
│  │                                                             │   │
│  │ A. ✓ 3/4                                                   │   │
│  │ B.   3/8                                                   │   │
│  │ C.   2/4                                                   │   │
│  │ D.   1/16                                                  │   │
│  │                                                             │   │
│  │ Variables: n1=1, d1=4, n2=2, d2=4, result_num=3, result_den=4│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  [Save Draft]  [Validate (10 generations)]  [Publish Template →]  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema Changes

### New Tables

```sql
-- Custom formulas created by content team
CREATE TABLE custom_formulas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,        -- "add_fractions"
    display_name VARCHAR(200) NOT NULL,       -- "Add Two Fractions"
    category VARCHAR(50) NOT NULL,            -- "Fractions"
    
    -- Definition
    parameters JSONB NOT NULL,                -- [{name, type, description}]
    return_type VARCHAR(50) NOT NULL,         -- "tuple"
    code TEXT NOT NULL,                       -- Python code
    
    -- Documentation
    description TEXT,
    example_usage TEXT,
    
    -- Validation
    test_cases JSONB,                         -- [{input, expected}]
    
    -- Metadata
    status VARCHAR(20) DEFAULT 'DRAFT',       -- DRAFT, ACTIVE, DEPRECATED
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Concepts in the knowledge graph (editable from UI)
CREATE TABLE concepts (
    id VARCHAR(255) PRIMARY KEY,              -- "math.class5.fractions.addition"
    name VARCHAR(200) NOT NULL,               -- "Fraction Addition"
    
    -- Graph Position
    parent_id VARCHAR(255) REFERENCES concepts(id),
    prerequisites JSONB DEFAULT '[]',         -- ["math.class5.fractions.basics"]
    
    -- Metadata
    subject VARCHAR(50) NOT NULL,
    grade INTEGER NOT NULL,
    chapter VARCHAR(100),
    
    -- Learning
    bloom_levels JSONB DEFAULT '[]',
    learning_outcomes JSONB DEFAULT '[]',
    difficulty_range JSONB DEFAULT '[1, 4]',
    
    -- Search
    tags JSONB DEFAULT '[]',
    
    -- Status
    status VARCHAR(20) DEFAULT 'DRAFT',
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Link templates to custom formulas used
CREATE TABLE template_formula_usage (
    template_id INTEGER REFERENCES question_templates(id),
    formula_id UUID REFERENCES custom_formulas(id),
    PRIMARY KEY (template_id, formula_id)
);
```

---

## 🔧 Backend API Changes

### New Endpoints

```python
# === FORMULA MANAGEMENT ===

@router.post("/api/admin/formulas")
async def create_formula(formula: FormulaCreate) -> Formula:
    """Create a new custom formula."""
    # 1. Validate Python code (syntax check)
    # 2. Run test cases in sandbox
    # 3. Save if all tests pass
    pass

@router.get("/api/admin/formulas")
async def list_formulas(category: str = None, status: str = "ACTIVE") -> List[Formula]:
    """List available formulas for template editor."""
    pass

@router.post("/api/admin/formulas/{id}/test")
async def test_formula(id: UUID, test_input: dict) -> dict:
    """Run a formula with given input (sandbox)."""
    pass

@router.post("/api/admin/formulas/{id}/publish")
async def publish_formula(id: UUID) -> Formula:
    """Publish a formula (makes it available in templates)."""
    # 1. Run all test cases
    # 2. Change status to ACTIVE
    # 3. Add to SAFE_FUNCTIONS dynamically
    pass


# === CONCEPT MANAGEMENT ===

@router.post("/api/admin/concepts")
async def create_concept(concept: ConceptCreate) -> Concept:
    """Add a new concept to the knowledge graph."""
    pass

@router.get("/api/admin/concepts/tree")
async def get_concept_tree(subject: str = None, grade: int = None) -> dict:
    """Get concept hierarchy for tree view."""
    pass

@router.put("/api/admin/concepts/{id}")
async def update_concept(id: str, concept: ConceptUpdate) -> Concept:
    """Update concept metadata."""
    pass


# === TEMPLATE WITH FORMULAS ===

@router.post("/api/admin/templates/preview")
async def preview_template(template: TemplatePreview) -> dict:
    """Preview template with custom formulas."""
    # 1. Load all referenced formulas
    # 2. Build safe_globals with formulas
    # 3. Generate question
    pass
```

---

## 🔒 Formula Sandbox Security

```python
# backend/domain/template_engine/formula_sandbox.py

class FormulaSandbox:
    """
    Secure execution environment for custom formulas.
    Only allows safe operations.
    """
    
    ALLOWED_IMPORTS = {'math', 'functools', 'itertools'}
    ALLOWED_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
        'float', 'int', 'len', 'list', 'map', 'max', 'min', 'pow',
        'range', 'round', 'set', 'sorted', 'str', 'sum', 'tuple', 'zip'
    }
    
    FORBIDDEN_PATTERNS = [
        '__import__', 'eval', 'exec', 'compile', 'open', 'file',
        'input', 'raw_input', '__builtins__', 'globals', 'locals',
        'getattr', 'setattr', 'delattr', 'hasattr',
        'os.', 'sys.', 'subprocess', 'socket', 'requests'
    ]
    
    def validate_code(self, code: str) -> tuple[bool, str]:
        """Check if code is safe to execute."""
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in code:
                return False, f"Forbidden pattern: {pattern}"
        return True, "OK"
    
    def execute(self, code: str, function_name: str, args: list) -> any:
        """Execute formula in sandbox with timeout."""
        # 1. Validate code
        # 2. Create restricted globals
        # 3. Execute with timeout (1 second max)
        # 4. Return result
        pass
    
    def run_test_cases(self, code: str, function_name: str, 
                       test_cases: list) -> list[dict]:
        """Run all test cases and return results."""
        results = []
        for test in test_cases:
            try:
                result = self.execute(code, function_name, test['input'])
                passed = result == test['expected']
                results.append({
                    'input': test['input'],
                    'expected': test['expected'],
                    'actual': result,
                    'passed': passed
                })
            except Exception as e:
                results.append({
                    'input': test['input'],
                    'error': str(e),
                    'passed': False
                })
        return results
```

---

## 📦 Dynamic Formula Loading

```python
# backend/domain/template_engine/lean_template_engine.py

class VariableGenerator:
    """Extended to support dynamic custom formulas."""
    
    @classmethod
    def _get_safe_functions(cls, template_id: int = None):
        """
        Get safe functions including custom formulas.
        If template_id provided, load formulas used by that template.
        """
        # Base safe functions (always available)
        safe = cls._get_base_safe_functions()
        
        # Load all ACTIVE custom formulas from database
        custom_formulas = db.query(CustomFormula).filter(
            CustomFormula.status == 'ACTIVE'
        ).all()
        
        sandbox = FormulaSandbox()
        for formula in custom_formulas:
            # Compile formula code and add to safe functions
            safe[formula.name] = sandbox.create_function(
                formula.code, 
                formula.name
            )
        
        return safe
```

---

## 🎨 Frontend Components

### New Components Needed

```
admin-ui/src/
├── pages/
│   ├── ConceptManager.tsx          # NEW: Add/edit concepts
│   ├── FormulaBuilder.tsx          # NEW: Create custom formulas
│   └── TemplateEditorV2.tsx        # UPGRADED: Full gateway
│
├── components/
│   ├── concept/
│   │   ├── ConceptTree.tsx         # Hierarchical concept view
│   │   ├── ConceptForm.tsx         # Add/edit concept form
│   │   └── ConceptSearch.tsx       # Search concepts
│   │
│   ├── formula/
│   │   ├── FormulaEditor.tsx       # Code editor with syntax highlight
│   │   ├── FormulaTestRunner.tsx   # Run test cases
│   │   ├── FormulaPicker.tsx       # Select formula for template
│   │   └── FormulaDocumentation.tsx
│   │
│   └── template/
│       ├── VariableBuilder.tsx     # Base + computed variables
│       ├── FormulaSelector.tsx     # Pick from library or write custom
│       └── LivePreview.tsx         # Real-time preview
```

---

## 🚀 Implementation Phases

### Phase 1: Formula Builder (1 week) ✅ COMPLETED
- [x] Database: `custom_formulas` table
- [x] Backend: Formula CRUD + sandbox execution
- [x] Frontend: `FormulaBuilder.tsx` with code editor
- [x] Frontend: `FormulaList.tsx` formula library browser
- [x] Integration: Formula picker in Template Editor
- [x] Testing: Formula test runner

### Phase 2: Universal Template Ingestor ✅ COMPLETED (18 Jan 2026)
- [x] Pydantic Schema: `universal_schema.py` with full validation
- [x] Backend Ingestor: `ingestor.py` with test generation
- [x] API Routes: 7 endpoints for template management  
- [x] File Import: JSON/YAML upload support
- [x] Validation: Schema, formula, and constraint validation

### Phase 3: Concept Manager (1 week)
- [ ] Database: `concepts` table (or extend existing)
- [ ] Backend: Concept CRUD + tree API
- [ ] Frontend: `ConceptManager.tsx` with tree view
- [ ] Link: Connect to template editor

### Phase 4: Enhanced Template Editor (1 week)
- [x] Integrate formula picker ✅ DONE
- [ ] Integrate concept selector
- [ ] Variable builder with formula support
- [ ] Live preview with custom formulas

### Phase 5: Polish & Security (3 days)
- [ ] Formula code review workflow
- [ ] Audit logging
- [ ] Performance optimization
- [ ] Documentation

---

## 📊 Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| Time to add new concept | 2+ hours (code change) | 5 minutes (UI) |
| Time to create formula | Developer required | Content team self-serve |
| Template creation time | 30 min | 10 min |
| Code deployments for content | Weekly | Zero |
| Content team independence | Low | High |

---

## 🔑 Key Principles

1. **Self-Service:** Content team never needs to touch codebase
2. **Safety First:** All custom code runs in sandbox
3. **Test-Driven:** Formulas must pass tests before publishing
4. **Discoverability:** Easy to find and reuse existing formulas
5. **Auditability:** Track who created what, when
6. **Reversibility:** Draft → Review → Published workflow

---

## Next Steps

1. **Approve this plan**
2. **Start with Formula Builder** (highest impact)
3. **Iterate based on content team feedback**

Would you like me to start implementing Phase 1 (Formula Builder)?
