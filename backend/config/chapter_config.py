"""Chapter configuration for CBSE Class 5 Mathematics MVP.

This defines the curriculum structure, concepts, and Bloom level distribution
for each chapter.
"""

from typing import Dict, List, Any
from enum import Enum


class ChapterEnum(Enum):
    """All available chapters."""
    CH1_LARGE_NUMBERS = 1
    CH2_CLOCK_ANGLES = 2
    CH3_SYMMETRY = 3
    CH4_ROTATION = 4
    CH5_FRACTION_AREA = 5
    CH6_FRACTIONS_DECIMALS = 6
    CH7_DICE_LOGIC = 7
    CH8_NETS = 8
    CH9_FACTORS_MULTIPLES = 9
    CH10_DATA_PATTERNS = 10
    CH11_MAPPING = 11
    CH12_CUBE_COUNTING = 12
    CH13_GEOMETRY_MEASUREMENT = 13
    CH14_DATA_HANDLING = 14
    CH15_MULTIPLICATION_DIVISION = 15
    CH16_MEASUREMENT = 16


# ============================================================================
# CHAPTER CONFIGURATION
# ============================================================================

CHAPTER_CONFIG = {
    # =========================================================================
    # CHAPTER 1: The Fish Tale - Large Numbers
    # =========================================================================
    1: {
        "id": 1,
        "name": "The Fish Tale - Large Numbers",
        "description": "Place value, rounding, comparing large numbers",
        "icon": "🔢",
        "order": 1,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "large_numbers",
        "concepts": ["place_value", "rounding", "comparing", "operations", "estimation"],
        "critical_concepts": ["place_value", "rounding"],
        "misconceptions": ["place_value_confusion", "rounding_direction_error", "zero_placement_error"],
        "bloom_distribution": {"remember": 30, "understand": 25, "apply": 20, "analyze": 15, "evaluate": 10},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.3, "apply": 1.6, "analyze": 2.0, "evaluate": 2.5},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 4, "evaluate": 3},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 45}
    },
    
    # =========================================================================
    # CHAPTER 2: Shapes & Angles (Part 1)
    # =========================================================================
    2: {
        "id": 2,
        "name": "Shapes & Angles - Clock Angles",
        "description": "Clock angles, angle measurement, time calculation",
        "icon": "⏰",
        "order": 2,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "clock_angles",
        "concepts": ["angles", "clock_angles", "time_measurement", "angle_calculation"],
        "critical_concepts": ["clock_angles", "angle_measurement"],
        "misconceptions": ["angle_measurement_error", "clock_position_confusion", "minute_hour_error"],
        "bloom_distribution": {"remember": 25, "understand": 30, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.3, "apply": 1.5, "analyze": 1.9, "evaluate": 2.3},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 4, "evaluate": 3},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 40}
    },
    
    3: {
        "id": 3,
        "name": "Shapes & Angles - Symmetry",
        "description": "Lines of symmetry, reflections, symmetric patterns",
        "icon": "🪞",
        "order": 3,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "symmetry",
        "concepts": ["symmetry", "line_of_symmetry", "reflection", "pattern_symmetry"],
        "critical_concepts": ["symmetry", "line_of_symmetry"],
        "misconceptions": ["symmetry_axis_confusion", "multiple_symmetry_error", "reflection_direction_error"],
        "bloom_distribution": {"remember": 25, "understand": 30, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.3, "apply": 1.5, "analyze": 1.9, "evaluate": 2.3},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 4, "evaluate": 3},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 40}
    },
    
    4: {
        "id": 4,
        "name": "Shapes & Angles - Rotation",
        "description": "Rotations, geometric transformations, 2D-3D relationships",
        "icon": "🔄",
        "order": 4,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "rotation",
        "concepts": ["rotation", "rotation_angle", "transformation", "spatial_reasoning"],
        "critical_concepts": ["rotation", "rotation_angle"],
        "misconceptions": ["rotation_direction_error", "angle_measurement_error", "perspective_error"],
        "bloom_distribution": {"remember": 25, "understand": 30, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.3, "apply": 1.5, "analyze": 1.9, "evaluate": 2.3},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 4, "evaluate": 3},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 40}
    },
    
    # =========================================================================
    # CHAPTER 3: How Many Squares - Fraction Area
    # =========================================================================
    5: {
        "id": 5,
        "name": "How Many Squares - Fractions in Area",
        "description": "Fractions using area models, part-to-whole relationships",
        "icon": "📐",
        "order": 5,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "fraction_area",
        "concepts": ["fractions", "area_fractions", "part_whole", "equivalent_fractions"],
        "critical_concepts": ["fractions", "area_fractions"],
        "misconceptions": ["denominator_confusion", "unequal_parts_error", "fraction_value_error"],
        "bloom_distribution": {"remember": 25, "understand": 30, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.1, "understand": 1.4, "apply": 1.8, "analyze": 2.1, "evaluate": 2.5},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 3, "evaluate": 2},
        "advancement_threshold": 0.75,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.70, "concepts_mastery_target": 0.75, "time_estimate_minutes": 45}
    },
    
    # =========================================================================
    # CHAPTER 4: Parts & Wholes - Fractions & Decimals
    # =========================================================================
    6: {
        "id": 6,
        "name": "Parts & Wholes - Fractions & Decimals",
        "description": "Fractions, decimals, conversions, operations",
        "icon": "🍰",
        "order": 6,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "fractions_decimals",
        "concepts": ["fractions", "decimals", "fraction_operations", "decimal_operations", "fraction_decimal_conversion", "comparison"],
        "critical_concepts": ["fractions", "decimals", "fraction_decimal_conversion"],
        "misconceptions": ["denominator_error", "decimal_place_error", "conversion_error", "operation_error"],
        "bloom_distribution": {"remember": 25, "understand": 30, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.1, "understand": 1.4, "apply": 1.8, "analyze": 2.1, "evaluate": 2.5},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 3, "evaluate": 2},
        "advancement_threshold": 0.75,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.70, "concepts_mastery_target": 0.75, "time_estimate_minutes": 50}
    },
    
    # =========================================================================
    # CHAPTER 5: Does it Look the Same (Part 1) - 3D Visualization
    # =========================================================================
    7: {
        "id": 7,
        "name": "Does it Look the Same - Dice Logic",
        "description": "3D visualization, dice logic, spatial reasoning",
        "icon": "🎲",
        "order": 7,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "dice_logic",
        "concepts": ["dice_logic", "3d_visualization", "spatial_reasoning", "opposite_faces"],
        "critical_concepts": ["dice_logic", "opposite_faces"],
        "misconceptions": ["dice_opposite_error", "spatial_visualization_error", "face_counting_error"],
        "bloom_distribution": {"remember": 20, "understand": 30, "apply": 25, "analyze": 15, "evaluate": 10},
        "bloom_difficulty": {"remember": 1.2, "understand": 1.5, "apply": 1.8, "analyze": 2.1, "evaluate": 2.5},
        "bloom_requirements": {"remember": 4, "understand": 5, "apply": 5, "analyze": 4, "evaluate": 3},
        "advancement_threshold": 0.75,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.70, "concepts_mastery_target": 0.75, "time_estimate_minutes": 45}
    },
    
    8: {
        "id": 8,
        "name": "Does it Look the Same - Nets & Solids",
        "description": "Nets of 3D shapes, folding patterns, solid recognition",
        "icon": "📦",
        "order": 8,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "nets",
        "concepts": ["nets", "3d_shapes", "net_folding", "solid_recognition"],
        "critical_concepts": ["nets", "net_folding"],
        "misconceptions": ["net_folding_error", "shape_misidentification", "edge_counting_error"],
        "bloom_distribution": {"remember": 20, "understand": 30, "apply": 25, "analyze": 15, "evaluate": 10},
        "bloom_difficulty": {"remember": 1.2, "understand": 1.5, "apply": 1.8, "analyze": 2.1, "evaluate": 2.5},
        "bloom_requirements": {"remember": 4, "understand": 5, "apply": 5, "analyze": 4, "evaluate": 3},
        "advancement_threshold": 0.75,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.70, "concepts_mastery_target": 0.75, "time_estimate_minutes": 50}
    },
    
    # =========================================================================
    # CHAPTER 6: Be My Multiple - Factors & Multiples
    # =========================================================================
    9: {
        "id": 9,
        "name": "Be My Multiple - Factors & Multiples",
        "description": "HCF, LCM, divisibility, prime numbers",
        "icon": "🔢",
        "order": 9,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "factors_multiples",
        "concepts": ["factors", "multiples", "hcf", "lcm", "prime_numbers", "divisibility"],
        "critical_concepts": ["factors", "multiples", "hcf", "lcm"],
        "misconceptions": ["factor_multiple_confusion", "hcf_lcm_reversal", "prime_number_definition_error", "divisibility_error"],
        "bloom_distribution": {"remember": 30, "understand": 25, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.4, "apply": 1.7, "analyze": 2.0, "evaluate": 2.4},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 3, "evaluate": 2},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 45}
    },
    
    # =========================================================================
    # CHAPTER 7: Can You See Pattern - Data Patterns
    # =========================================================================
    10: {
        "id": 10,
        "name": "Can You See Pattern - Data Patterns",
        "description": "Sequences, patterns, missing data, prediction",
        "icon": "🔍",
        "order": 10,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "data_patterns",
        "concepts": ["patterns", "sequences", "missing_data", "pattern_rules", "prediction"],
        "critical_concepts": ["patterns", "sequences"],
        "misconceptions": ["pattern_identification_error", "sequence_rule_error", "missing_value_error", "prediction_error"],
        "bloom_distribution": {"remember": 20, "understand": 25, "apply": 30, "analyze": 15, "evaluate": 10},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.3, "apply": 1.7, "analyze": 2.0, "evaluate": 2.3},
        "bloom_requirements": {"remember": 4, "understand": 5, "apply": 5, "analyze": 4, "evaluate": 3},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 45}
    },
    
    # =========================================================================
    # CHAPTER 8: Mapping Your Way - Mapping
    # =========================================================================
    11: {
        "id": 11,
        "name": "Mapping Your Way - Mapping",
        "description": "Coordinates, scales, map reading, proportional reasoning",
        "icon": "🗺️",
        "order": 11,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "mapping",
        "concepts": ["coordinates", "scales", "map_reading", "proportional_reasoning", "distance_calculation"],
        "critical_concepts": ["coordinates", "scales"],
        "misconceptions": ["scale_misreading", "coordinate_order_error", "distance_calculation_error"],
        "bloom_distribution": {"remember": 25, "understand": 30, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.3, "apply": 1.6, "analyze": 1.9, "evaluate": 2.2},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 4, "analyze": 3, "evaluate": 3},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 45}
    },
    
    # =========================================================================
    # CHAPTER 9: Boxes & Sketches - Cube Counting & Geometry
    # =========================================================================
    12: {
        "id": 12,
        "name": "Boxes & Sketches - Cube Counting",
        "description": "Cube counting, 3D visualization, spatial patterns",
        "icon": "🧩",
        "order": 12,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "cube_counting",
        "concepts": ["cube_counting", "3d_patterns", "spatial_reasoning", "volume_estimation"],
        "critical_concepts": ["cube_counting", "spatial_reasoning"],
        "misconceptions": ["cube_counting_error", "hidden_cube_error", "perspective_error"],
        "bloom_distribution": {"remember": 20, "understand": 30, "apply": 25, "analyze": 15, "evaluate": 10},
        "bloom_difficulty": {"remember": 1.2, "understand": 1.5, "apply": 1.8, "analyze": 2.1, "evaluate": 2.5},
        "bloom_requirements": {"remember": 4, "understand": 5, "apply": 5, "analyze": 4, "evaluate": 3},
        "advancement_threshold": 0.75,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.70, "concepts_mastery_target": 0.75, "time_estimate_minutes": 50}
    },
    
    13: {
        "id": 13,
        "name": "Area & Measurement - Geometry & Measurement",
        "description": "Area, perimeter, volume, measurement concepts",
        "icon": "📏",
        "order": 13,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "geometry_measurement",
        "concepts": ["area", "perimeter", "volume", "measurement_units", "conversion"],
        "critical_concepts": ["area", "perimeter", "volume"],
        "misconceptions": ["area_perimeter_confusion", "unit_conversion_error", "measurement_error", "volume_calculation_error"],
        "bloom_distribution": {"remember": 20, "understand": 30, "apply": 30, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.4, "apply": 1.8, "analyze": 2.1, "evaluate": 2.4},
        "bloom_requirements": {"remember": 4, "understand": 5, "apply": 5, "analyze": 3, "evaluate": 2},
        "advancement_threshold": 0.75,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.70, "concepts_mastery_target": 0.75, "time_estimate_minutes": 55}
    },
    
    # =========================================================================
    # CHAPTER 10: Smart Charts - Data Handling
    # =========================================================================
    14: {
        "id": 14,
        "name": "Smart Charts - Data Handling",
        "description": "Tables, graphs, pictographs, data interpretation",
        "icon": "📊",
        "order": 14,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "data_handling",
        "concepts": ["tables", "bar_graphs", "pictographs", "data_interpretation", "scales"],
        "critical_concepts": ["tables", "bar_graphs", "scales"],
        "misconceptions": ["scale_misreading", "data_interpretation_error", "graph_reading_error", "symbol_value_error"],
        "bloom_distribution": {"remember": 25, "understand": 30, "apply": 20, "analyze": 15, "evaluate": 10},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.3, "apply": 1.6, "analyze": 1.9, "evaluate": 2.2},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 4, "analyze": 3, "evaluate": 3},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 40}
    },
    
    # =========================================================================
    # CHAPTER 11: Ways to Multiply/Divide - Multiplication & Division
    # =========================================================================
    15: {
        "id": 15,
        "name": "Ways to Multiply/Divide - Multiplication & Division",
        "description": "Multiplication strategies, division, properties of operations",
        "icon": "✖️",
        "order": 15,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "multiplication_division",
        "concepts": ["multiplication", "division", "multiplication_strategies", "division_strategies", "properties", "factors"],
        "critical_concepts": ["multiplication", "division"],
        "misconceptions": ["multiplication_order_error", "division_remainder_error", "operation_property_error"],
        "bloom_distribution": {"remember": 30, "understand": 25, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.4, "apply": 1.7, "analyze": 2.0, "evaluate": 2.4},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 3, "evaluate": 2},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 45}
    },
    
    # =========================================================================
    # CHAPTER 12: How Big/Heavy - Measurement
    # =========================================================================
    16: {
        "id": 16,
        "name": "How Big/Heavy - Measurement",
        "description": "Measurement units, conversions, weight, capacity",
        "icon": "⚖️",
        "order": 16,
        "subject": "Mathematics",
        "class_level": 5,
        "strategy": "measurement",
        "concepts": ["measurement_units", "weight", "capacity", "length", "conversion", "estimation"],
        "critical_concepts": ["measurement_units", "conversion"],
        "misconceptions": ["unit_conversion_error", "measurement_error", "estimation_error"],
        "bloom_distribution": {"remember": 30, "understand": 25, "apply": 25, "analyze": 12, "evaluate": 8},
        "bloom_difficulty": {"remember": 1.0, "understand": 1.3, "apply": 1.6, "analyze": 1.9, "evaluate": 2.3},
        "bloom_requirements": {"remember": 5, "understand": 5, "apply": 5, "analyze": 3, "evaluate": 2},
        "advancement_threshold": 0.80,
        "min_questions_per_concept": 3,
        "target_metrics": {"completion_percentage": 100.0, "accuracy_target": 0.75, "concepts_mastery_target": 0.80, "time_estimate_minutes": 45}
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_chapter_config(chapter_id: int) -> Dict[str, Any]:
    """Get configuration for a specific chapter.
    
    Args:
        chapter_id: The chapter ID
    
    Returns:
        Dictionary with chapter configuration, or None if not found
    """
    return CHAPTER_CONFIG.get(chapter_id)


def get_all_chapters() -> Dict[int, Dict[str, Any]]:
    """Get all chapter configurations.
    
    Returns:
        Dictionary of all chapters indexed by ID
    """
    return CHAPTER_CONFIG


def get_chapter_concepts(chapter_id: int) -> List[str]:
    """Get all concepts for a chapter.
    
    Args:
        chapter_id: The chapter ID
    
    Returns:
        List of concept names
    """
    config = get_chapter_config(chapter_id)
    if not config:
        return []
    return config.get("concepts", [])


def get_chapter_critical_concepts(chapter_id: int) -> List[str]:
    """Get critical concepts for a chapter.
    
    Args:
        chapter_id: The chapter ID
    
    Returns:
        List of critical concept names
    """
    config = get_chapter_config(chapter_id)
    if not config:
        return []
    return config.get("critical_concepts", [])


def get_bloom_distribution(chapter_id: int) -> Dict[str, int]:
    """Get Bloom level distribution for a chapter.
    
    Args:
        chapter_id: The chapter ID
    
    Returns:
        Dictionary with Bloom level percentages
    """
    config = get_chapter_config(chapter_id)
    if not config:
        return {}
    return config.get("bloom_distribution", {})


def get_bloom_difficulty(chapter_id: int) -> Dict[str, float]:
    """Get difficulty multipliers for each Bloom level.
    
    Args:
        chapter_id: The chapter ID
    
    Returns:
        Dictionary with difficulty multipliers
    """
    config = get_chapter_config(chapter_id)
    if not config:
        return {}
    return config.get("bloom_difficulty", {})


def get_advancement_threshold(chapter_id: int) -> float:
    """Get advancement threshold for a chapter.
    
    Args:
        chapter_id: The chapter ID
    
    Returns:
        Accuracy threshold (0.0-1.0)
    """
    config = get_chapter_config(chapter_id)
    if not config:
        return 0.80
    return config.get("advancement_threshold", 0.80)


def get_chapter_misconceptions(chapter_id: int) -> List[str]:
    """Get common misconceptions for a chapter.
    
    Args:
        chapter_id: The chapter ID
    
    Returns:
        List of misconception names
    """
    config = get_chapter_config(chapter_id)
    if not config:
        return []
    return config.get("misconceptions", [])


def validate_concept(chapter_id: int, concept: str) -> bool:
    """Check if a concept belongs to a chapter.
    
    Args:
        chapter_id: The chapter ID
        concept: The concept name
    
    Returns:
        True if concept is valid for chapter, False otherwise
    """
    concepts = get_chapter_concepts(chapter_id)
    return concept in concepts


def validate_bloom_level(bloom_level: str) -> bool:
    """Check if a Bloom level is valid.
    
    Args:
        bloom_level: The Bloom level name
    
    Returns:
        True if valid, False otherwise
    """
    valid_levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
    return bloom_level.lower() in valid_levels
