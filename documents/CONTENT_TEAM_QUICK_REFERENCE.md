# Content Team Template Upload Guide
## Quick Reference for Factors & Multiples Chapter

**Date:** 18 January 2026  
**Chapter:** Class 5 - Be My Multiple (Chapter 9)

---

## 📝 EXACT JSON STRUCTURE FOR A SINGLE TEMPLATE

```json
{
  "name": "Template Name (Descriptive)",
  "concept_id": "math.class5.factors_multiples.{concept}",
  "question_type": "MCQ | MCQ_MULTI | FILL_BLANK | TRUE_FALSE | ASSERTION_REASON | CASE_STUDY | MATCH_FOLLOWING | ORDERING | NUMERIC",
  "question_pattern": "Question text with {{variable}} placeholders.",
  
  "variables": {
    "base": {
      "variable_name": {
        "type": "integer",
        "enum": [12, 18, 24, 30, 36]
      }
    },
    "computed": {
      "result": { "formula": "gcd(a, b)" }
    },
    "constraints": ["a != b"]
  },
  
  "options": [
    { "pattern": "{{result}}", "is_correct": true },
    { "pattern": "{{wrong1}}", "is_correct": false, "misconception_id": "ERROR_TYPE" }
  ],
  
  "difficulty": 2,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Step 1 explanation with {{variable}}" }
    ]
  },
  
  "hints": ["Hint 1", "Hint 2"],
  "tags": ["factors", "basic"],
  "source": "FILE_IMPORT"
}
```

---

## 🎯 VALID CONCEPT IDs (Use EXACTLY These - from Knowledge Graph)

⚠️ **IMPORTANT:** Only use these EXACT concept IDs. Any other format will be rejected.

| Concept ID | Description | Difficulty |
|------------|-------------|------------|
| `math.class5.factors_multiples.divisibility` | Divisibility rules (2,3,5,9,10) | 1 |
| `math.class5.factors_multiples.prime_composite` | Prime vs composite classification | 1 |
| `math.class5.factors_multiples.factors` | Find all factors of a number | 2 |
| `math.class5.factors_multiples.multiples` | Generate multiples | 2 |
| `math.class5.factors_multiples.factor_pairs` | Find factor pairs (a,b) where a×b=n | 2 |
| `math.class5.factors_multiples.gcd` | HCF/GCD of numbers | 2 |
| `math.class5.factors_multiples.lcm` | LCM of numbers | 2 |
| `math.class5.factors_multiples.prime_factorization` | Express as product of primes | 2 |
| `math.class5.factors_multiples.word_problem` | Real-world HCF/LCM problems | 3 |
| `math.class5.factors_multiples.assertion_reason` | A-R statement evaluation | 3 |
| `math.class5.factors_multiples.error_analysis` | Find errors in solutions | 3 |
| `math.class5.factors_multiples.cross_concept` | Combined concept problems | 4 |

### Copy-Paste Ready:
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

---

## 🔧 AVAILABLE FORMULA FUNCTIONS

| Function | Example | Result |
|----------|---------|--------|
| `gcd(a, b)` | `gcd(12, 18)` | `6` |
| `lcm(a, b)` | `lcm(4, 6)` | `12` |
| `gcd_three(a, b, c)` | `gcd_three(12, 18, 24)` | `6` |
| `lcm_three(a, b, c)` | `lcm_three(4, 6, 8)` | `24` |
| `factors(n)` | `factors(12)` | `[1,2,3,4,6,12]` |
| `multiples(n, count)` | `multiples(3, 5)` | `[3,6,9,12,15]` |
| `is_prime(n)` | `is_prime(7)` | `True` |
| `prime_factors(n)` | `prime_factors(12)` | `[2,2,3]` |
| `factor_count(n)` | `factor_count(12)` | `6` |
| `sum_factors(n)` | `sum_factors(12)` | `28` |
| `is_coprime(a, b)` | `is_coprime(8, 15)` | `True` |
| `common_factors(a, b)` | `common_factors(12, 18)` | `[1,2,3,6]` |
| `count_primes(start, end)` | `count_primes(1, 10)` | `4` |
| `divisibility_rule(d)` | `divisibility_rule(3)` | `"Sum of digits..."` |
| `nearest_multiple_above(n, d)` | `nearest_multiple_above(17, 5)` | `20` |
| `len(list)` | `len([1,2,3])` | `3` |
| `sum(list)` | `sum([1,2,3])` | `6` |
| `min(a, b)` / `max(a, b)` | `min(3, 7)` | `3` |

---

## 📋 QUESTION TYPE REQUIREMENTS

### 1. MCQ (Multiple Choice)
```json
{
  "question_type": "MCQ",
  "options": [
    { "pattern": "...", "is_correct": true },
    { "pattern": "...", "is_correct": false },
    { "pattern": "...", "is_correct": false },
    { "pattern": "...", "is_correct": false }
  ]
}
```
**Rule:** Exactly ONE option with `is_correct: true`

### 2. MCQ_MULTI (Multiple Correct)
```json
{
  "question_type": "MCQ_MULTI",
  "options": [
    { "pattern": "...", "is_correct": true },
    { "pattern": "...", "is_correct": true },
    { "pattern": "...", "is_correct": false },
    { "pattern": "...", "is_correct": false }
  ]
}
```
**Rule:** Multiple options can have `is_correct: true`

### 3. FILL_BLANK
```json
{
  "question_type": "FILL_BLANK",
  "question_pattern": "The HCF of 12 and 18 is ____."
}
```
**Rule:** Use `____` in question_pattern

### 4. TRUE_FALSE
```json
{
  "question_type": "TRUE_FALSE",
  "options": [
    { "pattern": "True", "is_correct": "{{is_prime(number)}}" },
    { "pattern": "False", "is_correct": "{{not is_prime(number)}}" }
  ]
}
```
**Rule:** Dynamic correctness using formula

### 5. ASSERTION_REASON
```json
{
  "question_type": "ASSERTION_REASON",
  "parts": [
    { "type": "assertion", "label": "A", "pattern": "Statement A" },
    { "type": "reason", "label": "R", "pattern": "Statement R" }
  ],
  "options": [
    { "pattern": "Both A and R are true, R explains A", "is_correct": true },
    { "pattern": "Both true, R doesn't explain A", "is_correct": false },
    { "pattern": "A true, R false", "is_correct": false },
    { "pattern": "A false, R true", "is_correct": false }
  ]
}
```

### 6. CASE_STUDY
```json
{
  "question_type": "CASE_STUDY",
  "parts": [
    { "type": "context", "pattern": "Background story..." },
    { "type": "sub_question", "label": "i", "pattern": "Question 1", "options": [...] },
    { "type": "sub_question", "label": "ii", "pattern": "Question 2", "options": [...] }
  ]
}
```

### 7. MATCH_FOLLOWING
```json
{
  "question_type": "MATCH_FOLLOWING",
  "parts": [
    { "type": "context", "pattern": "Column A | Column B\n1. ... | P. ...\n2. ... | Q. ..." }
  ],
  "options": [
    { "pattern": "1-P, 2-Q", "is_correct": true },
    { "pattern": "1-Q, 2-P", "is_correct": false }
  ]
}
```

### 8. ORDERING
```json
{
  "question_type": "ORDERING",
  "question_pattern": "Arrange in ascending order: {{a}}, {{b}}, {{c}}"
}
```

### 9. NUMERIC
```json
{
  "question_type": "NUMERIC",
  "question_pattern": "How many prime numbers between 1 and 20?"
}
```

---

## 📁 FILE UPLOAD FORMAT

### Single Template
Save as `.json` file:
```json
{
  "name": "...",
  "concept_id": "...",
  ...
}
```

### Batch Upload (Multiple Templates)
Save as `.json` file:
```json
{
  "templates": [
    { "name": "Template 1", ... },
    { "name": "Template 2", ... }
  ],
  "metadata": {
    "chapter": "factors_multiples",
    "grade": 5,
    "subject": "mathematics"
  }
}
```

---

## ✅ VALIDATION CHECKLIST

Before uploading, verify:

1. ☐ `name` is present and descriptive
2. ☐ `concept_id` matches hierarchy above
3. ☐ `question_type` is one of 9 valid types
4. ☐ `question_pattern` uses `{{variable}}` syntax
5. ☐ All variables used in patterns are defined
6. ☐ Formulas only use functions from the list above
7. ☐ Exactly ONE correct option (for MCQ)
8. ☐ `difficulty` is 1-5
9. ☐ `solution.steps` explains the answer
10. ☐ `source` is set to `"FILE_IMPORT"`

---

## 🚀 UPLOAD STEPS

1. **Create JSON file** with your templates
2. **Go to Admin UI** → `/templates/universal`
3. **Click "Import File"** or paste JSON
4. **Click "Preview"** to generate test questions
5. **Verify** the generated questions look correct
6. **Save** to store in database
7. **Publish** when ready for students

---

## 📊 REQUIRED COVERAGE (20 Templates)

| Concept Area | Required | Question Types |
|--------------|----------|----------------|
| Factors | 4 | MCQ, FILL_BLANK, MCQ_MULTI, ORDERING |
| Multiples | 3 | MCQ, FILL_BLANK |
| Prime/Composite | 3 | TRUE_FALSE, MCQ, NUMERIC |
| Divisibility | 3 | FILL_BLANK, MCQ |
| HCF | 4 | MCQ, ASSERTION_REASON, CASE_STUDY |
| LCM | 3 | MCQ, CASE_STUDY |
| **Total** | **20** | **All 9 types** |

---

## 📚 SAMPLE FILE LOCATION

See complete 20-template example at:
`documents/SAMPLE_20_TEMPLATES.json`

This file contains working examples of ALL 9 question types that you can use as reference or modify.
