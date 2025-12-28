"""Strategy for Chapter 13: Ways to Multiply/Divide - Different Calculation Strategies."""

import random
from typing import List
from models.question import Question, ChapterEnum
from models.distractor import MisconceptionType, TrapType
from models.cognitive_levels import BloomLevel
from strategies.base import BaseChapterStrategy


class MultiplicationDivisionStrategy(BaseChapterStrategy):
    """Generate questions for different multiplication and division strategies."""
    
    chapter = ChapterEnum.MULTIPLICATION_DIVISION
    chapter_name = "Chapter 13: Ways to Multiply/Divide"
    description = "Different calculation strategies for multiplication and division"
    
    def generate(self) -> Question:
        """Generate a random multiplication/division question from available types."""
        question_type = random.choice([
            self._generate_lattice_multiplication,
            self._generate_grid_multiplication,
            self._generate_long_division_steps,
            self._generate_division_with_remainder,
            self._generate_strategy_selection,
            self._generate_estimation_before_calc
        ])
        return question_type()
    
    def _generate_lattice_multiplication(self) -> Question:
        """Lattice multiplication method.
        
        Student solves using lattice grid method.
        """
        num1 = random.randint(12, 25)
        num2 = random.randint(13, 24)
        correct_answer = str(num1 * num2)
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: str(num1 * 10 + num2 * 10),  # Only tens
            MisconceptionType.ARITHMETIC_ERROR: str(num1 * num2 + random.choice([10, 20, 30])),  # Off by constant
            MisconceptionType.OPERATION_SELECTION: str(num1 + num2)  # Addition instead
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets to include ones place in lattice calculation",
            custom_why_effective="Lattice method requires tracking multiple partial products",
            custom_how_to_avoid="Carefully add each diagonal line in lattice grid"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        lattice_visual = self._create_lattice_visual(num1, num2)
        
        question = Question(
            chapter=self.chapter,
            topic="Lattice Multiplication Method",
            logical_trap="Student misses partial products or forgets to add diagonals",
            data_representation=lattice_visual,
            question_text=f"Using the lattice method, what is {num1} × {num2}?",
            solution_steps=[
                f"Set up lattice grid for {num1} (digits) × {num2} (digits)",
                f"Multiply each digit pair and write in cells",
                f"Add along diagonals from right to left",
                f"Read result: {correct_answer}"
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
    
    def _generate_grid_multiplication(self) -> Question:
        """Grid/area multiplication method.
        
        Break numbers into place values and multiply (distributive property).
        """
        num1 = random.randint(12, 30)
        num2 = random.randint(11, 25)
        correct_answer = str(num1 * num2)
        
        # Break into tens and ones
        tens1 = (num1 // 10) * 10
        ones1 = num1 % 10
        tens2 = (num2 // 10) * 10
        ones2 = num2 % 10
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: str(tens1 * tens2),  # Only tens multiplication
            MisconceptionType.OPERATION_SELECTION: str(tens1 * tens2 + ones1 + ones2),  # Partial calculation
            MisconceptionType.ARITHMETIC_ERROR: str(num1 * num2 - 5)  # Off by small amount
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets ones × ones or ones × tens products",
            custom_why_effective="4 partial products need to be calculated and added",
            custom_how_to_avoid="Always calculate all 4 boxes: (tens×tens), (tens×ones), (ones×tens), (ones×ones)"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        grid_visual = self._create_area_grid_visual(tens1, ones1, tens2, ones2)
        
        question = Question(
            chapter=self.chapter,
            topic="Grid/Area Multiplication",
            logical_trap="Student forgets to calculate all 4 partial products",
            data_representation=grid_visual,
            question_text=f"Using the grid method, what is {num1} × {num2}?",
            solution_steps=[
                f"Break {num1} into tens ({tens1}) and ones ({ones1})",
                f"Break {num2} into tens ({tens2}) and ones ({ones2})",
                f"Calculate 4 products:",
                f"  • {tens1} × {tens2} = {tens1 * tens2}",
                f"  • {ones1} × {tens2} = {ones1 * tens2}",
                f"  • {tens1} × {ones2} = {tens1 * ones2}",
                f"  • {ones1} × {ones2} = {ones1 * ones2}",
                f"Sum all: {tens1 * tens2} + {ones1 * tens2} + {tens1 * ones2} + {ones1 * ones2} = {correct_answer}"
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
    
    def _generate_long_division_steps(self) -> Question:
        """Long division with detailed steps.
        
        Student identifies correct step-by-step process.
        """
        dividend = random.randint(100, 500)
        divisor = random.randint(5, 15)
        
        # Ensure clean division for simplicity
        while dividend % divisor != 0:
            dividend = random.randint(100, 500)
        
        quotient = dividend // divisor
        correct_answer = str(quotient)
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: str(quotient - 1),  # Off by one
            MisconceptionType.OPERATION_SELECTION: str(dividend - divisor),  # Subtraction instead
            MisconceptionType.ARITHMETIC_ERROR: str(dividend // (divisor + 1))  # Wrong divisor
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student makes error in one step of long division",
            custom_why_effective="Long division has multiple steps; one error propagates",
            custom_how_to_avoid="Check each step: divide, multiply, subtract, bring down, repeat"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        division_visual = self._create_division_visual(dividend, divisor, quotient)
        
        question = Question(
            chapter=self.chapter,
            topic="Long Division Steps",
            logical_trap="Student makes arithmetic error in one step of division process",
            data_representation=division_visual,
            question_text=f"What is {dividend} ÷ {divisor}?",
            solution_steps=[
                f"Set up: {dividend} ÷ {divisor}",
                f"How many times does {divisor} go into first digits of {dividend}?",
                f"Work through each step: divide, multiply, subtract, bring down",
                f"Continue until complete division",
                f"Quotient: {correct_answer}"
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
    
    def _generate_division_with_remainder(self) -> Question:
        """Division with remainder.
        
        Student must identify quotient and remainder separately.
        """
        dividend = random.randint(50, 200)
        divisor = random.randint(5, 15)
        
        quotient = dividend // divisor
        remainder = dividend % divisor
        
        # Ensure there IS a remainder
        while remainder == 0:
            dividend = random.randint(50, 200)
            quotient = dividend // divisor
            remainder = dividend % divisor
        
        correct_answer = f"{quotient} R {remainder}"
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: str(quotient),  # Ignores remainder
            MisconceptionType.CONSTRAINT_VIOLATION: str(remainder),  # Only remainder
            MisconceptionType.OPERATION_SELECTION: f"{dividend}/{divisor}"  # Fraction instead of division
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student finds quotient but ignores the remainder",
            custom_why_effective="Remainder is 'leftover' - easy to forget in real contexts",
            custom_how_to_avoid="Always check if there's remainder after dividing"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        division_visual = f"{dividend} ÷ {divisor} = {quotient} with {remainder} left over"
        
        question = Question(
            chapter=self.chapter,
            topic="Division with Remainders",
            logical_trap="Student forgets remainder or ignores 'leftover' in real-world context",
            data_representation=division_visual,
            question_text=f"Divide: {dividend} ÷ {divisor} (write quotient and remainder)",
            solution_steps=[
                f"Dividend: {dividend}, Divisor: {divisor}",
                f"{divisor} goes into {dividend} exactly {quotient} times",
                f"Check: {divisor} × {quotient} = {divisor * quotient}",
                f"Remainder: {dividend} - {divisor * quotient} = {remainder}",
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
    
    def _generate_strategy_selection(self) -> Question:
        """Student selects most efficient strategy.
        
        'Which method would be fastest for 25 × 4?'
        """
        num1 = random.choice([12, 15, 20, 25, 50])
        num2 = random.choice([2, 4, 5, 10])
        
        # Determine fastest strategy
        if num2 in [2, 5, 10]:
            fastest = "Mental Math"
        else:
            fastest = "Grid Method"
        
        correct_answer = fastest
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.OPERATION_SELECTION: ("Long Multiplication" if fastest != "Long Multiplication" else "Grid Method"),
            MisconceptionType.INCOMPLETE_REASONING: "Lattice Method",
            MisconceptionType.CONSTRAINT_VIOLATION: "Calculator"
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.OPERATION_SELECTION,
            difficulty=3,
            custom_description="Student doesn't recognize when to use efficient mental strategies",
            custom_why_effective="All methods work; students don't always see when one is faster",
            custom_how_to_avoid="Look for patterns: multiplying by 2, 5, 10 has shortcuts"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.ANALYZE, trap_difficulty=3)
        
        question = Question(
            chapter=self.chapter,
            topic="Strategy Selection",
            logical_trap="Student uses inefficient method when faster strategy exists",
            data_representation=f"Solve: {num1} × {num2}",
            question_text=f"Which is the fastest method to calculate {num1} × {num2}?",
            solution_steps=[
                f"Looking at {num1} × {num2}",
                f"Notice {num2} is special (power of 2, 5, or 10)",
                f"Mental math: {num1} × {num2} = {num1 * num2}",
                f"Fastest method: {fastest}"
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
    
    def _generate_estimation_before_calc(self) -> Question:
        """Estimate before calculating.
        
        'Without calculating exactly, is 24 × 38 closer to 600, 800, or 1000?'
        """
        num1 = random.randint(15, 40)
        num2 = random.randint(15, 40)
        
        exact = num1 * num2
        
        # Create nearby estimates
        estimates = []
        for offset in [-200, -100, 0, 100, 200]:
            estimate = (exact // 100) * 100 + offset
            if estimate > 0:
                estimates.append(estimate)
        
        # Find closest
        closest = min(estimates, key=lambda x: abs(x - exact))
        correct_answer = str(closest)
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: str(num1 * 10 + num2 * 10),  # Add instead of multiply
            MisconceptionType.ARITHMETIC_ERROR: str(closest + 100),  # Off by 100
            MisconceptionType.CONSTRAINT_VIOLATION: str(abs(exact - closest) * 2)  # Difference instead
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=3,
            custom_description="Student doesn't round numbers before estimating product",
            custom_why_effective="Estimation requires rounding; students skip this step",
            custom_how_to_avoid="Always round to nearest 10 or 100, then multiply rounded numbers"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.ANALYZE, trap_difficulty=3)
        
        question = Question(
            chapter=self.chapter,
            topic="Estimation Before Calculation",
            logical_trap="Student doesn't round before estimating product",
            data_representation=f"Estimate: {num1} × {num2}\nOptions: {', '.join(map(str, [closest, closest + 100, closest - 100]))}",
            question_text=f"Without calculating exactly, what is {num1} × {num2} closest to?",
            solution_steps=[
                f"Round {num1} to nearest 10: {(num1 // 10) * 10}",
                f"Round {num2} to nearest 10: {(num2 // 10) * 10}",
                f"Multiply rounded: {(num1 // 10) * 10} × {(num2 // 10) * 10} = {((num1 // 10) * 10) * ((num2 // 10) * 10)}",
                f"Closest estimate: {correct_answer}",
                f"(Exact answer: {exact})"
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
    def _create_lattice_visual(num1: int, num2: int) -> str:
        """Create ASCII lattice grid."""
        digits1 = list(str(num1))
        digits2 = list(str(num2))
        
        visual = "Lattice Grid:\n"
        visual += "    " + "  ".join(digits2) + "\n"
        
        for d1 in digits1:
            row = f"{d1}  "
            for d2 in digits2:
                prod = int(d1) * int(d2)
                tens = prod // 10
                ones = prod % 10
                if tens == 0:
                    row += f"[0|{ones}] "
                else:
                    row += f"[{tens}|{ones}] "
            visual += row + "\n"
        
        return visual
    
    @staticmethod
    def _create_area_grid_visual(t1: int, o1: int, t2: int, o2: int) -> str:
        """Create area grid for multiplication."""
        visual = f"\n     {t2:3d}    {o2:3d}\n"
        visual += f"{t1:3d} [{t1*t2:4d}]  [{t1*o2:4d}]\n"
        visual += f"{o1:3d} [{o1*t2:4d}]  [{o1*o2:4d}]\n"
        return visual
    
    @staticmethod
    def _create_division_visual(dividend: int, divisor: int, quotient: int) -> str:
        """Create long division representation."""
        visual = f"\n      {quotient}\n"
        visual += f"    -------\n"
        visual += f"{divisor} | {dividend}\n"
        visual += f"      {divisor * quotient}\n"
        visual += f"      -------\n"
        visual += f"        {dividend % divisor}\n"
        return visual
    
    def _validate_question(self, question: Question) -> None:
        """Validate question has all required fields."""
        assert question.question_text
        assert question.answer
        assert len(question.options) == 4
        assert 0 <= question.correct_option_index < 4
        assert question.distractor_info
        assert question.trap_info
        assert question.bloom_info
