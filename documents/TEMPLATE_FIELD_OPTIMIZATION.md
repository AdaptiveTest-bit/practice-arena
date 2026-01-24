# Template Field Optimization Strategy

## Executive Summary

Current system has **22 fields** per template. This document identifies the **11 essential fields** that maximize student learning while minimizing content writer overhead.

---

## 🎯 Decision Matrix

| Field | Student Impact | Writer Effort | Keep? | Reason |
|-------|---------------|---------------|-------|--------|
| `concept_id` | 🔴 Critical | Low | ✅ **YES** | Adaptive learning requires concept mapping |
| `question_pattern` | 🔴 Critical | Low | ✅ **YES** | Core question text |
| `variable_schema` | 🟡 Medium | High | ⚠️ **SIMPLIFY** | Auto-infer from question_pattern |
| `template_code` | 🟢 None | Very High | ❌ **REMOVE** | Replaced by variable_schema |
| `answer_logic` | 🟢 None | Medium | ❌ **REMOVE** | Inline in correct option |
| `option_patterns[]` | 🔴 Critical | Low | ✅ **YES** | Multiple choice options |
| `difficulty` | 🟡 Medium | Low | ✅ **YES** | Pacing/scaffolding |
| `bloom_level` | 🟢 Low | Medium | ❌ **REMOVE** | Rarely used in practice UI |
| `estimated_time` | 🟢 Low | Low | ❌ **REMOVE** | Not shown to students, defaults work |
| `solution_pattern` | 🔴 Critical | Medium | ✅ **YES** | Learning from mistakes |
| `hint_pattern` | 🟡 Medium | Medium | ⚠️ **OPTIONAL** | Auto-generate fallback |
| `narrative_pattern` | 🟢 Low | Medium | ❌ **REMOVE** | Over-engineering, rarely adds value |
| `diagram_config` | 🟡 Medium | Low | ✅ **YES** | Visual learning |
| `misconceptions[]` | 🔴 Critical | Low | ✅ **YES** | Targeted remediation |

---

## 📋 Streamlined Template Schema (11 Fields)

### KEEP (Essential)

```python
class QuestionTemplate:
    # === Core Identity (2 fields) ===
    id: int                      # Auto
    concept_id: str              # Required - links to curriculum
    
    # === Question Definition (4 fields) ===
    question_pattern: str        # Required - "Find the GCD of {{a}} and {{b}}"
    options: List[OptionDef]     # Required - 4 options with correct marked
    difficulty: int              # Required - 1-4 scale
    diagram_type: str | None     # Optional - "gcd", "factors", etc.
    
    # === Learning Support (2 fields) ===
    solution_pattern: str        # Required - step-by-step solution
    misconceptions: List[...]    # Optional - links wrong options to misconceptions
    
    # === Workflow (3 fields) ===
    status: str                  # Auto-managed
    created_at: datetime         # Auto
    updated_at: datetime         # Auto
```

### REMOVE (Low Value / High Friction)

| Field | Why Remove |
|-------|------------|
| `template_code` | Python code is error-prone for content writers. Variable generation should be automatic from `question_pattern` analysis. |
| `answer_logic` | Redundant—correct answer is already marked in `options`. |
| `bloom_level` | Academic taxonomy rarely affects student UX. If needed, auto-infer from question type. |
| `estimated_time` | Default 60s works. Students don't see this. |
| `narrative_pattern` | Over-engineering. Most questions don't need story context. |
| `hint_pattern` | **Make optional with auto-fallback**: Generate from solution_pattern if not provided. |
| `variable_schema` | **Auto-infer**: Parse `{{a}}`, `{{b}}` from patterns. Only expose if writer needs constraints. |

---

## 🖥️ Simplified Admin UI

### Before: 6 Tabs, 22 Fields
```
[Basic] [Content] [Quality] [Options] [Diagrams] [Misconceptions]
```

### After: 3 Sections, 11 Fields
```
┌─────────────────────────────────────────────────────────────┐
│  📝 QUESTION                                                │
├─────────────────────────────────────────────────────────────┤
│  Concept: [dropdown with search] ───────────────────────    │
│  Difficulty: [1] [2] [3] [4]                                │
│                                                             │
│  Question:                                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Find the GCD of {{a}} and {{b}}.                      │ │
│  └───────────────────────────────────────────────────────┘ │
│  Variables detected: a (integer), b (integer)              │
│                                                             │
│  Diagram: [None ▾] [Factors] [GCD] [LCM] ...               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  🎯 OPTIONS                                                 │
├─────────────────────────────────────────────────────────────┤
│  ○ A: {{gcd_result}}              ← [Mark Correct]         │
│  ○ B: {{a}}                       [💡 Misconception: ...]  │
│  ○ C: {{b}}                       [💡 Misconception: ...]  │
│  ○ D: {{a * b}}                   [💡 Misconception: ...]  │
│                                                             │
│  [+ Add Option]                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ✅ SOLUTION (shown after student answers)                  │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Find factors of {{a}}: {{factors_a}}              │
│  Step 2: Find factors of {{b}}: {{factors_b}}              │
│  Step 3: Common factors: {{common}}                         │
│  Step 4: GCD = {{gcd_result}}                              │
│                                                             │
│  [+ Add Step]                                               │
└─────────────────────────────────────────────────────────────┘

[💾 Save Draft]  [👁️ Preview]  [📤 Submit for Review]
```

---

## 🔄 Migration Path

### Phase 1: Hide Fields (No Schema Change)
- Keep all DB columns
- Hide in UI: `template_code`, `answer_logic`, `bloom_level`, `estimated_time`, `narrative_pattern`
- Make `hint_pattern` collapsible (advanced section)

### Phase 2: Auto-Generation
- Auto-infer `variable_schema` from `{{...}}` patterns
- Auto-generate hints from solution_pattern if empty
- Default difficulty=2, estimated_time=60

### Phase 3: Variable Generation (Backend)
- Parse question_pattern to extract variable names
- Apply smart defaults:
  - `{{a}}`, `{{b}}`, `{{n}}` → integers 10-99
  - `{{number}}` → integer 2-100
  - `{{factors}}` → compute from number
  - `{{gcd_result}}` → compute from a, b

---

## 📊 Impact Analysis

### For Students
| Metric | Before | After |
|--------|--------|-------|
| Solution quality | ✅ Same | ✅ Same |
| Visual diagrams | ✅ Same | ✅ Same |
| Misconception feedback | ✅ Same | ✅ Same |
| Hint availability | ✅ Manual | ✅ Auto-fallback |

### For Content Writers
| Metric | Before | After |
|--------|--------|-------|
| Fields to fill | 22 | 8-11 |
| Need Python skills | Yes | No |
| Time per template | ~15 min | ~5 min |
| Error rate | High | Low |

---

## ✅ Recommended Simplified Schema

```python
class QuestionTemplateSimplified(Base):
    """Lean template - focused on what matters."""
    __tablename__ = "question_templates"
    
    # Identity
    id = Column(Integer, primary_key=True)
    concept_id = Column(String(255), nullable=False, index=True)
    
    # Question content
    question_pattern = Column(Text, nullable=False)
    option_patterns = Column(JSON, nullable=False)  # [{text, is_correct, misconception_id?}]
    difficulty = Column(Integer, nullable=False, default=2)
    
    # Visual support
    diagram_type = Column(String(50))  # Simplified from diagram_config
    
    # Learning support
    solution_pattern = Column(Text, nullable=False)  # Required!
    hint_pattern = Column(Text)  # Optional - auto-generate if empty
    
    # Workflow
    status = Column(String(20), default="DRAFT")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    misconception_links = relationship("TemplateOptionMisconception", ...)
    
    # Auto-computed (not stored)
    @property
    def variables(self) -> List[str]:
        """Extract {{var}} from patterns."""
        import re
        all_text = f"{self.question_pattern} {self.solution_pattern}"
        return list(set(re.findall(r'\{\{(\w+)\}\}', all_text)))
```

---

## 🚀 Implementation Status

### ✅ COMPLETED

1. **Simplified Template Editor UI** (`TemplateEditorSimplified.tsx`)
   - 3 sections: Question, Options, Solution
   - 11 fields instead of 22
   - Auto-detects variables from `{{...}}` patterns
   - No Python code required
   - Computed variables auto-generated from known patterns

2. **Enhanced VariableGenerator** (`lean_template_engine.py`)
   - Supports `computed` section in variable_schema
   - Safe formula library: `gcd`, `lcm`, `factors`, `multiples`, `is_prime`, etc.
   - Auto-computes derived variables before template rendering

3. **Navigation Updated** (`Layout.tsx`, `App.tsx`)
   - "✨ Create Template" → Simplified editor (content writers)
   - "Advanced Editor" → Full editor (developers)

### 🔄 IN PROGRESS

- Migrate existing 11 broken templates to use computed variables
- Add test-generation to validation endpoint

### 📋 TODO

- Dropdown for common formulas in UI
- Template library with working examples

---

## Summary

**Before**: 22 fields, Python code, complex UI → Content writers frustrated
**After**: 11 fields, no code, simple UI → 3x faster content creation

**Student experience**: Unchanged (same quality output)
**Scaling**: Much easier (non-technical content writers can author)
