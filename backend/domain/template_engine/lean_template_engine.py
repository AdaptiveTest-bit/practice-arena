"""
Lean Template Engine for Phase 4 implementation.

Generates question instances from templates and keeps responses lean.
Integrates with Phase 3 database models and Phase 2 validation.
Phase 6 Update: Uses CDN for diagram content instead of inline HTML.
"""

import json
import random
import sys
from typing import Dict, Any, List, Optional, Tuple
from jinja2 import Environment, BaseLoader, TemplateError
from sqlalchemy.orm import Session
from db.models import QuestionTemplate, Misconception, TemplateOptionMisconception
from domain.cdn import DiagramCDNService
import asyncio


class VariableGenerator:
    """Generates variables based on JSON schema definitions."""
    
    @staticmethod
    def generate_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate variables from a JSON schema.
        
        Args:
            schema: JSON schema defining variable generation rules
            
        Returns:
            Dictionary of generated variables
        """
        variables = {}
        
        if not isinstance(schema, dict):
            return variables
            
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            properties = schema.get('properties', {})
            for var_name, var_schema in properties.items():
                variables[var_name] = VariableGenerator._generate_single_variable(var_schema)
        
        elif schema_type == 'array':
            # Generate array of items
            items_schema = schema.get('items', {})
            min_items = schema.get('minItems', 1)
            max_items = schema.get('maxItems', 5)
            count = random.randint(min_items, max_items)
            
            variables = [
                VariableGenerator._generate_single_variable(items_schema)
                for _ in range(count)
            ]
        
        return variables
    
    @staticmethod
    def _generate_single_variable(var_schema: Dict[str, Any]) -> Any:
        """Generate a single variable based on its schema."""
        var_type = var_schema.get('type', 'string')
        
        if var_type == 'integer':
            minimum = var_schema.get('minimum', 1)
            maximum = var_schema.get('maximum', 100)
            return random.randint(minimum, maximum)
        
        elif var_type == 'number':
            minimum = var_schema.get('minimum', 1.0)
            maximum = var_schema.get('maximum', 100.0)
            return round(random.uniform(minimum, maximum), 2)
        
        elif var_type == 'string':
            # Handle predefined choices
            enum_values = var_schema.get('enum')
            if enum_values:
                return random.choice(enum_values)
            
            # Generate string based on pattern or constraints
            min_length = var_schema.get('minLength', 3)
            max_length = var_schema.get('maxLength', 10)
            
            # For now, generate a simple string
            length = random.randint(min_length, max_length)
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))
        
        elif var_type == 'boolean':
            return random.choice([True, False])
        
        elif var_type == 'array':
            items_schema = var_schema.get('items', {})
            min_items = var_schema.get('minItems', 1)
            max_items = var_schema.get('maxItems', 5)
            count = random.randint(min_items, max_items)
            
            return [
                VariableGenerator._generate_single_variable(items_schema)
                for _ in range(count)
            ]
        
        else:
            # Default fallback
            return None


class TemplateRenderer:
    """Renders template patterns with generated variables."""
    
    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader())
    
    def render_pattern(self, pattern: str, variables: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template pattern with variables.
        
        Args:
            pattern: Template string with variable placeholders
            variables: Dictionary of variables to substitute
            
        Returns:
            Rendered string
        """
        try:
            template = self.jinja_env.from_string(pattern)
            return template.render(**variables)
        except TemplateError as e:
            raise ValueError(f"Template rendering failed: {e}")
    
    def render_options(self, option_patterns: List[str], variables: Dict[str, Any]) -> List[str]:
        """
        Render multiple option patterns.
        
        Args:
            option_patterns: List of option template strings
            variables: Dictionary of variables to substitute
            
        Returns:
            List of rendered option strings
        """
        return [self.render_pattern(pattern, variables) for pattern in option_patterns]


class AnswerEvaluator:
    """Evaluates answer logic and determines correct answers."""
    
    @staticmethod
    def evaluate_answer_logic(answer_logic: str, variables: Dict[str, Any]) -> Any:
        """
        Safely evaluate answer logic with generated variables.
        
        Args:
            answer_logic: Python code string for computing answer
            variables: Dictionary of generated variables
            
        Returns:
            Computed answer
        """
        # Create a safe execution environment
        safe_globals = {
            '__builtins__': {
                'abs': abs,
                'min': min,
                'max': max,
                'round': round,
                'len': len,
                'sum': sum,
                'int': int,
                'float': float,
                'str': str,
                'bool': bool,
                'list': list,
                'range': range,
                'enumerate': enumerate,
                'sorted': sorted,
            },
            'variables': variables  # Make variables accessible
        }
        
        try:
            # Execute the answer logic
            exec(f"result = ({answer_logic})", safe_globals)
            return safe_globals['result']
        except Exception as e:
            raise ValueError(f"Answer logic evaluation failed: {e}")
    
    @staticmethod
    def find_correct_index(rendered_options: List[str], correct_answer: Any) -> int:
        """
        Find the index of the correct answer in rendered options.
        
        Args:
            rendered_options: List of rendered option strings
            correct_answer: The computed correct answer
            
        Returns:
            Index of the correct option (0-based)
        """
        # Convert both to strings for comparison
        correct_str = str(correct_answer).strip()
        
        for i, option in enumerate(rendered_options):
            option_str = str(option).strip()
            if option_str == correct_str:
                return i
        
        # If no exact match, try numeric comparison
        try:
            correct_num = float(correct_str)
            for i, option in enumerate(rendered_options):
                try:
                    option_num = float(str(option).strip())
                    if abs(option_num - correct_num) < 0.001:  # Small tolerance for floats
                        return i
                except ValueError:
                    continue
        except ValueError:
            pass
        
        raise ValueError(f"Correct answer '{correct_answer}' not found in options: {rendered_options}")


class LeanTemplateEngine:
    """
    Main engine for generating lean question instances from templates.
    
    Integrates variable generation, template rendering, and answer evaluation
    to create compact question payloads.
    Phase 6 Update: Uses CDN for diagram content.
    """
    
    def __init__(self, db_session: Session, cdn_service: Optional[DiagramCDNService] = None):
        self.db = db_session
        self.variable_generator = VariableGenerator()
        self.template_renderer = TemplateRenderer()
        self.answer_evaluator = AnswerEvaluator()
        self.cdn_service = cdn_service or DiagramCDNService()
    
    async def generate_question(self, template_id: int) -> Dict[str, Any]:
        """
        Generate a complete question instance from a template.
        
        Args:
            template_id: ID of the question template
            
        Returns:
            Lean question payload dictionary
        """
        # Fetch template from database
        template = self.db.query(QuestionTemplate).filter(
            QuestionTemplate.id == template_id,
            QuestionTemplate.status == "PUBLISHED"
        ).first()
        
        if not template:
            raise ValueError(f"Published template with ID {template_id} not found")
        
        # Step 1: Generate variables
        variables = self.variable_generator.generate_from_schema(template.variable_schema)
        
        # Step 2: Render question and options
        question_text = self.template_renderer.render_pattern(template.question_pattern, variables)
        rendered_options = self.template_renderer.render_options(template.option_patterns, variables)
        
        # Step 3: Compute correct answer
        correct_answer = self.answer_evaluator.evaluate_answer_logic(template.answer_logic, variables)
        correct_index = self.answer_evaluator.find_correct_index(rendered_options, correct_answer)
        
        # Step 4: Generate diagram URLs using CDN (Phase 6)
        diagram_urls = []
        if template.diagrams:
            for diagram in template.diagrams:
                try:
                    # Generate diagram parameters from template variables
                    diagram_params = self._generate_diagram_parameters(diagram, variables)
                    
                    # Get CDN URL for the diagram
                    diagram_url = await self.cdn_service.render_diagram_dynamically(
                        diagram.diagram_type, 
                        diagram_params
                    )
                    
                    diagram_urls.append({
                        'id': diagram.id,
                        'name': diagram.name,
                        'type': diagram.diagram_type,
                        'url': diagram_url,
                        'alt_text': diagram.alt_text or f"Diagram: {diagram.name}"
                    })
                except Exception as e:
                    # Log error but continue with other diagrams
                    print(f"Warning: Failed to generate diagram {diagram.id}: {e}")
                    continue
        
        # Step 5: Create lean payload
        lean_payload = {
            "id": f"q_{template_id}_{random.randint(1000, 9999)}",
            "template_id": template_id,
            "question": question_text,
            "options": rendered_options,
            "diagrams": diagram_urls,  # Phase 6: CDN URLs instead of inline HTML
            "metadata": {
                "concept_id": template.concept_id,
                "difficulty": template.difficulty,
                "bloom_level": template.bloom_level,
                "estimated_time": template.estimated_time
            }
            # Note: correct_answer is NOT included in payload for security
        }
        
        return {
            "payload": lean_payload,
            "correct_index": correct_index,
            "variables": variables  # For debugging/testing
        }
    
    def _generate_diagram_parameters(self, diagram, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate parameters for diagram rendering based on template variables.
        
        Args:
            diagram: Template diagram object
            variables: Generated variables
            
        Returns:
            Parameters dictionary for diagram rendering
        """
        # Start with template variables
        params = variables.copy()
        
        # Add diagram-specific variables from the template
        if diagram.variables:
            params.update(diagram.variables)
        
        # Add computed parameters based on diagram type
        if diagram.diagram_type == "factors":
            # For factors diagrams, ensure we have target_number and factors
            if 'target_number' not in params:
                # Generate a random number for factors
                params['target_number'] = random.randint(12, 48)
            
            target_number = params['target_number']
            if 'factors' not in params:
                # Calculate factors
                params['factors'] = sorted([i for i in range(1, target_number + 1) if target_number % i == 0])
        
        elif diagram.diagram_type == "multiples":
            # For multiples diagrams
            if 'number' not in params:
                params['number'] = random.randint(2, 12)
            
            if 'multiples' not in params:
                count = random.randint(5, 7)
                params['multiples'] = [params['number'] * i for i in range(1, count + 1)]
        
        elif diagram.diagram_type == "divisibility":
            # For divisibility diagrams
            if 'number' not in params:
                params['number'] = random.randint(10, 50)
            if 'divisor' not in params:
                params['divisor'] = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10])
            
            # Calculate divisibility
            params['is_divisible'] = params['number'] % params['divisor'] == 0
            params['quotient'] = params['number'] // params['divisor']
            params['remainder'] = params['number'] % params['divisor']
        
        elif diagram.diagram_type == "gcd":
            # For GCD diagrams
            if 'num1' not in params:
                params['num1'] = random.randint(10, 30)
            if 'num2' not in params:
                params['num2'] = random.randint(10, 30)
            
            # Calculate GCD
            import math
            params['gcd_result'] = math.gcd(params['num1'], params['num2'])
            
            # Add prime factors if not present
            if 'factors1' not in params:
                import sympy
                params['factors1'] = list(sympy.factorint(params['num1']).keys())
            if 'factors2' not in params:
                import sympy
                params['factors2'] = list(sympy.factorint(params['num2']).keys())
        
        elif diagram.diagram_type == "lcm":
            # For LCM diagrams
            if 'num1' not in params:
                params['num1'] = random.randint(2, 12)
            if 'num2' not in params:
                params['num2'] = random.randint(2, 12)
            
            # Calculate LCM
            import math
            params['lcm_result'] = (params['num1'] * params['num2']) // math.gcd(params['num1'], params['num2'])
        
        elif diagram.diagram_type == "prime_composite":
            # For prime/composite diagrams
            if 'number' not in params:
                params['number'] = random.randint(2, 30)
            
            # Calculate factors and primality
            if 'factors' not in params:
                params['factors'] = sorted([i for i in range(1, params['number'] + 1) if params['number'] % i == 0])
            if 'is_prime' not in params:
                params['is_prime'] = len(params['factors']) == 2
        
        return params
    
    def evaluate_answer(self, template_id: int, selected_index: int, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a student's answer and provide feedback.
        
        Args:
            template_id: ID of the question template
            selected_index: Index of the student's selected option
            variables: Variables used to generate the question
            
        Returns:
            Evaluation result with feedback
        """
        # Fetch template and misconceptions
        template = self.db.query(QuestionTemplate).filter(
            QuestionTemplate.id == template_id
        ).first()
        
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
        
        # Compute correct answer
        correct_answer = self.answer_evaluator.evaluate_answer_logic(template.answer_logic, variables)
        rendered_options = self.template_renderer.render_options(template.option_patterns, variables)
        correct_index = self.answer_evaluator.find_correct_index(rendered_options, correct_answer)
        
        # Determine if answer is correct
        is_correct = (selected_index == correct_index)
        
        result = {
            "is_correct": is_correct,
            "selected_index": selected_index,
            "correct_index": correct_index,
            "feedback": None
        }
        
        # If incorrect, provide misconception feedback
        if not is_correct:
            misconception_feedback = self._get_misconception_feedback(
                template_id, selected_index
            )
            result["feedback"] = misconception_feedback
        
        return result
    
    def _get_misconception_feedback(self, template_id: int, option_index: int) -> Optional[Dict[str, Any]]:
        """
        Get misconception feedback for a specific option.
        
        Args:
            template_id: ID of the question template
            option_index: Index of the selected option
            
        Returns:
            Misconception feedback dictionary or None
        """
        # Query for misconception mapping
        mapping = self.db.query(TemplateOptionMisconception).filter(
            TemplateOptionMisconception.template_id == template_id,
            TemplateOptionMisconception.option_index == option_index
        ).first()
        
        if not mapping:
            return None
        
        # Fetch misconception details
        misconception = self.db.query(Misconception).filter(
            Misconception.id == mapping.misconception_id
        ).first()
        
        if not misconception:
            return None
        
        return {
            "misconception_code": misconception.code,
            "title": misconception.title,
            "explanation": misconception.description,
            "teaching_point": misconception.teaching_point,
            "custom_explanation": mapping.custom_explanation
        }
    
    async def generate_questions_for_concept(self, concept_id: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple questions for a specific concept.
        
        Args:
            concept_id: Concept identifier
            count: Number of questions to generate
            
        Returns:
            List of lean question payloads
        """
        # Fetch published templates for concept
        templates = self.db.query(QuestionTemplate).filter(
            QuestionTemplate.concept_id == concept_id,
            QuestionTemplate.status == "PUBLISHED"
        ).limit(count).all()
        
        if not templates:
            raise ValueError(f"No published templates found for concept: {concept_id}")
        
        questions = []
        for template in templates:
            try:
                question_data = await self.generate_question(template.id)
                questions.append(question_data["payload"])
            except Exception as e:
                # Skip failed generations but continue with others
                print(f"Warning: Failed to generate question from template {template.id}: {e}")
                continue
        
        return questions
