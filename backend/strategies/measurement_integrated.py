"""
MEASUREMENT - INTEGRATED STRATEGY
=================================

Hybrid Neuro-Symbolic approach for Measurement

Integrates:
1. Measurement instrument simulation
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Scale reading error, Precision illusion)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class MeasurementIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic measurement logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.MEASUREMENT
    chapter_name = "Measurement"
    description = "Measurement with hybrid neuro-symbolic approach"
    
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
            "scale_reading",
            "instrument_precision",
            "unit_estimation",
        ])
        
        if problem_type == "scale_reading":
            return self._generate_scale_reading()
        elif problem_type == "instrument_precision":
            return self._generate_instrument_precision()
        else:  # unit_estimation
            return self._generate_unit_estimation()
    
    def _generate_scale_reading(self) -> Question:
        """
        Scale Reading - Reading values from measurement scales
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Different types of scales
        scale_scenarios = [
            {
                "instrument": "Measuring Tape",
                "unit": "cm",
                "markings_interval": 1,
                "pointer_position": 15,
                "correct_value": "15 cm",
                "description": "Measuring tape with 1cm interval markings"
            },
            {
                "instrument": "Weighing Scale",
                "unit": "kg",
                "markings_interval": 2,
                "pointer_position": 24,
                "correct_value": "24 kg",
                "description": "Weighing scale with 2kg interval markings"
            },
            {
                "instrument": "Thermometer",
                "unit": "°C",
                "markings_interval": 5,
                "pointer_position": 35,
                "correct_value": "35°C",
                "description": "Thermometer with 5°C interval markings"
            },
            {
                "instrument": "Liquid Measuring Cup",
                "unit": "ml",
                "markings_interval": 50,
                "pointer_position": 300,
                "correct_value": "300 ml",
                "description": "Measuring cup with 50ml interval markings"
            }
        ]
        
        scale_data = random.choice(scale_scenarios)
        correct_answer = scale_data["correct_value"]
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Arjun uses a {scale_data['instrument']} to measure something. The pointer points to a specific mark. What does the {scale_data['instrument'].lower()} show? ({scale_data['description']})",
            f"A {scale_data['instrument']} shows a measurement with the pointer at a specific position. What is the reading?",
            f"Priya reads a {scale_data['instrument']}. The pointer is exactly at a marking line. What's the measurement?",
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "misread the scale division",
            "forgot to check the interval between markings",
            "counted wrong number of divisions",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Off-by-one on scale
        wrong_value_1 = scale_data["pointer_position"] + scale_data["markings_interval"]
        wrong_options.append((
            f"{wrong_value_1} {scale_data['unit']}",
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Misread the scale - off by one interval",
            f"You read {wrong_value_1} {scale_data['unit']}, but the pointer is at {scale_data['correct_value']}. The next marking would be at {wrong_value_1} {scale_data['unit']}.",
            f"Look carefully: The pointer is at {scale_data['correct_value']}, not {wrong_value_1} {scale_data['unit']}."
        ))
        
        # Misconception 2: Wrong interval interpretation
        wrong_value_2 = scale_data["pointer_position"] - scale_data["markings_interval"]
        wrong_options.append((
            f"{wrong_value_2} {scale_data['unit']}",
            MisconceptionType.LOGICAL_DISCONNECT,
            "Misread by one division downward",
            f"You said {wrong_value_2} {scale_data['unit']}, but the pointer is clearly at {scale_data['correct_value']}. The previous marking is at {wrong_value_2} {scale_data['unit']}.",
            f"Match the pointer to the exact marking: {scale_data['correct_value']} is correct."
        ))
        
        # Misconception 3: Completely wrong reading
        wrong_value_3 = scale_data["pointer_position"] + (scale_data["markings_interval"] * random.randint(2, 4))
        wrong_options.append((
            f"{wrong_value_3} {scale_data['unit']}",
            MisconceptionType.INCOMPLETE_REASONING,
            "Misread the scale significantly",
            f"You read {wrong_value_3} {scale_data['unit']}, but the pointer is at {scale_data['correct_value']}. Always double-check by looking at nearby markings.",
            f"The pointer position: {scale_data['correct_value']} is the accurate reading."
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
            f"Instrument: {scale_data['instrument']}",
            f"Unit: {scale_data['unit']}",
            f"Markings interval: {scale_data['markings_interval']} {scale_data['unit']}",
            f"Pointer position: Located at a specific marking",
            f"Reading: {scale_data['correct_value']}",
            f"Verification: Pointer aligns with the {scale_data['correct_value']} marking"
        ]
        
        visual_diagram = self._render_scale_diagram(scale_data)
        
        hints = [
            f"Hint 1: The instrument is a {scale_data['instrument']}",
            f"Hint 2: Each small marking represents {scale_data['markings_interval']} {scale_data['unit']}",
            f"Hint 3: Locate where the pointer is positioned",
            f"Hint 4: The reading is {scale_data['correct_value']}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Reading Measurement Scales",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Read the exact marking position!",
            data_representation=f"{scale_data['instrument']} | Markings: {scale_data['markings_interval']} {scale_data['unit']} intervals",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s scale reading: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_instrument_precision(self) -> Question:
        """
        Instrument Precision - Understanding precision and accuracy of instruments
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Precision comparisons
        precision_scenarios = [
            {
                "instruments": "Ruler (mm markings) vs Measuring Tape (cm markings)",
                "more_precise": "Ruler",
                "reason": "Ruler has finer markings (mm) compared to Tape (cm)",
                "accuracy_difference": "Ruler: ±0.5mm | Tape: ±0.5cm (10x less precise)"
            },
            {
                "instruments": "Analog Thermometer (1°C divisions) vs Digital Thermometer (0.1°C)",
                "more_precise": "Digital Thermometer",
                "reason": "Digital shows 0.1°C precision vs Analog's 1°C",
                "accuracy_difference": "Digital: ±0.1°C | Analog: ±0.5°C"
            },
            {
                "instruments": "Spring Balance (100g markings) vs Electronic Scale (1g precision)",
                "more_precise": "Electronic Scale",
                "reason": "Electronic scale measures in grams vs Spring Balance's 100g intervals",
                "accuracy_difference": "Electronic: ±1g | Spring: ±50g"
            },
            {
                "instruments": "Standard Measuring Cup (50ml) vs Graduated Cylinder (5ml)",
                "more_precise": "Graduated Cylinder",
                "reason": "Graduated Cylinder has finer markings (5ml vs 50ml)",
                "accuracy_difference": "Cylinder: ±2.5ml | Cup: ±25ml"
            }
        ]
        
        precision_data = random.choice(precision_scenarios)
        correct_answer = precision_data["more_precise"]
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Priya needs to measure something very precisely for a science experiment. She has two instruments: {precision_data['instruments']}. Which one should she choose for more accurate results? ({precision_data['reason']})",
            f"When measuring {precision_data['instruments']}, which instrument gives more precise results?",
            f"For a task requiring high precision, which is better: {precision_data['instruments']}?",
        ])
        
        character = random.choice(["Priya", "Arjun", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "confused precision with accuracy",
            "didn't consider the markings/divisions",
            "guessed without checking the measurement intervals",
        ])
        
        # Create wrong option
        wrong_instrument = [i for i in precision_data["instruments"].split(" vs ") if i != correct_answer][0]
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Choosing the wrong instrument
        wrong_options.append((
            wrong_instrument,
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Chose {wrong_instrument} instead of {correct_answer}",
            f"You selected {wrong_instrument}, but {correct_answer} is more precise. {precision_data['reason']}",
            f"Precision comparison: {precision_data['accuracy_difference']}"
        ))
        
        # Misconception 2: Both are equally precise
        wrong_options.append((
            "Both are equally precise",
            MisconceptionType.LOGICAL_DISCONNECT,
            "Thought both instruments have same precision",
            f"The instruments have different precisions! {correct_answer} is more precise than {wrong_instrument}.",
            f"Check the markings: {precision_data['accuracy_difference']}"
        ))
        
        # Misconception 3: Confused definition of precision
        wrong_options.append((
            f"It depends on the situation",
            MisconceptionType.INCOMPLETE_REASONING,
            "Didn't understand precision hierarchy",
            f"For measuring precision, {correct_answer} is always more precise than {wrong_instrument} based on their design.",
            f"Precision is determined by the smallest marking: {precision_data['reason']}"
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
            f"Comparing: {precision_data['instruments']}",
            f"Precision of {correct_answer}: Very fine markings",
            f"Precision of {wrong_instrument}: Coarser markings",
            f"Key difference: {precision_data['reason']}",
            f"Accuracy ranges: {precision_data['accuracy_difference']}",
            f"Answer: {correct_answer} is more precise"
        ]
        
        visual_diagram = self._render_precision_diagram(precision_data)
        
        hints = [
            f"Hint 1: Precision depends on the smallest marking on the instrument",
            f"Hint 2: {precision_data['reason']}",
            f"Hint 3: Compare the measurement intervals",
            f"Hint 4: {correct_answer} is the more precise instrument"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Understanding Instrument Precision",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Smaller markings = higher precision!",
            data_representation=f"Precision comparison: {precision_data['accuracy_difference']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s precision challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_unit_estimation(self) -> Question:
        """
        Unit Estimation - Choosing and estimating in appropriate measurement units
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Unit estimation scenarios with real-world objects
        unit_scenarios = [
            {
                "object": "Height of a 5th grade student",
                "correct_unit": "cm or meters",
                "correct_range": "120-150 cm",
                "magnitude": "~140 cm",
                "wrong_units": ["mm (too small)", "km (way too large)"],
                "reasoning": "Student height is typically 100-150 cm, so cm or meters is appropriate"
            },
            {
                "object": "Mass of a math textbook",
                "correct_unit": "grams or kilograms",
                "correct_range": "500-800 grams",
                "magnitude": "~600 grams",
                "wrong_units": ["milligrams (too tiny)", "metric tons (absurdly large)"],
                "reasoning": "Textbook weighs between 500-800 grams, so grams or kg is right"
            },
            {
                "object": "Distance from your home to school",
                "correct_unit": "kilometers or meters",
                "correct_range": "1-5 km",
                "magnitude": "~2 km",
                "wrong_units": ["mm (impossibly small)", "cm (would take forever)"],
                "reasoning": "School distance is typically 1-5 km, so km or meters is appropriate"
            },
            {
                "object": "Volume of a water bottle",
                "correct_unit": "milliliters or liters",
                "correct_range": "500-750 ml",
                "magnitude": "~600 ml",
                "wrong_units": ["microliters (too small)", "cubic meters (way too large)"],
                "reasoning": "Water bottle is 500-750 ml, so ml or liters is right"
            },
            {
                "object": "Temperature on a hot summer day",
                "correct_unit": "degrees Celsius",
                "correct_range": "35-45°C",
                "magnitude": "~40°C",
                "wrong_units": ["Kelvin (scientific, too formal)", "Fahrenheit (different scale)"],
                "reasoning": "Hot day is around 35-45°C in Celsius scale"
            },
            {
                "object": "Thickness of a sheet of paper",
                "correct_unit": "millimeters",
                "correct_range": "0.1-0.2 mm",
                "magnitude": "~0.1 mm",
                "wrong_units": ["cm (too thick)", "meters (impossibly thick)"],
                "reasoning": "Paper thickness is ~0.1 mm, not centimeters"
            }
        ]
        
        unit_data = random.choice(unit_scenarios)
        correct_answer = unit_data["correct_unit"]
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"{random.choice(['Arjun', 'Priya', 'Dev', 'Sneha'])} needs to measure the {unit_data['object']}. Which unit should they use? The correct estimate is around {unit_data['magnitude']}.",
            f"To measure {unit_data['object']}, which unit makes the most sense? ({unit_data['reasoning']})",
            f"If you need to measure {unit_data['object']}, would you use {unit_data['correct_unit']} or something else?",
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "chose the wrong unit scale",
            "didn't think about realistic magnitudes",
            "forgot how measurement units are ordered",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Wrong magnitude order
        wrong_option_1 = random.choice(unit_data["wrong_units"])
        wrong_options.append((
            wrong_option_1,
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Chose {wrong_option_1} for {unit_data['object']}",
            f"You selected '{wrong_option_1}', but that's inappropriate for measuring {unit_data['object']}. {unit_data['reasoning']}",
            f"Remember: {unit_data['object']} ≈ {unit_data['magnitude']}, so {correct_answer} is right"
        ))
        
        # Misconception 2: Different but wrong unit family
        wrong_option_2_choices = {
            "cm or meters": ["inches", "feet"],
            "grams or kilograms": ["pounds", "ounces"],
            "kilometers or meters": ["miles", "yards"],
            "milliliters or liters": ["gallons", "pints"],
            "degrees Celsius": ["degrees Fahrenheit", "Kelvin"],
            "millimeters": ["inches", "cm"]
        }
        if unit_data["correct_unit"] in wrong_option_2_choices:
            wrong_option_2 = random.choice(wrong_option_2_choices[unit_data["correct_unit"]])
        else:
            wrong_option_2 = unit_data["wrong_units"][0]
        
        wrong_options.append((
            wrong_option_2,
            MisconceptionType.LOGICAL_DISCONNECT,
            f"Confused units - chose {wrong_option_2}",
            f"'{wrong_option_2}' is from a different measurement system. {unit_data['reasoning']}",
            f"In the standard metric system, use {correct_answer} for {unit_data['object']}"
        ))
        
        # Misconception 3: Incomplete reasoning
        if len(unit_data["wrong_units"]) > 1:
            wrong_option_3 = unit_data["wrong_units"][1]
        else:
            wrong_option_3 = "Some other unit"
        
        wrong_options.append((
            wrong_option_3,
            MisconceptionType.INCOMPLETE_REASONING,
            "Didn't reason about appropriate scale",
            f"This unit doesn't match the magnitude. {unit_data['object']} has a realistic size of {unit_data['magnitude']}, so {correct_answer} fits perfectly.",
            f"Always estimate the magnitude first, then pick the unit"
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
            f"Problem: Measure {unit_data['object']}",
            f"Estimate the magnitude: approximately {unit_data['magnitude']}",
            f"Choose unit that fits this magnitude: {correct_answer}",
            f"Why? {unit_data['reasoning']}",
            f"Avoid: {unit_data['wrong_units'][0]} (inappropriate scale)"
        ]
        
        visual_diagram = self._render_unit_estimation_diagram({
            "object": unit_data["object"],
            "magnitude": unit_data["magnitude"],
            "correct_unit": unit_data["correct_unit"],
            "wrong_units": unit_data["wrong_units"],
            "reasoning": unit_data["reasoning"]
        })
        
        hints = [
            f"Hint 1: First estimate the size of {unit_data['object']}",
            f"Hint 2: Think about whether it's {unit_data['magnitude']} or something else",
            f"Hint 3: Would you measure in {unit_data['wrong_units'][0]}? No! Too extreme.",
            f"Hint 4: The right unit is {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Choosing Appropriate Measurement Units",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Always estimate magnitude first!",
            data_representation=f"Magnitude: {unit_data['magnitude']}, Suitable unit: {unit_data['correct_unit']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s unit estimation challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question

    # ============================================================================
    # RENDERING HELPERS
    # ============================================================================

    def _render_scale_diagram(self, scale_data: dict) -> dict:
        """
        Render a visual diagram of a measurement scale with markings and pointer
        
        Args:
            scale_data: Dict with 'instrument', 'unit', 'markings_interval', 'pointer_position'
        
        Returns:
            Dict with 'html' key containing SVG/HTML visualization
        """
        instrument = scale_data.get("instrument", "Scale")
        unit = scale_data.get("unit", "")
        pointer_pos = scale_data.get("pointer_position", 5)
        
        # Create SVG scale diagram
        svg_content = f"""
        <svg width="400" height="150" xmlns="http://www.w3.org/2000/svg">
            <!-- Title -->
            <text x="200" y="20" font-size="16" font-weight="bold" text-anchor="middle">
                {instrument} Reading
            </text>
            
            <!-- Scale line -->
            <line x1="50" y1="60" x2="350" y2="60" stroke="black" stroke-width="2"/>
            
            <!-- Markings -->
            <text x="50" y="85" font-size="12" text-anchor="middle">0</text>
            <line x1="50" y1="55" x2="50" y2="65" stroke="black" stroke-width="2"/>
            
            <text x="100" y="85" font-size="12" text-anchor="middle">5</text>
            <line x1="100" y1="58" x2="100" y2="62" stroke="gray" stroke-width="1"/>
            
            <text x="150" y="85" font-size="12" text-anchor="middle">10</text>
            <line x1="150" y1="55" x2="150" y2="65" stroke="black" stroke-width="2"/>
            
            <text x="200" y="85" font-size="12" text-anchor="middle">15</text>
            <line x1="200" y1="58" x2="200" y2="62" stroke="gray" stroke-width="1"/>
            
            <text x="250" y="85" font-size="12" text-anchor="middle">20</text>
            <line x1="250" y1="55" x2="250" y2="65" stroke="black" stroke-width="2"/>
            
            <text x="300" y="85" font-size="12" text-anchor="middle">25</text>
            <line x1="300" y1="58" x2="300" y2="62" stroke="gray" stroke-width="1"/>
            
            <text x="350" y="85" font-size="12" text-anchor="middle">30</text>
            <line x1="350" y1="55" x2="350" y2="65" stroke="black" stroke-width="2"/>
            
            <!-- Pointer -->
            <polygon points="{50 + pointer_pos * 10},40 {45 + pointer_pos * 10},55 {55 + pointer_pos * 10},55" 
                     fill="red"/>
            
            <!-- Unit label -->
            <text x="200" y="120" font-size="14" text-anchor="middle" fill="blue">
                Correct reading: {scale_data.get('correct_value', '')} {unit}
            </text>
        </svg>
        """
        
        return {"html": svg_content}

    def _render_precision_diagram(self, precision_data: dict) -> dict:
        """
        Render comparison of instrument precision with accuracy ranges
        
        Args:
            precision_data: Dict with instrument details and accuracy info
        
        Returns:
            Dict with 'html' key containing comparison table
        """
        html_content = f"""
        <div style="margin: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <h3 style="text-align: center;">Precision Comparison</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #f0f0f0;">
                    <th style="border: 1px solid #999; padding: 8px;">Instrument</th>
                    <th style="border: 1px solid #999; padding: 8px;">Precision Level</th>
                    <th style="border: 1px solid #999; padding: 8px;">Accuracy Range</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #999; padding: 8px;">{precision_data['instruments'].split(' vs ')[0]}</td>
                    <td style="border: 1px solid #999; padding: 8px;">Coarser markings</td>
                    <td style="border: 1px solid #999; padding: 8px;">Lower precision</td>
                </tr>
                <tr style="background-color: #e8f5e9;">
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{precision_data['more_precise']}</strong></td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>Finer markings</strong></td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>Higher precision</strong></td>
                </tr>
            </table>
            <p style="margin-top: 10px; font-size: 13px; color: #333;">
                <strong>Key insight:</strong> {precision_data['reason']}
            </p>
        </div>
        """
        
        return {"html": html_content}

    def _render_unit_estimation_diagram(self, estimation_data: dict) -> dict:
        """
        Render unit estimation diagram showing object magnitude and unit options
        
        Args:
            estimation_data: Dict with object, magnitude, units, and reasoning
        
        Returns:
            Dict with 'html' key containing visual comparison
        """
        html_content = f"""
        <div style="margin: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <h3 style="text-align: center;">Unit Estimation Guide</h3>
            
            <div style="background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3;">
                <strong>Measuring:</strong> {estimation_data['object']}
            </div>
            
            <div style="background-color: #e3f2fd; padding: 10px; margin: 10px 0; border-radius: 3px;">
                <strong>Estimated magnitude:</strong> {estimation_data['magnitude']}
            </div>
            
            <div style="margin: 15px 0;">
                <h4>Unit Options:</h4>
                <ul style="list-style-type: none; padding: 0;">
                    <li style="padding: 8px; margin: 5px 0; background-color: #c8e6c9; border-radius: 3px;">
                        ✓ <strong>{estimation_data['correct_unit']}</strong> - CORRECT (matches magnitude)
                    </li>
                    <li style="padding: 8px; margin: 5px 0; background-color: #ffcccc; border-radius: 3px;">
                        ✗ {estimation_data['wrong_units'][0]} - Too extreme
                    </li>
                    {f'<li style="padding: 8px; margin: 5px 0; background-color: #ffcccc; border-radius: 3px;">✗ {estimation_data["wrong_units"][1]} - Inappropriate scale</li>' if len(estimation_data.get('wrong_units', [])) > 1 else ''}
                </ul>
            </div>
            
            <div style="background-color: #fff3e0; padding: 10px; margin: 10px 0; border-left: 4px solid #ff9800;">
                <strong>Remember:</strong> {estimation_data['reasoning']}
            </div>
        </div>
        """
        
        return {"html": html_content}

