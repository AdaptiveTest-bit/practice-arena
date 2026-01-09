"""Factory pattern for creating chapter-specific question generators."""

from typing import Dict, Type
from api.models.quiz import ChapterEnum
from domain.content_generation.generators.base import BaseChapterStrategy


class QuestionGeneratorFactory:
    """Factory for instantiating chapter-specific question generators.
    
    This eliminates the need for giant if-else blocks checking chapter names.
    Uses dependency injection to allow easy testing and extending.
    """
    
    # Registry mapping chapter enums to strategy classes
    # Populated by register() method or imported directly
    _registry: Dict[ChapterEnum, Type[BaseChapterStrategy]] = {}
    
    @classmethod
    def register(cls, chapter: ChapterEnum, strategy_class: Type[BaseChapterStrategy]) -> None:
        """Register a chapter strategy.
        
        Args:
            chapter: The ChapterEnum value
            strategy_class: The strategy class inheriting from BaseChapterStrategy
        """
        if not issubclass(strategy_class, BaseChapterStrategy):
            raise TypeError(f"{strategy_class} must inherit from BaseChapterStrategy")
        cls._registry[chapter] = strategy_class
    
    @classmethod
    def create(cls, chapter: ChapterEnum) -> BaseChapterStrategy:
        """Create and return an instance of the appropriate strategy.
        
        Args:
            chapter: The ChapterEnum value (or string that converts to it)
        
        Returns:
            An instance of the appropriate BaseChapterStrategy subclass
            
        Raises:
            ValueError: If chapter is not registered
        """
        # Convert string to enum if needed
        if isinstance(chapter, str):
            try:
                chapter = ChapterEnum(chapter)
            except ValueError as e:
                raise ValueError(f"Unknown chapter: {chapter}. Available: {list(ChapterEnum)}") from e
        
        if chapter not in cls._registry:
            raise ValueError(
                f"Strategy not registered for chapter: {chapter}. "
                f"Available: {list(cls._registry.keys())}"
            )
        
        strategy_class = cls._registry[chapter]
        return strategy_class()
    
    @classmethod
    def get_all_chapters(cls) -> Dict[ChapterEnum, Type[BaseChapterStrategy]]:
        """Get all registered chapters and their strategy classes.
        
        Returns:
            Dictionary mapping chapters to strategy classes
        """
        return cls._registry.copy()
    
    @classmethod
    def list_chapters(cls) -> list:
        """Get list of all registered chapter IDs.
        
        Returns:
            List of chapter enum values
        """
        return list(cls._registry.keys())
