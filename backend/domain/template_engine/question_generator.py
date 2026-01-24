"""
Question Generator - Main entry point for template-based question generation.

Orchestrates:
1. Variable generation (variable_generator.py)
2. Constraint validation (constraint_validator.py)
3. Template rendering (template_renderer.py)
4. Question building

Separation of Concerns:
- This module is the ORCHESTRATOR
- Delegates to specialized modules for each task
- Provides clean API for external use

Usage:
    from domain.template_engine.question_generator import question_generator
    
    template = {
        "name": "HCF Question",
        "question_pattern": "Find HCF of {{a}} and {{b}}",
        "variables": {
            "base": {"a": {"type": "integer", "min": 10, "max": 50}, ...},
            "computed": {"answer": {"formula": "gcd(a, b)"}},
            "constraints": ["a != b", "answer < 20"]
        },
        "options": [{"pattern": "{{answer}}", "is_correct": true}, ...],
    }
    
    result = question_generator.generate(template)
    if result.success:
        print(result.question)
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from domain.template_engine.variable_generator import VariableGenerator, GenerationResult
from domain.template_engine.template_renderer import QuestionBuilder, TemplateRenderer
from domain.template_engine.safe_functions import safe_functions

logger = logging.getLogger(__name__)


@dataclass
class QuestionResult:
    """Result of question generation."""
    success: bool
    question: Optional[Dict[str, Any]]
    variables: Dict[str, Any]
    attempts: int
    error: Optional[str] = None


class QuestionGenerator:
    """
    Main entry point for question generation from templates.
    
    Provides:
    - Single question generation
    - Batch generation with uniqueness
    - Preview generation (with explicit variable values)
    """
    
    def __init__(self):
        """Initialize generator with component modules."""
        self.variable_generator = VariableGenerator()
        self.renderer = TemplateRenderer()
        self.builder = QuestionBuilder(self.renderer)
    
    def generate(
        self,
        template: Dict[str, Any],
        seed: Optional[int] = None,
        shuffle_options: bool = True
    ) -> QuestionResult:
        """
        Generate a single question from template.
        
        Args:
            template: Question template dictionary
            seed: Optional random seed for reproducibility
            shuffle_options: Whether to shuffle answer options
            
        Returns:
            QuestionResult with success status and question
        """
        # Extract variable schema
        variables_config = template.get('variables', {})
        
        # Generate variables with constraint validation
        gen_result = self.variable_generator.generate(variables_config, seed)
        
        if not gen_result.success:
            logger.error(f"Variable generation failed: {gen_result.error}")
            return QuestionResult(
                success=False,
                question=None,
                variables={},
                attempts=gen_result.attempts,
                error=gen_result.error
            )
        
        # Build question from template and variables
        try:
            question = self.builder.build(
                template,
                gen_result.variables,
                shuffle_options=shuffle_options
            )
            
            return QuestionResult(
                success=True,
                question=question,
                variables=gen_result.variables,
                attempts=gen_result.attempts
            )
            
        except Exception as e:
            logger.error(f"Question building failed: {e}")
            return QuestionResult(
                success=False,
                question=None,
                variables=gen_result.variables,
                attempts=gen_result.attempts,
                error=str(e)
            )
    
    def generate_batch(
        self,
        template: Dict[str, Any],
        count: int = 5,
        ensure_unique: bool = True
    ) -> List[QuestionResult]:
        """
        Generate multiple questions from same template.
        
        Args:
            template: Question template dictionary
            count: Number of questions to generate
            ensure_unique: If True, ensure question texts are unique
            
        Returns:
            List of QuestionResult objects
        """
        results = []
        seen_texts = set()
        max_attempts = count * 3  # Allow extra attempts for uniqueness
        
        for _ in range(max_attempts):
            if len(results) >= count:
                break
            
            result = self.generate(template)
            
            if not result.success:
                results.append(result)
                continue
            
            # Check uniqueness
            if ensure_unique:
                question_text = result.question.get('question_text', '')
                if question_text in seen_texts:
                    continue
                seen_texts.add(question_text)
            
            results.append(result)
        
        return results[:count]
    
    def preview(
        self,
        template: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> QuestionResult:
        """
        Generate a preview with explicit variable values.
        
        Useful for testing templates with specific values.
        
        Args:
            template: Question template dictionary
            variables: Explicit variable values to use
            
        Returns:
            QuestionResult with generated question
        """
        try:
            question = self.builder.build(
                template,
                variables,
                shuffle_options=False  # Don't shuffle for preview
            )
            
            return QuestionResult(
                success=True,
                question=question,
                variables=variables,
                attempts=1
            )
            
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            return QuestionResult(
                success=False,
                question=None,
                variables=variables,
                attempts=1,
                error=str(e)
            )
    
    def validate_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a template without generating a question.
        
        Args:
            template: Question template dictionary
            
        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []
        
        # Required fields
        if not template.get('question_pattern') and not template.get('parts'):
            errors.append("Missing 'question_pattern' or 'parts'")
        
        if not template.get('variables'):
            errors.append("Missing 'variables' section")
        
        if not template.get('options') and template.get('question_type') not in ['FILL_BLANK', 'CASE_STUDY']:
            errors.append("Missing 'options' for question type")
        
        # Check for at least one correct option
        options = template.get('options', [])
        has_correct = any(opt.get('is_correct') for opt in options)
        if options and not has_correct:
            errors.append("No option marked as 'is_correct: true'")
        
        # Recommended fields
        if not template.get('difficulty'):
            warnings.append("Recommended: 'difficulty' (1-5)")
        
        if not template.get('solution'):
            warnings.append("Recommended: 'solution' with steps")
        
        if not template.get('concept_id'):
            warnings.append("Recommended: 'concept_id' for curriculum mapping")
        
        # Try a test generation
        if not errors:
            result = self.generate(template)
            if not result.success:
                errors.append(f"Test generation failed: {result.error}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
        }
    
    def list_available_functions(self) -> List[str]:
        """List all available functions for formulas."""
        return safe_functions.list_functions()
    
    def get_functions_by_category(self) -> Dict[str, List[str]]:
        """Get available functions grouped by category."""
        return safe_functions.list_by_category()


# Singleton instance for easy import
question_generator = QuestionGenerator()


# Convenience functions
def generate_question(template: Dict[str, Any], **kwargs) -> QuestionResult:
    """Generate a single question from template."""
    return question_generator.generate(template, **kwargs)


def generate_batch(template: Dict[str, Any], count: int = 5, **kwargs) -> List[QuestionResult]:
    """Generate multiple questions from template."""
    return question_generator.generate_batch(template, count, **kwargs)


def validate_template(template: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a template."""
    return question_generator.validate_template(template)
