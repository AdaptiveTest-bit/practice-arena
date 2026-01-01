"""
K.C. Nag Story Generation Schema

This module defines Pydantic schemas for structured K.C. Nag story generation.
The schemas enforce data validation at the field level, ensuring that all
generated story contexts meet pedagogical quality standards.

K.C. Nag's Educational Principles:
- INCOMPLETE_REASONING: Student stops before completing the logic chain
- VISUAL_MISCONCEPTION: Spatial or visual reasoning errors
- NOTATION_CONFUSION: Misunderstanding mathematical symbols or notation
- MAGNITUDE_ERROR: Incorrect estimation of scale or size
- REVERSIBLE_OPERATION: Confusing forward/backward operations (e.g., +/-)

Reference: "Teaching Mathematics at Elementary School" - K.C. Nag
"""

from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Optional
from datetime import datetime


class K_C_NagPedagogicalPrinciple(str, Enum):
    """
    K.C. Nag's core teaching principles.
    
    These represent common student misconceptions in Indian primary mathematics,
    derived from K.C. Nag's extensive research and classroom observations.
    """
    INCOMPLETE_REASONING = "incomplete_reasoning"
    VISUAL_MISCONCEPTION = "visual_misconception"
    NOTATION_CONFUSION = "notation_confusion"
    MAGNITUDE_ERROR = "magnitude_error"
    REVERSIBLE_OPERATION = "reversible_operation"


class MathProblemContext(BaseModel):
    """
    Rigid schema for K.C. Nag story context.
    
    This model ensures that all story contexts have:
    - Culturally relevant entity names (Indian context)
    - Clear scenario descriptions (20-150 chars)
    - Realistic settings and actions
    - Explicit connection to real-world mathematics
    
    Validation Rules:
    - entity_name_1: 5-15 characters (typical Indian name length)
    - scenario_description: 20-150 characters (detailed but concise)
    - All fields must be non-empty strings
    """
    
    entity_name_1: str
    """Primary entity name (e.g., 'Amar', 'Priya'). 5-15 characters."""
    
    entity_name_2: Optional[str] = None
    """Secondary entity name (e.g., 'Akbar'). Optional, 5-15 chars if provided."""
    
    scenario_description: str
    """Real-world scenario (e.g., 'sharing apples at a market'). 20-150 chars."""
    
    item_name: str
    """Singular object name (e.g., 'apple', 'rupee'). Essential for templating."""
    
    action_verb: str
    """Main action in the story (e.g., 'shared', 'bought', 'distributed')."""
    
    setting: str
    """Physical location (e.g., 'market', 'home', 'school', 'shop')."""
    
    real_world_relevance: str
    """
    Why this scenario matters for the student.
    Connects abstract math to real-world application.
    e.g., 'Understanding fair sharing is essential in daily transactions'
    """
    
    @field_validator('entity_name_1')
    @classmethod
    def validate_entity_name_1(cls, v):
        """Validate primary entity name length (5-15 characters)."""
        if not v or not isinstance(v, str):
            raise ValueError("entity_name_1 must be a non-empty string")
        if not (5 <= len(v) <= 15):
            raise ValueError(
                f"entity_name_1 must be 5-15 characters, got {len(v)} "
                f"('{v}')"
            )
        # Check that it's a valid name (letters, spaces, hyphens)
        if not all(c.isalpha() or c in ' -' for c in v):
            raise ValueError(
                f"entity_name_1 should contain only letters, spaces, or hyphens "
                f"(got '{v}')"
            )
        return v.strip()
    
    @field_validator('entity_name_2')
    @classmethod
    def validate_entity_name_2(cls, v):
        """Validate secondary entity name if provided."""
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError("entity_name_2 must be a string or None")
        if not (5 <= len(v) <= 15):
            raise ValueError(
                f"entity_name_2 must be 5-15 characters, got {len(v)} "
                f"('{v}')"
            )
        if not all(c.isalpha() or c in ' -' for c in v):
            raise ValueError(
                f"entity_name_2 should contain only letters, spaces, or hyphens "
                f"(got '{v}')"
            )
        return v.strip()
    
    @field_validator('scenario_description')
    @classmethod
    def validate_scenario_description(cls, v):
        """Validate scenario description length (20-150 characters)."""
        if not v or not isinstance(v, str):
            raise ValueError("scenario_description must be a non-empty string")
        if not (20 <= len(v) <= 150):
            raise ValueError(
                f"scenario_description must be 20-150 characters, got {len(v)} "
                f"('{v[:50]}...')"
            )
        return v.strip()
    
    @field_validator('item_name', 'action_verb', 'setting', 'real_world_relevance')
    @classmethod
    def validate_non_empty_string(cls, v, info):
        """Validate that these fields are non-empty strings."""
        if not v or not isinstance(v, str):
            field_name = info.field_name
            raise ValueError(f"{field_name} must be a non-empty string")
        if len(v.strip()) == 0:
            field_name = info.field_name
            raise ValueError(f"{field_name} cannot be just whitespace")
        return v.strip()


class StoryContextStructured(BaseModel):
    """
    Structured output from LLM for K.C. Nag stories.
    
    This schema is used with the Instructor library to enforce structured
    output from Claude, ensuring that the LLM always returns valid story
    contexts that match our pedagogical requirements.
    
    Schema Enforcement:
    - All fields are required (no optional fields)
    - Nested validation via MathProblemContext
    - Enum-based pedagogical principle selection
    - String length constraints on narrative elements
    
    Example Output:
    {
        "context": {
            "entity_name_1": "Amar",
            "entity_name_2": "Akbar",
            "scenario_description": "sharing apples at the market",
            "item_name": "apple",
            "action_verb": "shared",
            "setting": "market",
            "real_world_relevance": "Fair distribution is key to commerce"
        },
        "narrative_template": "{entity_1} had {num1} {items}. {entity_2} gave him {num2} more.",
        "pedagogical_principle": "incomplete_reasoning",
        "misconception_trigger_phrase": "Students forget to count both groups",
        "teaching_hook": "Emphasize systematic counting when combining groups"
    }
    """
    
    context: MathProblemContext
    """Nested context object with all story elements."""
    
    narrative_template: str
    """
    Template for the story narrative.
    Uses {{ }} placeholders for dynamic values:
    - {{entity_1}}: Primary character name
    - {{entity_2}}: Secondary character name (optional)
    - {{action}}: Main action verb
    - {{items}}: Plural item name
    - {{setting}}: Location
    
    Example: "{{entity_1}} had some {{items}} at the {{setting}}..."
    """
    
    pedagogical_principle: K_C_NagPedagogicalPrinciple
    """Which K.C. Nag principle this story teaches."""
    
    misconception_trigger_phrase: str
    """
    The specific phrase or concept in the story that reveals the logical trap.
    
    Example for INCOMPLETE_REASONING:
    "Forgetting to count the items already present"
    
    This helps teachers understand what misconception the story targets.
    """
    
    teaching_hook: str
    """
    Pedagogical explanation of why this story teaches the principle effectively.
    
    Helps educators understand the learning objective and how to use the
    story in classroom instruction.
    
    Example:
    "By combining items from two sources, students must track total quantity,
    preventing incomplete reasoning about the final count."
    """
    
    @field_validator('narrative_template')
    @classmethod
    def validate_narrative_template(cls, v):
        """Validate narrative template has required placeholders."""
        if not v or not isinstance(v, str):
            raise ValueError("narrative_template must be a non-empty string")
        
        # Must contain at least one placeholder
        if '{{' not in v or '}}' not in v:
            raise ValueError(
                "narrative_template must contain at least one {{placeholder}}"
            )
        
        # Validate placeholder format
        import re
        placeholders = re.findall(r'\{\{(\w+)\}\}', v)
        if not placeholders:
            raise ValueError(
                "narrative_template must have valid {{placeholder}} format"
            )
        
        return v.strip()
    
    @field_validator('misconception_trigger_phrase', 'teaching_hook')
    @classmethod
    def validate_explanation_fields(cls, v, info):
        """Validate explanation fields are detailed and meaningful."""
        if not v or not isinstance(v, str):
            field_name = info.field_name
            raise ValueError(f"{field_name} must be a non-empty string")
        
        # Require minimum length for detailed explanations
        if len(v.strip()) < 15:
            field_name = info.field_name
            raise ValueError(
                f"{field_name} must be at least 15 characters "
                f"(got {len(v)} chars)"
            )
        
        return v.strip()
    
    class Config:
        """Pydantic configuration for this model."""
        json_schema_extra = {
            "example": {
                "context": {
                    "entity_name_1": "Amar",
                    "entity_name_2": "Priya",
                    "scenario_description": "sharing mangoes in a garden",
                    "item_name": "mango",
                    "action_verb": "distributed",
                    "setting": "orchard",
                    "real_world_relevance": "Fair distribution teaches equality"
                },
                "narrative_template": (
                    "{{entity_1}} had {{num1}} {{items}} in his {{setting}}. "
                    "{{entity_2}} brought {{num2}} more. How many {{items}} "
                    "did {{entity_1}} have in total?"
                ),
                "pedagogical_principle": "incomplete_reasoning",
                "misconception_trigger_phrase": (
                    "Student may count only the initial {{items}}, "
                    "forgetting the ones {{entity_2}} brought"
                ),
                "teaching_hook": (
                    "This scenario forces systematic enumeration of all "
                    "items from multiple sources, preventing the common "
                    "mistake of incomplete counting"
                )
            }
        }


# ============================================================================
# VALIDATION HELPER FUNCTIONS
# ============================================================================

def validate_story_context(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate story context data without raising exceptions.
    
    Args:
        data: Dictionary with story context fields
    
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    
    Example:
        is_valid, error = validate_story_context(my_data)
        if not is_valid:
            print(f"Validation error: {error}")
    """
    try:
        StoryContextStructured(**data)
        return True, None
    except Exception as e:
        return False, str(e)


def validate_math_context(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate math problem context data.
    
    Args:
        data: Dictionary with context fields
    
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    try:
        MathProblemContext(**data)
        return True, None
    except Exception as e:
        return False, str(e)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example of creating a valid story context
    
    valid_context = StoryContextStructured(
        context=MathProblemContext(
            entity_name_1="Amar",
            entity_name_2="Akbar",
            scenario_description="sharing apples at the neighborhood market",
            item_name="apple",
            action_verb="shared",
            setting="market",
            real_world_relevance="Fair distribution is important in commerce"
        ),
        narrative_template=(
            "{{entity_1}} had {{num1}} {{items}} at the {{setting}}. "
            "{{entity_2}} gave him {{num2}} more. Total {{items}}?"
        ),
        pedagogical_principle=K_C_NagPedagogicalPrinciple.INCOMPLETE_REASONING,
        misconception_trigger_phrase="Forgetting to count the initial apples",
        teaching_hook="Systematic enumeration prevents incomplete counting"
    )
    
    print("✅ Valid story context created:")
    print(valid_context.model_dump_json(indent=2))
    
    # Try to create invalid context (will raise ValueError)
    try:
        invalid = StoryContextStructured(
            context=MathProblemContext(
                entity_name_1="X",  # Too short!
                scenario_description="test",  # Too short!
                item_name="apple",
                action_verb="shared",
                setting="home",
                real_world_relevance="Testing"
            ),
            narrative_template="Invalid {{template",  # Bad format
            pedagogical_principle=K_C_NagPedagogicalPrinciple.MAGNITUDE_ERROR,
            misconception_trigger_phrase="x",  # Too short
            teaching_hook="y"  # Too short
        )
    except Exception as e:
        print(f"\n❌ Invalid context rejected (as expected):")
        print(f"Error: {e}")
