"""
FRACTION AREA - INTEGRATED STRATEGY
===================================

Hybrid Neuro-Symbolic approach for Fraction Area

Integrates:
1. Visual with grid representation
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Equal parts assumption, Nesting confusion)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorSet, DistractorInfo
import random
from typing import List, Tuple, Dict, Any


class FractionAreaIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic visual logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.FRACTION_AREA
    chapter_name = "Fraction Area"
    description = "Fraction Area with hybrid neuro-symbolic approach"
    
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
            "fraction_of_area",
            "equal_parts_verification",
            "fraction_of_fraction",
        ])
        
        if problem_type == "fraction_of_area":
            return self._generate_fraction_of_area()
        elif problem_type == "equal_parts_verification":
            return self._generate_equal_parts_verification()
        else:  # fraction_of_fraction
            return self._generate_fraction_of_fraction()
    
    def _generate_fraction_of_area(self) -> Question:
        """
        Fraction Of Area - What fraction is shaded?
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters (grid size, shaded cells)
        - Calculate correct fraction
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        # Generate a grid with some cells shaded
        grid_sizes = [4, 6, 8, 10, 12]  # Total cells in grid
        grid_size = random.choice(grid_sizes)
        
        # Choose how many cells to shade (must divide evenly for nice fractions)
        divisors = [d for d in range(1, grid_size) if grid_size % d == 0]
        numerator = random.choice(divisors)
        denominator = grid_size
        
        # Reduce fraction to simplest form
        from math import gcd
        g = gcd(numerator, denominator)
        simplified_num = numerator // g
        simplified_den = denominator // g
        correct_answer = f"{simplified_num}/{simplified_den}"
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A chocolate bar is divided into {grid_size} equal pieces. {numerator} pieces are already eaten. What fraction of the chocolate is eaten?",
            f"A garden is divided into {grid_size} equal plots. {numerator} plots are planted with flowers. What fraction has flowers?",
            f"A pizza is cut into {grid_size} equal slices. {numerator} slices are served. What fraction is served?",
            f"A cloth is divided into {grid_size} equal patches. {numerator} patches are dyed. What fraction is dyed?",
        ])
        
        # PHASE 3: Misconception-based distractors
        # Common mistake: using unreduced fractions, wrong numerator/denominator order
        wrong_answer_1 = f"{numerator}/{grid_size}"  # Not reduced
        wrong_answer_2 = f"{grid_size - numerator}/{grid_size}"  # Unshaded instead of shaded
        wrong_answer_3 = f"{denominator}/{simplified_num}"  # Numerator/denominator swapped
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct fraction in simplest form",
                None,
                None
            ),
            1: (
                wrong_answer_1,
                MisconceptionType.FORMULA_CONFUSION,
                "Used unreduced fraction",
                "Student didn't simplify the fraction to lowest terms",
                f"Always simplify fractions. {numerator}/{grid_size} = {simplified_num}/{simplified_den} after dividing by {g}."
            ),
            2: (
                wrong_answer_2,
                MisconceptionType.INCOMPLETE_REASONING,
                "Counted unshaded instead of shaded",
                "Student counted the part NOT shaded instead of the shaded part",
                f"The question asks for SHADED fraction. Shaded = {numerator} out of {grid_size} = {correct_answer}"
            ),
            3: (
                wrong_answer_3,
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Swapped numerator and denominator",
                "Student put denominator as numerator (upside-down fraction)",
                "Fraction = shaded parts / total parts. NOT total parts / shaded parts."
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = opt_val
            
            if misconception is None:
                correct_idx = display_idx
            
            distractor_info_list.append(DistractorInfo(
                value=opt_val,
                misconception_type=misconception or MisconceptionType.INCOMPLETE_REASONING,
                description=desc,
                why_wrong=why_wrong or "Correct",
                teaching_point=teaching or "Well done!"
            ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.FORMULA_CONFUSION,
            difficulty=1,
            custom_description="Not reducing fractions to simplest form",
            custom_why_effective="Students often forget the simplification step",
            custom_how_to_avoid="After finding the fraction, divide both numerator and denominator by their GCD."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        steps = [
            f"Total cells in grid: {grid_size}",
            f"Shaded cells: {numerator}",
            f"Fraction: {numerator}/{grid_size}",
            f"GCD of {numerator} and {grid_size}: {g}",
            f"Simplified: {simplified_num}/{simplified_den}",
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = self._render_fraction_grid(grid_size, numerator, correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Fraction Area - Identify Fraction",
            logical_trap="K.C. Nag Trap: Students often forget to simplify fractions to their lowest terms. They may also confuse which part is shaded vs unshaded.",
            data_representation=f"```\nGrid: {grid_size} cells\nShaded: {numerator} cells\nFraction: ?\n```",
            question_text=f"A grid has {grid_size} equal cells. {numerator} cells are shaded. What fraction of the grid is shaded? (Give answer in simplest form)",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: To find a fraction, count the shaded parts (numerator) and total parts (denominator). Always simplify by dividing both by their GCD.",
            visual_hints=[
                f"Count shaded cells: {numerator}",
                f"Count total cells: {grid_size}",
                f"Fraction before simplification: {numerator}/{grid_size}",
                f"Simplify to: {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _generate_equal_parts_verification(self) -> Question:
        """
        Equal Parts Verification - Are parts equal?
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters
        - Determine if parts are equal
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        # Show a shape divided into parts - are they equal?
        scenarios = [
            {
                "description": "A rectangle divided by lines",
                "parts": 4,
                "equal": random.choice([True, False]),
                "visual": "rectangle with horizontal/vertical lines"
            },
            {
                "description": "A circle divided into sections",
                "parts": 6,
                "equal": random.choice([True, False]),
                "visual": "circle with radial divisions"
            },
            {
                "description": "A square divided into parts",
                "parts": 4,
                "equal": random.choice([True, False]),
                "visual": "square with grid pattern"
            },
        ]
        
        scenario = random.choice(scenarios)
        correct_answer = "Yes" if scenario["equal"] else "No"
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A pizza is cut into {scenario['parts']} pieces. Are all the pieces the same size?",
            f"A cake is divided into {scenario['parts']} parts. Are the parts equal?",
            f"A field is divided into {scenario['parts']} sections. Do the sections have equal area?",
            f"A piece of cloth is cut into {scenario['parts']} pieces. Are all pieces the same?",
        ])
        
        # PHASE 3: Misconception-based distractors
        # Common mistake: thinking parts LOOK similar enough, not checking carefully
        opposite = "No" if correct_answer == "Yes" else "Yes"
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct answer about equality",
                None,
                None
            ),
            1: (
                opposite,
                MisconceptionType.INCOMPLETE_REASONING,
                "Didn't check carefully",
                "Student didn't measure or compare all parts systematically",
                f"To verify equal parts, check that EVERY part has the SAME area. Not just 'close enough'."
            ),
            2: (
                "Partially",
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Gave a non-definitive answer",
                "Student wasn't sure about the equality criteria",
                "Equal parts means EXACTLY the same area. Either yes or no - not 'kind of'."
            ),
            3: (
                "Cannot determine",
                MisconceptionType.FORMULA_CONFUSION,
                "Gave up without analyzing",
                "Student didn't attempt to compare the parts",
                "Compare parts systematically: count grid squares, measure angles, check dimensions."
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = opt_val
            
            if misconception is None:
                correct_idx = display_idx
            
            distractor_info_list.append(DistractorInfo(
                value=opt_val,
                misconception_type=misconception or MisconceptionType.INCOMPLETE_REASONING,
                description=desc,
                why_wrong=why_wrong or "Correct",
                teaching_point=teaching or "Well done!"
            ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Not systematically comparing part areas",
            custom_why_effective="Students assume parts are equal without careful measurement",
            custom_how_to_avoid="Count squares or measure dimensions to verify EVERY part is exactly equal."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        steps = [
            f"Shape: {scenario['description']}",
            f"Number of parts: {scenario['parts']}",
            "Check if each part has the same area",
            f"Conclusion: Parts are {'' if scenario['equal'] else 'NOT '}equal"
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = self._render_equal_parts_verification(scenario['description'], scenario['equal'])
        
        question = Question(
            chapter=self.chapter,
            topic="Fraction Area - Equal Parts",
            logical_trap="K.C. Nag Trap: Students often assume parts are equal without careful verification. They may think parts that LOOK similar are actually equal.",
            data_representation=f"```\nShape: {scenario['description']}\nDivided into: {scenario['parts']} parts\nAre parts equal?\n```",
            question_text=f"{scenario['description']} divided into {scenario['parts']} parts. Are all parts equal in area?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Equal parts means EXACTLY the same area. Before using a shape for fractions, always verify that all parts are equal by counting or measuring.",
            visual_hints=[
                f"Look at all {scenario['parts']} parts",
                "Compare their sizes carefully",
                "Count grid squares or measure dimensions",
                f"Are they EXACTLY equal? {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _generate_fraction_of_fraction(self) -> Question:
        """
        Fraction Of Fraction - Shade a fraction of an already-fractioned area
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters
        - Calculate correct result
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        # A fraction is divided, then we shade a fraction of that
        # Example: 1/2 of the rectangle is red. Shade 1/3 of the red part.
        # What fraction of the whole is shaded?
        
        fractions = [
            ("1/2", 1, 2),
            ("1/3", 1, 3),
            ("1/4", 1, 4),
            ("2/3", 2, 3),
            ("3/4", 3, 4),
        ]
        
        first_frac_name, first_num, first_den = random.choice(fractions)
        second_frac_name, second_num, second_den = random.choice(fractions)
        
        # Result is (num1 * num2) / (den1 * den2)
        from math import gcd
        result_num = first_num * second_num
        result_den = first_den * second_den
        g = gcd(result_num, result_den)
        result_simplified_num = result_num // g
        result_simplified_den = result_den // g
        correct_answer = f"{result_simplified_num}/{result_simplified_den}"
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A chocolate bar is {first_frac_name} dark chocolate. Of the dark chocolate, {second_frac_name} has nuts. What fraction of the whole bar is dark chocolate with nuts?",
            f"A garden is {first_frac_name} planted with flowers. Of the flower section, {second_frac_name} has red flowers. What fraction of the whole garden has red flowers?",
            f"A pizza is {first_frac_name} pepperoni. Of the pepperoni section, {second_frac_name} has extra cheese. What fraction of the whole pizza has both?",
        ])
        
        # PHASE 3: Misconception-based distractors
        # Common mistake: adding fractions instead of multiplying, not reducing
        wrong_answer_1 = f"{first_num + second_num}/{first_den + second_den}"  # Added instead of multiplied
        wrong_answer_2 = f"{result_num}/{result_den}"  # Not reduced
        wrong_answer_3 = f"{second_frac_name}"  # Only remembered second fraction
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct result of fraction multiplication",
                None,
                None
            ),
            1: (
                wrong_answer_1,
                MisconceptionType.FORMULA_CONFUSION,
                "Added fractions instead of multiplying",
                "Student added numerators and denominators instead of multiplying them",
                f"To find a fraction OF a fraction, MULTIPLY: ({first_num}/{first_den}) × ({second_num}/{second_den}) = {result_num}/{result_den} = {correct_answer}"
            ),
            2: (
                wrong_answer_2,
                MisconceptionType.INCOMPLETE_REASONING,
                "Didn't simplify the result",
                "Student multiplied correctly but forgot to reduce to lowest terms",
                f"Multiply the fractions: {result_num}/{result_den}, then simplify by dividing by {g}: {correct_answer}"
            ),
            3: (
                wrong_answer_3,
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Only remembered the second fraction",
                "Student ignored the first fraction and only reported the second",
                f"You need BOTH fractions. First: {first_frac_name} of the whole. Second: {second_frac_name} OF THAT. Result: {correct_answer}"
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = opt_val
            
            if misconception is None:
                correct_idx = display_idx
            
            distractor_info_list.append(DistractorInfo(
                value=opt_val,
                misconception_type=misconception or MisconceptionType.INCOMPLETE_REASONING,
                description=desc,
                why_wrong=why_wrong or "Correct",
                teaching_point=teaching or "Well done!"
            ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.FORMULA_CONFUSION,
            difficulty=3,
            custom_description="Confusing fraction multiplication with addition",
            custom_why_effective="Students incorrectly try to add fractions when multiplication is needed",
            custom_how_to_avoid="'Of' means multiply: 1/2 of 1/3 = (1/2) × (1/3) = 1/6. Always multiply numerators and denominators."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=3)
        
        steps = [
            f"First fraction: {first_frac_name}",
            f"Second fraction (OF the first): {second_frac_name}",
            f"Multiply: ({first_num}/{first_den}) × ({second_num}/{second_den}) = {result_num}/{result_den}",
            f"Simplify by GCD {g}: {correct_answer}",
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = self._render_fraction_of_fraction(first_frac_name, second_frac_name, correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Fraction Area - Fraction of Fraction",
            logical_trap="K.C. Nag Trap: Students often add fractions instead of multiplying when finding a fraction OF another fraction. 'Of' means multiply, not add!",
            data_representation=f"```\nFirst fraction: {first_frac_name}\nSecond fraction of first: {second_frac_name}\nResult: ?\n```",
            question_text=f"Find {second_frac_name} of {first_frac_name}. What fraction of the whole is this? (Give answer in simplest form)",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: When finding a fraction OF another fraction, MULTIPLY them. 'Of' in math means ×. Always simplify the result.",
            visual_hints=[
                f"First fraction: {first_frac_name}",
                f"Shade {second_frac_name} of that part",
                f"Multiply the fractions: ({first_num}/{first_den}) × ({second_num}/{second_den}) = {result_num}/{result_den}",
                f"Simplify to: {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question


    # ==================== HELPER METHODS ====================
    
    def _render_fraction_grid(self, grid_size: int, shaded: int, fraction: str) -> str:
        """
        Render HTML visual representation of fraction grid
        
        Args:
            grid_size: Total number of cells
            shaded: Number of shaded cells
            fraction: Fraction in simplest form
            
        Returns:
            HTML string with grid visual
        """
        html = f"""
<div style='border:2px solid #2196F3; border-radius:8px; padding:15px; background:#e3f2fd;'>
    <h4 style='color:#1976D2; margin-top:0;'>Fraction Grid</h4>
    
    <div style='background:white; padding:10px; border-left:4px solid #2196F3; color:#333; margin-bottom:10px;'>
        <p style='margin:5px 0;'><strong>Total cells:</strong> {grid_size}</p>
        <p style='margin:5px 0;'><strong>Shaded cells:</strong> {shaded}</p>
        <p style='margin:5px 0;'><strong>Fraction:</strong> {shaded}/{grid_size}</p>
        <p style='margin:5px 0;'><strong>Simplified:</strong> {fraction}</p>
    </div>
    
    <p style='background:#fff9c4; padding:10px; border-left:4px solid #FBC02D; color:#000;'>
        <strong>Remember:</strong> Always simplify fractions by dividing both numerator and denominator by their GCD.
    </p>
</div>
"""
        return html
    
    def _render_equal_parts_verification(self, shape_desc: str, are_equal: bool) -> str:
        """
        Render HTML visual for equal parts verification
        
        Args:
            shape_desc: Description of the shape
            are_equal: Whether parts are equal
            
        Returns:
            HTML string with diagram
        """
        result_text = "YES - all parts are equal" if are_equal else "NO - parts are NOT equal"
        result_color = "#4CAF50" if are_equal else "#f44336"
        
        html = f"""
<div style='border:2px solid {result_color}; border-radius:8px; padding:15px; background:#f5f5f5;'>
    <h4 style='color:{result_color}; margin-top:0;'>Equal Parts Verification</h4>
    
    <div style='background:white; padding:10px; border-left:4px solid {result_color}; color:#333; margin-bottom:10px;'>
        <p style='margin:5px 0;'><strong>Shape:</strong> {shape_desc}</p>
        <p style='margin:5px 0;'><strong>Are parts equal?</strong></p>
        <p style='font-size:18px; color:{result_color}; font-weight:bold;'>{result_text}</p>
    </div>
    
    <p style='background:#c8e6c9; padding:10px; border-left:4px solid #388E3C; color:#1b5e20;'>
        <strong>Key point:</strong> Equal parts means EXACTLY the same area. Check by counting squares or measuring.
    </p>
</div>
"""
        return html
    
    def _render_fraction_of_fraction(self, first_frac: str, second_frac: str, result: str) -> str:
        """
        Render HTML visual for fraction of fraction
        
        Args:
            first_frac: First fraction
            second_frac: Second fraction
            result: Result fraction
            
        Returns:
            HTML string with diagram
        """
        html = f"""
<div style='border:2px solid #FF9800; border-radius:8px; padding:15px; background:#fff3e0;'>
    <h4 style='color:#E65100; margin-top:0;'>Fraction of Fraction</h4>
    
    <div style='background:white; padding:10px; border-left:4px solid #FF9800; color:#333; margin-bottom:10px;'>
        <p style='margin:5px 0;'><strong>First fraction:</strong> {first_frac}</p>
        <p style='margin:5px 0;'><strong>Take {second_frac} of that:</strong></p>
        <p style='margin:5px 0;'><strong>Result:</strong> {first_frac} × {second_frac} = {result}</p>
    </div>
    
    <p style='background:#f3e5f5; padding:10px; border-left:4px solid #7B1FA2; color:#4a148c;'>
        <strong>Remember:</strong> "Of" means multiply! {first_frac} of {second_frac} = {first_frac} × {second_frac} = {result}
        </p>
</div>
"""
        return html
    
    # ==================== SVG RENDERING METHODS ====================
    
    def _render_fraction_grid_svg(self, grid_size: int, shaded_count: int, label: str = "Shaded") -> str:
        """
        Render SVG grid showing fraction visualization
        
        Args:
            grid_size: Total number of cells in grid
            shaded_count: Number of shaded cells
            label: Label for shaded cells
            
        Returns:
            HTML string with SVG grid diagram
        """
        # Calculate grid dimensions (as square as possible)
        import math
        cols = int(math.ceil(math.sqrt(grid_size)))
        rows = int(math.ceil(grid_size / cols))
        
        cell_size = 30
        padding = 10
        svg_width = cols * cell_size + 2 * padding
        svg_height = rows * cell_size + 2 * padding
        
        # Generate grid cells
        cells_svg = ""
        shaded = set(random.sample(range(grid_size), shaded_count))
        
        for i in range(grid_size):
            row = i // cols
            col = i % cols
            x = padding + col * cell_size
            y = padding + row * cell_size
            
            if i in shaded:
                # Shaded cell
                cells_svg += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="#4CAF50" stroke="#2E7D32" stroke-width="1"/>'
            else:
                # Empty cell
                cells_svg += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="white" stroke="#ccc" stroke-width="1"/>'
        
        # Calculate fraction
        from fractions import Fraction
        frac = Fraction(shaded_count, grid_size)
        
        html = f"""
<div style="border:2px solid #2196F3; border-radius:8px; padding:15px; background:#e3f2fd; text-align:center;">
    <h4 style="color:#1976D2; margin-top:0;">Fraction Grid</h4>
    
    <svg width="{svg_width}" height="{svg_height}" style="border:2px solid #1976D2; background:white; display:inline-block; margin:10px 0;">
        {cells_svg}
    </svg>
    
    <p style="font-size:18px; font-weight:bold; color:#1976D2; margin:10px 0;">
        Shaded: {shaded_count} out of {grid_size} = <span style="color:#4CAF50;">{frac}</span>
    </p>
    
    <p style="background:white; padding:10px; border-left:4px solid #4CAF50; color:#333; text-align:left; font-size:13px;">
        <strong>How to read this fraction:</strong><br>
        <span style="color:#4CAF50;"><strong>{shaded_count}</strong></span> <strong style="color:#2E7D32;">shaded squares</strong> (numerator)<br>
        <strong>÷</strong><br>
        <span style="color:#1976D2;"><strong>{grid_size}</strong></span> <strong style="color:#1565C0;">total squares</strong> (denominator)<br>
        <strong>=</strong> <span style="font-size:16px; font-weight:bold; color:#4CAF50;">{frac}</span>
    </p>
</div>
"""
        return html
    
    # ==================== UTILITY METHODS ====================
    
    def _difficulty_level_to_int(self, difficulty: str) -> int:
        """Convert difficulty string to 1-5 scale"""
        mapping = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
            "expert": 4,
        }
        return mapping.get(difficulty.lower(), 2) if difficulty else 2
