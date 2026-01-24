"""
Variable Generator for Template Engine.

Handles generation of:
1. Base variables (random values from schema)
2. Computed variables (formulas using base variables)

With two-phase constraint validation:
1. Generate base vars → validate base constraints
2. Compute derived vars → validate all constraints

Separation of Concerns:
- This module ONLY generates variables
- Uses safe_functions.py for formula evaluation
- Uses constraint_validator.py for validation
- No template rendering logic
"""

import random
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass

from domain.template_engine.safe_functions import safe_functions
from domain.template_engine.constraint_validator import constraint_validator

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result of variable generation."""
    success: bool
    variables: Dict[str, Any]
    attempts: int
    failed_constraints: List[str]
    error: Optional[str] = None


class VariableGenerator:
    """
    Generates variables from template schema with constraint validation.
    
    Supports variable types:
    - integer: Random integer in range
    - float: Random float in range
    - enum: Random choice from list
    - boolean: Random True/False
    - prime: Random prime number
    - composite: Random composite number
    - multiple_of: Random multiple of a number
    
    Two-phase constraint validation ensures computed constraints
    (like n1 < 300) are properly enforced.
    """
    
    MAX_ATTEMPTS = 100  # Max attempts to satisfy all constraints
    
    def __init__(self, custom_functions: Dict[str, Any] = None):
        """
        Initialize generator with optional custom functions.
        
        Args:
            custom_functions: Additional functions for formula evaluation
        """
        self.functions = safe_functions.get_all()
        if custom_functions:
            self.functions.update(custom_functions)
    
    def generate(
        self,
        schema: Dict[str, Any],
        seed: Optional[int] = None
    ) -> GenerationResult:
        """
        Generate variables from schema with constraint validation.
        
        Uses two-phase constraint validation:
        1. Generate base variables
        2. Check base-only constraints (fail fast)
        3. Compute derived variables
        4. Check ALL constraints (including computed)
        
        Args:
            schema: Variable schema with base, computed, constraints, custom_functions
            seed: Optional random seed for reproducibility
            
        Returns:
            GenerationResult with success status and variables
        """
        if seed is not None:
            random.seed(seed)
        
        # Extract schema components
        base_config = schema.get('base', schema.get('properties', {}))
        computed_config = schema.get('computed', {})
        constraints = schema.get('constraints', [])
        custom_function_defs = schema.get('custom_functions', {})
        
        # Compile custom functions
        custom_funcs = self._compile_custom_functions(custom_function_defs)
        
        # Store for use during evaluation
        self._active_custom_functions = custom_funcs
        
        # Get variable name sets for constraint categorization
        base_var_names = set(base_config.keys())
        computed_var_names = set(computed_config.keys())
        
        # Categorize constraints
        base_constraints, computed_constraints = constraint_validator.categorize_constraints(
            constraints, base_var_names, computed_var_names
        )
        
        logger.debug(
            f"Schema: {len(base_var_names)} base vars, {len(computed_var_names)} computed vars, "
            f"{len(base_constraints)} base constraints, {len(computed_constraints)} computed constraints"
        )
        
        # Try to generate valid variables
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                # Phase 1: Generate base variables
                base_vars = self._generate_base_variables(base_config)
                
                # Phase 1b: Check base-only constraints
                if not constraint_validator.validate_base_constraints(
                    constraints, base_var_names, computed_var_names, base_vars
                ):
                    continue
                
                # Phase 2: Compute derived variables
                all_vars = self._compute_variables(base_vars, computed_config)
                
                # Phase 2b: Check ALL constraints (including computed)
                if not constraint_validator.validate_all_constraints(constraints, all_vars):
                    continue
                
                # Success!
                logger.debug(f"Generated valid variables in {attempt} attempt(s)")
                return GenerationResult(
                    success=True,
                    variables=all_vars,
                    attempts=attempt,
                    failed_constraints=[]
                )
                
            except Exception as e:
                logger.warning(f"Generation attempt {attempt} failed: {e}")
                continue
        
        # Failed to satisfy constraints
        logger.error(f"Failed to generate valid variables after {self.MAX_ATTEMPTS} attempts")
        return GenerationResult(
            success=False,
            variables={},
            attempts=self.MAX_ATTEMPTS,
            failed_constraints=constraints,
            error=f"Failed to satisfy constraints after {self.MAX_ATTEMPTS} attempts"
        )
    
    def _generate_base_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate random values for base variables.
        
        Args:
            config: Base variable configuration
            
        Returns:
            Dictionary of generated base variables
        """
        variables = {}
        
        for name, var_config in config.items():
            variables[name] = self._generate_single(var_config)
        
        return variables
    
    def _generate_single(self, config: Dict[str, Any]) -> Any:
        """
        Generate a single variable value from config.
        
        Args:
            config: Variable configuration
            
        Returns:
            Generated value
        """
        var_type = config.get('type', 'integer')
        
        # Check for enum first (works for any type)
        if 'enum' in config:
            return random.choice(config['enum'])
        
        # Type-specific generation
        if var_type == 'integer':
            return self._gen_integer(config)
        elif var_type == 'float' or var_type == 'number':
            return self._gen_float(config)
        elif var_type == 'boolean':
            return random.choice([True, False])
        elif var_type == 'string':
            return self._gen_string(config)
        elif var_type == 'prime':
            return self._gen_prime(config)
        elif var_type == 'composite':
            return self._gen_composite(config)
        elif var_type == 'multiple_of':
            return self._gen_multiple_of(config)
        else:
            # Default to integer
            return self._gen_integer(config)
    
    def _gen_integer(self, config: Dict[str, Any]) -> int:
        """Generate random integer."""
        min_val = config.get('min', config.get('minimum', 1))
        max_val = config.get('max', config.get('maximum', 100))
        step = config.get('step', 1)
        
        if step == 1:
            return random.randint(min_val, max_val)
        else:
            # Generate value respecting step
            values = list(range(min_val, max_val + 1, step))
            return random.choice(values) if values else min_val
    
    def _gen_float(self, config: Dict[str, Any]) -> float:
        """Generate random float."""
        min_val = config.get('min', config.get('minimum', 0.0))
        max_val = config.get('max', config.get('maximum', 100.0))
        precision = config.get('precision', 2)
        
        return round(random.uniform(min_val, max_val), precision)
    
    def _gen_string(self, config: Dict[str, Any]) -> str:
        """Generate random string."""
        min_len = config.get('minLength', 3)
        max_len = config.get('maxLength', 10)
        charset = config.get('charset', 'abcdefghijklmnopqrstuvwxyz')
        
        length = random.randint(min_len, max_len)
        return ''.join(random.choices(charset, k=length))
    
    def _gen_prime(self, config: Dict[str, Any]) -> int:
        """Generate random prime number."""
        min_val = config.get('min', 2)
        max_val = config.get('max', 100)
        
        is_prime = safe_functions.get_function('is_prime')
        primes = [n for n in range(min_val, max_val + 1) if is_prime(n)]
        
        return random.choice(primes) if primes else 2
    
    def _gen_composite(self, config: Dict[str, Any]) -> int:
        """Generate random composite number."""
        min_val = config.get('min', 4)
        max_val = config.get('max', 100)
        
        is_prime = safe_functions.get_function('is_prime')
        composites = [n for n in range(max(4, min_val), max_val + 1) if n > 1 and not is_prime(n)]
        
        return random.choice(composites) if composites else 4
    
    def _gen_multiple_of(self, config: Dict[str, Any]) -> int:
        """Generate random multiple of a number."""
        base = config.get('of', config.get('base', 1))
        min_val = config.get('min', base)
        max_val = config.get('max', 100)
        
        multiples = [n for n in range(min_val, max_val + 1) if n % base == 0]
        
        return random.choice(multiples) if multiples else base
    
    def _compute_variables(
        self,
        base_vars: Dict[str, Any],
        computed_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute derived variables from formulas.
        
        Handles dependencies between computed variables by iterating
        until all are resolved.
        
        Args:
            base_vars: Generated base variables
            computed_config: Computed variable formulas
            
        Returns:
            Dictionary with all variables (base + computed)
        """
        all_vars = dict(base_vars)
        
        if not computed_config:
            return all_vars
        
        remaining = dict(computed_config)
        max_iterations = len(remaining) + 5
        
        for iteration in range(max_iterations):
            if not remaining:
                break
            
            resolved = []
            
            for name, config in remaining.items():
                formula = config.get('formula', '')
                
                if not formula:
                    all_vars[name] = config.get('default')
                    resolved.append(name)
                    continue
                
                try:
                    result = self._evaluate_formula(formula, all_vars)
                    all_vars[name] = result
                    resolved.append(name)
                except NameError:
                    # Missing dependency, try later
                    continue
                except Exception as e:
                    logger.warning(f"Formula error for '{name}': {formula} - {e}")
                    continue
            
            for name in resolved:
                del remaining[name]
            
            # No progress - possible circular dependency
            if not resolved and remaining:
                raise ValueError(
                    f"Cannot resolve computed variables: {list(remaining.keys())}. "
                    "Check for circular dependencies."
                )
        
        if remaining:
            raise ValueError(f"Failed to compute variables: {list(remaining.keys())}")
        
        return all_vars
    
    def _evaluate_formula(self, formula: str, variables: Dict[str, Any]) -> Any:
        """
        Safely evaluate a formula expression.
        
        Args:
            formula: Formula string (e.g., "gcd(a, b)" or "a * b")
            variables: Current variable values
            
        Returns:
            Computed result
        """
        # Build namespace with safe functions + custom functions + variables
        namespace = {**self.functions, **variables}
        
        # Add any active custom functions
        if hasattr(self, '_active_custom_functions') and self._active_custom_functions:
            namespace.update(self._active_custom_functions)
        
        namespace['__builtins__'] = {}
        
        try:
            result = eval(formula, namespace)
            
            # Convert whole number floats to int
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            return result
        except Exception as e:
            raise ValueError(f"Formula '{formula}' failed: {e}")
    
    def _compile_custom_functions(
        self,
        function_defs: Dict[str, Any]
    ) -> Dict[str, callable]:
        """
        Compile custom function definitions into callable functions.
        
        Args:
            function_defs: Dictionary of function definitions
                {
                    "my_func": {
                        "params": ["x", "y"],
                        "body": "x + y"
                    }
                }
                
        Returns:
            Dictionary of compiled functions
            
        Security:
            - Only evaluates expressions (not statements)
            - Only has access to safe_functions
            - Cannot import modules
        """
        compiled = {}
        
        for name, definition in function_defs.items():
            params = definition.get('params', [])
            body = definition.get('body', '')
            
            if not body:
                logger.warning(f"Custom function '{name}' has empty body, skipping")
                continue
            
            # Create the function dynamically
            compiled[name] = self._make_custom_function(name, params, body)
            logger.debug(f"Compiled custom function: {name}({', '.join(params)}) -> {body}")
        
        return compiled
    
    def _make_custom_function(
        self,
        name: str,
        params: List[str],
        body: str
    ) -> callable:
        """
        Create a callable function from parameters and body expression.
        
        Args:
            name: Function name (for error messages)
            params: Parameter names
            body: Body expression
            
        Returns:
            A callable function
        """
        # Get reference to safe functions for closure
        safe_funcs = self.functions
        # Get reference to the generator instance for accessing other custom functions
        generator = self
        
        def custom_func(*args, **kwargs):
            # Build local namespace for function
            if len(args) > len(params):
                raise ValueError(
                    f"Function '{name}' expects {len(params)} arguments, got {len(args)}"
                )
            
            local_vars = {}
            
            # Positional arguments
            for i, arg in enumerate(args):
                local_vars[params[i]] = arg
            
            # Keyword arguments
            for key, value in kwargs.items():
                if key in local_vars:
                    raise ValueError(f"Duplicate argument: {key}")
                if key not in params:
                    raise ValueError(f"Unknown argument: {key}")
                local_vars[key] = value
            
            # Check all params are provided
            missing = set(params) - set(local_vars.keys())
            if missing:
                raise ValueError(f"Missing arguments for '{name}': {missing}")
            
            # Evaluate body with safe functions, other custom functions, and local variables
            namespace = {**safe_funcs, **local_vars}
            
            # Add other custom functions (allows calling custom funcs from custom funcs)
            if hasattr(generator, '_active_custom_functions') and generator._active_custom_functions:
                namespace.update(generator._active_custom_functions)
            
            namespace['__builtins__'] = {}
            
            try:
                return eval(body, namespace)
            except Exception as e:
                raise ValueError(f"Error in custom function '{name}': {e}")
        
        return custom_func


# Singleton instance
variable_generator = VariableGenerator()
