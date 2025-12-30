"""
HYBRID NEURO-SYMBOLIC INTEGRATION FRAMEWORK
============================================

This module provides the architectural pattern and utilities for scaling the hybrid 
neuro-symbolic approach (SymPy skeletons + K.C. Nag stories + misconception tracking)
across all 14+ chapters.

Pattern: Each chapter strategy extends BaseChapterStrategy and follows the 5-phase pipeline:
1. Generate deterministic skeleton (SymPy/Python logic)
2. Generate K.C. Nag story context (pedagogical narrative)
3. Generate misconception-based options (adaptive distractors)
4. Render rich question (Jinja2 HTML)
5. Return trackable Question object (enables analytics)
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any, Tuple
from pydantic import BaseModel
import json


class MathSkeleton(BaseModel):
    """Deterministic mathematical structure for a problem."""
    concept: str
    question_type: str
    parameters: Dict[str, Any]
    latex_problem: str
    solution: Any
    steps: List[str]
    explanation: str
    is_valid: bool = True


class StoryContext(BaseModel):
    """K.C. Nag pedagogical narrative context."""
    concept_name: str
    real_world_scenario: str
    character_names: List[str]
    narrative: str
    misconception_hooks: List[str]
    teaching_principles: List[str]


class RichQuestionContent(BaseModel):
    """Complete rich question output."""
    html: str  # Rendered HTML with story + problem + hints
    narrative: str  # K.C. Nag story text
    hints: List[str]  # Progressive hint sequence
    visual_diagram: Optional[str] = None  # SVG or image URL


# ============================================================================
# PHASE IMPLEMENTATIONS FOR EACH CHAPTER
# ============================================================================

class ChapterIntegrationTemplate:
    """
    Template for scaling hybrid neuro-symbolic to each chapter.
    Subclass this and override phase methods.
    """
    
    chapter_name: str = "Template"
    chapter_enum = None  # Set in subclass
    
    def __init__(self):
        """Initialize hybrid system components."""
        # These should be overridden or imported based on chapter
        self.sympy_generator = None  # Chapter-specific SymPy generator
        self.story_generator = None  # KCNagStoryGeneratorLocal
        self.renderer = None  # RichQuestionRenderer
    
    # ========== PHASE 1: DETERMINISTIC SKELETON ==========
    
    def phase_1_generate_skeleton(self) -> MathSkeleton:
        """
        Generate mathematically correct skeleton.
        
        For chapters with SymPy generator:
            - Use deterministic reverse-engineering (e.g., pick answer first)
            - Validate all constraints before returning
            
        For chapters without SymPy:
            - Create minimal MathSkeleton with parameters
            - Ensure logical consistency
        """
        raise NotImplementedError(f"{self.chapter_name}: Implement phase_1 skeleton generation")
    
    # ========== PHASE 2: K.C. NAG STORY ==========
    
    def phase_2_generate_story(self, skeleton: MathSkeleton) -> StoryContext:
        """
        Generate K.C. Nag pedagogical narrative.
        
        K.C. Nag principles:
        - Real-world context relevant to child's life
        - Concrete scenarios before abstract math
        - Narrative that makes numbers "meaningful"
        - Hooks that reveal common misconceptions
        
        Pattern:
        1. Receive skeleton with parameters
        2. Call KCNagStoryGeneratorLocal.generate_story_context(skeleton)
        3. Extract: narrative, teaching_principles, misconception_hooks
        4. Return StoryContext object
        """
        raise NotImplementedError(f"{self.chapter_name}: Implement phase_2 story generation")
    
    # ========== PHASE 3: MISCONCEPTION OPTIONS ==========
    
    def phase_3_generate_misconceptions(
        self, 
        skeleton: MathSkeleton,
        story: StoryContext
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Generate misconception-based distractors.
        
        For each question type:
        1. Identify primary misconception from K.C. Nag literature
        2. Generate 3 misconception options:
           - Option A: Common partial reasoning
           - Option B: Constraint violation
           - Option C: Formula confusion/inversion
        3. Create DistractorInfo with 5-tuple format:
           (value, misconception_type, description, why_wrong, teaching_point)
        
        Return: (options_list, distractor_info_list)
        """
        raise NotImplementedError(f"{self.chapter_name}: Implement phase_3 misconception generation")
    
    # ========== PHASE 4: RICH RENDERING ==========
    
    def phase_4_render_rich_question(
        self,
        skeleton: MathSkeleton,
        story: StoryContext,
        options: List[str],
        misconceptions: List[Dict]
    ) -> RichQuestionContent:
        """
        Render beautiful HTML with story + problem + progressive hints.
        
        Pattern:
        1. Inject skeleton parameters into K.C. Nag story
        2. Render problem with LaTeX
        3. Create progressive hint sequence (3-4 hints)
        4. Package as HTML with styling
        
        Returns: RichQuestionContent with html, narrative, hints
        """
        raise NotImplementedError(f"{self.chapter_name}: Implement phase_4 rich rendering")
    
    # ========== PHASE 5: TRACKABLE QUESTION ==========
    
    def phase_5_create_question(
        self,
        skeleton: MathSkeleton,
        story: StoryContext,
        options: List[str],
        correct_idx: int,
        misconceptions: List[Dict],
        rich_content: RichQuestionContent
    ):
        """
        Create final Question object for database + analytics.
        
        Fields to populate:
        - topic: Specific subtopic (e.g., "Clock Angles - Acute Angle")
        - logical_trap: K.C. Nag misconception description
        - data_representation: Visual/tabular representation
        - question_text: The problem statement
        - solution_steps: Step-by-step solution
        - answer: Final answer
        - options: MCQ choices
        - correct_option_index: Index of correct answer
        - distractor_info: DistractorInfo objects for each option
        - trap_info: TrapInfo for misconception classification
        - bloom_info: BloomInfo for Bloom's level tracking
        - rich_html_content: rendered HTML
        - rich_narrative: K.C. Nag story
        - visual_hints: progressive hints
        
        Returns: Question object ready for database
        """
        raise NotImplementedError(f"{self.chapter_name}: Implement phase_5 question creation")


# ============================================================================
# MISCONCEPTION DATABASES BY CHAPTER
# ============================================================================

MISCONCEPTIONS_BY_CHAPTER = {
    "large_numbers": [
        {
            "type": "place_value_confusion",
            "description": "Confusing lakh/crore place values",
            "why_effective": "Indian numbering is different from Western",
            "hook": "What's the difference between 1,00,000 and 10,00,000?",
        },
        {
            "type": "profit_loss_reversal",
            "description": "Calculating profit instead of loss (or vice versa)",
            "why_effective": "Formula reversal is common",
            "hook": "When cost > selling price, profit or loss?",
        },
    ],
    "clock_angles": [
        {
            "type": "angle_direction_confusion",
            "description": "Confusing clockwise vs counterclockwise angles",
            "why_effective": "Direction change seems like same angle",
            "hook": "Is the angle same if hand moves different direction?",
        },
        {
            "type": "hand_speed_error",
            "description": "Using wrong formula for hand movement",
            "why_effective": "Hour hand moves differently than minute hand",
            "hook": "Does hour hand move as fast as minute hand?",
        },
    ],
    "fractions_decimals": [
        {
            "type": "denominator_addition",
            "description": "Adding denominators when adding fractions",
            "why_effective": "Misapplying the addition algorithm",
            "hook": "Can you add fractions by adding denominators?",
        },
        {
            "type": "decimal_magnitude_error",
            "description": "Treating 0.5 as smaller than 0.05",
            "why_effective": "Comparing decimal digits without place value",
            "hook": "Which is bigger: 0.5 or 0.05?",
        },
    ],
    "geometry_measurement": [
        {
            "type": "perimeter_area_confusion",
            "description": "Confusing perimeter (boundary) with area (interior)",
            "why_effective": "Both measure shapes but differently",
            "hook": "Is perimeter the same as area?",
        },
        {
            "type": "unit_conversion_error",
            "description": "Forgetting to convert units before calculating",
            "why_effective": "Can mix cm, m, km without thinking",
            "hook": "What if sides are in different units?",
        },
    ],
    "data_handling": [
        {
            "type": "average_median_confusion",
            "description": "Treating average as the middle value always",
            "why_effective": "Both are measures of central tendency",
            "hook": "Is average always the middle number?",
        },
        {
            "type": "probability_misunderstanding",
            "description": "Assuming all outcomes equally likely without basis",
            "why_effective": "Neglects actual probability calculations",
            "hook": "Are heads and tails equally likely?",
        },
    ],
    "multiplication_division": [
        {
            "type": "commutative_overextension",
            "description": "Assuming all operations are commutative (5÷2 = 2÷5)",
            "why_effective": "Works for multiplication, not division",
            "hook": "Is 12÷3 the same as 3÷12?",
        },
        {
            "type": "zero_multiplication_confusion",
            "description": "Misapplying zero rules in multiplication",
            "why_effective": "Zero is a special case",
            "hook": "What is 5 × 0? Is it same as 5 × 1?",
        },
    ],
    "measurement": [
        {
            "type": "scale_interpretation_error",
            "description": "Misreading scale on measuring instruments",
            "why_effective": "Requires careful attention to divisions",
            "hook": "If scale goes 0,1,2,3, what's at the middle?",
        },
        {
            "type": "precision_illusion",
            "description": "Claiming more precision than measurement allows",
            "why_effective": "Decimal places suggest false precision",
            "hook": "Can you measure more precisely than instrument allows?",
        },
    ],
    "dice_logic": [
        {
            "type": "opposite_face_assumption",
            "description": "Assuming opposite dice faces without verification",
            "why_effective": "Not always sum to 7",
            "hook": "Do opposite faces of a die always sum to 7?",
        },
        {
            "type": "rotation_confusion",
            "description": "Misunderstanding which face is which after rotation",
            "why_effective": "3D spatial reasoning is hard",
            "hook": "After rolling, which number is on top?",
        },
    ],
    "nets": [
        {
            "type": "net_connectivity_error",
            "description": "Creating nets where faces don't connect properly when folded",
            "why_effective": "Hard to visualize 3D folding",
            "hook": "Does this net fold correctly into a cube?",
        },
        {
            "type": "orientation_mistake",
            "description": "Misjudging how faces align after folding",
            "why_effective": "Requires mental rotation",
            "hook": "After folding, which face touches which?",
        },
    ],
    "cube_counting": [
        {
            "type": "hidden_cube_miscounting",
            "description": "Forgetting to count cubes hidden inside",
            "why_effective": "Only visible cubes are obvious",
            "hook": "Are there cubes inside you can't see?",
        },
        {
            "type": "surface_area_formula_error",
            "description": "Miscalculating with standard surface area formula",
            "why_effective": "Formula easy to get wrong",
            "hook": "How many small faces are on a 3×3×3 cube?",
        },
    ],
    "data_patterns": [
        {
            "type": "pattern_overgeneralization",
            "description": "Assuming pattern continues without checking all cases",
            "why_effective": "First few terms can mislead",
            "hook": "If pattern is 1,2,4,8... is next always 16?",
        },
        {
            "type": "sequence_index_error",
            "description": "Off-by-one errors in finding nth term",
            "why_effective": "0-indexing vs 1-indexing confusion",
            "hook": "Is the 5th term the same as position 5?",
        },
    ],
    "symmetry": [
        {
            "type": "line_placement_error",
            "description": "Drawing line of symmetry incorrectly",
            "why_effective": "Symmetry requires precise placement",
            "hook": "Is every line through shape a line of symmetry?",
        },
        {
            "type": "rotational_symmetry_confusion",
            "description": "Confusing line and rotational symmetry",
            "why_effective": "Both are symmetries but different",
            "hook": "Does rotation look same as reflection?",
        },
    ],
    "rotation": [
        {
            "type": "direction_confusion",
            "description": "Confusing clockwise and counterclockwise rotation",
            "why_effective": "Direction matters for angle",
            "hook": "Is 90° clockwise same as 270° counterclockwise?",
        },
        {
            "type": "rotation_center_error",
            "description": "Rotating around wrong center point",
            "why_effective": "Center of rotation changes result",
            "hook": "Does rotation center affect final position?",
        },
    ],
    "fraction_area": [
        {
            "type": "equal_parts_assumption",
            "description": "Assuming parts are equal when they're not",
            "why_effective": "Visual deception in drawings",
            "hook": "Are all sections the same size?",
        },
        {
            "type": "fraction_of_fraction_error",
            "description": "Misunderstanding nested fractions",
            "why_effective": "Requires two-level thinking",
            "hook": "What's half of one-third?",
        },
    ],
    "mapping": [
        {
            "type": "scale_ratio_confusion",
            "description": "Misapplying map scale to calculate distances",
            "why_effective": "Requires proportional reasoning",
            "hook": "If map says 1:1000, how far is 5cm on map?",
        },
        {
            "type": "coordinate_order_error",
            "description": "Swapping x,y coordinates",
            "why_effective": "Order matters but can be forgotten",
            "hook": "Is (2,3) the same point as (3,2)?",
        },
    ],
}


# ============================================================================
# K.C. NAG PRINCIPLES & TEACHING HOOKS
# ============================================================================

KC_NAG_PRINCIPLES = {
    "concrete_before_abstract": "Start with real objects, move to pictures, then symbols",
    "avoid_rote_learning": "Understand why, not just procedures",
    "use_analogies": "Connect to known concepts",
    "address_misconceptions": "Actively teach what's wrong and why",
    "meaningful_practice": "Vary contexts to avoid procedural fixation",
    "diagnostic_feedback": "Identify where student went wrong",
}

TEACHING_HOOKS_TEMPLATE = {
    "prerequisite_check": "What do students need to know first?",
    "misconception_trigger": "What phrase or question reveals the trap?",
    "aha_moment": "How do we show why the student was wrong?",
    "alternative_method": "Is there another way to solve this?",
    "real_world_connection": "How does this appear in daily life?",
}

# ============================================================================
# VALIDATOR & QUALITY ASSURANCE
# ============================================================================

class HybridQuestionValidator:
    """Validates that questions follow hybrid neuro-symbolic best practices."""
    
    @staticmethod
    def validate_question(question) -> Tuple[bool, List[str]]:
        """
        Validate a question against hybrid standards.
        
        Returns: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check Phase 1: Skeleton
        if not question.answer:
            issues.append("Phase 1 Error: No answer provided")
        if not question.solution_steps:
            issues.append("Phase 1 Error: No solution steps")
        
        # Check Phase 2: Story
        if not question.rich_narrative:
            issues.append("Phase 2 Error: No narrative provided")
        
        # Check Phase 3: Misconceptions
        if not question.distractor_info or len(question.distractor_info) < 3:
            issues.append("Phase 3 Error: Need at least 3 misconception-based distractors")
        
        # Check Phase 4: Rich rendering
        if not question.rich_html_content:
            issues.append("Phase 4 Error: No HTML rendering")
        if not question.visual_hints or len(question.visual_hints) < 2:
            issues.append("Phase 4 Error: Need at least 2 progressive hints")
        
        # Check Phase 5: Analytics
        if not question.logical_trap:
            issues.append("Phase 5 Error: No logical trap description")
        if not question.trap_info:
            issues.append("Phase 5 Error: No trap metadata")
        if not question.bloom_info:
            issues.append("Phase 5 Error: No Bloom's level info")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def quality_score(question) -> float:
        """
        Rate question quality on 0-100 scale.
        
        Criteria:
        - Follows 5-phase pipeline: +20 each
        - Misconception pedagogically sound: +10
        - Progressive hints well-sequenced: +5
        - Real-world K.C. Nag context: +5
        """
        score = 0
        
        # Phase completeness
        if question.answer and question.solution_steps:
            score += 20
        if question.rich_narrative:
            score += 20
        if question.distractor_info and len(question.distractor_info) >= 3:
            score += 20
        if question.rich_html_content:
            score += 20
        if question.logical_trap and question.trap_info and question.bloom_info:
            score += 20
        
        return score


# ============================================================================
# DEPLOYMENT & REGISTRATION
# ============================================================================

CHAPTER_INTEGRATION_STATUS = {
    "factors_multiples": {"status": "COMPLETE", "integrated_file": "factors_multiples_integrated.py"},
    "large_numbers": {"status": "PENDING", "target_file": "large_numbers_integrated.py"},
    "clock_angles": {"status": "PENDING", "target_file": "clock_angles_integrated.py"},
    "symmetry": {"status": "PENDING", "target_file": "symmetry_integrated.py"},
    "rotation": {"status": "PENDING", "target_file": "rotation_integrated.py"},
    "fraction_area": {"status": "PENDING", "target_file": "fraction_area_integrated.py"},
    "fractions_decimals": {"status": "PENDING", "target_file": "fractions_decimals_integrated.py"},
    "dice_logic": {"status": "PENDING", "target_file": "dice_logic_integrated.py"},
    "nets": {"status": "PENDING", "target_file": "nets_integrated.py"},
    "cube_counting": {"status": "PENDING", "target_file": "cube_counting_integrated.py"},
    "geometry_measurement": {"status": "PENDING", "target_file": "geometry_measurement_integrated.py"},
    "data_patterns": {"status": "PENDING", "target_file": "data_patterns_integrated.py"},
    "mapping": {"status": "PENDING", "target_file": "mapping_integrated.py"},
    "data_handling": {"status": "PENDING", "target_file": "data_handling_integrated.py"},
    "measurement": {"status": "PENDING", "target_file": "measurement_integrated.py"},
    "multiplication_division": {"status": "PENDING", "target_file": "multiplication_division_integrated.py"},
}
