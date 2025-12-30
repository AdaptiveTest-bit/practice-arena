"""
MAPPING - INTEGRATED STRATEGY
=============================

Hybrid Neuro-Symbolic approach for Mapping

Integrates:
1. Proportional reasoning with coordinates
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Scale confusion, Coordinate order error)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class MappingIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic proportional logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.MAPPING
    chapter_name = "Mapping"
    description = "Mapping with hybrid neuro-symbolic approach"
    
    def __init__(self):
        super().__init__()
        # Initialize hybrid system components here
        # self.sympy_generator = ...
        # self.story_generator = ...
        # self.renderer = ...
    
    def generate(self) -> Question:
        """
        Main generation pipeline:
        1. Select problem type
        2. Generate skeleton (PHASE 1)
        3. Generate K.C. Nag story (PHASE 2)
        4. Generate misconception options (PHASE 3)
        5. Render rich question (PHASE 4)
        6. Create trackable Question (PHASE 5)
        """
        problem_type = random.choice([
            "scale_calculation",
            "distance_finding",
            "coordinate_reading",
        ])
        
        if problem_type == "scale_calculation":
            return self._generate_scale_calculation()
        elif problem_type == "distance_finding":
            return self._generate_distance_finding()
        else:  # coordinate_reading
            return self._generate_coordinate_reading()
    
    def _generate_scale_calculation(self) -> Question:
        """
        Scale Calculation - Understanding map scales and proportional distances
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Map scale scenarios
        scale_scenarios = [
            {
                "map_name": "City Map",
                "scale": "1 cm = 2 km",
                "scale_ratio": 1,  # cm on map
                "scale_distance": 2,  # km in reality
                "map_distance": 3.5,  # cm on map
                "real_distance": 7,  # km in reality
                "context": "distance between two parks"
            },
            {
                "map_name": "Country Map",
                "scale": "1 cm = 50 km",
                "scale_ratio": 1,
                "scale_distance": 50,
                "map_distance": 2.4,  # cm on map
                "real_distance": 120,  # km in reality
                "context": "distance between two cities"
            },
            {
                "map_name": "Local Area Map",
                "scale": "1 cm = 500 m",
                "scale_ratio": 1,
                "scale_distance": 0.5,  # km
                "map_distance": 4,  # cm on map
                "real_distance": 2,  # km in reality
                "context": "distance to school"
            },
            {
                "map_name": "Regional Map",
                "scale": "2 cm = 10 km",
                "scale_ratio": 2,
                "scale_distance": 10,
                "map_distance": 5,  # cm on map
                "real_distance": 25,  # km in reality
                "context": "distance between towns"
            }
        ]
        
        scale_data = random.choice(scale_scenarios)
        correct_answer = str(scale_data["real_distance"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"On a {scale_data['map_name']}, the scale is {scale_data['scale']}. Two places are {scale_data['map_distance']} cm apart on the map. What is the actual {scale_data['context']} in km?",
            f"A map shows {scale_data['context']} as {scale_data['map_distance']} cm apart. If the scale is {scale_data['scale']}, what's the real distance?",
            f"Using a {scale_data['map_name']} with scale {scale_data['scale']}, {scale_data['map_distance']} cm on the map equals how many km in reality?"
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "confused the scale ratio direction",
            "forgot to multiply by the scale factor",
            "mixed up map distance with real distance"
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Wrong scale interpretation (inverted ratio)
        wrong_value_1 = scale_data["map_distance"] / scale_data["scale_distance"]
        wrong_options.append((
            str(wrong_value_1),
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Inverted scale calculation",
            f"You calculated {wrong_value_1} km, but you divided instead of multiplied! When scale is {scale_data['scale']}, multiply: {scale_data['map_distance']} × {scale_data['scale_distance']} = {scale_data['real_distance']} km.",
            f"Scale formula: Real Distance = Map Distance × Scale Factor"
        ))
        
        # Misconception 2: Used map distance directly
        wrong_options.append((
            str(scale_data["map_distance"]),
            MisconceptionType.LOGICAL_DISCONNECT,
            f"Ignored the scale, used map distance",
            f"You said {scale_data['map_distance']} km, but that's the map distance, not the real distance! Apply the scale: {scale_data['map_distance']} cm × {scale_data['scale_distance']} = {scale_data['real_distance']} km.",
            f"Always apply the scale to convert map distance to real distance"
        ))
        
        # Misconception 3: Partial calculation
        partial_value = scale_data["map_distance"] * random.choice([0.5, 1.5, 2])
        wrong_options.append((
            str(partial_value),
            MisconceptionType.INCOMPLETE_REASONING,
            f"Incomplete scale calculation",
            f"You got {partial_value} km, but the correct calculation is: {scale_data['map_distance']} cm × {scale_data['scale_distance']} = {scale_data['real_distance']} km.",
            f"Check each multiplication step carefully"
        ))
        
        random.shuffle(wrong_options)
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Map Scale: {scale_data['scale']}",
            f"Distance on map: {scale_data['map_distance']} cm",
            f"Scale factor: 1 cm = {scale_data['scale_distance']} km",
            f"Calculation: {scale_data['map_distance']} cm × {scale_data['scale_distance']} km/cm = {scale_data['real_distance']} km",
            f"Answer: {scale_data['real_distance']} km"
        ]
        
        visual_diagram = self._render_scale_diagram(scale_data)
        
        hints = [
            f"Hint 1: The scale is {scale_data['scale']}",
            f"Hint 2: Map distance is {scale_data['map_distance']} cm",
            f"Hint 3: Multiply map distance by the scale factor",
            f"Hint 4: {scale_data['map_distance']} × {scale_data['scale_distance']} = {scale_data['real_distance']} km"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Map Scales and Proportional Reasoning",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Scale up, don't down!",
            data_representation=f"Scale: {scale_data['scale']} | Map: {scale_data['map_distance']}cm → Real: {scale_data['real_distance']}km",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s map calculation: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_distance_finding(self) -> Question:
        """
        Distance Finding - Using coordinates to find distances between points
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Grid-based distance scenarios
        distance_scenarios = [
            {
                "point_a": (2, 3),
                "point_b": (5, 7),
                "horizontal": 3,
                "vertical": 4,
                "manhattan": 7,
                "euclidean": 5,
                "context": "two locations on a city grid"
            },
            {
                "point_a": (1, 2),
                "point_b": (4, 6),
                "horizontal": 3,
                "vertical": 4,
                "manhattan": 7,
                "euclidean": 5,
                "context": "points on a treasure map"
            },
            {
                "point_a": (0, 0),
                "point_b": (6, 8),
                "horizontal": 6,
                "vertical": 8,
                "manhattan": 14,
                "euclidean": 10,
                "context": "starting point and destination"
            },
            {
                "point_a": (3, 1),
                "point_b": (7, 9),
                "horizontal": 4,
                "vertical": 8,
                "manhattan": 12,
                "euclidean": int((16 + 64) ** 0.5),  # sqrt(80) ≈ 8.94
                "context": "two buildings in a city"
            }
        ]
        
        distance_data = random.choice(distance_scenarios)
        # Using Manhattan (grid) distance for simplicity
        correct_answer = str(distance_data["manhattan"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"On a grid map, point A is at {distance_data['point_a']} and point B is at {distance_data['point_b']}. If you can only move horizontally or vertically, how many units is the {distance_data['context']}?",
            f"Walking on city blocks from {distance_data['point_a']} to {distance_data['point_b']}, how many blocks do you travel ({distance_data['context']})?",
            f"A robot moves from coordinates {distance_data['point_a']} to {distance_data['point_b']} on a grid. Moving only right/left and up/down, how far does it go?"
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "calculated only horizontal distance",
            "confused diagonal distance with grid distance",
            "forgot to add both horizontal and vertical movements"
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Only horizontal distance
        wrong_options.append((
            str(distance_data["horizontal"]),
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Used only horizontal distance",
            f"You said {distance_data['horizontal']} units, but that's only the horizontal movement! You must also count vertical: {distance_data['horizontal']} + {distance_data['vertical']} = {distance_data['manhattan']} units.",
            f"Grid distance = |x₂ - x₁| + |y₂ - y₁| (both directions matter)"
        ))
        
        # Misconception 2: Only vertical distance
        wrong_options.append((
            str(distance_data["vertical"]),
            MisconceptionType.LOGICAL_DISCONNECT,
            f"Used only vertical distance",
            f"You said {distance_data['vertical']} units, but that's only vertical! Include horizontal too: {distance_data['horizontal']} + {distance_data['vertical']} = {distance_data['manhattan']} units.",
            f"Always count movements in both horizontal and vertical directions"
        ))
        
        # Misconception 3: Straight-line (Euclidean) distance
        wrong_options.append((
            str(distance_data["euclidean"]),
            MisconceptionType.INCOMPLETE_REASONING,
            f"Used straight-line distance",
            f"You calculated {distance_data['euclidean']} using diagonal, but on a grid, you can only move right/left/up/down. That's {distance_data['manhattan']} units.",
            f"On a grid, use Manhattan distance (not diagonal straight line)"
        ))
        
        random.shuffle(wrong_options)
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Point A: {distance_data['point_a']}",
            f"Point B: {distance_data['point_b']}",
            f"Horizontal distance: |{distance_data['point_b'][0]} - {distance_data['point_a'][0]}| = {distance_data['horizontal']} units",
            f"Vertical distance: |{distance_data['point_b'][1]} - {distance_data['point_a'][1]}| = {distance_data['vertical']} units",
            f"Total grid distance: {distance_data['horizontal']} + {distance_data['vertical']} = {distance_data['manhattan']} units"
        ]
        
        visual_diagram = self._render_distance_diagram(distance_data)
        
        hints = [
            f"Hint 1: Points are at {distance_data['point_a']} and {distance_data['point_b']}",
            f"Hint 2: Horizontal distance: {distance_data['horizontal']} units",
            f"Hint 3: Vertical distance: {distance_data['vertical']} units",
            f"Hint 4: Total: {distance_data['horizontal']} + {distance_data['vertical']} = {distance_data['manhattan']} units"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Grid Distance and Coordinates",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Grid distance needs both directions!",
            data_representation=f"From {distance_data['point_a']} to {distance_data['point_b']} | Horizontal: {distance_data['horizontal']} + Vertical: {distance_data['vertical']} = {distance_data['manhattan']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s grid distance challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_coordinate_reading(self) -> Question:
        """
        Coordinate Reading - Identifying locations on maps using coordinates
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Coordinate scenarios with location names
        coordinate_scenarios = [
            {
                "location": "Park",
                "coordinates": (4, 6),
                "x": 4,
                "y": 6,
                "wrong_x": 6,  # swapped
                "wrong_y": 4,
                "context": "a park in the city"
            },
            {
                "location": "School",
                "coordinates": (2, 5),
                "x": 2,
                "y": 5,
                "wrong_x": 5,
                "wrong_y": 2,
                "context": "a school building"
            },
            {
                "location": "Library",
                "coordinates": (7, 3),
                "x": 7,
                "y": 3,
                "wrong_x": 3,
                "wrong_y": 7,
                "context": "a library"
            },
            {
                "location": "Museum",
                "coordinates": (5, 8),
                "x": 5,
                "y": 8,
                "wrong_x": 8,
                "wrong_y": 5,
                "context": "a museum"
            },
            {
                "location": "Hospital",
                "coordinates": (3, 4),
                "x": 3,
                "y": 4,
                "wrong_x": 4,
                "wrong_y": 3,
                "context": "a hospital"
            }
        ]
        
        coord_data = random.choice(coordinate_scenarios)
        correct_answer = str(coord_data["coordinates"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"On a coordinate map, the {coord_data['context'].lower()} is located at position ({coord_data['x']}, {coord_data['y']}). What are the coordinates of the {coord_data['location']}?",
            f"A map shows {coord_data['context']} at x = {coord_data['x']} and y = {coord_data['y']}. What are the coordinates?",
            f"If we mark {coord_data['context']} on a grid, with {coord_data['x']} units right and {coord_data['y']} units up from the origin, what's the coordinate pair?"
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "swapped the x and y coordinates",
            "mixed up row and column order",
            "confused which number comes first"
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Swapped coordinates (x, y) → (y, x)
        wrong_options.append((
            f"({coord_data['wrong_x']}, {coord_data['wrong_y']})",
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Swapped x and y coordinates",
            f"You said ({coord_data['wrong_x']}, {coord_data['wrong_y']}), but that's backwards! The correct order is (x, y) = ({coord_data['x']}, {coord_data['y']}).",
            f"Coordinates are always written as (x, y) where x is horizontal, y is vertical"
        ))
        
        # Misconception 2: Partial coordinates
        wrong_options.append((
            f"({coord_data['x']}, {coord_data['y'] - 1})" if coord_data['y'] > 1 else f"({coord_data['x']}, {coord_data['y'] + 1})",
            MisconceptionType.LOGICAL_DISCONNECT,
            f"Off by one in vertical position",
            f"You're close but the y-coordinate is off! The correct coordinates are ({coord_data['x']}, {coord_data['y']}).",
            f"Check both x and y values carefully on the grid"
        ))
        
        # Misconception 3: Completely different coordinates
        wrong_x = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
        wrong_y = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
        while (wrong_x, wrong_y) == (coord_data['x'], coord_data['y']):
            wrong_x = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
            wrong_y = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
        
        wrong_options.append((
            f"({wrong_x}, {wrong_y})",
            MisconceptionType.INCOMPLETE_REASONING,
            f"Wrong location entirely",
            f"You said ({wrong_x}, {wrong_y}), but that's not where {coord_data['context']} is! The correct coordinates are ({coord_data['x']}, {coord_data['y']}).",
            f"Locate the point on the grid and read both coordinates carefully"
        ))
        
        random.shuffle(wrong_options)
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Location: {coord_data['location']} ({coord_data['context']})",
            f"Starting from origin (0, 0)",
            f"Move {coord_data['x']} units right (x-coordinate): {coord_data['x']}",
            f"Move {coord_data['y']} units up (y-coordinate): {coord_data['y']}",
            f"Coordinates: ({coord_data['x']}, {coord_data['y']})"
        ]
        
        visual_diagram = self._render_coordinate_diagram(coord_data)
        
        hints = [
            f"Hint 1: The {coord_data['location']} is {coord_data['context']}",
            f"Hint 2: First value is x (horizontal): {coord_data['x']}",
            f"Hint 3: Second value is y (vertical): {coord_data['y']}",
            f"Hint 4: Write as (x, y) = ({coord_data['x']}, {coord_data['y']})"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Reading Coordinates on Maps",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Order matters: (x, y) always!",
            data_representation=f"{coord_data['location']}: ({coord_data['x']}, {coord_data['y']}) | x={coord_data['x']}, y={coord_data['y']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s coordinate challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question

    # ============================================================================
    # RENDERING HELPERS
    # ============================================================================

    def _render_scale_diagram(self, scale_data: dict) -> dict:
        """
        Render a visual scale comparison diagram
        
        Args:
            scale_data: Dict with scale info and distances
        
        Returns:
            Dict with 'html' key containing visualization
        """
        html_content = f"""
        <div style="margin: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <h3 style="text-align: center;">Map Scale Calculation</h3>
            
            <div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 3px;">
                <strong>Map Scale:</strong> {scale_data['scale']}
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background-color: #e3f2fd;">
                    <th style="border: 1px solid #999; padding: 8px;">Measurement</th>
                    <th style="border: 1px solid #999; padding: 8px;">Value</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #999; padding: 8px;">Distance on Map</td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{scale_data['map_distance']} cm</strong></td>
                </tr>
                <tr style="background-color: #fff3e0;">
                    <td style="border: 1px solid #999; padding: 8px;">Scale Factor</td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{scale_data['scale_distance']} km per cm</strong></td>
                </tr>
                <tr style="background-color: #c8e6c9;">
                    <td style="border: 1px solid #999; padding: 8px;"><strong>Real Distance</strong></td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong style="color: green;">{scale_data['real_distance']} km</strong></td>
                </tr>
            </table>
            
            <div style="background-color: #f9f9f9; padding: 10px; border-left: 4px solid #2196F3;">
                <strong>Calculation:</strong> {scale_data['map_distance']} cm × {scale_data['scale_distance']} km = {scale_data['real_distance']} km
            </div>
        </div>
        """
        
        return {"html": html_content}

    def _render_distance_diagram(self, distance_data: dict) -> dict:
        """
        Render a grid distance diagram showing horizontal and vertical components
        
        Args:
            distance_data: Dict with point coordinates and distances
        
        Returns:
            Dict with 'html' key containing grid visualization
        """
        html_content = f"""
        <div style="margin: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <h3 style="text-align: center;">Grid Distance Calculation</h3>
            
            <div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0;">
                <strong>Point A:</strong> {distance_data['point_a']} <br/>
                <strong>Point B:</strong> {distance_data['point_b']}
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background-color: #e3f2fd;">
                    <th style="border: 1px solid #999; padding: 8px;">Direction</th>
                    <th style="border: 1px solid #999; padding: 8px;">Calculation</th>
                    <th style="border: 1px solid #999; padding: 8px;">Distance</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #999; padding: 8px;">Horizontal (x)</td>
                    <td style="border: 1px solid #999; padding: 8px;">|{distance_data['point_b'][0]} - {distance_data['point_a'][0]}|</td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{distance_data['horizontal']} units</strong></td>
                </tr>
                <tr style="background-color: #f5f5f5;">
                    <td style="border: 1px solid #999; padding: 8px;">Vertical (y)</td>
                    <td style="border: 1px solid #999; padding: 8px;">|{distance_data['point_b'][1]} - {distance_data['point_a'][1]}|</td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{distance_data['vertical']} units</strong></td>
                </tr>
                <tr style="background-color: #c8e6c9;">
                    <td style="border: 1px solid #999; padding: 8px;"><strong>Total Grid Distance</strong></td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{distance_data['horizontal']} + {distance_data['vertical']}</strong></td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong style="color: green;">{distance_data['manhattan']} units</strong></td>
                </tr>
            </table>
            
            <div style="background-color: #fff3e0; padding: 10px; border-left: 4px solid #ff9800;">
                <strong>Key:</strong> On a grid, you can only move horizontally or vertically, so add both components.
            </div>
        </div>
        """
        
        return {"html": html_content}

    def _render_coordinate_diagram(self, coord_data: dict) -> dict:
        """
        Render a coordinate grid diagram
        
        Args:
            coord_data: Dict with location and coordinates
        
        Returns:
            Dict with 'html' key containing grid visualization
        """
        svg_content = f"""
        <svg width="300" height="300" xmlns="http://www.w3.org/2000/svg" style="border: 1px solid #ccc; margin: 15px;">
            <!-- Grid background -->
            <defs>
                <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                    <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#e0e0e0" stroke-width="0.5"/>
                </pattern>
            </defs>
            <rect width="300" height="300" fill="url(#grid)" />
            
            <!-- Axes -->
            <line x1="20" y1="280" x2="280" y2="280" stroke="black" stroke-width="2"/>
            <line x1="20" y1="280" x2="20" y2="20" stroke="black" stroke-width="2"/>
            
            <!-- Axis labels -->
            <text x="270" y="295" font-size="12">x</text>
            <text x="10" y="25" font-size="12">y</text>
            
            <!-- Origin -->
            <circle cx="20" cy="280" r="3" fill="blue"/>
            <text x="5" y="295" font-size="10">(0,0)</text>
            
            <!-- Grid markings -->
            <text x="50" y="295" font-size="10">1</text>
            <text x="15" y="255" font-size="10">1</text>
            
            <!-- Target point -->
            <circle cx="{20 + coord_data['x'] * 30}" cy="{280 - coord_data['y'] * 30}" r="4" fill="red"/>
            
            <!-- Location label -->
            <text x="{20 + coord_data['x'] * 30 - 15}" y="{280 - coord_data['y'] * 30 - 10}" font-size="11" fill="red">
                <tspan>{coord_data['location']}</tspan>
                <tspan x="{20 + coord_data['x'] * 30 - 15}" dy="12">({coord_data['x']}, {coord_data['y']})</tspan>
            </text>
        </svg>
        """
        
        return {"html": svg_content}
    #
    # For each _generate_* method:
    #
    # PHASE 1: Deterministic Skeleton
    # --------------------------------
    # def _generate_xxx(self) -> Question:
    #     # Generate parameters using pure Python/SymPy
    #     # Validate answer is correct (critical!)
    #     # Create MathSkeleton with parameters, solution, steps
    #     skeleton = MathSkeleton(...)
    #
    # PHASE 2: K.C. Nag Story
    # ----------------------
    # story_context = self.story_generator.generate_story_context(skeleton)
    # Or manually create StoryContext with:
    #   - concept_name: what we're learning
    #   - real_world_scenario: something from student's life
    #   - character_names: people in the story
    #   - narrative: the K.C. Nag story text
    #   - misconception_hooks: phrases that reveal traps
    #   - teaching_principles: how K.C. Nag would teach it
    #
    # PHASE 3: Misconception-Based Distractors
    # ----------------------------------------
    # For each of 3 misconceptions:
    #   distractor_info.append(DistractorInfo(
    #       value="...",  # What student sees
    #       misconception_type=MisconceptionType.XXX,
    #       description="...",  # Short label
    #       why_wrong="...",  # Why this is wrong
    #       teaching_point="..."  # What to learn instead
    #   ))
    #
    # PHASE 4: Rich Rendering
    # -----------------------
    # rich_content = self.renderer.render_rich_question(
    #     question_text=...,
    #     story_context=story_context,
    #     solution_steps=steps,
    #     explanation=...,
    #     visual_hint=...,
    #     progressive_hints=[hint1, hint2, hint3, hint4]
    # )
    #
    # PHASE 5: Question Object
    # -----------------------
    # question = Question(
    #     chapter=self.chapter,
    #     topic="...",
    #     logical_trap="K.C. Nag Trap: ...",
    #     data_representation="...",
    #     question_text=...,
    #     solution_steps=steps,
    #     answer=correct_answer,
    #     options=options,
    #     correct_option_index=correct_idx,
    #     distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
    #     trap_info=trap_info,
    #     bloom_info=bloom_info,
    #     rich_html_content=rich_content.get("html"),
    #     rich_narrative=rich_content.get("narrative"),
    #     visual_hints=rich_content.get("hints"),
    # )
    # self._validate_question(question)
    # return question

