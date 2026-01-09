"""Base strategy class for chapter-specific question generators."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional, Any
from api.models.quiz import Question, ChapterEnum
from api.models.distractor import DistractorSet, DistractorInfo, MisconceptionType, TrapInfo, TrapType, MISCONCEPTION_TO_TRAP_MAP
from api.models.cognitive_levels import BloomLevel, BloomInfo, get_bloom_info
import random


class BaseChapterStrategy(ABC):
    """Abstract base class for chapter-specific generators.
    
    Implements common utilities and defines interface for all chapter strategies.
    """
    
    chapter: ChapterEnum
    chapter_name: str
    description: str
    
    def __init__(self):
        """Initialize the strategy with chapter metadata."""
        if not hasattr(self, 'chapter'):
            raise NotImplementedError(f"{self.__class__.__name__} must define 'chapter' attribute")
        if not hasattr(self, 'chapter_name'):
            raise NotImplementedError(f"{self.__class__.__name__} must define 'chapter_name' attribute")
    
    @abstractmethod
    def generate(self) -> Question:
        """Generate a question for this chapter.
        
        Returns:
            Question: A fully formed question with all required fields.
        """
        pass
    
    # ============================================================================
    # HELPER UTILITIES - Used by all subclasses
    # ============================================================================
    
    @staticmethod
    def ensure_unique_options(options: List[str], max_attempts: int = 10) -> List[str]:
        """Ensure all MCQ options are unique. Removes duplicates, generates fallbacks if needed.
        
        Args:
            options: List of option strings (may contain duplicates)
            max_attempts: Max generation attempts for fallback options
        
        Returns:
            List of 4 unique strings
        
        Note:
            If fewer than 4 unique options exist after deduplication, this method
            will attempt to generate nearby values or use placeholders as last resort.
        """
        # Remove exact duplicates while preserving order
        seen = set()
        unique = []
        for option in options:
            option_str = str(option)  # Convert to string if not already
            if option_str not in seen:
                unique.append(option_str)
                seen.add(option_str)
        
        # If we have 4 or more unique options, we're good
        if len(unique) >= 4:
            return unique[:4]
        
        # CRITICAL: Generate pedagogical fallbacks - NO PLACEHOLDERS ALLOWED
        # Strategy 1: If options are numeric, generate mathematically meaningful nearby values
        try:
            # Extract all numeric values from existing options
            numeric_values = []
            for opt in unique:
                try:
                    # Handle different numeric formats
                    cleaned = str(opt).strip().replace(',', '')
                    if cleaned.replace('.', '').replace('-', '').replace('+', '').isdigit():
                        numeric_values.append(float(cleaned))
                except (ValueError, TypeError):
                    continue
            
            if numeric_values and len(unique) < 4:
                # Use statistical approach to generate meaningful distractors
                min_val = min(numeric_values)
                max_val = max(numeric_values)
                avg_val = sum(numeric_values) / len(numeric_values)
                
                # Generate candidates based on mathematical relationships
                candidates = []
                
                # 1. Arithmetic variations (±10%, ±20%, ±50%)
                for val in numeric_values:
                    if val != 0:
                        candidates.extend([
                            val * 0.9,   # 10% less
                            val * 1.1,   # 10% more
                            val * 0.8,   # 20% less
                            val * 1.2,   # 20% more
                            val * 0.5,   # Half
                            val * 2,     # Double
                        ])
                
                # 2. Common misconception patterns
                if len(numeric_values) >= 2:
                    candidates.extend([
                        numeric_values[0] + numeric_values[-1],  # Sum
                        numeric_values[0] * numeric_values[-1],  # Product
                        abs(numeric_values[0] - numeric_values[-1]),  # Difference
                    ])
                
                # 3. Nearby integers (for cleaner options)
                for val in numeric_values:
                    candidates.extend([val - 1, val + 1, val - 2, val + 2])
                
                # 4. Round numbers near the values
                for val in numeric_values:
                    base_10 = 10 ** len(str(int(abs(val))))
                    candidates.extend([
                        (int(val / base_10) + 1) * base_10,
                        (int(val / base_10) - 1) * base_10,
                    ])
                
                # Clean candidates: remove duplicates, negatives (for most contexts), and format
                for candidate in candidates:
                    if len(unique) >= 4:
                        break
                    
                    # Format candidate
                    if candidate == int(candidate):
                        candidate_str = str(int(candidate))
                    else:
                        candidate_str = f"{candidate:.2f}".rstrip('0').rstrip('.')
                    
                    # Add if valid and unique
                    if candidate_str not in seen and candidate > 0:  # Positive values only
                        unique.append(candidate_str)
                        seen.add(candidate_str)
        
        except (ValueError, TypeError, ZeroDivisionError):
            pass  # If numeric strategy fails, continue to next strategy
        
        # Strategy 2: For non-numeric or if still short, generate contextual fallbacks
        # This should RARELY be needed if distractor generation is done properly
        if len(unique) < 4:
            # Last resort: Use mathematical expressions or contextual hints
            # These are better than "Option X" but signal that distractor generation needs improvement
            contextual_fallbacks = [
                "Recheck calculation",
                "Try another method",
                "Review the question",
                "Check your work",
            ]
            
            for fallback in contextual_fallbacks:
                if len(unique) >= 4:
                    break
                if fallback not in seen:
                    unique.append(fallback)
                    seen.add(fallback)
        
        # Final safety: If we STILL don't have 4 options, something is seriously wrong
        # Generate numeric sequence as absolute last resort (should never happen in production)
        attempt = 1
        while len(unique) < 4 and attempt < 100:
            emergency_option = str(attempt * 10)  # Generate 10, 20, 30, etc.
            if emergency_option not in seen:
                unique.append(emergency_option)
                seen.add(emergency_option)
            attempt += 1
        
        # Return first 4 unique options
        return unique[:4]
    
    @staticmethod
    def shuffle_options_keep_correct(correct_answer: str, distractors: List[str]) -> tuple:
        """Shuffle options and track which index the correct answer ended up at.
        
        Args:
            correct_answer: The correct answer string
            distractors: List of distractor strings (should be 3 items)
        
        Returns:
            Tuple of (shuffled_options_list, correct_answer_index)
        """
        options = BaseChapterStrategy.ensure_unique_options([correct_answer] + distractors)
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        return options, correct_idx
    
    @staticmethod
    def validate_unique_option_distractors(option_distractors: Dict[int, tuple]) -> bool:
        """
        Validate that option_distractors dict has unique values.
        
        Args:
            option_distractors: Dict mapping index to (value, misconception, desc, why, teaching) tuples
            
        Returns:
            True if all option values are unique, False otherwise
        """
        values = [opt[0] for opt in option_distractors.values()]
        return len(values) == len(set(values))
    
    @staticmethod
    def ensure_unique_option_values(options_list: List[str]) -> List[str]:
        """
        Ensure option values are unique by deduplicating and padding if needed.
        
        Args:
            options_list: List of option strings that may have duplicates
            
        Returns:
            List of exactly 4 unique option strings
            
        Note:
            This function delegates to ensure_unique_options() which has
            robust pedagogical fallback logic. NO PLACEHOLDERS.
        """
        # Delegate to the improved ensure_unique_options method
        return BaseChapterStrategy.ensure_unique_options(options_list)
    
    @staticmethod
    def create_categorized_distractors(
        correct_answer: str,
        misconception_map: Dict[MisconceptionType, str]
    ) -> Tuple[List[str], int, DistractorSet]:
        """Create distractors with misconception categorization (PHASE 1).
        
        Args:
            correct_answer: The correct answer string
            misconception_map: {
                MisconceptionType.OPPOSITE_CONFUSION: "₹20",
                MisconceptionType.INCOMPLETE_REASONING: "₹10",
                MisconceptionType.ARITHMETIC_ERROR: "₹25"
            }
        
        Returns:
            (shuffled_options_list, correct_index, distractor_info_for_teachers)
        
        Example:
            options, idx, distractor_info = create_categorized_distractors(
                correct_answer="₹25",
                misconception_map={
                    MisconceptionType.OPPOSITE_CONFUSION: "₹15",
                    MisconceptionType.INCOMPLETE_REASONING: "₹10",
                    MisconceptionType.ARITHMETIC_ERROR: "₹30"
                }
            )
        """
        # Create distractor objects with metadata
        distractor_info_list = []
        distractor_values = []
        
        for misconception_type, distractor_value in misconception_map.items():
            distractor_info_list.append(
                DistractorInfo(
                    value=distractor_value,
                    misconception_type=misconception_type,
                    why_wrong=BaseChapterStrategy._get_why_wrong_explanation(misconception_type),
                    teaching_point=BaseChapterStrategy._get_teaching_point(misconception_type)
                )
            )
            distractor_values.append(distractor_value)
        
        # Create distractor set
        distractor_set = DistractorSet(
            correct_answer=correct_answer,
            distractors=distractor_info_list
        )
        
        # Ensure unique options
        all_options = BaseChapterStrategy.ensure_unique_options(
            [correct_answer] + distractor_values
        )
        
        # Shuffle and find correct index
        random.shuffle(all_options)
        correct_idx = all_options.index(correct_answer)
        
        return all_options, correct_idx, distractor_set
    
    @staticmethod
    def create_trap_info(
        misconception_type: MisconceptionType,
        difficulty: Optional[int] = None,
        custom_description: Optional[str] = None,
        custom_why_effective: Optional[str] = None,
        custom_how_to_avoid: Optional[str] = None
    ) -> TrapInfo:
        """Convert Phase 1 misconception to Phase 2 trap info (PHASE 2).
        
        Maps a misconception type to its corresponding trap type and generates
        metadata about the trap for assessment and pedagogy.
        
        Args:
            misconception_type: The primary misconception type
            difficulty: Optional override for difficulty (1-5)
            custom_description: Optional custom description of the trap
            custom_why_effective: Optional custom explanation of why it works
            custom_how_to_avoid: Optional custom explanation of how to avoid it
        
        Returns:
            TrapInfo object with trap metadata
        
        Example:
            trap_info = create_trap_info(
                MisconceptionType.OPPOSITE_CONFUSION,
                difficulty=3,
                custom_description="Student confuses which face is opposite"
            )
        """
        from api.models.distractor import MISCONCEPTION_TO_TRAP_MAP
        
        # Map misconception to trap type
        trap_type = MISCONCEPTION_TO_TRAP_MAP.get(
            misconception_type,
            TrapType.CALCULATION_TRAP  # Fallback
        )
        
        # Generate trap name from type
        trap_name_map = {
            TrapType.CALCULATION_TRAP: "Calculation Shortcut",
            TrapType.CONTEXT_TRAP: "Context Misunderstanding",
            TrapType.ASSUMPTION_TRAP: "Unstated Assumption",
            TrapType.VISUAL_TRAP: "Visual Misinterpretation",
            TrapType.UNIT_TRAP: "Unit Handling Error",
            TrapType.INVERSE_TRAP: "Inverse Operation Trap",
            TrapType.OVERGENERALIZATION_TRAP: "Overgeneralization",
            TrapType.SEQUENCE_TRAP: "Sequence Violation",
        }
        trap_name = trap_name_map.get(trap_type, "Unknown Trap")
        
        # Default difficulty based on trap type
        if difficulty is None:
            trap_difficulty_map = {
                TrapType.CALCULATION_TRAP: 2,
                TrapType.CONTEXT_TRAP: 2,
                TrapType.ASSUMPTION_TRAP: 2,
                TrapType.VISUAL_TRAP: 3,
                TrapType.UNIT_TRAP: 2,
                TrapType.INVERSE_TRAP: 3,
                TrapType.OVERGENERALIZATION_TRAP: 3,
                TrapType.SEQUENCE_TRAP: 2,
            }
            difficulty = trap_difficulty_map.get(trap_type, 2)
        
        # Ensure difficulty is in valid range
        difficulty = max(1, min(5, difficulty))
        
        # Use custom or default descriptions
        description = custom_description or f"Student misunderstands {misconception_type.value.replace('_', ' ')}"
        why_effective = custom_why_effective or f"This trap exploits confusion about {trap_type.value.replace('_', ' ')}"
        how_to_avoid = custom_how_to_avoid or f"Carefully review the {trap_type.value.replace('_', ' ')} concept"
        
        return TrapInfo(
            trap_type=trap_type,
            trap_name=trap_name,
            difficulty=difficulty,
            description=description,
            why_effective=why_effective,
            how_to_avoid=how_to_avoid
        )
    
    @staticmethod
    def create_bloom_info(
        bloom_level: BloomLevel,
        trap_difficulty: Optional[int] = None
    ) -> BloomInfo:
        """Convert Bloom's cognitive level to Phase 3 bloom info (PHASE 3).
        
        Maps a Bloom's cognitive level to comprehensive assessment metadata
        including cognitive verbs, example activities, and time estimates.
        
        Args:
            bloom_level: The Bloom's cognitive level (Remember through Create)
            trap_difficulty: Optional trap difficulty (1-5) - used to ensure
                             consistency with trap classification
        
        Returns:
            BloomInfo object with complete Bloom's level metadata
        
        Example:
            bloom_info = create_bloom_info(
                BloomLevel.ANALYZE,
                trap_difficulty=4
            )
        """
        # Get the predefined Bloom info for this level
        bloom_info = get_bloom_info(bloom_level)
        
        # Verify trap difficulty aligns with Bloom's level if provided
        if trap_difficulty is not None:
            from api.models.cognitive_levels import BLOOM_TO_DIFFICULTY_MAP
            min_diff, max_diff = BLOOM_TO_DIFFICULTY_MAP.get(
                bloom_level, 
                (1, 5)
            )
            # Note: We don't enforce this - just validate it makes sense
            # (higher Bloom levels should have moderate-to-high trap difficulty)
            if trap_difficulty < min_diff:
                # Warn: trap difficulty seems too low for this Bloom level
                pass
        
        return bloom_info
    
    @staticmethod
    def assign_bloom_level(
        question_complexity: str,
        trap_difficulty: int,
        requires_justification: bool = False,
        requires_synthesis: bool = False
    ) -> BloomLevel:
        """Intelligently assign Bloom's level based on question characteristics.
        
        Uses trap difficulty and question characteristics to assign appropriate
        cognitive level. This is useful when creating questions programmatically.
        
        Args:
            question_complexity: One of 'simple', 'moderate', 'complex'
            trap_difficulty: The trap difficulty (1-5)
            requires_justification: Does question require student to justify?
            requires_synthesis: Does question require creating new content?
        
        Returns:
            BloomLevel enum value
        
        Example:
            level = assign_bloom_level(
                question_complexity='moderate',
                trap_difficulty=3,
                requires_justification=True
            )
            # Returns BloomLevel.ANALYZE
        """
        # Logic for assigning Bloom's level
        if requires_synthesis:
            # Synthesis/Create is highest level
            return BloomLevel.CREATE
        elif requires_justification:
            # Justification requires evaluation
            return BloomLevel.EVALUATE
        
        # Map based on complexity and difficulty
        if question_complexity == 'simple' and trap_difficulty <= 1:
            return BloomLevel.REMEMBER
        elif question_complexity == 'simple' and trap_difficulty <= 2:
            return BloomLevel.UNDERSTAND
        elif question_complexity == 'moderate' and trap_difficulty <= 2:
            return BloomLevel.UNDERSTAND
        elif question_complexity == 'moderate' and trap_difficulty <= 3:
            return BloomLevel.APPLY
        elif question_complexity == 'moderate' and trap_difficulty <= 4:
            return BloomLevel.ANALYZE
        elif question_complexity == 'complex' and trap_difficulty <= 2:
            return BloomLevel.APPLY
        elif question_complexity == 'complex' and trap_difficulty <= 3:
            return BloomLevel.ANALYZE
        elif question_complexity == 'complex' and trap_difficulty <= 4:
            return BloomLevel.EVALUATE
        else:
            # Highest complexity and difficulty
            return BloomLevel.EVALUATE
    
    @staticmethod
    def _get_why_wrong_explanation(misconception_type: MisconceptionType) -> str:
        """Get teacher-facing explanation of why this misconception occurs."""
        explanations = {
            MisconceptionType.OPPOSITE_CONFUSION: 
                "Student used opposite/inverse value instead of shown value",
            MisconceptionType.UNIVERSAL_VS_SPECIFIC:
                "Student generalized from specific example instead of universal rule",
            MisconceptionType.INCOMPLETE_REASONING:
                "Student stopped calculation before final step",
            MisconceptionType.ARITHMETIC_ERROR:
                "Student made arithmetic/calculation mistake",
            MisconceptionType.REFERENCE_POINT_ERROR:
                "Student operated on wrong amount (original vs remaining)",
            MisconceptionType.OPERATION_DIRECTION:
                "Student used wrong direction (multiply vs divide, or addition vs subtraction)",
            MisconceptionType.OPERATION_SELECTION:
                "Student selected entirely wrong operation type",
            MisconceptionType.FORMULA_MISAPPLICATION:
                "Student applied wrong formula for this concept",
            MisconceptionType.FORMULA_CONFUSION:
                "Student confused similar formulas for different concepts",
            MisconceptionType.UNIT_ERROR:
                "Student forgot or mishandled units of measurement",
            MisconceptionType.LOGICAL_DISCONNECT:
                "Student broke logical chain in multi-step problem",
            MisconceptionType.CONSTRAINT_VIOLATION:
                "Student ignored given constraints or conditions",
            MisconceptionType.PATTERN_MISIDENTIFICATION:
                "Student identified wrong pattern in sequence/data",
            MisconceptionType.SIMILAR_CONCEPT_ERROR:
                "Student confused with similar but different concept",
        }
        return explanations.get(misconception_type, "Common misconception in this area")
    
    @staticmethod
    def _get_teaching_point(misconception_type: MisconceptionType) -> str:
        """Get teaching point to address this misconception."""
        teaching_points = {
            MisconceptionType.OPPOSITE_CONFUSION:
                "Remember: Use the SHOWN/GIVEN value, not its opposite",
            MisconceptionType.UNIVERSAL_VS_SPECIFIC:
                "This rule applies to ALL cases, not just the example shown",
            MisconceptionType.INCOMPLETE_REASONING:
                "After calculating intermediate result, check: does the problem ask for more steps?",
            MisconceptionType.ARITHMETIC_ERROR:
                "Verify calculation by using a different method or checking units",
            MisconceptionType.REFERENCE_POINT_ERROR:
                "Mark clearly: 'Remaining after step 1' is the new base for step 2",
            MisconceptionType.OPERATION_DIRECTION:
                "Going smaller→larger: DIVIDE. Going larger→smaller: MULTIPLY. Going up: ADD. Going down: SUBTRACT",
            MisconceptionType.OPERATION_SELECTION:
                "Identify what the problem is asking: Do I combine (add/multiply) or compare (subtract/divide)?",
            MisconceptionType.FORMULA_MISAPPLICATION:
                "Revisit what each formula measures: Area (space inside), Perimeter (boundary only), Volume (3D space)",
            MisconceptionType.FORMULA_CONFUSION:
                "Create a comparison chart showing what makes each formula different",
            MisconceptionType.UNIT_ERROR:
                "Always write units alongside numbers. Convert units before combining different measurements",
            MisconceptionType.LOGICAL_DISCONNECT:
                "Draw a diagram or write down what you know. Ensure each step connects to the next",
            MisconceptionType.CONSTRAINT_VIOLATION:
                "Reread problem. Does your answer make sense in the real-world context?",
            MisconceptionType.PATTERN_MISIDENTIFICATION:
                "Test the pattern you identified with 2-3 more examples before assuming it's correct",
            MisconceptionType.SIMILAR_CONCEPT_ERROR:
                "What is DIFFERENT between these two concepts? Write down the differences",
        }
        return teaching_points.get(misconception_type, "Review the core concept")
    
    # ============================================================================
    # VALIDATION
    # ============================================================================
    
    def _validate_question(self, question: Question) -> None:
        """Validate that a question has all required fields.
        
        Args:
            question: The question to validate
            
        Raises:
            ValueError: If any required field is missing
        """
        required_fields = [
            'topic', 'logical_trap', 'data_representation', 'question_text',
            'solution_steps', 'answer', 'chapter'
        ]
        
        for field in required_fields:
            value = getattr(question, field, None)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                raise ValueError(f"Question missing required field: {field}")
        
        # Validate MCQ fields are consistent
        if question.options is not None:
            if len(question.options) != 4:
                raise ValueError(f"Expected 4 options, got {len(question.options)}")
            if question.correct_option_index is None:
                raise ValueError("If options provided, correct_option_index must be set")
            if question.correct_option_index < 0 or question.correct_option_index > 3:
                raise ValueError(f"correct_option_index must be 0-3, got {question.correct_option_index}")
            # Check correct answer exists in options
            if question.answer not in question.options:
                raise ValueError(f"Answer '{question.answer}' not found in options")
