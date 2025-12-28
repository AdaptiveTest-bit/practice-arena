"""Bloom's Taxonomy Cognitive Levels for Question Classification.

Based on Bloom's Revised Taxonomy (Anderson & Krathwohl, 2001), questions
are classified into 6 cognitive levels ranging from simple recall to complex
creative synthesis. This enables:

1. Learning Progression: Questions scaffold from Remember → Create
2. Cognitive Load: Students progress to higher-order thinking
3. Assessment Alignment: Match teaching objectives to question difficulty
4. Adaptive Learning: Customize learning paths by cognitive level

Cognitive Levels:
1. REMEMBER: Recall facts and basic concepts (knowledge)
2. UNDERSTAND: Explain ideas or concepts (comprehension)
3. APPLY: Use information in new situations (application)
4. ANALYZE: Draw connections among ideas (analysis)
5. EVALUATE: Justify a choice or decision (evaluation)
6. CREATE: Produce new or original work (synthesis)
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class BloomLevel(str, Enum):
    """Bloom's Revised Taxonomy Cognitive Levels (6 levels)."""
    
    REMEMBER = "remember"      # L1: Recall facts (Who? What? When? Where?)
    UNDERSTAND = "understand"  # L2: Explain concepts (Why? How?)
    APPLY = "apply"            # L3: Use knowledge in new contexts
    ANALYZE = "analyze"        # L4: Break down & find relationships
    EVALUATE = "evaluate"      # L5: Justify decisions & defend positions
    CREATE = "create"          # L6: Synthesize new ideas from components


class BloomInfo(BaseModel):
    """Comprehensive Bloom's cognitive level classification for a question."""
    
    bloom_level: BloomLevel = Field(
        ..., 
        description="Primary Bloom's cognitive level (1-6)"
    )
    level_name: str = Field(
        ...,
        description="Human-readable level name"
    )
    description: str = Field(
        ...,
        description="What students do at this level"
    )
    cognitive_verbs: list[str] = Field(
        ...,
        description="Action verbs associated with this level"
    )
    example_activities: list[str] = Field(
        ...,
        description="Example question types/activities at this level"
    )
    minimum_difficulty: int = Field(
        ...,
        ge=1, le=5,
        description="Minimum trap difficulty for this level (1-5)"
    )
    estimated_time_seconds: int = Field(
        ...,
        description="Estimated time to solve in seconds"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "bloom_level": "remember",
                "level_name": "Remember",
                "description": "Student recalls facts and definitions",
                "cognitive_verbs": ["define", "recall", "list"],
                "example_activities": ["name the opposite face", "list dice values"],
                "minimum_difficulty": 1,
                "estimated_time_seconds": 30
            }
        }


# Bloom's Level Definitions (Complete Taxonomy)
BLOOM_DEFINITIONS = {
    BloomLevel.REMEMBER: BloomInfo(
        bloom_level=BloomLevel.REMEMBER,
        level_name="Remember",
        description="Student recalls facts, definitions, and basic concepts without elaboration",
        cognitive_verbs=["define", "recall", "list", "name", "identify", "state"],
        example_activities=[
            "What is the value on the opposite face?",
            "List all factors of 12",
            "Name the shape when unfolded",
            "Identify the symmetry type"
        ],
        minimum_difficulty=1,
        estimated_time_seconds=30
    ),
    
    BloomLevel.UNDERSTAND: BloomInfo(
        bloom_level=BloomLevel.UNDERSTAND,
        level_name="Understand",
        description="Student explains concepts, interprets, translates, and grasps meaning",
        cognitive_verbs=["explain", "interpret", "summarize", "classify", "compare", "describe"],
        example_activities=[
            "Explain why opposite faces sum to 7",
            "Classify shapes by symmetry properties",
            "Compare two fractions using visualization",
            "Describe the pattern in this sequence",
            "Why does rotating 180° equal this image?"
        ],
        minimum_difficulty=1,
        estimated_time_seconds=45
    ),
    
    BloomLevel.APPLY: BloomInfo(
        bloom_level=BloomLevel.APPLY,
        level_name="Apply",
        description="Student uses information in new situations; applies rules, concepts, and principles",
        cognitive_verbs=["use", "solve", "calculate", "apply", "compute", "show"],
        example_activities=[
            "Calculate missing data value using formula",
            "Find LCM of three numbers",
            "Calculate clock angle at given time",
            "Apply scale to convert map distance",
            "Solve multi-step geometry problem"
        ],
        minimum_difficulty=2,
        estimated_time_seconds=60
    ),
    
    BloomLevel.ANALYZE: BloomInfo(
        bloom_level=BloomLevel.ANALYZE,
        level_name="Analyze",
        description="Student distinguishes relationships, breaks down components, identifies patterns",
        cognitive_verbs=["analyze", "break down", "compare", "contrast", "distinguish", "categorize"],
        example_activities=[
            "Analyze which net folds correctly and why others fail",
            "Distinguish between complete and incomplete data",
            "Compare two solution approaches - which is more efficient?",
            "Break down the multi-step word problem into parts",
            "Identify the error in this flawed calculation"
        ],
        minimum_difficulty=2,
        estimated_time_seconds=90
    ),
    
    BloomLevel.EVALUATE: BloomInfo(
        bloom_level=BloomLevel.EVALUATE,
        level_name="Evaluate",
        description="Student justifies decisions, argues for position, evaluates validity of claims",
        cognitive_verbs=["evaluate", "justify", "defend", "critique", "argue", "judge"],
        example_activities=[
            "Is this solution method valid? Justify your answer.",
            "Evaluate: Which approach best solves this constraint problem?",
            "Defend your choice of operation in this word problem",
            "Critique this student's solution - where's the error?",
            "Is this claim about factors always true? Why/why not?"
        ],
        minimum_difficulty=3,
        estimated_time_seconds=120
    ),
    
    BloomLevel.CREATE: BloomInfo(
        bloom_level=BloomLevel.CREATE,
        level_name="Create",
        description="Student synthesizes elements to create new patterns, structures, or original work",
        cognitive_verbs=["create", "design", "construct", "develop", "compose", "generate"],
        example_activities=[
            "Design a dice problem with these constraints",
            "Create a number pattern with specific properties",
            "Develop a multi-step word problem for this topic",
            "Construct a cube net with labeled faces",
            "Compose a symmetry pattern using given shapes"
        ],
        minimum_difficulty=4,
        estimated_time_seconds=180
    )
}


def get_bloom_info(bloom_level: BloomLevel) -> BloomInfo:
    """Retrieve Bloom's level information by level.
    
    Args:
        bloom_level: The Bloom's cognitive level
        
    Returns:
        BloomInfo object with comprehensive level details
        
    Raises:
        ValueError: If bloom_level is not in valid enum
        
    Example:
        >>> info = get_bloom_info(BloomLevel.ANALYZE)
        >>> print(info.description)
    """
    if bloom_level not in BLOOM_DEFINITIONS:
        raise ValueError(f"Invalid Bloom's level: {bloom_level}")
    return BLOOM_DEFINITIONS[bloom_level]


def get_bloom_by_name(name: str) -> Optional[BloomLevel]:
    """Get Bloom's level by name (case-insensitive).
    
    Args:
        name: The level name (e.g., "Remember", "Apply", "Create")
        
    Returns:
        BloomLevel enum value or None if not found
        
    Example:
        >>> level = get_bloom_by_name("analyze")
        >>> level == BloomLevel.ANALYZE
    """
    for level in BloomLevel:
        if level.value.lower() == name.lower():
            return level
    return None


# Bloom's Level Difficulty Mapping
# Maps Bloom's levels to typical trap difficulty ranges
BLOOM_TO_DIFFICULTY_MAP = {
    BloomLevel.REMEMBER: (1, 1),      # Difficulty 1 only
    BloomLevel.UNDERSTAND: (1, 2),    # Difficulty 1-2
    BloomLevel.APPLY: (2, 3),         # Difficulty 2-3
    BloomLevel.ANALYZE: (3, 4),       # Difficulty 3-4
    BloomLevel.EVALUATE: (4, 5),      # Difficulty 4-5
    BloomLevel.CREATE: (4, 5)         # Difficulty 4-5
}


def get_difficulty_range_for_bloom(bloom_level: BloomLevel) -> tuple[int, int]:
    """Get the appropriate difficulty range for a Bloom's level.
    
    Args:
        bloom_level: The cognitive level
        
    Returns:
        Tuple of (min_difficulty, max_difficulty)
        
    Example:
        >>> min_d, max_d = get_difficulty_range_for_bloom(BloomLevel.APPLY)
        >>> min_d, max_d
        (2, 3)
    """
    return BLOOM_TO_DIFFICULTY_MAP.get(bloom_level, (1, 5))
