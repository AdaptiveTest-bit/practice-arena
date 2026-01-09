"""
Question Bank Loader Service
============================

This module provides infrastructure to load, manage, and query pre-authored
questions from YAML question banks. It enables:

1. Loading YAML questions with rich metadata
2. Filtering by multiple criteria (category, difficulty, Bloom's level, concept)
3. Sampling questions with weighted distributions
4. Constructing Question objects from YAML data with all rich content

Architecture:
    QuestionBank: Loads and manages YAML data
    ├─ get_by_category_difficulty(category, difficulty)
    ├─ get_by_bloom_level(bloom_level)
    ├─ get_by_concept(concept)
    ├─ get_random_sample(filters, count)
    └─ get_all_questions()

    QuestionConstructor: Converts YAML → Question objects
    ├─ construct_from_yaml(q_data, narrative_engine)
    └─ _generate_html_rendering(question_data)

Philosophy:
    - Load high-quality, pre-authored questions first (60% of generation)
    - Use dynamic generation for remaining (40%) to ensure variety
    - Maintain full pedagogical metadata from authors
    - Enable filtering for adaptive learning (difficulty, bloom level, concept)
"""

import yaml
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import random

from api.models.quiz import Question
from api.models.distractor import (
    DistractorSet, TrapInfo, DistractorInfo, MisconceptionType,
    TrapType, MISCONCEPTION_TO_TRAP_MAP
)
from api.models.cognitive_levels import BloomInfo, BloomLevel


@dataclass
class QuestionMetadata:
    """Metadata about a question from the bank"""
    id: str
    category: str  # factors_multiples, assertion_reason, problem_solving
    bloom_level: str  # REMEMBER, UNDERSTAND, APPLY, ANALYZE, EVALUATE, CREATE
    difficulty: int  # 1-5
    concept: str  # core concept being tested
    misconception: str  # common error students make
    misconception_type: str  # error category
    teaching_point: str  # what to emphasize
    real_world_context: Optional[str] = None


class QuestionBank:
    """
    Loads and manages questions from YAML bank files.
    
    Features:
        - Load questions from YAML with rich metadata
        - Filter by category, difficulty, bloom level, concept
        - Random sampling with weighted distributions
        - Comprehensive question lookup
    """

    def __init__(self, filepath: str):
        """
        Initialize QuestionBank from YAML file.
        
        Args:
            filepath: Path to YAML question bank file
            
        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML format is invalid
        """
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"Question bank file not found: {filepath}")
        
        self._questions_by_id: Dict[str, Dict[str, Any]] = {}
        self._metadata_index: Dict[str, QuestionMetadata] = {}
        self._load_yaml()

    def _load_yaml(self):
        """Load and index YAML question bank file."""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'questions' not in data:
            raise ValueError("YAML must contain 'questions' root key")
        
        # Flatten nested structure: questions -> categories -> difficulty -> [questions]
        questions_root = data['questions']
        
        for category, category_data in questions_root.items():
            if isinstance(category_data, dict):
                for difficulty_level, difficulty_data in category_data.items():
                    if isinstance(difficulty_data, list):
                        for q_data in difficulty_data:
                            if 'id' in q_data:
                                q_id = q_data['id']
                                self._questions_by_id[q_id] = q_data
                                
                                # Create metadata index
                                metadata = QuestionMetadata(
                                    id=q_id,
                                    category=category,
                                    bloom_level=q_data.get('bloom_level', 'UNDERSTAND'),
                                    difficulty=q_data.get('difficulty', 1),
                                    concept=q_data.get('concept', ''),
                                    misconception=q_data.get('misconception', ''),
                                    misconception_type=q_data.get('misconception_type', ''),
                                    teaching_point=q_data.get('teaching_point', ''),
                                    real_world_context=q_data.get('real_world_context'),
                                )
                                self._metadata_index[q_id] = metadata

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all questions in a category.
        
        Args:
            category: Category name (e.g., 'factors_multiples')
            
        Returns:
            List of question dictionaries
        """
        return [
            q for q_id, q in self._questions_by_id.items()
            if self._metadata_index[q_id].category == category
        ]

    def get_by_category_difficulty(self, category: str, difficulty: int) -> List[Dict[str, Any]]:
        """
        Get questions filtered by category and difficulty.
        
        Args:
            category: Category name
            difficulty: Difficulty level (1-5)
            
        Returns:
            List of matching question dictionaries
        """
        return [
            q for q_id, q in self._questions_by_id.items()
            if (self._metadata_index[q_id].category == category and
                self._metadata_index[q_id].difficulty == difficulty)
        ]

    def get_by_bloom_level(self, bloom_level: str) -> List[Dict[str, Any]]:
        """
        Get questions at specific Bloom's cognitive level.
        
        Args:
            bloom_level: Bloom level (REMEMBER, UNDERSTAND, APPLY, ANALYZE, EVALUATE, CREATE)
            
        Returns:
            List of matching question dictionaries
        """
        return [
            q for q_id, q in self._questions_by_id.items()
            if self._metadata_index[q_id].bloom_level == bloom_level
        ]

    def get_by_concept(self, concept: str) -> List[Dict[str, Any]]:
        """
        Get all questions testing specific concept.
        
        Args:
            concept: Concept name
            
        Returns:
            List of matching question dictionaries
        """
        return [
            q for q_id, q in self._questions_by_id.items()
            if concept.lower() in self._metadata_index[q_id].concept.lower()
        ]

    def get_by_misconception(self, misconception_type: str) -> List[Dict[str, Any]]:
        """
        Get questions that target specific misconception type.
        
        Args:
            misconception_type: Misconception type (e.g., 'INCOMPLETE_REASONING')
            
        Returns:
            List of matching question dictionaries
        """
        return [
            q for q_id, q in self._questions_by_id.items()
            if self._metadata_index[q_id].misconception_type == misconception_type
        ]

    def get_random_sample(
        self,
        count: int = 1,
        category: Optional[str] = None,
        difficulty: Optional[int] = None,
        bloom_level: Optional[str] = None,
        concept: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get random sample of questions with optional filters.
        
        Args:
            count: Number of questions to sample
            category: Optional category filter
            difficulty: Optional difficulty filter (1-5)
            bloom_level: Optional Bloom level filter
            concept: Optional concept filter
            
        Returns:
            List of randomly sampled questions
        """
        # Start with all questions
        candidates = list(self._questions_by_id.values())
        
        # Apply filters
        if category:
            candidates = [
                q for q in candidates
                if self._metadata_index[q['id']].category == category
            ]
        
        if difficulty:
            candidates = [
                q for q in candidates
                if self._metadata_index[q['id']].difficulty == difficulty
            ]
        
        if bloom_level:
            candidates = [
                q for q in candidates
                if self._metadata_index[q['id']].bloom_level == bloom_level
            ]
        
        if concept:
            candidates = [
                q for q in candidates
                if concept.lower() in self._metadata_index[q['id']].concept.lower()
            ]
        
        # Sample without replacement
        sample_size = min(count, len(candidates))
        return random.sample(candidates, sample_size)

    def get_all_questions(self) -> List[Dict[str, Any]]:
        """Get all questions in the bank."""
        return list(self._questions_by_id.values())

    def get_metadata(self, question_id: str) -> Optional[QuestionMetadata]:
        """Get metadata for a specific question."""
        return self._metadata_index.get(question_id)

    def stats(self) -> Dict[str, Any]:
        """
        Get statistics about the question bank.
        
        Returns:
            Dict with total count, category breakdown, difficulty distribution, etc.
        """
        categories = {}
        difficulties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        bloom_levels = {}
        
        for metadata in self._metadata_index.values():
            # Category count
            categories[metadata.category] = categories.get(metadata.category, 0) + 1
            
            # Difficulty count
            difficulties[metadata.difficulty] += 1
            
            # Bloom level count
            bloom_levels[metadata.bloom_level] = bloom_levels.get(metadata.bloom_level, 0) + 1
        
        return {
            'total_questions': len(self._questions_by_id),
            'by_category': categories,
            'by_difficulty': difficulties,
            'by_bloom_level': bloom_levels,
        }


class QuestionConstructor:
    """
    Constructs rich Question objects from YAML data.
    
    Converts question bank YAML entries into fully-formed Question objects with:
    - Rich narrative context (K.C. Nag stories)
    - HTML diagram rendering instructions
    - Progressive visual hints
    - Trap info and Bloom's level assignments
    - Distractor misconception mappings
    """

    @staticmethod
    def construct_from_yaml(
        question_data: Dict[str, Any],
        question_id: Optional[str] = None,
    ) -> Question:
        """
        Construct a Question object from YAML data.
        
        Args:
            question_data: Dictionary from YAML bank
            question_id: Override question ID if needed
            
        Returns:
            Fully-formed Question object with all rich content
        """
        q_id = question_id or question_data.get('id', 'unknown')
        
        # Extract basic data
        question_text = question_data.get('question', '')
        options = question_data.get('options', [])
        correct_answer = question_data.get('correct_answer', '')
        
        # Shuffle options and find correct index
        shuffled_options = options.copy()
        random.shuffle(shuffled_options)
        correct_idx = shuffled_options.index(correct_answer)
        
        # Create distractors with misconception info
        distractors = []
        for option in shuffled_options:
            if option != correct_answer:
                # Safely handle misconception type enum
                misconception_type_str = question_data.get('misconception_type', 'INCOMPLETE_REASONING').upper().replace(' ', '_')
                try:
                    misconception_enum = MisconceptionType[misconception_type_str]
                except (KeyError, AttributeError):
                    misconception_enum = MisconceptionType.INCOMPLETE_REASONING
                
                distractors.append(DistractorInfo(
                    value=option,
                    misconception_type=misconception_enum,
                    why_wrong=question_data.get('misconception', 'Common error'),
                    teaching_point=question_data.get('teaching_point', ''),
                ))
        
        # Create distractor set
        distractor_set = DistractorSet(
            correct_answer=correct_answer,
            distractors=distractors,
            generation_method='from_bank',
        )
        
        # Create trap info
        misconception_type_str = question_data.get('misconception_type', 'INCOMPLETE_REASONING').upper().replace(' ', '_')
        try:
            misconception_enum = MisconceptionType[misconception_type_str]
        except (KeyError, AttributeError):
            misconception_enum = MisconceptionType.INCOMPLETE_REASONING
        
        trap_type = MISCONCEPTION_TO_TRAP_MAP.get(misconception_enum, TrapType.CALCULATION_TRAP)
        
        trap_info = TrapInfo(
            trap_type=trap_type,
            trap_name=question_data.get('concept', 'Unknown'),
            difficulty=question_data.get('difficulty', 1),
            description=question_data.get('misconception', ''),
            why_effective=question_data.get('why_effective', ''),
            how_to_avoid=question_data.get('how_to_avoid', ''),
        )
        
        # Create bloom info
        bloom_level_str = question_data.get('bloom_level', 'UNDERSTAND').upper()
        bloom_info = BloomInfo(
            bloom_level=BloomLevel[bloom_level_str],
            level_name=bloom_level_str,
            description=f"Question testing {bloom_level_str} level",
            cognitive_verbs=['identify', 'recall', 'apply'],
            example_activities=['factor identification', 'multiple testing'],
            minimum_difficulty=question_data.get('difficulty', 1),
            estimated_time_seconds=60,
        )
        
        # Get narrative and rendering
        narrative = QuestionConstructor._generate_narrative(question_data)
        html_rendering = QuestionConstructor._generate_html_rendering(question_data)
        visual_hints = QuestionConstructor._generate_visual_hints(question_data)
        
        # Create Question object with all rich content
        question = Question(
            topic=question_data.get('concept', 'Factors and Multiples'),
            logical_trap=question_data.get('why_effective', ''),
            data_representation=html_rendering,
            question_text=question_text,
            solution_steps=question_data.get('solution_steps', []),
            answer=correct_answer,
            options=shuffled_options,
            correct_option_index=correct_idx,
            chapter='factors_multiples',
            distractor_info=distractor_set,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_narrative=narrative,
            rich_html_content=html_rendering,
            visual_hints=visual_hints,
        )
        
        return question

    @staticmethod
    def _generate_narrative(question_data: Dict[str, Any]) -> str:
        """Generate rich narrative context for question (plain text, not HTML)."""
        real_world_context = question_data.get('real_world_context', '')
        concept = question_data.get('concept', '')
        teaching_point = question_data.get('teaching_point', '')
        
        # Plain text narrative for frontend rendering
        parts = []
        if real_world_context:
            parts.append(real_world_context)
        if teaching_point:
            parts.append(f"Key Insight: {teaching_point}")
        
        narrative = " ".join(parts) if parts else f"Learn about {concept}"
        
        return narrative

    @staticmethod
    def _generate_html_rendering(question_data: Dict[str, Any]) -> str:
        """Generate HTML diagram based on question type."""
        template = question_data.get('html_template', 'generic')
        visual_hint = question_data.get('visual_hint', '')
        concept = question_data.get('concept', '')
        
        # Create a better HTML diagram based on template type
        if 'factor' in template.lower():
            html = f"""
<div class="diagram factor-diagram" style="text-align: center; padding: 20px;">
    <h4 style="color: #1e40af; margin-bottom: 15px;">{concept}</h4>
    <svg width="400" height="200" style="border: 1px solid #e5e7eb; border-radius: 8px;">
        <rect x="10" y="10" width="380" height="180" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1"/>
        <text x="200" y="40" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e40af">
            Finding Factors
        </text>
        <text x="200" y="70" text-anchor="middle" font-size="14" fill="#374151">
            {visual_hint}
        </text>
        <line x1="50" y1="100" x2="350" y2="100" stroke="#d1d5db" stroke-width="1"/>
        <text x="200" y="130" text-anchor="middle" font-size="13" fill="#6b7280">
            Test each number by division
        </text>
        <text x="200" y="155" text-anchor="middle" font-size="13" fill="#6b7280">
            Include numbers with remainder 0
        </text>
    </svg>
</div>
            """.strip()
        elif 'multiple' in template.lower():
            html = f"""
<div class="diagram multiple-diagram" style="text-align: center; padding: 20px;">
    <h4 style="color: #1e40af; margin-bottom: 15px;">{concept}</h4>
    <svg width="400" height="150" style="border: 1px solid #e5e7eb; border-radius: 8px;">
        <rect x="10" y="10" width="380" height="130" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1"/>
        <text x="200" y="40" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e40af">
            Finding Multiples
        </text>
        <text x="200" y="70" text-anchor="middle" font-size="14" fill="#374151">
            {visual_hint}
        </text>
        <text x="200" y="100" text-anchor="middle" font-size="13" fill="#6b7280">
            Multiply by 1, 2, 3, 4... to find the sequence
        </text>
    </svg>
</div>
            """.strip()
        else:
            # Generic diagram
            html = f"""
<div class="diagram generic-diagram" style="text-align: center; padding: 20px;">
    <h4 style="color: #1e40af; margin-bottom: 15px;">{concept}</h4>
    <svg width="400" height="150" style="border: 1px solid #e5e7eb; border-radius: 8px;">
        <rect x="10" y="10" width="380" height="130" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1"/>
        <text x="200" y="50" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e40af">
            {concept}
        </text>
        <text x="200" y="85" text-anchor="middle" font-size="14" fill="#374151">
            {visual_hint}
        </text>
    </svg>
</div>
            """.strip()
        
        return html

    @staticmethod
    def _generate_visual_hints(question_data: Dict[str, Any]) -> List[str]:
        """Generate progressive visual hints for the question."""
        hints = []
        
        if 'visual_hint' in question_data:
            hints.append(question_data['visual_hint'])
        
        if 'teaching_point' in question_data:
            hints.append(f"Remember: {question_data['teaching_point']}")
        
        if 'solution_steps' in question_data:
            hints.extend(question_data['solution_steps'][:2])
        
        return hints if hints else ['Check each option carefully.']
