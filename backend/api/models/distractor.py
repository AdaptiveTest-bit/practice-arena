"""Distractor taxonomy for categorizing mathematical misconceptions.

Based on K.C. Nag pedagogy, each distractor targets a specific misconception
that Class 5 students commonly make. Teachers can use these categories
to understand where students are struggling.
"""

from enum import Enum
from pydantic import BaseModel
from typing import Optional


class MisconceptionType(str, Enum):
    """Categories of mathematical misconceptions Class 5 students make."""
    
    # Conceptual Misunderstandings
    OPPOSITE_CONFUSION = "opposite_confusion"
    # Description: Student uses opposite/inverse when shouldn't
    # Example: Dice shows 5, student uses 7-5=2
    # Why it happens: Confuses pattern recognition with universal rule
    
    UNIVERSAL_VS_SPECIFIC = "universal_vs_specific"
    # Description: Generalizes specific example or vice versa
    # Example: Applies formula only to shown case, not all cases
    # Why it happens: Hasn't internalized universal nature of rules
    
    OPERATION_DIRECTION = "operation_direction"
    # Description: Uses wrong operation direction (multiply vs divide)
    # Example: Multiplies when should divide (or vice versa)
    # Why it happens: Doesn't understand which direction operation should go
    
    REFERENCE_POINT_ERROR = "reference_point_error"
    # Description: Operates on wrong reference (original vs remaining)
    # Example: Uses 1/4 of 500 = 125 as final answer, forgets subtraction
    # Why it happens: Loses track of state changes in multi-step problems
    
    # Calculation & Procedural Errors
    INCOMPLETE_REASONING = "incomplete_reasoning"
    # Description: Stops calculation mid-way (skipped step)
    # Example: Knows 1 kg = 1000 g but forgets to multiply by quantity
    # Why it happens: Incomplete mental checklist
    
    ARITHMETIC_ERROR = "arithmetic_error"
    # Description: Calculation mistake (correct approach, wrong answer)
    # Example: 5 × 7 = 40 (should be 35)
    # Why it happens: Careless mistake or weak multiplication facts
    
    OPERATION_SELECTION = "operation_selection"
    # Description: Selects wrong operation type entirely
    # Example: Adds when should multiply; subtracts when should divide
    # Why it happens: Doesn't understand when to apply each operation
    
    # Formula & Structure Errors
    FORMULA_MISAPPLICATION = "formula_misapplication"
    # Description: Applies incorrect formula to problem
    # Example: Uses Area = L × W for Perimeter (should be 2(L+W))
    # Why it happens: Memorized formulas without understanding what they measure
    
    FORMULA_CONFUSION = "formula_confusion"
    # Description: Confuses similar formulas for different concepts
    # Example: Confuses HCF and LCM calculation
    # Why it happens: Didn't distinguish between related concepts
    
    UNIT_ERROR = "unit_error"
    # Description: Forgets or mishandles units of measurement
    # Example: Calculates in cm but answer should be in m
    # Why it happens: Focuses on number, forgets unit conversion
    
    # Logical & Reasoning Errors
    LOGICAL_DISCONNECT = "logical_disconnect"
    # Description: Breaks logical chain in multi-step problem
    # Example: Calculates two pieces separately without combining
    # Why it happens: Doesn't see overall structure of problem
    
    CONSTRAINT_VIOLATION = "constraint_violation"
    # Description: Ignores given constraints or conditions
    # Example: Gives negative answer when context requires positive
    # Why it happens: Processes numbers without context understanding
    
    # Structural Errors
    PATTERN_MISIDENTIFICATION = "pattern_misidentification"
    # Description: Identifies wrong pattern in sequence/data
    # Example: Continues sequence with wrong pattern
    # Why it happens: Jumped to conclusion without verifying pattern
    
    # Distractor for confusion with similar concept
    SIMILAR_CONCEPT_ERROR = "similar_concept_error"
    # Description: Confuses with similar but different concept
    # Example: Confuses cube with square; 3D with 2D
    # Why it happens: Hasn't internalized difference between concepts


class DistractorInfo(BaseModel):
    """Information about a distractor's pedagogical purpose."""
    
    value: str
    """The distractor value (e.g., "₹20")"""
    
    misconception_type: MisconceptionType
    """What misconception this distractor targets"""
    
    why_wrong: str
    """Why this answer is incorrect (for teacher reference)"""
    
    teaching_point: str
    """What to teach student if they choose this"""
    
    common_in_percentage: Optional[float] = None
    """Estimate of students who make this error (0-100)"""


class DistractorSet(BaseModel):
    """Set of distractors for a multiple choice question."""
    
    correct_answer: str
    """The correct answer"""
    
    distractors: list[DistractorInfo]
    """3 distractors, each targeting a specific misconception"""
    
    def to_options_list(self) -> list[str]:
        """Convert to simple list for API response (backwards compatible)."""
        return [self.correct_answer] + [d.value for d in self.distractors]


# 🆕 PHASE 2: TRAP TYPE CLASSIFICATION
class TrapType(str, Enum):
    """Categories of logical traps that make problems harder."""
    
    CALCULATION_TRAP = "calculation_trap"
    CONTEXT_TRAP = "context_trap"
    ASSUMPTION_TRAP = "assumption_trap"
    VISUAL_TRAP = "visual_trap"
    UNIT_TRAP = "unit_trap"
    INVERSE_TRAP = "inverse_trap"
    OVERGENERALIZATION_TRAP = "overgeneralization_trap"
    SEQUENCE_TRAP = "sequence_trap"


class TrapInfo(BaseModel):
    """Metadata about a logical trap (Phase 2)."""
    
    trap_type: TrapType
    trap_name: str
    difficulty: int = 2
    description: str
    why_effective: str
    how_to_avoid: str


# Mapping from Phase 1 Misconceptions to Phase 2 Traps
MISCONCEPTION_TO_TRAP_MAP = {
    MisconceptionType.OPPOSITE_CONFUSION: TrapType.INVERSE_TRAP,
    MisconceptionType.UNIVERSAL_VS_SPECIFIC: TrapType.OVERGENERALIZATION_TRAP,
    MisconceptionType.OPERATION_DIRECTION: TrapType.INVERSE_TRAP,
    MisconceptionType.REFERENCE_POINT_ERROR: TrapType.CONTEXT_TRAP,
    MisconceptionType.INCOMPLETE_REASONING: TrapType.CALCULATION_TRAP,
    MisconceptionType.ARITHMETIC_ERROR: TrapType.CALCULATION_TRAP,
    MisconceptionType.OPERATION_SELECTION: TrapType.CALCULATION_TRAP,
    MisconceptionType.FORMULA_MISAPPLICATION: TrapType.CONTEXT_TRAP,
    MisconceptionType.FORMULA_CONFUSION: TrapType.ASSUMPTION_TRAP,
    MisconceptionType.UNIT_ERROR: TrapType.UNIT_TRAP,
    MisconceptionType.LOGICAL_DISCONNECT: TrapType.ASSUMPTION_TRAP,
    MisconceptionType.CONSTRAINT_VIOLATION: TrapType.CONTEXT_TRAP,
    MisconceptionType.PATTERN_MISIDENTIFICATION: TrapType.SEQUENCE_TRAP,
    MisconceptionType.SIMILAR_CONCEPT_ERROR: TrapType.ASSUMPTION_TRAP,
}
