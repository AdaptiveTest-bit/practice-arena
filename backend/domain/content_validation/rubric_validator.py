"""
Rubric Validator for Phase 2 implementation.
Validates template structure and constraints against quality rubrics.
"""

import yaml
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class RubricValidator:
    """
    Validates question templates against quality rubrics.
    
    Loads rubrics from backend/config/content/rubrics/question_quality.yaml and
    provides comprehensive validation for template structure, fields, and quality.
    """
    
    def __init__(self, rubric_path: Optional[str] = None):
        """
        Initialize the rubric validator.
        
        Args:
            rubric_path: Path to rubric YAML file. If None, uses default question quality rubric.
        """
        if rubric_path is None:
            rubric_path = Path(__file__).parent.parent.parent / "config" / "content" / "rubrics" / "question_quality.yaml"
        
        self.rubric_path = Path(rubric_path)
        self.rubric_data = self._load_rubrics()
        self.valid_concept_keys = self.rubric_data.get('VALID_CONCEPT_KEYS', [])
    
    def _load_rubrics(self) -> Dict:
        """Load rubric YAML file."""
        try:
            with open(self.rubric_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError(f"Rubric file not found: {self.rubric_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid rubric YAML: {e}")
    
    def _evaluate_rule(self, rule: str, data: Dict) -> bool:
        """
        Evaluate a validation rule against data.
        
        Args:
            rule: Rule string (e.g., "len(options) == 4")
            data: Data dictionary to evaluate against
            
        Returns:
            Boolean result of rule evaluation
        """
        try:
            # Create a safe evaluation context with only the data and builtins
            context = {
                'len': len,
                'all': all,
                'any': any,
                'sum': sum,
                'sorted': sorted,
                'range': range,
                'set': set,
                'list': list,
                'VALID_CONCEPT_KEYS': self.valid_concept_keys,
                # Add data fields directly to context for easier access
                **data
            }
            
            # Handle meta object - convert to object with attribute access
            if 'meta' in data and isinstance(data['meta'], dict):
                class MetaWrapper:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                context['meta'] = MetaWrapper(data['meta'])
            
            # Handle misconception_info - convert to objects with attribute access
            if 'misconception_info' in data and isinstance(data['misconception_info'], list):
                # Create a simple wrapper class for attribute access
                class MisconceptionWrapper:
                    def __init__(self, data):
                        self.option_index = data.get('option_index')
                        self.is_correct = data.get('is_correct')
                        self.value = data.get('value')
                        self.target_misconception = data.get('target_misconception')
                        self.teaching_point = data.get('teaching_point')
                        self.why_wrong = data.get('why_wrong')
                
                context['misconception_info'] = [MisconceptionWrapper(m) for m in data['misconception_info']]
            
            # Evaluate the rule
            return eval(rule, {"__builtins__": {}}, context)
        except Exception as e:
            logger.warning(f"Rule evaluation failed: '{rule}' - {e}")
            return False
    
    def validate_required_fields(self, template: Dict) -> Tuple[bool, List[str]]:
        """
        Validate that all required fields are present.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        required_fields = self.rubric_data.get('required_question_fields', [])
        
        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")
            elif template[field] is None:
                errors.append(f"Required field cannot be null: {field}")
            elif isinstance(template[field], str) and not template[field].strip():
                errors.append(f"Required field cannot be empty: {field}")
        
        return len(errors) == 0, errors
    
    def validate_meta_fields(self, template: Dict) -> Tuple[bool, List[str]]:
        """
        Validate meta sub-fields if meta exists.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        if 'meta' not in template:
            return True, errors
        
        meta = template['meta']
        required_meta_fields = self.rubric_data.get('required_meta_fields', [])
        
        for field in required_meta_fields:
            if field not in meta:
                errors.append(f"Missing required meta field: {field}")
            elif meta[field] is None:
                errors.append(f"Required meta field cannot be null: {field}")
            elif isinstance(meta[field], str) and not meta[field].strip():
                errors.append(f"Required meta field cannot be empty: {field}")
        
        return len(errors) == 0, errors
    
    def validate_misconception_fields(self, template: Dict) -> Tuple[bool, List[str]]:
        """
        Validate misconception_info structure.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        if 'misconception_info' not in template:
            return True, errors
        
        misconception_info = template['misconception_info']
        required_misconception_fields = self.rubric_data.get('required_misconception_fields', [])
        
        if not isinstance(misconception_info, list):
            errors.append("misconception_info must be a list")
            return False, errors
        
        for i, misconception in enumerate(misconception_info):
            if not isinstance(misconception, dict):
                errors.append(f"misconception_info[{i}] must be a dictionary")
                continue
            
            for field in required_misconception_fields:
                if field not in misconception:
                    errors.append(f"Missing required misconception field at index {i}: {field}")
        
        return len(errors) == 0, errors
    
    def validate_checks(self, template: Dict) -> Tuple[bool, List[str]]:
        """
        Run all validation checks from the rubric.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        checks = self.rubric_data.get('checks', [])
        
        for check in checks:
            rule = check.get('rule', '')
            message = check.get('message', 'Validation failed')
            
            if not self._evaluate_rule(rule, template):
                errors.append(message)
        
        return len(errors) == 0, errors
    
    def validate_concept_key(self, concept_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if concept_key is in the allowed list.
        
        Args:
            concept_key: The concept key to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not concept_key:
            return False, "concept_key cannot be empty"
        
        if concept_key not in self.valid_concept_keys:
            return False, f"concept_key '{concept_key}' not in valid list: {self.valid_concept_keys}"
        
        return True, None
    
    def validate_template_structure(self, template: Dict) -> Tuple[bool, List[str]]:
        """
        Perform complete template structure validation.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        all_errors = []
        
        # Run all validation types
        validations = [
            self.validate_required_fields(template),
            self.validate_meta_fields(template),
            self.validate_misconception_fields(template),
            self.validate_checks(template)
        ]
        
        for is_valid, errors in validations:
            if not is_valid:
                all_errors.extend(errors)
        
        return len(all_errors) == 0, all_errors
    
    def calculate_quality_score(self, template: Dict) -> Tuple[int, str]:
        """
        Calculate quality score based on rubric criteria.
        
        Args:
            template: Template dictionary to score
            
        Returns:
            Tuple of (score_0_100, quality_level)
        """
        score = 0
        quality_scoring = self.rubric_data.get('quality_scoring', {})
        
        # Check for excellent criteria
        excellent = quality_scoring.get('excellent', {})
        excellent_criteria = excellent.get('criteria', [])
        excellent_score = excellent.get('min_score', 90)
        
        excellent_count = 0
        for criterion in excellent_criteria:
            if template.get(criterion.replace('has_', '').replace('_', '')):
                excellent_count += 1
        
        if excellent_count >= len(excellent_criteria) * 0.8:  # 80% of excellent criteria
            score = max(score, excellent_score)
        
        # Check for good criteria
        good = quality_scoring.get('good', {})
        good_criteria = good.get('criteria', [])
        good_score = good.get('min_score', 70)
        
        good_count = 0
        for criterion in good_criteria:
            if template.get(criterion.replace('has_', '').replace('_', '')):
                good_count += 1
        
        if good_count >= len(good_criteria) * 0.8:  # 80% of good criteria
            score = max(score, good_score)
        
        # Check for acceptable criteria
        acceptable = quality_scoring.get('acceptable', {})
        acceptable_criteria = acceptable.get('criteria', [])
        acceptable_score = acceptable.get('min_score', 50)
        
        acceptable_count = 0
        for criterion in acceptable_criteria:
            if template.get(criterion.replace('has_', '').replace('_', '')):
                acceptable_count += 1
        
        if acceptable_count >= len(acceptable_criteria) * 0.8:  # 80% of acceptable criteria
            score = max(score, acceptable_score)
        
        # Determine quality level
        if score >= excellent_score:
            level = 'excellent'
        elif score >= good_score:
            level = 'good'
        elif score >= acceptable_score:
            level = 'acceptable'
        else:
            level = 'poor'
        
        return score, level
    
    def validate_pedagogical_requirements(self, template: Dict) -> Tuple[bool, List[str]]:
        """
        Validate pedagogical requirements from rubric.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        ped_reqs = self.rubric_data.get('pedagogical_requirements', {})
        
        # Validate distractors
        if 'misconception_info' in template and isinstance(template['misconception_info'], list):
            distractor_reqs = ped_reqs.get('distractors', [])
            
            for i, misconception in enumerate(template['misconception_info']):
                if not misconception.get('is_correct', False):  # Only check wrong options
                    if distractor_reqs.get('must_target_misconception') and not misconception.get('target_misconception'):
                        errors.append(f"Distractor at index {i} must target a misconception")
                    
                    if distractor_reqs.get('must_have_teaching_point') and not misconception.get('teaching_point'):
                        errors.append(f"Distractor at index {i} must have a teaching point")
                    
                    if distractor_reqs.get('must_have_why_wrong') and not misconception.get('why_wrong'):
                        errors.append(f"Distractor at index {i} must explain why it's wrong")
        
        # Validate bloom alignment
        if 'meta' in template and 'bloom_level' in template['meta']:
            bloom_level = template['meta']['bloom_level']
            bloom_alignment = ped_reqs.get('bloom_alignment', {})
            
            if bloom_level in bloom_alignment:
                expected_verbs = bloom_alignment[bloom_level]
                question_text = template.get('question_text', '').lower()
                
                # Check if question uses appropriate verbs for bloom level
                has_appropriate_verb = any(verb in question_text for verb in expected_verbs)
                if not has_appropriate_verb:
                    errors.append(f"Question for {bloom_level} level should use verbs like: {expected_verbs}")
        
        return len(errors) == 0, errors


# Singleton instance for easy import
_rubric_validator = None

def get_rubric_validator() -> RubricValidator:
    """Get singleton instance of RubricValidator."""
    global _rubric_validator
    if _rubric_validator is None:
        _rubric_validator = RubricValidator()
    return _rubric_validator
