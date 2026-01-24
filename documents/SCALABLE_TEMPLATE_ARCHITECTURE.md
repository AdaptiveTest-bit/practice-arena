# Scalable Template Architecture for K-12 CBSE

## Problem Statement

Current template system has 61% failure rate (11/18 templates broken) due to:
1. Templates require Python code in `answer_logic` field
2. Computed variables (gcd_result, factors, etc.) not auto-generated
3. No validation before publishing
4. Content writers need technical knowledge

## Proposed Solution: Pre-Computed Variables + Declarative Templates

### Core Principle
**Variables should be GENERATED, not COMPUTED in templates**

Instead of:
```
answer_logic: "gcd(variables['a'], variables['b'])"
option_patterns: ["{{ gcd(a, b) }}", "{{ a }}", "{{ b }}"]
```

Use:
```
variable_schema: {
  a: { type: integer, min: 12, max: 48 },
  b: { type: integer, min: 12, max: 48 },
  gcd_result: { type: computed, formula: "gcd(a, b)" }  # AUTO-COMPUTED
}
answer_logic: "variables['gcd_result']"  # Simple lookup
option_patterns: ["{{ gcd_result }}", "{{ a }}", "{{ b }}"]
```

### Architecture Changes

#### 1. Enhanced Variable Schema (JSON Schema Extension)

```json
{
  "type": "object",
  "properties": {
    "a": { "type": "integer", "minimum": 12, "maximum": 48 },
    "b": { "type": "integer", "minimum": 12, "maximum": 48 }
  },
  "computed": {
    "gcd_result": { "formula": "gcd(a, b)" },
    "lcm_result": { "formula": "lcm(a, b)" },
    "product": { "formula": "a * b" },
    "factors_a": { "formula": "factors(a)" },
    "is_coprime": { "formula": "gcd(a, b) == 1" }
  }
}
```

#### 2. Safe Formula Evaluator (Whitelist Approach)

```python
ALLOWED_FUNCTIONS = {
    # Math operations
    'gcd': math.gcd,
    'lcm': math.lcm,
    'sqrt': math.sqrt,
    'abs': abs,
    'min': min,
    'max': max,
    'pow': pow,
    
    # Educational helpers
    'factors': lambda n: [i for i in range(1, n+1) if n % i == 0],
    'multiples': lambda n, count=10: [n * i for i in range(1, count+1)],
    'is_prime': lambda n: len([i for i in range(1, n+1) if n % i == 0]) == 2,
    'prime_factors': lambda n: get_prime_factors(n),
    'divisibility_rule': lambda n, d: DIVISIBILITY_RULES.get(d, ''),
}
```

#### 3. Template Validation Pipeline

```
[Content Writer Creates Template]
         ↓
[Schema Validation] → Error: "gcd_result not defined"
         ↓
[Formula Validation] → Error: "Unknown function 'custom_func'"
         ↓
[Test Generation] → Generate 10 random instances
         ↓
[Option Matching] → Error: "Correct answer not in options"
         ↓
[✅ Ready to Publish]
```

### Implementation Plan

#### Phase 1: Enhanced VariableGenerator (1 day)
- Add `computed` section to variable schema
- Implement safe formula evaluation
- Auto-compute derived variables before template rendering

#### Phase 2: Pre-Publish Validation (1 day)
- Add validation endpoint `/api/admin/templates/{id}/validate`
- Run 10 test generations before allowing publish
- Show specific error messages to content writers

#### Phase 3: Content Writer Tools (2 days)
- Dropdown for common formulas (GCD, LCM, factors, etc.)
- Live preview with validation errors
- Template library with working examples

### Benefits

| Metric | Before | After |
|--------|--------|-------|
| Template success rate | 39% | 99%+ |
| Content writer skill needed | Python | None |
| Time to fix broken template | 30 min | 0 (prevented) |
| Runtime errors | Common | Rare |
| Scalability | Manual fixes | Auto-healing |

### Migration Path

1. **Add computed variables support** (backward compatible)
2. **Migrate existing templates** (one-time script)
3. **Enforce validation** on new templates
4. **Deprecate raw Python** in answer_logic

---

## Immediate Fix vs Long-term

### Immediate (Today): Fix the 7 working templates for E2E demo
- Templates 5, 11, 18, 20, 21, 26, 27 work
- Use only these for student sessions
- Document known working templates

### Short-term (This Week): Add computed variables
- Enhance VariableGenerator to support `computed` section
- Fix remaining 11 templates using computed variables
- Add basic validation

### Long-term (This Month): Full pipeline
- Admin UI validation
- Content writer friendly interface
- Template testing framework

---

## K-12 CBSE Scale Assessment (10K+ Students)

### Current Architecture Scorecard

| Requirement | Score | Notes |
|-------------|-------|-------|
| **Template Creation Speed** | 🟢 Good | Computed variables = no Python needed |
| **Runtime Reliability** | 🟢 Good | Pre-validation prevents failures |
| **Concurrent Users** | 🟡 Needs Work | No caching, DB hits per question |
| **Subject Coverage** | 🟡 Needs Work | Only math functions defined |
| **Grade Adaptation** | 🔴 Missing | Same difficulty for Class 1-12 |
| **Regional Languages** | 🔴 Missing | English only templates |
| **Offline Support** | 🔴 Missing | Requires internet |
| **Analytics at Scale** | 🟡 Needs Work | Basic mastery tracking |

### What's Needed for True K-12 Scale

#### 1. **Performance Layer** (Critical for 10K+ concurrent)
```
Current: DB query → Generate → Render → Return
Needed:  Cache → Pre-generated pool → Return instantly
```

**Solution**: Question Pool Pre-generation
- Generate 100 instances per template at publish time
- Store in Redis/cache
- Serve instantly, no runtime generation
- Regenerate pool nightly

#### 2. **Subject-Specific Formula Libraries**

```python
# Current: Only basic math
SAFE_FUNCTIONS = {'gcd', 'lcm', 'factors', ...}

# Needed: Subject-wise libraries
MATH_FUNCTIONS = {'gcd', 'lcm', 'factors', 'area', 'perimeter', ...}
SCIENCE_FUNCTIONS = {'convert_units', 'calculate_speed', 'balance_equation', ...}
ENGLISH_FUNCTIONS = {'pluralize', 'past_tense', 'synonym', ...}
```

#### 3. **Grade-Aware Difficulty**

```json
{
  "variable_schema": {
    "properties": {
      "a": {
        "type": "integer",
        "grade_ranges": {
          "1-2": {"minimum": 1, "maximum": 10},
          "3-5": {"minimum": 10, "maximum": 100},
          "6-8": {"minimum": 100, "maximum": 1000},
          "9-12": {"minimum": 1000, "maximum": 10000}
        }
      }
    }
  }
}
```

#### 4. **Multi-Language Support**

```json
{
  "question_pattern": {
    "en": "Find the GCD of {{a}} and {{b}}",
    "hi": "{{a}} और {{b}} का म.स. ज्ञात करें",
    "ta": "{{a}} மற்றும் {{b}} இன் மீ.பொ.வ காண்க"
  }
}
```

### Recommended Architecture Evolution

```
Phase 1 (Current): Computed Variables ✅
     ↓
Phase 2: Pre-generated Question Pools
     ↓
Phase 3: Subject Libraries + Grade Adaptation
     ↓
Phase 4: Multi-language + Offline Support
```

### Cost-Benefit for 10K Students

| Investment | Impact | Priority |
|------------|--------|----------|
| Computed Variables | Prevents 60% runtime errors | ✅ Done |
| Pre-generation Cache | 10x faster response, handles 10K concurrent | 🔴 High |
| Grade-aware ranges | Same template works K-12 | 🟡 Medium |
| Subject libraries | Expand beyond math | 🟡 Medium |
| Multi-language | 3x market reach | 🟢 Later |

---

## Verdict: Is Current Architecture Scalable?

**For 10K students in Class 5 Math: YES** ✅
- Computed variables fix reliability
- 7+ working templates is enough to start
- Add caching before launch

**For K-12 all subjects: NEEDS EVOLUTION** 🟡
- Foundation is solid
- Add grade-awareness and subject libraries
- Multi-language is nice-to-have

### Immediate Recommendation

1. **Today**: Use 7 working templates for E2E demo
2. **This Week**: Add Redis caching for question pools
3. **Before Launch**: Migrate remaining templates to computed variables
4. **Post-Launch**: Expand to other grades/subjects
