# Generator Registry Architecture - Implementation Plan

**Version:** 1.0  
**Date:** January 2025  
**Status:** Technical Specification  

---

## Executive Summary

This document presents a **Generator Registry Architecture** where **Python generator functions ARE the content**, not pre-stored questions. Instead of storing millions of static questions, we store ~10,000 generator functions that produce **infinite variations** on-demand.

### Core Philosophy
```
Traditional: LLM → Questions → Database → Student
Generator:   LLM → Python Code → Registry → Runtime Execution → Infinite Questions
```

---

## 1. Directory Structure for Generator Ecosystem

### 1.1 Top-Level Organization
```
backend/
├── generators/                          # 🆕 NEW: Generator Registry Root
│   ├── __init__.py
│   ├── registry.py                      # Generator discovery & execution engine
│   ├── interface.py                     # Standard GeneratorInterface protocol
│   ├── sandbox/                         # Secure execution environment
│   │   ├── __init__.py
│   │   ├── executor.py                  # RestrictedPython / Docker runner
│   │   ├── whitelist.py                 # Allowed modules & functions
│   │   └── timeout.py                   # Execution time limits
│   │
│   ├── math/                            # Subject: Mathematics
│   │   ├── __init__.py
│   │   ├── grade_03/                    # CBSE Class 3
│   │   │   ├── __init__.py
│   │   │   ├── ch01_where_to_look_from/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── left_right_perception.py
│   │   │   │   ├── front_back_perception.py
│   │   │   │   └── manifest.yaml        # Generator metadata
│   │   │   ├── ch02_fun_with_numbers/
│   │   │   └── ...
│   │   │
│   │   ├── grade_05/                    # CBSE Class 5
│   │   │   ├── __init__.py
│   │   │   ├── ch06_factors_multiples/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── divisibility_test_2.py
│   │   │   │   ├── divisibility_test_3.py
│   │   │   │   ├── divisibility_test_5.py
│   │   │   │   ├── divisibility_test_9.py
│   │   │   │   ├── divisibility_test_10.py
│   │   │   │   ├── lcm_story.py
│   │   │   │   ├── lcm_bus_stop.py
│   │   │   │   ├── hcf_distribution.py
│   │   │   │   ├── hcf_grouping.py
│   │   │   │   ├── prime_factorization.py
│   │   │   │   ├── common_factors_range.py
│   │   │   │   └── manifest.yaml
│   │   │   ├── ch07_patterns/
│   │   │   └── ...
│   │   │
│   │   ├── grade_06/
│   │   ├── grade_07/
│   │   ├── grade_08/
│   │   ├── grade_09/
│   │   └── grade_10/
│   │
│   ├── science/                         # Subject: Science
│   │   ├── __init__.py
│   │   ├── grade_05/
│   │   │   ├── ch01_food_we_eat/
│   │   │   │   ├── nutrient_sources.py       # Isomorphic: same structure, different foods
│   │   │   │   ├── food_groups.py
│   │   │   │   └── manifest.yaml
│   │   │   └── ...
│   │   └── ...
│   │
│   ├── english/                         # Subject: English
│   │   ├── __init__.py
│   │   ├── grade_05/
│   │   │   ├── grammar/
│   │   │   │   ├── subject_verb_agreement.py
│   │   │   │   ├── tense_conversion.py
│   │   │   │   └── manifest.yaml
│   │   │   └── ...
│   │   └── ...
│   │
│   └── templates/                       # Reusable generator patterns
│       ├── __init__.py
│       ├── reverse_construction.py      # Math pattern: answer → question
│       ├── isomorphic_mutation.py       # Science/English pattern
│       ├── story_wrapper.py             # K.C. Nag narrative wrapper
│       └── visual_builder.py            # SVG/MathJax helpers
│
├── domain/
│   └── content_generation/
│       ├── generators/                  # EXISTING: Keep for backward compatibility
│       │   ├── base.py                  # BaseChapterStrategy (legacy)
│       │   └── factors_multiples.py     # FactorsMultiplesIntegrated (legacy)
│       └── service.py                   # 🔄 MODIFIED: Route to Generator Registry
```

### 1.2 Naming Convention
```
{subject}/grade_{nn}/ch{mm}_{slug}/{concept_slug}.py

Examples:
- math/grade_05/ch06_factors_multiples/lcm_story.py
- science/grade_05/ch01_food_we_eat/nutrient_sources.py
- english/grade_05/grammar/subject_verb_agreement.py
```

### 1.3 Estimated Scale
| Subject | Grades | Chapters/Grade | Concepts/Chapter | Total Generators |
|---------|--------|----------------|------------------|------------------|
| Math    | 8      | 14             | 8                | ~900             |
| Science | 8      | 12             | 6                | ~580             |
| English | 8      | 10             | 10               | ~800             |
| **Total** | -    | -              | -                | **~2,300**       |

With difficulty variants (3 levels × 2 cognitive tiers): **~13,800 generator functions**

---

## 2. Database Schema for Generator Registry

### 2.1 Core Tables

```sql
-- ============================================
-- GENERATOR REGISTRY: Core Tables
-- ============================================

-- 1. Generator definitions (metadata only - code in filesystem)
CREATE TABLE generators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Unique identifier for the generator
    generator_id VARCHAR(128) NOT NULL UNIQUE,  -- e.g., "MATH_G05_CH06_LCM_STORY_E1"
    
    -- Taxonomy keys
    subject VARCHAR(32) NOT NULL,               -- math, science, english
    grade_level INTEGER NOT NULL,               -- 3-10
    chapter_key VARCHAR(100) NOT NULL,          -- factors_multiples
    concept_id VARCHAR(64) NOT NULL,            -- lcm_story
    
    -- Difficulty & Cognitive Level
    difficulty_tier INTEGER NOT NULL,           -- 1=Easy, 2=Medium, 3=Hard
    bloom_level VARCHAR(20) NOT NULL,           -- REMEMBER, UNDERSTAND, APPLY, ANALYZE
    
    -- Code location (filesystem path relative to generators/)
    module_path VARCHAR(256) NOT NULL,          -- math/grade_05/ch06_factors_multiples/lcm_story.py
    function_name VARCHAR(64) NOT NULL,         -- generate_easy, generate_medium, etc.
    
    -- Execution metadata
    avg_execution_ms INTEGER DEFAULT 0,         -- Performance tracking
    last_executed_at TIMESTAMP,
    execution_count BIGINT DEFAULT 0,
    
    -- Quality control
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, deprecated, testing
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(64),                     -- 'deepseek_r1', 'human_author', etc.
    
    -- Indexes
    CONSTRAINT generators_pkey PRIMARY KEY (id)
);

-- Composite index for taxonomy-based lookups
CREATE INDEX idx_generators_taxonomy 
    ON generators(subject, grade_level, chapter_key, concept_id, difficulty_tier, bloom_level);

CREATE INDEX idx_generators_status ON generators(status);
CREATE INDEX idx_generators_module ON generators(module_path, function_name);


-- 2. Generator code versions (for LLM-generated code auditing)
CREATE TABLE generator_code_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id VARCHAR(128) NOT NULL REFERENCES generators(generator_id),
    
    version INTEGER NOT NULL,
    
    -- Full Python code (for audit trail)
    code_text TEXT NOT NULL,
    code_hash VARCHAR(64) NOT NULL,             -- SHA256 of code_text
    
    -- Generation metadata
    generated_by VARCHAR(64) NOT NULL,          -- 'deepseek_r1_v20250120'
    prompt_hash VARCHAR(64),                    -- Hash of prompt used
    
    -- Review status
    review_status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, approved, rejected
    reviewed_by VARCHAR(64),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    
    -- Test results
    test_passed BOOLEAN,
    test_output JSONB,                          -- Sample outputs, timing, etc.
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(generator_id, version)
);

CREATE INDEX idx_code_versions_generator ON generator_code_versions(generator_id);
CREATE INDEX idx_code_versions_review ON generator_code_versions(review_status);


-- 3. Generator execution logs (for analytics & debugging)
CREATE TABLE generator_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    generator_id VARCHAR(128) NOT NULL,
    session_id VARCHAR(36),
    student_id VARCHAR(64),
    
    -- Execution details
    execution_ms INTEGER NOT NULL,
    seed_used BIGINT,                           -- Random seed for reproducibility
    
    -- Input parameters (JSON)
    input_params JSONB,
    
    -- Output hash (not full question, just for dedup tracking)
    output_hash VARCHAR(64),
    
    -- Status
    success BOOLEAN NOT NULL,
    error_message TEXT,
    
    executed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Partition by time for efficient cleanup
CREATE INDEX idx_executions_time ON generator_executions(executed_at);
CREATE INDEX idx_executions_generator ON generator_executions(generator_id);
CREATE INDEX idx_executions_student ON generator_executions(student_id);


-- 4. Generator dependencies (for module imports)
CREATE TABLE generator_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id VARCHAR(128) NOT NULL REFERENCES generators(generator_id),
    
    dependency_type VARCHAR(32) NOT NULL,       -- 'import', 'template', 'helper'
    dependency_name VARCHAR(128) NOT NULL,      -- 'sympy', 'random', 'templates.reverse_construction'
    
    UNIQUE(generator_id, dependency_name)
);

CREATE INDEX idx_dependencies_generator ON generator_dependencies(generator_id);


-- 5. Cached outputs (optional: for frequently-requested generators)
CREATE TABLE generator_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generator_id VARCHAR(128) NOT NULL,
    
    cache_key VARCHAR(64) NOT NULL,             -- Hash of (generator_id + params)
    output_json JSONB NOT NULL,
    
    hit_count INTEGER DEFAULT 0,
    last_hit_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,                       -- TTL for cache invalidation
    
    UNIQUE(cache_key)
);

CREATE INDEX idx_cache_key ON generator_cache(cache_key);
CREATE INDEX idx_cache_expires ON generator_cache(expires_at);
```

### 2.2 SQLAlchemy Models

```python
# backend/db/models/generators.py

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Index, Integer, 
    String, Text, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from db.base import Base


class Generator(Base):
    """Generator registry entry - metadata only, code lives in filesystem."""
    __tablename__ = "generators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id = Column(String(128), unique=True, nullable=False, index=True)
    
    # Taxonomy
    subject = Column(String(32), nullable=False, index=True)
    grade_level = Column(Integer, nullable=False, index=True)
    chapter_key = Column(String(100), nullable=False, index=True)
    concept_id = Column(String(64), nullable=False, index=True)
    
    # Difficulty & Cognitive
    difficulty_tier = Column(Integer, nullable=False, index=True)  # 1-3
    bloom_level = Column(String(20), nullable=False, index=True)
    
    # Code location
    module_path = Column(String(256), nullable=False)
    function_name = Column(String(64), nullable=False)
    
    # Execution stats
    avg_execution_ms = Column(Integer, default=0)
    last_executed_at = Column(DateTime, nullable=True)
    execution_count = Column(BigInteger, default=0)
    
    # Quality control
    status = Column(String(20), nullable=False, default='active', index=True)
    version = Column(Integer, nullable=False, default=1)
    
    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(64), nullable=True)
    
    # Relationships
    code_versions = relationship("GeneratorCodeVersion", back_populates="generator")
    dependencies = relationship("GeneratorDependency", back_populates="generator")

    __table_args__ = (
        Index('idx_generators_taxonomy', 
              'subject', 'grade_level', 'chapter_key', 'concept_id', 
              'difficulty_tier', 'bloom_level'),
    )


class GeneratorCodeVersion(Base):
    """Audit trail for LLM-generated code."""
    __tablename__ = "generator_code_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id = Column(String(128), ForeignKey('generators.generator_id'), nullable=False)
    
    version = Column(Integer, nullable=False)
    code_text = Column(Text, nullable=False)
    code_hash = Column(String(64), nullable=False)
    
    generated_by = Column(String(64), nullable=False)
    prompt_hash = Column(String(64), nullable=True)
    
    review_status = Column(String(20), nullable=False, default='pending')
    reviewed_by = Column(String(64), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    test_passed = Column(Boolean, nullable=True)
    test_output = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    generator = relationship("Generator", back_populates="code_versions")

    __table_args__ = (
        Index('idx_code_versions_generator', 'generator_id'),
        Index('idx_code_versions_review', 'review_status'),
    )


class GeneratorExecution(Base):
    """Execution log for analytics."""
    __tablename__ = "generator_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id = Column(String(128), nullable=False, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    student_id = Column(String(64), nullable=True, index=True)
    
    execution_ms = Column(Integer, nullable=False)
    seed_used = Column(BigInteger, nullable=True)
    input_params = Column(JSONB, nullable=True)
    output_hash = Column(String(64), nullable=True)
    
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    
    executed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class GeneratorDependency(Base):
    """Track module dependencies for security analysis."""
    __tablename__ = "generator_dependencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id = Column(String(128), ForeignKey('generators.generator_id'), nullable=False)
    
    dependency_type = Column(String(32), nullable=False)  # 'import', 'template', 'helper'
    dependency_name = Column(String(128), nullable=False)  # 'sympy', 'random', etc.
    
    generator = relationship("Generator", back_populates="dependencies")

    __table_args__ = (
        Index('idx_dependencies_generator', 'generator_id'),
    )
```

---

## 3. Standard Python Interface (GeneratorInterface)

### 3.1 Protocol Definition

```python
# backend/generators/interface.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Protocol
from enum import Enum
import random


# ============================================
# INPUT: Generator Request
# ============================================

class DifficultyTier(int, Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class BloomLevel(str, Enum):
    REMEMBER = "REMEMBER"       # Recall facts
    UNDERSTAND = "UNDERSTAND"   # Explain concepts
    APPLY = "APPLY"             # Use in new situations
    ANALYZE = "ANALYZE"         # Break down, compare
    EVALUATE = "EVALUATE"       # Judge, critique (rarely used in K-10)
    CREATE = "CREATE"           # Synthesize new (rarely used in K-10)


@dataclass
class GeneratorInput:
    """Standard input for all generators."""
    
    # Required
    difficulty: DifficultyTier
    bloom_level: BloomLevel
    
    # Optional constraints
    seed: Optional[int] = None              # For reproducibility
    avoid_numbers: List[int] = field(default_factory=list)  # Numbers already seen
    avoid_hashes: List[str] = field(default_factory=list)   # Question hashes already served
    
    # Context for adaptive difficulty
    student_accuracy: Optional[float] = None  # 0.0 - 1.0
    consecutive_correct: int = 0
    consecutive_wrong: int = 0
    
    # Story/theme preferences (optional)
    preferred_context: Optional[str] = None  # "sports", "food", "animals"
    
    def __post_init__(self):
        """Apply seed if provided."""
        if self.seed is not None:
            random.seed(self.seed)


# ============================================
# OUTPUT: Generator Response
# ============================================

@dataclass
class DistractorInfo:
    """Pedagogical info about a wrong answer option."""
    value: str
    misconception_type: str      # "CARRY_ERROR", "UNIT_CONFUSION", etc.
    description: str             # "Student added instead of multiplied"
    why_wrong: str               # "This happens when..."
    teaching_hint: str           # "Remember that LCM means..."


@dataclass
class GeneratorOutput:
    """Standard output from all generators. Maps to frontend Question model."""
    
    # Core question content
    question_text: str           # The actual question (supports LaTeX: $$x^2$$)
    question_html: Optional[str] = None  # Rich HTML with MathJax pre-rendered
    
    # Answer
    answer: str                  # Correct answer value
    answer_latex: Optional[str] = None   # LaTeX representation: $$42$$
    
    # MCQ Options (exactly 4)
    options: List[str] = field(default_factory=list)        # Plain text options
    options_latex: Optional[List[str]] = None               # LaTeX options
    correct_option_index: int = 0
    
    # Distractors with pedagogical rationale
    distractors: List[DistractorInfo] = field(default_factory=list)
    
    # Solution
    solution_steps: List[str] = field(default_factory=list)  # Step-by-step
    solution_latex: Optional[List[str]] = None               # LaTeX steps
    
    # Metadata
    topic: str = ""              # Human-readable topic
    logical_trap: str = ""       # K.C. Nag-style trap explanation
    data_representation: str = "" # Visual/tabular hint
    
    # Rich content (optional)
    narrative: Optional[str] = None       # Story wrapper
    svg_diagram: Optional[str] = None     # SVG visual
    visual_hints: List[str] = field(default_factory=list)
    
    # Tracking
    fingerprint: str = ""        # Unique hash for dedup
    template_id: str = ""        # For "same concept, different numbers"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "question_text": self.question_text,
            "question_html": self.question_html,
            "answer": self.answer,
            "answer_latex": self.answer_latex,
            "options": self.options,
            "options_latex": self.options_latex,
            "correct_option_index": self.correct_option_index,
            "distractors": [
                {
                    "value": d.value,
                    "misconception_type": d.misconception_type,
                    "description": d.description,
                    "why_wrong": d.why_wrong,
                    "teaching_hint": d.teaching_hint,
                }
                for d in self.distractors
            ],
            "solution_steps": self.solution_steps,
            "solution_latex": self.solution_latex,
            "topic": self.topic,
            "logical_trap": self.logical_trap,
            "data_representation": self.data_representation,
            "narrative": self.narrative,
            "svg_diagram": self.svg_diagram,
            "visual_hints": self.visual_hints,
            "fingerprint": self.fingerprint,
            "template_id": self.template_id,
        }


# ============================================
# GENERATOR PROTOCOL
# ============================================

class GeneratorProtocol(Protocol):
    """Protocol that all generators must implement."""
    
    # Metadata (class attributes)
    GENERATOR_ID: str           # "MATH_G05_CH06_LCM_STORY_E1"
    SUBJECT: str                # "math"
    GRADE: int                  # 5
    CHAPTER: str                # "factors_multiples"
    CONCEPT: str                # "lcm_story"
    DIFFICULTY: DifficultyTier
    BLOOM: BloomLevel
    
    def generate(self, input: GeneratorInput) -> GeneratorOutput:
        """Generate a question with the given constraints."""
        ...


class BaseGenerator(ABC):
    """Abstract base class for all generators with common utilities."""
    
    # Subclasses must define these
    GENERATOR_ID: str
    SUBJECT: str
    GRADE: int
    CHAPTER: str
    CONCEPT: str
    DIFFICULTY: DifficultyTier
    BLOOM: BloomLevel
    
    @abstractmethod
    def generate(self, input: GeneratorInput) -> GeneratorOutput:
        """Generate a single question. Must be implemented by subclass."""
        pass
    
    # ========================
    # Utility Methods
    # ========================
    
    def create_fingerprint(self, *args) -> str:
        """Create a unique hash from question components."""
        import hashlib
        combined = "||".join(str(a) for a in args)
        return hashlib.sha256(combined.encode()).hexdigest()[:12]
    
    def shuffle_options(
        self, 
        correct: str, 
        distractors: List[str]
    ) -> tuple[List[str], int]:
        """Shuffle options and return (options, correct_index)."""
        options = [correct] + distractors[:3]
        random.shuffle(options)
        return options, options.index(correct)
    
    def format_latex(self, expr: str) -> str:
        """Wrap expression in LaTeX delimiters."""
        return f"$${expr}$$"
    
    def format_number(self, n: float, decimals: int = 2) -> str:
        """Format number, removing trailing zeros."""
        if n == int(n):
            return str(int(n))
        return f"{n:.{decimals}f}".rstrip('0').rstrip('.')
    
    def random_indian_name(self) -> str:
        """Return a random Indian name for story problems."""
        names = [
            "Aarav", "Ananya", "Arjun", "Diya", "Ishaan", "Kavya",
            "Rohan", "Priya", "Vivaan", "Saanvi", "Aditya", "Meera",
            "Rahul", "Neha", "Vikram", "Pooja", "Karan", "Anjali",
        ]
        return random.choice(names)
    
    def random_indian_city(self) -> str:
        """Return a random Indian city for context."""
        cities = [
            "Jaipur", "Lucknow", "Patna", "Bhopal", "Indore",
            "Chandigarh", "Pune", "Nagpur", "Varanasi", "Coimbatore",
        ]
        return random.choice(cities)
```

### 3.2 Example Generator Implementation

```python
# backend/generators/math/grade_05/ch06_factors_multiples/lcm_story.py

"""
Generator: LCM Story Problems (Bus Stop / Bells / Repeating Events)

This generator creates story problems where LCM is the natural solution.
Uses REVERSE CONSTRUCTION: Start with LCM, derive the factors.
"""

from generators.interface import (
    BaseGenerator, GeneratorInput, GeneratorOutput,
    DistractorInfo, DifficultyTier, BloomLevel
)
import random
from math import gcd


class LCMStoryEasyGenerator(BaseGenerator):
    """Easy LCM story problems - small numbers, 2 factors."""
    
    GENERATOR_ID = "MATH_G05_CH06_LCM_STORY_E1"
    SUBJECT = "math"
    GRADE = 5
    CHAPTER = "factors_multiples"
    CONCEPT = "lcm_story"
    DIFFICULTY = DifficultyTier.EASY
    BLOOM = BloomLevel.APPLY
    
    def generate(self, input: GeneratorInput) -> GeneratorOutput:
        # ========================================
        # REVERSE CONSTRUCTION
        # ========================================
        
        # Step 1: Pick a "nice" LCM (the answer)
        nice_lcms = [12, 15, 18, 20, 24, 30, 36]
        
        # Avoid numbers student has seen
        available = [n for n in nice_lcms if n not in input.avoid_numbers]
        if not available:
            available = nice_lcms
        
        lcm_value = random.choice(available)
        
        # Step 2: Find factor pairs that give this LCM
        factor_pairs = self._find_factor_pairs(lcm_value)
        a, b = random.choice(factor_pairs)
        
        # Step 3: Generate story context
        contexts = [
            {
                "template": "bus_stop",
                "setup": f"From the bus stop near {self.random_indian_city()}, "
                         f"one bus leaves every {a} minutes and another every {b} minutes.",
                "question": "If both buses leave together at 6:00 AM, after how many minutes will they leave together again?",
                "unit": "minutes"
            },
            {
                "template": "bells",
                "setup": f"In {self.random_indian_name()}'s school, one bell rings every {a} minutes "
                         f"and another bell rings every {b} minutes.",
                "question": "If both bells ring together at 9:00 AM, after how many minutes will they ring together again?",
                "unit": "minutes"
            },
            {
                "template": "lights",
                "setup": f"Two traffic lights at a junction blink every {a} seconds and {b} seconds respectively.",
                "question": "If they both blink together now, after how many seconds will they blink together again?",
                "unit": "seconds"
            },
        ]
        
        ctx = random.choice(contexts)
        
        # ========================================
        # BUILD QUESTION
        # ========================================
        
        question_text = f"{ctx['setup']} {ctx['question']}"
        
        # ========================================
        # BUILD DISTRACTORS (Misconception-based)
        # ========================================
        
        distractors = [
            DistractorInfo(
                value=str(a * b),  # Product (common mistake)
                misconception_type="PRODUCT_CONFUSION",
                description="Student multiplied the numbers instead of finding LCM",
                why_wrong=f"Product = {a} × {b} = {a*b}, but LCM considers common factors",
                teaching_hint="LCM is the smallest number divisible by both, not necessarily the product"
            ),
            DistractorInfo(
                value=str(a + b),  # Sum (careless mistake)
                misconception_type="OPERATION_ERROR",
                description="Student added the numbers instead of finding LCM",
                why_wrong="Addition is not the correct operation for finding LCM",
                teaching_hint="LCM requires finding multiples, not adding numbers"
            ),
            DistractorInfo(
                value=str(max(a, b)),  # Larger number (partial understanding)
                misconception_type="PARTIAL_UNDERSTANDING",
                description="Student thought LCM is the larger of the two numbers",
                why_wrong=f"{max(a,b)} is not divisible by {min(a,b)}",
                teaching_hint="LCM must be divisible by BOTH numbers"
            ),
        ]
        
        # ========================================
        # BUILD OPTIONS
        # ========================================
        
        options, correct_idx = self.shuffle_options(
            str(lcm_value),
            [d.value for d in distractors]
        )
        
        # Update distractors with correct indices
        for i, opt in enumerate(options):
            if opt != str(lcm_value):
                for d in distractors:
                    if d.value == opt:
                        break
        
        # ========================================
        # BUILD SOLUTION
        # ========================================
        
        solution_steps = [
            f"We need to find when both events happen together - this is LCM({a}, {b})",
            f"Multiples of {a}: {a}, {a*2}, {a*3}, ..., {lcm_value}",
            f"Multiples of {b}: {b}, {b*2}, {b*3}, ..., {lcm_value}",
            f"The smallest common multiple is {lcm_value}",
            f"Answer: They will coincide after {lcm_value} {ctx['unit']}"
        ]
        
        # ========================================
        # BUILD OUTPUT
        # ========================================
        
        return GeneratorOutput(
            question_text=question_text,
            answer=str(lcm_value),
            answer_latex=self.format_latex(str(lcm_value)),
            options=options,
            correct_option_index=correct_idx,
            distractors=distractors,
            solution_steps=solution_steps,
            topic="LCM Story Problems",
            logical_trap="Students often multiply numbers directly instead of finding LCM",
            data_representation=f"Numbers: {a}, {b}",
            fingerprint=self.create_fingerprint(ctx['template'], a, b, lcm_value),
            template_id=f"lcm_story_{ctx['template']}"
        )
    
    def _find_factor_pairs(self, lcm: int) -> list[tuple[int, int]]:
        """Find pairs (a, b) where LCM(a, b) = lcm and a, b are reasonably small."""
        pairs = []
        for a in range(2, lcm):
            if lcm % a != 0:
                continue
            for b in range(a + 1, lcm + 1):
                if lcm % b != 0:
                    continue
                if (a * b) // gcd(a, b) == lcm:
                    pairs.append((a, b))
        return pairs if pairs else [(lcm // 2, lcm)]


# ========================================
# GENERATOR REGISTRATION
# ========================================

# Each module exports a list of generator classes
GENERATORS = [
    LCMStoryEasyGenerator,
    # LCMStoryMediumGenerator,  # Would be defined similarly
    # LCMStoryHardGenerator,    # Would be defined similarly
]
```

---

## 4. Factory Pipeline for Safe Code Execution

### 4.1 Execution Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                     GENERATOR EXECUTION PIPELINE                      │
└──────────────────────────────────────────────────────────────────────┘

Request                                                          Response
   │                                                                 ▲
   ▼                                                                 │
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌────────┐
│  API    │───▶│ Registry │───▶│ Validator │───▶│ Executor │───▶│ Output │
│ Router  │    │  Lookup  │    │  (AST)    │    │ (Sandbox)│    │ Mapper │
└─────────┘    └──────────┘    └───────────┘    └──────────┘    └────────┘
                    │                │                │               │
                    ▼                ▼                ▼               ▼
              generators/      Whitelist        RestrictedPython   Question
               module         Check             or Docker          Model
```

### 4.2 Security Model

```python
# backend/generators/sandbox/whitelist.py

"""
Security whitelist for generator execution.
Only these modules/functions can be used by generators.
"""

# Allowed imports
ALLOWED_MODULES = {
    # Standard library - safe subset
    'random': ['choice', 'randint', 'shuffle', 'sample', 'uniform', 'seed'],
    'math': ['gcd', 'sqrt', 'floor', 'ceil', 'log', 'log10', 'factorial'],
    'fractions': ['Fraction'],
    'decimal': ['Decimal'],
    'itertools': ['combinations', 'permutations', 'product'],
    'functools': ['reduce'],
    'typing': ['*'],  # All typing constructs
    'dataclasses': ['dataclass', 'field'],
    'enum': ['Enum', 'IntEnum'],
    'hashlib': ['sha256', 'md5'],
    
    # Scientific computing - restricted
    'sympy': [
        'Symbol', 'symbols', 'Eq', 'solve', 'simplify', 'expand', 'factor',
        'gcd', 'lcm', 'factorint', 'isprime', 'prime', 'primerange',
        'sqrt', 'Rational', 'Integer', 'Float',
        'latex',  # For LaTeX output
    ],
    
    # Our internal modules
    'generators.interface': ['*'],
    'generators.templates': ['*'],
}

# Explicitly forbidden (even if in allowed modules)
FORBIDDEN_NAMES = {
    'eval', 'exec', 'compile', 'open', 'file', 'input',
    '__import__', 'globals', 'locals', 'vars', 'dir',
    'getattr', 'setattr', 'delattr', 'hasattr',
    'os', 'sys', 'subprocess', 'socket', 'requests', 'urllib',
}

# Maximum execution time per generator call
MAX_EXECUTION_MS = 500

# Maximum memory per generator call
MAX_MEMORY_MB = 50
```

### 4.3 Sandbox Executor

```python
# backend/generators/sandbox/executor.py

"""
Sandbox executor for generator functions.
Provides multiple execution strategies based on trust level.
"""

from __future__ import annotations
import importlib
import time
import hashlib
from typing import Any, Dict, Optional, Type
from dataclasses import dataclass
import threading
import multiprocessing

from generators.interface import (
    BaseGenerator, GeneratorInput, GeneratorOutput
)
from generators.sandbox.whitelist import (
    ALLOWED_MODULES, FORBIDDEN_NAMES, MAX_EXECUTION_MS, MAX_MEMORY_MB
)


@dataclass
class ExecutionResult:
    """Result of generator execution."""
    success: bool
    output: Optional[GeneratorOutput] = None
    error: Optional[str] = None
    execution_ms: int = 0
    generator_id: str = ""


class GeneratorExecutor:
    """
    Safe executor for generator functions.
    
    Trust Levels:
    1. TRUSTED: Direct Python import (for human-reviewed code)
    2. RESTRICTED: RestrictedPython sandbox (for LLM-generated code)
    3. ISOLATED: Docker container (for untrusted code)
    """
    
    def __init__(self, trust_level: str = "TRUSTED"):
        self.trust_level = trust_level
        self._module_cache: Dict[str, Any] = {}
    
    def execute(
        self,
        module_path: str,
        function_name: str,
        generator_class: str,
        input: GeneratorInput
    ) -> ExecutionResult:
        """
        Execute a generator and return the result.
        
        Args:
            module_path: Python module path (e.g., 'generators.math.grade_05...')
            function_name: Not used for class-based generators
            generator_class: Class name to instantiate
            input: Generator input parameters
        
        Returns:
            ExecutionResult with output or error
        """
        start_time = time.perf_counter()
        
        try:
            if self.trust_level == "TRUSTED":
                result = self._execute_trusted(module_path, generator_class, input)
            elif self.trust_level == "RESTRICTED":
                result = self._execute_restricted(module_path, generator_class, input)
            else:
                result = self._execute_isolated(module_path, generator_class, input)
            
            execution_ms = int((time.perf_counter() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output=result,
                execution_ms=execution_ms,
                generator_id=result.template_id if result else ""
            )
            
        except TimeoutError:
            return ExecutionResult(
                success=False,
                error=f"Execution timeout ({MAX_EXECUTION_MS}ms exceeded)",
                execution_ms=MAX_EXECUTION_MS
            )
        except Exception as e:
            execution_ms = int((time.perf_counter() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_ms=execution_ms
            )
    
    def _execute_trusted(
        self,
        module_path: str,
        generator_class: str,
        input: GeneratorInput
    ) -> GeneratorOutput:
        """
        Direct Python execution for trusted, human-reviewed code.
        """
        # Convert filesystem path to module path
        # e.g., 'math/grade_05/ch06_factors_multiples/lcm_story.py' 
        #    -> 'generators.math.grade_05.ch06_factors_multiples.lcm_story'
        module_name = module_path.replace('/', '.').replace('.py', '')
        if not module_name.startswith('generators.'):
            module_name = f'generators.{module_name}'
        
        # Cache module imports
        if module_name not in self._module_cache:
            self._module_cache[module_name] = importlib.import_module(module_name)
        
        module = self._module_cache[module_name]
        
        # Get generator class
        gen_cls: Type[BaseGenerator] = getattr(module, generator_class)
        
        # Instantiate and execute
        generator = gen_cls()
        return generator.generate(input)
    
    def _execute_restricted(
        self,
        module_path: str,
        generator_class: str,
        input: GeneratorInput
    ) -> GeneratorOutput:
        """
        RestrictedPython execution for LLM-generated code.
        Uses AST analysis and restricted globals.
        """
        # TODO: Implement RestrictedPython sandbox
        # For now, fall back to trusted execution with timeout
        return self._execute_with_timeout(
            self._execute_trusted,
            module_path,
            generator_class,
            input
        )
    
    def _execute_isolated(
        self,
        module_path: str,
        generator_class: str,
        input: GeneratorInput
    ) -> GeneratorOutput:
        """
        Docker container execution for untrusted code.
        Maximum isolation but higher latency.
        """
        # TODO: Implement Docker-based execution
        raise NotImplementedError("Docker execution not yet implemented")
    
    def _execute_with_timeout(
        self,
        func,
        *args,
        timeout_ms: int = MAX_EXECUTION_MS
    ) -> GeneratorOutput:
        """
        Execute function with timeout.
        """
        result = [None]
        error = [None]
        
        def target():
            try:
                result[0] = func(*args)
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=timeout_ms / 1000)
        
        if thread.is_alive():
            raise TimeoutError(f"Execution exceeded {timeout_ms}ms")
        
        if error[0]:
            raise error[0]
        
        return result[0]


class GeneratorRegistry:
    """
    Central registry for all generators.
    Provides lookup and execution services.
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.executor = GeneratorExecutor(trust_level="TRUSTED")
        self._cache: Dict[str, Any] = {}
    
    def get_generator(
        self,
        subject: str,
        grade: int,
        chapter: str,
        concept: str,
        difficulty: int,
        bloom: str
    ) -> Optional[Dict[str, Any]]:
        """
        Look up a generator by taxonomy.
        Returns generator metadata or None.
        """
        # Build cache key
        cache_key = f"{subject}:{grade}:{chapter}:{concept}:{difficulty}:{bloom}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        if self.db:
            from db.models.generators import Generator
            gen = self.db.query(Generator).filter(
                Generator.subject == subject,
                Generator.grade_level == grade,
                Generator.chapter_key == chapter,
                Generator.concept_id == concept,
                Generator.difficulty_tier == difficulty,
                Generator.bloom_level == bloom,
                Generator.status == 'active'
            ).first()
            
            if gen:
                result = {
                    'generator_id': gen.generator_id,
                    'module_path': gen.module_path,
                    'function_name': gen.function_name,
                }
                self._cache[cache_key] = result
                return result
        
        return None
    
    def execute_generator(
        self,
        generator_id: str,
        input: GeneratorInput
    ) -> ExecutionResult:
        """
        Execute a generator by ID.
        """
        # Look up generator
        if self.db:
            from db.models.generators import Generator
            gen = self.db.query(Generator).filter(
                Generator.generator_id == generator_id,
                Generator.status == 'active'
            ).first()
            
            if not gen:
                return ExecutionResult(
                    success=False,
                    error=f"Generator not found: {generator_id}"
                )
            
            # Extract class name from function_name (convention: class name)
            return self.executor.execute(
                gen.module_path,
                gen.function_name,
                gen.function_name,  # Class name
                input
            )
        
        return ExecutionResult(
            success=False,
            error="Database not configured"
        )
```

---

## 5. Implementation Roadmap

### Phase 1: Core Math Foundation (Weeks 1-4)

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1 | Infrastructure | - Database schema migration<br>- GeneratorInterface protocol<br>- Basic sandbox executor |
| 2 | Port Existing | - Convert FactorsMultiplesIntegrated to new format<br>- Create 11 generators for Chapter 6<br>- Unit tests for each |
| 3 | Expand Class 5 | - Generators for Chapters 1-5, 7-14<br>- ~50 generators total<br>- Integration tests |
| 4 | Quality & API | - Content service routing<br>- Performance benchmarks<br>- Error handling & logging |

**Key Deliverables:**
- `generators/math/grade_05/` complete with all chapters
- `GeneratorRegistry` with DB integration
- API endpoint: `GET /api/v2/question?subject=math&grade=5&chapter=factors_multiples&concept=lcm`

### Phase 2: Reasoning Model Factory (Weeks 5-8)

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 5 | DeepSeek Integration | - DeepSeek R1 API client<br>- Prompt templates for code generation<br>- Validation pipeline |
| 6 | Auto-Generation | - Generate 100+ generators via DeepSeek<br>- Automated testing framework<br>- Human review queue |
| 7 | Scale Out | - Class 3-4 Math generators<br>- Class 6-7 Math generators<br>- ~300 generators total |
| 8 | Science Pilot | - Science isomorphic templates<br>- 20 Science generators<br>- Cross-subject validation |

**Key Deliverables:**
- DeepSeek Factory pipeline
- `generator_code_versions` audit trail
- Human review dashboard (basic)
- 300+ active generators

### Phase 3: Full Scale (Weeks 9-12)

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 9 | Math Complete | - Classes 3-10 Math<br>- ~1,000 generators |
| 10 | Science Complete | - Classes 3-10 Science<br>- ~600 generators |
| 11 | English Pilot | - Grammar generators<br>- Comprehension templates<br>- ~200 generators |
| 12 | Launch Prep | - Performance tuning<br>- Monitoring dashboards<br>- Documentation |

**Final Deliverables:**
- ~2,000 generators across Math, Science, English
- <100ms average generation time
- Zero hallucination guarantee
- Infinite question variations

---

## 6. Migration Strategy

### 6.1 Parallel Running

```python
# backend/domain/content_generation/service.py

class ContentService:
    """
    Content service with dual-path support:
    - Legacy: BaseChapterStrategy generators
    - New: Generator Registry
    """
    
    def __init__(self, db_session, feature_flags):
        self.legacy_factory = QuestionGeneratorFactory()
        self.new_registry = GeneratorRegistry(db_session)
        self.feature_flags = feature_flags
    
    async def generate_question(
        self,
        chapter: str,
        concept: str,
        difficulty: int,
        bloom: str,
        student_id: Optional[str] = None
    ) -> Question:
        """Generate question using appropriate backend."""
        
        # Check if new registry has this generator
        use_new = self.feature_flags.get('use_generator_registry', False)
        
        if use_new:
            gen = self.new_registry.get_generator(
                subject='math',
                grade=5,
                chapter=chapter,
                concept=concept,
                difficulty=difficulty,
                bloom=bloom
            )
            
            if gen:
                result = self.new_registry.execute_generator(
                    gen['generator_id'],
                    GeneratorInput(
                        difficulty=DifficultyTier(difficulty),
                        bloom_level=BloomLevel(bloom)
                    )
                )
                
                if result.success:
                    return self._map_to_question(result.output)
        
        # Fallback to legacy
        return self.legacy_factory.generate(chapter)
    
    def _map_to_question(self, output: GeneratorOutput) -> Question:
        """Map GeneratorOutput to legacy Question model."""
        return Question(
            topic=output.topic,
            logical_trap=output.logical_trap,
            data_representation=output.data_representation,
            question_text=output.question_text,
            solution_steps=output.solution_steps,
            answer=output.answer,
            options=output.options,
            correct_option_index=output.correct_option_index,
            chapter=ChapterEnum.FACTORS_MULTIPLES,  # Map appropriately
            # ... rest of fields
        )
```

### 6.2 Feature Flag Rollout

```yaml
# config/feature_flags.yaml

generator_registry:
  # Start with 0%, gradually increase
  rollout_percentage: 0
  
  # Per-chapter overrides
  chapters:
    factors_multiples: 100  # Fully migrated
    large_numbers: 50       # A/B testing
    fractions_decimals: 0   # Not started
  
  # Fallback behavior
  fallback_to_legacy: true
```

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Generation Latency | <100ms p95 | `generator_executions.execution_ms` |
| Zero Hallucinations | 100% | Manual spot-check + student reports |
| Question Uniqueness | >99.9% per student session | `output_hash` collision rate |
| Generator Coverage | 100% Class 5 Math | Generator count vs. curriculum map |
| Code Quality | 100% tests pass | CI/CD pipeline |
| Sandbox Security | 0 escapes | Security audit |

---

## Appendix A: Naming Conventions

### Generator IDs
```
{SUBJECT}_{GRADE}_{CHAPTER}_{CONCEPT}_{DIFFICULTY}{VARIANT}

Examples:
- MATH_G05_CH06_LCM_STORY_E1      (Easy, variant 1)
- MATH_G05_CH06_LCM_STORY_M1      (Medium, variant 1)
- MATH_G05_CH06_DIV2_DETECT_H2    (Hard, variant 2)
- SCI_G05_CH01_NUTRIENTS_E1       (Science)
- ENG_G05_GR_SVA_M1               (English Grammar)
```

### Module Paths
```
{subject}/grade_{nn}/ch{mm}_{slug}/{concept_slug}.py

Examples:
- math/grade_05/ch06_factors_multiples/lcm_story.py
- science/grade_05/ch01_food_we_eat/nutrients.py
- english/grade_05/grammar/subject_verb_agreement.py
```

---

## Appendix B: Security Considerations

1. **AST Validation**: All LLM-generated code must pass AST checks before execution
2. **Import Whitelist**: Only pre-approved modules can be imported
3. **Resource Limits**: CPU time and memory are hard-capped
4. **Audit Trail**: Every code version is stored with generation metadata
5. **Human Review**: New generators require approval before production deployment
6. **Rollback**: Easy revert to previous versions if issues detected

---

*Document End*
