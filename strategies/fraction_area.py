"""Strategy for Chapter 3: How Many Squares - Visual Fraction Understanding."""

import random
from typing import List
from models.question import Question, ChapterEnum
from models.distractor import MisconceptionType, TrapType
from models.cognitive_levels import BloomLevel
from strategies.base import BaseChapterStrategy


class FractionAreaStrategy(BaseChapterStrategy):
    """Generate questions for visual fraction understanding using grids."""
    
    chapter = ChapterEnum.FRACTION_AREA
    chapter_name = "Chapter 3: How Many Squares"
    description = "Visual fractions using grid/square representations"
    
    def generate(self) -> Question:
        """Generate a random fraction question from available types."""
        question_type = random.choice([
            self._generate_fraction_identification,
            self._generate_multiple_parts_addition,
            self._generate_equivalent_fractions,
            self._generate_part_to_whole,
            self._generate_fraction_comparison,
            self._generate_fraction_decomposition
        ])
        return question_type()
    
    def _generate_fraction_identification(self) -> Question:
        """Identify fraction from grid representation.
        
        Student sees grid with shaded squares and identifies the fraction.
        """
        # Generate random grid and shading
        total_squares = random.choice([4, 9, 16, 25])
        shaded = random.randint(1, total_squares - 1)
        
        # Calculate correct answer
        from math import gcd
        g = gcd(shaded, total_squares)
        numerator = shaded // g
        denominator = total_squares // g
        correct_answer = f"{numerator}/{denominator}"
        
        # PHASE 1: Create misconception-mapped distractors
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{shaded}/{shaded}",  # Only numerator
            MisconceptionType.OPERATION_SELECTION: f"{total_squares - shaded}/{total_squares}",  # Complement
            MisconceptionType.CONSTRAINT_VIOLATION: f"{shaded}/{total_squares - shaded}"  # Inverted parts
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Create trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Student counts shaded squares but forgets total",
            custom_why_effective="The shaded number is visible and memorable",
            custom_how_to_avoid="Always count both shaded AND total squares"
        )
        
        # PHASE 3: Create bloom info
        bloom_info = self.create_bloom_info(BloomLevel.REMEMBER, trap_difficulty=1)
        
        # Create visual representation
        grid_visual = self._create_grid_visual(total_squares, shaded)
        
        question = Question(
            chapter=self.chapter,
            topic="Fraction Identification from Grid",
            logical_trap="Student only counts shaded squares, ignoring the total",
            data_representation=grid_visual,
            question_text=f"What fraction of the grid is shaded?",
            solution_steps=[
                f"Count shaded squares: {shaded}",
                f"Count total squares: {total_squares}",
                f"Write as fraction: {shaded}/{total_squares}",
                f"Simplify by dividing both by {g}: {numerator}/{denominator}"
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
    
    def _generate_multiple_parts_addition(self) -> Question:
        """Add multiple fraction parts that sum to total.
        
        Parts of grid are different colors; student identifies sum.
        """
        total_squares = random.choice([8, 12, 16])
        
        # Create two non-overlapping parts
        part1 = random.randint(1, total_squares // 2)
        part2 = random.randint(1, total_squares - part1)
        sum_parts = part1 + part2
        
        from math import gcd
        g = gcd(sum_parts, total_squares)
        numerator = sum_parts // g
        denominator = total_squares // g
        correct_answer = f"{numerator}/{denominator}"
        
        # PHASE 1: Misconception mapping
        misconception_map = {
            MisconceptionType.OPERATION_SELECTION: f"{part1 + part2}/{part1 + part2}",  # Sum only
            MisconceptionType.INCOMPLETE_REASONING: f"{part1}/{total_squares}",  # Only first part
            MisconceptionType.ARITHMETIC_ERROR: f"{part1 + part2}/{total_squares + 1}"  # Wrong total
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.OPERATION_SELECTION,
            difficulty=2,
            custom_description="Student adds parts but forgets to show as fraction of total",
            custom_why_effective="Adding is obvious; making fraction is often forgotten",
            custom_how_to_avoid="Always place sum over total in fraction form"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        grid_visual = self._create_colored_grid_visual(total_squares, [(part1, "red"), (part2, "blue")])
        
        question = Question(
            chapter=self.chapter,
            topic="Adding Fraction Parts",
            logical_trap="Student adds numerators but doesn't create proper fraction",
            data_representation=grid_visual,
            question_text=f"What fraction is colored red or blue together?",
            solution_steps=[
                f"Red squares: {part1}",
                f"Blue squares: {part2}",
                f"Total colored: {part1} + {part2} = {sum_parts}",
                f"Fraction: {sum_parts}/{total_squares} = {numerator}/{denominator}"
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
    
    def _generate_equivalent_fractions(self) -> Question:
        """Identify equivalent fraction from grid.
        
        Two different grid sizes show same amount shaded.
        """
        # Create base fraction
        base_numerator = random.choice([1, 2, 3])
        base_denominator = random.choice([2, 3, 4, 5])
        
        if base_numerator >= base_denominator:
            base_numerator = base_denominator - 1
        
        # Generate equivalent by multiplying
        multiplier = random.choice([2, 3, 4])
        equivalent_num = base_numerator * multiplier
        equivalent_den = base_denominator * multiplier
        
        correct_answer = f"{equivalent_num}/{equivalent_den}"
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.SIMILAR_CONCEPT_ERROR: f"{base_numerator + multiplier}/{base_denominator + multiplier}",  # Adding
            MisconceptionType.OPERATION_SELECTION: f"{equivalent_num - 1}/{equivalent_den}",  # Off by one
            MisconceptionType.INCOMPLETE_REASONING: f"{base_numerator}/{base_denominator}"  # Original fraction only
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.SIMILAR_CONCEPT_ERROR,
            difficulty=2,
            custom_description="Student confuses multiplying with adding",
            custom_why_effective="Adding feels more natural to elementary students",
            custom_how_to_avoid="Check: multiply numerator AND denominator by same number"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        grid1 = self._create_grid_visual(base_denominator, base_numerator)
        grid2 = self._create_grid_visual(equivalent_den, equivalent_num)
        
        question = Question(
            chapter=self.chapter,
            topic="Equivalent Fractions",
            logical_trap="Student adds instead of multiplying to find equivalent fraction",
            data_representation=f"{grid1}\n\n{grid2}",
            question_text=f"The second grid shows an equivalent fraction to {base_numerator}/{base_denominator}. What is it?",
            solution_steps=[
                f"First grid shows {base_numerator}/{base_denominator} shaded",
                f"Second grid is {multiplier}x larger",
                f"Multiply numerator: {base_numerator} × {multiplier} = {equivalent_num}",
                f"Multiply denominator: {base_denominator} × {multiplier} = {equivalent_den}",
                f"Equivalent fraction: {equivalent_num}/{equivalent_den}"
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
    
    def _generate_part_to_whole(self) -> Question:
        """Find whole when given part and fraction.
        
        'If shaded part is 3 squares and that's 1/4 of grid, how many total squares?'
        """
        total = random.choice([8, 12, 16, 20])
        denominator = random.randint(2, 5)
        
        while total % denominator != 0:
            denominator = random.randint(2, 5)
        
        numerator = 1
        part_value = (numerator * total) // denominator
        
        correct_answer = str(total)
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: str(part_value),  # Only the part
            MisconceptionType.OPERATION_DIRECTION: str(part_value * denominator),  # Wrong multiplication
            MisconceptionType.CONSTRAINT_VIOLATION: str(total - part_value)  # Complement
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=3,
            custom_description="Student forgets to reverse calculation to find whole",
            custom_why_effective="Given the part; forgetting to multiply is natural error",
            custom_how_to_avoid="If 1/n of whole is X, then whole = X × n"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=3)
        
        grid_visual = self._create_grid_visual(total, part_value)
        
        question = Question(
            chapter=self.chapter,
            topic="Finding Whole from Part",
            logical_trap="Student only remembers the given part, not the relationship",
            data_representation=f"{grid_visual}\n(Shaded squares = {part_value})",
            question_text=f"The shaded region shows {numerator}/{denominator} of the whole grid. How many total squares are there?",
            solution_steps=[
                f"Given: {numerator}/{denominator} of grid = {part_value} squares",
                f"If {numerator}/{denominator} = {part_value}, then 1/{denominator} = {part_value}",
                f"Whole grid = {denominator}/{denominator} = {part_value} × {denominator} = {total}"
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
    
    def _generate_fraction_comparison(self) -> Question:
        """Compare two fractions shown as grid parts.
        
        'Which is bigger: shaded in grid A or grid B?'
        """
        # Create two comparable fractions
        frac1_num = random.randint(1, 3)
        frac1_den = random.choice([3, 4, 5])
        while frac1_num >= frac1_den:
            frac1_num = random.randint(1, 3)
        
        frac2_num = random.randint(1, 3)
        frac2_den = random.choice([3, 4, 5])
        while frac2_num >= frac2_den or frac2_den == frac1_den:
            frac2_den = random.choice([3, 4, 5])
        
        # Calculate decimal values to determine which is bigger
        val1 = frac1_num / frac1_den
        val2 = frac2_num / frac2_den
        
        if val1 > val2:
            correct_answer = "A"
            bigger_num, bigger_den = frac1_num, frac1_den
            smaller_num, smaller_den = frac2_num, frac2_den
        else:
            correct_answer = "B"
            bigger_num, bigger_den = frac2_num, frac2_den
            smaller_num, smaller_den = frac1_num, frac1_den
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: ("B" if correct_answer == "A" else "A"),  # Reversed
            MisconceptionType.CONSTRAINT_VIOLATION: "Equal",  # False equivalence
            MisconceptionType.OPERATION_SELECTION: ("Cannot compare" if correct_answer != "Cannot compare" else "A")
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student reverses comparison or ignores denominators",
            custom_why_effective="Comparing fractions requires careful analysis",
            custom_how_to_avoid="Convert to same denominator or decimal to compare"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        grid_a = self._create_grid_visual(frac1_den, frac1_num)
        grid_b = self._create_grid_visual(frac2_den, frac2_num)
        
        question = Question(
            chapter=self.chapter,
            topic="Comparing Fractions with Grids",
            logical_trap="Student doesn't systematically compare or reverses order",
            data_representation=f"Grid A: {grid_a}\n\nGrid B: {grid_b}",
            question_text=f"Which grid has more shaded area?",
            solution_steps=[
                f"Grid A: {frac1_num}/{frac1_den} = {val1:.3f}",
                f"Grid B: {frac2_num}/{frac2_den} = {val2:.3f}",
                f"Comparing: {val1:.3f} vs {val2:.3f}",
                f"Answer: Grid {correct_answer} is {'bigger' if val1 > val2 else 'bigger'}"
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
    
    def _generate_fraction_decomposition(self) -> Question:
        """Decompose fraction into smaller unit fractions.
        
        'Show 2/3 as sum of unit fractions (1/3 + 1/3)'
        """
        numerator = random.choice([2, 3, 4])
        denominator = random.choice([3, 4, 5])
        
        while numerator >= denominator:
            numerator = random.choice([2, 3])
        
        # Decomposition: n/d = (1/d) + (1/d) + ... n times
        unit_fraction = f"1/{denominator}"
        correct_answer = " + ".join([unit_fraction] * numerator)
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{numerator}/{denominator}",  # Just original
            MisconceptionType.OPERATION_SELECTION: f"1/{denominator} × {numerator}",  # Multiplication form
            MisconceptionType.CONSTRAINT_VIOLATION: " + ".join([f"1/{denominator + 1}"] * numerator)  # Wrong unit fraction
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=3,
            custom_description="Student doesn't break fraction into unit parts",
            custom_why_effective="Decomposition requires understanding unit fractions",
            custom_how_to_avoid="Always show as sum of unit fractions: 1/d added n times"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=3)
        
        grid_visual = self._create_grid_visual(denominator, numerator)
        
        question = Question(
            chapter=self.chapter,
            topic="Fraction Decomposition",
            logical_trap="Student shows fraction but not as sum of unit fractions",
            data_representation=grid_visual,
            question_text=f"Decompose {numerator}/{denominator} as a sum of unit fractions:",
            solution_steps=[
                f"Numerator: {numerator} (how many parts)",
                f"Denominator: {denominator} (size of each part)",
                f"Unit fraction: 1/{denominator}",
                f"Decomposition: 1/{denominator} + 1/{denominator} + ... ({numerator} times)",
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
    
    # ============================================================================
    # VISUALIZATION HELPERS
    # ============================================================================
    
    @staticmethod
    def _create_grid_visual(total: int, shaded: int) -> str:
        """Create ASCII grid visualization."""
        cols = int(total ** 0.5) if total in [4, 9, 16, 25] else min(4, total)
        rows = (total + cols - 1) // cols
        
        grid = []
        count = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                if count < total:
                    if count < shaded:
                        row.append("■")
                    else:
                        row.append("□")
                    count += 1
            grid.append(" ".join(row))
        
        return "\n".join(grid)
    
    @staticmethod
    def _create_colored_grid_visual(total: int, parts: List[tuple]) -> str:
        """Create grid with different colored parts."""
        cols = int(total ** 0.5) if total in [4, 9, 16, 25] else min(4, total)
        rows = (total + cols - 1) // cols
        
        grid = []
        count = 0
        part_dict = {}
        
        for part_count, color in parts:
            for i in range(part_count):
                part_dict[count] = color[0].upper()
                count += 1
        
        count = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                if count < total:
                    if count in part_dict:
                        row.append(part_dict[count])
                    else:
                        row.append("□")
                    count += 1
            grid.append(" ".join(row))
        
        return "\n".join(grid)
    
    def _validate_question(self, question: Question) -> None:
        """Validate question has all required fields."""
        assert question.question_text
        assert question.answer
        assert len(question.options) == 4
        assert 0 <= question.correct_option_index < 4
        assert question.distractor_info
        assert question.trap_info
        assert question.bloom_info
