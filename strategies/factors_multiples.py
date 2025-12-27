"""Factors and Multiples question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
import random
import math


class FactorsMultiplesStrategy(BaseChapterStrategy):
    """Generates factors, multiples, and divisibility problems."""
    
    chapter = ChapterEnum.FACTORS_MULTIPLES
    chapter_name = "Factors & Multiples"
    description = "Factors, multiples, LCM, GCD problems"
    
    def generate(self) -> Question:
        """Generate a factors/multiples question."""
        problem_type = random.choice([
            "find_factors",
            "find_multiples",
            "divisibility",
            "lcm_problem",
            "gcd_problem",
            "prime_factorization"
        ])
        
        if problem_type == "find_factors":
            return self._generate_find_factors()
        elif problem_type == "find_multiples":
            return self._generate_find_multiples()
        elif problem_type == "divisibility":
            return self._generate_divisibility()
        elif problem_type == "lcm_problem":
            return self._generate_lcm_problem()
        elif problem_type == "gcd_problem":
            return self._generate_gcd_problem()
        else:
            return self._generate_prime_factorization()
    
    def _generate_find_factors(self) -> Question:
        """Find all factors of a number."""
        number = random.choice([12, 18, 20, 24, 30, 36, 40, 48])
        
        # Calculate actual factors
        factors = [i for i in range(1, number + 1) if number % i == 0]
        correct_answer = f"{factors}"
        
        # Create wrong options by missing/adding factors
        wrong1 = str([i for i in range(1, number) if number % i == 0])  # Missing last
        wrong2 = str([i for i in range(1, number + 1) if number % i == 0 and i != factors[-2]])  # Missing one
        wrong3 = str([1, number])  # Only 1 and number
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - Finding Factors",
            logical_trap="K.C. Nag trap: Students forget to include 1 and the number itself as factors.",
            data_representation=f"```\nNumber: {number}\nFactors: 1, ..., {number}\nDivisible? 0 remainder\n```",
            question_text=f"What are all the factors of {number}?",
            solution_steps=[
                f"Number: {number}",
                "Test each number from 1 to 20:",
                "20 ÷ 1 = 20 ✓",
                "20 ÷ 2 = 10 ✓",
                "20 ÷ 4 = 5 ✓",
                "20 ÷ 5 = 4 ✓",
                "20 ÷ 10 = 2 ✓",
                "20 ÷ 20 = 1 ✓",
                f"Factors: {factors}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_find_multiples(self) -> Question:
        """Find multiples of a number."""
        number = random.choice([3, 4, 5, 6, 7, 8, 9])
        count = random.randint(3, 5)
        
        multiples = [number * i for i in range(1, count + 1)]
        correct_answer = f"{multiples}"
        
        # Wrong options
        wrong1 = str([number * i for i in range(0, count)])  # Starting from 0
        wrong2 = str([number * i for i in range(1, count)])  # One less
        wrong3 = str([number * i for i in range(1, count + 2)])  # One more
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - Finding Multiples",
            logical_trap="Students confuse which number multiplies by which.",
            data_representation=f"```\nNumber: {number}\nMultiples: {number}×1, {number}×2, ..., {number}×{count}\n"
                               f"Result: {multiples}\n```",
            question_text=f"What are the first {count} multiples of {number}?",
            solution_steps=[
                f"Number: {number}",
                f"{number} × 1 = {number}",
                f"{number} × 2 = {number * 2}",
                f"{number} × 3 = {number * 3}",
                f"Multiples: {multiples}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_divisibility(self) -> Question:
        """Test divisibility rules."""
        number = random.randint(100, 999)
        divisor = random.choice([2, 3, 5, 9])
        
        is_divisible = number % divisor == 0
        correct_answer = f"{'Yes' if is_divisible else 'No'}, {number} is {'divisible' if is_divisible else 'not divisible'} by {divisor}"
        wrong_answer = f"{'No' if is_divisible else 'Yes'}, {number} is {'not divisible' if is_divisible else 'divisible'} by {divisor}"
        
        options = self.ensure_unique_options([correct_answer, wrong_answer, "Cannot determine", "Partially divisible"])
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - Divisibility Rules",
            logical_trap="K.C. Nag trap: Students don't know divisibility rules correctly.",
            data_representation=f"```\nNumber: {number}\nDivisor: {divisor}\nRemainder: {number % divisor}\n```",
            question_text=f"Is {number} divisible by {divisor}?",
            solution_steps=[
                f"Number: {number}",
                f"Divisor: {divisor}",
                f"{number} ÷ {divisor} = {number // divisor} remainder {number % divisor}",
                f"{'Divisible' if is_divisible else 'Not divisible'}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_lcm_problem(self) -> Question:
        """Find LCM (Least Common Multiple)."""
        a = random.choice([4, 6, 8, 9, 12])
        b = random.choice([6, 8, 10, 12, 15])
        
        lcm = (a * b) // math.gcd(a, b)
        correct_answer = f"LCM({a}, {b}) = {lcm}"
        
        wrong1 = f"LCM({a}, {b}) = {a * b}"  # Product
        wrong2 = f"LCM({a}, {b}) = {max(a, b)}"  # Larger number
        wrong3 = f"LCM({a}, {b}) = {math.gcd(a, b)}"  # GCD instead
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - LCM",
            logical_trap="K.C. Nag trap: Students confuse LCM with product or GCD.",
            data_representation=f"```\nNumber 1: {a}\nNumber 2: {b}\nMultiples of {a}: {a}, {a*2}, {a*3}, {a*4}...\n"
                               f"Multiples of {b}: {b}, {b*2}, {b*3}, {b*4}...\nCommon multiple: {lcm}\n```",
            question_text=f"Find the LCM (Least Common Multiple) of {a} and {b}.",
            solution_steps=[
                f"Multiples of {a}: {a}, {a*2}, {a*3}, {a*4}...",
                f"Multiples of {b}: {b}, {b*2}, {b*3}, {b*4}...",
                f"Common multiples: {lcm}, {lcm*2}...",
                f"Least common: {lcm}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_gcd_problem(self) -> Question:
        """Find GCD (Greatest Common Divisor)."""
        a = random.choice([12, 18, 24, 30, 36])
        b = random.choice([18, 24, 30, 36, 48])
        
        gcd = math.gcd(a, b)
        correct_answer = f"GCD({a}, {b}) = {gcd}"
        
        wrong1 = f"GCD({a}, {b}) = {min(a, b)}"  # Smaller number
        wrong2 = f"GCD({a}, {b}) = 1"  # Coprime
        wrong3 = f"GCD({a}, {b}) = {(a * b) // math.lcm(a, b)}"  # LCM formula
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - GCD",
            logical_trap="Students confuse GCD with LCM or think GCD is always 1.",
            data_representation=f"```\nNumber 1: {a}\nNumber 2: {b}\nFactors of {a}: 1, ..., {a}\n"
                               f"Factors of {b}: 1, ..., {b}\nCommon factors: 1, ..., {gcd}\n```",
            question_text=f"Find the GCD (Greatest Common Divisor) of {a} and {b}.",
            solution_steps=[
                f"Factors of {a}: {[i for i in range(1, a+1) if a % i == 0]}",
                f"Factors of {b}: {[i for i in range(1, b+1) if b % i == 0]}",
                f"Common factors: {[i for i in range(1, min(a,b)+1) if a % i == 0 and b % i == 0]}",
                f"Greatest common: {gcd}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_prime_factorization(self) -> Question:
        """Prime factorization of a number."""
        number = random.choice([12, 18, 20, 24, 30, 36, 40, 48, 60])
        
        # Simple prime factorization
        factors = []
        n = number
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        
        factors.sort()
        correct_answer = f"{number} = {' × '.join(map(str, factors))}"
        
        wrong1 = f"{number} = {factors[0]} × {number // factors[0]}"
        wrong2 = f"{number} = 2 × {number // 2}"
        wrong3 = f"{number} = {[i for i in range(1, number+1) if number % i == 0]}"
        
        options = self.ensure_unique_options([correct_answer, wrong1, wrong2, wrong3])
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - Prime Factorization",
            logical_trap="K.C. Nag trap: Students include composite factors instead of only primes.",
            data_representation=f"```\nNumber: {number}\nPrime factors: {factors}\n```",
            question_text=f"Find the prime factorization of {number}.",
            solution_steps=[
                f"Number: {number}",
                "Divide by smallest prime 2:",
                f"{number} ÷ {factors[0]} = {number // factors[0]}",
                "Continue dividing...",
                f"Prime factors: {factors}",
                f"Answer: {factors[0]} × {' × '.join(map(str, factors[1:]))}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
