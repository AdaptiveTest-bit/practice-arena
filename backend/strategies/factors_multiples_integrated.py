"""
INTEGRATED FACTORS & MULTIPLES STRATEGY
========================================

Seamlessly merges:
1. HYBRID NEURO-SYMBOLIC: SymPy-generated skeletons + K.C. Nag storytelling
2. EXISTING ADAPTIVE ENGINE: Misconception-based distractors + Bloom's progression

Result: Indistinguishable integration where both systems enhance each other
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
from models.distractor import MisconceptionType, DistractorSet, DistractorInfo
import random
import math
import time
from typing import List, Tuple, Dict, Any
import sympy
from pathlib import Path

# Import hybrid system components
from content.generators.factors_multiples import (
    FactorsMultiplesGenerator,
    FactorMultipleConcept,
    DifficultyLevel as HybridDifficultyLevel,
)
from content.generators.kc_nag_story import KCNagStoryGeneratorLocal
from content.renderer import RichQuestionRenderer

# Import question bank components
from services.question_bank_loader import QuestionBank, QuestionConstructor

# Import caching
from core.skeleton_cache import get_skeleton_cache


class FactorsMultiplesIntegrated(BaseChapterStrategy):
    """
    INTEGRATED STRATEGY: Hybrid SymPy + Adaptive Engine
    
    Phase 1: Generate deterministic SymPy skeleton (guarantees correctness)
    Phase 2: Generate K.C. Nag story context (ensures engagement)
    Phase 3: Generate misconception-based options (trains detection)
    Phase 4: Render rich question (beautiful presentation)
    Phase 5: Return trackable Question object (enables analytics)
    """
    
    chapter = ChapterEnum.FACTORS_MULTIPLES
    chapter_name = "Factors & Multiples"
    description = "Factors, multiples, LCM, GCD with hybrid neuro-symbolic generation"
    
    def __init__(self):
        super().__init__()
        self.sympy_generator = FactorsMultiplesGenerator()
        self.story_generator = KCNagStoryGeneratorLocal()
        self.renderer = RichQuestionRenderer()
        self.skeleton_cache = get_skeleton_cache()  # Initialize cache
        
        # INTEGRATION: Initialize question bank (60% of questions from here)
        try:
            bank_path = Path(__file__).parent.parent / 'data' / 'class5_chapter5_bank.yaml'
            self.question_bank = QuestionBank(str(bank_path))
            self.use_question_bank = True
            self._validate_question_bank()
        except FileNotFoundError:
            print("⚠ Warning: Question bank file not found at", bank_path)
            print("  Using dynamic generation only (100% instead of 60/40 split)")
            self.use_question_bank = False
        except Exception as e:
            print(f"⚠ Warning: Failed to load question bank: {e}")
            self.use_question_bank = False
    
    def _validate_question_bank(self) -> bool:
        """
        Validate question bank on initialization.
        
        Returns:
            True if bank is valid and ready, False otherwise
        """
        if not self.use_question_bank:
            return False
        
        try:
            stats = self.question_bank.stats()
            total = stats['total_questions']
            print(f"✓ Question bank loaded: {total} questions available")
            print(f"  By difficulty: {stats['by_difficulty']}")
            print(f"  By Bloom's level: {stats['by_bloom_level']}")
            
            # Verify coverage
            missing_levels = []
            for level in range(1, 6):
                level_qs = self.question_bank.get_by_category_difficulty(
                    'factors_multiples', level
                )
                if len(level_qs) == 0:
                    missing_levels.append(level)
            
            if missing_levels:
                print(f"⚠ Warning: No questions at difficulty levels {missing_levels}")
            
            return True
            
        except Exception as e:
            print(f"✗ Question bank validation failed: {e}")
            return False
    
    def _generate_from_bank(self, difficulty: int) -> Question:
        """
        Generate a question from the pre-authored bank.
        
        This provides high-quality, pedagogically-vetted questions with rich content.
        
        Args:
            difficulty: Difficulty level (1-5)
            
        Returns:
            Question object with complete rich content
        """
        if not self.use_question_bank:
            # Fallback to dynamic generation
            return self._generate_find_factors_integrated()
        
        try:
            # Get questions at this difficulty level
            bank_questions = self.question_bank.get_by_category_difficulty(
                'factors_multiples', difficulty
            )
            
            if not bank_questions:
                # Fallback if no questions at this difficulty
                return self._generate_find_factors_integrated()
            
            # Pick random question from bank
            selected_yaml = random.choice(bank_questions)
            
            # Convert YAML to Question object with all rich content
            question = QuestionConstructor.construct_from_yaml(selected_yaml)
            
            return question
            
        except Exception as e:
            print(f"⚠ Error generating from bank: {e}")
            # Fallback to dynamic generation
            return self._generate_find_factors_integrated()
    
    def _generate_assertion_reason_integrated(self) -> Question:
        """
        Generate Assertion-Reason question (Bloom's Level 4: ANALYZE).
        
        Format: 
        - Assertion: A statement about factors/multiples
        - Reason: An explanation for why the assertion might be true
        - Options: 
          A) Both assertion and reason are correct, reason explains assertion
          B) Both are correct, but reason doesn't explain assertion
          C) Assertion is correct, but reason is wrong
          D) Both are wrong
        
        This tests deep understanding and critical thinking.
        
        Returns:
            Question object with assertion-reason structure
        """
        # Pick a random concept
        concept = random.choice([
            "factors_property",
            "multiples_property", 
            "gcd_property",
            "lcm_property"
        ])
        
        if concept == "factors_property":
            # Assertion: Statement about factors
            num1 = random.randint(12, 48)
            num2 = random.randint(12, 48)
            assertion_text = f"The number {num1} is a factor of {num1 * num2}"
            reason_text = f"Because {num1} × {num2} = {num1 * num2}"
            correct = True
            
        elif concept == "multiples_property":
            # Assertion: Statement about multiples
            base = random.randint(3, 12)
            multiple_count = random.randint(3, 7)
            num = base * multiple_count
            assertion_text = f"The number {num} is a multiple of {base}"
            reason_text = f"Because {base} × {multiple_count} = {num}"
            correct = True
            
        elif concept == "gcd_property":
            # Assertion: Statement about GCD
            num1 = random.randint(10, 30)
            num2 = random.randint(10, 30)
            from math import gcd
            gcd_val = gcd(num1, num2)
            assertion_text = f"The GCD of {num1} and {num2} is a factor of both numbers"
            reason_text = f"By definition, GCD({num1}, {num2}) = {gcd_val} divides both"
            correct = True
            
        else:  # lcm_property
            # Assertion: Statement about LCM
            num1 = random.randint(2, 12)
            num2 = random.randint(2, 12)
            from math import gcd
            lcm_val = (num1 * num2) // gcd(num1, num2)
            assertion_text = f"The LCM of {num1} and {num2} is divisible by both numbers"
            reason_text = f"LCM({num1}, {num2}) = {lcm_val}, which is a multiple of both"
            correct = True
        
        # Create question content
        question_text = f"**Assertion:** {assertion_text}\n\n**Reason:** {reason_text}\n\nChoose the correct option:"
        
        # Options for assertion-reason format
        options = [
            "Both assertion and reason are correct; reason explains assertion",
            "Both are correct; reason does NOT explain assertion",
            "Assertion is correct; reason is incorrect",
            "Both assertion and reason are incorrect"
        ]
        
        # For this prototype, assertion and reason are always correct and related
        correct_option_index = 0
        
        # Create Question object with proper model structure
        question = Question(
            topic=f"{concept.replace('_', ' ')} - Assertion Reasoning",
            logical_trap=f"Understanding whether both the assertion and reason are correct, AND whether the reason explains the assertion",
            data_representation=f"Assertion: {assertion_text}\nReason: {reason_text}",
            question_text=question_text,
            solution_steps=[
                f"Step 1: Evaluate the assertion - {assertion_text} - This is TRUE",
                f"Step 2: Evaluate the reason - {reason_text} - This is TRUE",
                f"Step 3: Check if reason explains assertion - The reason directly explains why the assertion is true",
                f"Conclusion: Both are correct AND reason explains assertion → Answer is A"
            ],
            answer="A",
            options=options,
            correct_option_index=correct_option_index,
            chapter=self.chapter,
            rich_narrative=f"Deep dive into {concept.replace('_', ' ')} - Testing your analytical thinking",
            rich_html_content=None
        )
        
        return question
    
    def generate(self) -> Question:
        """
        Main generation pipeline with HYBRID architecture:
        - 60% from pre-authored question bank (rich narratives, diagrams, hints)
        - 40% from dynamic SymPy generation (procedurally diverse)
        
        Bank Generation Process:
        1. Pick random difficulty (1-5)
        2. Load question from YAML bank
        3. Convert to Question with rich content
        4. Return ready-to-use question
        
        Dynamic Generation Process:
        1. Pick problem type (factors, multiples, GCD, LCM, divisibility)
        2. Generate SymPy skeleton
        3. Generate K.C. Nag narrative
        4. Create misconception distractors
        5. Render rich question content
        6. Return trackable Question
        """
        
        # INTEGRATION: 60/40 hybrid generation
        use_bank = self.use_question_bank and random.random() < 0.6
        
        if use_bank:
            # 60% from question bank
            difficulty = random.randint(1, 5)
            return self._generate_from_bank(difficulty)
        
        else:
            # 40% from dynamic generation (existing methods)
            problem_type = random.choice([
                "find_factors",
                "find_multiples", 
                "find_gcd",
                "find_lcm",
                "divisibility_test"
            ])
            
            if problem_type == "find_factors":
                return self._generate_find_factors_integrated()
            elif problem_type == "find_multiples":
                return self._generate_find_multiples_integrated()
            elif problem_type == "find_gcd":
                return self._generate_find_gcd_integrated()
            elif problem_type == "find_lcm":
                return self._generate_find_lcm_integrated()
            else:
                return self._generate_divisibility_integrated()
    
    # ==================== PHASE 1: FIND FACTORS ====================
    
    def _generate_find_factors_integrated(self) -> Question:
        """
        Find all factors of a number
        
        Integration:
        - SymPy generates correct skeleton (guarantees no errors)
        - K.C. Nag story wraps in real-world context
        - Misconception distractors train detection
        - Rich rendering makes it beautiful
        """
        
        # HYBRID: Generate SymPy skeleton
        hybrid_difficulty = random.choice([
            HybridDifficultyLevel.EASY,
            HybridDifficultyLevel.MEDIUM,
            HybridDifficultyLevel.HARD,
        ])
        
        skeleton = self.sympy_generator.generate_factor_identification_question(
            difficulty=hybrid_difficulty,
            bloom_level=BloomLevel.UNDERSTAND
        )
        
        target_number = skeleton.parameters["target_number"]
        factors = skeleton.parameters["factors"]
        correct_answer = str(factors)
        
        # HYBRID: Generate K.C. Nag story context
        story_context = self.story_generator.generate_story_context(skeleton=skeleton)
        
        # ADAPTIVE: Generate misconception-based options
        distractor1_val = str([f for f in factors if f not in [1, target_number]])
        distractor2_val = str([1, target_number])
        distractor3_val = str([f for f in range(1, target_number + 1) if random.random() > 0.6])
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Complete set of factors",
                None,
                None
            ),
            1: (
                distractor1_val,
                MisconceptionType.INCOMPLETE_REASONING,
                "Missing 1 and the number itself",
                "Student forgot to include 1 and the number itself as factors",
                "1 divides every number, and every number divides itself"
            ),
            2: (
                distractor2_val,
                MisconceptionType.INCOMPLETE_REASONING,
                "Only boundary factors",
                "Student only listed 1 and the number",
                "A factor is any number that divides evenly; test all numbers from 1 to the target"
            ),
            3: (
                distractor3_val,
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Includes non-divisors",
                "Student included numbers that don't divide the target evenly",
                "A factor must divide with NO remainder; check your division carefully"
            ),
        }
        
        # Shuffle to randomize correct position
        shuffled_positions = list(range(4))
        random.shuffle(shuffled_positions)
        
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled_positions):
            option_text, misconception, short_desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = option_text
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer",
                    why_wrong="This is the correct answer",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=misconception,
                    description=short_desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # ADAPTIVE: Create trap info for misconception detection
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=self._difficulty_level_to_int(hybrid_difficulty),
            custom_description="Students forget to include 1 and the number itself as factors",
            custom_why_effective="Common oversight; seems logical to skip edge cases",
            custom_how_to_avoid="Check: Does 1 divide the number? Yes. Does the number divide itself? Yes. Both are factors!"
        )
        
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=self._difficulty_level_to_int(hybrid_difficulty)
        )
        
        # HYBRID: Render rich question
        # rich_content = self.renderer.render_rich_question(
        #             question_text=skeleton.latex_problem,
        #             story_context=story_context,
        #             solution_steps=skeleton.steps,
        #             explanation=skeleton.explanation,
        #             visual_hint="Use a factor tree or systematic division",
        #             progressive_hints=[
        #                 "Start by testing if 1 divides the number",
        #                 "Then test 2, 3, 4, ... up to the number",
        #                 "Record all numbers that divide evenly (remainder 0)",
        #                 "Don't forget to include the number itself!"
        #             ]
        #         )
        
        # ADAPTIVE: Return trackable Question object
        logical_trap = "K.C. Nag Trap: Students forget to include 1 and the number itself as factors. They often think only 'middle' factors count, forgetting that 1 divides everything and every number divides itself."
        
        # Wrap distractor_info in DistractorSet
        from models.distractor import DistractorSet
        distractor_info = DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer])
        
        # Generate rich narratives and diagrams
        rich_narrative = f"Let's find all the factors of {target_number}. A factor is a number that divides {target_number} with no remainder. We need to test every number from 1 to {target_number} and see which ones divide evenly. Remember: 1 always divides every number, and every number divides itself!"
        
        visual_hints = [
            f"Start by testing if 1 divides {target_number} evenly (it always does!)",
            f"Test 2, 3, 4, ... up to {target_number}",
            f"Only include numbers with remainder 0",
            f"Don't forget: {target_number} ÷ {target_number} = 1 with remainder 0, so {target_number} is a factor of itself!",
            f"Your final list should have exactly {len(factors)} factors"
        ]
        
        # Render HTML diagram for factors
        rich_html_content = self._render_factors_diagram(target_number, factors)
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - Finding Factors",
            logical_trap=logical_trap,
            data_representation=f"```\nNumber: {target_number}\nDivisibility: Test each from 1 to {target_number}\nResult: No remainder\n```",
            question_text=skeleton.latex_problem,
            solution_steps=skeleton.steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=rich_html_content,
            rich_narrative=rich_narrative,
            visual_hints=visual_hints,
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 2: FIND MULTIPLES ====================
    
    def _generate_find_multiples_integrated(self) -> Question:
        """Find first N multiples of a number"""
        
        hybrid_difficulty = random.choice([
            HybridDifficultyLevel.EASY,
            HybridDifficultyLevel.MEDIUM,
            HybridDifficultyLevel.HARD,
        ])
        
        skeleton = self.sympy_generator.generate_multiple_identification_question(
            difficulty=hybrid_difficulty,
            bloom_level=BloomLevel.UNDERSTAND
        )
        
        base_number = skeleton.parameters["base_number"]
        multiples = skeleton.parameters["multiples"]
        correct_answer = str(multiples)
        
        # HYBRID: Generate K.C. Nag story
        story_context = self.story_generator.generate_story_context(skeleton=skeleton)
        
        # ADAPTIVE: Misconception-based options
        option_distractors = {
            0: (
                correct_answer,
                None,
                "All multiples starting from base_number x 1",
                None,
                None
            ),
            1: (
                str([base_number * i for i in range(0, len(multiples) + 1)]),
                MisconceptionType.INCOMPLETE_REASONING,
                "Incorrectly includes 0 as first multiple",
                "Student added 0 as the first multiple",
                "Multiples start at 1x the base number, not 0x"
            ),
            2: (
                str([base_number * i for i in range(2, len(multiples) + 2)]),
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Starts from 2x instead of 1x",
                "Student skipped the first multiple",
                "The first multiple is the number itself (1x)"
            ),
            3: (
                str([base_number * i for i in range(1, len(multiples)) ] + [base_number * (len(multiples) + 1)]),
                MisconceptionType.ARITHMETIC_ERROR,
                "Off-by-one error in sequence",
                "Student miscounted the multiples",
                "List the exact number of multiples requested"
            ),
        }
        
        shuffled_positions = list(range(4))
        random.shuffle(shuffled_positions)
        
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled_positions):
            option_text, misconception, short_desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = option_text
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer",
                    why_wrong="This is correct",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=misconception,
                    description=short_desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        trap_info = self.create_trap_info(
            MisconceptionType.CONSTRAINT_VIOLATION,
            difficulty=self._difficulty_level_to_int(hybrid_difficulty),
            custom_description="Starting multiples from 0 instead of the base number",
            custom_why_effective="Seems logical to include 0, but 0 is not a 'multiple' in the traditional sense",
            custom_how_to_avoid="First multiple = 1 x base; second = 2 x base; 0 x base = 0 doesn't count"
        )
        
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=self._difficulty_level_to_int(hybrid_difficulty)
        )
        
        # HYBRID: Render rich question
        # rich_content = self.renderer.render_rich_question(
        #             question_text=skeleton.latex_problem,
        #             story_context=story_context,
        #             solution_steps=skeleton.steps,
        #             explanation=skeleton.explanation,
        #             visual_hint="Use a number line or multiplication table",
        #             progressive_hints=[
        #                 f"First multiple: {base_number} x 1 = {multiples[0]}",
        #                 f"Second multiple: {base_number} x 2 = {multiples[1]}",
        #                 f"Continue this pattern up to {len(multiples)} multiples",
        #                 "Don't include 0 as a multiple"
        #             ]
        #         )
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - Finding Multiples",
            logical_trap="K.C. Nag Trap: Students confuse which number multiplies by which, or incorrectly include 0 as the first multiple.",
            data_representation=f"```\nBase: {base_number}\nPattern: {base_number}x1, {base_number}x2, ...\nCount: {len(multiples)}\n```",
            question_text=skeleton.latex_problem,
            solution_steps=skeleton.steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=self._render_multiples_diagram(base_number, len(multiples), multiples),
            rich_narrative=f"A multiple of {base_number} is any number you get by multiplying {base_number} by a whole number (1, 2, 3, ...). The first multiple is {base_number} × 1 = {multiples[0]}, the second is {base_number} × 2 = {multiples[1]}, and so on. Notice we start with 1, not 0!",
            visual_hints=[
                f"Multiples of {base_number} follow a pattern: {base_number}, {base_number*2}, {base_number*3}, ...",
                f"Each multiple is the previous one plus {base_number}",
                f"First {len(multiples)} multiples: {', '.join(map(str, multiples))}",
                f"Remember: 0 × {base_number} = 0 is NOT a multiple; we start from 1 × {base_number}",
                f"Check: Is each number in your list exactly divisible by {base_number}?"
            ],
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 3: FIND GCD ====================
    
    def _generate_find_gcd_integrated(self) -> Question:
        """Find GCD using Euclidean algorithm or prime factorization"""
        
        a = random.randint(10, 50)
        b = random.randint(10, 50)
        
        gcd_value = math.gcd(a, b)
        correct_answer = str(gcd_value)
        
        factors_a = list(sympy.factorint(a).items())
        factors_b = list(sympy.factorint(b).items())
        
        # HYBRID: Create minimal skeleton for story context
        from content.models import MathSkeleton
        skeleton = MathSkeleton(
            concept="Greatest Common Divisor",
            question_type="gcd-calculation",
            difficulty=HybridDifficultyLevel.MEDIUM,
            bloom_level=BloomLevel.APPLY,
            parameters={"number_1": a, "number_2": b},
            latex_problem=f"Find GCD({a}, {b})",
            solution=gcd_value,
            steps=[],
            explanation="",
            is_valid=True,
            validation_notes=""
        )
        story_context = self.story_generator.generate_story_context(skeleton=skeleton)
        
        # ADAPTIVE: Misconception options
        option_distractors = {
            0: (
                correct_answer,
                None,
                "The largest number that divides both",
                None,
                None
            ),
            1: (
                str(a * b),
                MisconceptionType.FORMULA_CONFUSION,
                "Multiplying instead of finding GCD",
                "Student multiplied instead of finding GCD",
                "GCD is the largest divisor of both numbers"
            ),
            2: (
                str(min(a, b)),
                MisconceptionType.INCOMPLETE_REASONING,
                "Using the smaller number without checking divisibility",
                "Student just took the smaller number",
                "The smaller number may not divide the larger one evenly"
            ),
            3: (
                str(a + b),
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Adding the numbers instead of finding common divisor",
                "Student added instead of finding GCD",
                "GCD is about divisibility, not addition"
            ),
        }
        
        shuffled_positions = list(range(4))
        random.shuffle(shuffled_positions)
        
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled_positions):
            option_text, misconception, short_desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = option_text
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer",
                    why_wrong="This is correct",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=misconception,
                    description=short_desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        trap_info = self.create_trap_info(
            MisconceptionType.FORMULA_CONFUSION,
            difficulty=2,
            custom_description="Confusing GCD with LCM or just multiplying numbers",
            custom_why_effective="GCD and LCM are often taught together, causing confusion",
            custom_how_to_avoid="GCD: largest divisor of BOTH; LCM: smallest multiple of BOTH"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        steps = [
            f"Numbers: {a} and {b}",
            f"Factors of {a}: {factors_a}",
            f"Factors of {b}: {factors_b}",
            f"Common factors: (calculated)",
            f"GCD({a}, {b}) = {gcd_value}"
        ]
        
        # rich_content = self.renderer.render_rich_question(
        #             question_text=f"Find the GCD of {a} and {b}",
        #             story_context=story_context,
        #             solution_steps=steps,
        #             explanation="GCD is the largest number that divides both numbers evenly",
        #             visual_hint="List all factors of each number and find the largest common one",
        #             progressive_hints=[
        #                 f"Factors of {a}: ...",
        #                 f"Factors of {b}: ...",
        #                 "Find factors that appear in BOTH lists",
        #                 "The GCD is the largest of these common factors"
        #             ]
        #         )
        
        question = Question(
            chapter=self.chapter,
            topic="Number Theory - Greatest Common Divisor",
            logical_trap="K.C. Nag Trap: Students confuse GCD with LCM or just multiply the numbers together.",
            data_representation=f"```\nGCD({a}, {b}) = ?\nLargest divisor of both\n```",
            question_text=f"What is the GCD of {a} and {b}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=self._render_gcd_diagram(a, b, gcd_value),
            rich_narrative=f"To find the GCD (Greatest Common Divisor) of {a} and {b}, we look for the largest number that divides both of them evenly. The GCD is {gcd_value}, which means {gcd_value} divides both {a} and {b} with no remainder. This is the largest such divisor.",
            visual_hints=[
                f"The GCD must divide both {a} and {b} evenly",
                f"List factors of {a}: {self._get_prime_factors(a)} (prime factors)",
                f"List factors of {b}: {self._get_prime_factors(b)} (prime factors)",
                f"Find common factors and multiply them together",
                f"The result is the GCD = {gcd_value}"
            ],
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 4: FIND LCM ====================
    
    def _generate_find_lcm_integrated(self) -> Question:
        """Find LCM (Least Common Multiple)"""
        
        a = random.randint(4, 20)
        b = random.randint(4, 20)
        
        lcm_value = sympy.lcm(a, b)
        correct_answer = str(lcm_value)
        
        # HYBRID: Create minimal skeleton for story context
        from content.models import MathSkeleton
        skeleton = MathSkeleton(
            concept="Least Common Multiple",
            question_type="lcm-calculation",
            difficulty=HybridDifficultyLevel.MEDIUM,
            bloom_level=BloomLevel.APPLY,
            parameters={"number_1": a, "number_2": b},
            latex_problem=f"Find LCM({a}, {b})",
            solution=lcm_value,
            steps=[],
            explanation="",
            is_valid=True,
            validation_notes=""
        )
        story_context = self.story_generator.generate_story_context(skeleton=skeleton)
        
        # ADAPTIVE: Options
        option_distractors = {
            0: (
                correct_answer,
                None,
                "The smallest number divisible by both",
                None,
                None
            ),
            1: (
                str(a * b),
                MisconceptionType.FORMULA_MISAPPLICATION,
                "Multiplying instead of finding LCM",
                "Student multiplied the numbers",
                "LCM is usually smaller than the product"
            ),
            2: (
                str(math.gcd(a, b)),
                MisconceptionType.FORMULA_CONFUSION,
                "Finding GCD instead of LCM",
                "Student found GCD instead of LCM",
                "LCM is the smallest multiple, GCD is the largest divisor"
            ),
            3: (
                str(max(a, b)),
                MisconceptionType.INCOMPLETE_REASONING,
                "Using the larger number without checking",
                "Student just took the larger number",
                "The larger number may not be a multiple of the smaller one"
            ),
        }
        
        shuffled_positions = list(range(4))
        random.shuffle(shuffled_positions)
        
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled_positions):
            option_text, misconception, short_desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = option_text
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer",
                    why_wrong="This is correct",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=misconception,
                    description=short_desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        trap_info = self.create_trap_info(
            MisconceptionType.FORMULA_MISAPPLICATION,
            difficulty=2,
            custom_description="Multiplying the numbers instead of finding their LCM",
            custom_why_effective="Product is superficially similar to LCM for some numbers",
            custom_how_to_avoid="LCM <= product; use prime factorization or list multiples"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        steps = [
            f"Numbers: {a} and {b}",
            f"Multiples of {a}: {a}, {a*2}, {a*3}, ...",
            f"Multiples of {b}: {b}, {b*2}, {b*3}, ...",
            f"First common multiple: {lcm_value}",
            f"LCM({a}, {b}) = {lcm_value}"
        ]
        
        # rich_content = self.renderer.render_rich_question(
        #             question_text=f"Find the LCM of {a} and {b}",
        #             story_context=story_context,
        #             solution_steps=steps,
        #             explanation="LCM is the smallest positive integer divisible by both numbers",
        #             visual_hint="List multiples of each and find the first one that appears in both lists",
        #             progressive_hints=[
        #                 f"Multiples of {a}: {a}, {a*2}, {a*3}, ...",
        #                 f"Multiples of {b}: {b}, {b*2}, {b*3}, ...",
        #                 "Find the first number appearing in BOTH lists",
        #                 f"That's the LCM = {lcm_value}"
        #             ]
        #         )
        
        question = Question(
            chapter=self.chapter,
            topic="Number Theory - Least Common Multiple",
            logical_trap="K.C. Nag Trap: Students confuse LCM with GCD or just multiply the numbers together.",
            data_representation=f"```\nLCM({a}, {b}) = ?\nSmallest multiple of both\n```",
            question_text=f"What is the LCM of {a} and {b}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=self._render_lcm_diagram(a, b, lcm_value),
            rich_narrative=f"To find the LCM (Least Common Multiple) of {a} and {b}, we look for the smallest positive number that is a multiple of both. The LCM is {lcm_value}, which means it can be divided evenly by both {a} and {b}. This is the smallest such number.",
            visual_hints=[
                f"Multiples of {a}: {a}, {a*2}, {a*3}, {a*4}, {a*5}, ...",
                f"Multiples of {b}: {b}, {b*2}, {b*3}, {b*4}, {b*5}, ...",
                f"Find the first number that appears in BOTH lists",
                f"That's the LCM = {lcm_value}",
                f"Check: {lcm_value} ÷ {a} = {lcm_value // a} and {lcm_value} ÷ {b} = {lcm_value // b} (both whole numbers)"
            ],
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 5: DIVISIBILITY TEST ====================
    
    def _generate_divisibility_integrated(self) -> Question:
        """Test divisibility rules (Remember level)"""
        
        number = random.randint(100, 999)
        divisor = random.choice([2, 3, 5, 9, 10])
        
        is_divisible = number % divisor == 0
        correct_answer = f"{'Yes' if is_divisible else 'No'}"
        
        # HYBRID: Create minimal skeleton for story context
        from content.models import MathSkeleton
        skeleton = MathSkeleton(
            concept="Divisibility Rules",
            question_type="divisibility-test",
            difficulty=HybridDifficultyLevel.EASY,
            bloom_level=BloomLevel.REMEMBER,
            parameters={"number": number, "divisor": divisor},
            latex_problem=f"Is {number} divisible by {divisor}?",
            solution=is_divisible,
            steps=[],
            explanation="",
            is_valid=True,
            validation_notes=""
        )
        story_context = self.story_generator.generate_story_context(skeleton=skeleton)
        
        # ADAPTIVE: Options
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correctly applies divisibility rule",
                None,
                None
            ),
            1: (
                f"{'No' if is_divisible else 'Yes'}",
                MisconceptionType.OPPOSITE_CONFUSION,
                "Gives opposite answer",
                "Student inverted the result",
                "Double-check: remainder 0 means divisible"
            ),
            2: (
                "Cannot determine",
                MisconceptionType.INCOMPLETE_REASONING,
                "Doesn't know divisibility rule",
                "Student doesn't know the rule",
                "Learn the divisibility rules for each number"
            ),
            3: (
                "Partially",
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Doesn't understand binary nature of divisibility",
                "Student thinks divisibility is not binary",
                "A number is either divisible or not - no 'partially'"
            ),
        }
        
        shuffled_positions = list(range(4))
        random.shuffle(shuffled_positions)
        
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled_positions):
            option_text, misconception, short_desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = option_text
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer",
                    why_wrong="This is correct",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text,
                    misconception_type=misconception,
                    description=short_desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=1,
            custom_description="Inverting the divisibility test result",
            custom_why_effective="Simple Boolean confusion after correct calculation",
            custom_how_to_avoid="Divisible = remainder 0; Not divisible = remainder > 0; Double-check before answering"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.REMEMBER, trap_difficulty=1)
        
        rule_text = {
            2: "Last digit is even (0, 2, 4, 6, 8)",
            3: "Sum of digits is divisible by 3",
            5: "Last digit is 0 or 5",
            9: "Sum of digits is divisible by 9",
            10: "Last digit is 0"
        }[divisor]
        
        steps = [
            f"Number: {number}",
            f"Divisor: {divisor}",
            f"Rule for divisibility by {divisor}: {rule_text}",
            f"Check: {number} / {divisor} = {number // divisor} remainder {number % divisor}",
            f"Result: {'DIVISIBLE' if is_divisible else 'NOT DIVISIBLE'}"
        ]
        
        # rich_content = self.renderer.render_rich_question(
        #             question_text=f"Is {number} divisible by {divisor}?",
        #             story_context=story_context,
        #             solution_steps=steps,
        #             explanation=f"Divisibility rule for {divisor}: {rule_text}",
        #             visual_hint="Use divisibility rule or long division",
        #             progressive_hints=[
        #                 f"Divisibility rule for {divisor}: {rule_text}",
        #                 f"Check if {number} satisfies this rule",
        #                 f"{number} / {divisor} = {number // divisor} R{number % divisor}",
        #                 f"Remainder = {number % divisor}, so it is {'divisible' if is_divisible else 'NOT divisible'}"
        #             ]
        #         )
        
        question = Question(
            chapter=self.chapter,
            topic="Number Sense - Divisibility Rules",
            logical_trap="K.C. Nag Trap: Students invert the divisibility test result or don't know the divisibility rules.",
            data_representation=f"```\n{number} / {divisor}\nRemainder: {number % divisor}\n```",
            question_text=f"Is {number} divisible by {divisor}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=self._render_divisibility_diagram(number, divisor, is_divisible),
            rich_narrative=f"To check if {number} is divisible by {divisor}, we use the divisibility rule: {rule_text}. A number is divisible by another if it divides evenly with no remainder. In this case, {number} ÷ {divisor} = {number // divisor} remainder {number % divisor}, so {number} is {'DIVISIBLE' if is_divisible else 'NOT DIVISIBLE'} by {divisor}.",
            visual_hints=[
                f"Divisibility rule for {divisor}: {rule_text}",
                f"Apply the rule to {number}",
                f"Perform the division: {number} ÷ {divisor} = {number // divisor} R{number % divisor}",
                f"Check the remainder: {number % divisor}",
                f"Result: {number} is {'DIVISIBLE ✓' if is_divisible else 'NOT DIVISIBLE ✗'} by {divisor}"
            ],
        )
        
        self._validate_question(question)
        return question
    
    # ==================== RENDERING METHODS ====================
    
    def _render_factors_diagram(self, target_number: int, factors: List[int]) -> str:
        """Create HTML factor tree diagram"""
        html = f"""
        <div class="diagram factors-tree">
            <h4>Factor Tree for {target_number}</h4>
            <svg width="500" height="300" style="border: 1px solid #ddd; margin: 10px 0;">
                <text x="250" y="30" text-anchor="middle" font-size="18" font-weight="bold">{target_number}</text>
                <line x1="250" y1="35" x2="250" y2="60" stroke="black" stroke-width="2"/>
                <circle cx="250" cy="80" r="20" fill="lightblue" stroke="black" stroke-width="2"/>
                <text x="250" y="85" text-anchor="middle" font-size="12">{target_number}</text>
            </svg>
            <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #4CAF50;">
                <p><strong>Factors of {target_number}:</strong></p>
                <p style="font-size: 16px; color: #2196F3;">{', '.join(map(str, factors))}</p>
                <p><strong>Total factors:</strong> {len(factors)}</p>
            </div>
        </div>
        """
        return html
    
    def _render_multiples_diagram(self, number: int, count: int, multiples: List[int]) -> str:
        """Create HTML multiples sequence diagram"""
        multiples_str = ' → '.join(map(str, multiples[:min(6, len(multiples))]))
        if len(multiples) > 6:
            multiples_str += " → ..."
        
        html = f"""
        <div class="diagram multiples-sequence">
            <h4>Multiples of {number}</h4>
            <svg width="500" height="150" style="border: 1px solid #ddd; margin: 10px 0;">
                <text x="10" y="30" font-size="14" font-weight="bold">Sequence:</text>
                <text x="10" y="60" font-size="14" fill="#2196F3">{multiples_str}</text>
                <line x1="10" y1="75" x2="490" y2="75" stroke="#ccc" stroke-width="1"/>
                <text x="10" y="100" font-size="12">Each is {number} times a whole number</text>
            </svg>
            <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #FF9800;">
                <p><strong>First {min(count, 10)} multiples of {number}:</strong></p>
                <p style="font-size: 15px; color: #FF5722;">{', '.join(map(str, multiples[:min(count, 10)]))}</p>
            </div>
        </div>
        """
        return html
    
    def _render_gcd_diagram(self, num1: int, num2: int, gcd_result: int) -> str:
        """Create HTML GCD visualization using prime factors"""
        factors1 = self._get_prime_factors(num1)
        factors2 = self._get_prime_factors(num2)
        
        html = f"""
        <div class="diagram gcd-factors">
            <h4>Finding GCD({num1}, {num2})</h4>
            <svg width="500" height="250" style="border: 1px solid #ddd; margin: 10px 0;">
                <text x="250" y="25" text-anchor="middle" font-size="16" font-weight="bold">Prime Factorization</text>
                <text x="50" y="70" font-size="13"><tspan font-weight="bold">{num1} =</tspan> {' × '.join(map(str, factors1))}</text>
                <text x="50" y="100" font-size="13"><tspan font-weight="bold">{num2} =</tspan> {' × '.join(map(str, factors2))}</text>
                <line x1="20" y1="120" x2="480" y2="120" stroke="#ccc" stroke-width="1"/>
                <text x="50" y="155" font-size="13" fill="#4CAF50"><tspan font-weight="bold">GCD =</tspan> {gcd_result}</text>
            </svg>
            <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #4CAF50;">
                <p><strong>Greatest Common Divisor of {num1} and {num2}:</strong></p>
                <p style="font-size: 16px; color: #4CAF50;"><strong>{gcd_result}</strong></p>
                <p><em>The largest number that divides both {num1} and {num2}</em></p>
            </div>
        </div>
        """
        return html
    
    def _render_lcm_diagram(self, num1: int, num2: int, lcm_result: int) -> str:
        """Create HTML LCM visualization"""
        html = f"""
        <div class="diagram lcm-multiples">
            <h4>Finding LCM({num1}, {num2})</h4>
            <svg width="500" height="280" style="border: 1px solid #ddd; margin: 10px 0;">
                <text x="250" y="25" text-anchor="middle" font-size="16" font-weight="bold">Least Common Multiple</text>
                
                <text x="30" y="65" font-size="13" font-weight="bold">Multiples of {num1}:</text>
                <text x="30" y="90" font-size="12" fill="#2196F3">{', '.join(map(str, [num1*i for i in range(1, 6)]))}, ...</text>
                
                <text x="30" y="135" font-size="13" font-weight="bold">Multiples of {num2}:</text>
                <text x="30" y="160" font-size="12" fill="#FF9800">{', '.join(map(str, [num2*i for i in range(1, 6)]))}, ...</text>
                
                <line x1="20" y1="185" x2="480" y2="185" stroke="#ccc" stroke-width="1"/>
                
                <text x="30" y="220" font-size="13" fill="#FF5722"><tspan font-weight="bold">LCM =</tspan> {lcm_result}</text>
                <text x="30" y="245" font-size="11" fill="#666"><em>First common multiple of both numbers</em></text>
            </svg>
            <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #FF5722;">
                <p><strong>Least Common Multiple of {num1} and {num2}:</strong></p>
                <p style="font-size: 16px; color: #FF5722;"><strong>{lcm_result}</strong></p>
            </div>
        </div>
        """
        return html
    
    def _render_divisibility_diagram(self, number: int, divisor: int, is_divisible: bool) -> str:
        """Create HTML divisibility test visualization"""
        quotient = number // divisor
        remainder = number % divisor
        status = "✓ DIVISIBLE" if is_divisible else "✗ NOT DIVISIBLE"
        status_color = "#4CAF50" if is_divisible else "#F44336"
        
        html = f"""
        <div class="diagram divisibility-test">
            <h4>Divisibility Test: {number} ÷ {divisor}</h4>
            <svg width="500" height="250" style="border: 1px solid #ddd; margin: 10px 0;">
                <text x="250" y="30" text-anchor="middle" font-size="18" font-weight="bold">{number} ÷ {divisor}</text>
                
                <rect x="100" y="60" width="150" height="80" fill="lightblue" stroke="black" stroke-width="2"/>
                <text x="175" y="110" text-anchor="middle" font-size="16" font-weight="bold">{quotient}</text>
                <text x="175" y="125" text-anchor="middle" font-size="12">quotient</text>
                
                <text x="300" y="100" font-size="14" font-weight="bold">R {remainder}</text>
                <text x="300" y="120" font-size="11">remainder</text>
                
                <line x1="50" y1="175" x2="450" y2="175" stroke="#ccc" stroke-width="1"/>
                
                <text x="250" y="210" text-anchor="middle" font-size="16" font-weight="bold" fill="{status_color}">{status}</text>
            </svg>
            <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid {status_color};">
                <p><strong>Division Result:</strong></p>
                <p style="font-size: 14px;">{number} = {divisor} × {quotient} + {remainder}</p>
                <p style="font-size: 14px; color: {status_color}; font-weight: bold;">{status}</p>
            </div>
        </div>
        """
        return html
    
    def _get_prime_factors(self, n: int) -> List[int]:
        """Get prime factorization of n"""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
    
    # ==================== UTILITY METHODS ====================
    
    def _difficulty_level_to_int(self, hybrid_diff: HybridDifficultyLevel) -> int:
        """Convert hybrid difficulty to 1-5 scale"""
        mapping = {
            HybridDifficultyLevel.EASY: 1,
            HybridDifficultyLevel.MEDIUM: 2,
            HybridDifficultyLevel.HARD: 3,
            HybridDifficultyLevel.EXPERT: 4,
        }
        return mapping.get(hybrid_diff, 2)
