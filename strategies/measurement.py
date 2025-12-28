"""Strategy for Chapter 14: How Big/Heavy - Measurement and Unit Conversions."""

import random
from typing import List, Tuple
from models.question import Question, ChapterEnum
from models.distractor import MisconceptionType, TrapType
from models.cognitive_levels import BloomLevel
from strategies.base import BaseChapterStrategy


class MeasurementStrategy(BaseChapterStrategy):
    """Generate questions for measurement and unit conversions."""
    
    chapter = ChapterEnum.MEASUREMENT
    chapter_name = "Chapter 14: How Big/Heavy"
    description = "Measurement, conversions, and real-world applications"
    
    def generate(self) -> Question:
        """Generate a random measurement question from available types."""
        question_type = random.choice([
            self._generate_length_conversion,
            self._generate_weight_conversion,
            self._generate_capacity_conversion,
            self._generate_measurement_comparison,
            self._generate_estimation_real_world,
            self._generate_multiple_unit_conversion
        ])
        return question_type()
    
    def _generate_length_conversion(self) -> Question:
        """Convert between mm, cm, m, km.
        
        Example: 5 cm = ? mm, or 1500 m = ? km
        """
        # Choose conversion type
        conversion_type = random.choice([
            ("mm", "cm"),
            ("cm", "m"),
            ("m", "km"),
            ("cm", "mm"),
            ("m", "cm")
        ])
        
        from_unit, to_unit = conversion_type
        
        # Define conversion factors
        factors = {
            ("mm", "cm"): (1, 10),
            ("cm", "mm"): (10, 1),
            ("cm", "m"): (1, 100),
            ("m", "cm"): (100, 1),
            ("m", "km"): (1, 1000),
            ("km", "m"): (1000, 1),
        }
        
        factor_from, factor_to = factors[conversion_type]
        
        # Generate number
        from_value = random.choice([2, 3, 4, 5, 10, 25, 50, 100])
        if to_unit == "km":
            from_value = random.choice([500, 1000, 1500, 2000, 5000])
        
        to_value = from_value * factor_from // factor_to
        correct_answer = str(to_value)
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.UNIT_ERROR: str(from_value),  # No conversion
            MisconceptionType.INCOMPLETE_REASONING: str(from_value * factor_to),  # Wrong direction
            MisconceptionType.OPERATION_SELECTION: str(from_value + factor_from)  # Addition instead
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.UNIT_ERROR,
            difficulty=2,
            custom_description="Student forgets to convert units or multiplies instead of dividing",
            custom_why_effective="Conversion direction is confusing; students reverse multiply/divide",
            custom_how_to_avoid="Remember: smaller unit = bigger number. To go from large to small unit, multiply"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        conversion_table = self._create_conversion_table("Length")
        
        question = Question(
            chapter=self.chapter,
            topic="Length Unit Conversion",
            logical_trap="Student reverses conversion or forgets the conversion factor",
            data_representation=conversion_table,
            question_text=f"Convert: {from_value} {from_unit} = ? {to_unit}",
            solution_steps=[
                f"Converting from {from_unit} to {to_unit}",
                f"1 {to_unit} = {factor_from} {from_unit}",
                f"{from_value} {from_unit} ÷ {factor_from} = {to_value} {to_unit}" if factor_from > 1 else f"{from_value} {from_unit} × {factor_to} = {to_value} {to_unit}",
                f"Answer: {to_value} {to_unit}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_weight_conversion(self) -> Question:
        """Convert between mg, g, kg.
        
        Example: 2500 g = ? kg, or 3 kg = ? g
        """
        conversion_type = random.choice([
            ("g", "kg"),
            ("kg", "g"),
            ("mg", "g"),
            ("g", "mg")
        ])
        
        from_unit, to_unit = conversion_type
        
        # Define conversion factors
        factors = {
            ("g", "kg"): (1, 1000),
            ("kg", "g"): (1000, 1),
            ("mg", "g"): (1, 1000),
            ("g", "mg"): (1000, 1),
        }
        
        factor_from, factor_to = factors[conversion_type]
        
        # Generate value
        if from_unit == "kg":
            from_value = random.choice([2, 3, 5, 10])
        elif from_unit == "g":
            from_value = random.choice([500, 1000, 1500, 2000, 2500])
        else:  # mg
            from_value = random.choice([250, 500, 1000])
        
        to_value = from_value * factor_from // factor_to
        correct_answer = str(to_value)
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.UNIT_ERROR: str(from_value),  # No conversion
            MisconceptionType.INCOMPLETE_REASONING: str(from_value * factor_to),  # Wrong direction
            MisconceptionType.CONSTRAINT_VIOLATION: str(to_value + 100)  # Off by constant
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.UNIT_ERROR,
            difficulty=2,
            custom_description="Student applies wrong conversion factor for weight units",
            custom_why_effective="Weight units have less familiar conversion factors",
            custom_how_to_avoid="Write down: 1 kg = 1000 g, then work from there"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        conversion_table = self._create_conversion_table("Weight")
        
        question = Question(
            chapter=self.chapter,
            topic="Weight Unit Conversion",
            logical_trap="Student reverses weight conversion or uses wrong factor",
            data_representation=conversion_table,
            question_text=f"Convert: {from_value} {from_unit} = ? {to_unit}",
            solution_steps=[
                f"Converting from {from_unit} to {to_unit}",
                f"1 kg = 1000 g (or 1 g = 1000 mg)",
                f"{from_value} {from_unit} = {to_value} {to_unit}",
                f"Answer: {to_value} {to_unit}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_capacity_conversion(self) -> Question:
        """Convert between mL and L.
        
        Example: 2500 mL = ? L, or 3 L = ? mL
        """
        conversion_type = random.choice([
            ("mL", "L"),
            ("L", "mL")
        ])
        
        from_unit, to_unit = conversion_type
        
        # Define conversion factor
        if conversion_type == ("mL", "L"):
            factor_from, factor_to = 1, 1000
            from_value = random.choice([250, 500, 750, 1000, 1500, 2000])
        else:  # L to mL
            factor_from, factor_to = 1000, 1
            from_value = random.choice([1, 2, 3, 4, 5])
        
        to_value = from_value * factor_from // factor_to
        correct_answer = str(to_value)
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.UNIT_ERROR: str(from_value),  # No conversion
            MisconceptionType.INCOMPLETE_REASONING: str(from_value * factor_to),  # Wrong direction
            MisconceptionType.ARITHMETIC_ERROR: str(to_value - 50)  # Off by 50
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.UNIT_ERROR,
            difficulty=2,
            custom_description="Student doesn't convert between mL and L or uses wrong factor",
            custom_why_effective="Capacity conversions are less practiced than length",
            custom_how_to_avoid="Remember: 1 L = 1000 mL (just like 1 kg = 1000 g)"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        conversion_table = self._create_conversion_table("Capacity")
        
        question = Question(
            chapter=self.chapter,
            topic="Capacity Unit Conversion",
            logical_trap="Student forgets conversion factor or applies it backwards",
            data_representation=conversion_table,
            question_text=f"Convert: {from_value} {from_unit} = ? {to_unit}",
            solution_steps=[
                f"Converting from {from_unit} to {to_unit}",
                f"1 L = 1000 mL",
                f"{from_value} {from_unit} = {to_value} {to_unit}",
                f"Answer: {to_value} {to_unit}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_measurement_comparison(self) -> Question:
        """Compare measurements in different units.
        
        'Which is longer: 1.5 m or 150 cm?'
        """
        # Create two measurements
        value1, unit1 = random.choice([
            (150, "cm"),
            (1.5, "m"),
            (1500, "mm"),
            (2000, "g"),
            (2, "kg"),
            (750, "mL"),
            (0.75, "L")
        ])
        
        value2, unit2 = random.choice([
            (1.5, "m"),
            (150, "cm"),
            (2, "kg"),
            (2000, "g"),
            (0.75, "L"),
            (750, "mL")
        ])
        
        # Convert to common units for comparison
        conversion_map = {
            "mm": 0.001,
            "cm": 0.01,
            "m": 1,
            "km": 1000,
            "g": 0.001,
            "kg": 1,
            "mL": 0.001,
            "L": 1
        }
        
        val1_standard = value1 * conversion_map[unit1]
        val2_standard = value2 * conversion_map[unit2]
        
        if val1_standard > val2_standard:
            correct_answer = f"{value1} {unit1}"
        elif val2_standard > val1_standard:
            correct_answer = f"{value2} {unit2}"
        else:
            correct_answer = "They are equal"
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{value2} {unit2}",  # Reversed
            MisconceptionType.CONSTRAINT_VIOLATION: "Cannot compare different units",
            MisconceptionType.OPERATION_SELECTION: f"{value1 + value2} {unit1}"  # Add instead
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student compares numbers without converting to same units",
            custom_why_effective="150 > 1.5 numerically, but 150 cm < 1.5 m when converted",
            custom_how_to_avoid="Always convert to same units before comparing"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Comparing Measurements",
            logical_trap="Student compares numbers without converting to common units",
            data_representation=f"Compare: {value1} {unit1} vs {value2} {unit2}",
            question_text=f"Which is larger: {value1} {unit1} or {value2} {unit2}?",
            solution_steps=[
                f"Convert to common units:",
                f"{value1} {unit1} = {val1_standard} (standard)",
                f"{value2} {unit2} = {val2_standard} (standard)",
                f"Compare: {val1_standard} vs {val2_standard}",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_estimation_real_world(self) -> Question:
        """Estimate measurements in real-world context.
        
        'What is the most realistic height of a door?'
        """
        # Create context with measurement options
        contexts = [
            {
                "item": "height of a door",
                "options": ["2 cm", "2 m", "2 km"],
                "correct": "2 m"
            },
            {
                "item": "length of a pencil",
                "options": ["19 cm", "19 m", "19 km"],
                "correct": "19 cm"
            },
            {
                "item": "weight of an apple",
                "options": ["200 g", "200 kg", "20 g"],
                "correct": "200 g"
            },
            {
                "item": "capacity of a water bottle",
                "options": ["500 mL", "500 L", "50 mL"],
                "correct": "500 mL"
            },
            {
                "item": "height of a basketball hoop",
                "options": ["3 m", "30 cm", "30 m"],
                "correct": "3 m"
            }
        ]
        
        context = random.choice(contexts)
        correct_answer = context["correct"]
        
        # PHASE 1: Misconceptions
        wrong_options = [o for o in context["options"] if o != correct_answer]
        misconception_map = {}
        
        for i, wrong in enumerate(wrong_options):
            misc_types = [
                MisconceptionType.CONSTRAINT_VIOLATION,
                MisconceptionType.INCOMPLETE_REASONING,
                MisconceptionType.UNIT_ERROR
            ]
            misconception_map[misc_types[i % len(misc_types)]] = wrong
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.CONSTRAINT_VIOLATION,
            difficulty=3,
            custom_description="Student chooses unrealistic unit or scale",
            custom_why_effective="Without real-world reference, students pick any number",
            custom_how_to_avoid="Think of familiar objects and compare: is this bigger/smaller?"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=3)
        
        question = Question(
            chapter=self.chapter,
            topic="Real-World Estimation",
            logical_trap="Student doesn't connect measurement to real-world experience",
            data_representation=f"Estimate the {context['item']}",
            question_text=f"What is the most realistic {context['item']}?",
            solution_steps=[
                f"Think of real-world comparison",
                f"Is {context['item']} very small, medium, or very large?",
                f"Compare to familiar objects",
                f"Most realistic answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_multiple_unit_conversion(self) -> Question:
        """Convert through multiple unit steps.
        
        'Convert 3 km to cm'
        """
        # Create multi-step conversion
        steps = random.choice([
            (("km", "m"), ("m", "cm")),
            (("kg", "g"), ("g", "mg")),
            (("L", "mL"), )
        ])
        
        # Start with base value
        if steps[0][0] == "km":
            start_value = random.randint(1, 5)
        elif steps[0][0] == "kg":
            start_value = random.randint(1, 5)
        else:
            start_value = random.randint(1, 3)
        
        start_unit = steps[0][0]
        
        # Calculate through each step
        current_value = start_value
        for from_u, to_u in steps:
            factors = {
                ("km", "m"): 1000,
                ("m", "cm"): 100,
                ("kg", "g"): 1000,
                ("g", "mg"): 1000,
                ("L", "mL"): 1000,
            }
            current_value *= factors.get((from_u, to_u), 1)
        
        end_unit = steps[-1][1]
        correct_answer = str(int(current_value))
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: str(start_value),  # Only first value
            MisconceptionType.OPERATION_SELECTION: str(start_value * 1100),  # Only first step
            MisconceptionType.ARITHMETIC_ERROR: str(int(current_value) - 1000)  # Off by constant
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=3,
            custom_description="Student forgets to complete all conversion steps",
            custom_why_effective="Multi-step conversion requires tracking each stage",
            custom_how_to_avoid="Work through each unit change one at a time"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=3)
        
        question = Question(
            chapter=self.chapter,
            topic="Multi-Step Unit Conversion",
            logical_trap="Student stops after first conversion step",
            data_representation=f"Convert: {start_value} {start_unit} → ? {end_unit}",
            question_text=f"Convert {start_value} {start_unit} to {end_unit}",
            solution_steps=[
                f"Starting value: {start_value} {start_unit}",
                *[f"Step {i+1}: Convert {steps[i][0]} to {steps[i][1]}" for i in range(len(steps))],
                f"Final answer: {correct_answer} {end_unit}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    # ============================================================================
    # VISUALIZATION HELPERS
    # ============================================================================
    
    @staticmethod
    def _create_conversion_table(measurement_type: str) -> str:
        """Create reference table for conversions."""
        tables = {
            "Length": """
Length Conversions:
1 cm = 10 mm
1 m = 100 cm
1 km = 1000 m
            """,
            "Weight": """
Weight Conversions:
1 g = 1000 mg
1 kg = 1000 g
            """,
            "Capacity": """
Capacity Conversions:
1 L = 1000 mL
            """
        }
        return tables.get(measurement_type, "")
    
    def _validate_question(self, question: Question) -> None:
        """Validate question has all required fields."""
        assert question.question_text
        assert question.answer
        assert len(question.options) == 4
        assert 0 <= question.correct_option_index < 4
        assert question.distractor_info
        assert question.trap_info
        assert question.bloom_info
