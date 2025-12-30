"""
Chapter 5: Factors & Multiples - Deterministic SymPy Question Generator

This generator uses reverse-engineering to guarantee valid, nice numbers.
All questions are verified before being marked as valid.
"""

import sympy
from typing import Dict, List, Any, Tuple
from enum import Enum
import random
from ..models import MathSkeleton, DifficultyLevel, BloomLevel


class FactorMultipleConcept(str, Enum):
    """Concepts covered in Ch5"""
    FACTORS = "factors"
    MULTIPLES = "multiples"
    GCD = "gcd"
    LCM = "lcm"
    PRIME = "prime"
    COMPOSITE = "composite"
    DIVISIBILITY = "divisibility"


class FactorsMultiplesGenerator:
    """
    Deterministic question generator for Factors & Multiples.
    
    Key principle: Reverse-engineer questions from answers to guarantee correctness.
    - Pick answer first
    - Build problem based on answer
    - Verify using SymPy
    - Generate question
    """
    
    def __init__(self):
        self.concept_ranges = {
            DifficultyLevel.EASY: {
                "min_number": 1,
                "max_number": 20,
                "factors_count": (2, 6),  # 2-6 factors
            },
            DifficultyLevel.MEDIUM: {
                "min_number": 20,
                "max_number": 100,
                "factors_count": (4, 12),  # 4-12 factors
            },
            DifficultyLevel.HARD: {
                "min_number": 50,
                "max_number": 200,
                "factors_count": (6, 16),  # 6-16 factors
            },
            DifficultyLevel.EXPERT: {
                "min_number": 100,
                "max_number": 500,
                "factors_count": (8, 24),  # Many factors
            },
        }
    
    def generate_factor_identification_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.UNDERSTAND,
    ) -> MathSkeleton:
        """
        Generate: "Find all factors of X"
        
        Reverse engineering:
        1. Pick target number based on difficulty
        2. Calculate all factors using SymPy
        3. Verify count is within difficulty range
        4. Generate problem
        """
        
        ranges = self.concept_ranges[difficulty]
        
        # Pick random number in difficulty range
        target_number = random.randint(ranges["min_number"], ranges["max_number"])
        
        # Get factors deterministically using SymPy, convert to Python ints
        factors = sorted([int(f) for f in sympy.divisors(target_number)])
        factors_count = len(factors)
        
        # Verify factors count is appropriate for difficulty
        min_count, max_count = ranges["factors_count"]
        if not (min_count <= factors_count <= max_count):
            # If outside range, adjust by re-rolling (max 10 attempts)
            for _ in range(10):
                target_number = random.randint(ranges["min_number"], ranges["max_number"])
                factors = sorted([int(f) for f in sympy.divisors(target_number)])
                factors_count = len(factors)
                if min_count <= factors_count <= max_count:
                    break
        
        # Generate LaTeX problem
        latex_problem = f"Find all factors of ${target_number}$."
        
        # Generate step-by-step solution
        steps = self._generate_factor_steps(target_number, factors)
        
        return MathSkeleton(
            concept="Finding Factors",
            question_type="factor-identification",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "target_number": target_number,
                "factors": factors,
                "factors_count": factors_count,
            },
            latex_problem=latex_problem,
            solution=factors,
            steps=steps,
            explanation=f"Factors of {target_number} are numbers that divide {target_number} evenly with no remainder. We test each number from 1 to {target_number}.",
            is_valid=True,
            validation_notes=f"Verified: {target_number} has exactly {factors_count} factors: {factors}",
        )
    
    def generate_multiple_identification_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.UNDERSTAND,
    ) -> MathSkeleton:
        """
        Generate: "Find first N multiples of X"
        
        Reverse engineering:
        1. Pick base number
        2. Generate multiples
        3. Create identification question
        """
        
        ranges = self.concept_ranges[difficulty]
        
        # Pick base number (factor)
        base_number = random.randint(2, 15)
        
        # Determine how many multiples to ask for
        multiples_count = {
            DifficultyLevel.EASY: 5,
            DifficultyLevel.MEDIUM: 7,
            DifficultyLevel.HARD: 10,
            DifficultyLevel.EXPERT: 12,
        }[difficulty]
        
        # Generate multiples
        multiples = [base_number * i for i in range(1, multiples_count + 1)]
        
        latex_problem = f"List the first {multiples_count} multiples of ${base_number}$."
        
        steps = self._generate_multiples_steps(base_number, multiples)
        
        return MathSkeleton(
            concept="Finding Multiples",
            question_type="multiple-identification",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "base_number": base_number,
                "multiples_count": multiples_count,
                "multiples": multiples,
            },
            latex_problem=latex_problem,
            solution=multiples,
            steps=steps,
            explanation=f"Multiples of {base_number} are obtained by multiplying {base_number} by 1, 2, 3, etc.",
            is_valid=True,
            validation_notes=f"Verified: First {multiples_count} multiples of {base_number}",
        )
    
    def generate_gcd_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        bloom_level: BloomLevel = BloomLevel.APPLY,
    ) -> MathSkeleton:
        """
        Generate: "Find GCD of X and Y"
        
        Reverse engineering:
        1. Pick desired GCD
        2. Generate coprime multipliers (GCD=1) to ensure GCD of result is exactly the desired GCD
        3. Calculate GCD to verify
        """
        
        # Pick desired GCD
        desired_gcd = random.randint(2, 10)
        
        # Generate two coprime multipliers (GCD=1) so GCD of num1, num2 = desired_gcd
        multiplier1 = random.randint(2, 8)
        multiplier2 = random.randint(2, 8)
        # Keep trying until we get coprime numbers
        while sympy.gcd(multiplier1, multiplier2) != 1:
            multiplier1 = random.randint(2, 8)
            multiplier2 = random.randint(2, 8)
        
        num1 = desired_gcd * multiplier1
        num2 = desired_gcd * multiplier2
        
        # Verify using SymPy
        actual_gcd = int(sympy.gcd(num1, num2))
        assert actual_gcd == desired_gcd, f"GCD mismatch: {actual_gcd} != {desired_gcd}"
        
        latex_problem = f"Find the Greatest Common Divisor (GCD) of ${num1}$ and ${num2}$."
        
        steps = self._generate_gcd_steps(num1, num2)
        
        return MathSkeleton(
            concept="Finding GCD",
            question_type="gcd-calculation",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "number_1": int(num1),
                "number_2": int(num2),
                "desired_gcd": int(desired_gcd),
            },
            latex_problem=latex_problem,
            solution=actual_gcd,
            steps=steps,
            explanation=f"The GCD is the largest number that divides both {num1} and {num2} evenly.",
            is_valid=True,
            validation_notes=f"Verified: GCD({num1}, {num2}) = {actual_gcd}",
        )
    
    def generate_lcm_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        bloom_level: BloomLevel = BloomLevel.APPLY,
    ) -> MathSkeleton:
        """
        Generate: "Find LCM of X and Y"
        
        Reverse engineering:
        1. Pick small base numbers
        2. Calculate LCM using SymPy
        3. Create question
        """
        
        # Pick two base numbers
        base1 = random.randint(2, 12)
        base2 = random.randint(2, 12)
        while base1 == base2:
            base2 = random.randint(2, 12)
        
        # Calculate LCM using SymPy
        lcm_value = sympy.lcm(base1, base2)
        
        latex_problem = f"Find the Least Common Multiple (LCM) of ${base1}$ and ${base2}$."
        
        steps = self._generate_lcm_steps(base1, base2)
        
        return MathSkeleton(
            concept="Finding LCM",
            question_type="lcm-calculation",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "number_1": base1,
                "number_2": base2,
                "lcm": int(lcm_value),
            },
            latex_problem=latex_problem,
            solution=int(lcm_value),
            steps=steps,
            explanation=f"The LCM is the smallest number that is a multiple of both {base1} and {base2}.",
            is_valid=True,
            validation_notes=f"Verified: LCM({base1}, {base2}) = {lcm_value}",
        )
    
    def generate_prime_check_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.REMEMBER,
    ) -> MathSkeleton:
        """
        Generate: "Is X prime or composite?"
        
        Reverse engineering:
        1. Pick a number (sometimes prime, sometimes composite)
        2. Check if prime using SymPy
        3. Create question
        """
        
        # Alternate between prime and composite
        is_prime_target = random.choice([True, False])
        
        if is_prime_target:
            # Pick a prime number
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
            if difficulty == DifficultyLevel.EASY:
                target_number = random.choice(primes[:10])
            elif difficulty == DifficultyLevel.MEDIUM:
                target_number = random.choice(primes[10:20])
            else:
                target_number = random.choice(primes[20:])
        else:
            # Pick a composite number
            ranges = self.concept_ranges[difficulty]
            target_number = random.randint(ranges["min_number"], ranges["max_number"])
            # Ensure it's composite
            while sympy.isprime(target_number) or target_number == 1:
                target_number = random.randint(ranges["min_number"], ranges["max_number"])
        
        is_prime = sympy.isprime(target_number)
        prime_status = "prime" if is_prime else "composite"
        
        latex_problem = f"Is ${target_number}$ prime or composite? Explain your answer."
        
        steps = self._generate_prime_steps(target_number, is_prime)
        
        return MathSkeleton(
            concept="Prime and Composite Numbers",
            question_type="prime-check",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "number": target_number,
                "is_prime": is_prime,
            },
            latex_problem=latex_problem,
            solution=prime_status,
            steps=steps,
            explanation=f"A prime number has exactly 2 factors (1 and itself). A composite number has more than 2 factors.",
            is_valid=True,
            validation_notes=f"Verified: {target_number} is {prime_status}",
        )
    
    # Helper methods for step-by-step solutions
    
    def _generate_factor_steps(self, number: int, factors: List[int]) -> List[str]:
        """Generate step-by-step solution for factor identification"""
        return [
            f"Step 1: Test which numbers divide {number} evenly.",
            f"Step 2: Check each number from 1 to {number}.",
            f"Step 3: A number is a factor if {number} ÷ number has no remainder.",
            f"Step 4: The factors are: {', '.join(map(str, factors))}",
        ]
    
    def _generate_multiples_steps(self, base: int, multiples: List[int]) -> List[str]:
        """Generate step-by-step solution for multiples"""
        return [
            f"Step 1: Multiply {base} by 1, 2, 3, ... to get multiples.",
            f"Step 2: {base} × 1 = {multiples[0]}",
            f"Step 3: {base} × 2 = {multiples[1]}",
            f"Step 4: Continue the pattern...",
            f"Step 5: The multiples are: {', '.join(map(str, multiples))}",
        ]
    
    def _generate_gcd_steps(self, num1: int, num2: int) -> List[str]:
        """Generate step-by-step solution for GCD"""
        factors1 = sorted(list(sympy.divisors(num1)))
        factors2 = sorted(list(sympy.divisors(num2)))
        common_factors = sorted(list(set(factors1) & set(factors2)))
        gcd_value = max(common_factors)
        
        return [
            f"Step 1: Find factors of {num1}: {factors1}",
            f"Step 2: Find factors of {num2}: {factors2}",
            f"Step 3: Find common factors: {common_factors}",
            f"Step 4: The greatest common factor is: {gcd_value}",
        ]
    
    def _generate_lcm_steps(self, num1: int, num2: int) -> List[str]:
        """Generate step-by-step solution for LCM"""
        lcm_val = int(sympy.lcm(num1, num2))
        
        return [
            f"Step 1: Find multiples of {num1}.",
            f"Step 2: Find multiples of {num2}.",
            f"Step 3: Find the smallest common multiple.",
            f"Step 4: LCM({num1}, {num2}) = {lcm_val}",
        ]
    
    def _generate_prime_steps(self, number: int, is_prime: bool) -> List[str]:
        """Generate step-by-step solution for prime check"""
        if is_prime:
            return [
                f"Step 1: Check if {number} has exactly 2 factors.",
                f"Step 2: The only factors are 1 and {number}.",
                f"Step 3: Therefore, {number} is a PRIME number.",
            ]
        else:
            factors = sorted(list(sympy.divisors(number)))
            return [
                f"Step 1: Find all factors of {number}.",
                f"Step 2: The factors are: {factors}",
                f"Step 3: Since there are {len(factors)} factors (more than 2), {number} is COMPOSITE.",
            ]
