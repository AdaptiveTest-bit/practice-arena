"""Fractions and Decimals question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
import random
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
            "mixed_operations"
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
        else:
            return self._generate_mixed_operations()
    
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
        
        # Wrong comparisons
        wrong_symbols = [s for s in [">", "<", "="] if s != symbol]
        wrong1 = f"{f1} {wrong_symbols[0]} {f2}"
        wrong2 = f"{f1} {wrong_symbols[1]} {f2}"
        wrong3 = "Cannot compare"
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
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
        
        # Wrong answers
        wrong1 = f"{num1 + num2}/{denom1 + denom2}"  # Adding directly
        wrong2 = f"{num1}/{denom1}"  # First fraction only
        wrong3 = f"{num2}/{denom2}"  # Second fraction only
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
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
        
        # Wrong answers
        wrong1 = f"{num1 * num2}/{denom1 * denom2}"  # Without simplifying
        wrong2 = f"{num1}/{denom2}"  # Cross terms
        wrong3 = f"{(num1 + num2)}/{(denom1 + denom2)}"  # Addition instead
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
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
        
        # Wrong decimals
        wrong1 = str(float(Fraction(fraction)) + 0.1)
        wrong2 = str(float(Fraction(fraction)) - 0.1)
        wrong3 = Fraction(fraction).denominator / Fraction(fraction).numerator
        
        options = self.ensure_unique_options([correct_answer, str(wrong1)[:4], str(wrong2)[:4], str(wrong3)[:4]])
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
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
        
        # Wrong comparisons
        wrong_symbols = [s for s in [">", "<", "="] if s != symbol]
        wrong1 = f"{dec1} {wrong_symbols[0]} {dec2}"
        wrong2 = f"{dec1} {wrong_symbols[1]} {dec2}"
        wrong3 = "Cannot compare"
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
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
        
        wrong1 = str(answer_val + 0.1)
        wrong2 = str(answer_val - 0.1)
        wrong3 = str(answer_val * 2)
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
