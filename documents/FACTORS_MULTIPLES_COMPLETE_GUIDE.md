# Factors & Multiples Chapter - Complete Template Creation Guide

**Date:** 18 January 2026  
**Chapter:** Class 5 - Be My Multiple (NCERT Chapter 9)  
**Goal:** Create 20 templates covering all concepts with all 9 question types

---

## 🎯 Table of Contents

1. [Concept Hierarchy (Knowledge Graph)](#concept-hierarchy)
2. [Template JSON Structure](#template-json-structure)
3. [Available Functions (Formula Library)](#available-functions)
4. [Question Types & Samples](#question-types)
5. [Complete Template Examples (All 9 Types)](#complete-examples)
6. [File Upload Specification](#file-upload-specification)
7. [Validation Checklist](#validation-checklist)

---

## 🌳 Concept Hierarchy (Knowledge Graph) {#concept-hierarchy}

Each template MUST be mapped to one of these **EXACT** concept IDs from the knowledge graph:

```
math.class5.factors_multiples
│
├── divisibility        → "math.class5.factors_multiples.divisibility"
│   Description: Apply divisibility rules for 2, 3, 5, 9, 10
│   Bloom: REMEMBER | Difficulty: 1
│
├── prime_composite     → "math.class5.factors_multiples.prime_composite"
│   Description: Classify numbers as prime or composite
│   Bloom: REMEMBER, UNDERSTAND | Difficulty: 1
│
├── factors             → "math.class5.factors_multiples.factors"
│   Description: Find all factors of a number
│   Bloom: UNDERSTAND, APPLY | Difficulty: 2
│
├── multiples           → "math.class5.factors_multiples.multiples"
│   Description: Generate multiples of a number
│   Bloom: UNDERSTAND, APPLY | Difficulty: 2
│
├── factor_pairs        → "math.class5.factors_multiples.factor_pairs"
│   Description: Find all pairs (a,b) where a×b = target
│   Bloom: UNDERSTAND | Difficulty: 2
│
├── gcd                 → "math.class5.factors_multiples.gcd"
│   Description: Find Greatest Common Divisor (HCF)
│   Bloom: APPLY | Difficulty: 2
│
├── lcm                 → "math.class5.factors_multiples.lcm"
│   Description: Find Least Common Multiple
│   Bloom: APPLY | Difficulty: 2
│
├── prime_factorization → "math.class5.factors_multiples.prime_factorization"
│   Description: Express number as product of primes
│   Bloom: APPLY | Difficulty: 2
│
├── word_problem        → "math.class5.factors_multiples.word_problem"
│   Description: Real-world HCF/LCM/factors problems
│   Bloom: APPLY, ANALYZE | Difficulty: 3
│
├── assertion_reason    → "math.class5.factors_multiples.assertion_reason"
│   Description: Evaluate assertion-reason statements
│   Bloom: ANALYZE | Difficulty: 3
│
├── error_analysis      → "math.class5.factors_multiples.error_analysis"
│   Description: Identify errors in worked solutions
│   Bloom: EVALUATE | Difficulty: 3
│
└── cross_concept       → "math.class5.factors_multiples.cross_concept"
    Description: Problems combining multiple concepts
    Bloom: ANALYZE | Difficulty: 4
```

### ⚠️ IMPORTANT: Valid Concept IDs (Copy exactly)

```
math.class5.factors_multiples.divisibility
math.class5.factors_multiples.prime_composite
math.class5.factors_multiples.factors
math.class5.factors_multiples.multiples
math.class5.factors_multiples.factor_pairs
math.class5.factors_multiples.gcd
math.class5.factors_multiples.lcm
math.class5.factors_multiples.prime_factorization
math.class5.factors_multiples.word_problem
math.class5.factors_multiples.assertion_reason
math.class5.factors_multiples.error_analysis
math.class5.factors_multiples.cross_concept
```

### Concept ID Format

```
math.class{grade}.{chapter}.{concept}
```

**Examples:**
- `math.class5.factors_multiples.factors` ✅
- `math.class5.factors_multiples.gcd` ✅
- `math.class5.factors_multiples.word_problem` ✅

---

## 📋 Template JSON Structure {#template-json-structure}

### MINIMAL REQUIRED FIELDS (11 fields)

```json
{
  "name": "string (required) - Human readable name",
  "concept_id": "string (required) - From knowledge graph above",
  "question_type": "string (required) - One of 9 types below",
  "question_pattern": "string (required for most types) - Uses {{variables}}",
  "variables": {
    "base": { },
    "computed": { },
    "constraints": [ ]
  },
  "options": [ ],
  "difficulty": 1-5,
  "solution": { },
  "hints": [ ],
  "tags": [ ],
  "source": "FILE_IMPORT"
}
```

### COMPLETE STRUCTURE (All Fields)

```json
{
  "id": "optional - auto-generated if not provided",
  
  "name": "HCF of Two Numbers",
  "concept_id": "math.class5.factors_multiples.hcf.two_numbers",
  "question_type": "MCQ",
  
  "question_pattern": "Find the HCF (GCD) of {{a}} and {{b}}.",
  
  "parts": null,
  
  "variables": {
    "base": {
      "a": {
        "type": "integer",
        "enum": [12, 18, 24, 30, 36, 48, 60],
        "description": "First number"
      },
      "b": {
        "type": "integer", 
        "enum": [8, 16, 20, 24, 32, 40],
        "description": "Second number"
      }
    },
    "computed": {
      "hcf_result": {
        "formula": "gcd(a, b)",
        "description": "HCF of a and b"
      },
      "lcm_result": {
        "formula": "lcm(a, b)",
        "description": "LCM - common wrong answer"
      },
      "factors_a": {
        "formula": "factors(a)",
        "description": "All factors of a"
      },
      "factors_b": {
        "formula": "factors(b)", 
        "description": "All factors of b"
      }
    },
    "constraints": [
      "a != b",
      "a > 10",
      "b > 10"
    ]
  },
  
  "options": [
    {
      "pattern": "{{hcf_result}}",
      "is_correct": true
    },
    {
      "pattern": "{{a}}",
      "is_correct": false,
      "misconception_id": "CONFUSED_NUMBER_WITH_HCF",
      "student_thinking": "Thought the first number itself is the HCF",
      "remediation": "HCF is the LARGEST factor common to BOTH numbers"
    },
    {
      "pattern": "{{lcm_result}}",
      "is_correct": false,
      "misconception_id": "CONFUSED_HCF_WITH_LCM",
      "student_thinking": "Confused HCF with LCM",
      "remediation": "HCF = Highest Common FACTOR (divides both), LCM = Lowest Common MULTIPLE (both divide into)"
    },
    {
      "pattern": "{{a * b}}",
      "is_correct": false,
      "misconception_id": "PRODUCT_CONFUSION",
      "student_thinking": "Multiplied the numbers instead",
      "remediation": "HCF involves finding common factors, not multiplying"
    }
  ],
  
  "difficulty": 2,
  
  "solution": {
    "steps": [
      {
        "number": 1,
        "text": "Find factors of {{a}}: {{factors_a}}",
        "explanation": "List all numbers that divide {{a}} evenly"
      },
      {
        "number": 2,
        "text": "Find factors of {{b}}: {{factors_b}}",
        "explanation": "List all numbers that divide {{b}} evenly"
      },
      {
        "number": 3,
        "text": "Common factors are: {{common_factors(a, b)}}",
        "explanation": "Numbers that appear in both lists"
      },
      {
        "number": 4,
        "text": "HCF = {{hcf_result}} (the highest common factor)",
        "explanation": "Pick the largest from common factors"
      }
    ]
  },
  
  "hints": [
    "First, list all factors of {{a}}",
    "Then, list all factors of {{b}}",
    "Find which factors are common to both lists"
  ],
  
  "diagram": {
    "type": "gcd",
    "parameters": {
      "num1": "{{a}}",
      "num2": "{{b}}",
      "result": "{{hcf_result}}"
    }
  },
  
  "requires_latex": false,
  
  "source": "FILE_IMPORT",
  "status": "DRAFT",
  "tags": ["hcf", "gcd", "factors", "class5"],
  
  "bloom_level": "APPLY",
  "estimated_time": 90
}
```

---

## 🔧 Available Functions (Formula Library) {#available-functions}

### Math Operations
| Function | Usage | Example | Result |
|----------|-------|---------|--------|
| `gcd(a, b)` | HCF/GCD of two numbers | `gcd(12, 18)` | `6` |
| `lcm(a, b)` | LCM of two numbers | `lcm(4, 6)` | `12` |
| `gcd_three(a, b, c)` | HCF of three numbers | `gcd_three(12, 18, 24)` | `6` |
| `lcm_three(a, b, c)` | LCM of three numbers | `lcm_three(4, 6, 8)` | `24` |
| `sqrt(n)` | Square root | `sqrt(16)` | `4.0` |
| `abs(n)` | Absolute value | `abs(-5)` | `5` |
| `pow(a, b)` | Power | `pow(2, 3)` | `8` |
| `min(a, b, ...)` | Minimum | `min(3, 7, 1)` | `1` |
| `max(a, b, ...)` | Maximum | `max(3, 7, 1)` | `7` |
| `floor(n)` | Floor | `floor(3.7)` | `3` |
| `ceil(n)` | Ceiling | `ceil(3.2)` | `4` |
| `round(n)` | Round | `round(3.5)` | `4` |

### Educational Helpers
| Function | Usage | Example | Result |
|----------|-------|---------|--------|
| `factors(n)` | All factors of n | `factors(12)` | `[1,2,3,4,6,12]` |
| `multiples(n, count)` | First 'count' multiples | `multiples(3, 5)` | `[3,6,9,12,15]` |
| `is_prime(n)` | Check if prime | `is_prime(7)` | `True` |
| `prime_factors(n)` | Prime factorization | `prime_factors(12)` | `[2,2,3]` |
| `factor_count(n)` | Number of factors | `factor_count(12)` | `6` |
| `sum_factors(n)` | Sum of all factors | `sum_factors(12)` | `28` |
| `is_coprime(a, b)` | Are a,b coprime? | `is_coprime(8, 15)` | `True` |
| `common_factors(a, b)` | Common factors | `common_factors(12, 18)` | `[1,2,3,6]` |
| `is_perfect_square(n)` | Perfect square check | `is_perfect_square(16)` | `True` |
| `is_perfect_cube(n)` | Perfect cube check | `is_perfect_cube(27)` | `True` |
| `count_primes(start, end)` | Primes in range | `count_primes(1, 10)` | `4` |
| `nearest_multiple_above(n, d)` | Nearest multiple ≥ n | `nearest_multiple_above(17, 5)` | `20` |
| `nearest_multiple_below(n, d)` | Nearest multiple ≤ n | `nearest_multiple_below(17, 5)` | `15` |
| `divisibility_rule(d)` | Rule text for divisor | `divisibility_rule(3)` | `"Sum of digits..."` |
| `lcm_plus_remainder(a, b, r)` | LCM + remainder | `lcm_plus_remainder(4, 6, 3)` | `15` |

### Data Operations
| Function | Usage | Example | Result |
|----------|-------|---------|--------|
| `len(list)` | Length | `len([1,2,3])` | `3` |
| `sum(list)` | Sum | `sum([1,2,3])` | `6` |
| `sorted(list)` | Sort | `sorted([3,1,2])` | `[1,2,3]` |
| `list(x)` | Convert to list | - | - |

---

## 📝 Question Types & Samples {#question-types}

### 1. MCQ (Multiple Choice Question)

```json
{
  "question_type": "MCQ",
  "question_pattern": "What is the HCF of {{a}} and {{b}}?",
  "options": [
    { "pattern": "{{gcd(a, b)}}", "is_correct": true },
    { "pattern": "{{lcm(a, b)}}", "is_correct": false },
    { "pattern": "{{a}}", "is_correct": false },
    { "pattern": "{{b}}", "is_correct": false }
  ]
}
```

### 2. MCQ_MULTI (Multiple Correct Answers)

```json
{
  "question_type": "MCQ_MULTI",
  "question_pattern": "Which of the following are factors of {{number}}?",
  "options": [
    { "pattern": "{{factor1}}", "is_correct": true },
    { "pattern": "{{factor2}}", "is_correct": true },
    { "pattern": "{{non_factor1}}", "is_correct": false },
    { "pattern": "{{non_factor2}}", "is_correct": false }
  ]
}
```

### 3. FILL_BLANK

```json
{
  "question_type": "FILL_BLANK",
  "question_pattern": "The LCM of {{a}} and {{b}} is ____.",
  "options": [
    { "pattern": "{{lcm(a, b)}}", "is_correct": true },
    { "pattern": "{{gcd(a, b)}}", "is_correct": false },
    { "pattern": "{{a * b}}", "is_correct": false },
    { "pattern": "{{a + b}}", "is_correct": false }
  ]
}
```

### 4. TRUE_FALSE

```json
{
  "question_type": "TRUE_FALSE",
  "question_pattern": "{{number}} is a prime number.",
  "variables": {
    "base": {
      "number": { "type": "integer", "enum": [7, 11, 13, 17, 19, 23] }
    },
    "computed": {
      "is_prime_result": { "formula": "is_prime(number)" }
    }
  },
  "options": [
    { "pattern": "True", "is_correct": "{{is_prime_result}}" },
    { "pattern": "False", "is_correct": "{{not is_prime_result}}" }
  ]
}
```

### 5. ASSERTION_REASON

```json
{
  "question_type": "ASSERTION_REASON",
  "question_pattern": "",
  "parts": [
    {
      "type": "assertion",
      "label": "A",
      "pattern": "{{a}} and {{b}} are co-prime numbers.",
      "is_true": "{{is_coprime(a, b)}}"
    },
    {
      "type": "reason",
      "label": "R",
      "pattern": "The HCF of {{a}} and {{b}} is 1.",
      "is_true": "{{gcd(a, b) == 1}}"
    }
  ],
  "options": [
    {
      "pattern": "Both A and R are true, and R is the correct explanation of A",
      "is_correct": "{{is_coprime(a, b) and gcd(a, b) == 1}}"
    },
    {
      "pattern": "Both A and R are true, but R is not the correct explanation of A",
      "is_correct": false
    },
    {
      "pattern": "A is true but R is false",
      "is_correct": false
    },
    {
      "pattern": "A is false but R is true",
      "is_correct": "{{not is_coprime(a, b) and gcd(a, b) == 1}}"
    }
  ]
}
```

### 6. CASE_STUDY

```json
{
  "question_type": "CASE_STUDY",
  "question_pattern": "",
  "parts": [
    {
      "type": "context",
      "pattern": "Priya has {{total_apples}} apples and {{total_oranges}} oranges. She wants to pack them into baskets so that each basket has the same number of fruits and no fruits are left over."
    },
    {
      "type": "sub_question",
      "label": "i",
      "pattern": "What is the maximum number of baskets she can make?",
      "options": [
        { "pattern": "{{gcd(total_apples, total_oranges)}}", "is_correct": true },
        { "pattern": "{{lcm(total_apples, total_oranges)}}", "is_correct": false },
        { "pattern": "{{total_apples + total_oranges}}", "is_correct": false },
        { "pattern": "{{total_apples}}", "is_correct": false }
      ]
    },
    {
      "type": "sub_question",
      "label": "ii",
      "pattern": "How many apples will be in each basket?",
      "options": [
        { "pattern": "{{total_apples // gcd(total_apples, total_oranges)}}", "is_correct": true },
        { "pattern": "{{total_apples}}", "is_correct": false },
        { "pattern": "{{gcd(total_apples, total_oranges)}}", "is_correct": false },
        { "pattern": "{{total_oranges // gcd(total_apples, total_oranges)}}", "is_correct": false }
      ]
    }
  ]
}
```

### 7. MATCH_FOLLOWING

```json
{
  "question_type": "MATCH_FOLLOWING",
  "question_pattern": "Match the numbers with their number of factors:",
  "variables": {
    "base": {
      "num1": { "type": "integer", "enum": [12, 18, 24] },
      "num2": { "type": "integer", "enum": [15, 20, 25] },
      "num3": { "type": "integer", "enum": [16, 36, 49] }
    },
    "computed": {
      "count1": { "formula": "factor_count(num1)" },
      "count2": { "formula": "factor_count(num2)" },
      "count3": { "formula": "factor_count(num3)" }
    }
  },
  "parts": [
    {
      "type": "context",
      "pattern": "Column A: Numbers | Column B: Number of Factors\n1. {{num1}} | P. {{count2}}\n2. {{num2}} | Q. {{count3}}\n3. {{num3}} | R. {{count1}}"
    }
  ],
  "options": [
    { "pattern": "1-R, 2-P, 3-Q", "is_correct": true },
    { "pattern": "1-P, 2-Q, 3-R", "is_correct": false },
    { "pattern": "1-Q, 2-R, 3-P", "is_correct": false },
    { "pattern": "1-R, 2-Q, 3-P", "is_correct": false }
  ]
}
```

### 8. ORDERING

```json
{
  "question_type": "ORDERING",
  "question_pattern": "Arrange the following numbers in ascending order of their number of factors: {{num1}}, {{num2}}, {{num3}}, {{num4}}",
  "variables": {
    "base": {
      "num1": { "type": "integer", "enum": [12] },
      "num2": { "type": "integer", "enum": [7] },
      "num3": { "type": "integer", "enum": [24] },
      "num4": { "type": "integer", "enum": [16] }
    },
    "computed": {
      "c1": { "formula": "factor_count(num1)" },
      "c2": { "formula": "factor_count(num2)" },
      "c3": { "formula": "factor_count(num3)" },
      "c4": { "formula": "factor_count(num4)" }
    }
  },
  "options": [
    { "pattern": "7, 16, 12, 24", "is_correct": true },
    { "pattern": "7, 12, 16, 24", "is_correct": false },
    { "pattern": "12, 7, 16, 24", "is_correct": false },
    { "pattern": "24, 16, 12, 7", "is_correct": false }
  ]
}
```

### 9. NUMERIC (Direct Answer)

```json
{
  "question_type": "NUMERIC",
  "question_pattern": "How many prime numbers are there between 1 and {{upper_limit}}?",
  "variables": {
    "base": {
      "upper_limit": { "type": "integer", "enum": [20, 30, 50, 100] }
    },
    "computed": {
      "prime_count": { "formula": "count_primes(1, upper_limit)" }
    }
  },
  "options": [
    { "pattern": "{{prime_count}}", "is_correct": true },
    { "pattern": "{{prime_count + 1}}", "is_correct": false },
    { "pattern": "{{prime_count - 1}}", "is_correct": false },
    { "pattern": "{{prime_count + 2}}", "is_correct": false }
  ]
}
```

---

## 📁 File Upload Specification {#file-upload-specification}

### Supported Formats
- **JSON** (`.json`) - Preferred
- **YAML** (`.yaml`, `.yml`)

### Single Template Upload

**File:** `template.json`
```json
{
  "name": "Find Factors of a Number",
  "concept_id": "math.class5.factors_multiples.factors.find_all",
  "question_type": "MCQ",
  "question_pattern": "Find all factors of {{number}}.",
  "variables": {
    "base": {
      "number": {
        "type": "integer",
        "enum": [12, 18, 24, 30, 36, 48, 60, 72]
      }
    },
    "computed": {
      "factors_list": { "formula": "factors(number)" },
      "factor_count": { "formula": "len(factors(number))" },
      "multiples_list": { "formula": "multiples(number, 4)" }
    }
  },
  "options": [
    {
      "pattern": "{{factors_list}}",
      "is_correct": true
    },
    {
      "pattern": "{{multiples_list}}",
      "is_correct": false,
      "misconception_id": "FACTORS_VS_MULTIPLES",
      "student_thinking": "Confused factors with multiples"
    },
    {
      "pattern": "[1, {{number}}]",
      "is_correct": false,
      "misconception_id": "ONLY_TRIVIAL_FACTORS",
      "student_thinking": "Only listed 1 and the number itself"
    },
    {
      "pattern": "{{factors_list[1:-1]}}",
      "is_correct": false,
      "misconception_id": "MISSING_ENDPOINTS",
      "student_thinking": "Forgot to include 1 and the number"
    }
  ],
  "difficulty": 2,
  "solution": {
    "steps": [
      { "number": 1, "text": "To find factors of {{number}}, we need numbers that divide {{number}} evenly." },
      { "number": 2, "text": "Start from 1 and test each number up to {{number}}." },
      { "number": 3, "text": "{{number}} ÷ 1 = {{number}} ✓ (1 is a factor)" },
      { "number": 4, "text": "Continue testing: 2, 3, 4, ..." },
      { "number": 5, "text": "The factors of {{number}} are: {{factors_list}}" }
    ]
  },
  "hints": [
    "A factor divides the number evenly (no remainder)",
    "1 is always a factor of every number",
    "The number itself is always its own factor"
  ],
  "tags": ["factors", "find-factors", "basic"],
  "source": "FILE_IMPORT"
}
```

### Batch Upload (Multiple Templates)

**File:** `factors_multiples_templates.json`
```json
{
  "templates": [
    {
      "name": "Template 1 - Find Factors",
      "concept_id": "math.class5.factors_multiples.factors.find_all",
      "question_type": "MCQ",
      "question_pattern": "...",
      "variables": { ... },
      "options": [ ... ],
      "difficulty": 2,
      "solution": { ... },
      "source": "FILE_IMPORT"
    },
    {
      "name": "Template 2 - Find Multiples",
      "concept_id": "math.class5.factors_multiples.multiples.find",
      "question_type": "MCQ",
      "question_pattern": "...",
      "variables": { ... },
      "options": [ ... ],
      "difficulty": 2,
      "solution": { ... },
      "source": "FILE_IMPORT"
    }
  ],
  "metadata": {
    "chapter": "factors_multiples",
    "grade": 5,
    "subject": "mathematics",
    "uploaded_by": "content_team",
    "version": "1.0"
  }
}
```

### YAML Format Example

**File:** `template.yaml`
```yaml
name: "Find Factors of a Number"
concept_id: "math.class5.factors_multiples.factors.find_all"
question_type: "MCQ"
question_pattern: "Find all factors of {{number}}."

variables:
  base:
    number:
      type: integer
      enum: [12, 18, 24, 30, 36, 48, 60, 72]
  computed:
    factors_list:
      formula: "factors(number)"
    factor_count:
      formula: "len(factors(number))"

options:
  - pattern: "{{factors_list}}"
    is_correct: true
  - pattern: "{{multiples(number, 4)}}"
    is_correct: false
    misconception_id: "FACTORS_VS_MULTIPLES"
  - pattern: "[1, {{number}}]"
    is_correct: false
  - pattern: "{{factors_list[1:-1]}}"
    is_correct: false

difficulty: 2

solution:
  steps:
    - number: 1
      text: "To find factors of {{number}}, test which numbers divide evenly."
    - number: 2
      text: "The factors are: {{factors_list}}"

hints:
  - "A factor divides the number with no remainder"
  - "Don't forget 1 and the number itself"

tags:
  - factors
  - basic
  - class5

source: FILE_IMPORT
```

---

## ✅ Validation Checklist {#validation-checklist}

Before submitting templates, verify:

### Structure Validation
- [ ] `name` is present and descriptive
- [ ] `concept_id` matches the knowledge graph hierarchy
- [ ] `question_type` is one of: MCQ, MCQ_MULTI, FILL_BLANK, TRUE_FALSE, ASSERTION_REASON, CASE_STUDY, MATCH_FOLLOWING, ORDERING, NUMERIC
- [ ] `question_pattern` OR `parts` is present
- [ ] At least 2 options (4 recommended for MCQ)
- [ ] Exactly ONE option has `is_correct: true` (for MCQ) OR dynamic correctness formula
- [ ] `difficulty` is 1-5

### Variable Validation
- [ ] All `{{variable}}` in patterns are defined in `variables.base` or `variables.computed`
- [ ] `computed` formulas use only available functions
- [ ] `constraints` prevent invalid combinations (e.g., `a != b`)

### Content Validation
- [ ] Question is clear and unambiguous
- [ ] Correct answer is mathematically accurate
- [ ] Distractors are plausible (common mistakes)
- [ ] Solution steps are logical and complete
- [ ] Hints are progressive (not giving away the answer)

### Misconception Validation
- [ ] Wrong options have `misconception_id` (recommended)
- [ ] `student_thinking` explains why a student might choose this
- [ ] `remediation` provides guidance to correct the misconception

---

## 📊 Coverage Matrix - Your 20 Templates

Please ensure your 20 templates cover:

| Concept | MCQ | Fill Blank | True/False | A-R | Case Study | Other | Total |
|---------|-----|------------|------------|-----|------------|-------|-------|
| Factors | 2 | 1 | 1 | - | - | - | 4 |
| Multiples | 2 | 1 | 1 | - | - | - | 4 |
| Prime/Composite | 1 | - | 1 | 1 | - | - | 3 |
| Divisibility | 1 | 1 | - | - | - | 1 | 3 |
| HCF | 1 | - | - | 1 | 1 | - | 3 |
| LCM | 1 | - | - | - | 1 | 1 | 3 |
| **Total** | 8 | 3 | 3 | 2 | 2 | 2 | **20** |

---

## 🚀 Next Steps

1. **Create your 20 templates** following this guide
2. **Validate using the checklist** above
3. **Upload via Admin UI** at `/templates/universal`
4. **Preview each template** to verify question generation
5. **Save & Publish** approved templates
6. **Test student practice flow** with adaptive learning

I will validate your templates against:
- Schema compliance
- Formula correctness
- Question generation (10 test instances per template)
- Option validity (correct answer present, no duplicates)
- Concept ID validity

Ready when you are! 📚
