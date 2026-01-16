"""
Phase 10: Legacy Generator to Template Extractor

Extracts question patterns from legacy Python generators and converts them
to lean template format for the new template-based architecture.

Usage:
    python -m tools.legacy_extractor --concept factors --output templates/
    python -m tools.legacy_extractor --all --output templates/
"""

import json
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum


class BloomLevel(str, Enum):
    REMEMBER = "REMEMBER"
    UNDERSTAND = "UNDERSTAND"
    APPLY = "APPLY"
    ANALYZE = "ANALYZE"
    EVALUATE = "EVALUATE"
    CREATE = "CREATE"


@dataclass
class MisconceptionTemplate:
    """Template for a misconception-based distractor."""
    option_pattern: str  # Jinja2 pattern for the option value
    misconception_code: str  # e.g., "INCOMPLETE_REASONING"
    why_wrong: str
    teaching_point: str


@dataclass
class ExtractedTemplate:
    """Extracted template ready for database insertion."""
    concept_id: str
    template_code: str  # Unique identifier like "factors_v1", "gcd_v2"
    question_pattern: str  # Jinja2 template for question text
    variable_schema: Dict[str, Any]  # JSON schema for variable generation
    answer_logic: str  # Python expression for correct answer
    option_patterns: List[str]  # Jinja2 templates for options
    difficulty: int
    bloom_level: str
    estimated_time: int
    misconceptions: List[MisconceptionTemplate] = field(default_factory=list)
    diagram_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['misconceptions'] = [asdict(m) for m in self.misconceptions]
        return result


# ============================================================================
# TEMPLATE DEFINITIONS FOR EACH CONCEPT
# These are manually curated from analyzing the legacy generator patterns
# ============================================================================

FACTORS_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.factors",
        template_code="factors_find_all_v1",
        question_pattern="Find all factors of {{ target_number }}.",
        variable_schema={
            "type": "object",
            "properties": {
                "target_number": {
                    "type": "integer",
                    "minimum": 6,
                    "maximum": 100,
                    "description": "Number to find factors of"
                }
            }
        },
        answer_logic="sorted([i for i in range(1, variables['target_number'] + 1) if variables['target_number'] % i == 0])",
        option_patterns=[
            "{{ factors }}",  # Correct: all factors
            "{{ factors_without_1_and_self }}",  # Missing 1 and self
            "[1, {{ target_number }}]",  # Only boundary factors
            "{{ random_subset }}"  # Random subset with non-divisors
        ],
        difficulty=2,
        bloom_level="UNDERSTAND",
        estimated_time=90,
        misconceptions=[
            MisconceptionTemplate(
                option_pattern="{{ factors_without_1_and_self }}",
                misconception_code="INCOMPLETE_REASONING",
                why_wrong="Missing 1 and the number itself as factors",
                teaching_point="1 divides every number, and every number divides itself"
            ),
            MisconceptionTemplate(
                option_pattern="[1, {{ target_number }}]",
                misconception_code="INCOMPLETE_REASONING",
                why_wrong="Only listed boundary factors",
                teaching_point="A factor is any number that divides evenly; test all numbers from 1 to target"
            ),
            MisconceptionTemplate(
                option_pattern="{{ random_subset }}",
                misconception_code="CONSTRAINT_VIOLATION",
                why_wrong="Includes numbers that don't divide evenly",
                teaching_point="A factor must divide with NO remainder; check your division"
            )
        ],
        diagram_type="factors"
    ),
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.factors",
        template_code="factors_count_v1",
        question_pattern="How many factors does {{ target_number }} have?",
        variable_schema={
            "type": "object",
            "properties": {
                "target_number": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 60,
                    "description": "Number to count factors of"
                }
            }
        },
        answer_logic="len([i for i in range(1, variables['target_number'] + 1) if variables['target_number'] % i == 0])",
        option_patterns=[
            "{{ factor_count }}",  # Correct
            "{{ factor_count - 2 }}",  # Missing 1 and self
            "{{ factor_count + 1 }}",  # Off by one
            "{{ target_number // 2 }}"  # Common mistake
        ],
        difficulty=2,
        bloom_level="UNDERSTAND",
        estimated_time=60,
        diagram_type="factors"
    ),
]

MULTIPLES_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.multiples",
        template_code="multiples_first_n_v1",
        question_pattern="Find the first {{ count }} multiples of {{ base_number }}.",
        variable_schema={
            "type": "object",
            "properties": {
                "base_number": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 15,
                    "description": "Base number for multiples"
                },
                "count": {
                    "type": "integer",
                    "minimum": 5,
                    "maximum": 7,
                    "description": "Number of multiples to find"
                }
            }
        },
        answer_logic="[variables['base_number'] * i for i in range(1, variables['count'] + 1)]",
        option_patterns=[
            "{{ multiples }}",  # Correct: starts from base_number
            "{{ multiples_with_zero }}",  # Includes 0
            "{{ multiples_skip_first }}",  # Starts from 2x
            "{{ multiples_off_by_one }}"  # Off by one
        ],
        difficulty=2,
        bloom_level="UNDERSTAND",
        estimated_time=60,
        misconceptions=[
            MisconceptionTemplate(
                option_pattern="{{ multiples_with_zero }}",
                misconception_code="INCOMPLETE_REASONING",
                why_wrong="Incorrectly included 0 as first multiple",
                teaching_point="Multiples start at 1x the base number, not 0x"
            ),
            MisconceptionTemplate(
                option_pattern="{{ multiples_skip_first }}",
                misconception_code="CONSTRAINT_VIOLATION",
                why_wrong="Skipped the first multiple",
                teaching_point="The first multiple is the number itself (1x)"
            ),
            MisconceptionTemplate(
                option_pattern="{{ multiples_off_by_one }}",
                misconception_code="ARITHMETIC_ERROR",
                why_wrong="Miscounted the multiples",
                teaching_point="List the exact number of multiples requested"
            )
        ],
        diagram_type="multiples"
    ),
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.multiples",
        template_code="multiples_is_multiple_v1",
        question_pattern="Is {{ test_number }} a multiple of {{ base_number }}?",
        variable_schema={
            "type": "object",
            "properties": {
                "base_number": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 12,
                    "description": "Base number"
                },
                "test_number": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 100,
                    "description": "Number to test"
                }
            }
        },
        answer_logic="'Yes' if variables['test_number'] % variables['base_number'] == 0 else 'No'",
        option_patterns=[
            "{{ answer }}",
            "{{ opposite_answer }}",
            "Cannot determine",
            "Depends on context"
        ],
        difficulty=1,
        bloom_level="REMEMBER",
        estimated_time=30,
        diagram_type="divisibility"
    ),
]

GCD_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.gcd",
        template_code="gcd_find_v1",
        question_pattern="What is the GCD (Greatest Common Divisor) of {{ num1 }} and {{ num2 }}?",
        variable_schema={
            "type": "object",
            "properties": {
                "num1": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 50,
                    "description": "First number"
                },
                "num2": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 50,
                    "description": "Second number"
                }
            }
        },
        answer_logic="__import__('math').gcd(variables['num1'], variables['num2'])",
        option_patterns=[
            "{{ gcd_result }}",  # Correct
            "{{ num1 * num2 }}",  # Product (LCM confusion)
            "{{ min(num1, num2) }}",  # Smaller number
            "{{ num1 + num2 }}"  # Sum
        ],
        difficulty=2,
        bloom_level="APPLY",
        estimated_time=90,
        misconceptions=[
            MisconceptionTemplate(
                option_pattern="{{ num1 * num2 }}",
                misconception_code="FORMULA_CONFUSION",
                why_wrong="Multiplied instead of finding GCD",
                teaching_point="GCD is the largest divisor of both numbers, not their product"
            ),
            MisconceptionTemplate(
                option_pattern="{{ min(num1, num2) }}",
                misconception_code="INCOMPLETE_REASONING",
                why_wrong="Just took the smaller number without checking divisibility",
                teaching_point="The smaller number may not divide the larger one evenly"
            ),
            MisconceptionTemplate(
                option_pattern="{{ num1 + num2 }}",
                misconception_code="CONSTRAINT_VIOLATION",
                why_wrong="Added the numbers instead of finding common divisor",
                teaching_point="GCD is about divisibility, not addition"
            )
        ],
        diagram_type="gcd"
    ),
]

LCM_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.lcm",
        template_code="lcm_find_v1",
        question_pattern="What is the LCM (Least Common Multiple) of {{ num1 }} and {{ num2 }}?",
        variable_schema={
            "type": "object",
            "properties": {
                "num1": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 12,
                    "description": "First number"
                },
                "num2": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 12,
                    "description": "Second number"
                }
            }
        },
        answer_logic="(variables['num1'] * variables['num2']) // __import__('math').gcd(variables['num1'], variables['num2'])",
        option_patterns=[
            "{{ lcm_result }}",  # Correct
            "{{ num1 * num2 }}",  # Product (ignoring GCD)
            "{{ gcd_result }}",  # GCD instead of LCM
            "{{ max(num1, num2) }}"  # Larger number
        ],
        difficulty=2,
        bloom_level="APPLY",
        estimated_time=90,
        misconceptions=[
            MisconceptionTemplate(
                option_pattern="{{ num1 * num2 }}",
                misconception_code="INCOMPLETE_REASONING",
                why_wrong="Multiplied without considering common factors",
                teaching_point="LCM = (a × b) ÷ GCD(a, b), not just a × b"
            ),
            MisconceptionTemplate(
                option_pattern="{{ gcd_result }}",
                misconception_code="FORMULA_CONFUSION",
                why_wrong="Confused GCD with LCM",
                teaching_point="GCD is the largest common divisor; LCM is the smallest common multiple"
            ),
            MisconceptionTemplate(
                option_pattern="{{ max(num1, num2) }}",
                misconception_code="CONSTRAINT_VIOLATION",
                why_wrong="Just took the larger number",
                teaching_point="LCM must be divisible by both numbers"
            )
        ],
        diagram_type="lcm"
    ),
]

DIVISIBILITY_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.divisibility",
        template_code="divisibility_check_v1",
        question_pattern="Is {{ number }} divisible by {{ divisor }}?",
        variable_schema={
            "type": "object",
            "properties": {
                "number": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 100,
                    "description": "Number to check"
                },
                "divisor": {
                    "type": "integer",
                    "enum": [2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "description": "Divisor to check"
                }
            }
        },
        answer_logic="'Yes' if variables['number'] % variables['divisor'] == 0 else 'No'",
        option_patterns=[
            "{{ 'Yes' if is_divisible else 'No' }}",
            "{{ 'No' if is_divisible else 'Yes' }}",
            "Cannot be determined",
            "Only if {{ number }} is even"
        ],
        difficulty=1,
        bloom_level="REMEMBER",
        estimated_time=30,
        diagram_type="divisibility"
    ),
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.divisibility",
        template_code="divisibility_rule_v1",
        question_pattern="Which divisibility rule helps check if {{ number }} is divisible by {{ divisor }}?",
        variable_schema={
            "type": "object",
            "properties": {
                "number": {
                    "type": "integer",
                    "minimum": 100,
                    "maximum": 999,
                    "description": "3-digit number"
                },
                "divisor": {
                    "type": "integer",
                    "enum": [2, 3, 5, 9, 10],
                    "description": "Divisor with known rule"
                }
            }
        },
        answer_logic="{'2': 'Last digit is even', '3': 'Sum of digits divisible by 3', '5': 'Last digit is 0 or 5', '9': 'Sum of digits divisible by 9', '10': 'Last digit is 0'}[str(variables['divisor'])]",
        option_patterns=[
            "{{ correct_rule }}",
            "{{ wrong_rule_1 }}",
            "{{ wrong_rule_2 }}",
            "{{ wrong_rule_3 }}"
        ],
        difficulty=2,
        bloom_level="UNDERSTAND",
        estimated_time=60
    ),
]

PRIME_COMPOSITE_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.prime_composite",
        template_code="prime_identify_v1",
        question_pattern="Is {{ number }} a prime number or a composite number?",
        variable_schema={
            "type": "object",
            "properties": {
                "number": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 50,
                    "description": "Number to classify"
                }
            }
        },
        answer_logic="'Prime' if len([i for i in range(1, variables['number'] + 1) if variables['number'] % i == 0]) == 2 else 'Composite'",
        option_patterns=[
            "{{ 'Prime' if is_prime else 'Composite' }}",
            "{{ 'Composite' if is_prime else 'Prime' }}",
            "Neither",
            "Both"
        ],
        difficulty=1,
        bloom_level="REMEMBER",
        estimated_time=45,
        misconceptions=[
            MisconceptionTemplate(
                option_pattern="{{ 'Composite' if is_prime else 'Prime' }}",
                misconception_code="SIMILAR_CONCEPT_ERROR",
                why_wrong="Confused prime and composite definitions",
                teaching_point="Prime has exactly 2 factors (1 and itself); composite has more than 2"
            )
        ],
        diagram_type="prime_composite"
    ),
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.prime_composite",
        template_code="prime_list_v1",
        question_pattern="Which of the following is a prime number?",
        variable_schema={
            "type": "object",
            "properties": {
                "prime": {
                    "type": "integer",
                    "enum": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
                    "description": "A prime number"
                },
                "composite1": {
                    "type": "integer",
                    "minimum": 4,
                    "maximum": 50,
                    "description": "A composite number"
                },
                "composite2": {
                    "type": "integer",
                    "minimum": 4,
                    "maximum": 50,
                    "description": "Another composite number"
                },
                "composite3": {
                    "type": "integer",
                    "minimum": 4,
                    "maximum": 50,
                    "description": "Third composite number"
                }
            }
        },
        answer_logic="variables['prime']",
        option_patterns=[
            "{{ prime }}",
            "{{ composite1 }}",
            "{{ composite2 }}",
            "{{ composite3 }}"
        ],
        difficulty=1,
        bloom_level="REMEMBER",
        estimated_time=30
    ),
]

CROSS_CONCEPT_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.cross_concept",
        template_code="cross_concept_factor_multiple_v1",
        question_pattern="Find a number that is both a factor of {{ num1 }} AND a multiple of {{ num2 }}.",
        variable_schema={
            "type": "object",
            "properties": {
                "num1": {
                    "type": "integer",
                    "minimum": 20,
                    "maximum": 100,
                    "description": "Larger number (must have factors that are multiples of num2)"
                },
                "num2": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 10,
                    "description": "Smaller number for multiple check"
                }
            }
        },
        answer_logic="[x for x in range(1, variables['num1']+1) if variables['num1'] % x == 0 and x % variables['num2'] == 0][0]",
        option_patterns=[
            "{{ answer }}",  # Correct: factor of num1 AND multiple of num2
            "{{ num2 }}",  # Wrong: just num2 (may not be factor of num1)
            "{{ num1 // 2 }}",  # Wrong: factor but not multiple
            "{{ num1 + num2 }}"  # Wrong: neither factor nor correct multiple
        ],
        difficulty=4,
        bloom_level="ANALYZE",
        estimated_time=120,
        misconceptions=[
            MisconceptionInfo(
                option_index=1,
                target_misconception="confuses_multiple_with_factor",
                teaching_point="A multiple of a number can be divided evenly by that number, but it must ALSO be a factor of the other number.",
                why_wrong="This is a multiple of the second number but may not be a factor of the first number."
            ),
            MisconceptionInfo(
                option_index=2,
                target_misconception="ignores_multiple_condition",
                teaching_point="The answer must satisfy BOTH conditions: be a factor AND be a multiple.",
                why_wrong="This is a factor of the first number but not a multiple of the second."
            ),
            MisconceptionInfo(
                option_index=3,
                target_misconception="adds_instead_of_finding_common",
                teaching_point="Cross-concept problems require finding numbers that satisfy multiple conditions, not combining the numbers.",
                why_wrong="Adding the numbers doesn't give a factor or multiple relationship."
            )
        ],
        rich_narrative="A farmer has {{ num1 }} apples to pack into boxes. Each box must hold a number of apples that's a multiple of {{ num2 }}. How many apples can go in each box if all boxes are equal?",
        visual_hints=[
            "List factors of {{ num1 }}",
            "Check which factors are multiples of {{ num2 }}",
            "A number is a multiple of {{ num2 }} if it can be divided evenly by {{ num2 }}"
        ],
        diagram_type="venn_diagram"
    ),
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.cross_concept",
        template_code="cross_concept_gcd_lcm_v1",
        question_pattern="If GCD({{ a }}, {{ b }}) = {{ gcd_val }} and LCM({{ a }}, {{ b }}) = {{ lcm_val }}, what is {{ a }} × {{ b }}?",
        variable_schema={
            "type": "object",
            "properties": {
                "a": {"type": "integer", "minimum": 6, "maximum": 30},
                "b": {"type": "integer", "minimum": 6, "maximum": 30},
                "gcd_val": {"type": "integer", "computed": True},
                "lcm_val": {"type": "integer", "computed": True}
            }
        },
        answer_logic="variables['gcd_val'] * variables['lcm_val']",
        option_patterns=[
            "{{ gcd_val * lcm_val }}",  # Correct: GCD × LCM = a × b
            "{{ gcd_val + lcm_val }}",  # Wrong: added instead of multiplied
            "{{ lcm_val - gcd_val }}",  # Wrong: subtracted
            "{{ lcm_val // gcd_val }}"  # Wrong: divided
        ],
        difficulty=5,
        bloom_level="ANALYZE",
        estimated_time=150,
        misconceptions=[
            MisconceptionInfo(
                option_index=1,
                target_misconception="adds_gcd_lcm",
                teaching_point="The relationship is GCD × LCM = a × b (multiplication, not addition).",
                why_wrong="GCD and LCM should be multiplied, not added."
            ),
            MisconceptionInfo(
                option_index=2,
                target_misconception="subtracts_gcd_lcm",
                teaching_point="Remember: GCD × LCM = a × b. This is a fundamental property.",
                why_wrong="Subtraction doesn't give the product of the two numbers."
            )
        ],
        rich_narrative="Two bells ring together at 6 AM. One rings every {{ a }} minutes, the other every {{ b }} minutes. Using GCD and LCM, find their product.",
        visual_hints=[
            "GCD × LCM = a × b is always true",
            "This is a fundamental property of GCD and LCM"
        ]
    )
]

PRIME_FACTORIZATION_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.prime_factorization",
        template_code="prime_factorization_v1",
        question_pattern="What is the prime factorization of {{ number }}?",
        variable_schema={
            "type": "object",
            "properties": {
                "number": {
                    "type": "integer",
                    "minimum": 12,
                    "maximum": 100,
                    "description": "Number to factorize"
                }
            }
        },
        answer_logic="' × '.join([f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(__import__('sympy').factorint(variables['number']).items())])",
        option_patterns=[
            "{{ prime_factorization }}",  # Correct
            "{{ factors_list }}",  # All factors, not prime factorization
            "{{ wrong_factorization }}",  # Wrong exponents
            "{{ partial_factorization }}"  # Incomplete
        ],
        difficulty=3,
        bloom_level="APPLY",
        estimated_time=120,
        diagram_type="prime_factorization"
    ),
]

WORD_PROBLEM_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.word_problem",
        template_code="word_problem_lcm_v1",
        question_pattern="Two buses leave a station at the same time. Bus A returns every {{ interval_a }} minutes and Bus B returns every {{ interval_b }} minutes. After how many minutes will both buses be at the station together again?",
        variable_schema={
            "type": "object",
            "properties": {
                "interval_a": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 30,
                    "description": "Bus A interval"
                },
                "interval_b": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 30,
                    "description": "Bus B interval"
                }
            }
        },
        answer_logic="(variables['interval_a'] * variables['interval_b']) // __import__('math').gcd(variables['interval_a'], variables['interval_b'])",
        option_patterns=[
            "{{ lcm_result }} minutes",
            "{{ interval_a * interval_b }} minutes",
            "{{ gcd_result }} minutes",
            "{{ interval_a + interval_b }} minutes"
        ],
        difficulty=3,
        bloom_level="APPLY",
        estimated_time=120,
        misconceptions=[
            MisconceptionTemplate(
                option_pattern="{{ interval_a * interval_b }} minutes",
                misconception_code="INCOMPLETE_REASONING",
                why_wrong="Multiplied intervals without considering common factors",
                teaching_point="Use LCM formula: (a × b) ÷ GCD(a, b)"
            ),
            MisconceptionTemplate(
                option_pattern="{{ gcd_result }} minutes",
                misconception_code="FORMULA_CONFUSION",
                why_wrong="Used GCD instead of LCM",
                teaching_point="This is a 'when will they meet again' problem - use LCM"
            ),
            MisconceptionTemplate(
                option_pattern="{{ interval_a + interval_b }} minutes",
                misconception_code="OPERATION_CONFUSION",
                why_wrong="Added intervals instead of finding LCM",
                teaching_point="Meeting again requires finding common multiple, not sum"
            )
        ]
    ),
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.word_problem",
        template_code="word_problem_gcd_v1",
        question_pattern="A carpenter has {{ length_a }} cm and {{ length_b }} cm wooden planks. He wants to cut them into equal pieces of the longest possible length. What is the length of each piece?",
        variable_schema={
            "type": "object",
            "properties": {
                "length_a": {
                    "type": "integer",
                    "minimum": 20,
                    "maximum": 100,
                    "description": "First plank length"
                },
                "length_b": {
                    "type": "integer",
                    "minimum": 20,
                    "maximum": 100,
                    "description": "Second plank length"
                }
            }
        },
        answer_logic="__import__('math').gcd(variables['length_a'], variables['length_b'])",
        option_patterns=[
            "{{ gcd_result }} cm",
            "{{ lcm_result }} cm",
            "{{ min(length_a, length_b) }} cm",
            "{{ (length_a + length_b) // 2 }} cm"
        ],
        difficulty=3,
        bloom_level="APPLY",
        estimated_time=120
    ),
]

ASSERTION_REASON_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.assertion_reason",
        template_code="assertion_reason_factors_v1",
        question_pattern="**Assertion:** {{ num1 }} is a factor of {{ num1 * num2 }}\n**Reason:** Because {{ num1 }} × {{ num2 }} = {{ num1 * num2 }}\n\nChoose the correct option:",
        variable_schema={
            "type": "object",
            "properties": {
                "num1": {
                    "type": "integer",
                    "minimum": 3,
                    "maximum": 12,
                    "description": "First number"
                },
                "num2": {
                    "type": "integer",
                    "minimum": 3,
                    "maximum": 12,
                    "description": "Second number"
                }
            }
        },
        answer_logic="'A'",  # Both correct, reason explains assertion
        option_patterns=[
            "Both assertion and reason are correct; reason explains assertion",
            "Both are correct; reason does NOT explain assertion",
            "Assertion is correct; reason is incorrect",
            "Both assertion and reason are incorrect"
        ],
        difficulty=3,
        bloom_level="ANALYZE",
        estimated_time=90,
        misconceptions=[
            MisconceptionTemplate(
                option_pattern="Both are correct; reason does NOT explain assertion",
                misconception_code="LOGICAL_DISCONNECT",
                why_wrong="Failed to recognize that the reason directly explains the assertion",
                teaching_point="Look for the logical connection - does the reason provide evidence for the assertion?"
            ),
            MisconceptionTemplate(
                option_pattern="Assertion is correct; reason is incorrect",
                misconception_code="SIMILAR_CONCEPT_ERROR",
                why_wrong="Incorrectly judged the mathematical reason as false",
                teaching_point="Verify each mathematical statement independently before judging their relationship"
            ),
            MisconceptionTemplate(
                option_pattern="Both assertion and reason are incorrect",
                misconception_code="SIMILAR_CONCEPT_ERROR",
                why_wrong="Failed to recognize valid mathematical truths",
                teaching_point="Break down complex statements - evaluate assertion and reason separately first"
            )
        ]
    ),
]

ERROR_ANALYSIS_TEMPLATES = [
    ExtractedTemplate(
        concept_id="math.class5.factors_multiples.error_analysis",
        template_code="error_analysis_factors_v1",
        question_pattern="Three students found all factors of {{ number }}:\n\n**Student A:** {{ correct_factors }}\n**Student B:** {{ missing_boundary }}\n**Student C:** {{ extra_factors }}\n\nWhich student is correct?",
        variable_schema={
            "type": "object",
            "properties": {
                "number": {
                    "type": "integer",
                    "minimum": 12,
                    "maximum": 36,
                    "description": "Number to find factors of"
                }
            }
        },
        answer_logic="'Student A'",
        option_patterns=[
            "Student A",
            "Student B",
            "Student C",
            "None of them"
        ],
        difficulty=3,
        bloom_level="ANALYZE",
        estimated_time=90
    ),
]


# All template collections
ALL_TEMPLATES = {
    "factors": FACTORS_TEMPLATES,
    "multiples": MULTIPLES_TEMPLATES,
    "gcd": GCD_TEMPLATES,
    "lcm": LCM_TEMPLATES,
    "divisibility": DIVISIBILITY_TEMPLATES,
    "prime_composite": PRIME_COMPOSITE_TEMPLATES,
    "prime_factorization": PRIME_FACTORIZATION_TEMPLATES,
    "word_problem": WORD_PROBLEM_TEMPLATES,
    "assertion_reason": ASSERTION_REASON_TEMPLATES,
    "error_analysis": ERROR_ANALYSIS_TEMPLATES,
    "cross_concept": CROSS_CONCEPT_TEMPLATES,
}


class LegacyExtractor:
    """Extracts templates from legacy generators."""
    
    def __init__(self, output_dir: str = "templates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_concept(self, concept_key: str) -> List[ExtractedTemplate]:
        """Extract templates for a specific concept."""
        if concept_key not in ALL_TEMPLATES:
            raise ValueError(f"Unknown concept: {concept_key}. Available: {list(ALL_TEMPLATES.keys())}")
        return ALL_TEMPLATES[concept_key]
    
    def extract_all(self) -> Dict[str, List[ExtractedTemplate]]:
        """Extract all templates from all concepts."""
        return ALL_TEMPLATES.copy()
    
    def export_to_json(self, concept_key: str = None) -> str:
        """Export templates to JSON file(s)."""
        if concept_key:
            templates = self.extract_concept(concept_key)
            output_file = self.output_dir / f"{concept_key}_templates.json"
            with open(output_file, 'w') as f:
                json.dump([t.to_dict() for t in templates], f, indent=2)
            return str(output_file)
        else:
            # Export all
            all_templates = self.extract_all()
            output_files = []
            for key, templates in all_templates.items():
                output_file = self.output_dir / f"{key}_templates.json"
                with open(output_file, 'w') as f:
                    json.dump([t.to_dict() for t in templates], f, indent=2)
                output_files.append(str(output_file))
            
            # Also create a combined file
            combined = []
            for templates in all_templates.values():
                combined.extend([t.to_dict() for t in templates])
            
            combined_file = self.output_dir / "all_templates.json"
            with open(combined_file, 'w') as f:
                json.dump(combined, f, indent=2)
            output_files.append(str(combined_file))
            
            return ", ".join(output_files)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about extracted templates."""
        all_templates = self.extract_all()
        
        stats = {
            "total_templates": 0,
            "by_concept": {},
            "by_bloom_level": {},
            "by_difficulty": {},
            "with_diagrams": 0,
            "with_misconceptions": 0,
        }
        
        for concept, templates in all_templates.items():
            stats["total_templates"] += len(templates)
            stats["by_concept"][concept] = len(templates)
            
            for t in templates:
                # Bloom level
                stats["by_bloom_level"][t.bloom_level] = stats["by_bloom_level"].get(t.bloom_level, 0) + 1
                
                # Difficulty
                stats["by_difficulty"][t.difficulty] = stats["by_difficulty"].get(t.difficulty, 0) + 1
                
                # Diagrams
                if t.diagram_type:
                    stats["with_diagrams"] += 1
                
                # Misconceptions
                if t.misconceptions:
                    stats["with_misconceptions"] += 1
        
        return stats


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract legacy generators to lean templates")
    parser.add_argument("--concept", type=str, help="Specific concept to extract (e.g., 'factors', 'gcd')")
    parser.add_argument("--all", action="store_true", help="Extract all concepts")
    parser.add_argument("--output", type=str, default="templates", help="Output directory")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    
    args = parser.parse_args()
    
    extractor = LegacyExtractor(output_dir=args.output)
    
    if args.stats:
        stats = extractor.get_statistics()
        print("\n📊 Extraction Statistics:")
        print(f"  Total templates: {stats['total_templates']}")
        print(f"\n  By concept:")
        for concept, count in stats['by_concept'].items():
            print(f"    - {concept}: {count}")
        print(f"\n  By Bloom level:")
        for level, count in stats['by_bloom_level'].items():
            print(f"    - {level}: {count}")
        print(f"\n  By difficulty:")
        for diff, count in stats['by_difficulty'].items():
            print(f"    - Level {diff}: {count}")
        print(f"\n  With diagrams: {stats['with_diagrams']}")
        print(f"  With misconceptions: {stats['with_misconceptions']}")
        return
    
    if args.all:
        output_files = extractor.export_to_json()
        print(f"✅ Exported all templates to: {output_files}")
    elif args.concept:
        output_file = extractor.export_to_json(args.concept)
        print(f"✅ Exported {args.concept} templates to: {output_file}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
