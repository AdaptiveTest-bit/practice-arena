"""Fractions and Decimals question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
import random
from models.distractor import MisconceptionType
from fractions import Fraction


class FractionsDecimalsStrategy(BaseChapterStrategy):
    """Generates fractions, decimals, and related problems."""
    
    chapter = ChapterEnum.FRACTIONS_DECIMALS
    chapter_name = "Fractions & Decimals"
    description = "Fraction and decimal operations"
    
    def generate(self) -> Question:
        """Generate a fractions/decimals question."""
        problem_type = random.choice([
            "fraction_comparison",
            "fraction_addition",
            "fraction_multiplication",
            "decimal_conversion",
            "decimal_comparison",
            "mixed_operations",
            "equivalent_fractions_unlike",
            "improper_to_mixed",
            "unit_fractions",
            "fraction_subtraction"
        ])
        
        if problem_type == "fraction_comparison":
            return self._generate_fraction_comparison()
        elif problem_type == "fraction_addition":
            return self._generate_fraction_addition()
        elif problem_type == "fraction_multiplication":
            return self._generate_fraction_multiplication()
        elif problem_type == "decimal_conversion":
            return self._generate_decimal_conversion()
        elif problem_type == "decimal_comparison":
            return self._generate_decimal_comparison()
        elif problem_type == "mixed_operations":
            return self._generate_mixed_operations()
        elif problem_type == "equivalent_fractions_unlike":
            return self._generate_equivalent_fractions_unlike()
        elif problem_type == "improper_to_mixed":
            return self._generate_improper_to_mixed()
        elif problem_type == "unit_fractions":
            return self._generate_unit_fractions()
        else:
            return self._generate_fraction_subtraction()
    
    def _generate_fraction_comparison(self) -> Question:
        """Compare two fractions."""
        pairs = [
            ("1/2", "2/4", "="),
            ("3/4", "2/3", ">"),
            ("1/5", "1/3", "<"),
            ("5/6", "4/5", ">"),
            ("2/3", "3/4", "<"),
        ]
        
        f1, f2, symbol = random.choice(pairs)
        correct_answer = f"{f1} {symbol} {f2}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        wrong_symbols = [s for s in [">", "<", "="] if s != symbol]
        misconception_map = {
            MisconceptionType.OPERATION_SELECTION: 
                f"{f1} {wrong_symbols[0]} {f2}",  # Wrong comparison operator
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{f1} {wrong_symbols[1]} {f2}",  # Other wrong operator
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Cannot compare"  # Refuses to compare
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Numbers - Fraction Comparison",
            logical_trap="K.C. Nag trap: Students compare denominators instead of finding common denominator.",
            data_representation=f"```\nFraction 1: {f1}\nFraction 2: {f2}\nCommon denominator method\n"
                               f"{f1} = {Fraction(f1).numerator * 3}/{Fraction(f1).denominator * 3}\n```",
            question_text=f"Which symbol makes this true? {f1} ___ {f2}",
            solution_steps=[
                f"Fractions: {f1} and {f2}",
                "Find common denominator",
                f"Convert and compare",
                f"Answer: {symbol}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.OPERATION_SELECTION, difficulty=1),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_fraction_addition(self) -> Question:
        """Add two fractions."""
        num1, denom1 = random.randint(1, 3), random.randint(3, 8)
        num2, denom2 = random.randint(1, 3), random.randint(3, 8)
        
        f1 = Fraction(num1, denom1)
        f2 = Fraction(num2, denom2)
        result = f1 + f2
        
        correct_answer = f"{result.numerator}/{result.denominator}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPERATION_SELECTION:
                f"{num1 + num2}/{denom1 + denom2}",  # Adding numerators and denominators directly
            MisconceptionType.INCOMPLETE_REASONING:
                f"{num1}/{denom1}",  # First fraction only
            MisconceptionType.ARITHMETIC_ERROR:
                f"{num2}/{denom2}"  # Second fraction only
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Numbers - Fraction Addition",
            logical_trap="Students add numerators and denominators separately instead of using common denominator.",
            data_representation=f"```\nFraction 1: {num1}/{denom1}\nFraction 2: {num2}/{denom2}\n"
                               f"Common denominator: {denom1 * denom2 // 2 if denom1 != denom2 else denom1}\nSum: {result}\n```",
            question_text=f"What is {num1}/{denom1} + {num2}/{denom2}?",
            solution_steps=[
                f"{num1}/{denom1} + {num2}/{denom2}",
                f"Common denominator: {result.denominator if result.denominator < 24 else denom1 * denom2}",
                f"Convert fractions",
                f"Add numerators",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.OPERATION_SELECTION, difficulty=1),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_fraction_multiplication(self) -> Question:
        """Multiply two fractions."""
        num1, denom1 = random.randint(1, 4), random.randint(2, 6)
        num2, denom2 = random.randint(1, 4), random.randint(2, 6)
        
        f1 = Fraction(num1, denom1)
        f2 = Fraction(num2, denom2)
        result = f1 * f2
        
        correct_answer = f"{result.numerator}/{result.denominator}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING:
                f"{num1 * num2}/{denom1 * denom2}",  # Without simplifying
            MisconceptionType.OPERATION_SELECTION:
                f"{num1}/{denom2}",  # Cross terms
            MisconceptionType.CONSTRAINT_VIOLATION:
                f"{(num1 + num2)}/{(denom1 + denom2)}"  # Addition instead
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Numbers - Fraction Multiplication",
            logical_trap="K.C. Nag trap: Students forget to simplify after multiplying numerators and denominators.",
            data_representation=f"```\nFraction 1: {num1}/{denom1}\nFraction 2: {num2}/{denom2}\n"
                               f"Product: ({num1}×{num2})/({denom1}×{denom2}) = {num1*num2}/{denom1*denom2}\nSimplified: {result}\n```",
            question_text=f"What is {num1}/{denom1} × {num2}/{denom2}?",
            solution_steps=[
                f"{num1}/{denom1} × {num2}/{denom2}",
                f"Multiply numerators: {num1} × {num2} = {num1*num2}",
                f"Multiply denominators: {denom1} × {denom2} = {denom1*denom2}",
                f"Result: {num1*num2}/{denom1*denom2}",
                f"Simplify: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.OPERATION_SELECTION, difficulty=1),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_decimal_conversion(self) -> Question:
        """Convert fraction to decimal."""
        pairs = [
            ("1/2", "0.5"),
            ("1/4", "0.25"),
            ("3/4", "0.75"),
            ("1/5", "0.2"),
            ("2/5", "0.4"),
            ("1/10", "0.1"),
        ]
        
        fraction, decimal = random.choice(pairs)
        correct_answer = decimal
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR:
                str(round(float(Fraction(fraction)) + 0.1, 2)),  # Off by 0.1
            MisconceptionType.INCOMPLETE_REASONING:
                str(round(float(Fraction(fraction)) - 0.1, 2)),  # Off by -0.1
            MisconceptionType.OPERATION_SELECTION:
                str(round(Fraction(fraction).denominator / Fraction(fraction).numerator, 2))  # Inverted division
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Numbers - Fraction to Decimal",
            logical_trap="Students don't know how to divide numerator by denominator correctly.",
            data_representation=f"```\nFraction: {fraction}\nDivide: {Fraction(fraction).numerator} ÷ {Fraction(fraction).denominator}\nDecimal: {decimal}\n```",
            question_text=f"Convert {fraction} to a decimal.",
            solution_steps=[
                f"Fraction: {fraction}",
                f"Numerator: {Fraction(fraction).numerator}",
                f"Denominator: {Fraction(fraction).denominator}",
                f"Divide: {Fraction(fraction).numerator} ÷ {Fraction(fraction).denominator}",
                f"Decimal: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.OPERATION_SELECTION, difficulty=1),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_decimal_comparison(self) -> Question:
        """Compare two decimals."""
        dec1 = round(random.uniform(0.1, 0.9), 2)
        dec2 = round(random.uniform(0.1, 0.9), 2)
        
        if dec1 > dec2:
            symbol = ">"
        elif dec1 < dec2:
            symbol = "<"
        else:
            symbol = "="
        
        correct_answer = f"{dec1} {symbol} {dec2}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        wrong_symbols = [s for s in [">", "<", "="] if s != symbol]
        misconception_map = {
            MisconceptionType.OPERATION_SELECTION:
                f"{dec1} {wrong_symbols[0]} {dec2}",  # Wrong comparison operator
            MisconceptionType.INCOMPLETE_REASONING:
                f"{dec1} {wrong_symbols[1]} {dec2}",  # Other wrong operator
            MisconceptionType.CONSTRAINT_VIOLATION:
                "Cannot compare"  # Refuses to compare
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Numbers - Decimal Comparison",
            logical_trap="K.C. Nag trap: Students ignore decimal places and compare only whole numbers.",
            data_representation=f"```\nDecimal 1: {dec1}\nDecimal 2: {dec2}\nPlace values: tenths, hundredths\n```",
            question_text=f"Which symbol makes this true? {dec1} ___ {dec2}",
            solution_steps=[
                f"Compare: {dec1} and {dec2}",
                "Check tenths place first",
                f"Then check hundredths place",
                f"Answer: {symbol}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.OPERATION_SELECTION, difficulty=1),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_mixed_operations(self) -> Question:
        """Mixed fraction and decimal operations."""
        operation = random.choice([
            ("1/2 + 0.25", 0.75),
            ("0.5 × 2/4", 0.25),
            ("3/4 - 0.2", 0.55),
            ("0.6 + 1/5", 0.8),
        ])
        
        expr, answer_val = operation
        correct_answer = str(answer_val)
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR:
                str(round(answer_val + 0.1, 2)),  # Off by 0.1
            MisconceptionType.INCOMPLETE_REASONING:
                str(round(answer_val - 0.1, 2)),  # Off by -0.1
            MisconceptionType.OPERATION_SELECTION:
                str(round(answer_val * 2, 2))  # Doubled the result
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Numbers - Mixed Fractions & Decimals",
            logical_trap="Students don't convert between fractions and decimals before operating.",
            data_representation=f"```\nExpression: {expr}\nConvert to common form: decimals\nCalculate: {answer_val}\n```",
            question_text=f"What is {expr}?",
            solution_steps=[
                f"Expression: {expr}",
                "Convert all to decimals",
                "Perform operation",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.OPERATION_SELECTION, difficulty=1),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_equivalent_fractions_unlike(self) -> Question:
        """Find equivalent fractions with unlike denominators."""
        frac1_num = random.choice([1, 2, 3])
        frac1_den = random.choice([3, 4, 5])
        
        # Find equivalent with different denominator
        multiplier = random.choice([2, 3, 4])
        equivalent_num = frac1_num * multiplier
        equivalent_den = frac1_den * multiplier
        
        correct_answer = f"{equivalent_num}/{equivalent_den}"
        
        misconception_map = {
            MisconceptionType.SIMILAR_CONCEPT_ERROR: f"{frac1_num + multiplier}/{frac1_den + multiplier}",
            MisconceptionType.OPERATION_SELECTION: f"{equivalent_num}/{frac1_den}",
            MisconceptionType.INCOMPLETE_REASONING: f"{frac1_num}/{frac1_den}"
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.SIMILAR_CONCEPT_ERROR,
            difficulty=2,
            custom_description="Student adds instead of multiplying both parts",
            custom_why_effective="Adding feels natural; multiplying is harder",
            custom_how_to_avoid="Multiply numerator AND denominator by same number"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Equivalent Fractions with Unlike Denominators",
            logical_trap="Student adds to numerator and denominator instead of multiplying",
            data_representation=f"{frac1_num}/{frac1_den} = ?/{equivalent_den}",
            question_text=f"Find equivalent fraction: {frac1_num}/{frac1_den} = ?/{equivalent_den}",
            solution_steps=[
                f"Original: {frac1_num}/{frac1_den}",
                f"Target denominator: {equivalent_den}",
                f"Multiplier: {equivalent_den} ÷ {frac1_den} = {multiplier}",
                f"Multiply both: {frac1_num} × {multiplier} = {equivalent_num}",
                f"Answer: {equivalent_num}/{equivalent_den}"
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
    
    def _generate_improper_to_mixed(self) -> Question:
        """Convert improper fraction to mixed number."""
        numerator = random.randint(5, 15)
        denominator = random.randint(2, 6)
        
        whole_part = numerator // denominator
        remainder = numerator % denominator
        
        correct_answer = f"{whole_part} {remainder}/{denominator}"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{numerator}/{denominator}",
            MisconceptionType.OPERATION_SELECTION: f"{whole_part}/{remainder}",
            MisconceptionType.CONSTRAINT_VIOLATION: f"{remainder}/{denominator}"
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student provides improper fraction instead of converting to mixed",
            custom_why_effective="Conversion requires division and understanding remainder",
            custom_how_to_avoid="Divide numerator by denominator: whole part + remainder/denominator"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Improper to Mixed Number Conversion",
            logical_trap="Student doesn't convert improper fraction to mixed number form",
            data_representation=f"Improper fraction: {numerator}/{denominator}",
            question_text=f"Convert {numerator}/{denominator} to a mixed number",
            solution_steps=[
                f"Divide numerator by denominator: {numerator} ÷ {denominator} = {whole_part} remainder {remainder}",
                f"Mixed number: {whole_part} {remainder}/{denominator}",
                f"Check: {whole_part} × {denominator} + {remainder} = {numerator} ✓"
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
    
    def _generate_unit_fractions(self) -> Question:
        """Identify and order unit fractions."""
        fractions = [
            ("1/2", 0.5),
            ("1/3", 0.333),
            ("1/4", 0.25),
            ("1/5", 0.2),
            ("1/6", 0.167)
        ]
        
        selected = random.sample(fractions, 3)
        selected_sorted = sorted(selected, key=lambda x: x[1], reverse=True)
        
        correct_answer = " > ".join([f[0] for f in selected_sorted])
        
        wrong_orders = [
            " > ".join([f[0] for f in selected_sorted[::-1]]),  # Reversed
            " > ".join([f[0] for f in selected]),  # Original order
        ]
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: wrong_orders[0],
            MisconceptionType.CONSTRAINT_VIOLATION: wrong_orders[1],
            MisconceptionType.OPERATION_SELECTION: " = ".join([f[0] for f in selected])
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student reverses unit fraction ordering (bigger denominator = smaller fraction)",
            custom_why_effective="Counter-intuitive: 1/5 < 1/3 even though 5 > 3",
            custom_how_to_avoid="Smaller denominator = bigger fraction piece. 1/2 > 1/3 > 1/4"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Ordering Unit Fractions",
            logical_trap="Student doesn't understand that smaller denominators make bigger pieces",
            data_representation=" , ".join([f[0] for f in selected]),
            question_text=f"Order from greatest to least: {', '.join([f[0] for f in selected])}",
            solution_steps=[
                f"Unit fractions: {', '.join([f[0] for f in selected])}",
                f"Smaller denominator = bigger piece",
                f"Order: {correct_answer}"
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
    
    def _generate_fraction_subtraction(self) -> Question:
        """Subtract fractions with common denominators."""
        denominator = random.choice([4, 5, 6, 8])
        num1 = random.randint(3, denominator - 1)
        num2 = random.randint(1, num1 - 1)
        
        result_num = num1 - num2
        correct_answer = f"{result_num}/{denominator}"
        
        misconception_map = {
            MisconceptionType.OPERATION_SELECTION: f"{num1 + num2}/{denominator}",
            MisconceptionType.ARITHMETIC_ERROR: f"{num1 - num2 + 1}/{denominator}",
            MisconceptionType.INCOMPLETE_REASONING: f"{num1}/{denominator}"
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.OPERATION_SELECTION,
            difficulty=1,
            custom_description="Student adds instead of subtracting numerators",
            custom_why_effective="Addition and subtraction symbols can be confused",
            custom_how_to_avoid="With common denominators: subtract numerators only, keep denominator same"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        question = Question(
            chapter=self.chapter,
            topic="Fraction Subtraction",
            logical_trap="Student adds numerators instead of subtracting",
            data_representation=f"{num1}/{denominator} - {num2}/{denominator}",
            question_text=f"Calculate: {num1}/{denominator} - {num2}/{denominator}",
            solution_steps=[
                f"Same denominator: {denominator}",
                f"Subtract numerators: {num1} - {num2} = {result_num}",
                f"Keep denominator: {denominator}",
                f"Answer: {result_num}/{denominator}"
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
