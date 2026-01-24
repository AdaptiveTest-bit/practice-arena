# Content Writer Admin Flow Guide
## Step-by-Step Template Creation with LLM Assistance

**For:** Content Writers  
**Date:** 18 January 2026  
**System:** Practice Arena Template Editor

---

## 🎯 Overview

This guide walks you through creating a new question template using the Admin UI.
You'll learn:
1. How to define a concept and question type
2. How to use the formula library
3. When to use LLM assistance (optional)
4. How to validate and publish

---

## 📋 Complete Example: Creating a Quadratic Roots Template

### Step 1: Access the Template Editor

```
Admin UI → Templates → Create New Template
```

### Step 2: Fill the Template Form

Copy this JSON into the **Universal Template Ingestor** at:
`POST /api/admin/templates/universal/ingest`

Or use the Admin UI form with these values:

---

## 📝 EXAMPLE 1: Standard MCQ (No LLM Needed)

### Template JSON (Copy-Paste Ready)

```json
{
  "name": "Quadratic - Find Roots by Factorization",
  "concept_id": "math.class10.quadratic.solve_factorization",
  "question_type": "MCQ",
  
  "question_pattern": "Find the roots of the equation x² − {{sum}}x + {{product}} = 0",
  
  "variables": {
    "base": {
      "root1": {
        "type": "integer",
        "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9]
      },
      "root2": {
        "type": "integer", 
        "enum": [2, 3, 4, 5, 6, 7, 8, 9, 10]
      }
    },
    "computed": {
      "sum": { "formula": "root1 + root2" },
      "product": { "formula": "root1 * root2" }
    },
    "constraints": [
      "root1 < root2",
      "root1 != root2"
    ]
  },
  
  "options": [
    {
      "pattern": "{{root1}} and {{root2}}",
      "is_correct": true
    },
    {
      "pattern": "{{root1}} and −{{root2}}",
      "is_correct": false,
      "misconception_id": "SIGN_ERROR",
      "student_thinking": "Student forgot that both roots are positive when product is positive"
    },
    {
      "pattern": "{{sum}} and {{product}}",
      "is_correct": false,
      "misconception_id": "SUM_PRODUCT_CONFUSION",
      "student_thinking": "Confused sum and product of roots with the roots themselves"
    },
    {
      "pattern": "{{root1 + 1}} and {{root2 - 1}}",
      "is_correct": false,
      "misconception_id": "FACTORIZATION_ERROR",
      "student_thinking": "Made arithmetic error during factorization"
    }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 60,
  "requires_latex": true,
  
  "solution": {
    "steps": [
      {"number": 1, "text": "We need two numbers whose sum is {{sum}} and product is {{product}}"},
      {"number": 2, "text": "Think: What numbers multiply to {{product}}?"},
      {"number": 3, "text": "{{root1}} × {{root2}} = {{product}} ✓"},
      {"number": 4, "text": "{{root1}} + {{root2}} = {{sum}} ✓"},
      {"number": 5, "text": "So, x² − {{sum}}x + {{product}} = (x − {{root1}})(x − {{root2}})"},
      {"number": 6, "text": "Therefore, x = {{root1}} or x = {{root2}}"}
    ]
  },
  
  "hints": [
    "What two numbers add up to {{sum}}?",
    "Those same two numbers should multiply to give {{product}}",
    "Try listing factor pairs of {{product}}"
  ],
  
  "tags": ["quadratic", "factorization", "roots", "class10", "cbse"]
}
```

### What This Template Generates

With `root1=3, root2=5`:
- **Question:** Find the roots of the equation x² − 8x + 15 = 0
- **Options:**
  - A) 3 and 5 ✓
  - B) 3 and −5
  - C) 8 and 15
  - D) 4 and 4

---

## 📝 EXAMPLE 2: Nature of Roots (Discriminant)

```json
{
  "name": "Quadratic - Nature of Roots",
  "concept_id": "math.class10.quadratic.nature_of_roots",
  "question_type": "MCQ",
  
  "question_pattern": "Determine the nature of roots of the equation x² − {{b}}x + {{c}} = 0",
  
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [2, 3, 4, 5, 6, 7, 8] },
      "c": { "type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16, 20] }
    },
    "computed": {
      "discriminant": { "formula": "b*b - 4*c" },
      "nature_text": { 
        "formula": "'two distinct real roots' if (b*b - 4*c) > 0 else ('two equal real roots' if (b*b - 4*c) == 0 else 'no real roots')" 
      }
    },
    "constraints": []
  },
  
  "options": [
    {
      "pattern": "{{nature_text}}",
      "is_correct": true
    },
    {
      "pattern": "two distinct real roots",
      "is_correct": false,
      "misconception_id": "DISCRIMINANT_CALC_ERROR"
    },
    {
      "pattern": "two equal real roots", 
      "is_correct": false,
      "misconception_id": "DISCRIMINANT_CONDITION_ERROR"
    },
    {
      "pattern": "no real roots",
      "is_correct": false,
      "misconception_id": "NEGATIVE_DISCRIMINANT_ERROR"
    }
  ],
  
  "difficulty": 2,
  "bloom_level": "UNDERSTAND",
  "estimated_time": 45,
  "requires_latex": true,
  
  "solution": {
    "steps": [
      {"number": 1, "text": "For ax² + bx + c = 0, discriminant D = b² − 4ac"},
      {"number": 2, "text": "Here a = 1, b = −{{b}}, c = {{c}}"},
      {"number": 3, "text": "D = (−{{b}})² − 4(1)({{c}}) = {{b*b}} − {{4*c}} = {{discriminant}}"},
      {"number": 4, "text": "Since D = {{discriminant}} is {{'> 0' if discriminant > 0 else ('= 0' if discriminant == 0 else '< 0')}}"},
      {"number": 5, "text": "The equation has {{nature_text}}"}
    ]
  },
  
  "tags": ["quadratic", "discriminant", "nature-of-roots", "class10"]
}
```

---

## 📝 EXAMPLE 3: Word Problem (LLM Helps Generate Variations)

### Base Template (Human Creates)

```json
{
  "name": "Quadratic - Consecutive Integers Product",
  "concept_id": "math.class10.quadratic.word_problems",
  "question_type": "MCQ",
  
  "question_pattern": "The product of two consecutive positive integers is {{product}}. Find the integers.",
  
  "variables": {
    "base": {
      "n": { "type": "integer", "enum": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20] }
    },
    "computed": {
      "n_plus_1": { "formula": "n + 1" },
      "product": { "formula": "n * (n + 1)" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "{{n}} and {{n_plus_1}}", "is_correct": true },
    { "pattern": "{{n - 1}} and {{n}}", "is_correct": false, "misconception_id": "OFF_BY_ONE" },
    { "pattern": "{{n}} and {{n + 2}}", "is_correct": false, "misconception_id": "NON_CONSECUTIVE" },
    { "pattern": "{{n - 2}} and {{n + 1}}", "is_correct": false, "misconception_id": "RANDOM_FACTORS" }
  ],
  
  "difficulty": 3,
  "bloom_level": "APPLY",
  "estimated_time": 90,
  
  "variations": [
    {
      "id": "var_base",
      "context": "abstract",
      "question_pattern": "The product of two consecutive positive integers is {{product}}. Find the integers.",
      "answer_pattern": "{{n}} and {{n_plus_1}}",
      "status": "APPROVED"
    },
    {
      "id": "var_age",
      "context": "age",
      "question_pattern": "Ravi's age this year multiplied by his age next year equals {{product}}. How old is Ravi now?",
      "answer_pattern": "Ravi is {{n}} years old",
      "status": "APPROVED"
    },
    {
      "id": "var_rectangle",
      "context": "geometry",
      "question_pattern": "A rectangle has length 1 meter more than its width. If its area is {{product}} sq.m, find its dimensions.",
      "answer_pattern": "Width = {{n}} m, Length = {{n_plus_1}} m",
      "status": "APPROVED"
    },
    {
      "id": "var_pages",
      "context": "books",
      "question_pattern": "Two facing pages in a book have page numbers whose product is {{product}}. Find the page numbers.",
      "answer_pattern": "Pages {{n}} and {{n_plus_1}}",
      "status": "APPROVED"
    }
  ],
  
  "solution": {
    "steps": [
      {"number": 1, "text": "Let the consecutive integers be n and (n+1)"},
      {"number": 2, "text": "Given: n × (n+1) = {{product}}"},
      {"number": 3, "text": "n² + n − {{product}} = 0"},
      {"number": 4, "text": "Solving this quadratic equation:"},
      {"number": 5, "text": "n = {{n}} (taking positive value)"},
      {"number": 6, "text": "The integers are {{n}} and {{n_plus_1}}"}
    ]
  },
  
  "tags": ["quadratic", "word-problem", "consecutive-integers", "class10"]
}
```

### 🤖 LLM Assistance for Word Problems

If you want MORE variations, use the LLM tool:

**Step 1:** Go to Admin UI → LLM Tools → Word Problem Variations

**Step 2:** Fill the form:
```
Base Problem: "The product of two consecutive positive integers is {{product}}. Find them."
Variables: n (first integer), n_plus_1 (second integer), product
Number of Variations: 5
Contexts: sports, shopping, travel, science, cooking
```

**Step 3:** LLM generates (you review & approve):
```json
[
  {
    "context": "sports",
    "question_pattern": "In a cricket tournament, Team A scored runs in two consecutive overs. The product of runs scored is {{product}}. Find the runs in each over.",
    "status": "DRAFT"
  },
  {
    "context": "shopping",
    "question_pattern": "Priya bought items priced at two consecutive rupee values. The product of prices is ₹{{product}}. What were the prices?",
    "status": "DRAFT"
  },
  {
    "context": "science",
    "question_pattern": "Two consecutive atomic numbers have nuclei whose product of protons is {{product}}. Find the atomic numbers.",
    "status": "DRAFT"
  }
]
```

**Step 4:** Review each variation and click "Approve" or "Reject"

---

## 📝 EXAMPLE 4: Assertion-Reason Type

```json
{
  "name": "Quadratic - Assertion Reason (Nature of Roots)",
  "concept_id": "math.class10.quadratic.assertion_reason",
  "question_type": "ASSERTION_REASON",
  
  "parts": [
    {
      "type": "assertion",
      "label": "A",
      "pattern": "The equation x² − {{b}}x + {{c}} = 0 has {{'two distinct real' if discriminant > 0 else ('two equal' if discriminant == 0 else 'no real')}} roots."
    },
    {
      "type": "reason",
      "label": "R",
      "pattern": "The discriminant of the equation is {{discriminant}}, which is {{'positive' if discriminant > 0 else ('zero' if discriminant == 0 else 'negative')}}."
    }
  ],
  
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [4, 5, 6, 7, 8] },
      "c": { "type": "integer", "enum": [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 16] }
    },
    "computed": {
      "discriminant": { "formula": "b*b - 4*c" }
    },
    "constraints": []
  },
  
  "options": [
    {
      "pattern": "Both A and R are true, and R is the correct explanation of A",
      "is_correct": true
    },
    {
      "pattern": "Both A and R are true, but R is NOT the correct explanation of A",
      "is_correct": false
    },
    {
      "pattern": "A is true but R is false",
      "is_correct": false
    },
    {
      "pattern": "A is false but R is true",
      "is_correct": false
    }
  ],
  
  "difficulty": 3,
  "bloom_level": "ANALYZE",
  "estimated_time": 90,
  
  "solution": {
    "steps": [
      {"number": 1, "text": "For the equation x² − {{b}}x + {{c}} = 0:"},
      {"number": 2, "text": "a = 1, b = −{{b}}, c = {{c}}"},
      {"number": 3, "text": "Discriminant D = b² − 4ac = {{b}}² − 4({{c}}) = {{discriminant}}"},
      {"number": 4, "text": "Since D = {{discriminant}} is {{'positive' if discriminant > 0 else ('zero' if discriminant == 0 else 'negative')}}:"},
      {"number": 5, "text": "Assertion is TRUE (equation has {{'two distinct real' if discriminant > 0 else ('two equal' if discriminant == 0 else 'no real')}} roots)"},
      {"number": 6, "text": "Reason is TRUE (discriminant is correctly stated)"},
      {"number": 7, "text": "R correctly explains A, so answer is (a)"}
    ]
  },
  
  "tags": ["quadratic", "assertion-reason", "discriminant", "class10", "cbse"]
}
```

---

## 📝 EXAMPLE 5: Case Study (Projectile Motion)

```json
{
  "name": "Quadratic - Case Study (Projectile Motion)",
  "concept_id": "math.class10.quadratic.applications.projectile",
  "question_type": "CASE_STUDY",
  
  "parts": [
    {
      "type": "context",
      "pattern": "In a school sports day, a student throws a ball. The height h (in meters) of the ball above the ground is given by the equation:\n\nh = −x² + {{b}}x\n\nwhere x is the horizontal distance (in meters) from the throwing point.\n\nBased on this information, answer the following questions:"
    },
    {
      "type": "sub_question",
      "label": "i",
      "pattern": "At what horizontal distance does the ball reach its maximum height?",
      "options": [
        { "pattern": "{{max_x}} m", "is_correct": true },
        { "pattern": "{{b}} m", "is_correct": false },
        { "pattern": "{{max_x + 1}} m", "is_correct": false },
        { "pattern": "{{landing_x}} m", "is_correct": false }
      ]
    },
    {
      "type": "sub_question",
      "label": "ii", 
      "pattern": "What is the maximum height reached by the ball?",
      "options": [
        { "pattern": "{{max_height}} m", "is_correct": true },
        { "pattern": "{{b}} m", "is_correct": false },
        { "pattern": "{{max_x}} m", "is_correct": false },
        { "pattern": "{{max_height - 1}} m", "is_correct": false }
      ]
    },
    {
      "type": "sub_question",
      "label": "iii",
      "pattern": "At what horizontal distance does the ball hit the ground?",
      "options": [
        { "pattern": "{{landing_x}} m", "is_correct": true },
        { "pattern": "{{max_x}} m", "is_correct": false },
        { "pattern": "{{b + 1}} m", "is_correct": false },
        { "pattern": "{{max_height}} m", "is_correct": false }
      ]
    }
  ],
  
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [4, 6, 8, 10, 12] }
    },
    "computed": {
      "max_x": { "formula": "b / 2" },
      "max_height": { "formula": "(b * b) / 4" },
      "landing_x": { "formula": "b" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "See sub-questions above", "is_correct": true }
  ],
  
  "difficulty": 4,
  "bloom_level": "ANALYZE",
  "estimated_time": 180,
  "requires_latex": true,
  
  "diagram": {
    "type": "parabola",
    "parameters": {
      "a": "-1",
      "b": "{{b}}",
      "c": "0",
      "show_vertex": "true",
      "show_zeros": "true"
    }
  },
  
  "solution": {
    "steps": [
      {"number": 1, "text": "The equation h = −x² + {{b}}x represents a downward parabola"},
      {"number": 2, "text": "Maximum height at vertex: x = −b/2a = −{{b}}/2(−1) = {{max_x}}"},
      {"number": 3, "text": "Max height h = −({{max_x}})² + {{b}}({{max_x}}) = {{max_height}} m"},
      {"number": 4, "text": "Ball hits ground when h = 0: −x² + {{b}}x = 0"},
      {"number": 5, "text": "x(−x + {{b}}) = 0, so x = 0 or x = {{landing_x}}"},
      {"number": 6, "text": "Landing distance = {{landing_x}} m (non-zero root)"}
    ]
  },
  
  "tags": ["quadratic", "case-study", "projectile", "parabola", "vertex", "class10", "cbse"]
}
```

---

## 🔄 Admin UI Workflow Summary

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONTENT WRITER WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 1: CREATE NEW TEMPLATE                                         │   │
│  │                                                                      │   │
│  │  Admin UI → Templates → Create New                                  │   │
│  │                                                                      │   │
│  │  Choose input method:                                               │   │
│  │  [📝 Form Editor]  [📋 JSON/YAML]  [📁 Upload File]                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 2: BASIC INFORMATION                                           │   │
│  │                                                                      │   │
│  │  Name: [Quadratic - Find Roots by Factorization        ]           │   │
│  │  Concept: [math.class10.quadratic.solve_factorization  ▼]          │   │
│  │  Question Type: [MCQ                                   ▼]          │   │
│  │  Difficulty: [1] [2●] [3] [4] [5]                                  │   │
│  │  Estimated Time: [60] seconds                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 3: QUESTION PATTERN                                            │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ Find the roots of the equation x² − {{sum}}x + {{product}} │   │   │
│  │  │ = 0                                                          │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  💡 Use {{variable_name}} for dynamic values                        │   │
│  │  📚 [Browse Formula Library]                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 4: DEFINE VARIABLES                                            │   │
│  │                                                                      │   │
│  │  ┌─ BASE VARIABLES (randomly generated) ──────────────────────┐    │   │
│  │  │                                                             │    │   │
│  │  │  [+] root1: integer, enum: [1,2,3,4,5,6,7,8,9]            │    │   │
│  │  │  [+] root2: integer, enum: [2,3,4,5,6,7,8,9,10]           │    │   │
│  │  │                                                             │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  ┌─ COMPUTED VARIABLES (formulas) ────────────────────────────┐    │   │
│  │  │                                                             │    │   │
│  │  │  [+] sum = root1 + root2                                   │    │   │
│  │  │  [+] product = root1 * root2                               │    │   │
│  │  │                                                             │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  ┌─ CONSTRAINTS ──────────────────────────────────────────────┐    │   │
│  │  │                                                             │    │   │
│  │  │  [+] root1 < root2                                         │    │   │
│  │  │  [+] root1 != root2                                        │    │   │
│  │  │                                                             │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 5: ANSWER OPTIONS                                              │   │
│  │                                                                      │   │
│  │  Option 1: [{{root1}} and {{root2}}            ] ✅ Correct        │   │
│  │  Option 2: [{{root1}} and -{{root2}}           ] ❌ Wrong          │   │
│  │            Misconception: [SIGN_ERROR          ▼]                  │   │
│  │  Option 3: [{{sum}} and {{product}}            ] ❌ Wrong          │   │
│  │            Misconception: [SUM_PRODUCT_CONFUSION▼]                 │   │
│  │  Option 4: [{{root1+1}} and {{root2-1}}        ] ❌ Wrong          │   │
│  │            Misconception: [FACTORIZATION_ERROR ▼]                  │   │
│  │                                                                      │   │
│  │  [+ Add Option]                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 6: SOLUTION & HINTS (Optional but Recommended)                 │   │
│  │                                                                      │   │
│  │  Solution Steps:                                                    │   │
│  │  1. [We need two numbers with sum {{sum}} and product {{product}}] │   │
│  │  2. [Think: What numbers multiply to {{product}}?                 ] │   │
│  │  3. [{{root1}} × {{root2}} = {{product}} ✓                        ] │   │
│  │  [+ Add Step]                                                       │   │
│  │                                                                      │   │
│  │  Hints:                                                             │   │
│  │  1. [What two numbers add up to {{sum}}?                          ] │   │
│  │  2. [Those numbers should multiply to give {{product}}            ] │   │
│  │  [+ Add Hint]                                                       │   │
│  │                                                                      │   │
│  │  🤖 [Generate Solution with LLM]  🤖 [Generate Hints with LLM]     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 7: PREVIEW & VALIDATE                                          │   │
│  │                                                                      │   │
│  │  ┌─ Generated Question Preview ───────────────────────────────┐    │   │
│  │  │                                                             │    │   │
│  │  │  Q: Find the roots of the equation x² − 8x + 15 = 0        │    │   │
│  │  │                                                             │    │   │
│  │  │  A) 3 and 5      ✓                                         │    │   │
│  │  │  B) 3 and -5                                                │    │   │
│  │  │  C) 8 and 15                                                │    │   │
│  │  │  D) 4 and 4                                                 │    │   │
│  │  │                                                             │    │   │
│  │  │  Variables: root1=3, root2=5, sum=8, product=15            │    │   │
│  │  │                                                             │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  [🔄 Generate Another]  [Generate 10 for Review]                   │   │
│  │                                                                      │   │
│  │  ┌─ Validation Results ───────────────────────────────────────┐    │   │
│  │  │  ✅ Schema valid                                           │    │   │
│  │  │  ✅ Formulas compile                                       │    │   │
│  │  │  ✅ 10/10 test generations passed                          │    │   │
│  │  │  ✅ No duplicate options detected                          │    │   │
│  │  │  ✅ All constraints satisfied                              │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ STEP 8: SAVE & PUBLISH                                              │   │
│  │                                                                      │   │
│  │  [💾 Save as Draft]  [📤 Submit for Review]  [🚀 Publish Now]      │   │
│  │                                                                      │   │
│  │  Status: DRAFT → REVIEW → APPROVED → PUBLISHED                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 When to Use LLM Assistance

| Task | Use LLM? | Why |
|------|----------|-----|
| **Number generation** | ❌ No | Use formulas - deterministic, free |
| **Basic calculations** | ❌ No | Use computed variables |
| **Option patterns** | ❌ No | Define with misconceptions |
| **Word problem variations** | ✅ Yes | Creative, saves hours |
| **Solution steps** | ✅ Maybe | Review carefully for math accuracy |
| **Diagram generation** | ✅ Yes | SVG/description generation |
| **Case study context** | ✅ Yes | Real-world scenarios |

---

## 📋 Quick Reference: Available Functions

Use these in your `computed` formulas:

| Function | Example | Result |
|----------|---------|--------|
| `gcd(a, b)` | `gcd(12, 8)` | `4` |
| `lcm(a, b)` | `lcm(4, 6)` | `12` |
| `factors(n)` | `factors(12)` | `[1,2,3,4,6,12]` |
| `is_prime(n)` | `is_prime(7)` | `True` |
| `prime_factors(n)` | `prime_factors(12)` | `[2,2,3]` |
| `sqrt(n)` | `sqrt(16)` | `4.0` |
| `abs(n)` | `abs(-5)` | `5` |
| `min(a, b)` | `min(3, 7)` | `3` |
| `max(a, b)` | `max(3, 7)` | `7` |
| `pow(a, b)` | `pow(2, 3)` | `8` |

**Get full list:** `GET /api/admin/templates/universal/functions`

---

## ✅ Checklist Before Publishing

- [ ] Template name is descriptive
- [ ] Concept ID matches knowledge graph
- [ ] Question type is correct (MCQ, A-R, Case Study, etc.)
- [ ] All variables have valid ranges/enums
- [ ] Constraints ensure valid questions
- [ ] At least one correct option marked
- [ ] Wrong options have misconception IDs
- [ ] Solution steps are clear
- [ ] Hints are progressive
- [ ] Difficulty is appropriate (1-5)
- [ ] Tags are added for searchability
- [ ] 10+ test generations pass
- [ ] No duplicate options in any generation

---

## 🆘 Troubleshooting

### "Duplicate options detected"
→ Your formula generates same value for correct and wrong option
→ Add constraints to ensure different values

### "Constraint never satisfied"
→ Your constraints are too strict
→ Expand enum values or relax constraints

### "Formula evaluation failed"
→ Check syntax of computed variable formula
→ Use available functions only (see list above)

### "Schema validation failed"
→ Check JSON format (missing commas, brackets)
→ Use the `/validate` endpoint first

---

## 📞 Support

- **API Docs:** `/api/admin/templates/universal/schema`
- **Function List:** `/api/admin/templates/universal/functions`
- **Preview:** `/api/admin/templates/universal/preview`
- **Validate:** `/api/admin/templates/universal/validate`
