"""
Lean Template Engine for Phase 4 implementation.

Generates question instances from templates and keeps responses lean.
Integrates with Phase 3 database models and Phase 2 validation.
Phase 6 Update: Uses CDN for diagram content instead of inline HTML.
Phase 7 Update: Loads custom formulas from database for self-service content authoring.
"""

import json
import random
import sys
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
from jinja2 import Environment, BaseLoader, TemplateError
from sqlalchemy.orm import Session
from db.models import QuestionTemplate, Misconception, TemplateOptionMisconception
from domain.cdn import DiagramCDNService
import asyncio

logger = logging.getLogger(__name__)


class VariableGenerator:
    """Generates variables based on JSON schema definitions.
    
    Supports both basic variable generation and computed/derived variables.
    This makes templates maintainable without requiring Python code in answer_logic.
    """
    
    # Safe functions available for computed variables
    # Content writers can use these without knowing Python
    SAFE_FUNCTIONS = None  # Lazy-loaded
    
    # Custom formulas loaded from database
    CUSTOM_FORMULAS: Dict[str, Callable] = {}
    _custom_formulas_loaded = False
    
    @classmethod
    def _get_safe_functions(cls):
        """Lazy-load safe functions for computed variables."""
        if cls.SAFE_FUNCTIONS is None:
            import math
            
            def get_factors(n):
                """Get all factors of a number."""
                return sorted([i for i in range(1, abs(int(n)) + 1) if int(n) % i == 0])
            
            def get_multiples(n, count=10):
                """Get first 'count' multiples of a number."""
                return [int(n) * i for i in range(1, count + 1)]
            
            def is_prime(n):
                """Check if a number is prime."""
                n = abs(int(n))
                if n < 2:
                    return False
                return len([i for i in range(1, n + 1) if n % i == 0]) == 2
            
            def get_prime_factors(n):
                """Get prime factorization of a number."""
                n = abs(int(n))
                factors = []
                d = 2
                while d * d <= n:
                    while n % d == 0:
                        factors.append(d)
                        n //= d
                    d += 1
                if n > 1:
                    factors.append(n)
                return factors
            
            DIVISIBILITY_RULES = {
                2: "Last digit is even (0, 2, 4, 6, 8)",
                3: "Sum of digits divisible by 3",
                4: "Last two digits divisible by 4",
                5: "Last digit is 0 or 5",
                6: "Divisible by both 2 and 3",
                9: "Sum of digits divisible by 9",
                10: "Last digit is 0",
            }
            
            def divisibility_rule(divisor):
                """Get the divisibility rule for a number."""
                return DIVISIBILITY_RULES.get(int(divisor), f"Check if divisible by {divisor}")
            
            # Phase 1 Extensions for StudyAdda-style questions
            def sum_factors(n):
                """Sum of all factors of a number."""
                return sum(get_factors(n))
            
            def is_coprime(a, b):
                """Check if two numbers are co-prime (GCD = 1)."""
                return math.gcd(int(a), int(b)) == 1
            
            def lcm_three(a, b, c):
                """LCM of three numbers."""
                lcm_func = getattr(math, 'lcm', lambda x, y: abs(x * y) // math.gcd(x, y))
                return lcm_func(lcm_func(int(a), int(b)), int(c))
            
            def gcd_three(a, b, c):
                """GCD of three numbers."""
                return math.gcd(math.gcd(int(a), int(b)), int(c))
            
            def factor_count(n):
                """Count of factors of a number."""
                return len(get_factors(n))
            
            def is_perfect_square(n):
                """Check if a number is a perfect square."""
                n = int(n)
                root = int(math.sqrt(n))
                return root * root == n
            
            def is_perfect_cube(n):
                """Check if a number is a perfect cube."""
                n = int(n)
                root = round(n ** (1/3))
                return root ** 3 == n
            
            def count_primes_in_range(start, end):
                """Count prime numbers in a range [start, end]."""
                return sum(1 for i in range(int(start), int(end) + 1) if is_prime(i))
            
            def nearest_multiple_above(target, divisor):
                """Find the smallest multiple of divisor >= target."""
                target, divisor = int(target), int(divisor)
                if target % divisor == 0:
                    return target
                return ((target // divisor) + 1) * divisor
            
            def nearest_multiple_below(target, divisor):
                """Find the largest multiple of divisor <= target."""
                target, divisor = int(target), int(divisor)
                return (target // divisor) * divisor
            
            def lcm_plus_remainder(a, b, remainder):
                """LCM of a and b, plus a remainder."""
                lcm_func = getattr(math, 'lcm', lambda x, y: abs(x * y) // math.gcd(x, y))
                return lcm_func(int(a), int(b)) + int(remainder)
            
            def common_factors(a, b):
                """Find common factors of two numbers."""
                return get_factors(math.gcd(int(a), int(b)))
            
            cls.SAFE_FUNCTIONS = {
                # Math operations
                'gcd': math.gcd,
                'lcm': getattr(math, 'lcm', lambda a, b: abs(a * b) // math.gcd(a, b)),
                'sqrt': math.sqrt,
                'abs': abs,
                'min': min,
                'max': max,
                'pow': pow,
                'floor': math.floor,
                'ceil': math.ceil,
                'round': round,
                'int': int,
                'float': float,
                'str': str,
                'len': len,
                'sum': sum,
                'sorted': sorted,
                'list': list,
                
                # Educational helpers - K-12 CBSE specific
                'factors': get_factors,
                'multiples': get_multiples,
                'is_prime': is_prime,
                'prime_factors': get_prime_factors,
                'divisibility_rule': divisibility_rule,
                
                # Phase 1 Extensions (StudyAdda coverage)
                'sum_factors': sum_factors,
                'is_coprime': is_coprime,
                'lcm_three': lcm_three,
                'gcd_three': gcd_three,
                'factor_count': factor_count,
                'is_perfect_square': is_perfect_square,
                'is_perfect_cube': is_perfect_cube,
                'count_primes': count_primes_in_range,
                'nearest_multiple_above': nearest_multiple_above,
                'nearest_multiple_below': nearest_multiple_below,
                'lcm_plus_remainder': lcm_plus_remainder,
                'common_factors': common_factors,
            }
            
            # Load custom formulas from database and merge them
            cls._load_custom_formulas()
            cls.SAFE_FUNCTIONS.update(cls.CUSTOM_FORMULAS)
            
        return cls.SAFE_FUNCTIONS

    @classmethod
    def _load_custom_formulas(cls) -> None:
        """
        Load ACTIVE custom formulas from the database.
        
        This enables content writers to create new formula functions
        via the Admin UI without requiring code deployments.
        """
        if cls._custom_formulas_loaded:
            return
        
        try:
            from core.database import SessionLocal
            from db.models.custom_formula import CustomFormula
            from domain.template_engine.formula_sandbox import FormulaSandbox
            
            db = SessionLocal()
            try:
                # Get all ACTIVE custom formulas
                active_formulas = db.query(CustomFormula).filter(
                    CustomFormula.status == "ACTIVE"
                ).all()
                
                if not active_formulas:
                    logger.debug("No active custom formulas found in database")
                    cls._custom_formulas_loaded = True
                    return
                
                sandbox = FormulaSandbox()
                
                for formula in active_formulas:
                    try:
                        # Validate formula code
                        is_valid, error = sandbox.validate_code(formula.code)
                        if not is_valid:
                            logger.warning(f"Custom formula '{formula.name}' failed validation: {error}")
                            continue
                        
                        # Create callable function from formula code
                        func = sandbox.create_callable(
                            code=formula.code,
                            function_name=formula.name
                        )
                        
                        if func:
                            cls.CUSTOM_FORMULAS[formula.name] = func
                            logger.info(f"Loaded custom formula: {formula.name}")
                    except Exception as e:
                        logger.error(f"Failed to load custom formula '{formula.name}': {e}")
                        continue
                
                logger.info(f"Loaded {len(cls.CUSTOM_FORMULAS)} custom formulas from database")
                cls._custom_formulas_loaded = True
                
            finally:
                db.close()
                
        except ImportError as e:
            logger.warning(f"Cannot load custom formulas - import error: {e}")
            cls._custom_formulas_loaded = True
        except Exception as e:
            logger.error(f"Error loading custom formulas from database: {e}")
            cls._custom_formulas_loaded = True

    @classmethod
    def reload_custom_formulas(cls) -> int:
        """
        Force reload of custom formulas from database.
        
        Call this after publishing new formulas to make them
        available immediately without server restart.
        
        Returns:
            Number of formulas loaded
        """
        cls.CUSTOM_FORMULAS.clear()
        cls._custom_formulas_loaded = False
        cls.SAFE_FUNCTIONS = None  # Force full reload
        cls._get_safe_functions()
        return len(cls.CUSTOM_FORMULAS)
    
    @staticmethod
    def generate_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate variables from a JSON schema, including computed variables.
        
        Supports:
        - Basic types: integer, number, string, boolean, array
        - Enum values for constrained choices
        - Computed variables using safe formulas
        
        Args:
            schema: JSON schema defining variable generation rules
            
        Returns:
            Dictionary of generated variables (including computed ones)
        """
        variables = {}
        
        if not isinstance(schema, dict):
            return variables
            
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            # Step 1: Generate base variables from properties
            properties = schema.get('properties', {})
            for var_name, var_schema in properties.items():
                variables[var_name] = VariableGenerator._generate_single_variable(var_schema)
            
            # Step 2: Compute derived variables
            computed = schema.get('computed', {})
            for var_name, compute_schema in computed.items():
                try:
                    formula = compute_schema.get('formula', '')
                    if formula:
                        variables[var_name] = VariableGenerator._evaluate_formula(formula, variables)
                except Exception as e:
                    # Log but don't fail - use a fallback
                    print(f"Warning: Failed to compute '{var_name}': {e}")
                    variables[var_name] = compute_schema.get('default', None)
        
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
    def _evaluate_formula(formula: str, variables: Dict[str, Any]) -> Any:
        """
        Safely evaluate a formula using pre-defined safe functions.
        
        Args:
            formula: Formula string (e.g., "gcd(a, b)" or "a * b")
            variables: Current variables dict
            
        Returns:
            Computed result
        """
        safe_funcs = VariableGenerator._get_safe_functions()
        
        # Create evaluation context with variables and safe functions
        eval_context = {**variables, **safe_funcs}
        
        try:
            return eval(formula, {"__builtins__": {}}, eval_context)
        except Exception as e:
            raise ValueError(f"Formula evaluation failed for '{formula}': {e}")
    
    @staticmethod
    def _generate_single_variable(var_schema: Dict[str, Any]) -> Any:
        """Generate a single variable based on its schema."""
        var_type = var_schema.get('type', 'string')
        
        # Check for enum values first (works for any type)
        enum_values = var_schema.get('enum')
        if enum_values:
            return random.choice(enum_values)
        
        if var_type == 'integer':
            minimum = var_schema.get('minimum', 1)
            maximum = var_schema.get('maximum', 100)
            return random.randint(minimum, maximum)
        
        elif var_type == 'number':
            minimum = var_schema.get('minimum', 1.0)
            maximum = var_schema.get('maximum', 100.0)
            return round(random.uniform(minimum, maximum), 2)
        
        elif var_type == 'string':
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
        import math
        self.jinja_env = Environment(loader=BaseLoader())
        # Add math functions to Jinja2 globals for use in templates
        self.jinja_env.globals['gcd'] = math.gcd
        self.jinja_env.globals['lcm'] = getattr(math, 'lcm', lambda a, b: abs(a * b) // math.gcd(a, b))
        self.jinja_env.globals['sqrt'] = math.sqrt
        self.jinja_env.globals['floor'] = math.floor
        self.jinja_env.globals['ceil'] = math.ceil
        self.jinja_env.globals['abs'] = abs
        self.jinja_env.globals['min'] = min
        self.jinja_env.globals['max'] = max
        self.jinja_env.globals['pow'] = pow
    
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
        import math
        
        # Create a safe execution environment with math functions
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
                'pow': pow,
                'divmod': divmod,
            },
            'variables': variables,  # Make variables accessible
            # Add math functions commonly needed for educational content
            'math': math,  # Full math module access
            'gcd': math.gcd,  # Direct access to GCD
            'lcm': getattr(math, 'lcm', lambda a, b: abs(a * b) // math.gcd(a, b)),  # LCM (Python 3.9+)
            'sqrt': math.sqrt,
            'floor': math.floor,
            'ceil': math.ceil,
            'factorial': math.factorial,
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
    
    async def generate_question(self, template_id: int, allow_any_status: bool = False) -> Dict[str, Any]:
        """
        Generate a complete question instance from a template.
        
        Args:
            template_id: ID of the question template
            allow_any_status: If True, allows generation from non-PUBLISHED templates (for preview)
            
        Returns:
            Lean question payload dictionary with quality content
        """
        # Fetch template from database
        if allow_any_status:
            template = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.id == template_id
            ).first()
        else:
            template = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.id == template_id,
                QuestionTemplate.status == "PUBLISHED"
            ).first()
        
        if not template:
            status_msg = "" if allow_any_status else "Published "
            raise ValueError(f"{status_msg}template with ID {template_id} not found")
        
        # Step 1: Generate variables
        variables = self.variable_generator.generate_from_schema(template.variable_schema)
        
        # Step 2: Render question and options
        question_text = self.template_renderer.render_pattern(template.question_pattern, variables)
        rendered_options = self.template_renderer.render_options(template.option_patterns, variables)
        
        # Step 3: Compute correct answer
        correct_answer = self.answer_evaluator.evaluate_answer_logic(template.answer_logic, variables)
        correct_index = self.answer_evaluator.find_correct_index(rendered_options, correct_answer)
        
        # Step 4: Generate quality content (solution, hints, narrative)
        solution_steps = self._render_solution_steps(template, variables)
        visual_hints = self._render_hints(template, variables)
        rich_narrative = self._render_narrative(template, variables)
        
        # Step 5: Generate diagram URLs using CDN (Phase 6)
        diagram_urls = await self._generate_diagrams(template, variables)
        
        # Step 6: Create lean payload with quality content
        lean_payload = {
            "id": f"q_{template_id}_{random.randint(1000, 9999)}",
            "template_id": template_id,
            "question": question_text,
            "options": rendered_options,
            "diagrams": diagram_urls,  # Phase 6: CDN URLs instead of inline HTML
            "solution_steps": solution_steps,  # NEW: Step-by-step solution
            "visual_hints": visual_hints,  # NEW: Progressive hints
            "rich_narrative": rich_narrative,  # NEW: Story narrative
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
    
    def _render_solution_steps(self, template, variables: Dict[str, Any]) -> List[str]:
        """Render step-by-step solution from template pattern."""
        if not template.solution_pattern:
            # Fallback: Generate basic solution from answer logic
            correct_answer = self.answer_evaluator.evaluate_answer_logic(template.answer_logic, variables)
            return [
                f"Apply the formula/logic to solve",
                f"The correct answer is: {correct_answer}"
            ]
        
        try:
            # Render solution pattern with variables
            rendered = self.template_renderer.render_pattern(template.solution_pattern, variables)
            # Split by newlines or numbered markers
            steps = [s.strip() for s in rendered.split('\n') if s.strip()]
            return steps if steps else [rendered]
        except Exception as e:
            print(f"Warning: Failed to render solution steps: {e}")
            return ["Solution steps unavailable"]
    
    def _render_hints(self, template, variables: Dict[str, Any]) -> List[str]:
        """Render progressive hints from template pattern."""
        if not template.hint_pattern:
            # Fallback: Generate concept-based hints
            concept = template.concept_id.split('.')[-1].replace('_', ' ')
            return [
                f"Think about the key concept: {concept}",
                "Break down the problem step by step",
                "Check your calculations carefully"
            ]
        
        try:
            rendered = self.template_renderer.render_pattern(template.hint_pattern, variables)
            hints = [h.strip() for h in rendered.split('\n') if h.strip()]
            return hints if hints else [rendered]
        except Exception as e:
            print(f"Warning: Failed to render hints: {e}")
            return ["Hint unavailable"]
    
    def _render_narrative(self, template, variables: Dict[str, Any]) -> Optional[str]:
        """Render rich story narrative from template pattern."""
        if not template.narrative_pattern:
            return None
        
        try:
            return self.template_renderer.render_pattern(template.narrative_pattern, variables)
        except Exception as e:
            print(f"Warning: Failed to render narrative: {e}")
            return None
    
    async def _generate_diagrams(self, template, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate diagram URLs using CDN or diagram_config."""
        diagram_urls = []
        
        # Use new diagram_config if available
        if template.diagram_config:
            try:
                config = template.diagram_config
                diagram_type = config.get('type', 'generic')
                
                # Extract diagram parameters from variables based on config mappings
                diagram_params = {}
                for param_name, var_path in config.get('variable_mappings', {}).items():
                    if var_path in variables:
                        diagram_params[param_name] = variables[var_path]
                
                # Add any static parameters from config
                diagram_params.update(config.get('static_params', {}))
                
                # Generate CDN URL
                diagram_url = await self.cdn_service.render_diagram_dynamically(
                    diagram_type, diagram_params
                )
                
                diagram_urls.append({
                    'type': diagram_type,
                    'url': diagram_url,
                    'alt_text': config.get('alt_text', f"Diagram for {diagram_type}")
                })
            except Exception as e:
                print(f"Warning: Failed to generate diagram from config: {e}")
        
        # Also process legacy diagram relations
        if template.diagrams:
            for diagram in template.diagrams:
                try:
                    diagram_params = self._generate_diagram_parameters(diagram, variables)
                    diagram_url = await self.cdn_service.render_diagram_dynamically(
                        diagram.diagram_type, diagram_params
                    )
                    diagram_urls.append({
                        'id': diagram.id,
                        'name': diagram.name,
                        'type': diagram.diagram_type,
                        'url': diagram_url,
                        'alt_text': diagram.alt_text or f"Diagram: {diagram.name}"
                    })
                except Exception as e:
                    print(f"Warning: Failed to generate diagram {diagram.id}: {e}")
                    continue
        
        return diagram_urls
    
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
