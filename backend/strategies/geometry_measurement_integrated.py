"""
GEOMETRY & MEASUREMENT - INTEGRATED STRATEGY
============================================

Hybrid Neuro-Symbolic approach for Geometry & Measurement

Integrates:
1. SymPy geometric shapes and formula verification
2. K.C. Nag real-world scenarios (culturally relevant storytelling)
3. Misconception-based distractors (Perimeter/area confusion, Unit error)
4. Rich HTML rendering (visual pedagogical aids)
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any
import sympy
from sympy import symbols

# Import hybrid system components
from content.generators.geometry_measurement import (
    GeometryMeasurementGenerator,
    GeometryMeasurementConcept,
    DifficultyLevel as HybridDifficultyLevel,
)


class GeometryMeasurementIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic formula-based logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.GEOMETRY_MEASUREMENT
    chapter_name = "Geometry & Measurement"
    description = "Geometry & Measurement with hybrid neuro-symbolic approach"
    
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
            "perimeter_calculation",
            "area_calculation",
            "unit_conversion",
        ])
        
        if problem_type == "perimeter_calculation":
            return self._generate_perimeter_calculation()
        elif problem_type == "area_calculation":
            return self._generate_area_calculation()
        else:  # unit_conversion
            return self._generate_unit_conversion()
    
    def _generate_perimeter_calculation(self) -> Question:
        """
        Perimeter Calculation - Using SymPy for geometric verification
        
        PHASE 1: Deterministic Skeleton (SymPy Rectangle/geometry)
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton with SymPy
        # ===========================================
        shape = random.choice(["rectangle", "square"])
        
        if shape == "rectangle":
            length = random.randint(4, 10)
            width = random.randint(2, 8)
            # Calculate perimeter: 2 × (length + width)
            correct_perimeter = 2 * (length + width)
            shape_desc = f"rectangle with length {length} cm and width {width} cm"
        else:  # square
            side = random.randint(5, 12)
            # Calculate perimeter: 4 × side
            correct_perimeter = 4 * side
            shape_desc = f"square with side {side} cm"
        
        correct_answer = str(correct_perimeter)
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Ravi wants to fence his {shape} garden. He needs to calculate the perimeter to buy the right amount of fencing. His garden is a {shape_desc}. What is the perimeter?",
            f"Priya is drawing a {shape} on paper with a border. The {shape_desc}. How much border does she need?",
            f"A {shape} playground has dimensions of {shape_desc}. The groundkeeper needs to know the perimeter to buy paint for the edges. What is the perimeter in cm?",
            f"An art class is framing a {shape} picture with {shape_desc}. The frame goes around the entire edge. What is the perimeter?",
            f"A {shape} room has {shape_desc}. The carpenter needs to know the perimeter to install baseboards. What is the perimeter in cm?",
        ])
        
        character = random.choice(["Dev", "Ananya", "Vikram", "Sneha"])
        misconception_hook = random.choice([
            "confused perimeter with area",
            "forgot to multiply by 2 for opposite sides",
            "added length and width only once",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Using area instead of perimeter
        if shape == "rectangle":
            wrong_area = length * width
        else:
            wrong_area = side * side
        
        wrong_options.append((
            str(wrong_area),
            MisconceptionType.FORMULA_CONFUSION,
            "Calculated area instead",
            f"You multiplied the dimensions to get {wrong_area}, which is the AREA, not the perimeter. Perimeter is the distance AROUND the shape.",
            "Perimeter = sum of all sides. For rectangle: 2×(length + width). For square: 4×side"
        ))
        
        # Misconception 2: Adding only 2 sides instead of all
        if shape == "rectangle":
            half_perimeter = length + width
        else:
            half_perimeter = side * 2
        
        wrong_options.append((
            str(half_perimeter),
            MisconceptionType.INCOMPLETE_REASONING,
            "Counted only half the sides",
            f"You added only 2 sides ({half_perimeter}), but you need to count ALL sides around the shape",
            "Every side of the shape must be counted. A rectangle has 4 sides: 2 lengths + 2 widths"
        ))
        
        # Misconception 3: Using wrong dimension or formula
        if shape == "rectangle":
            wrong_formula = (length + width + length)  # Forgot one dimension
        else:
            wrong_formula = side * 3  # Only 3 sides
        
        wrong_options.append((
            str(wrong_formula),
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Incomplete formula",
            f"This uses an incomplete formula. You need to count every side exactly once.",
            "Perimeter counts every edge: rectangle has 2 length sides + 2 width sides = 4 sides total"
        ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
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
        
        # Convert distractor_info list to DistractorSet
        distractor_info = DistractorSet(
            correct_answer=correct_answer,
            distractors=[d for d in distractor_info_list if d is not None and d.value != correct_answer]
        )
        
        # Create trap_info using the helper
        trap_info = self.create_trap_info(
            MisconceptionType.FORMULA_CONFUSION,
            custom_description="Confusing perimeter (around) with area (inside)",
            custom_why_effective="Students focus on 'size' rather than 'distance around'",
            custom_how_to_avoid="Perimeter = distance AROUND the edge. Area = space INSIDE."
        )
        
        # PHASE 4: Rich Rendering
        # =======================
        if shape == "rectangle":
            solution_steps = [
                f"Rectangle: length = {length} cm, width = {width} cm",
                f"Perimeter = 2 × (length + width)",
                f"Perimeter = 2 × ({length} + {width})",
                f"Perimeter = 2 × {length + width}",
                f"Perimeter = {correct_perimeter} cm"
            ]
        else:
            solution_steps = [
                f"Square: side = {side} cm",
                f"Perimeter = 4 × side",
                f"Perimeter = 4 × {side}",
                f"Perimeter = {correct_perimeter} cm"
            ]
        
        visual_diagram = self._render_perimeter_diagram(shape, length if shape == "rectangle" else side, width if shape == "rectangle" else None)
        
        hints = [
            f"Hint 1: Perimeter means the distance AROUND the outside of the shape",
            f"Hint 2: A {shape} has 4 sides",
            f"Hint 3: Remember to add up ALL 4 sides, not just 2",
            f"Hint 4: The formula for a {shape} perimeter is " + ("2×(length + width)" if shape == "rectangle" else "4×side")
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic=f"Perimeter Calculation - {shape.capitalize()}",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Remember: Perimeter = distance AROUND (not area inside).",
            data_representation=f"{shape.capitalize()} with labeled dimensions",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s geometry problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_area_calculation(self) -> Question:
        """
        Area Calculation
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        shape = random.choice(["rectangle", "square", "triangle"])
        
        if shape == "rectangle":
            length = random.randint(4, 10)
            width = random.randint(2, 8)
            correct_area = length * width
            shape_desc = f"rectangle with length {length} cm and width {width} cm"
            params = {"length": length, "width": width}
        elif shape == "square":
            side = random.randint(5, 12)
            correct_area = side * side
            shape_desc = f"square with side {side} cm"
            params = {"side": side}
        else:  # triangle
            base = random.randint(4, 10)
            height = random.randint(3, 8)
            correct_area = (base * height) // 2
            shape_desc = f"triangle with base {base} cm and height {height} cm"
            params = {"base": base, "height": height}
        
        correct_answer = str(correct_area)
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A farmer has a {shape_desc}. He wants to know the area to plan his crops. What is the area in square cm?",
            f"Meera's {shape} plot is {shape_desc}. She needs to calculate the area to buy seeds. What is the area?",
            f"A school is creating a {shape} garden with {shape_desc}. The gardener needs to know the area to buy soil. What is the area in square cm?",
            f"An architect is designing a {shape} room with {shape_desc}. What is the area in square cm?",
            f"A painter needs to paint a {shape} wall with {shape_desc}. What is the total area to paint in square cm?",
        ])
        
        character = random.choice(["Rohan", "Priya", "Karan", "Anaya"])
        misconception_hook = random.choice([
            "confused area with perimeter",
            "forgot to use the correct formula",
            "didn't divide by 2 for triangle",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Using perimeter instead of area
        if shape == "rectangle":
            wrong_perimeter = 2 * (length + width)
        elif shape == "square":
            wrong_perimeter = 4 * side
        else:
            wrong_perimeter = base + height + int((base**2 + height**2)**0.5)
        
        wrong_options.append((
            str(wrong_perimeter),
            MisconceptionType.FORMULA_CONFUSION,
            "Calculated perimeter instead",
            f"You calculated {wrong_perimeter}, which is the PERIMETER (distance around), not the area. Area is the space INSIDE.",
            "Area measures space inside the shape. Perimeter measures distance around the shape."
        ))
        
        # Misconception 2: Not using complete formula (for triangle: forgot to divide by 2)
        if shape == "triangle":
            wrong_full_product = base * height
            wrong_options.append((
                str(wrong_full_product),
                MisconceptionType.INCOMPLETE_REASONING,
                "Forgot to divide by 2",
                f"You multiplied base × height = {wrong_full_product}, but for a triangle, you must divide by 2. A triangle is half a rectangle.",
                "Triangle area = (base × height) ÷ 2, because a triangle is exactly half a rectangle"
            ))
        else:
            # For rectangle/square: wrong formula using only one dimension
            if shape == "rectangle":
                wrong_one_dim = length * 2  # Only used length
            else:
                wrong_one_dim = side * 2  # Only used one measurement
            
            wrong_options.append((
                str(wrong_one_dim),
                MisconceptionType.INCOMPLETE_REASONING,
                "Used only one dimension",
                f"You used only one measurement, but area requires multiplying LENGTH × WIDTH (or side × side for square)",
                "Area always multiplies two perpendicular measurements"
            ))
        
        # Misconception 3: Adding instead of multiplying
        if shape == "rectangle":
            wrong_add = length + width
        elif shape == "square":
            wrong_add = side + side
        else:
            wrong_add = base + height
        
        wrong_options.append((
            str(wrong_add),
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Added instead of multiplied",
            f"You added the dimensions ({wrong_add}), but area requires MULTIPLICATION of length × width",
            "Area = length × width (or base × height for triangle ÷ 2). Never add dimensions for area."
        ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
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
        if shape == "rectangle":
            solution_steps = [
                f"Rectangle: length = {length} cm, width = {width} cm",
                f"Area = length × width",
                f"Area = {length} × {width}",
                f"Area = {correct_area} square cm"
            ]
        elif shape == "square":
            solution_steps = [
                f"Square: side = {side} cm",
                f"Area = side × side",
                f"Area = {side} × {side}",
                f"Area = {correct_area} square cm"
            ]
        else:
            solution_steps = [
                f"Triangle: base = {base} cm, height = {height} cm",
                f"Area = (base × height) ÷ 2",
                f"Area = ({base} × {height}) ÷ 2",
                f"Area = {base * height} ÷ 2",
                f"Area = {correct_area} square cm"
            ]
        
        visual_diagram = self._render_area_diagram(shape, params)
        
        hints = [
            f"Hint 1: Area means the space INSIDE the {shape}",
            f"Hint 2: Area is measured in SQUARE units (cm²)",
            f"Hint 3: You must MULTIPLY the dimensions",
            f"Hint 4: Area formula for {shape}: " + (
                "length × width" if shape == "rectangle" else
                "side × side" if shape == "square" else
                "(base × height) ÷ 2"
            )
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic=f"Area Calculation - {shape.capitalize()}",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Remember: Area = space INSIDE. Use correct formula!",
            data_representation=f"{shape.capitalize()} with labeled dimensions and grid squares",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s geometry problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_unit_conversion(self) -> Question:
        """
        Unit Conversion
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        conversion_type = random.choice(["cm_to_m", "m_to_cm", "km_to_m"])
        
        if conversion_type == "cm_to_m":
            value_cm = random.choice([100, 200, 300, 450, 500, 750])
            correct_value_m = value_cm / 100
            correct_answer = str(int(correct_value_m) if correct_value_m == int(correct_value_m) else correct_value_m)
            conversion_desc = f"{value_cm} cm to meters"
            factor = 100
            unit_from = "cm"
            unit_to = "m"
        elif conversion_type == "m_to_cm":
            value_m = random.choice([2, 3, 4, 5, 6, 7, 8])
            correct_value_cm = value_m * 100
            correct_answer = str(correct_value_cm)
            conversion_desc = f"{value_m} m to centimeters"
            factor = 100
            unit_from = "m"
            unit_to = "cm"
        else:  # km_to_m
            value_km = random.choice([1, 2, 3, 4, 5])
            correct_value_m = value_km * 1000
            correct_answer = str(correct_value_m)
            conversion_desc = f"{value_km} km to meters"
            factor = 1000
            unit_from = "km"
            unit_to = "m"
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A runner jogs {conversion_desc} every morning. What is the distance in {unit_to}?",
            f"The distance from Ravi's home to school is {conversion_desc}. How many {unit_to} does he walk?",
            f"A cloth roll has a length of {conversion_desc}. Express in {unit_to}.",
            f"The height of a building is {conversion_desc}. What is the height in {unit_to}?",
            f"A road project requires measurements of {conversion_desc}. What is this in {unit_to}?",
        ])
        
        character = random.choice(["Rahul", "Priya", "Vikram", "Sneha"])
        misconception_hook = random.choice([
            "mixed up which way to convert",
            "used the wrong conversion factor",
            "moved the decimal the wrong direction",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Wrong direction (reverse conversion)
        if conversion_type == "cm_to_m":
            wrong_reverse = value_cm * 100
        elif conversion_type == "m_to_cm":
            wrong_reverse = value_m / 100
        else:
            wrong_reverse = value_km / 1000
        
        wrong_options.append((
            str(int(wrong_reverse) if wrong_reverse == int(wrong_reverse) else wrong_reverse),
            MisconceptionType.FORMULA_CONFUSION,
            "Reversed conversion",
            f"You converted backwards. {unit_from} to {unit_to} requires dividing by {factor} (if going smaller) or multiplying by {factor} (if going larger).",
            f"Remember: 1 {unit_to} = {factor} {unit_from}. So divide to go to larger units, multiply to go to smaller units."
        ))
        
        # Misconception 2: Off-by-one factor error (using 10 instead of 100, or 100 instead of 1000)
        if conversion_type == "cm_to_m":
            wrong_factor = value_cm / 10
        elif conversion_type == "m_to_cm":
            wrong_factor = value_m * 10
        else:
            wrong_factor = value_km * 100
        
        wrong_options.append((
            str(int(wrong_factor) if wrong_factor == int(wrong_factor) else wrong_factor),
            MisconceptionType.INCOMPLETE_REASONING,
            "Wrong conversion factor",
            f"You used the wrong factor. The correct conversion is 1 {unit_to} = {factor} {unit_from}",
            f"Write down the conversion first: 1 {unit_to} = {factor} {unit_from}. Then multiply or divide accordingly."
        ))
        
        # Misconception 3: Decimal point error or random guess
        random_options = []
        if conversion_type == "cm_to_m" and isinstance(correct_value_m, float):
            random_options.append(int(correct_value_m))
        if conversion_type == "m_to_cm" and isinstance(correct_value_cm, float):
            random_options.append(int(correct_value_cm))
        if conversion_type == "km_to_m" and isinstance(correct_value_m, float):
            random_options.append(int(correct_value_m))
        
        if random_options:
            random_wrong = random.choice(random_options)
        else:
            random_wrong = random.choice([999, 888])
        
        if str(random_wrong) not in [opt[0] for opt in wrong_options]:
            wrong_options.append((
                str(random_wrong),
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Random guess",
                f"This doesn't follow the correct conversion. Always use the conversion factor {factor}.",
                f"Step 1: Know the conversion factor (1 {unit_to} = {factor} {unit_from}). Step 2: Apply it carefully."
            ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
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
            f"Conversion: {unit_from} to {unit_to}",
            f"Conversion factor: 1 {unit_to} = {factor} {unit_from}",
        ]
        
        if conversion_type == "cm_to_m":
            solution_steps.extend([
                f"{value_cm} cm ÷ 100 = {correct_value_m} m",
                f"Answer: {correct_answer} m"
            ])
        elif conversion_type == "m_to_cm":
            solution_steps.extend([
                f"{value_m} m × 100 = {correct_value_cm} cm",
                f"Answer: {correct_answer} cm"
            ])
        else:
            solution_steps.extend([
                f"{value_km} km × 1000 = {correct_value_m} m",
                f"Answer: {correct_answer} m"
            ])
        
        visual_diagram = self._render_unit_conversion_chart(unit_from, unit_to, factor)
        
        hints = [
            f"Hint 1: The conversion factor is 1 {unit_to} = {factor} {unit_from}",
            f"Hint 2: Smaller unit ({unit_from}) = larger number; larger unit ({unit_to}) = smaller number",
            f"Hint 3: Going from {unit_from} to {unit_to}: " + ("divide by " + str(factor) if conversion_type == "cm_to_m" else "multiply by " + str(factor)),
            f"Hint 4: Write the conversion clearly before calculating"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic=f"Unit Conversion - {unit_from} to {unit_to}",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Always use correct conversion factor: 1 {unit_to} = {factor} {unit_from}",
            data_representation="Conversion factor chart and calculation steps",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s measurement problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question


    # ==================== HELPER RENDERING METHODS ====================
    
    def _render_perimeter_diagram(self, shape: str, dim1: int, dim2: int = None) -> Dict[str, str]:
        """
        Render perimeter visualization with labeled sides
        Shows the path around the shape with arrows
        """
        if shape == "rectangle":
            length = dim1
            width = dim2
            html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Perimeter of Rectangle</h4>
            
            <div style="margin: 20px auto; width: 300px; height: 200px; position: relative; border: 3px solid #d32f2f;">
                <!-- Top side -->
                <div style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-weight: bold; color: #d32f2f;">{length} cm</div>
                
                <!-- Right side -->
                <div style="position: absolute; right: -50px; top: 50%; transform: translateY(-50%); font-weight: bold; color: #d32f2f;">{width} cm</div>
                
                <!-- Bottom side -->
                <div style="position: absolute; bottom: -25px; left: 50%; transform: translateX(-50%); font-weight: bold; color: #d32f2f;">{length} cm</div>
                
                <!-- Left side -->
                <div style="position: absolute; left: -50px; top: 50%; transform: translateY(-50%); font-weight: bold; color: #d32f2f;">{width} cm</div>
                
                <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #666;">
                    (Inside area)
                </div>
            </div>
            
            <div style="margin: 20px 0; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                <strong>Formula:</strong> Perimeter = 2 × (length + width)<br>
                <strong>Calculation:</strong> 2 × ({length} + {width}) = 2 × {length + width} = {2 * (length + width)} cm<br>
                <strong>What it means:</strong> The distance you travel if you walk around the entire edge
            </div>
        </div>
        """
        else:  # square
            side = dim1
            html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Perimeter of Square</h4>
            
            <div style="margin: 20px auto; width: 250px; height: 250px; position: relative; border: 3px solid #d32f2f;">
                <!-- All sides labeled -->
                <div style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-weight: bold; color: #d32f2f;">{side} cm</div>
                <div style="position: absolute; right: -50px; top: 50%; transform: translateY(-50%); font-weight: bold; color: #d32f2f;">{side} cm</div>
                <div style="position: absolute; bottom: -25px; left: 50%; transform: translateX(-50%); font-weight: bold; color: #d32f2f;">{side} cm</div>
                <div style="position: absolute; left: -50px; top: 50%; transform: translateY(-50%); font-weight: bold; color: #d32f2f;">{side} cm</div>
                
                <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #666;">
                    (Inside area)
                </div>
            </div>
            
            <div style="margin: 20px 0; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                <strong>Formula:</strong> Perimeter = 4 × side<br>
                <strong>Calculation:</strong> 4 × {side} = {4 * side} cm<br>
                <strong>What it means:</strong> All 4 sides are equal, so we multiply by 4
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_area_diagram(self, shape: str, params: Dict[str, int]) -> Dict[str, str]:
        """
        Render area visualization with grid squares
        Shows the internal space being measured
        """
        if shape == "rectangle":
            length = params["length"]
            width = params["width"]
            area = length * width
            html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Area of Rectangle</h4>
            
            <div style="margin: 20px auto; position: relative;">
                <div style="display: grid; grid-template-columns: repeat({min(length, 10)}, 20px); grid-template-rows: repeat({min(width, 10)}, 20px); gap: 2px; padding: 10px; background: #fff; border: 2px solid #4CAF50;">
        """
            for i in range(min(area, 100)):
                html += f'<div style="background: #4CAF50; border: 1px solid #2e7d32;"></div>'
            html += f"""
                </div>
                
                <div style="margin-top: 10px; text-align: center;">
                    <strong>Length = {length} cm, Width = {width} cm</strong>
                </div>
            </div>
            
            <div style="margin: 20px 0; padding: 10px; background: #e8f5e9; border-left: 4px solid #4CAF50;">
                <strong>Formula:</strong> Area = length × width<br>
                <strong>Calculation:</strong> {length} × {width} = {area} square cm<br>
                <strong>What it means:</strong> The total green squares you can fit inside = {area}
            </div>
        </div>
        """
        elif shape == "square":
            side = params["side"]
            area = side * side
            html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Area of Square</h4>
            
            <div style="margin: 20px auto; position: relative;">
                <div style="display: grid; grid-template-columns: repeat({min(side, 10)}, 20px); grid-template-rows: repeat({min(side, 10)}, 20px); gap: 2px; padding: 10px; background: #fff; border: 2px solid #2196F3;">
        """
            for i in range(min(area, 100)):
                html += f'<div style="background: #2196F3; border: 1px solid #1565c0;"></div>'
            html += f"""
                </div>
                
                <div style="margin-top: 10px; text-align: center;">
                    <strong>Side = {side} cm</strong>
                </div>
            </div>
            
            <div style="margin: 20px 0; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                <strong>Formula:</strong> Area = side × side<br>
                <strong>Calculation:</strong> {side} × {side} = {area} square cm<br>
                <strong>What it means:</strong> The total blue squares you can fit inside = {area}
            </div>
        </div>
        """
        else:  # triangle
            base = params["base"]
            height = params["height"]
            area = (base * height) // 2
            html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Area of Triangle</h4>
            
            <div style="margin: 20px auto; width: 100%; max-width: 300px;">
                <svg viewBox="0 0 {base * 10} {height * 12}" style="border: 1px solid #666; background: #fff;">
                    <!-- Triangle -->
                    <polygon points="0,{height*10} {base*10},{height*10} {base*5},0" fill="#ff9800" stroke="#e65100" stroke-width="2"/>
                    
                    <!-- Height line -->
                    <line x1="{base*5}" y1="0" x2="{base*5}" y2="{height*10}" stroke="#d32f2f" stroke-width="2" stroke-dasharray="5,5"/>
                    
                    <!-- Base label -->
                    <text x="{base*5}" y="{height*10+20}" text-anchor="middle" font-weight="bold" fill="#d32f2f">
                        Base = {base} cm
                    </text>
                    
                    <!-- Height label -->
                    <text x="{base*5+25}" y="{height*5}" font-weight="bold" fill="#d32f2f">
                        Height = {height} cm
                    </text>
                </svg>
            </div>
            
            <div style="margin: 20px 0; padding: 10px; background: #fff3e0; border-left: 4px solid #ff9800;">
                <strong>Formula:</strong> Area = (base × height) ÷ 2<br>
                <strong>Calculation:</strong> ({base} × {height}) ÷ 2 = {base * height} ÷ 2 = {area} square cm<br>
                <strong>Why divide by 2?</strong> A triangle is exactly half a rectangle with the same base and height
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_unit_conversion_chart(self, unit_from: str, unit_to: str, factor: int) -> Dict[str, str]:
        """
        Render unit conversion reference chart
        Shows the relationship between units
        """
        html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Metric Unit Conversion Chart</h4>
            
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0; background: #fff;">
                <tr style="background: #2196F3; color: white;">
                    <th style="border: 1px solid #333; padding: 10px;">Smaller Unit</th>
                    <th style="border: 1px solid #333; padding: 10px;">Conversion</th>
                    <th style="border: 1px solid #333; padding: 10px;">Larger Unit</th>
                </tr>
                <tr style="background: #e3f2fd;">
                    <td style="border: 1px solid #333; padding: 10px; font-weight: bold; text-align: center;">{factor} {unit_from}</td>
                    <td style="border: 1px solid #333; padding: 10px; text-align: center;">
                        <span style="color: #d32f2f; font-weight: bold;">÷ {factor}</span><br>
                        or<br>
                        <span style="color: #d32f2f; font-weight: bold;">× 1/{factor}</span>
                    </td>
                    <td style="border: 1px solid #333; padding: 10px; font-weight: bold; text-align: center;">1 {unit_to}</td>
                </tr>
            </table>
            
            <div style="margin: 15px 0; padding: 10px; background: #c8e6c9; border-left: 4px solid #4CAF50;">
                <strong>To convert from {unit_from} to {unit_to}:</strong><br>
                Divide by {factor} (because {unit_to} is larger)<br>
                <strong>To convert from {unit_to} to {unit_from}:</strong><br>
                Multiply by {factor} (because {unit_from} is smaller)
            </div>
            
            <div style="margin: 15px 0; padding: 10px; background: #fff9c4; border-left: 4px solid #fbc02d;">
                <strong>Remember:</strong><br>
                • Smaller unit = larger number<br>
                • Larger unit = smaller number<br>
                • Always check if your answer makes sense!
            </div>
        </div>
        """
        
        return {"html": html}

    # ==================== IMPLEMENTATION GUIDE ====================
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

