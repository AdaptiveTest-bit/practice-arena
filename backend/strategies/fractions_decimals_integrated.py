"""
FRACTIONS & DECIMALS - INTEGRATED STRATEGY
==========================================

Hybrid Neuro-Symbolic approach for Fractions & Decimals

Integrates:
1. SymPy fraction arithmetic (Rational for exact fraction operations)
2. K.C. Nag real-world scenarios (culturally relevant storytelling)
3. Misconception-based distractors (Denominator addition, Magnitude confusion)
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
from sympy import Rational, gcd as sympy_gcd, simplify

# Import hybrid system components
from content.generators.fractions_decimals import (
    FractionsDecimalsGenerator,
    FractionConcept,
    DifficultyLevel as HybridDifficultyLevel,
)


class FractionsDecimalsIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic sympy logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.FRACTIONS_DECIMALS
    chapter_name = "Fractions & Decimals"
    description = "Fractions & Decimals with hybrid neuro-symbolic approach"
    
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
            "simplify_fraction",
            "convert_to_decimal",
            "order_fractions_decimals",
        ])
        
        if problem_type == "simplify_fraction":
            return self._generate_fraction_simplification()
        elif problem_type == "convert_to_decimal":
            return self._generate_convert_to_decimal()
        else:  # order_fractions_decimals
            return self._generate_order_fractions_decimals()
    
    def _generate_fraction_simplification(self) -> Question:
        """
        Fraction Simplification - Using SymPy for mathematical guarantee
        
        PHASE 1: Deterministic Skeleton (SymPy Rational for exact arithmetic)
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton with SymPy
        # ===========================================
        # Generate a fraction that can be simplified
        denominator = random.choice([4, 6, 8, 9, 10, 12, 15, 18, 20])
        
        # Create reducible fractions
        reduction_factors = {
            4: [2],           # 2/4 → 1/2
            6: [2, 3],        # 2/6 → 1/3, 3/6 → 1/2
            8: [2, 4],        # 2/8 → 1/4, 4/8 → 1/2
            9: [3],           # 3/9 → 1/3
            10: [2, 5],       # 2/10 → 1/5, 5/10 → 1/2
            12: [2, 3, 4, 6], # 2/12 → 1/6, 3/12 → 1/4, 4/12 → 1/3, 6/12 → 1/2
            15: [3, 5],       # 3/15 → 1/5, 5/15 → 1/3
            18: [2, 3, 6, 9], # 2/18 → 1/9, 3/18 → 1/6, 6/18 → 1/3, 9/18 → 1/2
            20: [2, 4, 5, 10],# 2/20 → 1/10, 4/20 → 1/5, 5/20 → 1/4, 10/20 → 1/2
        }
        
        factor = random.choice(reduction_factors[denominator])
        numerator = factor
        
        # Use SymPy Rational for guaranteed correct simplification
        fraction = Rational(numerator, denominator)
        correct_num = fraction.p  # Numerator of simplified fraction
        correct_den = fraction.q  # Denominator of simplified fraction
        correct_answer = f"{correct_num}/{correct_den}"
        
        # Get GCD using SymPy for consistency
        g = int(sympy_gcd(numerator, denominator))
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"You have {numerator} pieces of a chocolate bar broken into {denominator} equal pieces. Simplify the fraction.",
            f"A recipe needs {numerator}/{denominator} cup of flour. Simplify to the simplest form.",
            f"You've completed {numerator}/{denominator} of your homework. Write in simplest form.",
            f"{numerator} out of {denominator} students prefer tea. Express as simplified fraction.",
            f"A cloth is cut into {denominator} equal parts. You use {numerator} parts. Simplify.",
        ])
        
        character = random.choice(["Ravi", "Priya", "Anaya", "Rohan"])
        misconception_hook = random.choice([
            "forgot to check if it can be reduced",
            "thought denominator can only go down",
            "didn't use GCD properly",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Not reducing at all (value stays same)
        wrong_options.append((
            f"{numerator}/{denominator}",
            MisconceptionType.FORMULA_CONFUSION,
            "Not reduced",
            "This fraction is not in simplest form because both numerator and denominator share a common factor",
            "Always find the GCD of numerator and denominator and divide both by it"
        ))
        
        # Misconception 2: Partially reduced (dividing by wrong GCD)
        partial_reduction = random.choice([2, 3, 5]) if g > 2 else 2
        if numerator > partial_reduction and denominator > partial_reduction:
            partial_num = numerator // partial_reduction
            partial_den = denominator // partial_reduction
            if int(sympy_gcd(partial_num, partial_den)) != 1:  # Ensure not fully reduced
                wrong_options.append((
                    f"{partial_num}/{partial_den}",
                    MisconceptionType.INCOMPLETE_REASONING,
                    "Partially reduced",
                    "You divided by a factor, but not the GCD. The fraction can still be reduced further.",
                    "The GCD (Greatest Common Divisor) of numerator and denominator must divide both completely"
                ))
        
        # Misconception 3: Inverted or wrong operation
        if correct_num != 1:
            inverted = f"{correct_den}/{correct_num}"
            wrong_options.append((
                inverted,
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Inverted fraction",
                "You flipped the numerator and denominator, changing the meaning completely.",
                "Keep numerator on top and denominator on bottom - they represent different quantities"
            ))
        else:
            # Wrong GCD application
            alt_factors = [f for f in reduction_factors.get(denominator, [2]) if f != g]
            if alt_factors:
                wrong_gcd = random.choice(alt_factors)
                wrong_num = numerator // wrong_gcd if numerator % wrong_gcd == 0 else numerator
                wrong_den = denominator // wrong_gcd if denominator % wrong_gcd == 0 else denominator
                wrong_options.append((
                    f"{wrong_num}/{wrong_den}",
                    MisconceptionType.FORMULA_CONFUSION,
                    "Wrong GCD",
                    "You used a common factor instead of the GREATEST common factor.",
                    "Keep dividing both numerator and denominator by common factors until no more factors work"
                ))
            else:
                # Fallback: use a simple wrong answer
                wrong_options.append((
                    f"{numerator + 1}/{denominator}",
                    MisconceptionType.INCOMPLETE_REASONING,
                    "Off by one",
                    "You modified the numerator slightly but didn't simplify correctly.",
                    "Always find the GCD first, then divide both numerator and denominator by it"
                ))
        
        # Ensure we have at least 3 wrong options
        while len(wrong_options) < 3:
            wrong_options.append((
                f"{numerator * 2}/{denominator * 2}",
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Multiplied both sides",
                "You multiplied instead of dividing. This changes the value!",
                "Simplification means dividing both by common factors, not multiplying"
            ))        
        # Ensure we have at least 3 wrong options
        while len(wrong_options) < 3:
            wrong_options.append((
                "1/1",
                MisconceptionType.INCOMPLETE_REASONING,
                "Invalid option",
                "This is a placeholder for insufficient distractors.",
                "There should be multiple choice options available."
            ))
        

        
        # Shuffle distractors
        random.shuffle(wrong_options)
        
        # Prepare options and distractor info
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Find GCD({numerator}, {denominator})",
            f"GCD = {g}",
            f"Divide numerator: {numerator} ÷ {g} = {correct_num}",
            f"Divide denominator: {denominator} ÷ {g} = {correct_den}",
            f"Simplified form: {correct_num}/{correct_den}"
        ]
        
        visual_diagram = self._render_simplification_grid(numerator, denominator, correct_num, correct_den)
        
        hints = [
            f"Hint 1: Look for common factors of {numerator} and {denominator}",
            f"Hint 2: The largest common factor is {g}",
            f"Hint 3: Divide both numerator and denominator by {g}",
            f"Hint 4: The simplified form has no common factors between numerator and denominator"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Fraction Simplification",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Always simplify to lowest terms by dividing by GCD.",
            data_representation="Fraction bar with divided sections",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s question: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_convert_to_decimal(self) -> Question:
        """
        Convert Fraction to Decimal
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Select fractions that convert to "nice" decimals
        fraction_pairs = [
            (1, 2, 0.5),    # 1/2 = 0.5
            (1, 4, 0.25),   # 1/4 = 0.25
            (3, 4, 0.75),   # 3/4 = 0.75
            (1, 5, 0.2),    # 1/5 = 0.2
            (2, 5, 0.4),    # 2/5 = 0.4
            (3, 5, 0.6),    # 3/5 = 0.6
            (4, 5, 0.8),    # 4/5 = 0.8
            (1, 8, 0.125),  # 1/8 = 0.125
            (3, 8, 0.375),  # 3/8 = 0.375
            (5, 8, 0.625),  # 5/8 = 0.625
            (7, 8, 0.875),  # 7/8 = 0.875
            (1, 10, 0.1),   # 1/10 = 0.1
            (3, 10, 0.3),   # 3/10 = 0.3
            (7, 10, 0.7),   # 7/10 = 0.7
        ]
        
        num, den, correct_decimal = random.choice(fraction_pairs)
        correct_answer = str(correct_decimal)
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A shopkeeper sells items at {num}/{den} of the original price. Express as decimal for the billing system.",
            f"You scored {num}/{den} marks in a test. Convert to decimal form.",
            f"The weight of an item is {num}/{den} kilograms. Write as decimal.",
            f"A water tank is filled to {num}/{den} capacity. What is the decimal representation?",
            f"{num}/{den} of the class participated in the event. Express as decimal percentage.",
        ])
        
        character = random.choice(["Meera", "Vikram", "Sneha", "Arjun"])
        misconception_hook = random.choice([
            "didn't know how to convert properly",
            "confused the decimal point placement",
            "used the fraction numbers directly as decimal",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Direct fraction read as decimal (most common)
        direct_read = f"0.{num}{den}"
        wrong_options.append((
            direct_read,
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Direct digit reading",
            f"You read {num} and {den} as consecutive digits after decimal, but {num}/{den} doesn't equal 0.{num}{den}",
            "Use division: {num} ÷ {den} to find the decimal, not digit-by-digit reading"
        ))
        
        # Misconception 2: Swapped numerator/denominator
        if num != den:
            swapped_decimal = round(den / num, 3)
            wrong_options.append((
                str(swapped_decimal),
                MisconceptionType.FORMULA_CONFUSION,
                "Swapped fraction",
                f"You inverted the fraction to {den}/{num} instead of {num}/{den}",
                "Keep the original fraction order: numerator (top) divided by denominator (bottom)"
            ))
        
        # Misconception 3: Magnitude confusion (forgot decimal point or shifted)
        magnitude_wrong = random.choice([
            int(num * 10 / den) / 10,  # Shifted decimal place
            (num / den) * 10 if (num / den) < 1 else (num / den),  # Magnified
        ])
        if magnitude_wrong != correct_decimal and magnitude_wrong > 0:
            wrong_options.append((
                str(magnitude_wrong),
                MisconceptionType.INCOMPLETE_REASONING,
                "Magnitude error",
                f"The decimal value {magnitude_wrong} is not equal to {num}/{den}",
                "Perform the actual division: {num} ÷ {den} carefully to get the correct decimal"
            ))
        
        # Ensure we have 3 wrong options
        while len(wrong_options) < 3:
            wrong_val = round(random.uniform(0.1, 0.9), 2)
            if str(wrong_val) not in [opt[0] for opt in wrong_options] and wrong_val != correct_decimal:
                wrong_options.append((
                    str(wrong_val),
                    MisconceptionType.CONSTRAINT_VIOLATION,
                    "Random guess",
                    f"{wrong_val} is not the correct decimal for {num}/{den}",
                    f"Divide: {num} ÷ {den} = {correct_decimal}"
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
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Start with fraction: {num}/{den}",
            f"Perform division: {num} ÷ {den}",
            f"Decimal result: {correct_decimal}",
            f"Verification: {correct_decimal} × {den} = {num} ✓"
        ]
        
        visual_diagram = self._render_decimal_conversion(num, den, correct_decimal)
        
        hints = [
            f"Hint 1: The line in a fraction means 'divide'",
            f"Hint 2: You need to divide {num} by {den}",
            f"Hint 3: {num} ÷ {den} = ?",
            f"Hint 4: The decimal form has {len(str(correct_decimal).split('.')[-1])} decimal places"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Fraction to Decimal Conversion",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Divide numerator by denominator to get decimal.",
            data_representation="Number line showing fraction and decimal equivalence",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s conversion problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_order_fractions_decimals(self) -> Question:
        """
        Order Fractions and Decimals
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Create 3 numbers (mix of fractions and decimals)
        number_pool = [
            (0.5, "0.5"),
            (0.25, "0.25"),
            (0.75, "0.75"),
            (0.2, "0.2"),
            (0.4, "0.4"),
            (0.6, "0.6"),
            (0.8, "0.8"),
            (1/3, "1/3"),
            (2/3, "2/3"),
            (1/6, "1/6"),
            (5/6, "5/6"),
        ]
        
        selected_numbers = random.sample(number_pool, 3)
        selected_numbers_sorted = sorted(selected_numbers, key=lambda x: x[0])
        
        correct_answer = ", ".join([num[1] for num in selected_numbers_sorted])
        order_format = " < ".join([num[1] for num in selected_numbers_sorted])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Arrange these prices in increasing order: {', '.join([num[1] for num in selected_numbers])} rupees",
            f"Students scored different fractions on a test: {', '.join([num[1] for num in selected_numbers])}. Order from lowest to highest.",
            f"Three water containers are filled to levels: {', '.join([num[1] for num in selected_numbers])}. Which is most full?",
            f"Pizzas left after parties: {', '.join([num[1] for num in selected_numbers])}. Order from least to most.",
            f"Three measurements in meters: {', '.join([num[1] for num in selected_numbers])}. Order from smallest to largest.",
        ])
        
        character = random.choice(["Dev", "Priya", "Ananya", "Karan"])
        misconception_hook = random.choice([
            "thought decimal must be smaller than fractions",
            "compared only the digits, not their values",
            "confused the denominator's effect",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        # Generate wrong orderings
        wrong_orderings = []
        
        # Misconception 1: Reversed order
        reversed_order = ", ".join([num[1] for num in selected_numbers_sorted[::-1]])
        wrong_orderings.append((
            reversed_order,
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Reversed order",
            "You arranged them from largest to smallest, but the question asks for ascending (smallest to largest)",
            "Always arrange in ascending order: smallest first, then increasing values"
        ))
        
        # Misconception 2: Decimal-first misconception (thinking decimals < fractions)
        decimal_first = []
        fractions = []
        for num, display in selected_numbers:
            if '.' in display:
                decimal_first.append((num, display))
            else:
                fractions.append((num, display))
        
        if decimal_first and fractions:
            # Put all decimals before all fractions (wrong)
            wrong_order_2 = decimal_first + fractions
            wrong_orderings.append((
                ", ".join([num[1] for num in wrong_order_2]),
                MisconceptionType.FORMULA_CONFUSION,
                "Decimals before fractions",
                "You grouped decimals together and fractions together, but you must compare actual values",
                "Convert all to decimals to compare: 1/2 = 0.5, 2/3 ≈ 0.667, etc."
            ))
        
        # Misconception 3: Comparing only denominator (for fractions) or first digit (for decimals)
        # This creates a nonsensical order based on wrong logic
        if len(wrong_orderings) < 3:
            random_shuffle = random.sample(selected_numbers, 3)
            wrong_orderings.append((
                ", ".join([num[1] for num in random_shuffle]),
                MisconceptionType.INCOMPLETE_REASONING,
                "Random comparison",
                f"This order doesn't correctly compare the values",
                f"Compare actual decimal values: {', '.join([f'{num[1]}={num[0]:.3f}' for num in selected_numbers_sorted])}"
            ))
        
        random.shuffle(wrong_orderings)
        
        # Prepare options
        all_options = [correct_answer] + [opt[0] for opt in wrong_orderings[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_orderings):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_orderings[wrong_count][0],
                    misconception_type=wrong_orderings[wrong_count][1],
                    description=wrong_orderings[wrong_count][2],
                    why_wrong=wrong_orderings[wrong_count][3],
                    teaching_point=wrong_orderings[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Convert all to decimals:",
        ]
        for num, display in selected_numbers:
            solution_steps.append(f"  {display} = {num:.4f}")
        solution_steps.append(f"Compare decimal values:")
        solution_steps.append(f"  {selected_numbers_sorted[0][0]:.4f} < {selected_numbers_sorted[1][0]:.4f} < {selected_numbers_sorted[2][0]:.4f}")
        solution_steps.append(f"Therefore: {order_format}")
        
        visual_diagram = self._render_ordering_number_line(
            [num[0] for num in selected_numbers],
            [num[1] for num in selected_numbers]
        )
        
        hints = [
            f"Hint 1: Convert all fractions to decimals for easy comparison",
            f"Hint 2: Place each value on a number line from 0 to 1",
            f"Hint 3: The leftmost value is smallest, rightmost is largest",
            f"Hint 4: Correct order should use '<' symbols between increasing values"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Ordering Fractions and Decimals",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Always convert to same form (decimals) to compare.",
            data_representation="Number line from 0 to 1",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s ordering problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question


    # ==================== HELPER RENDERING METHODS ====================
    
    def _render_simplification_grid(self, num: int, den: int, simplified_num: int, simplified_den: int) -> Dict[str, str]:
        """
        Render grid representation of fraction simplification
        Shows original fraction divided into den parts with num shaded,
        then shows reduction to simplified form
        """
        from math import gcd
        g = gcd(num, den)
        
        # Create visual grid for original fraction
        grid_size = min(den, 12)  # Limit grid size for visualization
        shaded = int((num / den) * grid_size)
        
        grid_html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Simplifying {num}/{den}</h4>
            
            <div style="margin: 15px 0;">
                <strong>Original Fraction:</strong>
                <div style="display: flex; gap: 4px; margin: 8px 0; flex-wrap: wrap;">
        """
        
        for i in range(grid_size):
            color = "#4CAF50" if i < shaded else "#e0e0e0"
            grid_html += f'<div style="width: 20px; height: 20px; background: {color}; border: 1px solid #333;"></div>'
        
        grid_html += f"""
                </div>
                <p>{num} shaded out of {den} parts = <strong>{num}/{den}</strong></p>
            </div>
            
            <div style="margin: 15px 0; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                <strong>Step 1:</strong> Find GCD({num}, {den}) = {g}
                <br><strong>Step 2:</strong> Divide both by {g}:
                <br>&nbsp;&nbsp;&nbsp;&nbsp;{num} ÷ {g} = {simplified_num}
                <br>&nbsp;&nbsp;&nbsp;&nbsp;{den} ÷ {g} = {simplified_den}
                <br><strong>Simplified:</strong> {num}/{den} = <span style="color: #d32f2f; font-weight: bold;">{simplified_num}/{simplified_den}</span>
            </div>
        </div>
        """
        
        return {"html": grid_html}
    
    def _render_decimal_conversion(self, num: int, den: int, decimal: float) -> Dict[str, str]:
        """
        Render division process and decimal visualization
        Shows the long division and number line placement
        """
        html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Converting {num}/{den} to Decimal</h4>
            
            <div style="margin: 15px 0; padding: 10px; background: #fff3e0; border-left: 4px solid #ff9800;">
                <strong>Division Process:</strong>
                <div style="font-family: monospace; margin: 8px 0;">
                    {num} ÷ {den} = {decimal}
                </div>
            </div>
            
            <div style="margin: 15px 0;">
                <strong>Number Line Representation:</strong>
                <div style="width: 100%; height: 40px; position: relative; border: 1px solid #333; margin: 8px 0; background: #f0f0f0;">
                    <div style="position: absolute; width: 2%; height: 100%; left: 0%; background: #333;"></div>
                    <div style="position: absolute; width: 2%; height: 100%; left: 100%; transform: translateX(-100%); background: #333;"></div>
                    <div style="position: absolute; width: 1px; height: 100%; left: 50%; background: #ddd;"></div>
                    
                    <div style="position: absolute; top: -20px; left: 0%; transform: translateX(-50%); font-size: 12px;">0</div>
                    <div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: 12px;">0.5</div>
                    <div style="position: absolute; top: -20px; left: 100%; transform: translateX(-50%); font-size: 12px;">1</div>
                    
                    <div style="position: absolute; top: 50%; left: {decimal*100}%; transform: translate(-50%, -50%); width: 12px; height: 12px; background: #d32f2f; border-radius: 50%; border: 2px solid #b71c1c;"></div>
                    <div style="position: absolute; top: -40px; left: {decimal*100}%; transform: translateX(-50%); font-weight: bold; color: #d32f2f;">
                        {decimal}
                    </div>
                </div>
            </div>
            
            <div style="margin: 15px 0; padding: 10px; background: #e8f5e9; border-left: 4px solid #4CAF50;">
                <strong>Verification:</strong> {decimal} × {den} = {decimal * den} ✓
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_ordering_number_line(self, values: List[float], labels: List[str]) -> Dict[str, str]:
        """
        Render number line with marked positions for ordering
        Shows all numbers positioned on 0-1 scale
        """
        # Sort for display
        sorted_pairs = sorted(zip(values, labels), key=lambda x: x[0])
        
        html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Ordering on Number Line</h4>
            
            <div style="margin: 20px 0;">
                <strong>Number Line (0 to 1):</strong>
                <div style="width: 100%; height: 50px; position: relative; border: 2px solid #333; margin: 20px 0; background: #f0f0f0;">
                    <div style="position: absolute; width: 2px; height: 100%; left: 0%; background: #333;"></div>
                    <div style="position: absolute; width: 2px; height: 100%; left: 100%; transform: translateX(-100%); background: #333;"></div>
                    
                    <div style="position: absolute; top: -25px; left: 0%; transform: translateX(-50%); font-size: 12px; font-weight: bold;">0</div>
                    <div style="position: absolute; top: -25px; left: 100%; transform: translateX(-50%); font-size: 12px; font-weight: bold;">1</div>
        """
        
        colors = ["#e91e63", "#2196F3", "#4CAF50", "#ff9800"]
        for idx, (value, label) in enumerate(sorted_pairs):
            position = value * 100
            color = colors[idx % len(colors)]
            html += f"""
                    <div style="position: absolute; top: 50%; left: {position}%; transform: translate(-50%, -50%); width: 16px; height: 16px; background: {color}; border-radius: 50%; border: 2px solid #333;"></div>
                    <div style="position: absolute; top: -50px; left: {position}%; transform: translateX(-50%); font-weight: bold; color: {color}; font-size: 14px;">
                        {label}
                    </div>
            """
        
        html += """
                </div>
            </div>
            
            <div style="margin: 15px 0; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                <strong>Correct Order (Left to Right):</strong>
                <br>"""
        
        html += " < ".join([label for _, label in sorted_pairs])
        html += """
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