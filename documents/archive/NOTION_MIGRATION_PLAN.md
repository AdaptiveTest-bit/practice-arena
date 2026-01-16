# Notion CMS + Hybrid System Migration Plan

## Overview
Migrate `factors_multiples` chapter from on-the-fly generation (2015-line monolith) to Notion CMS + template-based hybrid system.

## Current State Analysis

### Existing Generator (`factors_multiples.py`)
- **Lines**: 2015
- **Concepts**: 11 (divisibility, prime_composite, factors, multiples, factor_pairs, gcd, lcm, prime_factorization, word_problem, assertion_reason, error_analysis)
- **Pattern**: Each concept has a dedicated generator method (`_generate_*_integrated`)

### Current Generation Pattern (Extracted from Code)
Each generator follows this structure:
1. Pick random numbers based on difficulty
2. Compute correct answer (using math/sympy)
3. Generate misconception-based distractors
4. Create `Question` object with full meta

### Key Data to Extract for Templates

| Concept | Number Ranges | Answer Formula | Distractor Patterns | Bloom Level |
|---------|---------------|----------------|---------------------|-------------|
| divisibility | 100-999, divisors [2,3,5,9,10] | `n % d == 0` | Opposite, "Cannot determine", "Partially" | REMEMBER |
| prime_composite | Primes [2-47], Composites [4-28] | `len(factors) == 2` | Opposite, "Neither", "Cannot determine" | REMEMBER |
| factors | 6-100 | `[i for i in 1..n if n%i==0]` | Missing 1/n, only 1&n, random subset | UNDERSTAND |
| multiples | base 2-15, count 5-7 | `[b*i for i in 1..count]` | Includes 0, skips 1×, off-by-one | UNDERSTAND |
| factor_pairs | 12-72 | `[(i,n//i) for i in 1..√n if n%i==0]` | Missing pairs, duplicates, wrong pairs | UNDERSTAND |
| gcd | 10-50 × 2 numbers | `math.gcd(a,b)` | Product, min, sum | APPLY |
| lcm | 4-20 × 2 numbers | `a*b//gcd(a,b)` | Product, GCD, max, sum | APPLY |
| prime_factorization | 12-120 | `sympy.factorint(n)` | Incomplete, composite factors | APPLY |
| word_problem | Varies by subtype | GCD/LCM/factors | Wrong operation | APPLY |
| assertion_reason | Varies | Both correct + explains | Wrong relationship | ANALYZE |
| error_analysis | 3 students | Identify correct one | Wrong student | EVALUATE |

---

## Target Architecture

### 1. Notion Database Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    NOTION WORKSPACE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📁 Question Templates (Database)                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ concept_id        │ difficulty │ story_templates │ ... │ │
│  │ factors           │ 1          │ [...json...]    │     │ │
│  │ factors           │ 2          │ [...json...]    │     │ │
│  │ gcd               │ 2          │ [...json...]    │     │ │
│  │ lcm               │ 3          │ [...json...]    │     │ │
│  │ word_problem_lcm  │ 3          │ [...json...]    │     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  📁 Number Ranges (Database)                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ concept_id │ diff │ param_name │ min │ max │ choices   │ │
│  │ factors    │ 1    │ target     │ 6   │ 20  │ null      │ │
│  │ factors    │ 2    │ target     │ 24  │ 48  │ null      │ │
│  │ gcd        │ 2    │ num1       │ 10  │ 30  │ null      │ │
│  │ divisor    │ any  │ divisor    │ -   │ -   │ [2,3,5,9] │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  📁 Distractor Formulas (Database)                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ concept_id │ name              │ formula         │ ...  │ │
│  │ factors    │ missing_1_and_n   │ factors[1:-1]   │      │ │
│  │ factors    │ only_boundaries   │ [1, n]          │      │ │
│  │ gcd        │ product_confusion │ a * b           │      │ │
│  │ lcm        │ gcd_confusion     │ gcd(a, b)       │      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  📁 Story Templates (Database)                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ concept_id │ template                              │    │ │
│  │ gcd        │ "A teacher has {a} pencils and..."    │    │ │
│  │ lcm        │ "Bus A comes every {a} minutes..."    │    │ │
│  │ factors    │ "Arrange {n} students in rows..."     │    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Backend Services Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      NEW BACKEND ARCHITECTURE                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                  │
│  │  Notion CMS     │    │   Redis Cache   │                  │
│  │  (Source)       │───▶│   (Runtime)     │                  │
│  └─────────────────┘    └────────┬────────┘                  │
│                                  │                           │
│         Sync Every 5min          │  <10ms access             │
│                                  │                           │
│  ┌───────────────────────────────▼───────────────────────┐   │
│  │               NotionSyncService                        │   │
│  │  • Polls Notion API for changes                       │   │
│  │  • Updates Redis cache                                │   │
│  │  • Validates template integrity                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │               QuestionEngine                           │   │
│  │  • Reads templates from Redis                         │   │
│  │  • Picks random numbers within ranges                 │   │
│  │  • Computes correct answer using formula              │   │
│  │  • Generates distractors using formulas               │   │
│  │  • Returns Question object                            │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │               QuestionOrchestrator                     │   │
│  │  • Reads YAML configs (blueprints, graphs)            │   │
│  │  • Routes requests based on concept/difficulty        │   │
│  │  • Manages session templates                          │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Create New Services (Day 1-2)

#### 1.1 Create Template Models
```python
# backend/domain/content_generation/templates/models.py
@dataclass
class QuestionTemplate:
    concept_id: str
    difficulty: int
    story_template: str        # "Find GCD of {a} and {b}"
    answer_formula: str        # "gcd(a, b)"
    params: Dict[str, ParamRange]
    distractors: List[DistractorFormula]
    solution_steps_template: List[str]
    bloom_level: BloomLevel
    misconception_types: List[MisconceptionType]
```

#### 1.2 Create NotionSyncService
```python
# backend/domain/content_generation/services/notion_sync.py
class NotionSyncService:
    def __init__(self, notion_token: str, redis_client):
        self.notion = NotionClient(notion_token)
        self.redis = redis_client
        
    async def sync_all(self):
        """Pull all templates from Notion, update Redis"""
        
    async def sync_concept(self, concept_id: str):
        """Sync single concept's templates"""
```

#### 1.3 Create QuestionEngine
```python
# backend/domain/content_generation/engines/template_engine.py
class TemplateQuestionEngine:
    def __init__(self, redis_client):
        self.redis = redis_client
        
    def generate(self, concept_id: str, difficulty: int) -> Question:
        # 1. Get template from Redis
        template = self._get_template(concept_id, difficulty)
        
        # 2. Pick random numbers
        params = self._generate_params(template.params)
        
        # 3. Compute answer
        answer = self._evaluate_formula(template.answer_formula, params)
        
        # 4. Generate distractors
        options = self._generate_options(template.distractors, params, answer)
        
        # 5. Build Question
        return self._build_question(template, params, answer, options)
```

### Phase 2: Extract Templates from Monolith (Day 2-3)

For each concept, extract:

#### 2.1 Factors Concept
```yaml
# notion_export/factors.yaml
concept_id: math.class5.factors_multiples.factors
templates:
  - difficulty: 1
    story: "Find all factors of {target_number}."
    answer_formula: "sorted([i for i in range(1, target_number + 1) if target_number % i == 0])"
    params:
      target_number:
        type: choice
        choices: [6, 8, 10, 12, 15, 18, 20]
    distractors:
      - name: missing_boundaries
        formula: "[f for f in factors if f not in [1, target_number]]"
        misconception: INCOMPLETE_REASONING
        why_wrong: "Forgot to include 1 and the number itself"
      - name: only_boundaries
        formula: "[1, target_number]"
        misconception: INCOMPLETE_REASONING
        why_wrong: "Only listed 1 and the number"
    solution_steps:
      - "Test each number from 1 to {target_number}"
      - "If {target_number} ÷ n has no remainder, n is a factor"
      - "Factors: {factors}"
```

#### 2.2 GCD Concept
```yaml
concept_id: math.class5.factors_multiples.gcd
templates:
  - difficulty: 2
    story: "What is the GCD of {a} and {b}?"
    answer_formula: "math.gcd(a, b)"
    params:
      a: {type: range, min: 10, max: 50}
      b: {type: range, min: 10, max: 50}
    distractors:
      - name: product_confusion
        formula: "a * b"
        misconception: FORMULA_CONFUSION
      - name: min_number
        formula: "min(a, b)"
        misconception: INCOMPLETE_REASONING
      - name: sum_confusion
        formula: "a + b"
        misconception: CONSTRAINT_VIOLATION
```

### Phase 3: Create Notion Databases (Day 3-4)

1. **Question Templates Database**
   - Properties: concept_id, difficulty, story_template, answer_formula, params (JSON), solution_steps (JSON)
   
2. **Number Ranges Database**
   - Properties: concept_id, difficulty, param_name, range_type, min, max, choices
   
3. **Distractor Formulas Database**
   - Properties: concept_id, distractor_name, formula, misconception_type, why_wrong, teaching_point

4. **Populate from Extracted Templates**

### Phase 4: Wire Up and Test (Day 4-5)

1. Deploy NotionSyncService
2. Initial full sync to Redis
3. Test each concept generates correctly
4. Compare output with monolith generator
5. A/B test with small user group

### Phase 5: Cutover (Day 5-6)

1. Update QuestionOrchestrator to use TemplateQuestionEngine
2. Keep monolith as fallback
3. Gradual rollout: 10% → 50% → 100%
4. Monitor for errors

---

## Notion Database Schema (Detailed)

### Database 1: Question Templates

| Property | Type | Description |
|----------|------|-------------|
| concept_id | Select | `factors`, `gcd`, `lcm`, etc. |
| difficulty | Number | 1-4 |
| bloom_level | Select | REMEMBER, UNDERSTAND, APPLY, ANALYZE, EVALUATE |
| story_template | Rich Text | "Find the GCD of {a} and {b}" |
| answer_formula | Code | `math.gcd(a, b)` |
| params_json | Code | `{"a": {"min": 10, "max": 50}, "b": {...}}` |
| solution_steps | Rich Text | Multi-line steps with {params} |
| visual_hint | Text | "Use factor tree" |
| tags | Multi-select | word_problem, scheduling, grouping |

### Database 2: Distractor Patterns

| Property | Type | Description |
|----------|------|-------------|
| concept_id | Relation | Links to Question Templates |
| name | Text | `product_confusion` |
| formula | Code | `a * b` |
| misconception_type | Select | FORMULA_CONFUSION, etc. |
| why_wrong | Text | "Student multiplied instead of GCD" |
| teaching_point | Text | "GCD is the largest divisor of both" |

### Database 3: Story Templates (for Word Problems)

| Property | Type | Description |
|----------|------|-------------|
| concept_id | Select | `word_problem_lcm`, `word_problem_gcd` |
| context | Select | scheduling, grouping, arrangement |
| template | Rich Text | "Bus A comes every {a} minutes..." |
| unit | Text | minutes, days, bags |

---

## File Structure (New)

```
backend/
├── domain/
│   └── content_generation/
│       ├── generators/
│       │   ├── base.py              # Keep
│       │   └── factors_multiples.py # Keep as fallback
│       │
│       ├── templates/               # NEW
│       │   ├── __init__.py
│       │   ├── models.py            # Template dataclasses
│       │   └── validators.py        # Template validation
│       │
│       ├── engines/                 # NEW
│       │   ├── __init__.py
│       │   ├── template_engine.py   # TemplateQuestionEngine
│       │   └── formula_eval.py      # Safe formula evaluation
│       │
│       ├── services/                # NEW
│       │   ├── __init__.py
│       │   ├── notion_sync.py       # NotionSyncService
│       │   └── cache_manager.py     # Redis cache wrapper
│       │
│       └── orchestrator.py          # QuestionOrchestrator (updated)
│
├── config/
│   └── notion_config.py             # Notion API config
│
└── data/
    └── template_exports/            # YAML exports from extraction
        ├── factors.yaml
        ├── multiples.yaml
        ├── gcd.yaml
        ├── lcm.yaml
        └── ...
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Notion API rate limits | Redis cache (5-min sync), not real-time |
| Template formula errors | Validation on sync + fallback to monolith |
| Redis downtime | In-memory cache fallback |
| Content team breaks template | Schema validation + preview environment |

---

## Success Metrics

1. **Generation latency**: <15ms (vs current ~50ms)
2. **Content updates**: <5 min from Notion edit to live
3. **Error rate**: <0.1% (same or better than monolith)
4. **Coverage**: All 11 concepts supported

---

## Next Steps

1. [ ] Create `backend/domain/content_generation/templates/` directory
2. [ ] Implement `QuestionTemplate` model
3. [ ] Implement `TemplateQuestionEngine`
4. [ ] Extract first concept (factors) to YAML
5. [ ] Set up Notion workspace with databases
6. [ ] Implement `NotionSyncService`
7. [ ] Test end-to-end with factors
8. [ ] Extract remaining 10 concepts
9. [ ] A/B test with users
10. [ ] Full cutover
