"""
Safe Functions Registry for Template Engine.

Provides mathematical and educational functions that content writers
can use in template formulas without writing Python code.

Separation of Concerns:
- This module ONLY defines available functions
- No variable generation logic
- No constraint validation logic
- No template rendering logic
"""

import math
from typing import Dict, Callable, List, Any


class SafeFunctions:
    """
    Registry of safe functions available for formula evaluation.
    
    All functions here are:
    - Safe to execute (no file/network access)
    - Deterministic (same input = same output)
    - Educational (useful for K-12 CBSE content)
    """
    
    _instance = None
    _functions: Dict[str, Callable] = None
    _custom_functions: Dict[str, Callable] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the function registry."""
        self._functions = {}
        self._register_math_functions()
        self._register_number_theory_functions()
        self._register_geometry_functions()
        self._register_utility_functions()
    
    # =========================================================================
    # MATH BASICS
    # =========================================================================
    
    def _register_math_functions(self):
        """Register basic math operations."""
        self._functions.update({
            # Arithmetic
            'abs': abs,
            'min': min,
            'max': max,
            'pow': pow,
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil,
            'sqrt': math.sqrt,
            
            # Type conversion
            'int': int,
            'float': float,
            'str': str,
            
            # GCD/LCM
            'gcd': math.gcd,
            'lcm': self._lcm,
            'gcd_three': self._gcd_three,
            'lcm_three': self._lcm_three,
            
            # Constants
            'pi': math.pi,
            'e': math.e,
        })
    
    @staticmethod
    def _lcm(a: int, b: int) -> int:
        """Least Common Multiple of two numbers."""
        a, b = int(a), int(b)
        if a == 0 or b == 0:
            return 0
        return abs(a * b) // math.gcd(a, b)
    
    @staticmethod
    def _gcd_three(a: int, b: int, c: int) -> int:
        """GCD of three numbers."""
        return math.gcd(math.gcd(int(a), int(b)), int(c))
    
    def _lcm_three(self, a: int, b: int, c: int) -> int:
        """LCM of three numbers."""
        return self._lcm(self._lcm(int(a), int(b)), int(c))
    
    # =========================================================================
    # NUMBER THEORY (K-12 CBSE Focus)
    # =========================================================================
    
    def _register_number_theory_functions(self):
        """Register number theory functions for factors, multiples, primes."""
        self._functions.update({
            # Factors
            'factors': self._get_factors,
            'factor_count': self._factor_count,
            'sum_factors': self._sum_factors,
            'common_factors': self._common_factors,
            
            # Multiples
            'multiples': self._get_multiples,
            'nearest_multiple_above': self._nearest_multiple_above,
            'nearest_multiple_below': self._nearest_multiple_below,
            'lcm_plus_remainder': self._lcm_plus_remainder,
            
            # Primes
            'is_prime': self._is_prime,
            'prime_factors': self._prime_factors,
            'count_primes': self._count_primes_in_range,
            
            # Coprime
            'is_coprime': self._is_coprime,
            
            # Perfect numbers
            'is_perfect_square': self._is_perfect_square,
            'is_perfect_cube': self._is_perfect_cube,
            
            # Digit operations
            'sum_of_digits': self._sum_of_digits,
            'reverse_number': self._reverse_number,
            'digit_count': self._digit_count,
            
            # Divisibility
            'is_divisible': self._is_divisible,
            'divisibility_rule': self._divisibility_rule,
        })
    
    @staticmethod
    def _get_factors(n: int) -> List[int]:
        """Get all factors of a number."""
        n = abs(int(n))
        if n == 0:
            return []
        return sorted([i for i in range(1, n + 1) if n % i == 0])
    
    def _factor_count(self, n: int) -> int:
        """Count of factors of a number."""
        return len(self._get_factors(n))
    
    def _sum_factors(self, n: int) -> int:
        """Sum of all factors of a number."""
        return sum(self._get_factors(n))
    
    def _common_factors(self, a: int, b: int) -> List[int]:
        """Find common factors of two numbers."""
        return self._get_factors(math.gcd(int(a), int(b)))
    
    @staticmethod
    def _get_multiples(n: int, count: int = 10) -> List[int]:
        """Get first 'count' multiples of a number."""
        n = int(n)
        return [n * i for i in range(1, count + 1)]
    
    @staticmethod
    def _nearest_multiple_above(target: int, divisor: int) -> int:
        """Find the smallest multiple of divisor >= target."""
        target, divisor = int(target), int(divisor)
        if divisor == 0:
            return target
        if target % divisor == 0:
            return target
        return ((target // divisor) + 1) * divisor
    
    @staticmethod
    def _nearest_multiple_below(target: int, divisor: int) -> int:
        """Find the largest multiple of divisor <= target."""
        target, divisor = int(target), int(divisor)
        if divisor == 0:
            return target
        return (target // divisor) * divisor
    
    def _lcm_plus_remainder(self, a: int, b: int, remainder: int) -> int:
        """LCM of a and b, plus a remainder."""
        return self._lcm(int(a), int(b)) + int(remainder)
    
    @staticmethod
    def _is_prime(n: int) -> bool:
        """Check if a number is prime."""
        n = abs(int(n))
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def _prime_factors(n: int) -> List[int]:
        """Get prime factorization of a number."""
        n = abs(int(n))
        if n < 2:
            return []
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
    
    def _count_primes_in_range(self, start: int, end: int) -> int:
        """Count prime numbers in a range [start, end]."""
        return sum(1 for i in range(int(start), int(end) + 1) if self._is_prime(i))
    
    @staticmethod
    def _is_coprime(a: int, b: int) -> bool:
        """Check if two numbers are co-prime (GCD = 1)."""
        return math.gcd(int(a), int(b)) == 1
    
    @staticmethod
    def _is_perfect_square(n: int) -> bool:
        """Check if a number is a perfect square."""
        n = int(n)
        if n < 0:
            return False
        root = int(math.sqrt(n))
        return root * root == n
    
    @staticmethod
    def _is_perfect_cube(n: int) -> bool:
        """Check if a number is a perfect cube."""
        n = int(n)
        if n < 0:
            root = -round(abs(n) ** (1/3))
        else:
            root = round(n ** (1/3))
        return root ** 3 == n
    
    @staticmethod
    def _sum_of_digits(n: int) -> int:
        """Sum of digits of a number."""
        return sum(int(d) for d in str(abs(int(n))))
    
    @staticmethod
    def _reverse_number(n: int) -> int:
        """Reverse a number."""
        return int(str(abs(int(n)))[::-1])
    
    @staticmethod
    def _digit_count(n: int) -> int:
        """Count digits in a number."""
        return len(str(abs(int(n))))
    
    @staticmethod
    def _is_divisible(n: int, divisor: int) -> bool:
        """Check if n is divisible by divisor."""
        if divisor == 0:
            return False
        return int(n) % int(divisor) == 0
    
    @staticmethod
    def _divisibility_rule(divisor: int) -> str:
        """Get the divisibility rule for a number."""
        rules = {
            2: "Last digit is even (0, 2, 4, 6, 8)",
            3: "Sum of digits is divisible by 3",
            4: "Last two digits form a number divisible by 4",
            5: "Last digit is 0 or 5",
            6: "Divisible by both 2 and 3",
            8: "Last three digits form a number divisible by 8",
            9: "Sum of digits is divisible by 9",
            10: "Last digit is 0",
            11: "Alternating sum of digits is divisible by 11",
        }
        return rules.get(int(divisor), f"Check if divisible by {divisor}")
    
    # =========================================================================
    # GEOMETRY FUNCTIONS
    # =========================================================================
    
    def _register_geometry_functions(self):
        """Register geometry functions for area, perimeter, volume."""
        self._functions.update({
            # 2D - Areas
            'area_square': lambda s: s * s,
            'area_rectangle': lambda l, w: l * w,
            'area_triangle': lambda b, h: 0.5 * b * h,
            'area_circle': lambda r: math.pi * r * r,
            'area_parallelogram': lambda b, h: b * h,
            'area_trapezium': lambda a, b, h: 0.5 * (a + b) * h,
            'area_rhombus': lambda d1, d2: 0.5 * d1 * d2,
            
            # 2D - Perimeters
            'perimeter_square': lambda s: 4 * s,
            'perimeter_rectangle': lambda l, w: 2 * (l + w),
            'perimeter_triangle': lambda a, b, c: a + b + c,
            'circumference': lambda r: 2 * math.pi * r,
            
            # 3D - Volumes
            'volume_cube': lambda s: s ** 3,
            'volume_cuboid': lambda l, w, h: l * w * h,
            'volume_cylinder': lambda r, h: math.pi * r * r * h,
            'volume_cone': lambda r, h: (1/3) * math.pi * r * r * h,
            'volume_sphere': lambda r: (4/3) * math.pi * r * r * r,
            'volume_hemisphere': lambda r: (2/3) * math.pi * r * r * r,
            
            # 3D - Surface Areas
            'surface_area_cube': lambda s: 6 * s * s,
            'surface_area_cuboid': lambda l, w, h: 2 * (l*w + w*h + h*l),
            'surface_area_cylinder': lambda r, h: 2 * math.pi * r * (r + h),
            'surface_area_sphere': lambda r: 4 * math.pi * r * r,
            'lateral_surface_cylinder': lambda r, h: 2 * math.pi * r * h,
            'lateral_surface_cone': lambda r, l: math.pi * r * l,  # l = slant height
            
            # Pythagorean
            'hypotenuse': lambda a, b: math.sqrt(a*a + b*b),
            'pythagorean_leg': lambda c, a: math.sqrt(c*c - a*a) if c > a else 0,
        })
    
    # =========================================================================
    # UTILITY FUNCTIONS
    # =========================================================================
    
    def _register_utility_functions(self):
        """Register utility functions for lists, strings, etc."""
        self._functions.update({
            # List operations
            'len': len,
            'sum': sum,
            'sorted': sorted,
            'list': list,
            'range': range,
            'first': lambda x: x[0] if x else None,
            'last': lambda x: x[-1] if x else None,
            
            # Boolean
            'True': True,
            'False': False,
            'None': None,
        })
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def get_all(self) -> Dict[str, Any]:
        """Get all available functions."""
        return {**self._functions, **self._custom_functions}
    
    def get_function(self, name: str) -> Callable:
        """Get a specific function by name."""
        if name in self._custom_functions:
            return self._custom_functions[name]
        return self._functions.get(name)
    
    def register_custom(self, name: str, func: Callable):
        """Register a custom function."""
        self._custom_functions[name] = func
    
    def clear_custom(self):
        """Clear all custom functions."""
        self._custom_functions.clear()
    
    def list_functions(self) -> List[str]:
        """List all available function names."""
        return sorted(set(self._functions.keys()) | set(self._custom_functions.keys()))
    
    def list_by_category(self) -> Dict[str, List[str]]:
        """List functions grouped by category."""
        return {
            'math_basics': ['abs', 'min', 'max', 'pow', 'round', 'floor', 'ceil', 'sqrt', 'gcd', 'lcm', 'pi'],
            'number_theory': [
                'factors', 'factor_count', 'sum_factors', 'common_factors',
                'multiples', 'is_prime', 'prime_factors', 'is_coprime',
                'is_perfect_square', 'is_perfect_cube', 'sum_of_digits',
            ],
            'geometry_2d': [
                'area_square', 'area_rectangle', 'area_triangle', 'area_circle',
                'perimeter_square', 'perimeter_rectangle', 'circumference',
            ],
            'geometry_3d': [
                'volume_cube', 'volume_cuboid', 'volume_cylinder', 'volume_cone', 'volume_sphere',
                'surface_area_cube', 'surface_area_cuboid', 'surface_area_cylinder',
            ],
        }


# Singleton instance for easy access
safe_functions = SafeFunctions()
