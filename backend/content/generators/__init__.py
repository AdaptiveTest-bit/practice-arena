"""
Question Generators using Hybrid Neuro-Symbolic Architecture

Each module implements deterministic question generation for a specific chapter
using reverse-engineering (pick answer first, build problem).

Current implementations:
- factors_multiples.py: Chapter 5 - Factors, Multiples, GCD, LCM, Prime/Composite

Future implementations:
- Chapter 1: Large Numbers
- Chapter 2: Addition & Subtraction
- Chapter 3-4: Multiplication & Division
- Chapter 6-7: Fractions & Decimals
- ... and more
"""

from .factors_multiples import FactorsMultiplesGenerator

__all__ = ["FactorsMultiplesGenerator"]
