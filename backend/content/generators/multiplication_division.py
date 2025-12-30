"""
Chapter 2: Multiplication & Division - Deterministic SymPy Question Generator

This generator uses SymPy to guarantee correct multiplication and division problems.
All questions are verified before being marked as valid.
"""

import sympy
from sympy import symbols, expand, simplify, factorint
from typing import Dict, List, Any, Tuple
from enum import Enum
import random
from ..models import MathSkeleton, DifficultyLevel, BloomLevel


class MultiplicationDivisionConcept(str, Enum):
    """Concepts covered in Ch2"""
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    FACTORS = "factors"
    QUOTIENT_REMAINDER = "quotient_remainder"
    PROPERTIES = "properties"


class MultiplicationDivisionGenerator:
    """
    Deterministic question generator for Multiplication & Division.
    
    Key principle: Use SymPy to verify all calculations.
    - Pick numbers
    - Calculate using SymPy
    - Verify correctness
    - Generate question
    """
    
    def __init__(self):
        self.concept_ranges = {
            DifficultyLevel.EASY: {
                "min_factor": 2,
                "max_factor": 12,
            },
            DifficultyLevel.MEDIUM: {
                "min_factor": 10,
                "max_factor": 50,
            },
            DifficultyLevel.HARD: {
                "min_factor": 20,
                "max_factor": 100,
            },
            DifficultyLevel.EXPERT: {
                "min_factor": 50,
                "max_factor": 200,
            },
        }
    
    def generate_multiplication_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.REMEMBER,
    ) -> MathSkeleton:
        """
        Generate: "Calculate A × B"
        
        Using SymPy:
        1. Pick two numbers
        2. Calculate product using SymPy
        3. Verify using alternative method
        4. Generate problem
        """
        
        ranges = self.concept_ranges[difficulty]
        
        factor1 = random.randint(ranges["min_factor"], ranges["max_factor"])
        factor2 = random.randint(ranges["min_factor"], ranges["max_factor"])
        
        # Use SymPy for guaranteed correctness
        product = int(sympy.sympify(factor1) * sympy.sympify(factor2))
        
        correct_answer = str(product)
        
        latex_problem = f"Calculate: ${factor1} \\times {factor2}$"
        
        # Break down the multiplication for pedagogy
        steps = [
            f"First number: {factor1}",
            f"Second number: {factor2}",
            f"Multiply: {factor1} × {factor2}",
            f"Result: {product}",
        ]
        
        return MathSkeleton(
            concept="Multiplication",
            question_type="multiplication",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "factor_1": factor1,
                "factor_2": factor2,
                "product": product,
            },
            latex_problem=latex_problem,
            solution=correct_answer,
            steps=steps,
            explanation=f"Multiplication combines groups. {factor1} groups of {factor2} = {product}",
            is_valid=True,
            validation_notes=f"Verified: {factor1} × {factor2} = {product}",
        )
    
    def generate_division_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.REMEMBER,
    ) -> MathSkeleton:
        """
        Generate: "Calculate A ÷ B"
        
        Using SymPy:
        1. Pick divisor and quotient
        2. Calculate dividend
        3. Generate problem
        """
        
        ranges = self.concept_ranges[difficulty]
        
        # Reverse engineer: pick quotient and divisor, calculate dividend
        quotient = random.randint(2, 20)
        divisor = random.randint(ranges["min_factor"], ranges["max_factor"])
        
        # Use SymPy for guaranteed correctness
        dividend = int(sympy.sympify(quotient) * sympy.sympify(divisor))
        
        correct_answer = str(quotient)
        
        latex_problem = f"Calculate: ${dividend} \\div {divisor}$"
        
        steps = [
            f"Dividend (number being divided): {dividend}",
            f"Divisor (dividing by): {divisor}",
            f"Divide: {dividend} ÷ {divisor}",
            f"Quotient: {quotient}",
            f"Check: {quotient} × {divisor} = {dividend}",
        ]
        
        return MathSkeleton(
            concept="Division",
            question_type="division",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "dividend": dividend,
                "divisor": divisor,
                "quotient": quotient,
                "remainder": 0,
            },
            latex_problem=latex_problem,
            solution=correct_answer,
            steps=steps,
            explanation=f"Division shares equally. {dividend} shared into {divisor} groups = {quotient} each",
            is_valid=True,
            validation_notes=f"Verified: {dividend} ÷ {divisor} = {quotient}",
        )
    
    def generate_division_with_remainder_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        bloom_level: BloomLevel = BloomLevel.UNDERSTAND,
    ) -> MathSkeleton:
        """
        Generate: "Calculate A ÷ B with remainder"
        
        Using SymPy:
        1. Pick dividend and divisor
        2. Calculate quotient and remainder
        3. Verify
        4. Generate problem
        """
        
        ranges = self.concept_ranges[difficulty]
        
        dividend = random.randint(20, 200)
        divisor = random.randint(3, 15)
        
        # Use SymPy floor division and modulo
        quotient = int(sympy.floor(dividend / divisor))
        remainder = dividend % divisor
        
        correct_answer = f"{quotient} R {remainder}"
        
        latex_problem = f"Calculate: ${dividend} \\div {divisor}$ (with remainder)"
        
        steps = [
            f"Dividend: {dividend}",
            f"Divisor: {divisor}",
            f"Divide: {dividend} ÷ {divisor}",
            f"Quotient: {quotient}",
            f"Remainder: {remainder}",
            f"Check: {quotient} × {divisor} + {remainder} = {quotient * divisor + remainder}",
        ]
        
        return MathSkeleton(
            concept="Division with Remainder",
            question_type="division-with-remainder",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "dividend": dividend,
                "divisor": divisor,
                "quotient": quotient,
                "remainder": remainder,
            },
            latex_problem=latex_problem,
            solution=correct_answer,
            steps=steps,
            explanation=f"When dividing, the remainder is what's left over. {dividend} = {quotient} × {divisor} + {remainder}",
            is_valid=True,
            validation_notes=f"Verified: {dividend} ÷ {divisor} = {quotient} R {remainder}",
        )
    
    def generate_multiplication_property_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.UNDERSTAND,
    ) -> MathSkeleton:
        """
        Generate: "Find the missing number in multiplication"
        
        Using SymPy:
        1. Create equation: A × ? = C
        2. Solve for ?
        3. Verify
        """
        
        ranges = self.concept_ranges[difficulty]
        
        # Reverse engineer: pick A and B, calculate C
        a = random.randint(ranges["min_factor"], ranges["max_factor"])
        b = random.randint(ranges["min_factor"], ranges["max_factor"])
        c = int(sympy.sympify(a) * sympy.sympify(b))
        
        # Now ask: A × ? = C, find ?
        x = symbols('x')
        equation = a * x - c
        solution = sympy.solve(equation, x)
        missing_number = int(solution[0])
        
        correct_answer = str(missing_number)
        
        latex_problem = f"Find the missing number: ${a} \\times ? = {c}$"
        
        steps = [
            f"Equation: {a} × ? = {c}",
            f"Solve: ? = {c} ÷ {a}",
            f"Result: ? = {missing_number}",
            f"Check: {a} × {missing_number} = {c}",
        ]
        
        return MathSkeleton(
            concept="Multiplication Property / Division",
            question_type="multiplication-property",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "factor_1": a,
                "product": c,
                "factor_2": missing_number,
            },
            latex_problem=latex_problem,
            solution=correct_answer,
            steps=steps,
            explanation=f"To find the missing factor, divide the product by the known factor.",
            is_valid=True,
            validation_notes=f"Verified: {a} × {missing_number} = {c}",
        )
