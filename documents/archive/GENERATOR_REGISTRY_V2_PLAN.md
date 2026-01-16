# Generator Registry v2: End-to-End Architecture Plan

**Version:** 2.0  
**Date:** January 2025  
**Status:** Architecture Discussion  
**Central Example:** `factors_multiples` (Class 5 Math, Chapter 6)

---

## Executive Summary

This document presents a **revised Generator Registry Architecture** based on our discussions:

1. **DUMB Generators**: Single-concept, parameterized Python functions that produce question variations
2. **YAML-Driven Orchestration**: Cross-concept logic, difficulty progression, and session management live in YAML configs (NOT embedded in generators)
3. **LLM Role**: One-time code generation for generators + YAML validation, NOT runtime question generation

### The Key Insight

```
CURRENT: 2000-line monolithic FactorsMultiplesIntegrated class with embedded logic
NEW:     11 simple generators + 3 YAML files + 1 smart orchestrator
```

---

## 1. Current State Analysis: `factors_multiples`

### 1.1 What We Have Today

```
backend/
├── domain/content_generation/generators/
│   └── factors_multiples.py         # 2015 lines - MONOLITHIC
│
├── config/content/
│   ├── taxonomy/math.yaml           # Concept definitions (11 concepts)
│   ├── blueprints/math/class5/factors_multiples.yaml  # Coverage rules
│   └── graphs/math/class5/factors_multiples.yaml      # Prerequisite edges
```

**Current Generator (`factors_multiples.py`):**
```python
class FactorsMultiplesIntegrated(BaseChapterStrategy):
    """2015 lines of code containing:
    - 11 concept generators (_generate_find_factors, _generate_gcd, etc.)
    - Difficulty logic embedded in EACH generator
    - Cross-concept logic (word problems) embedded
    - Story generation embedded
    - Distractor generation embedded
    """
```

**Problems with Current Approach:**
1. **Monolithic**: 2000+ lines in one file
2. **Duplication**: Difficulty logic repeated in each `_generate_X` method
3. **Tight Coupling**: Story templates hardcoded in generators
4. **No Reuse**: Can't share patterns across chapters/subjects
5. **Hard to Scale**: Adding new question types = modifying monolith

### 1.2 What YAML Configs Already Define

**`taxonomy/math.yaml`** - The "WHAT":
```yaml
# 11 concepts for factors_multiples chapter
- id: math.class5.factors_multiples.divisibility
  bloom_level: REMEMBER
  difficulty_range: [1, 2]

- id: math.class5.factors_multiples.word_problem
  bloom_level: APPLY
  difficulty_range: [2, 4]  # Allows difficulty 4 (hard)
```

**`blueprints/.../factors_multiples.yaml`** - The "HOW MUCH":
```yaml
coverage_targets:
  math.class5.factors_multiples.gcd:
    difficulty_mix: {"2": 0.5, "3": 0.5}  # 50% medium, 50% hard
    bloom_mix: {APPLY: 1.0}

session_templates:
  challenge_mode:
    concept_weights: {word_problem: 0.3, assertion_reason: 0.35, error_analysis: 0.35}
    difficulty_range: [3, 4]
```

**`graphs/.../factors_multiples.yaml`** - The "ORDER":
```yaml
edges:
  - from: math.class5.factors_multiples.divisibility
    to: math.class5.factors_multiples.factors
    kind: prerequisite

  - from: math.class5.factors_multiples.gcd
    to: math.class5.factors_multiples.lcm
    kind: co_requisite  # Often combined in cross-concept questions
```

---

## 2. New Architecture: Layered Design

### 2.1 The Three Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LAYER 3: ORCHESTRATOR                            │
│  QuestionOrchestrator - Reads YAML, decides WHAT to generate         │
│  - Select concept based on prerequisites + mastery                   │
│  - Compute difficulty based on blueprint + performance               │
│  - Decide when to combine concepts (cross-concept)                   │
│  - Call appropriate generator(s)                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     LAYER 2: YAML CONFIGS                            │
│  taxonomy/     - Concept definitions, Bloom levels, difficulty range │
│  blueprints/   - Coverage targets, session templates, difficulty mix │
│  graphs/       - Prerequisites, co-requisites, cross-concept edges   │
│  rubrics/      - Quality criteria for generated questions            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     LAYER 1: DUMB GENERATORS                         │
│  generators/math/grade_05/factors_multiples/                         │
│  - divisibility.py      - ONLY generates divisibility questions      │
│  - factors.py           - ONLY generates factor questions            │
│  - gcd.py               - ONLY generates GCD questions               │
│  - lcm.py               - ONLY generates LCM questions               │
│  - word_problem.py      - ONLY generates word problems (parameterized)│
│                                                                       │
│  Each generator:                                                      │
│  - Takes (difficulty, bloom_level, seed, avoid_set) as INPUT          │
│  - Returns (question, answer, options, distractors) as OUTPUT         │
│  - Has NO knowledge of cross-concept or session logic                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Example

**Request**: "Generate a challenge session for a student who has mastered basic concepts"

```
1. API Request
   └─► QuestionOrchestrator.generate_session(
         student_id="abc",
         template="challenge_mode"
       )

2. Orchestrator reads blueprint
   └─► session_templates.challenge_mode:
       - concept_weights: {word_problem: 0.3, assertion_reason: 0.35}
       - difficulty_range: [3, 4]

3. Orchestrator checks prerequisites (graph)
   └─► Can student access assertion_reason?
       ├─► Requires: gcd ✓, lcm ✓ (student has mastery)
       └─► YES, include in session

4. Orchestrator checks mastery (database)
   └─► student.mastery["gcd"] = 0.85  # High
       student.mastery["lcm"] = 0.72  # Medium-high

5. For each question in session:
   a. Select concept based on weights + prerequisites
   b. Compute difficulty: base (from blueprint) + adjustment (from mastery)
   c. Check if cross-concept (co_requisite edge exists)
   d. Call generator(s)

6. Generator produces question
   └─► gcd.py.generate(difficulty=3, bloom=APPLY)
       └─► Returns: Question with 4 options, distractors, solution

7. Return session
   └─► [Question, Question, ...] (10 questions)
```

---

## 3. Generator Design: The "DUMB" Approach

### 3.1 What Makes a Generator "DUMB"

| DUMB Generators DO | DUMB Generators DON'T |
|---|---|
| Generate variations of ONE concept | Know about other concepts |
| Accept difficulty as parameter | Decide what difficulty to use |
| Generate correct answers + distractors | Know about student mastery |
| Return structured output | Know about session context |
| Use seed for reproducibility | Know about prerequisites |

### 3.2 Example: Refactored `gcd.py`

**BEFORE (in monolith - 150 lines embedded in 2000-line file):**
```python
def _generate_find_gcd_integrated(self) -> Question:
    # Difficulty logic embedded
    hybrid_difficulty = random.choice([EASY, MEDIUM, HARD])
    
    # Story logic embedded
    if hybrid_difficulty == EASY:
        story = "Aarav has {a} red marbles and {b} blue marbles..."
    
    # Cross-concept check embedded (BAD - generator shouldn't know this)
    if self._should_combine_with_lcm():
        return self._generate_gcd_lcm_combined()
    
    # ... 100+ more lines
```

**AFTER (standalone generator - ~80 lines):**
```python
# generators/math/grade_05/factors_multiples/gcd.py

from generators.interface import BaseGenerator, GeneratorInput, GeneratorOutput
from typing import List
import random
import math


class GCDGenerator(BaseGenerator):
    """
    DUMB Generator: GCD (Greatest Common Divisor)
    
    - Generates GCD questions for TWO numbers
    - Parameterized by difficulty (1-4)
    - NO knowledge of LCM, prerequisites, or sessions
    """
    
    CONCEPT_ID = "math.class5.factors_multiples.gcd"
    
    # Number ranges by difficulty (content team can adjust via YAML later)
    NUMBER_RANGES = {
        1: (6, 20),      # Easy: small numbers
        2: (12, 48),     # Medium: medium numbers
        3: (24, 100),    # Hard: larger numbers
        4: (50, 200),    # Expert: large numbers
    }
    
    # Story templates (could move to YAML later)
    STORY_TEMPLATES = [
        {
            "context": "grouping",
            "template": "{name} has {a} red ribbons and {b} blue ribbons. "
                       "She wants to cut them into equal pieces with no ribbon left over. "
                       "What is the longest length each piece can be?",
        },
        {
            "context": "distribution",
            "template": "A shopkeeper has {a} apples and {b} oranges. "
                       "He wants to arrange them in rows with equal number of fruits. "
                       "What is the maximum number of fruits in each row?",
        },
        {
            "context": "tiling",
            "template": "A room is {a} cm long and {b} cm wide. "
                       "What is the largest size of square tile that can exactly fit?",
        },
    ]
    
    def generate(self, input: GeneratorInput) -> GeneratorOutput:
        """Generate a GCD question."""
        
        # Apply seed if provided
        if input.seed:
            random.seed(input.seed)
        
        # Get difficulty-appropriate number range
        min_n, max_n = self.NUMBER_RANGES.get(input.difficulty, (12, 48))
        
        # REVERSE CONSTRUCTION: Start with GCD, derive numbers
        gcd_value = random.randint(2, min(12, min_n))
        multiplier_a = random.randint(2, max_n // gcd_value)
        multiplier_b = random.randint(2, max_n // gcd_value)
        
        # Ensure multipliers are coprime (so GCD is exactly gcd_value)
        while math.gcd(multiplier_a, multiplier_b) != 1:
            multiplier_b = random.randint(2, max_n // gcd_value)
        
        a = gcd_value * multiplier_a
        b = gcd_value * multiplier_b
        
        # Avoid numbers student has seen
        while a in input.avoid_numbers or b in input.avoid_numbers:
            gcd_value = random.randint(2, min(12, min_n))
            multiplier_a = random.randint(2, max_n // gcd_value)
            multiplier_b = random.randint(2, max_n // gcd_value)
            while math.gcd(multiplier_a, multiplier_b) != 1:
                multiplier_b = random.randint(2, max_n // gcd_value)
            a = gcd_value * multiplier_a
            b = gcd_value * multiplier_b
        
        # Pick story template
        story = random.choice(self.STORY_TEMPLATES)
        name = self.random_indian_name()
        question_text = story["template"].format(name=name, a=a, b=b)
        
        # Generate distractors (misconception-based)
        distractors = self._generate_distractors(a, b, gcd_value)
        
        # Build options
        options, correct_idx = self.shuffle_options(str(gcd_value), [d.value for d in distractors])
        
        # Build solution steps
        solution_steps = self._build_solution(a, b, gcd_value)
        
        return GeneratorOutput(
            question_text=question_text,
            answer=str(gcd_value),
            options=options,
            correct_option_index=correct_idx,
            distractors=distractors,
            solution_steps=solution_steps,
            topic="GCD (Greatest Common Divisor)",
            fingerprint=self.create_fingerprint("gcd", a, b, gcd_value),
            template_id=f"gcd_{story['context']}",
        )
    
    def _generate_distractors(self, a: int, b: int, gcd: int) -> List:
        """Generate pedagogically meaningful wrong answers."""
        from generators.interface import DistractorInfo
        
        return [
            DistractorInfo(
                value=str(a * b),
                misconception_type="PRODUCT_CONFUSION",
                description="Multiplied instead of finding GCD",
                why_wrong="Product gives a much larger number; GCD divides both numbers",
                teaching_hint="GCD is a DIVISOR, not a multiple",
            ),
            DistractorInfo(
                value=str(min(a, b)),
                misconception_type="SMALLER_NUMBER",
                description="Chose the smaller number",
                why_wrong=f"{min(a,b)} doesn't divide {max(a,b)} evenly",
                teaching_hint="GCD must divide BOTH numbers evenly",
            ),
            DistractorInfo(
                value=str(gcd * 2) if gcd * 2 < min(a, b) else str(gcd + 1),
                misconception_type="ARITHMETIC_ERROR",
                description="Calculation error",
                why_wrong="Double-check your factorization",
                teaching_hint="Verify: Does your answer divide both numbers?",
            ),
        ]
    
    def _build_solution(self, a: int, b: int, gcd: int) -> List[str]:
        """Build step-by-step solution."""
        # Find factors
        factors_a = sorted([i for i in range(1, a+1) if a % i == 0])
        factors_b = sorted([i for i in range(1, b+1) if b % i == 0])
        common = sorted(set(factors_a) & set(factors_b))
        
        return [
            f"Step 1: Find all factors of {a}: {factors_a}",
            f"Step 2: Find all factors of {b}: {factors_b}",
            f"Step 3: Find common factors: {common}",
            f"Step 4: The greatest common factor is {gcd}",
            f"Answer: GCD({a}, {b}) = {gcd}",
        ]


# Export for registry
GENERATORS = [GCDGenerator]
```

### 3.3 Cross-Concept Generator: `gcd_lcm_combined.py`

For questions that require BOTH GCD and LCM knowledge:

```python
# generators/math/grade_05/factors_multiples/gcd_lcm_combined.py

"""
Cross-Concept Generator: GCD + LCM Combined Questions

This generator creates questions that test understanding of the
relationship between GCD and LCM: GCD(a,b) × LCM(a,b) = a × b

Only called by Orchestrator when:
1. Student has mastered both GCD and LCM (from graph)
2. Blueprint indicates cross-concept question (difficulty 3-4)
"""

from generators.interface import BaseGenerator, GeneratorInput, GeneratorOutput
import random
import math


class GCDLCMRelationshipGenerator(BaseGenerator):
    """
    Cross-concept generator for GCD-LCM relationship questions.
    
    Question types:
    1. Given GCD and LCM, find the numbers
    2. Given one number, GCD, find LCM
    3. Verify GCD × LCM = a × b
    """
    
    CONCEPT_IDS = [
        "math.class5.factors_multiples.gcd",
        "math.class5.factors_multiples.lcm",
    ]
    
    def generate(self, input: GeneratorInput) -> GeneratorOutput:
        # Pick question type based on difficulty
        if input.difficulty <= 2:
            return self._generate_verify_relationship(input)
        elif input.difficulty == 3:
            return self._generate_find_lcm_from_gcd(input)
        else:
            return self._generate_find_numbers(input)
    
    def _generate_verify_relationship(self, input: GeneratorInput) -> GeneratorOutput:
        """Verify that GCD × LCM = a × b"""
        # Start with nice numbers
        gcd = random.randint(2, 8)
        m1, m2 = random.randint(2, 6), random.randint(2, 6)
        while math.gcd(m1, m2) != 1:
            m2 = random.randint(2, 6)
        
        a, b = gcd * m1, gcd * m2
        lcm = a * b // gcd
        
        question_text = (
            f"For two numbers {a} and {b}:\n"
            f"GCD = {gcd}, LCM = {lcm}\n\n"
            f"What is GCD × LCM?"
        )
        
        correct = gcd * lcm
        distractors = [
            str(a + b),       # Sum
            str(a * b + gcd), # Wrong formula
            str(lcm - gcd),   # Subtraction
        ]
        
        return GeneratorOutput(
            question_text=question_text,
            answer=str(correct),
            options=self.shuffle_options(str(correct), distractors)[0],
            correct_option_index=self.shuffle_options(str(correct), distractors)[1],
            solution_steps=[
                f"GCD({a}, {b}) = {gcd}",
                f"LCM({a}, {b}) = {lcm}",
                f"GCD × LCM = {gcd} × {lcm} = {correct}",
                f"Also: {a} × {b} = {correct} ✓",
                f"This verifies: GCD × LCM = a × b",
            ],
            topic="GCD-LCM Relationship",
            fingerprint=self.create_fingerprint("gcd_lcm_rel", a, b),
        )
    
    # ... other methods


GENERATORS = [GCDLCMRelationshipGenerator]
```

---

## 4. Orchestrator Design: The "SMART" Layer

### 4.1 Orchestrator Responsibilities

```python
# backend/domain/orchestration/question_orchestrator.py

class QuestionOrchestrator:
    """
    The SMART layer that reads YAML and makes decisions.
    
    Responsibilities:
    1. Load and cache YAML configs (taxonomy, blueprints, graphs)
    2. Select concepts based on student mastery + prerequisites
    3. Compute difficulty based on performance + blueprint rules
    4. Decide when to use cross-concept generators
    5. Call appropriate generators and validate output
    """
    
    def __init__(self, db_session, config_path: str = "config/content"):
        self.db = db_session
        self.taxonomy = self._load_taxonomy(config_path)
        self.blueprints = self._load_blueprints(config_path)
        self.graphs = self._load_graphs(config_path)
        self.registry = GeneratorRegistry(db_session)
    
    # ==================== PUBLIC API ====================
    
    def generate_question(
        self,
        subject: str,
        grade: int,
        chapter: str,
        student_id: str,
        concept_id: str = None,  # Optional: specific concept
        difficulty: int = None,   # Optional: override
    ) -> Question:
        """
        Generate a single question using YAML rules.
        
        If concept_id is None, selects based on:
        - Student mastery (from DB)
        - Prerequisites (from graph)
        - Coverage targets (from blueprint)
        """
        # Get student mastery
        mastery = self._get_student_mastery(student_id, chapter)
        
        # Select concept if not specified
        if concept_id is None:
            concept_id = self._select_concept(
                chapter=chapter,
                mastery=mastery,
                graph=self.graphs[chapter]
            )
        
        # Compute difficulty if not specified
        if difficulty is None:
            difficulty = self._compute_difficulty(
                concept_id=concept_id,
                mastery=mastery,
                blueprint=self.blueprints[chapter]
            )
        
        # Check for cross-concept opportunity
        if self._should_combine_concepts(concept_id, mastery, self.graphs[chapter]):
            return self._generate_cross_concept(concept_id, difficulty, mastery)
        
        # Get appropriate generator
        generator = self.registry.get_generator(
            subject=subject,
            grade=grade,
            chapter=chapter,
            concept=concept_id.split('.')[-1],  # Extract short key
            difficulty=difficulty
        )
        
        # Execute generator
        result = self.registry.execute_generator(
            generator['generator_id'],
            GeneratorInput(
                difficulty=difficulty,
                bloom_level=self._get_bloom_level(concept_id),
                avoid_numbers=self._get_recent_numbers(student_id),
            )
        )
        
        return self._to_question(result.output)
    
    def generate_session(
        self,
        subject: str,
        grade: int,
        chapter: str,
        student_id: str,
        template: str = "practice_fundamentals",
    ) -> List[Question]:
        """
        Generate a full session using blueprint template.
        """
        # Get session template from blueprint
        session = self.blueprints[chapter]['session_templates'][template]
        
        questions = []
        seen_fingerprints = set()
        
        for i in range(session['question_count']):
            # Select concept based on weights
            concept_id = self._weighted_concept_selection(
                session['concept_weights'],
                chapter
            )
            
            # Compute difficulty within session range
            difficulty = self._compute_session_difficulty(
                i, session['question_count'],
                session['difficulty_range'],
                student_id
            )
            
            # Generate question (avoid duplicates)
            q = self.generate_question(
                subject, grade, chapter, student_id,
                concept_id=concept_id,
                difficulty=difficulty
            )
            
            while q.fingerprint in seen_fingerprints:
                q = self.generate_question(
                    subject, grade, chapter, student_id,
                    concept_id=concept_id,
                    difficulty=difficulty
                )
            
            seen_fingerprints.add(q.fingerprint)
            questions.append(q)
        
        return questions
    
    # ==================== PRIVATE METHODS ====================
    
    def _select_concept(self, chapter: str, mastery: dict, graph: dict) -> str:
        """
        Select next concept based on prerequisites and mastery.
        
        Algorithm:
        1. Find all concepts where prerequisites are met
        2. Among those, prefer concepts with lower mastery
        3. Apply coverage targets from blueprint
        """
        eligible = []
        
        for node in graph['nodes']:
            concept_id = node['concept_id']
            
            # Check prerequisites
            prereqs = self._get_prerequisites(concept_id, graph)
            if all(mastery.get(p, 0) >= 0.6 for p in prereqs):
                eligible.append(concept_id)
        
        # Sort by mastery (ascending) - focus on weaker areas
        eligible.sort(key=lambda c: mastery.get(c, 0))
        
        # Weight by coverage targets
        blueprint = self.blueprints[chapter]
        weights = []
        for c in eligible:
            target = blueprint['coverage_targets']['by_concept_id'].get(c, {})
            priority = {"high": 3, "medium": 2, "low": 1}.get(target.get('priority', 'medium'), 2)
            weights.append(priority * (1 - mastery.get(c, 0)))  # Lower mastery = higher weight
        
        # Weighted random selection
        return random.choices(eligible, weights=weights, k=1)[0]
    
    def _compute_difficulty(self, concept_id: str, mastery: dict, blueprint: dict) -> int:
        """
        Compute difficulty based on mastery and blueprint rules.
        
        Formula:
        - Base difficulty from concept's difficulty_range
        - Adjusted by student mastery on this concept
        - Constrained by blueprint's difficulty_mix
        """
        concept_short = concept_id.split('.')[-1]
        
        # Get concept config
        concept_config = blueprint['coverage_targets']['by_concept_id'].get(concept_id, {})
        difficulty_mix = concept_config.get('difficulty_mix', {"2": 1.0})
        
        # Get concept's range from taxonomy
        taxonomy_entry = self._get_taxonomy_entry(concept_id)
        min_d, max_d = taxonomy_entry.get('difficulty_range', [1, 3])
        
        # Adjust based on mastery
        student_mastery = mastery.get(concept_id, 0)
        
        if student_mastery < 0.4:
            # Struggling - stay at lower difficulty
            target = min_d
        elif student_mastery < 0.7:
            # Progressing - middle difficulty
            target = (min_d + max_d) // 2
        else:
            # Mastered - push to higher difficulty
            target = max_d
        
        # Constrain by blueprint's difficulty_mix
        allowed_difficulties = [int(d) for d in difficulty_mix.keys()]
        if target not in allowed_difficulties:
            target = min(allowed_difficulties, key=lambda d: abs(d - target))
        
        return target
    
    def _should_combine_concepts(self, concept_id: str, mastery: dict, graph: dict) -> bool:
        """
        Decide if we should generate a cross-concept question.
        
        Conditions:
        1. Concept has co_requisite edges
        2. Student has mastered BOTH concepts (>70%)
        3. Random chance (30% when conditions met)
        """
        co_requisites = self._get_co_requisites(concept_id, graph)
        
        if not co_requisites:
            return False
        
        # Check if student has mastered all related concepts
        for co_req in co_requisites:
            if mastery.get(co_req, 0) < 0.7:
                return False
        
        # 30% chance of cross-concept when eligible
        return random.random() < 0.3
    
    def _get_prerequisites(self, concept_id: str, graph: dict) -> List[str]:
        """Get all prerequisite concepts from graph."""
        return [
            edge['from'] for edge in graph['edges']
            if edge['to'] == concept_id and edge['kind'] == 'prerequisite'
        ]
    
    def _get_co_requisites(self, concept_id: str, graph: dict) -> List[str]:
        """Get all co-requisite concepts from graph."""
        co_reqs = []
        for edge in graph['edges']:
            if edge['kind'] == 'co_requisite':
                if edge['from'] == concept_id:
                    co_reqs.append(edge['to'])
                elif edge['to'] == concept_id:
                    co_reqs.append(edge['from'])
        return co_reqs
```

---

## 5. LLM's Role: One-Time Generator Creation

### 5.1 What LLM Does (One-Time)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LLM FACTORY PROCESS                             │
│                                                                      │
│  INPUT:                                                              │
│  ├── Taxonomy YAML (concept definition)                              │
│  ├── Blueprint YAML (difficulty ranges, coverage targets)            │
│  ├── Graph YAML (prerequisites, co-requisites)                       │
│  ├── Example question from current monolith                          │
│  └── GeneratorInterface protocol                                     │
│                                                                      │
│  PROMPT:                                                             │
│  "Create a DUMB generator for concept {concept_id}.                 │
│   - Accept difficulty (1-4) as parameter                             │
│   - Use REVERSE CONSTRUCTION (answer → question)                     │
│   - Generate 3 distractors with misconception types                  │
│   - Follow GeneratorInterface protocol exactly"                      │
│                                                                      │
│  OUTPUT:                                                             │
│  └── generators/math/grade_05/factors_multiples/{concept}.py         │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 What LLM Does NOT Do (Runtime)

- ❌ Generate questions at runtime
- ❌ Make decisions about difficulty
- ❌ Handle cross-concept logic
- ❌ Manage session flow

### 5.3 Generator Creation Prompt Template

```
You are creating a Python generator for an educational math app.

CONCEPT: {concept_id}
- Name: {concept_name}
- Bloom Level: {bloom_level}
- Difficulty Range: {difficulty_range}

YAML CONTEXT:
- Prerequisite concepts: {prerequisites}
- Co-requisite concepts: {co_requisites}
- Blueprint priority: {priority}

INTERFACE REQUIREMENTS:
- Extend BaseGenerator
- Implement generate(self, input: GeneratorInput) -> GeneratorOutput
- Accept difficulty as parameter (use NUMBER_RANGES dict)
- Use REVERSE CONSTRUCTION when possible
- Generate exactly 3 distractors with MisconceptionType

EXAMPLE FROM CURRENT CODEBASE:
{existing_generator_code}

Generate a clean, standalone generator file that:
1. Has ~80-120 lines (not 500+)
2. Uses Indian names/contexts for word problems
3. Includes clear misconception-based distractors
4. Has step-by-step solution

OUTPUT: Only the Python code, no explanations.
```

### 5.4 One-Time Cost Estimate

| Task | Generators | Tokens/Gen | Cost/1M tokens | Total |
|------|------------|------------|----------------|-------|
| Class 5 Math (factors_multiples) | 11 | ~3000 | ₹5 | ₹165 |
| Class 5 Math (all chapters) | ~100 | ~3000 | ₹5 | ₹1,500 |
| Classes 3-10 Math | ~900 | ~3000 | ₹5 | ₹13,500 |
| Science + English | ~1,400 | ~3000 | ₹5 | ₹21,000 |
| **Total (one-time)** | ~2,400 | - | - | **~₹36,000** |

**Plus human review time**: ~2 hours/chapter × 100 chapters = 200 hours

---

## 6. Migration Plan for `factors_multiples`

### Phase 1: Extract Generators (Week 1)

```
CURRENT:
  domain/content_generation/generators/factors_multiples.py (2015 lines)

AFTER:
  generators/math/grade_05/factors_multiples/
  ├── __init__.py
  ├── manifest.yaml
  ├── divisibility.py       (~80 lines, extracted from lines 800-900)
  ├── prime_composite.py    (~80 lines)
  ├── factors.py            (~100 lines, extracted from lines 350-500)
  ├── multiples.py          (~80 lines)
  ├── factor_pairs.py       (~80 lines)
  ├── gcd.py                (~100 lines)
  ├── lcm.py                (~100 lines)
  ├── prime_factorization.py (~100 lines)
  ├── word_problem.py       (~150 lines)
  ├── assertion_reason.py   (~100 lines)
  ├── error_analysis.py     (~100 lines)
  └── gcd_lcm_combined.py   (~100 lines, NEW cross-concept)
```

### Phase 2: Build Orchestrator (Week 2)

```python
# Test that orchestrator produces same quality as monolith

def test_orchestrator_parity():
    old = FactorsMultiplesIntegrated()
    new = QuestionOrchestrator(db, config_path)
    
    for concept in CONCEPTS:
        for difficulty in [1, 2, 3]:
            q_old = old.generate(concept_key=concept, difficulty=difficulty)
            q_new = new.generate_question(
                subject="math", grade=5, chapter="factors_multiples",
                student_id="test", concept_id=f"math.class5.factors_multiples.{concept}",
                difficulty=difficulty
            )
            
            assert q_new.options == 4
            assert q_new.distractors is not None
            assert q_new.solution_steps is not None
```

### Phase 3: A/B Test (Week 3)

```yaml
# config/feature_flags.yaml

generator_registry_v2:
  enabled: true
  rollout_percentage: 10  # Start with 10%
  chapters:
    factors_multiples: 50  # 50% for our test chapter
```

### Phase 4: Validate & Expand (Week 4)

```
Metrics to track:
- Generation latency (target: <100ms)
- Question uniqueness (target: >99.9%)
- Student engagement (time on question)
- Correct answer rate (should be similar to current)
```

---

## 7. Hard/Cross-Concept Question Examples

### 7.1 Current Gap: No Difficulty 4 Questions

**Blueprint says:**
```yaml
math.class5.factors_multiples.word_problem:
  difficulty_mix: {"2": 0.3, "3": 0.5, "4": 0.2}  # 20% should be difficulty 4
```

**Current generator:** Only produces difficulty 1-3 (hardcoded ranges)

### 7.2 New Architecture Enables Difficulty 4

**`word_problem.py` with difficulty 4 support:**
```python
NUMBER_RANGES = {
    1: {"lcm_cap": 30, "gcd_cap": 20, "steps": 1},
    2: {"lcm_cap": 60, "gcd_cap": 48, "steps": 2},
    3: {"lcm_cap": 120, "gcd_cap": 100, "steps": 2},
    4: {"lcm_cap": 200, "gcd_cap": 150, "steps": 3},  # NEW: Multi-step problems
}

def generate(self, input: GeneratorInput) -> GeneratorOutput:
    config = self.NUMBER_RANGES[input.difficulty]
    
    if input.difficulty == 4:
        # Multi-step problem: GCD + LCM in same context
        return self._generate_multi_step_problem(config)
    else:
        return self._generate_single_step_problem(config)

def _generate_multi_step_problem(self, config):
    """
    Example: "Aarav has 72 red balls and 90 blue balls. He wants to:
    1. Divide them into identical groups (GCD)
    2. Also find when two bells ringing at intervals will ring together (LCM)"
    """
    # ... implementation
```

### 7.3 Cross-Concept Example: GCD + LCM + Factors

**Orchestrator detects opportunity:**
```python
# Student has mastery > 70% on gcd, lcm, and factors
# Graph shows co_requisite edges between gcd-lcm
# Blueprint allows difficulty 4 for word_problem

→ Call gcd_lcm_factors_combined.py generator
```

**Generated question:**
```
Two water tanks are being filled. Tank A fills completely every 24 minutes,
Tank B fills completely every 36 minutes.

(a) What is the GCD of 24 and 36? [12]
(b) What is the LCM of 24 and 36? [72]
(c) If both tanks start filling at 8:00 AM, when will they both be full at the same time? [9:12 AM]
(d) How many times will Tank A fill in the time it takes for both to be full together? [3]
```

---

## 8. Scalability: Other Chapters/Subjects

### 8.1 Same Pattern, Different YAML

```
config/content/
├── taxonomy/
│   ├── math.yaml           # All math concepts (Classes 3-10)
│   ├── science.yaml        # All science concepts
│   └── english.yaml        # All English concepts
│
├── blueprints/
│   ├── math/
│   │   ├── class3/ch01_shapes.yaml
│   │   ├── class5/factors_multiples.yaml  # ← Our example
│   │   └── class7/algebraic_expressions.yaml
│   ├── science/
│   │   └── class5/ch01_food_we_eat.yaml
│   └── english/
│       └── class5/grammar.yaml
│
├── graphs/
│   └── (same structure as blueprints)
```

### 8.2 Generator Reuse Across Grades

```python
# generators/templates/reverse_construction.py

class ReverseConstructionMixin:
    """Shared pattern: Start with answer, derive question."""
    
    def reverse_construct_factors(self, target_num: int) -> Tuple[int, List[int]]:
        """Given a target, find number with those factors."""
        ...
    
    def reverse_construct_lcm(self, lcm_value: int) -> Tuple[int, int]:
        """Given LCM, find two numbers that produce it."""
        ...

# Used by:
# - generators/math/grade_05/factors_multiples/lcm.py
# - generators/math/grade_06/fractions/lcm_denominator.py
# - generators/math/grade_07/ratios/lcm_comparison.py
```

---

## 9. Summary: Before vs After

| Aspect | BEFORE (Monolith) | AFTER (Registry v2) |
|--------|-------------------|---------------------|
| Code structure | 1 file × 2000 lines | 12 files × ~100 lines each |
| Difficulty logic | Embedded in each method | Centralized in Orchestrator |
| Cross-concept | Hardcoded checks | Driven by graph YAML |
| Session management | Not standardized | Blueprint templates |
| Adding new concept | Edit monolith | Add one generator file |
| Adding difficulty 4 | Major refactor | Update NUMBER_RANGES dict |
| LLM usage | None | One-time generator creation |
| Runtime cost | Zero | Zero (generators are Python) |

---

## 10. Next Steps

1. **Approve Architecture**: Review this document, raise concerns
2. **Extract `factors_multiples`**: Week 1 task - split monolith into 12 generators
3. **Build Orchestrator**: Week 2 task - implement QuestionOrchestrator
4. **A/B Test**: Week 3 - run 50% traffic through new system
5. **LLM Factory Setup**: Week 4 - automate generator creation for other chapters

---

*Document End - Ready for Discussion*
