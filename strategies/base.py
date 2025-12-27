"""Base strategy class for chapter-specific question generators."""

from abc import ABC, abstractmethod
from typing import List
from models.question import Question, ChapterEnum
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
        """Ensure all MCQ options are unique. Removes duplicates, keeps 4 options.
        
        Args:
            options: List of option strings (may contain duplicates)
            max_attempts: Max regeneration attempts (unused currently, kept for API compatibility)
        
        Returns:
            List of 4 unique strings
        """
        # Remove exact duplicates while preserving order
        seen = set()
        unique = []
        for option in options:
            if option not in seen:
                unique.append(option)
                seen.add(option)
        
        # Ensure exactly 4 unique options
        while len(unique) < 4:
            unique.append(f"Option {len(unique) + 1}")
        
        # Return first 4
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
