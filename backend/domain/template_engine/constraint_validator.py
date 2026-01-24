"""
Constraint Validator for Template Engine.

Handles two-phase constraint validation:
1. Base-only constraints (checked after generating base variables)
2. Computed constraints (checked after computing derived variables)

Separation of Concerns:
- This module ONLY validates constraints
- No variable generation logic
- No template rendering logic
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Set

from domain.template_engine.safe_functions import safe_functions

logger = logging.getLogger(__name__)


class ConstraintValidator:
    """
    Validates constraints on template variables.
    
    Supports:
    - Comparison: a > b, n1 < 300, x != y
    - Arithmetic in constraints: a + b < 100
    - Function calls: gcd(a, b) > 1, is_prime(n)
    - Logical operators: a > 0 and b > 0
    
    Two-phase validation:
    1. Base constraints: Only reference base variables
    2. Computed constraints: Can reference any variables
    """
    
    def __init__(self):
        self.safe_funcs = safe_functions.get_all()
    
    def categorize_constraints(
        self,
        constraints: List[str],
        base_vars: Set[str],
        computed_vars: Set[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Categorize constraints into base-only and computed.
        
        Args:
            constraints: List of constraint expressions
            base_vars: Set of base variable names
            computed_vars: Set of computed variable names
            
        Returns:
            Tuple of (base_only_constraints, computed_constraints)
        """
        base_only = []
        computed = []
        
        # Keywords and function names to exclude from variable detection
        keywords = {
            'and', 'or', 'not', 'True', 'False', 'None', 
            'in', 'is', 'if', 'else'
        }
        func_names = set(self.safe_funcs.keys())
        exclude = keywords | func_names
        
        for constraint in constraints:
            # Extract potential variable names from constraint
            tokens = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', constraint))
            var_tokens = tokens - exclude
            
            # Check if any token is a computed variable
            uses_computed = bool(var_tokens & computed_vars)
            
            if uses_computed:
                computed.append(constraint)
            else:
                base_only.append(constraint)
        
        logger.debug(f"Categorized constraints: {len(base_only)} base, {len(computed)} computed")
        return base_only, computed
    
    def validate(
        self,
        constraints: List[str],
        variables: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate all constraints against given variables.
        
        Args:
            constraints: List of constraint expressions
            variables: Current variable values
            
        Returns:
            Tuple of (all_passed, list_of_failed_constraints)
        """
        if not constraints:
            return True, []
        
        # Build evaluation namespace
        namespace = {**self.safe_funcs, **variables}
        namespace['__builtins__'] = {}
        
        failed = []
        
        for constraint in constraints:
            try:
                result = eval(constraint, namespace)
                if not result:
                    failed.append(constraint)
                    logger.debug(f"Constraint failed: {constraint} with vars {self._summarize_vars(variables)}")
            except NameError as e:
                # Variable not yet available - fail silently
                failed.append(constraint)
                logger.debug(f"Constraint eval error (NameError): {constraint} - {e}")
            except Exception as e:
                # Other evaluation error
                failed.append(constraint)
                logger.warning(f"Constraint eval error: {constraint} - {e}")
        
        return len(failed) == 0, failed
    
    def validate_base_constraints(
        self,
        constraints: List[str],
        base_vars: Set[str],
        computed_vars: Set[str],
        variables: Dict[str, Any]
    ) -> bool:
        """
        Validate only base constraints (Phase 1).
        
        Args:
            constraints: All constraints
            base_vars: Set of base variable names
            computed_vars: Set of computed variable names
            variables: Current base variable values
            
        Returns:
            True if all base constraints pass
        """
        base_only, _ = self.categorize_constraints(constraints, base_vars, computed_vars)
        passed, failed = self.validate(base_only, variables)
        return passed
    
    def validate_all_constraints(
        self,
        constraints: List[str],
        variables: Dict[str, Any]
    ) -> bool:
        """
        Validate all constraints (Phase 2).
        
        Args:
            constraints: All constraints
            variables: All variable values (base + computed)
            
        Returns:
            True if all constraints pass
        """
        passed, failed = self.validate(constraints, variables)
        return passed
    
    def get_variables_in_constraint(self, constraint: str) -> Set[str]:
        """
        Extract variable names from a constraint expression.
        
        Args:
            constraint: Constraint expression string
            
        Returns:
            Set of variable names found in the constraint
        """
        # Keywords and function names to exclude
        keywords = {
            'and', 'or', 'not', 'True', 'False', 'None',
            'in', 'is', 'if', 'else'
        }
        func_names = set(self.safe_funcs.keys())
        exclude = keywords | func_names
        
        # Find all potential identifiers
        tokens = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', constraint))
        
        return tokens - exclude
    
    def _summarize_vars(self, variables: Dict[str, Any], max_vars: int = 5) -> str:
        """Create a short summary of variables for logging."""
        items = list(variables.items())[:max_vars]
        summary = ", ".join(f"{k}={v}" for k, v in items)
        if len(variables) > max_vars:
            summary += f" ... (+{len(variables) - max_vars} more)"
        return summary


# Singleton instance
constraint_validator = ConstraintValidator()
