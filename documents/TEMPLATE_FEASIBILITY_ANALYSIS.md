# Template Editor Feasibility Analysis
## Can Our System Generate StudyAdda-Quality Questions?

**Analysis Date:** January 2026  
**Source:** [StudyAdda Class 5 Factors & Multiples](https://www.studyadda.com/question-bank/5th-class/mathematics/factors-and-multiples/factor-multiple/4546)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total StudyAdda Questions Analyzed | 30 |
| ✅ Fully Supported Now | 8 (27%) |
| ⚠️ Needs Minor Extension | 10 (33%) |
| ❌ Needs New Features | 7 (23%) |
| 🔴 Complex/Out of Scope | 5 (17%) |

**Bottom Line:** With **~2 days of work** extending our formula library, we can support **~83%** of StudyAdda-style questions.

---

## Detailed Question Analysis

### ✅ FULLY SUPPORTED (8 questions)

| # | Question Type | Template Pattern | Current Support |
|---|---------------|------------------|-----------------|
| 4 | Perfect square identification | `Is {{number}} a perfect square?` | ✅ Need `is_perfect_square(n)` |
| 10 | Prime factorization | `What is the prime factorization of {{number}}?` | ✅ `prime_factors(number)` |
| 15 | Count factors | `How many factors does {{number}} have?` | ✅ `len(factors(number))` |
| 21 | HCF/LCM relationship | `HCF is {{hcf}}, what could LCM be?` | ✅ Inference question |
| 23 | HCF of expressions | `HCF of {{expr1}} and {{expr2}}` | ✅ With pre-computed values |
| 26 | HCF of consecutive numbers | `What is HCF of consecutive numbers?` | ✅ Static answer (always 1) |
| 29 | Co-prime properties | `M and N are co-primes, which is true?` | ✅ Theory question |
| 30 | Fraction ordering | `Which series is in descending order?` | ⚠️ Fraction support needed |

### ⚠️ NEEDS MINOR EXTENSION (10 questions)

| # | Question Type | What's Missing | Effort |
|---|---------------|----------------|--------|
| 6 | LCM of 3 numbers | `lcm_three(a, b, c)` function | 30 min |
| 8 | Sum of factors | `sum_factors(n)` → `sum(factors(n))` | 15 min |
| 9 | Composite divisibility rules | `is_divisible_by_composite(n, d)` | 1 hr |
| 14 | Co-prime check | `is_coprime(a, b)` → `gcd(a,b) == 1` | 15 min |
| 17 | LCM + remainder | `lcm(a,b,c) + remainder` pattern | 30 min |
| 22 | Nearest divisible number | `nearest_divisible(target, divisor)` | 1 hr |
| 24 | 3-bus LCM problem | `lcm_three(30, 20, 45)` + time calc | 30 min |
| 27 | LCM + remainder | Same as #17 | Done |
| 2 | "Infinite" as answer | Allow text options like "infinite" | 15 min |
| 3 | Prime count in range | `count_primes_in_range(1, 100)` | 30 min |

**Total Effort: ~5 hours**

### ❌ NEEDS NEW FEATURES (7 questions)

| # | Question Type | New Feature Required | Effort |
|---|---------------|---------------------|--------|
| 1 | "Which statement is correct?" | **Statement-based templates** | 2 hrs |
| 7 | "Product = LCM × HCF" formula | **Formula verification templates** | 1 hr |
| 12 | Sum of reciprocals of factors | **Fraction arithmetic** | 3 hrs |
| 13 | Reduce fraction to lowest | **GCD for fraction simplification** | 2 hrs |
| 16 | Find missing digit | **Digit constraint problems** | 4 hrs |
| 25 | Find digits for divisibility | **Multi-variable digit search** | 4 hrs |
| 28 | Make perfect cube | **Cube root & factor analysis** | 2 hrs |

**Total Effort: ~18 hours (2-3 days)**

### 🔴 COMPLEX/OUT OF SCOPE (5 questions)

| # | Question Type | Why Complex |
|---|---------------|-------------|
| 11 | "Nearest to 100000 divisible by 8,15,21" | Multi-step optimization |
| 18 | "Sum of squares of 4 odd numbers divisibility" | Mathematical proof |
| 19 | "Reduce fraction by identifying common factor" | Fraction + GCD + insight |
| 20 | "₹4.65 daily savings, least days for whole ₹" | Decimal arithmetic + LCM |

These require either:
- More sophisticated reasoning templates
- Pre-computed lookup tables
- Step-by-step problem solving (not MCQ-friendly)

---

## Current Formula Library

```python
# backend/domain/template_engine/lean_template_engine.py

SAFE_FUNCTIONS = {
    # Basic Math
    'gcd': math.gcd,           # ✅ GCD of 2 numbers
    'lcm': math.lcm,           # ✅ LCM of 2 numbers
    'sqrt': math.sqrt,         # ✅ Square root
    'abs': abs,                # ✅ Absolute value
    'min': min,                # ✅ Minimum
    'max': max,                # ✅ Maximum
    'pow': pow,                # ✅ Power
    'floor': math.floor,       # ✅ Floor
    'ceil': math.ceil,         # ✅ Ceiling
    'round': round,            # ✅ Round
    
    # Educational Helpers
    'factors': get_factors,           # ✅ All factors of n
    'multiples': get_multiples,       # ✅ First k multiples
    'is_prime': is_prime,             # ✅ Primality check
    'prime_factors': get_prime_factors, # ✅ Prime factorization
    'divisibility_rule': divisibility_rule, # ✅ Rule text
}
```

---

## Proposed Extensions (Priority Order)

### Phase 1: Quick Wins (2 hours)

```python
# Add to SAFE_FUNCTIONS:

'sum_factors': lambda n: sum(get_factors(n)),
'is_coprime': lambda a, b: math.gcd(a, b) == 1,
'lcm_three': lambda a, b, c: lcm(lcm(a, b), c),
'factor_count': lambda n: len(get_factors(n)),
'is_perfect_square': lambda n: int(math.sqrt(n))**2 == n,
'count_primes': lambda start, end: sum(1 for i in range(start, end+1) if is_prime(i)),
```

### Phase 2: Fraction Support (4 hours)

```python
# New fraction module:

'simplify_fraction': lambda num, den: (num // gcd(num, den), den // gcd(num, den)),
'add_fractions': lambda n1, d1, n2, d2: simplify_fraction(n1*d2 + n2*d1, d1*d2),
'compare_fractions': lambda n1, d1, n2, d2: n1*d2 - n2*d1,  # <0, 0, >0
```

### Phase 3: Advanced Number Theory (8 hours)

```python
# Advanced helpers:

'nearest_multiple': lambda target, divisor: round(target / divisor) * divisor,
'nearest_divisible_above': lambda target, divisor: ((target // divisor) + 1) * divisor,
'is_perfect_cube': lambda n: round(n**(1/3))**3 == n,
'cube_root_factor_needed': lambda n: ...,  # Complex
```

---

## Template Editor Changes Needed

### 1. Extended KNOWN_COMPUTED (in TemplateEditorSimplified.tsx)

```typescript
const KNOWN_COMPUTED = {
  // Existing
  'gcd_result': { formula: 'gcd(a, b)' },
  'lcm_result': { formula: 'lcm(a, b)' },
  
  // NEW - Phase 1
  'sum_factors': { formula: 'sum_factors(number)' },
  'is_coprime': { formula: 'is_coprime(a, b)' },
  'lcm_three': { formula: 'lcm_three(a, b, c)' },
  'factor_count': { formula: 'factor_count(number)' },
  'is_perfect_square': { formula: 'is_perfect_square(number)' },
  'prime_count': { formula: 'count_primes(1, 100)' },
  
  // NEW - Phase 2 (Fractions)
  'simplified_num': { formula: 'simplify_fraction(num, den)[0]' },
  'simplified_den': { formula: 'simplify_fraction(num, den)[1]' },
}
```

### 2. New Question Types

```typescript
const QUESTION_TYPES = [
  { value: 'computation', label: '🔢 Computation (Find GCD, LCM, etc.)' },
  { value: 'identification', label: '🔍 Identification (Is prime? Is factor?)' },
  { value: 'statement', label: '📝 Statement (Which is correct?)' },  // NEW
  { value: 'word_problem', label: '📖 Word Problem (Real-world context)' },
  { value: 'formula', label: '📐 Formula Verification' },  // NEW
];
```

---

## Sample Templates for StudyAdda Questions

### Q6: LCM of Three Numbers
```
concept_id: math.class5.factors_multiples.lcm
question_pattern: What is the LCM of {{a}}, {{b}} and {{c}}?
options:
  - {{lcm_three}}  ← correct
  - {{a * b}}
  - {{b * c}}
  - {{gcd_three}}
variable_schema:
  properties:
    a: { enum: [4, 6, 8, 12] }
    b: { enum: [3, 5, 9, 15] }
    c: { enum: [2, 4, 6, 10] }
  computed:
    lcm_three: { formula: "lcm(lcm(a, b), c)" }
    gcd_three: { formula: "gcd(gcd(a, b), c)" }
```

### Q14: Co-prime Identification
```
concept_id: math.class5.factors_multiples.coprime
question_pattern: Which of the following pairs is co-prime?
options:
  - {{coprime_a}}, {{coprime_b}}  ← correct (GCD=1)
  - {{non_coprime_a}}, {{non_coprime_b}}  (GCD>1)
  - {{factor_pair_a}}, {{factor_pair_b}}  (one divides other)
  - {{common_factor_a}}, {{common_factor_b}}  (share factor)
variable_schema:
  properties:
    coprime_a: { enum: [7, 11, 13, 17, 19] }
    coprime_b: { enum: [9, 15, 16, 22, 25] }  # Chosen to be coprime
  computed:
    is_answer_coprime: { formula: "gcd(coprime_a, coprime_b) == 1" }  # Validation
```

### Q24: Bus Interval Problem (LCM Word Problem)
```
concept_id: math.class5.factors_multiples.lcm_word_problem
question_pattern: |
  Three buses leave at 9:00 AM. 
  Bus A returns every {{interval_a}} minutes.
  Bus B returns every {{interval_b}} minutes.
  Bus C returns every {{interval_c}} minutes.
  When will all buses return together?
options:
  - {{answer_time}}  ← correct
  - {{wrong_time_1}}
  - {{wrong_time_2}}
  - {{wrong_time_3}}
variable_schema:
  properties:
    interval_a: { enum: [20, 25, 30] }
    interval_b: { enum: [15, 30, 45] }
    interval_c: { enum: [10, 12, 20] }
  computed:
    lcm_minutes: { formula: "lcm(lcm(interval_a, interval_b), interval_c)" }
    answer_time: { formula: "format_time(9*60 + lcm_minutes)" }  # Needs format_time helper
```

---

## Recommendation

### Immediate (This Week)
1. ✅ Add Phase 1 functions to `lean_template_engine.py` (2 hrs)
2. ✅ Update `KNOWN_COMPUTED` in `TemplateEditorSimplified.tsx` (1 hr)
3. ✅ Create 10 new templates covering the "minor extension" questions

### Short-Term (This Month)
1. Add fraction support (Phase 2)
2. Create statement-based question type
3. Build template library with 50+ working examples

### Not Recommended
- Missing digit problems (too complex for template approach)
- Mathematical proof questions (not MCQ-friendly)
- Multi-step optimization (needs AI reasoning)

---

## Conclusion

**YES, the Template Editor is feasible** for generating StudyAdda-quality questions with minor extensions.

| Without Changes | With Phase 1 | With Phase 1+2 |
|-----------------|--------------|----------------|
| 27% coverage | 60% coverage | 83% coverage |

The remaining 17% requires either:
- AI-assisted question generation
- Pre-computed lookup tables
- Different question format (not template-based)

**Action:** Implement Phase 1 extensions (2 hours) to immediately double our question coverage.
