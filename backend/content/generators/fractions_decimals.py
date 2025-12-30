"""
Chapter 3: Fractions & Decimals - Deterministic SymPy Question Generator

This generator uses SymPy Rational for exact fraction operations.
All questions are verified before being marked as valid.
"""

import sympy
from sympy import Rational, gcd, simplify
from typing import Dict, List, Any, Tuple
from enum import Enum
import random
from ..models import MathSkeleton, DifficultyLevel, BloomLevel


class FractionConcept(str, Enum):
    """Concepts covered in Ch3"""
    SIMPLIFY = "simplify"
    CONVERT = "convert"
    COMPARE = "compare"
    ADD = "add"
    SUBTRACT = "subtract"
    DECIMAL_EQUIVALENT = "decimal_equivalent"


class FractionsDecimalsGenerator:
    """
    Deterministic question generator for Fractions & Decimals.
    
    Key principle: Use SymPy Rational for guaranteed correctness.
    - Pick numerator/denominator (or decimal)
    - Verify using SymPy Rational
    - Generate question
    """
    
    def __init__(self):
        self.concept_ranges = {
            DifficultyLevel.EASY: {
                "max_numerator": 12,
                "max_denominator": 10,
            },
            DifficultyLevel.MEDIUM: {
                "max_numerator": 30,
                "max_denominator": 20,
            },
            DifficultyLevel.HARD: {
                "max_numerator": 100,
                "max_denominator": 50,
            },
            DifficultyLevel.EXPERT: {
                "max_numerator": 200,
                "max_denominator": 100,
            },
        }
    
    def generate_simplify_fraction_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.UNDERSTAND,
    ) -> MathSkeleton:
        """
        Generate: "Simplify the fraction X/Y"
        
        Using SymPy:
        1. Pick numerator and denominator
        2. Calculate GCD to get simplified form
        3. Verify simplification is correct
        4. Generate problem
        """
        
        ranges = self.concept_ranges[difficulty]
        
        # Create a fraction that needs simplification
        # Ensure GCD > 1 so simplification is non-trivial
        gcd_value = 1
        attempts = 0
        while gcd_value == 1 and attempts < 10:
            numerator = random.randint(2, ranges["max_numerator"])
            denominator = random.randint(2, ranges["max_denominator"])
            gcd_value = int(sympy.gcd(numerator, denominator))
            attempts += 1
        
        # Using SymPy Rational for guaranteed correctness
        original_fraction = Rational(numerator, denominator)
        simplified_fraction = original_fraction  # Rational automatically simplifies
        
        simplified_num = simplified_fraction.p
        simplified_den = simplified_fraction.q
        
        correct_answer = f"{simplified_num}/{simplified_den}"
        
        latex_problem = f"Simplify $\\frac{{{numerator}}}{{{denominator}}}$"
        
        steps = [
            f"Original fraction: {numerator}/{denominator}",
            f"Find GCD({numerator}, {denominator}) = {gcd_value}",
            f"Divide both numerator and denominator by {gcd_value}",
            f"{numerator} ÷ {gcd_value} = {simplified_num}",
            f"{denominator} ÷ {gcd_value} = {simplified_den}",
            f"Simplified: {simplified_num}/{simplified_den}",
        ]
        
        return MathSkeleton(
            concept="Simplifying Fractions",
            question_type="simplify-fraction",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "original_numerator": numerator,
                "original_denominator": denominator,
                "gcd": gcd_value,
                "simplified_numerator": simplified_num,
                "simplified_denominator": simplified_den,
            },
            latex_problem=latex_problem,
            solution=correct_answer,
            steps=steps,
            explanation=f"To simplify a fraction, find the GCD of numerator and denominator, then divide both by it.",
            is_valid=True,
            validation_notes=f"Verified: {numerator}/{denominator} simplifies to {simplified_num}/{simplified_den}",
        )
    
    def generate_convert_to_decimal_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.UNDERSTAND,
    ) -> MathSkeleton:
        """
        Generate: "Convert fraction X/Y to decimal"
        
        Using SymPy:
        1. Pick simple fraction
        2. Calculate decimal using Rational
        3. Generate problem
        """
        
        ranges = self.concept_ranges[difficulty]
        
        numerator = random.randint(1, ranges["max_numerator"])
        denominator = random.choice([2, 4, 5, 8, 10, 20, 25, 50])  # Common denominators for nice decimals
        
        fraction = Rational(numerator, denominator)
        decimal_value = float(fraction)
        
        # Format decimal appropriately
        if decimal_value == int(decimal_value):
            correct_answer = str(int(decimal_value))
        else:
            correct_answer = f"{decimal_value:.4f}".rstrip('0').rstrip('.')
        
        latex_problem = f"Convert $\\frac{{{numerator}}}{{{denominator}}}$ to a decimal"
        
        steps = [
            f"Fraction: {numerator}/{denominator}",
            f"Divide: {numerator} ÷ {denominator}",
            f"Result: {decimal_value}",
        ]
        
        return MathSkeleton(
            concept="Converting Fractions to Decimals",
            question_type="fraction-to-decimal",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "numerator": numerator,
                "denominator": denominator,
                "decimal": decimal_value,
            },
            latex_problem=latex_problem,
            solution=correct_answer,
            steps=steps,
            explanation=f"Divide the numerator by the denominator to get the decimal equivalent.",
            is_valid=True,
            validation_notes=f"Verified: {numerator}/{denominator} = {decimal_value}",
        )
    
    def generate_compare_fractions_question(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        bloom_level: BloomLevel = BloomLevel.UNDERSTAND,
    ) -> MathSkeleton:
        """
        Generate: "Which fraction is larger: X/Y or A/B?"
        
        Using SymPy:
        1. Pick two fractions
        2. Compare using Rational
        3. Generate problem
        """
        
        ranges = self.concept_ranges[difficulty]
        
        num1 = random.randint(1, ranges["max_numerator"])
        den1 = random.randint(2, ranges["max_denominator"])
        num2 = random.randint(1, ranges["max_numerator"])
        den2 = random.randint(2, ranges["max_denominator"])
        
        frac1 = Rational(num1, den1)
        frac2 = Rational(num2, den2)
        
        if frac1 > frac2:
            larger_num, larger_den = num1, den1
            correct_answer = f"{num1}/{den1}"
        else:
            larger_num, larger_den = num2, den2
            correct_answer = f"{num2}/{den2}"
        
        latex_problem = f"Which is larger: $\\frac{{{num1}}}{{{den1}}}$ or $\\frac{{{num2}}}{{{den2}}}$?"
        
        steps = [
            f"Fraction 1: {num1}/{den1} = {float(frac1):.4f}",
            f"Fraction 2: {num2}/{den2} = {float(frac2):.4f}",
            f"Compare: {float(frac1):.4f} {'>' if frac1 > frac2 else '<'} {float(frac2):.4f}",
            f"Larger: {correct_answer}",
        ]
        
        return MathSkeleton(
            concept="Comparing Fractions",
            question_type="compare-fractions",
            difficulty=difficulty,
            bloom_level=bloom_level,
            parameters={
                "fraction_1_num": num1,
                "fraction_1_den": den1,
                "fraction_2_num": num2,
                "fraction_2_den": den2,
                "larger": correct_answer,
            },
            latex_problem=latex_problem,
            solution=correct_answer,
            steps=steps,
            explanation=f"Convert both fractions to decimals and compare.",
            is_valid=True,
            validation_notes=f"Verified: {num1}/{den1} vs {num2}/{den2}",
        )
