# Admin Template End-to-End Flow

## Overview

This document traces the complete flow from admin UI template creation to student question delivery.

**Architecture**: All questions are generated from `QuestionTemplate` database entries. No legacy Python generators are used.

---

## 🔄 Complete End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ADMIN TEMPLATE FLOW                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  STEP 1: Admin Creates Template (Admin UI)                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  POST /api/admin/templates/ingest                                        │    │
│  │  {                                                                       │    │
│  │    "concept_id": "math.class5.factors_multiples.gcd",  ← Links to graph │    │
│  │    "question_pattern": "Find GCD of {{a}} and {{b}}",                   │    │
│  │    "variable_schema": { "a": {min:10, max:50}, "b": {...} },            │    │
│  │    "option_patterns": ["{{gcd_result}}", "{{a}}", "{{b}}", ...],        │    │
│  │    "solution_pattern": "Step 1: ...\nStep 2: ...",                      │    │
│  │    "diagram_type": "gcd",                                               │    │
│  │    "difficulty": 2,                                                     │    │
│  │    "bloom_level": "APPLY"                                               │    │
│  │  }                                                                       │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    ↓                                            │
│  STEP 2: Template Stored in Database                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  question_templates table                                                │    │
│  │  - id: 42                                                               │    │
│  │  - concept_id: "math.class5.factors_multiples.gcd"                      │    │
│  │  - status: "DRAFT" → "REVIEW" → "APPROVED" → "PUBLISHED"                │    │
│  │  - validation_passed: true                                              │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    ↓                                            │
│  STEP 3: Preview (Admin clicks "Preview")                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  POST /api/admin/templates/42/preview                                    │    │
│  │                                                                          │    │
│  │  LeanTemplateEngine.generate_question(42, allow_any_status=True)        │    │
│  │  1. Generate variables: {a: 24, b: 36, gcd_result: 12, ...}             │    │
│  │  2. Render question: "Find GCD of 24 and 36"                            │    │
│  │  3. Render options: ["12", "24", "36", "6"]                             │    │
│  │  4. Render solution: ["Step 1: List factors...", ...]                   │    │
│  │  5. Generate diagram: CDN URL for GCD visualization                     │    │
│  │  6. Return: {question, options, correct_index, variables, diagram_url}  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           STUDENT QUESTION FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  STEP 4: Student Starts Practice Session                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  POST /api/practice/start                                                │    │
│  │  { "chapter": "factors_multiples", "student_id": "stu_123" }            │    │
│  │                                                                          │    │
│  │  SessionAdapter.start_session()                                          │    │
│  │  → Creates QuizSession record                                            │    │
│  │  → Returns session_id                                                    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    ↓                                            │
│  STEP 5: Request Next Question (TEMPLATE-BASED)                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  GET /api/practice/session/{session_id}/next                             │    │
│  │                                                                          │    │
│  │  AdaptiveQuestionSelector.select_question(student_id)                   │    │
│  │  │                                                                       │    │
│  │  ├─ MasteryTracker: Check student's mastery state                       │    │
│  │  │   └─ "gcd concept: 60% accuracy, LEARNING level"                     │    │
│  │  │                                                                       │    │
│  │  ├─ ConceptGraph: Check prerequisites                                   │    │
│  │  │   └─ "gcd requires: factors, multiples (both MASTERED ✓)"           │    │
│  │  │                                                                       │    │
│  │  ├─ Sequencer: Choose optimal next target                               │    │
│  │  │   └─ Target: concept=gcd, difficulty=2, reason="reinforcement"      │    │
│  │  │                                                                       │    │
│  │  └─ _find_template_for_target(): Query database                         │    │
│  │      │                                                                   │    │
│  │      │  SELECT * FROM question_templates                                │    │
│  │      │  WHERE concept_id LIKE '%gcd'                                    │    │
│  │      │    AND status = 'PUBLISHED'                                      │    │
│  │      │    AND difficulty = 2                                            │    │
│  │      │  ORDER BY RANDOM() LIMIT 1                                       │    │
│  │      │                                                                   │    │
│  │      └─ LeanTemplateEngine.generate_question(template_id)               │    │
│  │          │                                                               │    │
│  │          ├─ VariableGenerator: {a: 18, b: 42, gcd_result: 6}           │    │
│  │          ├─ TemplateRenderer: "Find GCD of 18 and 42"                  │    │
│  │          ├─ CDN DiagramService: /static/diagrams/gcd_18_42.svg         │    │
│  │          └─ Returns unique question instance                            │    │
│  │                                                                          │    │
│  └─ Format for frontend and return                                         │    │
│                                                                              │    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Architecture: Template-Based (No Legacy)

The `AdaptiveQuestionSelector` is now fully template-based:

The `LeanTemplateEngine` already ensures variety through:

1. **Variable Generation**: Random within schema bounds
   ```python
   VariableGenerator.generate_from_schema(schema)
   # {a: 24, b: 36} → {a: 18, b: 42} → {a: 30, b: 45}
   ```

2. **Multiple Templates per Concept**: Selector picks randomly
   ```sql
   SELECT * FROM question_templates
   WHERE concept_id = 'math...gcd' AND status = 'PUBLISHED'
   ORDER BY RANDOM() LIMIT 1
   ```

3. **Deduplication (optional)**: Track served questions per session
   ```python
   # Avoid repeating same template in same session
   excluded_ids = session.get_served_template_ids()
   query = query.filter(~QuestionTemplate.id.in_(excluded_ids))
   ```

---

## ✅ Simplified Admin Flow (After Template Optimization)

With the 11-field simplified schema:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     SIMPLIFIED ADMIN TEMPLATE CREATION                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  📝 QUESTION                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  Concept: [math.class5.factors_multiples.gcd ▾]                         │    │
│  │  Difficulty: [2 ⚫⚫○○]                                                  │    │
│  │                                                                          │    │
│  │  Question: Find the GCD of {{a}} and {{b}}.                             │    │
│  │                                                                          │    │
│  │  Variables detected: a (10-50), b (10-50)  [Edit constraints]           │    │
│  │                                                                          │    │
│  │  Diagram: [GCD Visualization ▾]                                         │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  🎯 OPTIONS                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  ● A: {{gcd_result}}              ← CORRECT                             │    │
│  │  ○ B: {{a}}                       [💡 CONFUSES_WITH_FACTOR]             │    │
│  │  ○ C: {{b}}                       [💡 CONFUSES_WITH_MULTIPLE]           │    │
│  │  ○ D: {{a * b // gcd_result}}     [💡 USES_LCM_INSTEAD]                 │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ✅ SOLUTION                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  Step 1: Find factors of {{a}}: {{factors_a}}                           │    │
│  │  Step 2: Find factors of {{b}}: {{factors_b}}                           │    │
│  │  Step 3: Common factors: {{common_factors}}                             │    │
│  │  Step 4: Greatest common factor: {{gcd_result}}                         │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  [💾 Save]  [👁️ Preview]  [📤 Submit for Review]                              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Implementation Priority

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Fix `AdaptiveQuestionSelector` to use templates | Critical | 4h | P0 |
| Unify concept_id format (graph ↔ templates) | High | 2h | P0 |
| Simplify Admin UI (hide unused fields) | Medium | 2h | P1 |
| Auto-infer variables from patterns | Medium | 4h | P1 |
| Remove `template_code`, `answer_logic` from UI | Low | 1h | P2 |

---

## 📋 Testing Checklist

After implementation:

- [ ] Create new template in Admin UI
- [ ] Verify template saves to database with correct `concept_id`
- [ ] Preview shows different question each time (random variables)
- [ ] Publish template
- [ ] Start student practice session
- [ ] Verify student receives template-generated question
- [ ] Check solution steps render correctly after answer
- [ ] Check diagram renders (CDN URL working)
- [ ] Verify misconception feedback shows for wrong answers
