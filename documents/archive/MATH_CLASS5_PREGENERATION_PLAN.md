# Math Class 5 Pre-Generation + Caching Strategy with LLM

## Executive Summary

This plan outlines the complete strategy to transform Math Class 5 from **on-the-fly Python/SymPy generation** (currently active only for `factors_multiples`) to a **pre-generated + cached question bank** using LLM (Claude) for all 16 chapters.

---

## 1. Current State Analysis

### 1.1 Production Truth Status

| Component | Status | Notes |
|-----------|--------|-------|
| `factors_multiples.py` | ✅ ACTIVE | 11 concepts, pure Python/SymPy, ~2000 lines |
| Other 15 chapters | ❌ NOT IMPLEMENTED | Only config defined |
| `config/content/graphs/` | ✅ ACTIVE | ConceptGraph loads prerequisites |
| `config/content/taxonomy/` | ⚠️ DEFINED | 11 concepts for factors_multiples only |
| `config/content/blueprints/` | ⚠️ DEFINED | Coverage targets, NOT WIRED |
| `config/content/rubrics/` | ⚠️ DEFINED | Validation rules, NOT WIRED |
| Question Bank | ❌ DISABLED | Code exists but commented out |

### 1.2 CBSE Class 5 Math Chapters (16 Total)

| ID | Chapter Name | Strategy Key | Concepts | Complexity |
|----|--------------|--------------|----------|------------|
| 1 | The Fish Tale - Large Numbers | `large_numbers` | 5 | Medium |
| 2 | Shapes & Angles - Clock Angles | `clock_angles` | 4 | Medium |
| 3 | Shapes & Angles - Symmetry | `symmetry` | 4 | Low |
| 4 | Shapes & Angles - Rotation | `rotation` | 4 | Medium |
| 5 | How Many Squares - Fractions in Area | `fraction_area` | 4 | High |
| 6 | Parts & Wholes - Fractions & Decimals | `fractions_decimals` | 6 | High |
| 7 | Does it Look Same - Dice Logic | `dice_logic` | 4 | High (Visual) |
| 8 | Does it Look Same - Nets & Solids | `nets` | 4 | High (Visual) |
| 9 | Be My Multiple - Factors & Multiples | `factors_multiples` | 11 | Medium ✅ DONE |
| 10 | Can You See Pattern - Data Patterns | `data_patterns` | 5 | Medium |
| 11 | Mapping Your Way - Mapping | `mapping` | 5 | Medium (Visual) |
| 12 | Boxes & Sketches - Cube Counting | `cube_counting` | 4 | High (Visual) |
| 13 | Area & Measurement - Geometry | `geometry_measurement` | 5 | Medium |
| 14 | Smart Charts - Data Handling | `data_handling` | 5 | Low |
| 15 | Ways to Multiply/Divide | `multiplication_division` | 6 | Medium |
| 16 | How Big/Heavy - Measurement | `measurement` | 6 | Low |

**Total Concepts: ~82 across 16 chapters**

---

## 2. Pre-Generation Strategy

### 2.1 Content Volume Targets

For each concept, we need coverage across:
- **5 Difficulty Levels** (1-5)
- **5 Bloom's Levels** (Remember, Understand, Apply, Analyze, Evaluate)
- **Minimum Questions per Cell**: 8-10 (for variety without repetition)

**Formula:**
```
Questions per concept = 5 difficulties × 5 blooms × 8 variations = 200 questions
Total for Class 5 = 82 concepts × 200 = ~16,400 questions
```

However, not all Difficulty×Bloom combinations are valid (e.g., REMEMBER at difficulty 5 is rare).

**Realistic Matrix per Concept:**

| Bloom Level | D1 | D2 | D3 | D4 | D5 | Total |
|-------------|----|----|----|----|-----|-------|
| REMEMBER | 8 | 8 | - | - | - | 16 |
| UNDERSTAND | 8 | 10 | 10 | - | - | 28 |
| APPLY | - | 10 | 10 | 10 | - | 30 |
| ANALYZE | - | - | 10 | 10 | 10 | 30 |
| EVALUATE | - | - | - | 10 | 10 | 20 |
| **Total** | 16 | 28 | 30 | 30 | 20 | **124** |

**Revised Total: 82 concepts × 124 questions = ~10,168 questions**

### 2.2 Content Types per Question

Each question requires:
1. **Core Question** (text + options)
2. **Misconception Distractors** (4 options with why_wrong, teaching_point)
3. **Solution Steps** (3-5 steps)
4. **Rich Narrative** (story context)
5. **Visual Hints** (progressive hints)
6. **Rich HTML Content** (diagrams where needed)

### 2.3 Generation Tiers (Hybrid Approach)

| Tier | Content Type | Generation Method | Cost Factor |
|------|--------------|-------------------|-------------|
| **Tier 1: Core Math** | Numbers, answer, solution | Python/SymPy | $0 (compute only) |
| **Tier 2: Pedagogy** | Misconceptions, why_wrong, teaching_points | Claude Haiku | $0.25/1K tokens |
| **Tier 3: Engagement** | Story narratives, Indian context | Claude Haiku | $0.25/1K tokens |
| **Tier 4: Validation** | Quality check, edge cases | Claude Sonnet | $3/1K tokens |

---

## 3. YAML Configuration Strategy

### 3.1 Role of YAML Files in Pre-Generation

| YAML File | Purpose in Pre-Generation |
|-----------|---------------------------|
| `taxonomy/math.yaml` | **INPUT**: Concept IDs, Bloom levels, difficulty ranges |
| `blueprints/.../chapter.yaml` | **INPUT**: Coverage targets, session templates |
| `rubrics/question_quality.yaml` | **VALIDATION**: Auto-validate generated questions |
| `graphs/.../chapter.yaml` | **SEQUENCING**: Prerequisite ordering for batches |

### 3.2 New YAML Files Needed

```
config/content/
├── generation_rules/           # NEW: LLM prompting rules
│   ├── math_class5/
│   │   ├── factors_multiples.yaml
│   │   ├── large_numbers.yaml
│   │   ├── fractions_decimals.yaml
│   │   └── ... (16 files)
│   └── common/
│       ├── misconception_patterns.yaml
│       ├── indian_story_contexts.yaml
│       └── bloom_question_templates.yaml
├── validation/                 # NEW: Post-generation validation
│   ├── math_validators.yaml
│   └── edge_cases.yaml
└── banks/                      # OUTPUT: Generated question banks
    └── math/
        └── class5/
            ├── factors_multiples.yaml
            └── ... (16 files)
```

---

## 4. Implementation Phases

### Phase 1: Foundation Infrastructure (Week 1-2)

#### 4.1.1 Tasks
1. **Create Question Bank Schema** (`api/models/question_bank.py`)
   - Pydantic models for stored questions
   - Versioning support
   - Validation integration

2. **Create Bank Storage Layer** (`domain/content_generation/bank/`)
   - YAML/SQLite hybrid storage
   - Query interface (by concept, difficulty, bloom)
   - Caching layer (Redis optional)

3. **Create Generation Rules YAML** for `factors_multiples`
   - Template prompts for each concept
   - Misconception patterns
   - Story context library

4. **Wire Existing YAML Configs**
   - Connect `blueprints/` to generation
   - Connect `rubrics/` to validation

#### 4.1.2 Deliverables
- [ ] `QuestionBank` model with full schema
- [ ] `BankLoader` class (load from YAML)
- [ ] `BankGenerator` class (generate → validate → store)
- [ ] `generation_rules/factors_multiples.yaml`

### Phase 2: LLM Generation Pipeline (Week 3-4)

#### 4.2.1 Tasks
1. **Create LLM Client Wrapper** (`tools/llm_generator.py`)
   - Claude API integration
   - Rate limiting & retry logic
   - Cost tracking

2. **Create Generation Templates**
   - PromptCoT templates for each Bloom level
   - Misconception generation prompts
   - Story context injection

3. **Create Validation Pipeline**
   - Auto-validation against rubrics
   - Human review queue for failures
   - Statistics dashboard

4. **Generate `factors_multiples` Bank**
   - Full coverage (11 concepts × 124 = 1,364 questions)
   - Validate all questions
   - Export to YAML

#### 4.2.2 Deliverables
- [ ] Working LLM generation pipeline
- [ ] `factors_multiples` question bank (1,364 questions)
- [ ] Validation report
- [ ] Cost report

### Phase 3: Remaining Chapters (Week 5-8)

#### 4.3.1 Chapter Prioritization

**Priority 1: Pure Computation (Low Visual)**
- Ch 1: Large Numbers (~620 questions)
- Ch 15: Multiplication/Division (~744 questions)
- Ch 16: Measurement (~744 questions)
- Ch 10: Data Patterns (~620 questions)
- Ch 14: Data Handling (~620 questions)

**Priority 2: Mixed (Some Visual)**
- Ch 2: Clock Angles (~496 questions)
- Ch 3: Symmetry (~496 questions)
- Ch 4: Rotation (~496 questions)
- Ch 13: Geometry & Measurement (~620 questions)

**Priority 3: High Visual (Need SVG/Images)**
- Ch 5: Fraction Area (~496 questions)
- Ch 6: Fractions & Decimals (~744 questions)
- Ch 7: Dice Logic (~496 questions)
- Ch 8: Nets & Solids (~496 questions)
- Ch 11: Mapping (~620 questions)
- Ch 12: Cube Counting (~496 questions)

#### 4.3.2 Deliverables
- [ ] 15 chapter question banks
- [ ] Validation reports per chapter
- [ ] Total ~10,168 questions

### Phase 4: Integration & Testing (Week 9-10)

#### 4.4.1 Tasks
1. **Modify SessionAdapter** to use question bank
2. **Add fallback** to on-the-fly generation
3. **A/B testing** framework
4. **Performance benchmarks**

#### 4.4.2 Deliverables
- [ ] Production-ready question bank integration
- [ ] A/B test results
- [ ] Performance report

---

## 5. Cost Estimation

### 5.1 Token Estimates per Question

| Component | Input Tokens | Output Tokens | Total |
|-----------|--------------|---------------|-------|
| Core question | 500 | 300 | 800 |
| Misconceptions (4) | 400 | 400 | 800 |
| Solution steps | 200 | 300 | 500 |
| Story narrative | 300 | 400 | 700 |
| **Total per question** | 1,400 | 1,400 | **2,800** |

### 5.2 Cost Breakdown

| Model | Price/1M tokens | Cost per Question | Total (10,168 Q) |
|-------|-----------------|-------------------|------------------|
| Claude Haiku | $0.25 input, $1.25 output | $0.002 | **$20** |
| Claude Sonnet | $3 input, $15 output | $0.025 | **$254** |

### 5.3 Recommended Hybrid Approach

| Generation Task | Model | Questions | Cost |
|-----------------|-------|-----------|------|
| Tier 1 (Core Math) | Python/SymPy | 10,168 | $0 |
| Tier 2 (Misconceptions) | Claude Haiku | 10,168 | $15 |
| Tier 3 (Stories) | Claude Haiku | 10,168 | $10 |
| Tier 4 (Validation 10%) | Claude Sonnet | 1,017 | $25 |
| **Total** | - | 10,168 | **~$50** |

### 5.4 Buffer for Regeneration (20%)
- Failed validations: ~$10
- Edge case fixes: ~$5
- **Total with buffer: ~$65**

---

## 6. Technical Architecture

### 6.1 New Directory Structure

```
backend/
├── domain/
│   └── content_generation/
│       ├── generators/           # Existing
│       │   ├── factors_multiples.py  # Keep for fallback
│       │   └── ...
│       ├── bank/                 # NEW
│       │   ├── __init__.py
│       │   ├── loader.py         # Load from YAML/DB
│       │   ├── generator.py      # LLM-based generation
│       │   ├── validator.py      # Quality validation
│       │   └── storage.py        # Persistence layer
│       └── llm/                  # NEW
│           ├── __init__.py
│           ├── client.py         # Claude API wrapper
│           ├── prompts.py        # Prompt templates
│           └── cost_tracker.py   # Usage tracking
├── config/content/
│   ├── generation_rules/         # NEW
│   │   └── math_class5/
│   │       ├── factors_multiples.yaml
│   │       └── ... (16 files)
│   └── banks/                    # NEW (OUTPUT)
│       └── math/
│           └── class5/
│               └── factors_multiples.yaml
└── tools/
    ├── generate_bank.py          # NEW: CLI for generation
    └── validate_bank.py          # NEW: CLI for validation
```

### 6.2 Generation Rules YAML Schema

```yaml
# config/content/generation_rules/math_class5/factors_multiples.yaml
version: 1
chapter_id: factors_multiples
subject: math
grade: 5

# Concept-specific generation rules
concepts:
  factors:
    description: "Find all factors of a number"
    bloom_levels: [UNDERSTAND, APPLY]
    difficulty_range: [1, 3]
    
    # Number generation rules (for Python/SymPy)
    parameter_rules:
      easy:
        range: [6, 20]
        exclude: [primes]  # Avoid prime numbers for factors
      medium:
        range: [20, 50]
      hard:
        range: [50, 100]
    
    # Misconception patterns (for LLM)
    misconception_templates:
      - type: INCOMPLETE_REASONING
        pattern: "Missing 1 and/or the number itself"
        why_wrong_template: "Student forgot that {n} is always a factor of itself"
        teaching_template: "Every number n has at least 2 factors: 1 and n"
      
      - type: CONSTRAINT_VIOLATION
        pattern: "Including non-divisors"
        why_wrong_template: "Student included {wrong} which does not divide {n} evenly"
        teaching_template: "A factor must divide with NO remainder"
    
    # Story contexts (Indian context)
    story_contexts:
      - theme: "festival"
        template: "Diwali lights: Ravi has {n} diyas to arrange in equal rows..."
      - theme: "sports"
        template: "Cricket teams: The coach wants to divide {n} players..."
      - theme: "cooking"
        template: "Ladoos: Amma made {n} ladoos to pack in boxes..."

  gcd:
    description: "Find GCD of two numbers"
    bloom_levels: [APPLY, ANALYZE]
    difficulty_range: [2, 4]
    
    parameter_rules:
      easy:
        range_a: [10, 30]
        range_b: [10, 30]
        ensure_gcd_gt: 2  # Ensure GCD > 2 for easy
      medium:
        range_a: [20, 50]
        range_b: [20, 50]
      hard:
        range_a: [30, 100]
        range_b: [30, 100]
    
    misconception_templates:
      - type: FORMULA_CONFUSION
        pattern: "Confusing GCD with LCM"
        why_wrong_template: "Student computed LCM ({lcm}) instead of GCD ({gcd})"
        teaching_template: "GCD = Greatest Common DIVISOR (largest factor of both)"
      
      - type: FORMULA_MISAPPLICATION
        pattern: "Just multiplying the numbers"
        why_wrong_template: "Product ({product}) is not GCD"
        teaching_template: "GCD ≤ min(a, b); use prime factorization or Euclidean algorithm"
    
    story_contexts:
      - theme: "gardening"
        template: "Garden tiles: A garden is {a}m × {b}m. What's the largest square tile..."
      - theme: "gifts"
        template: "Gift boxes: Priya has {a} chocolates and {b} candies to pack..."

# Common story characters (reusable)
characters:
  - name: "Ravi"
    grade: 5
    interests: ["cricket", "puzzles"]
  - name: "Priya"
    grade: 5
    interests: ["dance", "cooking"]
  - name: "Arjun"
    grade: 5
    interests: ["science", "coding"]

# Indian festivals/contexts
contexts:
  festivals: ["Diwali", "Holi", "Pongal", "Onam", "Eid", "Christmas"]
  sports: ["cricket", "kabaddi", "kho-kho", "football"]
  food: ["ladoos", "samosas", "idlis", "rotis"]
```

### 6.3 Question Bank YAML Schema

```yaml
# data/banks/math/class5/factors_multiples.yaml
version: 1
generated_at: "2026-01-10T10:00:00Z"
generator_version: "1.0.0"
chapter_id: factors_multiples
subject: math
grade: 5
total_questions: 1364

# Statistics
stats:
  by_concept:
    factors: 124
    multiples: 124
    gcd: 124
    lcm: 124
    divisibility: 124
    prime_composite: 124
    factor_pairs: 124
    prime_factorization: 124
    word_problem: 124
    error_analysis: 124
    assertion_reason: 124
  by_difficulty:
    1: 218
    2: 382
    3: 382
    4: 273
    5: 109
  by_bloom:
    REMEMBER: 218
    UNDERSTAND: 382
    APPLY: 382
    ANALYZE: 273
    EVALUATE: 109

# Questions array
questions:
  - id: "fm_factors_d1_b2_001"
    concept_key: "factors"
    concept_id: "math.class5.factors_multiples.factors"
    difficulty: 1
    bloom_level: "UNDERSTAND"
    
    # Core content
    question_text: "Find all the factors of 12."
    options:
      - "[1, 2, 3, 4, 6, 12]"
      - "[2, 3, 4, 6]"
      - "[1, 12]"
      - "[1, 2, 4, 6, 12]"
    correct_option_index: 0
    answer: "[1, 2, 3, 4, 6, 12]"
    
    # Solution
    solution_steps:
      - "Test each number from 1 to 12"
      - "1 × 12 = 12 ✓ → 1 and 12 are factors"
      - "2 × 6 = 12 ✓ → 2 and 6 are factors"
      - "3 × 4 = 12 ✓ → 3 and 4 are factors"
      - "Factors of 12: [1, 2, 3, 4, 6, 12]"
    
    # Misconception info
    misconception_info:
      - option_index: 0
        is_correct: true
        value: "[1, 2, 3, 4, 6, 12]"
        misconception_type: null
        why_wrong: null
        teaching_point: "Correct! You found all 6 factors."
      - option_index: 1
        is_correct: false
        value: "[2, 3, 4, 6]"
        misconception_type: "INCOMPLETE_REASONING"
        why_wrong: "Missing 1 and 12. Student forgot that 1 divides every number and 12 divides itself."
        teaching_point: "1 is always a factor (1 × n = n), and n is always a factor of itself (n ÷ n = 1)"
      - option_index: 2
        is_correct: false
        value: "[1, 12]"
        misconception_type: "INCOMPLETE_REASONING"
        why_wrong: "Only listed boundary factors. Student didn't check numbers between 1 and 12."
        teaching_point: "Test ALL numbers from 1 to n. Record those that divide evenly."
      - option_index: 3
        is_correct: false
        value: "[1, 2, 4, 6, 12]"
        misconception_type: "ARITHMETIC_ERROR"
        why_wrong: "Missing 3. Student may have skipped odd numbers or made a division error."
        teaching_point: "12 ÷ 3 = 4 with no remainder. Don't skip any number in your check!"
    
    # Rich content
    rich_narrative: "Ravi is arranging 12 diyas for Diwali. He wants to place them in equal rows. The number of diyas per row must be a factor of 12."
    visual_hints:
      - "Start with 1: Does 1 divide 12? Yes! (1 × 12 = 12)"
      - "Try 2: Does 2 divide 12? Yes! (2 × 6 = 12)"
      - "Try 3: Does 3 divide 12? Yes! (3 × 4 = 12)"
      - "Try 4: Does 4 divide 12? Yes! (already found: 4 × 3)"
      - "All factors: 1, 2, 3, 4, 6, 12"
    rich_html_content: "<div class='factor-diagram'>...</div>"
    
    # Meta
    meta:
      subject: "math"
      grade: 5
      chapter: "factors_multiples"
      chapter_id: "factors_multiples"
      concept_id: "math.class5.factors_multiples.factors"
      concept_key: "factors"
      difficulty: 1
      bloom_level: "UNDERSTAND"
    
    # Generation metadata
    generation_meta:
      generated_by: "hybrid_pipeline_v1"
      math_engine: "sympy"
      llm_model: "claude-3-haiku"
      validated: true
      validation_score: 0.95
```

---

## 7. LLM Prompt Templates

### 7.1 PromptCoT for Misconception Generation

```python
MISCONCEPTION_PROMPT = """
You are an expert math teacher creating diagnostic MCQ options for CBSE Class 5 students.

TASK: Generate 3 wrong options (distractors) for this math question, each targeting a specific misconception.

QUESTION: {question_text}
CORRECT ANSWER: {correct_answer}
CONCEPT: {concept_key}

For each distractor, provide:
1. The wrong answer value
2. The misconception type (from: INCOMPLETE_REASONING, ARITHMETIC_ERROR, FORMULA_CONFUSION, CONSTRAINT_VIOLATION, OPPOSITE_CONFUSION)
3. why_wrong: A specific explanation of what error the student made
4. teaching_point: A brief, encouraging correction (max 2 sentences)

IMPORTANT RULES:
- Each distractor must be a PLAUSIBLE wrong answer (not random)
- Target COMMON student mistakes, not obscure errors
- Distractors should be diverse (different misconception types)
- Values must be mathematically distinct from each other and the correct answer
- Use Indian context/names where appropriate

OUTPUT FORMAT (JSON):
{{
  "distractors": [
    {{
      "value": "...",
      "misconception_type": "...",
      "why_wrong": "...",
      "teaching_point": "..."
    }},
    ...
  ]
}}
"""
```

### 7.2 PromptCoT for Story Narrative

```python
STORY_NARRATIVE_PROMPT = """
You are creating an engaging story context for a math problem for Indian Class 5 students.

MATH PROBLEM: {question_text}
ANSWER: {correct_answer}
CONCEPT: {concept_key}
THEME: {story_theme}

Create a SHORT story narrative (2-3 sentences) that:
1. Features an Indian character ({character_name})
2. Uses the {story_theme} context
3. Naturally incorporates the math problem
4. Is relatable to a 10-year-old Indian student

AVOID:
- Making the story longer than necessary
- Using complex vocabulary
- Stereotypes or culturally insensitive content

OUTPUT: Just the narrative text (no JSON).
"""
```

---

## 8. Validation Pipeline

### 8.1 Automated Checks (from rubrics/question_quality.yaml)

```python
VALIDATION_CHECKS = [
    # Structure
    ("options_count", lambda q: len(q.options) == 4),
    ("options_unique", lambda q: len(set(q.options)) == 4),
    ("correct_in_range", lambda q: 0 <= q.correct_option_index < 4),
    
    # Misconception coverage
    ("misconception_coverage", lambda q: len(q.misconception_info) == 4),
    ("one_correct", lambda q: sum(1 for m in q.misconception_info if m.is_correct) == 1),
    
    # Content quality
    ("question_length", lambda q: 10 <= len(q.question_text) <= 1000),
    ("solution_steps", lambda q: len(q.solution_steps) >= 2),
    
    # Mathematical correctness
    ("answer_matches", lambda q: q.answer in q.options[q.correct_option_index]),
]
```

### 8.2 LLM-Assisted Validation (10% sample)

```python
VALIDATION_PROMPT = """
Review this math question for Class 5 students:

QUESTION: {question_text}
OPTIONS: {options}
MARKED CORRECT: {correct_answer}
SOLUTION: {solution_steps}

Check for:
1. Mathematical correctness (is the answer actually correct?)
2. Age-appropriateness (is this suitable for Class 5?)
3. Option quality (are distractors plausible but clearly wrong?)
4. Clarity (is the question unambiguous?)

OUTPUT (JSON):
{{
  "is_valid": true/false,
  "issues": ["..."],
  "suggestions": ["..."],
  "confidence": 0.0-1.0
}}
"""
```

---

## 9. CLI Tools

### 9.1 Generation CLI

```bash
# Generate full chapter bank
python -m tools.generate_bank \
  --chapter factors_multiples \
  --grade 5 \
  --output data/banks/math/class5/factors_multiples.yaml \
  --validate \
  --cost-limit 10.00

# Generate specific concept
python -m tools.generate_bank \
  --chapter factors_multiples \
  --concept gcd \
  --count 50 \
  --dry-run  # Preview cost without generating

# Generate all Class 5 chapters
python -m tools.generate_bank \
  --all-chapters \
  --grade 5 \
  --parallel 4 \
  --resume  # Resume from last checkpoint
```

### 9.2 Validation CLI

```bash
# Validate existing bank
python -m tools.validate_bank \
  --input data/banks/math/class5/factors_multiples.yaml \
  --rubric config/content/rubrics/question_quality.yaml \
  --report validation_report.json

# Fix failed validations
python -m tools.validate_bank \
  --input data/banks/math/class5/factors_multiples.yaml \
  --fix \
  --llm-assist  # Use LLM to regenerate failures
```

---

## 10. Success Metrics

### 10.1 Generation Metrics
- [ ] 10,168 questions generated
- [ ] 95%+ pass automated validation
- [ ] 90%+ pass LLM validation (sample)
- [ ] Cost within $65 budget

### 10.2 Quality Metrics
- [ ] Zero duplicate questions
- [ ] Each concept has full Bloom×Difficulty coverage
- [ ] All misconception types represented
- [ ] Indian context in 80%+ story narratives

### 10.3 Integration Metrics
- [ ] Bank loading < 100ms
- [ ] Question retrieval < 10ms
- [ ] Fallback to on-the-fly < 1% of requests
- [ ] A/B test shows equal/better learning outcomes

---

## 11. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM generates incorrect math | Tier 1 uses Python/SymPy for all calculations |
| High API costs | Haiku for bulk, Sonnet only for validation |
| Validation failures | Human review queue + regeneration pipeline |
| Bank corruption | Version control + checksums |
| Production disruption | Gradual rollout with feature flags |

---

## 12. Timeline Summary

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1-2 | Foundation | Infrastructure + factors_multiples rules |
| 3-4 | Generation Pipeline | LLM integration + factors_multiples bank |
| 5-6 | Priority 1 Chapters | 5 pure computation chapters |
| 7-8 | Priority 2-3 Chapters | Remaining 10 chapters |
| 9-10 | Integration | Production rollout + A/B testing |

**Total Duration: 10 weeks**
**Total Cost: ~$65 (LLM) + Engineering Time**

---

## 13. Next Steps (Immediate Actions)

1. **Create `generation_rules/factors_multiples.yaml`** - Define concept-specific rules
2. **Create `bank/loader.py`** - Basic YAML loading
3. **Create `llm/client.py`** - Claude API wrapper with cost tracking
4. **Generate 100 test questions** for `factors_multiples.factors` concept
5. **Validate against rubrics** - Tune prompts based on failures

Would you like me to start implementing Phase 1?
