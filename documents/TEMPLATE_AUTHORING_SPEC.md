# Template Authoring Specification
## For Factors & Multiples Chapter (Class 5 Mathematics)

---

## Table of Contents
1. [Template JSON Structure](#template-json-structure)
2. [Question Types Supported](#question-types-supported)
3. [Concept IDs & Knowledge Graph Mapping](#concept-ids--knowledge-graph-mapping)
4. [Variables System](#variables-system)
5. [Available Functions](#available-functions)
6. [Misconception Codes](#misconception-codes)
7. [Sample Templates by Concept](#sample-templates-by-concept)
8. [Validation Rules](#validation-rules)
9. [File Upload Format](#file-upload-format)

---

## Template JSON Structure

Every template must follow this Universal Schema format:

```json
{
  "name": "string (required) - Unique human-readable identifier",
  "concept_id": "string (required) - Maps to knowledge graph node",
  "question_type": "string (required) - One of: MCQ, FILL_BLANK, TRUE_FALSE, ASSERTION_REASON, MATCH_THE_FOLLOWING, CASE_STUDY, WORD_PROBLEM, DIAGRAM_BASED, ERROR_ANALYSIS",
  
  "question_pattern": "string (required) - Jinja2 template with {{variable}} placeholders",
  
  "variables": {
    "base": {
      "var_name": { "type": "integer|number|string", "min": N, "max": N, "enum": [...] }
    },
    "computed": {
      "derived_var": { "formula": "expression using base vars and functions" }
    },
    "constraints": ["expression that must be true, e.g., 'a != b'"]
  },
  
  "options": [
    { "pattern": "{{answer}}", "is_correct": true },
    { "pattern": "{{wrong1}}", "is_correct": false, "misconception_id": "CODE" },
    { "pattern": "{{wrong2}}", "is_correct": false, "misconception_id": "CODE" },
    { "pattern": "{{wrong3}}", "is_correct": false, "misconception_id": "CODE" }
  ],
  
  "difficulty": 1-5,
  "bloom_level": "REMEMBER|UNDERSTAND|APPLY|ANALYZE|EVALUATE|CREATE",
  "estimated_time": 30-120,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Step with {{variables}}" },
      { "number": 2, "text": "Next step..." }
    ]
  },
  
  "hints": [
    "Progressive hint 1 with {{variables}}",
    "Stronger hint 2 with {{variables}}"
  ],
  
  "narrative": "Optional K.C. Nag style story context with {{variables}}",
  
  "tags": ["topic", "subtopic", "grade", "board"]
}
```

---

## Question Types Supported

| Type | Description | Use Case |
|------|-------------|----------|
| `MCQ` | Multiple Choice (4 options) | Most common, misconception-based distractors |
| `FILL_BLANK` | Single numeric/text answer | Direct computation |
| `TRUE_FALSE` | Binary choice | Property verification |
| `ASSERTION_REASON` | A-R format (4 standard options) | Higher-order thinking |
| `ERROR_ANALYSIS` | "Find the error" questions | Evaluation level |
| `WORD_PROBLEM` | Contextual story problems | Real-world application |
| `MATCH_THE_FOLLOWING` | Matching pairs | Classification |
| `DIAGRAM_BASED` | Visual/spatial questions | Factor trees, Venn diagrams |
| `CASE_STUDY` | Multi-part from single context | Extended reasoning |

---

## Concept IDs & Knowledge Graph Mapping

### Factors & Multiples Chapter (Class 5)

| Concept ID | Short Key | Bloom Level(s) | Difficulty |
|------------|-----------|----------------|------------|
| `math.class5.factors_multiples.divisibility` | divisibility | REMEMBER | 1 |
| `math.class5.factors_multiples.prime_composite` | prime_composite | REMEMBER, UNDERSTAND | 1 |
| `math.class5.factors_multiples.factors` | factors | UNDERSTAND, APPLY | 2 |
| `math.class5.factors_multiples.multiples` | multiples | UNDERSTAND, APPLY | 2 |
| `math.class5.factors_multiples.factor_pairs` | factor_pairs | UNDERSTAND | 2 |
| `math.class5.factors_multiples.prime_factorization` | prime_factorization | APPLY | 2 |
| `math.class5.factors_multiples.gcd` | gcd | APPLY | 2 |
| `math.class5.factors_multiples.lcm` | lcm | APPLY | 2 |
| `math.class5.factors_multiples.word_problem` | word_problem | APPLY, ANALYZE | 3 |
| `math.class5.factors_multiples.assertion_reason` | assertion_reason | ANALYZE | 3 |
| `math.class5.factors_multiples.error_analysis` | error_analysis | EVALUATE | 3 |
| `math.class5.factors_multiples.cross_concept` | cross_concept | ANALYZE | 4 |

### Learning Path (Prerequisites)
```
divisibility ─┬─> factors ─┬─> factor_pairs
              │            ├─> gcd ──────────┬─> word_problem
              │            └─> prime_fact. ──┤
              │                              │
              ├─> multiples ─> lcm ──────────┼─> assertion_reason
              │                              │
              └─> prime_composite ───────────┴─> error_analysis ─> cross_concept
```

---

## Variables System

### Base Variables
Defined with random generation constraints:

```json
{
  "base": {
    "a": { "type": "integer", "min": 12, "max": 100 },
    "b": { "type": "integer", "enum": [2, 3, 5, 9, 10] },
    "name": { "type": "string", "enum": ["Aarav", "Priya", "Ravi", "Meera"] }
  }
}
```

### Computed Variables
Derived using formulas (see Available Functions):

```json
{
  "computed": {
    "gcd_result": { "formula": "gcd(a, b)" },
    "all_factors": { "formula": "factors(a)" },
    "wrong_answer": { "formula": "gcd(a, b) + 1" }
  }
}
```

### Constraints
Expressions that must evaluate to `True`:

```json
{
  "constraints": [
    "a != b",
    "gcd(a, b) > 1",
    "a % b != 0"
  ]
}
```

---

## Available Functions

### Basic Math
| Function | Description | Example |
|----------|-------------|---------|
| `gcd(a, b)` | Greatest Common Divisor | `gcd(24, 36)` → `12` |
| `lcm(a, b)` | Least Common Multiple | `lcm(4, 6)` → `12` |
| `factors(n)` | All factors of n | `factors(12)` → `[1, 2, 3, 4, 6, 12]` |
| `multiples(n, count)` | First `count` multiples | `multiples(3, 5)` → `[3, 6, 9, 12, 15]` |
| `prime_factors(n)` | Prime factorization list | `prime_factors(12)` → `[2, 2, 3]` |
| `is_prime(n)` | True if prime | `is_prime(7)` → `True` |
| `factor_count(n)` | Number of factors | `factor_count(12)` → `6` |
| `sum_factors(n)` | Sum of all factors | `sum_factors(12)` → `28` |

### Advanced Functions
| Function | Description | Example |
|----------|-------------|---------|
| `is_coprime(a, b)` | True if GCD is 1 | `is_coprime(8, 15)` → `True` |
| `common_factors(a, b)` | List of common factors | `common_factors(12, 18)` → `[1, 2, 3, 6]` |
| `gcd_three(a, b, c)` | GCD of three numbers | `gcd_three(12, 18, 24)` → `6` |
| `lcm_three(a, b, c)` | LCM of three numbers | `lcm_three(4, 6, 8)` → `24` |
| `divisibility_rule(n)` | Text rule for divisor | `divisibility_rule(3)` → `"Sum of digits..."` |
| `is_perfect_square(n)` | True if perfect square | `is_perfect_square(16)` → `True` |
| `nearest_multiple_above(n, d)` | Smallest multiple ≥ n | `nearest_multiple_above(17, 5)` → `20` |
| `nearest_multiple_below(n, d)` | Largest multiple ≤ n | `nearest_multiple_below(17, 5)` → `15` |
| `count_primes(start, end)` | Count primes in range | `count_primes(1, 10)` → `4` |

### Standard Math
| Function | Example |
|----------|---------|
| `abs(x)`, `min(a,b)`, `max(a,b)` | `min(5, 3)` → `3` |
| `pow(base, exp)`, `sqrt(n)` | `pow(2, 3)` → `8` |
| `floor(x)`, `ceil(x)`, `round(x)` | `floor(3.7)` → `3` |
| `len(list)`, `sum(list)`, `sorted(list)` | `len([1,2,3])` → `3` |

---

## Misconception Codes

Use these standard codes for distractor tagging:

### Factors & Multiples Specific
| Code | Description | Teaching Point |
|------|-------------|----------------|
| `GCD_LCM_CONFUSION` | Swapped GCD and LCM | GCD divides both; LCM is divisible by both |
| `MIN_IS_GCD` | Thinks smaller number is GCD | GCD can be smaller than both numbers |
| `PRODUCT_IS_LCM` | Thinks a×b is always LCM | Only true when GCD=1 |
| `FORGOT_1_FACTOR` | Didn't include 1 as factor | 1 is always a factor |
| `FORGOT_NUMBER_FACTOR` | Didn't include number itself | n is always a factor of n |
| `PRIME_VS_ODD` | Confuses prime with odd | 2 is prime but even; 9 is odd but composite |
| `DIVISIBILITY_RULE_ERROR` | Applied wrong divisibility rule | Each divisor has unique rule |

### General Math
| Code | Description |
|------|-------------|
| `CALCULATION_ERROR` | Arithmetic mistake |
| `SIGN_ERROR` | Wrong positive/negative |
| `OFF_BY_ONE` | Answer is ±1 from correct |
| `INCOMPLETE_REASONING` | Stopped before final step |
| `REVERSED_OPERATION` | Did subtraction instead of addition, etc. |
| `MAGNITUDE_ERROR` | Off by factor of 10 |

---

## Sample Templates by Concept

### 1. Divisibility (REMEMBER)

```json
{
  "name": "Divisibility Test - Single Divisor",
  "concept_id": "math.class5.factors_multiples.divisibility",
  "question_type": "MCQ",
  
  "question_pattern": "Which of the following numbers is divisible by {{divisor}}?",
  
  "variables": {
    "base": {
      "divisor": { "type": "integer", "enum": [2, 3, 5, 9, 10] },
      "base_number": { "type": "integer", "min": 10, "max": 50 }
    },
    "computed": {
      "correct": { "formula": "base_number * divisor" },
      "wrong1": { "formula": "base_number * divisor + 1" },
      "wrong2": { "formula": "base_number * divisor - 1" },
      "wrong3": { "formula": "(base_number + 1) * divisor + 2" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "{{correct}}", "is_correct": true },
    { "pattern": "{{wrong1}}", "is_correct": false, "misconception_id": "OFF_BY_ONE" },
    { "pattern": "{{wrong2}}", "is_correct": false, "misconception_id": "OFF_BY_ONE" },
    { "pattern": "{{wrong3}}", "is_correct": false, "misconception_id": "DIVISIBILITY_RULE_ERROR" }
  ],
  
  "difficulty": 1,
  "bloom_level": "REMEMBER",
  "estimated_time": 30,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Rule for {{divisor}}: {{divisibility_rule(divisor)}}" },
      { "number": 2, "text": "Check {{correct}}: divisible ✓" },
      { "number": 3, "text": "Check {{wrong1}}: not divisible ✗" }
    ]
  },
  
  "hints": [
    "Remember the divisibility rule for {{divisor}}",
    "{{divisibility_rule(divisor)}}"
  ],
  
  "tags": ["divisibility", "class5", "cbse", "easy"]
}
```

### 2. Factors (UNDERSTAND/APPLY)

```json
{
  "name": "Find All Factors",
  "concept_id": "math.class5.factors_multiples.factors",
  "question_type": "MCQ",
  
  "question_pattern": "How many factors does {{number}} have?",
  
  "variables": {
    "base": {
      "number": { "type": "integer", "enum": [12, 18, 24, 30, 36, 48] }
    },
    "computed": {
      "all_factors": { "formula": "factors(number)" },
      "answer": { "formula": "factor_count(number)" },
      "wrong1": { "formula": "factor_count(number) - 2" },
      "wrong2": { "formula": "factor_count(number) + 1" },
      "wrong3": { "formula": "number // 2" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "{{answer}}", "is_correct": true },
    { "pattern": "{{wrong1}}", "is_correct": false, "misconception_id": "FORGOT_1_FACTOR" },
    { "pattern": "{{wrong2}}", "is_correct": false, "misconception_id": "CALCULATION_ERROR" },
    { "pattern": "{{wrong3}}", "is_correct": false, "misconception_id": "INCOMPLETE_REASONING" }
  ],
  
  "difficulty": 2,
  "bloom_level": "UNDERSTAND",
  "estimated_time": 45,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Find all factors of {{number}} by checking which numbers divide it evenly" },
      { "number": 2, "text": "Factors: {{all_factors}}" },
      { "number": 3, "text": "Count: {{answer}} factors" }
    ]
  },
  
  "hints": [
    "Start by checking 1, 2, 3, ... up to √{{number}}",
    "Don't forget: 1 and {{number}} are always factors"
  ],
  
  "tags": ["factors", "counting", "class5"]
}
```

### 3. GCD (APPLY)

```json
{
  "name": "Find GCD of Two Numbers",
  "concept_id": "math.class5.factors_multiples.gcd",
  "question_type": "MCQ",
  
  "question_pattern": "Find the Greatest Common Divisor (GCD) of {{a}} and {{b}}.",
  
  "variables": {
    "base": {
      "multiplier": { "type": "integer", "min": 2, "max": 6 },
      "factor1": { "type": "integer", "enum": [2, 3, 4, 5, 6] },
      "factor2": { "type": "integer", "enum": [3, 4, 5, 7, 8] }
    },
    "computed": {
      "gcd_val": { "formula": "multiplier" },
      "a": { "formula": "multiplier * factor1" },
      "b": { "formula": "multiplier * factor2" },
      "lcm_val": { "formula": "lcm(a, b)" },
      "smaller": { "formula": "min(a, b)" },
      "wrong_calc": { "formula": "gcd(a, b) + 1" }
    },
    "constraints": [
      "factor1 != factor2",
      "gcd(factor1, factor2) == 1"
    ]
  },
  
  "options": [
    { "pattern": "{{gcd_val}}", "is_correct": true },
    { "pattern": "{{lcm_val}}", "is_correct": false, "misconception_id": "GCD_LCM_CONFUSION" },
    { "pattern": "{{smaller}}", "is_correct": false, "misconception_id": "MIN_IS_GCD" },
    { "pattern": "{{wrong_calc}}", "is_correct": false, "misconception_id": "CALCULATION_ERROR" }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 60,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Factors of {{a}}: {{factors(a)}}" },
      { "number": 2, "text": "Factors of {{b}}: {{factors(b)}}" },
      { "number": 3, "text": "Common factors: {{common_factors(a, b)}}" },
      { "number": 4, "text": "Greatest common factor (GCD): {{gcd_val}}" }
    ]
  },
  
  "hints": [
    "List all factors of both numbers",
    "Find which factors appear in BOTH lists",
    "Pick the LARGEST common factor"
  ],
  
  "tags": ["gcd", "hcf", "class5", "cbse"]
}
```

### 4. LCM (APPLY)

```json
{
  "name": "Find LCM of Two Numbers",
  "concept_id": "math.class5.factors_multiples.lcm",
  "question_type": "MCQ",
  
  "question_pattern": "Find the Least Common Multiple (LCM) of {{a}} and {{b}}.",
  
  "variables": {
    "base": {
      "a": { "type": "integer", "enum": [4, 6, 8, 10, 12] },
      "b": { "type": "integer", "enum": [3, 5, 6, 9, 15] }
    },
    "computed": {
      "lcm_val": { "formula": "lcm(a, b)" },
      "gcd_val": { "formula": "gcd(a, b)" },
      "product": { "formula": "a * b" },
      "wrong_sum": { "formula": "a + b" }
    },
    "constraints": ["a != b"]
  },
  
  "options": [
    { "pattern": "{{lcm_val}}", "is_correct": true },
    { "pattern": "{{gcd_val}}", "is_correct": false, "misconception_id": "GCD_LCM_CONFUSION" },
    { "pattern": "{{product}}", "is_correct": false, "misconception_id": "PRODUCT_IS_LCM" },
    { "pattern": "{{wrong_sum}}", "is_correct": false, "misconception_id": "REVERSED_OPERATION" }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 60,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Multiples of {{a}}: {{multiples(a, 6)}}, ..." },
      { "number": 2, "text": "Multiples of {{b}}: {{multiples(b, 6)}}, ..." },
      { "number": 3, "text": "First common multiple: {{lcm_val}}" },
      { "number": 4, "text": "LCM({{a}}, {{b}}) = {{lcm_val}}" }
    ]
  },
  
  "hints": [
    "List multiples of both numbers",
    "Find the smallest number that appears in both lists"
  ],
  
  "tags": ["lcm", "multiples", "class5"]
}
```

### 5. Word Problem (APPLY/ANALYZE)

```json
{
  "name": "Word Problem - Bus Scheduling (LCM)",
  "concept_id": "math.class5.factors_multiples.word_problem",
  "question_type": "WORD_PROBLEM",
  
  "question_pattern": "Two buses start together from a bus station. One bus leaves every {{interval1}} minutes and another leaves every {{interval2}} minutes. After how many minutes will both buses leave together again?",
  
  "variables": {
    "base": {
      "interval1": { "type": "integer", "enum": [10, 12, 15, 20] },
      "interval2": { "type": "integer", "enum": [12, 15, 18, 25, 30] }
    },
    "computed": {
      "answer": { "formula": "lcm(interval1, interval2)" },
      "wrong_gcd": { "formula": "gcd(interval1, interval2)" },
      "wrong_sum": { "formula": "interval1 + interval2" },
      "wrong_product": { "formula": "interval1 * interval2" }
    },
    "constraints": ["interval1 != interval2"]
  },
  
  "options": [
    { "pattern": "{{answer}} minutes", "is_correct": true },
    { "pattern": "{{wrong_gcd}} minutes", "is_correct": false, "misconception_id": "GCD_LCM_CONFUSION" },
    { "pattern": "{{wrong_sum}} minutes", "is_correct": false, "misconception_id": "INCOMPLETE_REASONING" },
    { "pattern": "{{wrong_product}} minutes", "is_correct": false, "misconception_id": "PRODUCT_IS_LCM" }
  ],
  
  "difficulty": 3,
  "bloom_level": "APPLY",
  "estimated_time": 90,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "This is an LCM problem - we need to find when both events coincide" },
      { "number": 2, "text": "Bus 1 leaves at: {{interval1}}, {{interval1 * 2}}, {{interval1 * 3}}, ..." },
      { "number": 3, "text": "Bus 2 leaves at: {{interval2}}, {{interval2 * 2}}, {{interval2 * 3}}, ..." },
      { "number": 4, "text": "LCM({{interval1}}, {{interval2}}) = {{answer}}" },
      { "number": 5, "text": "Both buses will leave together after {{answer}} minutes" }
    ]
  },
  
  "hints": [
    "When do we use LCM? When we need to find when events will happen together again.",
    "List when each bus leaves and find the first common time."
  ],
  
  "narrative": "{{name}} is at the central bus station. The {{destination1}} bus comes every {{interval1}} minutes and the {{destination2}} bus comes every {{interval2}} minutes. Both buses just left together.",
  
  "tags": ["lcm", "word-problem", "scheduling", "class5"]
}
```

### 6. Assertion-Reason (ANALYZE)

```json
{
  "name": "Assertion-Reason - GCD Property",
  "concept_id": "math.class5.factors_multiples.assertion_reason",
  "question_type": "ASSERTION_REASON",
  
  "question_pattern": "**Assertion (A):** GCD of {{a}} and {{b}} is {{gcd_val}}.\n\n**Reason (R):** {{gcd_val}} is the largest number that divides both {{a}} and {{b}} without remainder.\n\nChoose the correct option:",
  
  "variables": {
    "base": {
      "a": { "type": "integer", "enum": [24, 36, 48, 60] },
      "b": { "type": "integer", "enum": [18, 30, 42, 54] }
    },
    "computed": {
      "gcd_val": { "formula": "gcd(a, b)" }
    },
    "constraints": ["gcd(a, b) > 2"]
  },
  
  "options": [
    { "pattern": "Both A and R are true, and R is the correct explanation of A", "is_correct": true },
    { "pattern": "Both A and R are true, but R is NOT the correct explanation of A", "is_correct": false, "misconception_id": "INCOMPLETE_REASONING" },
    { "pattern": "A is true but R is false", "is_correct": false, "misconception_id": "GCD_LCM_CONFUSION" },
    { "pattern": "A is false but R is true", "is_correct": false, "misconception_id": "CALCULATION_ERROR" }
  ],
  
  "difficulty": 3,
  "bloom_level": "ANALYZE",
  "estimated_time": 90,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Check Assertion: Factors of {{a}} = {{factors(a)}}" },
      { "number": 2, "text": "Factors of {{b}} = {{factors(b)}}" },
      { "number": 3, "text": "Common factors = {{common_factors(a, b)}}, GCD = {{gcd_val}} ✓" },
      { "number": 4, "text": "Check Reason: By definition, GCD is the largest common divisor ✓" },
      { "number": 5, "text": "The reason correctly explains WHY the assertion is true" }
    ]
  },
  
  "hints": [
    "First verify if the assertion (A) is mathematically correct",
    "Then check if the reason (R) is the definition/explanation of A"
  ],
  
  "tags": ["assertion-reason", "gcd", "analyze", "class5"]
}
```

### 7. Error Analysis (EVALUATE)

```json
{
  "name": "Error Analysis - Student Calculation",
  "concept_id": "math.class5.factors_multiples.error_analysis",
  "question_type": "ERROR_ANALYSIS",
  
  "question_pattern": "**Student's Work:**\nFind factors of {{number}}\n\n{{name}}'s answer: {{wrong_factors}}\n\n**Question:** What error did {{name}} make?",
  
  "variables": {
    "base": {
      "number": { "type": "integer", "enum": [24, 36, 48, 60] },
      "name": { "type": "string", "enum": ["Aarav", "Priya", "Ravi", "Meera"] },
      "error_type": { "type": "string", "enum": ["forgot_1", "forgot_n", "missed_pair"] }
    },
    "computed": {
      "correct_factors": { "formula": "factors(number)" },
      "wrong_factors": { "formula": "factors(number)[1:]" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "Forgot to include 1 as a factor", "is_correct": true },
    { "pattern": "Forgot to include {{number}} as a factor", "is_correct": false, "misconception_id": "FORGOT_NUMBER_FACTOR" },
    { "pattern": "Made a calculation error", "is_correct": false, "misconception_id": "CALCULATION_ERROR" },
    { "pattern": "Listed too many factors", "is_correct": false, "misconception_id": "INCOMPLETE_REASONING" }
  ],
  
  "difficulty": 3,
  "bloom_level": "EVALUATE",
  "estimated_time": 75,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Correct factors of {{number}}: {{correct_factors}}" },
      { "number": 2, "text": "{{name}}'s factors: {{wrong_factors}}" },
      { "number": 3, "text": "Missing: 1" },
      { "number": 4, "text": "Error: Forgot that 1 is always a factor of every number" }
    ]
  },
  
  "hints": [
    "Compare the student's answer with the correct list",
    "What's missing from the student's answer?"
  ],
  
  "tags": ["error-analysis", "factors", "evaluate", "class5"]
}
```

### 8. Prime/Composite (REMEMBER/UNDERSTAND)

```json
{
  "name": "Classify Prime or Composite",
  "concept_id": "math.class5.factors_multiples.prime_composite",
  "question_type": "MCQ",
  
  "question_pattern": "Which of the following is a prime number?",
  
  "variables": {
    "base": {
      "prime": { "type": "integer", "enum": [7, 11, 13, 17, 19, 23, 29, 31] },
      "composite1": { "type": "integer", "enum": [9, 15, 21, 25, 27, 33] },
      "composite2": { "type": "integer", "enum": [14, 22, 26, 34, 38] },
      "one": { "type": "integer", "enum": [1] }
    },
    "computed": {},
    "constraints": []
  },
  
  "options": [
    { "pattern": "{{prime}}", "is_correct": true },
    { "pattern": "{{composite1}}", "is_correct": false, "misconception_id": "PRIME_VS_ODD" },
    { "pattern": "{{composite2}}", "is_correct": false, "misconception_id": "CALCULATION_ERROR" },
    { "pattern": "{{one}}", "is_correct": false, "misconception_id": "INCOMPLETE_REASONING" }
  ],
  
  "difficulty": 1,
  "bloom_level": "REMEMBER",
  "estimated_time": 30,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "A prime number has exactly 2 factors: 1 and itself" },
      { "number": 2, "text": "Factors of {{prime}}: [1, {{prime}}] → only 2 factors → PRIME ✓" },
      { "number": 3, "text": "Factors of {{composite1}}: more than 2 factors → COMPOSITE" },
      { "number": 4, "text": "1 has only one factor, so it is neither prime nor composite" }
    ]
  },
  
  "hints": [
    "Prime = exactly 2 factors",
    "Check: can the number be divided by anything other than 1 and itself?"
  ],
  
  "tags": ["prime", "composite", "classification", "class5"]
}
```

### 9. Prime Factorization (APPLY)

```json
{
  "name": "Prime Factorization - Express as Product",
  "concept_id": "math.class5.factors_multiples.prime_factorization",
  "question_type": "MCQ",
  
  "question_pattern": "Express {{number}} as a product of prime factors.",
  
  "variables": {
    "base": {
      "p1": { "type": "integer", "enum": [2, 3] },
      "p2": { "type": "integer", "enum": [2, 3, 5] },
      "exp1": { "type": "integer", "min": 1, "max": 3 },
      "exp2": { "type": "integer", "min": 1, "max": 2 }
    },
    "computed": {
      "number": { "formula": "pow(p1, exp1) * pow(p2, exp2)" },
      "answer": { "formula": "'{}^{} × {}^{}'.format(p1, exp1, p2, exp2)" },
      "wrong1": { "formula": "'{}^{} × {}^{}'.format(p1, exp1+1, p2, exp2)" },
      "wrong2": { "formula": "'{}^{} + {}^{}'.format(p1, exp1, p2, exp2)" },
      "wrong3": { "formula": "'{} × {}'.format(p1 * exp1, p2 * exp2)" }
    },
    "constraints": ["p1 != p2"]
  },
  
  "options": [
    { "pattern": "{{answer}}", "is_correct": true },
    { "pattern": "{{wrong1}}", "is_correct": false, "misconception_id": "CALCULATION_ERROR" },
    { "pattern": "{{wrong2}}", "is_correct": false, "misconception_id": "REVERSED_OPERATION" },
    { "pattern": "{{wrong3}}", "is_correct": false, "misconception_id": "INCOMPLETE_REASONING" }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 60,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Divide {{number}} by smallest prime" },
      { "number": 2, "text": "Continue until you get 1" },
      { "number": 3, "text": "Prime factors: {{prime_factors(number)}}" },
      { "number": 4, "text": "Express as powers: {{answer}}" }
    ]
  },
  
  "hints": [
    "Start dividing by 2, then 3, then 5...",
    "Keep dividing until quotient is 1"
  ],
  
  "tags": ["prime-factorization", "class5"]
}
```

---

## Validation Rules

Templates are validated before acceptance:

### Required Fields
- ✅ `name` - Unique, descriptive
- ✅ `concept_id` - Must match knowledge graph node
- ✅ `question_type` - Valid enum value
- ✅ `question_pattern` - Non-empty, uses valid variables
- ✅ `variables.base` - At least one variable
- ✅ `options` - Exactly 4 for MCQ (1 correct, 3 with misconceptions)
- ✅ `difficulty` - 1-5
- ✅ `bloom_level` - Valid taxonomy level
- ✅ `solution.steps` - At least 2 steps

### Variable Validation
- All `{{variable}}` in patterns must be defined
- Computed formulas must use only valid functions
- Constraints must evaluate to boolean

### Generation Test
- 5 questions generated during preview
- All must produce valid, different instances
- Correct answer must appear in options

---

## File Upload Format

### Single Template (JSON)
```json
{
  "name": "...",
  "concept_id": "...",
  ...
}
```

### Batch Templates (JSON)
```json
{
  "templates": [
    { "name": "Template 1", ... },
    { "name": "Template 2", ... }
  ],
  "metadata": {
    "chapter": "factors_multiples",
    "created_by": "Content Team",
    "version": "1.0"
  }
}
```

### YAML Format
```yaml
templates:
  - name: Template 1
    concept_id: math.class5.factors_multiples.gcd
    question_type: MCQ
    # ... rest of fields

  - name: Template 2
    concept_id: math.class5.factors_multiples.lcm
    question_type: MCQ
    # ...

metadata:
  chapter: factors_multiples
  created_by: Content Team
  version: "1.0"
```

---

## Workflow After Upload

1. **Validate** - System checks JSON schema & generates test questions
2. **Preview** - See 5 sample questions in UI
3. **Save as Draft** - Template saved but not active
4. **Submit for Review** - Goes to review queue
5. **Approve** - Reviewer validates pedagogical quality
6. **Publish** - Template becomes active for students

---

## Contact

For questions about this specification:
- API Documentation: `/api/docs` 
- Template Preview: Admin UI → Templates → Universal Editor
- Graph Visualization: Admin UI → Knowledge Graph

