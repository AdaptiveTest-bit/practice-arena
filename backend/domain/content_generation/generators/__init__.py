"""Question Generation Strategies

This package contains all 14 chapter-specific question generation strategies.
Each strategy extends BaseChapterStrategy and implements the 5-phase pipeline:
1. Generate deterministic skeleton (SymPy/Python logic)
2. Generate K.C. Nag story context (pedagogical narrative)
3. Generate misconception-based options (adaptive distractors)
4. Render rich question (Jinja2 HTML)
5. Return trackable Question object (enables analytics)

Available Strategies:
- factors_multiples: Factors, multiples, LCM, HCF
- fractions_decimals: Fractions, decimals, conversions
- large_numbers: Place value, rounding, operations
- data_patterns: Data handling and patterns
- clock_angles: Clock angle calculations
- symmetry: Line and rotational symmetry
- rotation: Geometric rotations
- nets: 3D nets and folding
- dice_logic: Dice probability and logic
- cube_counting: Cube counting puzzles
- data_handling: Data interpretation
- measurement: Length, area, volume
- multiplication_division: Multi-digit operations
- geometry_measurement: Combined geometry/measurement
"""

from .base import BaseChapterStrategy

__all__ = ["BaseChapterStrategy"]
