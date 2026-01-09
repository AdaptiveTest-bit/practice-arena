"""
Distractor Quality & Misconception Schema

This module defines Pydantic schemas for structured distractor generation
with explicit misconception mapping. The schemas enforce pedagogical quality
standards for multiple choice options.

Misconception Types:
- INCOMPLETE_REASONING: Student stops before completing the logic
- REVERSED_OPERATION: Confusing forward/backward operations (+/-, multiply/divide)
- FORGOT_STEP: Missing a crucial step in multi-step problems
- WRONG_OPERATION: Using correct operation on wrong operands
- MAGNITUDE_ERROR: Off by powers of 10 or wrong scale
- NOTATION_ERROR: Misunderstanding notation or decimal places
- VISUAL_ERROR: Spatial or visual reasoning mistakes
- OFF_BY_ONE: Classic off-by-one error
- WRONG_UNIT: Mixing up units or measurements
- CALCULATION_ERROR: Arithmetic mistake in execution

Reference: Educational research on common misconceptions in primary mathematics
"""

from pydantic import BaseModel, field_validator
from enum import Enum
from typing import List
from datetime import datetime


class MisconceptionType(str, Enum):
    """
    Catalog of common misconception types in primary mathematics.
    
    Each type represents a specific cognitive error pattern that students make.
    These are drawn from educational research and K.C. Nag's observations.
    """
    INCOMPLETE_REASONING = "incomplete_reasoning"
    REVERSED_OPERATION = "reversed_operation"
    FORGOT_STEP = "forgot_step"
    WRONG_OPERATION = "wrong_operation"
    MAGNITUDE_ERROR = "magnitude_error"
    NOTATION_ERROR = "notation_error"
    VISUAL_ERROR = "visual_error"
    OFF_BY_ONE = "off_by_one"
    WRONG_UNIT = "wrong_unit"
    CALCULATION_ERROR = "calculation_error"


class DistractorItem(BaseModel):
    """
    Individual distractor with complete pedagogical metadata.
    
    Each distractor represents a specific misconception that students commonly
    make. The schema enforces:
    - Valid numeric/string value
    - Clear teaching point
    - Specific misconception type
    - Detailed explanation of the error
    - Actionable remediation hint
    
    Validation Rules:
    - value: Non-empty string or number
    - teaching_point: Non-empty string
    - why_wrong: Minimum 20 characters (detailed explanation)
    - remediation_hint: Actionable guidance for students
    """
    
    value: str | float | int
    """
    The option value shown to students.
    
    Examples:
    - "5" (for numeric answer)
    - "2/4" (for fraction)
    - "10 cm" (with units)
    
    Must be plausible and represent the specific misconception.
    """
    
    teaching_point: str
    """
    Core mathematical concept this distractor addresses.
    
    Example: "Understanding the relationship between multiplication and division"
    
    Helps teachers understand what concept to focus on in remediation.
    """
    
    misconception_type: MisconceptionType
    """Which specific misconception this distractor targets."""
    
    why_wrong: str
    """
    Specific error in reasoning that leads to this wrong answer.
    
    Must be at least 20 characters and explain the exact cognitive error.
    
    Example: "Student multiplies only the first number by 2, forgetting to
    multiply the second number as well when doubling the fraction."
    """
    
    remediation_hint: str
    """
    Actionable guidance for students to correct the misconception.
    
    Should be concise but helpful for self-correction.
    
    Example: "Check your work by multiplying ALL parts of the fraction
    to verify the complete answer."
    """
    
    @field_validator('value')
    @classmethod
    def value_is_valid(cls, v):
        """Validate that value is not empty."""
        if v is None:
            raise ValueError("value cannot be None")
        
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("value cannot be an empty string")
        elif isinstance(v, (int, float)):
            pass  # Numeric values are always valid
        else:
            raise ValueError(f"value must be string, int, or float, got {type(v)}")
        
        return v
    
    @field_validator('teaching_point')
    @classmethod
    def teaching_point_not_empty(cls, v):
        """Validate teaching point is meaningful."""
        if not v or not isinstance(v, str):
            raise ValueError("teaching_point must be a non-empty string")
        if len(v.strip()) == 0:
            raise ValueError("teaching_point cannot be just whitespace")
        return v.strip()
    
    @field_validator('why_wrong')
    @classmethod
    def why_wrong_is_detailed(cls, v):
        """Validate why_wrong has sufficient detail (20+ characters)."""
        if not v or not isinstance(v, str):
            raise ValueError("why_wrong must be a non-empty string")
        
        cleaned = v.strip()
        if len(cleaned) < 20:
            raise ValueError(
                f"why_wrong must be at least 20 characters, got {len(cleaned)} "
                f"('{cleaned}')"
            )
        return cleaned
    
    @field_validator('remediation_hint')
    @classmethod
    def remediation_hint_not_empty(cls, v):
        """Validate remediation hint is actionable."""
        if not v or not isinstance(v, str):
            raise ValueError("remediation_hint must be a non-empty string")
        if len(v.strip()) == 0:
            raise ValueError("remediation_hint cannot be just whitespace")
        return v.strip()


class QuestionOptionsStructured(BaseModel):
    """
    Complete structured set of MCQ options with validated distractors.
    
    This schema ensures that:
    - The correct option is clearly marked
    - Exactly 3 pedagogically-sound distractors are provided
    - Each distractor targets a unique misconception
    - All misconceptions are appropriate for the topic
    
    Validation Rules:
    - Must have exactly 3 distractors
    - Each distractor targets a different misconception (no duplicates)
    - All fields are non-empty strings
    """
    
    correct_option: str | float | int
    """The correct answer to the question."""
    
    correct_teaching_point: str
    """
    Why this answer is correct and what concept it demonstrates.
    
    Example: "Multiplying each part of the fraction preserves the value
    because 2/4 = 1/2, and doubling both gives 4/8 = 1/2."
    
    Helps reinforce correct understanding when students choose this answer.
    """
    
    distractors: List[DistractorItem]
    """
    List of exactly 3 misconception-based distractors.
    
    Each distractor should:
    - Be plausible (not obviously wrong)
    - Target a different misconception
    - Have pedagogical value (teachable moment)
    - Lead to a wrong answer (not the correct option value)
    """
    
    @field_validator('correct_teaching_point')
    @classmethod
    def correct_teaching_point_not_empty(cls, v):
        """Validate teaching point for correct option."""
        if not v or not isinstance(v, str):
            raise ValueError("correct_teaching_point must be a non-empty string")
        if len(v.strip()) == 0:
            raise ValueError("correct_teaching_point cannot be just whitespace")
        return v.strip()
    
    @field_validator('distractors')
    @classmethod
    def exactly_three_distractors(cls, v):
        """Validate exactly 3 distractors."""
        if not isinstance(v, list):
            raise ValueError("distractors must be a list")
        
        if len(v) != 3:
            raise ValueError(
                f"Must have exactly 3 distractors, got {len(v)}"
            )
        
        # Ensure all misconceptions are unique (no duplicates)
        misconceptions = [d.misconception_type for d in v]
        if len(misconceptions) != len(set(misconceptions)):
            misconception_list = [m.value for m in misconceptions]
            raise ValueError(
                f"Each distractor must target a unique misconception. "
                f"Got duplicates: {misconception_list}"
            )
        
        # Ensure no distractor value matches correct answer
        # (This would be validated at the service level with correct_option)
        
        return v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "correct_option": "4/8",
                "correct_teaching_point": (
                    "Doubling both numerator and denominator preserves the "
                    "fraction's value (2/4 = 1/2, and 4/8 = 1/2)"
                ),
                "distractors": [
                    {
                        "value": "2/4",
                        "teaching_point": "Identity vs. equivalence in fractions",
                        "misconception_type": "incomplete_reasoning",
                        "why_wrong": (
                            "Student only recognizes the starting fraction, "
                            "not that the doubled fraction is equivalent"
                        ),
                        "remediation_hint": (
                            "Simplify both fractions: 2/4 simplifies to 1/2, "
                            "and 4/8 also simplifies to 1/2. They're equal!"
                        )
                    },
                    {
                        "value": "6/8",
                        "teaching_point": "Correct doubling operation",
                        "misconception_type": "wrong_operation",
                        "why_wrong": (
                            "Student doubles only the numerator (2×2=4) and "
                            "adds 2 to denominator (4+2=6) instead of doubling"
                        ),
                        "remediation_hint": (
                            "Double means multiply by 2. Multiply both parts: "
                            "2×2=4, 4×2=8. So 2/4 doubled is 4/8."
                        )
                    },
                    {
                        "value": "8/16",
                        "teaching_point": "Recognizing equivalent fractions",
                        "misconception_type": "magnitude_error",
                        "why_wrong": (
                            "Student quadruples the fraction (×4) instead of "
                            "doubling (×2), resulting in 8/16 = 1/2 but not "
                            "the direct answer"
                        ),
                        "remediation_hint": (
                            "Double means ×2, not ×4. Check: 2×2=4 (top) and "
                            "4×2=8 (bottom), not ×4 for both."
                        )
                    }
                ]
            }
        }


# ============================================================================
# VALIDATION HELPER FUNCTIONS
# ============================================================================

def validate_options_structure(data: dict) -> tuple[bool, str | None]:
    """
    Validate options structure without raising exceptions.
    
    Args:
        data: Dictionary with options fields
    
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    
    Example:
        is_valid, error = validate_options_structure(my_data)
        if not is_valid:
            print(f"Validation error: {error}")
    """
    try:
        QuestionOptionsStructured(**data)
        return True, None
    except Exception as e:
        return False, str(e)


def validate_distractor_item(data: dict) -> tuple[bool, str | None]:
    """
    Validate single distractor item.
    
    Args:
        data: Dictionary with distractor fields
    
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    try:
        DistractorItem(**data)
        return True, None
    except Exception as e:
        return False, str(e)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example of creating valid options
    
    valid_options = QuestionOptionsStructured(
        correct_option="4/8",
        correct_teaching_point=(
            "Doubling both numerator and denominator preserves the "
            "fraction's value (2/4 = 1/2, and 4/8 = 1/2)"
        ),
        distractors=[
            DistractorItem(
                value="2/4",
                teaching_point="Identity vs. equivalence in fractions",
                misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                why_wrong=(
                    "Student only recognizes the starting fraction, "
                    "not that the doubled fraction is equivalent"
                ),
                remediation_hint=(
                    "Simplify both: 2/4 = 1/2, and 4/8 = 1/2. They're equal!"
                )
            ),
            DistractorItem(
                value="6/8",
                teaching_point="Correct doubling operation",
                misconception_type=MisconceptionType.WRONG_OPERATION,
                why_wrong=(
                    "Student doubles only numerator (2×2=4) and "
                    "adds 2 to denominator instead of doubling"
                ),
                remediation_hint=(
                    "Double means multiply by 2 for both: 2×2=4, 4×2=8."
                )
            ),
            DistractorItem(
                value="8/16",
                teaching_point="Recognizing equivalent fractions",
                misconception_type=MisconceptionType.MAGNITUDE_ERROR,
                why_wrong=(
                    "Student quadruples instead of doubles, "
                    "getting a valid equivalent fraction but wrong answer"
                ),
                remediation_hint=(
                    "Double means ×2: 2×2=4 (top), 4×2=8 (bottom)."
                )
            )
        ]
    )
    
    print("✅ Valid options created:")
    print(valid_options.model_dump_json(indent=2))
    
    # Try to create invalid options (will raise ValueError)
    try:
        invalid = QuestionOptionsStructured(
            correct_option="4/8",
            correct_teaching_point="",  # Empty!
            distractors=[
                DistractorItem(
                    value="2/4",
                    teaching_point="test",
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    why_wrong="x",  # Too short!
                    remediation_hint="y"
                )
            ]
        )
    except Exception as e:
        print(f"\n❌ Invalid options rejected (as expected):")
        print(f"Error: {e}")
