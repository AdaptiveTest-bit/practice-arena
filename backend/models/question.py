"""Pydantic models for questions and responses."""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import hashlib
from .distractor import DistractorSet, TrapInfo
from .cognitive_levels import BloomInfo


class ChapterEnum(str, Enum):
    """Enum of available chapters."""
    # Chapter 1: The Fish Tale
    LARGE_NUMBERS = "large_numbers"
    # Chapter 2: Shapes & Angles
    CLOCK_ANGLES = "clock_angles"
    SYMMETRY = "symmetry"
    ROTATION = "rotation"
    # Chapter 3: How Many Squares
    FRACTION_AREA = "fraction_area"
    # Chapter 4: Parts & Wholes
    FRACTIONS_DECIMALS = "fractions_decimals"
    # Chapter 5: Does it Look the Same
    DICE_LOGIC = "dice_logic"
    NETS = "nets"
    # Chapter 6: Be My Multiple
    FACTORS_MULTIPLES = "factors_multiples"
    # Chapter 7: Can You See Pattern
    DATA_PATTERNS = "data_patterns"
    # Chapter 8: Mapping Your Way
    MAPPING = "mapping"
    # Chapter 9: Boxes & Sketches
    CUBE_COUNTING = "cube_counting"
    GEOMETRY_MEASUREMENT = "geometry_measurement"
    # Chapter 10: Tenths & Hundredths
    # (FRACTIONS_DECIMALS covers this)
    # Chapter 11: Area & Boundary
    # (GEOMETRY_MEASUREMENT covers this)
    # Chapter 12: Smart Charts
    DATA_HANDLING = "data_handling"
    # Chapter 13: Ways to Multiply/Divide
    MULTIPLICATION_DIVISION = "multiplication_division"
    # Chapter 14: How Big/Heavy
    MEASUREMENT = "measurement"


class Question(BaseModel):
    """Standardized Question model for all chapters."""
    
    topic: str = Field(..., description="Topic/subtopic of the question")
    logical_trap: str = Field(..., description="K.C. Nag-style logical trap explanation")
    data_representation: str = Field(..., description="Visual/tabular data representation")
    question_text: str = Field(..., description="The actual question")
    solution_steps: List[str] = Field(..., description="Step-by-step solution")
    answer: str = Field(..., description="Final answer")
    options: Optional[List[str]] = Field(None, description="MCQ options (4 choices)")
    correct_option_index: Optional[int] = Field(None, ge=0, le=3, description="Index of correct answer")
    chapter: ChapterEnum = Field(..., description="Chapter/category")
    distractor_info: Optional[DistractorSet] = Field(None, description="Phase 1: Pedagogical info about distractors")
    trap_info: Optional[TrapInfo] = Field(None, description="Phase 2: Trap classification and difficulty metadata")
    bloom_info: Optional[BloomInfo] = Field(None, description="Phase 3: Bloom's cognitive level and difficulty scaling")
    
    # 🔗 NEW: Rich content for hybrid neuro-symbolic rendering
    rich_html_content: Optional[str] = Field(None, description="Rendered HTML with story context and visuals")
    rich_narrative: Optional[str] = Field(None, description="K.C. Nag story narrative wrapping")
    visual_hints: Optional[List[str]] = Field(None, description="Progressive visual hints for problem-solving")
    
    class Config:
        use_enum_values = True
    
    def get_fingerprint(self) -> str:
        """Generate unique hash for deduplication.
        
        Uses question_text + answer as primary identifiers.
        Returns first 12 chars of SHA256 hash.
        """
        combined = f"{self.question_text}||{self.answer}"
        hash_obj = hashlib.sha256(combined.encode())
        return hash_obj.hexdigest()[:12]
    
    def format_for_display(self) -> str:
        """Format question for console/debug output."""
        output = []
        output.append(f"## TOPIC: {self.topic}")
        output.append(f"\n**The Logical Trap:** {self.logical_trap}")
        output.append(f"\n**Data Representation:**\n{self.data_representation}")
        output.append(f"\n**Question:**\n{self.question_text}")
        
        if self.options:
            output.append(f"\n**Options:**")
            for i, option in enumerate(self.options, 1):
                output.append(f"{chr(64+i)}) {option}")
        
        output.append(f"\n**Solution:**")
        for i, step in enumerate(self.solution_steps, 1):
            output.append(f"{i}. {step}")
        output.append(f"\n**Answer:** {self.answer}\n")
        output.append("---\n")
        return "\n".join(output)


class QuestionResponse(BaseModel):
    """API response for question generation."""
    
    success: bool
    questionId: str = Field(..., description="Unique question ID in this session")
    chapter: str
    chapterName: str
    topic: str
    logicalTrap: str
    dataRepresentation: str
    question: str
    options: Optional[List[str]] = None
    correctOptionIndex: Optional[int] = None
    richNarrative: Optional[str] = Field(None, description="K.C. Nag story context for engagement")
    richHtmlContent: Optional[str] = Field(None, description="SVG/HTML diagram for visual understanding")
    visualHints: Optional[List[str]] = Field(None, description="Progressive hints for problem-solving")


class CheckAnswerRequest(BaseModel):
    """Request body for answer checking."""
    selectedIndex: int = Field(..., ge=0, le=3)
    studentId: Optional[str] = Field(None, description="Optional student ID for adaptive learning tracking")


class CheckAnswerResponse(BaseModel):
    """Response for answer check."""
    
    success: bool
    isCorrect: bool
    correctIndex: int
    solutionSteps: List[str]
    answer: str


class RevealAnswerResponse(BaseModel):
    """Response for revealing answer."""
    
    success: bool
    solutionSteps: List[str]
    answer: str
