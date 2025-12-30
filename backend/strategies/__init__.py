"""Strategy implementations for K.C. Nag question generation.

Uses integrated hybrid neuro-symbolic approach for all chapters.
"""

from .base import BaseChapterStrategy
from .factors_multiples_integrated import FactorsMultiplesIntegrated
from .large_numbers_integrated import LargeNumbersIntegrated
from .clock_angles_integrated import ClockAnglesIntegrated
from .symmetry_integrated import SymmetryIntegrated
from .rotation_integrated import RotationIntegrated
from .fraction_area_integrated import FractionAreaIntegrated
from .fractions_decimals_integrated import FractionsDecimalsIntegrated
from .dice_logic_integrated import DiceLogicIntegrated
from .nets_integrated import NetsIntegrated
from .cube_counting_integrated import CubeCountingIntegrated
from .geometry_measurement_integrated import GeometryMeasurementIntegrated
from .data_patterns_integrated import DataPatternsIntegrated
from .mapping_integrated import MappingIntegrated
from .data_handling_integrated import DataHandlingIntegrated
from .measurement_integrated import MeasurementIntegrated
from .multiplication_division_integrated import MultiplicationDivisionIntegrated

__all__ = [
    "BaseChapterStrategy",
    "FactorsMultiplesIntegrated",
    "LargeNumbersIntegrated",
    "ClockAnglesIntegrated",
    "SymmetryIntegrated",
    "RotationIntegrated",
    "FractionAreaIntegrated",
    "FractionsDecimalsIntegrated",
    "DiceLogicIntegrated",
    "NetsIntegrated",
    "CubeCountingIntegrated",
    "GeometryMeasurementIntegrated",
    "DataPatternsIntegrated",
    "MappingIntegrated",
    "DataHandlingIntegrated",
    "MeasurementIntegrated",
    "MultiplicationDivisionIntegrated",
]

