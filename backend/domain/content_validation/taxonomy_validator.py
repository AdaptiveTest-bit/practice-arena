"""
Taxonomy Validator for Phase 2 implementation.
Validates concept_id against taxonomy configuration.
"""

import yaml
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TaxonomyValidator:
    """
    Validates concept IDs and their properties against the taxonomy configuration.
    
    Loads taxonomy from backend/config/content/taxonomy/math.yaml and provides
    validation for concept_id, bloom levels, and difficulty ranges.
    """
    
    def __init__(self, taxonomy_path: Optional[str] = None):
        """
        Initialize the taxonomy validator.
        
        Args:
            taxonomy_path: Path to taxonomy YAML file. If None, uses default math taxonomy.
        """
        if taxonomy_path is None:
            taxonomy_path = Path(__file__).parent.parent.parent / "config" / "content" / "taxonomy" / "math.yaml"
        
        self.taxonomy_path = Path(taxonomy_path)
        self.taxonomy_data = self._load_taxonomy()
        self.concepts = self._build_concept_index()
    
    def _load_taxonomy(self) -> Dict:
        """Load taxonomy YAML file."""
        try:
            with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError(f"Taxonomy file not found: {self.taxonomy_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid taxonomy YAML: {e}")
    
    def _build_concept_index(self) -> Dict[str, Dict]:
        """Build a quick lookup index for concepts by ID."""
        concepts = {}
        for concept in self.taxonomy_data.get('concepts', []):
            concepts[concept['id']] = concept
        return concepts
    
    def validate_concept_id(self, concept_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a concept_id exists in the taxonomy.
        
        Args:
            concept_id: The concept ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not concept_id:
            return False, "concept_id cannot be empty"
        
        if concept_id not in self.concepts:
            return False, f"concept_id '{concept_id}' not found in taxonomy"
        
        return True, None
    
    def validate_bloom_level(self, concept_id: str, bloom_level: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if bloom_level matches the concept's defined level.
        
        Args:
            concept_id: The concept ID
            bloom_level: The bloom level to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # First validate concept_id exists
        is_valid, error = self.validate_concept_id(concept_id)
        if not is_valid:
            return False, error
        
        valid_bloom_levels = ['REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE']
        
        if bloom_level not in valid_bloom_levels:
            return False, f"Invalid bloom_level '{bloom_level}'. Must be one of: {valid_bloom_levels}"
        
        concept = self.concepts[concept_id]
        expected_bloom = concept.get('bloom_level')
        
        if expected_bloom and bloom_level != expected_bloom:
            return False, f"bloom_level mismatch for '{concept_id}'. Expected: {expected_bloom}, Got: {bloom_level}"
        
        return True, None
    
    def validate_difficulty(self, concept_id: str, difficulty: int) -> Tuple[bool, Optional[str]]:
        """
        Validate if difficulty is within the concept's allowed range.
        
        Args:
            concept_id: The concept ID
            difficulty: The difficulty level (1-5)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # First validate concept_id exists
        is_valid, error = self.validate_concept_id(concept_id)
        if not is_valid:
            return False, error
        
        if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 5:
            return False, "difficulty must be an integer between 1 and 5"
        
        concept = self.concepts[concept_id]
        difficulty_range = concept.get('difficulty_range', [1, 5])
        
        if len(difficulty_range) != 2:
            return False, f"Invalid difficulty_range for concept '{concept_id}': {difficulty_range}"
        
        min_diff, max_diff = difficulty_range
        if difficulty < min_diff or difficulty > max_diff:
            return False, f"difficulty {difficulty} outside range for '{concept_id}'. Expected: {min_diff}-{max_diff}"
        
        return True, None
    
    def validate_grade(self, concept_id: str, grade: int) -> Tuple[bool, Optional[str]]:
        """
        Validate if grade is appropriate for the concept.
        
        Args:
            concept_id: The concept ID
            grade: The grade level
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # First validate concept_id exists
        is_valid, error = self.validate_concept_id(concept_id)
        if not is_valid:
            return False, error
        
        if not isinstance(grade, int) or grade < 1 or grade > 12:
            return False, "grade must be an integer between 1 and 12"
        
        concept = self.concepts[concept_id]
        valid_grades = concept.get('grades', [])
        
        if valid_grades and grade not in valid_grades:
            return False, f"grade {grade} not valid for concept '{concept_id}'. Valid grades: {valid_grades}"
        
        return True, None
    
    def validate_template_metadata(self, metadata: Dict) -> Tuple[bool, List[str]]:
        """
        Validate complete template metadata against taxonomy.
        
        Args:
            metadata: Dictionary containing concept_id, bloom_level, difficulty, grade
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Validate required fields
        required_fields = ['concept_id', 'bloom_level', 'difficulty', 'grade']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate each field
        validations = [
            (self.validate_concept_id, metadata['concept_id']),
            (self.validate_bloom_level, metadata['concept_id'], metadata['bloom_level']),
            (self.validate_difficulty, metadata['concept_id'], metadata['difficulty']),
            (self.validate_grade, metadata['concept_id'], metadata['grade'])
        ]
        
        for validator_func, *args in validations:
            is_valid, error = validator_func(*args)
            if not is_valid:
                errors.append(error)
        
        return len(errors) == 0, errors
    
    def get_concept_info(self, concept_id: str) -> Optional[Dict]:
        """Get detailed information about a concept."""
        return self.concepts.get(concept_id)
    
    def list_concepts_by_grade(self, grade: int) -> List[str]:
        """Get all concept IDs for a specific grade."""
        return [
            concept_id for concept_id, concept in self.concepts.items()
            if grade in concept.get('grades', [])
        ]
    
    def list_concepts_by_bloom_level(self, bloom_level: str) -> List[str]:
        """Get all concept IDs for a specific bloom level."""
        return [
            concept_id for concept_id, concept in self.concepts.items()
            if concept.get('bloom_level') == bloom_level
        ]


# Singleton instance for easy import
_taxonomy_validator = None

def get_taxonomy_validator() -> TaxonomyValidator:
    """Get singleton instance of TaxonomyValidator."""
    global _taxonomy_validator
    if _taxonomy_validator is None:
        _taxonomy_validator = TaxonomyValidator()
    return _taxonomy_validator
