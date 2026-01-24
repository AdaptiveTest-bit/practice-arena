"""
Template Renderer for Template Engine.

Handles substitution of variables into:
- Question text patterns
- Option patterns
- Solution step patterns
- Diagram SVG templates

Separation of Concerns:
- This module ONLY renders templates
- No variable generation logic
- No constraint validation logic
"""

import re
import logging
from typing import Dict, Any, List, Optional
from jinja2 import Environment, BaseLoader, TemplateError

from domain.template_engine.safe_functions import safe_functions

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """
    Renders template patterns with variable substitution.
    
    Supports:
    - Simple substitution: {{variable}}
    - Expressions: {{a + b}}
    - Function calls: {{gcd(a, b)}}
    - Conditionals: {{x if condition else y}}
    """
    
    def __init__(self):
        """Initialize Jinja2 environment with safe functions."""
        self.jinja_env = Environment(loader=BaseLoader())
        
        # Add safe functions to Jinja globals
        for name, func in safe_functions.get_all().items():
            if callable(func):
                self.jinja_env.globals[name] = func
            else:
                self.jinja_env.globals[name] = func
    
    def render(self, pattern: str, variables: Dict[str, Any]) -> str:
        """
        Render a single pattern with variables.
        
        Args:
            pattern: Template string with {{variable}} placeholders
            variables: Dictionary of variable values
            
        Returns:
            Rendered string
        """
        if not pattern:
            return ''
        
        try:
            template = self.jinja_env.from_string(pattern)
            result = template.render(**variables)
            return result
        except TemplateError as e:
            logger.error(f"Template rendering failed: {pattern[:50]}... - {e}")
            raise ValueError(f"Template rendering failed: {e}")
    
    def render_options(
        self,
        options: List[Dict[str, Any]],
        variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Render all options with variables.
        
        Args:
            options: List of option dicts with 'pattern' and 'is_correct'
            variables: Dictionary of variable values
            
        Returns:
            List of rendered options with 'text' and 'is_correct'
        """
        rendered = []
        
        for opt in options:
            pattern = opt.get('pattern', '')
            is_correct = opt.get('is_correct', False)
            
            rendered.append({
                'text': self.render(pattern, variables),
                'is_correct': is_correct,
                'misconception_id': opt.get('misconception_id'),
            })
        
        return rendered
    
    def render_solution_steps(
        self,
        steps: List[Dict[str, Any]],
        variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Render solution steps with variables.
        
        Args:
            steps: List of step dicts with 'number' and 'text'
            variables: Dictionary of variable values
            
        Returns:
            List of rendered steps
        """
        rendered = []
        
        for step in steps:
            rendered.append({
                'number': step.get('number', step.get('step', len(rendered) + 1)),
                'text': self.render(step.get('text', ''), variables),
            })
        
        return rendered
    
    def render_hints(
        self,
        hints: List[str],
        variables: Dict[str, Any]
    ) -> List[str]:
        """
        Render hint strings with variables.
        
        Args:
            hints: List of hint pattern strings
            variables: Dictionary of variable values
            
        Returns:
            List of rendered hint strings
        """
        return [self.render(hint, variables) for hint in hints]
    
    def render_svg(
        self,
        svg_template: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Render SVG template with variables.
        
        Args:
            svg_template: SVG string with {{variable}} placeholders
            variables: Dictionary of variable values
            
        Returns:
            Rendered SVG string
        """
        if not svg_template:
            return ''
        
        # Use simple string replacement for SVG (safer than Jinja for XML)
        result = svg_template
        
        for name, value in variables.items():
            result = result.replace(f'{{{{{name}}}}}', str(value))
        
        return result


class QuestionBuilder:
    """
    Builds complete question objects from templates and variables.
    
    Combines:
    - Variable generation (from VariableGenerator)
    - Template rendering (from TemplateRenderer)
    - Option shuffling
    - Correct answer tracking
    """
    
    def __init__(self, renderer: TemplateRenderer = None):
        """
        Initialize builder with renderer.
        
        Args:
            renderer: TemplateRenderer instance (creates one if not provided)
        """
        self.renderer = renderer or TemplateRenderer()
    
    def build(
        self,
        template: Dict[str, Any],
        variables: Dict[str, Any],
        shuffle_options: bool = True
    ) -> Dict[str, Any]:
        """
        Build a complete question from template and variables.
        
        Args:
            template: Question template dict
            variables: Generated variables
            shuffle_options: Whether to shuffle options
            
        Returns:
            Complete question dict ready for serving
        """
        # Render question text
        question_text = self.renderer.render(
            template.get('question_pattern', ''),
            variables
        )
        
        # Render options
        raw_options = template.get('options', [])
        rendered_options = self.renderer.render_options(raw_options, variables)
        
        # Track correct answer before shuffling
        correct_text = None
        correct_index = None
        for i, opt in enumerate(rendered_options):
            if opt.get('is_correct'):
                correct_text = opt['text']
                correct_index = i
                break
        
        # Shuffle options if requested
        if shuffle_options and len(rendered_options) > 1:
            import random
            random.shuffle(rendered_options)
            # Find new correct index
            for i, opt in enumerate(rendered_options):
                if opt['text'] == correct_text:
                    correct_index = i
                    break
        
        # Render solution
        solution_data = template.get('solution', {})
        solution_steps = []
        if solution_data:
            steps = solution_data.get('steps', [])
            solution_steps = self.renderer.render_solution_steps(steps, variables)
        
        # Render hints
        hints = self.renderer.render_hints(
            template.get('hints', []),
            variables
        )
        
        # Render diagram
        diagram_svg = None
        diagram_config = template.get('diagram')
        if diagram_config and diagram_config.get('type') == 'custom_svg':
            svg_template = diagram_config.get('parameters', {}).get('svg_template', '')
            if svg_template:
                diagram_svg = self.renderer.render_svg(svg_template, variables)
        
        # Build final question
        question = {
            'question_text': question_text,
            'question_type': template.get('question_type', 'MCQ'),
            'options': [
                {
                    'id': i,
                    'text': opt['text'],
                    'is_correct': opt.get('is_correct', False),
                }
                for i, opt in enumerate(rendered_options)
            ],
            'correct_answer': correct_text,
            'correct_index': correct_index,
            'difficulty': template.get('difficulty', 3),
            'concept_id': template.get('concept_id', ''),
            'tags': template.get('tags', []),
            'solution': {
                'steps': solution_steps,
            },
            'hints': hints,
            'variables': variables,  # Include for debugging/preview
        }
        
        if diagram_svg:
            question['diagram_svg'] = diagram_svg
        
        return question


# Singleton instances
template_renderer = TemplateRenderer()
question_builder = QuestionBuilder(template_renderer)
