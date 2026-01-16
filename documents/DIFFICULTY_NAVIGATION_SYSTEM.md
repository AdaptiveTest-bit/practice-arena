# Difficulty Navigation & Enforcement System

## Executive Summary

This document defines **how difficulty is navigated, tagged, and enforced** across the pre-generation pipeline to ensure pedagogical consistency between:
1. **Content Rules** (blueprints, taxonomy, graphs)
2. **Generation Logic** (Python/SymPy + LLM)
3. **Validation** (rubrics)
4. **Runtime Selection** (adaptive engine)

---

## 1. Current State Analysis: The Gap

### 1.1 What's Defined (YAML Rules)

| Source | Difficulty Info | Status |
|--------|-----------------|--------|
| `blueprints/factors_multiples.yaml` | `difficulty_mix: {"1": 0.6, "2": 0.4}` per concept | ✅ Defined |
| `graphs/factors_multiples.yaml` | `difficulty_default: 1-3` per concept | ✅ Defined |
| `taxonomy/math.yaml` | `difficulty_range: [1, 2]` per concept | ✅ Defined |

### 1.2 What's Implemented (Python Generator)

```python
# Current: factors_multiples.py line ~333
hybrid_difficulty = random.choice([
    HybridDifficultyLevel.EASY,    # Maps to 1
    HybridDifficultyLevel.MEDIUM,  # Maps to 2  
    HybridDifficultyLevel.HARD,    # Maps to 3
])

# Problem: This is RANDOM, not YAML-driven!
```

### 1.3 The Gap

| What Should Happen | What Actually Happens |
|--------------------|----------------------|
| `divisibility` → Difficulty 1-2 only (per taxonomy) | Random 1-3 |
| `gcd` → Difficulty 2-3 (per taxonomy) | Random 1-3 |
| `assertion_reason` → Difficulty 3-4 (per taxonomy) | Hardcoded 3 |

**Root Cause**: YAML configs are NOT WIRED to generators.

---

## 2. Difficulty Definition Matrix

### 2.1 Unified Difficulty Scale (1-5)

| Level | Name | Cognitive Load | Number Complexity | Steps | Time |
|-------|------|----------------|-------------------|-------|------|
| **1** | Foundational | Single operation | 1-digit, small 2-digit | 1-2 | <30s |
| **2** | Developing | 2 operations | 2-digit, simple | 2-3 | 30-60s |
| **3** | Proficient | 3+ operations | 2-digit, complex | 3-4 | 60-90s |
| **4** | Advanced | Multi-step reasoning | 3-digit, edge cases | 4-5 | 90-120s |
| **5** | Expert | Abstract/proof | Large numbers, proofs | 5+ | 2+ min |

### 2.2 Concept-Specific Difficulty Rules

From `taxonomy/math.yaml` + `graphs/factors_multiples.yaml`:

| Concept | Allowed Difficulty | Default | Bloom Targets |
|---------|-------------------|---------|---------------|
| `divisibility` | 1-2 | 1 | REMEMBER |
| `prime_composite` | 1-2 | 1 | REMEMBER, UNDERSTAND |
| `factors` | 1-3 | 2 | UNDERSTAND, APPLY |
| `multiples` | 1-3 | 2 | UNDERSTAND, APPLY |
| `factor_pairs` | 2-3 | 2 | UNDERSTAND |
| `gcd` | 2-3 | 2 | APPLY |
| `lcm` | 2-3 | 2 | APPLY |
| `prime_factorization` | 2-3 | 2 | APPLY |
| `word_problem` | 2-4 | 3 | APPLY, ANALYZE |
| `assertion_reason` | 3-4 | 3 | ANALYZE |
| `error_analysis` | 3-4 | 3 | EVALUATE |

### 2.3 Bloom × Difficulty Validity Matrix

Not all Bloom×Difficulty combinations are pedagogically valid:

```
              Difficulty
Bloom        1    2    3    4    5
─────────────────────────────────────
REMEMBER     ✅   ✅   ⚠️   ❌   ❌
UNDERSTAND   ✅   ✅   ✅   ⚠️   ❌
APPLY        ⚠️   ✅   ✅   ✅   ⚠️
ANALYZE      ❌   ⚠️   ✅   ✅   ✅
EVALUATE     ❌   ❌   ✅   ✅   ✅
CREATE       ❌   ❌   ⚠️   ✅   ✅

✅ = Valid    ⚠️ = Rare/Edge case    ❌ = Invalid
```

---

## 3. Parameter Rules: What Makes Difficulty

### 3.1 Factors Concept

```yaml
factors:
  difficulty_1:
    number_range: [6, 20]
    exclude: [primes]  # Primes have only 2 factors - too easy
    factor_count: [3, 6]  # 3-6 factors
    bloom: UNDERSTAND
    
  difficulty_2:
    number_range: [20, 50]
    factor_count: [4, 10]
    bloom: [UNDERSTAND, APPLY]
    
  difficulty_3:
    number_range: [50, 100]
    factor_count: [6, 12]
    include_perfect_squares: true
    bloom: APPLY
```

### 3.2 GCD Concept

```yaml
gcd:
  difficulty_2:
    number_range_a: [10, 30]
    number_range_b: [10, 30]
    gcd_range: [2, 10]  # Ensure non-trivial GCD
    method_hint: "factor_listing"
    bloom: APPLY
    
  difficulty_3:
    number_range_a: [30, 100]
    number_range_b: [30, 100]
    gcd_range: [2, 20]
    allow_coprime: false  # GCD=1 cases are tricky
    method_hint: "prime_factorization"
    bloom: APPLY
    
  difficulty_4:
    number_range_a: [50, 200]
    number_range_b: [50, 200]
    allow_coprime: true
    require_euclidean: true  # Must use Euclidean algorithm
    bloom: ANALYZE
```

### 3.3 Word Problem Concept

```yaml
word_problem:
  difficulty_2:
    scenario_complexity: "single_concept"  # Only GCD OR LCM
    numbers_given: 2
    context: ["grouping", "scheduling"]
    bloom: APPLY
    
  difficulty_3:
    scenario_complexity: "multi_step"  # GCD + LCM in sequence
    numbers_given: 2-3
    context: ["arrangement", "time_scheduling", "distance"]
    requires_interpretation: true
    bloom: [APPLY, ANALYZE]
    
  difficulty_4:
    scenario_complexity: "nested"  # Hidden conditions
    numbers_given: 3+
    requires_constraint_extraction: true
    multiple_valid_approaches: true
    bloom: ANALYZE
```

### 3.4 Divisibility Concept

```yaml
divisibility:
  difficulty_1:
    divisors: [2, 5, 10]  # Easy rules
    number_range: [10, 100]
    question_type: "is_divisible"  # Yes/No
    bloom: REMEMBER
    
  difficulty_2:
    divisors: [3, 9]  # Sum of digits rules
    number_range: [100, 999]
    question_type: "which_divisible"  # Multiple choice
    bloom: [REMEMBER, UNDERSTAND]
```

---

## 4. Enforcement Architecture

### 4.1 Three-Layer Validation

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: GENERATION                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Blueprint   │───>│ Difficulty  │───>│ Parameter   │      │
│  │ YAML        │    │ Selector    │    │ Generator   │      │
│  │(what to gen)│    │(pick level) │    │(gen numbers)│      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 2: VALIDATION                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Rubric      │───>│ Difficulty  │───>│ Bloom       │      │
│  │ Validator   │    │ Validator   │    │ Validator   │      │
│  │(structure)  │    │(in range?)  │    │(matches?)   │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 3: RUNTIME                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Student     │───>│ Adaptive    │───>│ Bank        │      │
│  │ Mastery     │    │ Selector    │    │ Query       │      │
│  │(current lvl)│    │(target diff)│    │(fetch Q)    │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Generation-Time Enforcement

```python
# NEW: DifficultyEnforcer class
class DifficultyEnforcer:
    """Ensures generated questions match content rules."""
    
    def __init__(self, taxonomy_path: str, blueprint_path: str):
        self.taxonomy = self._load_yaml(taxonomy_path)
        self.blueprint = self._load_yaml(blueprint_path)
        
    def get_allowed_range(self, concept_key: str) -> tuple[int, int]:
        """Get allowed difficulty range from taxonomy."""
        for concept in self.taxonomy['concepts']:
            if concept['id'].endswith(concept_key):
                return tuple(concept['difficulty_range'])
        raise ValueError(f"Unknown concept: {concept_key}")
    
    def get_target_distribution(self, concept_key: str) -> dict:
        """Get target difficulty distribution from blueprint."""
        concept_id = f"math.class5.factors_multiples.{concept_key}"
        targets = self.blueprint['coverage_targets']['by_concept_id']
        if concept_id in targets:
            return targets[concept_id]['difficulty_mix']
        return {"2": 1.0}  # Default to medium
    
    def select_difficulty(self, concept_key: str, 
                         student_level: int = None) -> int:
        """Select appropriate difficulty respecting constraints."""
        min_d, max_d = self.get_allowed_range(concept_key)
        distribution = self.get_target_distribution(concept_key)
        
        # If student level provided, constrain further
        if student_level:
            max_d = min(max_d, student_level + 1)
            min_d = max(min_d, student_level - 1)
        
        # Weighted random selection from distribution
        valid_levels = [int(k) for k in distribution.keys() 
                       if min_d <= int(k) <= max_d]
        weights = [float(distribution.get(str(d), 0)) for d in valid_levels]
        
        if not valid_levels:
            return min_d  # Fallback
            
        return random.choices(valid_levels, weights=weights)[0]
    
    def validate_difficulty(self, concept_key: str, 
                           difficulty: int, 
                           bloom_level: str) -> tuple[bool, str]:
        """Validate difficulty is appropriate for concept and bloom."""
        min_d, max_d = self.get_allowed_range(concept_key)
        
        # Check difficulty range
        if not (min_d <= difficulty <= max_d):
            return False, f"Difficulty {difficulty} outside range [{min_d}, {max_d}] for {concept_key}"
        
        # Check bloom compatibility
        bloom_map = {
            'REMEMBER': (1, 2),
            'UNDERSTAND': (1, 3),
            'APPLY': (2, 4),
            'ANALYZE': (3, 5),
            'EVALUATE': (3, 5),
        }
        bloom_min, bloom_max = bloom_map.get(bloom_level, (1, 5))
        if not (bloom_min <= difficulty <= bloom_max):
            return False, f"Difficulty {difficulty} incompatible with {bloom_level} (expected {bloom_min}-{bloom_max})"
        
        return True, "Valid"
```

### 4.3 Parameter Generator with Difficulty

```python
# NEW: DifficultyAwareParameterGenerator
class FactorsParameterGenerator:
    """Generate parameters for factors concept based on difficulty."""
    
    DIFFICULTY_RULES = {
        1: {
            'number_range': (6, 20),
            'exclude_primes': True,
            'target_factor_count': (3, 6),
        },
        2: {
            'number_range': (20, 50),
            'exclude_primes': False,
            'target_factor_count': (4, 10),
        },
        3: {
            'number_range': (50, 100),
            'exclude_primes': False,
            'target_factor_count': (6, 12),
            'prefer_perfect_squares': True,
        },
    }
    
    def generate(self, difficulty: int) -> dict:
        """Generate number and factors for given difficulty."""
        rules = self.DIFFICULTY_RULES.get(difficulty, self.DIFFICULTY_RULES[2])
        
        min_n, max_n = rules['number_range']
        min_factors, max_factors = rules['target_factor_count']
        
        # Generate candidate numbers
        candidates = []
        for n in range(min_n, max_n + 1):
            factors = self._get_factors(n)
            factor_count = len(factors)
            
            if rules.get('exclude_primes') and factor_count == 2:
                continue
            if not (min_factors <= factor_count <= max_factors):
                continue
            if rules.get('prefer_perfect_squares') and not self._is_perfect_square(n):
                continue  # Soft preference
                
            candidates.append((n, factors))
        
        if not candidates:
            # Fallback: relax constraints
            candidates = [(n, self._get_factors(n)) 
                         for n in range(min_n, max_n + 1)]
        
        number, factors = random.choice(candidates)
        return {
            'target_number': number,
            'factors': factors,
            'difficulty': difficulty,
            'factor_count': len(factors),
        }
    
    def _get_factors(self, n: int) -> list:
        return sorted([i for i in range(1, n + 1) if n % i == 0])
    
    def _is_perfect_square(self, n: int) -> bool:
        return int(n ** 0.5) ** 2 == n


class GCDParameterGenerator:
    """Generate parameters for GCD concept based on difficulty."""
    
    DIFFICULTY_RULES = {
        2: {
            'range_a': (10, 30),
            'range_b': (10, 30),
            'min_gcd': 2,
            'allow_coprime': False,
        },
        3: {
            'range_a': (30, 100),
            'range_b': (30, 100),
            'min_gcd': 2,
            'allow_coprime': False,
        },
        4: {
            'range_a': (50, 200),
            'range_b': (50, 200),
            'min_gcd': 1,
            'allow_coprime': True,
        },
    }
    
    def generate(self, difficulty: int) -> dict:
        rules = self.DIFFICULTY_RULES.get(difficulty, self.DIFFICULTY_RULES[2])
        
        # Generate pairs with desired GCD properties
        for _ in range(100):  # Max attempts
            a = random.randint(*rules['range_a'])
            b = random.randint(*rules['range_b'])
            gcd_val = math.gcd(a, b)
            
            if gcd_val < rules['min_gcd']:
                continue
            if gcd_val == 1 and not rules['allow_coprime']:
                continue
                
            return {
                'a': a,
                'b': b,
                'gcd': gcd_val,
                'difficulty': difficulty,
            }
        
        # Fallback: construct a valid pair
        gcd_target = random.randint(rules['min_gcd'], 10)
        a = gcd_target * random.randint(2, 5)
        b = gcd_target * random.randint(2, 5)
        return {'a': a, 'b': b, 'gcd': math.gcd(a, b), 'difficulty': difficulty}
```

---

## 5. Validation Rules (Rubric Extension)

### 5.1 Add to `rubrics/question_quality.yaml`

```yaml
# ==================== DIFFICULTY VALIDATION ====================
difficulty_rules:
  # Per-concept allowed ranges (from taxonomy)
  concept_ranges:
    divisibility: [1, 2]
    prime_composite: [1, 2]
    factors: [1, 3]
    multiples: [1, 3]
    factor_pairs: [2, 3]
    gcd: [2, 3]
    lcm: [2, 3]
    prime_factorization: [2, 3]
    word_problem: [2, 4]
    assertion_reason: [3, 4]
    error_analysis: [3, 4]
  
  # Bloom compatibility matrix
  bloom_difficulty_matrix:
    REMEMBER: [1, 2]
    UNDERSTAND: [1, 3]
    APPLY: [2, 4]
    ANALYZE: [3, 5]
    EVALUATE: [3, 5]
  
  # Validation checks
  checks:
    - name: difficulty_in_concept_range
      rule: |
        min_d, max_d = concept_ranges[meta.concept_key]
        min_d <= meta.difficulty <= max_d
      message: "Difficulty {difficulty} outside allowed range for {concept_key}"
      
    - name: bloom_difficulty_compatible
      rule: |
        bloom_min, bloom_max = bloom_difficulty_matrix[meta.bloom_level]
        bloom_min <= meta.difficulty <= bloom_max
      message: "Difficulty {difficulty} incompatible with {bloom_level}"
      
    - name: parameter_matches_difficulty
      rule: |
        # For factors: number should be in expected range
        if meta.concept_key == 'factors':
          difficulty_ranges = {1: (6, 20), 2: (20, 50), 3: (50, 100)}
          min_n, max_n = difficulty_ranges[meta.difficulty]
          min_n <= parameters.target_number <= max_n
      message: "Number {target_number} too easy/hard for difficulty {difficulty}"
```

### 5.2 Automated Validation Code

```python
class DifficultyValidator:
    """Validate questions against difficulty rules."""
    
    def __init__(self, rubric_path: str):
        self.rubric = self._load_yaml(rubric_path)
        self.concept_ranges = self.rubric['difficulty_rules']['concept_ranges']
        self.bloom_matrix = self.rubric['difficulty_rules']['bloom_difficulty_matrix']
    
    def validate(self, question: Question) -> list[str]:
        """Return list of validation errors (empty if valid)."""
        errors = []
        meta = question.meta
        
        # Check 1: Difficulty in concept range
        concept_key = meta.get('concept_key')
        difficulty = meta.get('difficulty')
        
        if concept_key in self.concept_ranges:
            min_d, max_d = self.concept_ranges[concept_key]
            if not (min_d <= difficulty <= max_d):
                errors.append(
                    f"Difficulty {difficulty} outside range [{min_d}, {max_d}] "
                    f"for concept '{concept_key}'"
                )
        
        # Check 2: Bloom compatibility
        bloom_level = meta.get('bloom_level')
        if bloom_level in self.bloom_matrix:
            bloom_min, bloom_max = self.bloom_matrix[bloom_level]
            if not (bloom_min <= difficulty <= bloom_max):
                errors.append(
                    f"Difficulty {difficulty} incompatible with Bloom level "
                    f"'{bloom_level}' (expected {bloom_min}-{bloom_max})"
                )
        
        # Check 3: Parameter sanity (concept-specific)
        if concept_key == 'factors':
            target_number = self._extract_target_number(question)
            expected_ranges = {1: (6, 20), 2: (20, 50), 3: (50, 100)}
            if difficulty in expected_ranges:
                min_n, max_n = expected_ranges[difficulty]
                if not (min_n <= target_number <= max_n):
                    errors.append(
                        f"Target number {target_number} outside expected range "
                        f"[{min_n}, {max_n}] for difficulty {difficulty}"
                    )
        
        return errors
    
    def _extract_target_number(self, question: Question) -> int:
        """Extract target number from question text."""
        import re
        match = re.search(r'factors of (\d+)', question.question_text)
        return int(match.group(1)) if match else 0
```

---

## 6. Pre-Generation Pipeline with Difficulty

### 6.1 Generation Batch Script

```python
# tools/generate_bank.py

class QuestionBankGenerator:
    """Generate question bank with difficulty enforcement."""
    
    def __init__(self, chapter_id: str, grade: int):
        self.chapter_id = chapter_id
        self.grade = grade
        
        # Load content rules
        base_path = Path("config/content")
        self.taxonomy = self._load_yaml(base_path / "taxonomy/math.yaml")
        self.blueprint = self._load_yaml(
            base_path / f"blueprints/math/class{grade}/{chapter_id}.yaml"
        )
        self.rubric = self._load_yaml(base_path / "rubrics/question_quality.yaml")
        
        # Initialize components
        self.enforcer = DifficultyEnforcer(self.taxonomy, self.blueprint)
        self.validator = DifficultyValidator(self.rubric)
        self.param_generators = {
            'factors': FactorsParameterGenerator(),
            'gcd': GCDParameterGenerator(),
            'lcm': LCMParameterGenerator(),
            # ... more
        }
    
    def generate_for_concept(self, concept_key: str, count: int) -> list[Question]:
        """Generate questions for a concept following content rules."""
        
        # Get distribution from blueprint
        concept_id = f"math.class{self.grade}.{self.chapter_id}.{concept_key}"
        config = self.blueprint['coverage_targets']['by_concept_id'].get(concept_id, {})
        
        difficulty_mix = config.get('difficulty_mix', {"2": 1.0})
        bloom_mix = config.get('bloom_mix', {"UNDERSTAND": 1.0})
        
        questions = []
        
        # Calculate how many questions per difficulty
        for diff_str, diff_ratio in difficulty_mix.items():
            difficulty = int(diff_str)
            diff_count = int(count * diff_ratio)
            
            # Validate difficulty is allowed
            is_valid, msg = self.enforcer.validate_difficulty(
                concept_key, difficulty, list(bloom_mix.keys())[0]
            )
            if not is_valid:
                print(f"Warning: {msg}, skipping difficulty {difficulty}")
                continue
            
            for _ in range(diff_count):
                # Generate parameters
                params = self.param_generators[concept_key].generate(difficulty)
                
                # Select bloom level from mix
                bloom_level = self._select_bloom(bloom_mix)
                
                # Generate question
                question = self._generate_question(
                    concept_key, params, difficulty, bloom_level
                )
                
                # Validate
                errors = self.validator.validate(question)
                if errors:
                    print(f"Validation failed: {errors}")
                    continue  # Skip invalid questions
                
                questions.append(question)
        
        return questions
    
    def generate_full_bank(self) -> dict:
        """Generate complete question bank for chapter."""
        bank = {
            'version': 1,
            'chapter_id': self.chapter_id,
            'grade': self.grade,
            'generated_at': datetime.now().isoformat(),
            'questions': [],
            'stats': {}
        }
        
        # Get all concepts from taxonomy
        concepts = [c['id'].split('.')[-1] for c in self.taxonomy['concepts']
                   if self.chapter_id in c['id']]
        
        for concept_key in concepts:
            # Get target count from blueprint
            target = self.blueprint['coverage_targets']['by_concept_id'].get(
                f"math.class{self.grade}.{self.chapter_id}.{concept_key}", {}
            )
            count = target.get('min_per_week', 10) * 10  # Generate 10 weeks worth
            
            print(f"Generating {count} questions for {concept_key}...")
            questions = self.generate_for_concept(concept_key, count)
            bank['questions'].extend(questions)
            bank['stats'][concept_key] = len(questions)
        
        return bank
```

### 6.2 Coverage Report

After generation, validate coverage matches blueprint:

```python
def generate_coverage_report(bank: dict, blueprint: dict) -> dict:
    """Check if generated bank meets blueprint coverage targets."""
    
    report = {
        'meets_targets': True,
        'concepts': {}
    }
    
    for concept_id, target in blueprint['coverage_targets']['by_concept_id'].items():
        concept_key = concept_id.split('.')[-1]
        
        # Count questions by difficulty
        questions = [q for q in bank['questions'] 
                    if q['meta']['concept_key'] == concept_key]
        
        difficulty_counts = {}
        for q in questions:
            d = str(q['meta']['difficulty'])
            difficulty_counts[d] = difficulty_counts.get(d, 0) + 1
        
        # Check against target mix
        total = len(questions)
        target_mix = target.get('difficulty_mix', {})
        
        concept_report = {
            'total': total,
            'target_min': target.get('min_per_week', 0) * 10,
            'by_difficulty': {},
            'meets_target': True
        }
        
        for diff_str, target_ratio in target_mix.items():
            actual_count = difficulty_counts.get(diff_str, 0)
            expected_count = int(total * target_ratio)
            
            concept_report['by_difficulty'][diff_str] = {
                'actual': actual_count,
                'expected': expected_count,
                'ratio_actual': actual_count / total if total else 0,
                'ratio_target': target_ratio
            }
            
            # Check if within 10% tolerance
            if total > 0 and abs(actual_count/total - target_ratio) > 0.1:
                concept_report['meets_target'] = False
                report['meets_targets'] = False
        
        report['concepts'][concept_key] = concept_report
    
    return report
```

---

## 7. Runtime Selection with Difficulty

### 7.1 Adaptive Selector Integration

```python
class AdaptiveQuestionSelector:
    """Select questions from bank based on student level and content rules."""
    
    def __init__(self, bank: QuestionBank, blueprint: dict):
        self.bank = bank
        self.blueprint = blueprint
    
    def select(self, 
               concept_key: str,
               student_mastery: float,  # 0.0 - 1.0
               recent_performance: list[bool]) -> Question:
        """Select appropriate question based on student state."""
        
        # Determine target difficulty from mastery
        target_difficulty = self._mastery_to_difficulty(student_mastery)
        
        # Adjust based on recent performance (last 3 questions)
        if len(recent_performance) >= 3:
            if all(recent_performance[-3:]):  # All correct → increase
                target_difficulty = min(target_difficulty + 1, 5)
            elif not any(recent_performance[-3:]):  # All wrong → decrease
                target_difficulty = max(target_difficulty - 1, 1)
        
        # Constrain to concept's allowed range
        concept_config = self._get_concept_config(concept_key)
        allowed_range = concept_config.get('difficulty_range', [1, 5])
        target_difficulty = max(allowed_range[0], 
                               min(allowed_range[1], target_difficulty))
        
        # Query bank
        candidates = self.bank.query(
            concept_key=concept_key,
            difficulty=target_difficulty,
            exclude_seen=True  # Don't repeat questions
        )
        
        if not candidates:
            # Fallback: expand difficulty range
            candidates = self.bank.query(
                concept_key=concept_key,
                difficulty_range=(target_difficulty - 1, target_difficulty + 1)
            )
        
        return random.choice(candidates) if candidates else None
    
    def _mastery_to_difficulty(self, mastery: float) -> int:
        """Convert mastery score to target difficulty."""
        if mastery < 0.3:
            return 1
        elif mastery < 0.5:
            return 2
        elif mastery < 0.7:
            return 3
        elif mastery < 0.9:
            return 4
        else:
            return 5
    
    def _get_concept_config(self, concept_key: str) -> dict:
        """Get concept configuration from blueprint."""
        concept_id = f"math.class5.factors_multiples.{concept_key}"
        return self.blueprint['coverage_targets']['by_concept_id'].get(concept_id, {})
```

---

## 8. Summary: Difficulty Enforcement Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                          PRE-GENERATION                               │
│                                                                       │
│  taxonomy.yaml ──┐                                                    │
│  (allowed range) │                                                    │
│                  ├──> DifficultyEnforcer ──> select_difficulty()     │
│  blueprint.yaml ─┘                               │                    │
│  (target mix)                                    ▼                    │
│                                          ParameterGenerator           │
│                                          (difficulty-aware)           │
│                                                  │                    │
│                                                  ▼                    │
│                                           generate_question()         │
│                                                  │                    │
│  rubrics.yaml ────────────────────────> DifficultyValidator          │
│  (validation rules)                             │                    │
│                                                 ▼                    │
│                                    [Valid Question] ──> Bank         │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                            RUNTIME                                    │
│                                                                       │
│  Student State ──┐                                                    │
│  (mastery, perf) │                                                    │
│                  ├──> AdaptiveSelector ──> target_difficulty         │
│  blueprint.yaml ─┘                              │                    │
│  (allowed range)                                ▼                    │
│                                          Bank.query(difficulty)      │
│                                                  │                    │
│                                                  ▼                    │
│                                           [Question]                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 9. Implementation Checklist

### Phase 1: Wire YAML to Generators
- [ ] Create `DifficultyEnforcer` class
- [ ] Create per-concept `ParameterGenerator` classes
- [ ] Add `difficulty_rules` section to `rubrics/question_quality.yaml`
- [ ] Create `DifficultyValidator` class

### Phase 2: Update Generators
- [ ] Modify `factors_multiples.py` to use `DifficultyEnforcer`
- [ ] Replace `random.choice([EASY, MEDIUM, HARD])` with `enforcer.select_difficulty()`
- [ ] Add difficulty-aware parameter generation

### Phase 3: Validation Pipeline
- [ ] Add difficulty validation to pre-generation pipeline
- [ ] Create coverage report generator
- [ ] Add automated tests for difficulty constraints

### Phase 4: Runtime Integration
- [ ] Update `AdaptiveQuestionSelector` to query bank by difficulty
- [ ] Add difficulty-based progression tracking
- [ ] Implement fallback to on-the-fly generation with difficulty constraints

---

## 10. Example: End-to-End Flow

**Input**: Generate question for `gcd` concept, student mastery = 0.6

1. **DifficultyEnforcer.select_difficulty("gcd", student_level=3)**
   - Taxonomy says: `gcd` → difficulty_range [2, 3]
   - Blueprint says: `difficulty_mix: {"2": 0.5, "3": 0.5}`
   - Student level suggests: difficulty 3
   - **Selected**: difficulty = 3

2. **GCDParameterGenerator.generate(difficulty=3)**
   - Rules: range_a=(30, 100), range_b=(30, 100), min_gcd=2
   - Generated: a=48, b=72, gcd=24
   - **Output**: `{a: 48, b: 72, gcd: 24, difficulty: 3}`

3. **Generate Question**
   - Question: "Find the GCD of 48 and 72"
   - Meta: `{concept_key: "gcd", difficulty: 3, bloom_level: "APPLY"}`

4. **DifficultyValidator.validate(question)**
   - Check 1: difficulty 3 in [2, 3] for gcd ✅
   - Check 2: difficulty 3 compatible with APPLY (2-4) ✅
   - Check 3: numbers 48, 72 in range (30, 100) ✅
   - **Result**: VALID

5. **Store in Bank**
   - Tagged: `gcd_d3_bAPPLY_001`

6. **Runtime Selection**
   - Student requests gcd question
   - Mastery 0.6 → target difficulty 3
   - Bank query: `concept=gcd, difficulty=3`
   - **Returns**: Our question!
