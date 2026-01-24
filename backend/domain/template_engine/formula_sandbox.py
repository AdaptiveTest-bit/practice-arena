"""
Formula Sandbox - Secure execution environment for custom formulas.

This module provides a sandboxed Python execution environment
that allows content writers to create custom formulas safely.
"""

import ast
import math
import functools
import itertools
from typing import Any, Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import logging

logger = logging.getLogger(__name__)


class FormulaSandboxError(Exception):
    """Custom exception for sandbox errors."""
    pass


class FormulaValidationError(FormulaSandboxError):
    """Raised when formula code fails validation."""
    pass


class FormulaExecutionError(FormulaSandboxError):
    """Raised when formula execution fails."""
    pass


class FormulaSandbox:
    """
    Secure execution environment for custom formulas.
    
    Features:
    - Validates code for forbidden patterns
    - Restricts available builtins
    - Executes with timeout protection
    - Provides safe math and utility functions
    
    Example:
        sandbox = FormulaSandbox()
        
        code = '''
        def add_fractions(n1, d1, n2, d2):
            from math import gcd
            num = n1 * d2 + n2 * d1
            den = d1 * d2
            g = gcd(num, den)
            return (num // g, den // g)
        '''
        
        # Validate
        is_valid, error = sandbox.validate_code(code)
        
        # Execute
        result = sandbox.execute(code, 'add_fractions', [1, 2, 1, 3])
        # Returns: (5, 6)
    """
    
    # Maximum execution time in seconds
    TIMEOUT_SECONDS = 2
    
    # Allowed imports
    ALLOWED_IMPORTS = {'math', 'functools', 'itertools'}
    
    # Safe builtins
    SAFE_BUILTINS = {
        'abs': abs,
        'all': all,
        'any': any,
        'bool': bool,
        'dict': dict,
        'enumerate': enumerate,
        'filter': filter,
        'float': float,
        'int': int,
        'len': len,
        'list': list,
        'map': map,
        'max': max,
        'min': min,
        'pow': pow,
        'range': range,
        'round': round,
        'set': set,
        'sorted': sorted,
        'str': str,
        'sum': sum,
        'tuple': tuple,
        'zip': zip,
        'True': True,
        'False': False,
        'None': None,
    }
    
    # Forbidden patterns that indicate unsafe code
    FORBIDDEN_PATTERNS = [
        '__import__',
        '__builtins__',
        '__class__',
        '__bases__',
        '__subclasses__',
        '__mro__',
        '__globals__',
        '__code__',
        'eval',
        'exec',
        'compile',
        'open',
        'file',
        'input',
        'raw_input',
        'globals',
        'locals',
        'vars',
        'getattr',
        'setattr',
        'delattr',
        'hasattr',
        'os.',
        'os(',
        'sys.',
        'sys(',
        'subprocess',
        'socket',
        'requests',
        'urllib',
        'importlib',
        'pickle',
        'shelve',
        'marshal',
    ]
    
    # Additional math functions to expose
    SAFE_MATH = {
        'gcd': math.gcd,
        'lcm': getattr(math, 'lcm', lambda a, b: abs(a * b) // math.gcd(a, b)),
        'sqrt': math.sqrt,
        'floor': math.floor,
        'ceil': math.ceil,
        'factorial': math.factorial,
        'log': math.log,
        'log10': math.log10,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'pi': math.pi,
        'e': math.e,
    }
    
    def __init__(self):
        """Initialize the sandbox with safe globals."""
        self._executor = ThreadPoolExecutor(max_workers=2)
    
    def validate_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate code for safety.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for forbidden patterns
        code_lower = code.lower()
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern.lower() in code_lower:
                return False, f"Forbidden pattern detected: '{pattern}'"
        
        # Check for valid Python syntax
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Validate AST nodes
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in self.ALLOWED_IMPORTS:
                        return False, f"Import not allowed: '{alias.name}'"
            
            if isinstance(node, ast.ImportFrom):
                if node.module not in self.ALLOWED_IMPORTS:
                    return False, f"Import not allowed: 'from {node.module}'"
            
            # Check for attribute access on dangerous objects
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('_'):
                    return False, f"Access to private attributes not allowed: '{node.attr}'"
        
        return True, "OK"
    
    def _build_safe_globals(self) -> Dict[str, Any]:
        """Build the safe globals dictionary for execution."""
        safe_globals = {
            '__builtins__': self.SAFE_BUILTINS.copy(),
        }
        
        # Add math module
        safe_globals['math'] = type('SafeMath', (), self.SAFE_MATH)()
        
        # Add direct math functions
        safe_globals.update(self.SAFE_MATH)
        
        # Add functools.reduce
        safe_globals['reduce'] = functools.reduce
        
        return safe_globals
    
    def _execute_with_timeout(self, code: str, function_name: str, 
                               args: List[Any]) -> Any:
        """Execute code with timeout protection."""
        safe_globals = self._build_safe_globals()
        safe_locals = {}
        
        # Execute the code to define the function
        exec(code, safe_globals, safe_locals)
        
        # Get the function
        if function_name not in safe_locals:
            raise FormulaExecutionError(
                f"Function '{function_name}' not found in code"
            )
        
        func = safe_locals[function_name]
        
        # Call the function with args
        return func(*args)
    
    def execute(self, code: str, function_name: str, 
                args: List[Any]) -> Any:
        """
        Execute a formula in the sandbox.
        
        Args:
            code: Python code containing the function
            function_name: Name of the function to call
            args: Arguments to pass to the function
            
        Returns:
            Result of the function call
            
        Raises:
            FormulaValidationError: If code fails validation
            FormulaExecutionError: If execution fails
        """
        # Validate first
        is_valid, error = self.validate_code(code)
        if not is_valid:
            raise FormulaValidationError(error)
        
        try:
            # Execute with timeout
            future = self._executor.submit(
                self._execute_with_timeout, 
                code, function_name, args
            )
            return future.result(timeout=self.TIMEOUT_SECONDS)
            
        except TimeoutError:
            raise FormulaExecutionError(
                f"Execution timed out (>{self.TIMEOUT_SECONDS}s)"
            )
        except Exception as e:
            raise FormulaExecutionError(f"Execution failed: {str(e)}")
    
    def run_test_cases(self, code: str, function_name: str,
                       test_cases: List[Dict]) -> List[Dict]:
        """
        Run all test cases for a formula.
        
        Args:
            code: Python code containing the function
            function_name: Name of the function to call
            test_cases: List of {input: [...], expected: ...}
            
        Returns:
            List of test results with pass/fail status
        """
        results = []
        
        for i, test in enumerate(test_cases):
            test_result = {
                'index': i,
                'input': test.get('input', []),
                'expected': test.get('expected'),
            }
            
            try:
                actual = self.execute(code, function_name, test['input'])
                test_result['actual'] = actual
                test_result['passed'] = actual == test['expected']
                test_result['error'] = None
                
            except FormulaSandboxError as e:
                test_result['actual'] = None
                test_result['passed'] = False
                test_result['error'] = str(e)
                
            except Exception as e:
                test_result['actual'] = None
                test_result['passed'] = False
                test_result['error'] = f"Unexpected error: {str(e)}"
            
            results.append(test_result)
        
        return results
    
    def create_callable(self, code: str, function_name: str) -> callable:
        """
        Create a callable function from code.
        
        This is used to add custom formulas to SAFE_FUNCTIONS.
        
        Args:
            code: Python code containing the function
            function_name: Name of the function to call
            
        Returns:
            A callable that executes the formula
        """
        # Validate first
        is_valid, error = self.validate_code(code)
        if not is_valid:
            raise FormulaValidationError(error)
        
        def wrapper(*args):
            return self.execute(code, function_name, list(args))
        
        wrapper.__name__ = function_name
        wrapper.__doc__ = f"Custom formula: {function_name}"
        
        return wrapper


# Singleton instance
_sandbox = None

def get_sandbox() -> FormulaSandbox:
    """Get the singleton sandbox instance."""
    global _sandbox
    if _sandbox is None:
        _sandbox = FormulaSandbox()
    return _sandbox
