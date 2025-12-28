"""Factors and Multiples question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
import random
from models.distractor import MisconceptionType
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                str([i for i in range(1, number) if number % i == 0]),  # Missing the number itself
            MisconceptionType.CONSTRAINT_VIOLATION: 
                str([i for i in range(1, number + 1) if number % i == 0 and i != factors[-2]]),  # Missing a factor
            MisconceptionType.ARITHMETIC_ERROR: 
                str([1, number])  # Only 1 and the number
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Student forgets to include 1 and the number itself as factors of a number",
            custom_why_effective="Common oversight; students often think only 'middle' factors count",
            custom_how_to_avoid="Remember: 1 divides everything; the number divides itself; find ALL divisors with no remainder"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.REMEMBER,
            trap_difficulty=1
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_find_multiples(self) -> Question:
        """Find multiples of a number."""
        number = random.choice([3, 4, 5, 6, 7, 8, 9])
        count = random.randint(3, 5)
        
        multiples = [number * i for i in range(1, count + 1)]
        correct_answer = f"{multiples}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.CONSTRAINT_VIOLATION: 
                str([number * i for i in range(0, count)]),  # Starting from 0
            MisconceptionType.INCOMPLETE_REASONING: 
                str([number * i for i in range(1, count)]),  # One less
            MisconceptionType.ARITHMETIC_ERROR: 
                str([number * i for i in range(1, count + 2)])  # One more
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.CONSTRAINT_VIOLATION,
            difficulty=1,
            custom_description="Student starts multiples from 0 instead of the number itself (n×0=0 is not a 'first multiple')",
            custom_why_effective="Basic constraint violation; 0 times anything is 0, but we don't list 0 as a multiple",
            custom_how_to_avoid="Multiples start at n×1, not n×0; the first multiple is the number itself"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.REMEMBER,
            trap_difficulty=1
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_divisibility(self) -> Question:
        """Test divisibility rules."""
        number = random.randint(100, 999)
        divisor = random.choice([2, 3, 5, 9])
        
        is_divisible = number % divisor == 0
        correct_answer = f"{'Yes' if is_divisible else 'No'}, {number} is {'divisible' if is_divisible else 'not divisible'} by {divisor}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPPOSITE_CONFUSION: 
                f"{'No' if is_divisible else 'Yes'}, {number} is {'not divisible' if is_divisible else 'divisible'} by {divisor}",  # Inverted answer
            MisconceptionType.INCOMPLETE_REASONING: 
                "Cannot determine",  # Unclear logic
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Partially divisible"  # Invalid concept
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=1,
            custom_description="Student inverts the divisibility test result; says 'no' when answer is 'yes' or vice versa",
            custom_why_effective="Simple Boolean confusion; testing divisibility is straightforward but students often flip the answer",
            custom_how_to_avoid="Check remainder: 0 remainder = divisible; any other remainder = NOT divisible; verify before answering"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.REMEMBER,
            trap_difficulty=1
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_lcm_problem(self) -> Question:
        """Find LCM (Least Common Multiple)."""
        a = random.choice([4, 6, 8, 9, 12])
        b = random.choice([6, 8, 10, 12, 15])
        
        lcm = (a * b) // math.gcd(a, b)
        correct_answer = f"LCM({a}, {b}) = {lcm}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.FORMULA_MISAPPLICATION: 
                f"LCM({a}, {b}) = {a * b}",  # Product instead of LCM
            MisconceptionType.INCOMPLETE_REASONING: 
                f"LCM({a}, {b}) = {max(a, b)}",  # Just the larger number
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"LCM({a}, {b}) = {math.gcd(a, b)}"  # GCD instead of LCM
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.FORMULA_MISAPPLICATION,
            difficulty=2,
            custom_description="Student multiplies the two numbers instead of finding their least common multiple",
            custom_why_effective="Product is closest wrong answer; students often apply wrong formula when confused",
            custom_how_to_avoid="LCM ≠ a×b; use prime factorization or list multiples; LCM is usually smaller than product"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_gcd_problem(self) -> Question:
        """Find GCD (Greatest Common Divisor)."""
        a = random.choice([12, 18, 24, 30, 36])
        b = random.choice([18, 24, 30, 36, 48])
        
        gcd = math.gcd(a, b)
        correct_answer = f"GCD({a}, {b}) = {gcd}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"GCD({a}, {b}) = {min(a, b)}",  # Just the smaller number
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"GCD({a}, {b}) = 1",  # Assumes coprime
            MisconceptionType.FORMULA_MISAPPLICATION: 
                f"GCD({a}, {b}) = {(a * b) // math.lcm(a, b)}"  # LCM-based formula
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student reports just the smaller number instead of finding greatest common divisor",
            custom_why_effective="Incomplete reasoning; students sometimes report the smaller input value instead of computing GCD",
            custom_how_to_avoid="List all factors of both numbers; find COMMON ones; select GREATEST; verify by dividing both numbers"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{number} = {factors[0]} × {number // factors[0]}",  # Partial factorization
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"{number} = 2 × {number // 2}",  # Only divides by 2 once
            MisconceptionType.PATTERN_MISIDENTIFICATION: 
                f"{number} = {[i for i in range(1, number+1) if number % i == 0]}"  # Lists all factors instead of primes
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.CONSTRAINT_VIOLATION,
            difficulty=2,
            custom_description="Student lists all factors instead of only PRIME factors; includes composite numbers",
            custom_why_effective="Students often confuse 'all factors' with 'prime factors'; constraint violation by including composites",
            custom_how_to_avoid="Remember: Prime factorization uses ONLY prime numbers (2,3,5,7,...); no composite factors allowed"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
