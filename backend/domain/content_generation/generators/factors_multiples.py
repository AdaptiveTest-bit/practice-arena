"""
INTEGRATED FACTORS & MULTIPLES STRATEGY
========================================

Seamlessly merges:
1. HYBRID NEURO-SYMBOLIC: SymPy-generated skeletons + K.C. Nag storytelling
2. EXISTING ADAPTIVE ENGINE: Misconception-based distractors + Bloom's progression

Result: Indistinguishable integration where both systems enhance each other
"""

from domain.content_generation.generators.base import BaseChapterStrategy
from api.models.quiz import Question, ChapterEnum
from api.models.cognitive_levels import BloomLevel, BloomInfo
from api.models.distractor import MisconceptionType, DistractorSet, DistractorInfo
import random
import math
import time
from typing import List, Tuple, Dict, Any
import sympy
from pathlib import Path

# Import hybrid system components - using relative imports within domain
try:
    from content.generators.factors_multiples import (
        FactorsMultiplesGenerator,
        FactorMultipleConcept,
        DifficultyLevel as HybridDifficultyLevel,
    )
    from content.generators.kc_nag_story import KCNagStoryGeneratorLocal
    from content.renderer import RichQuestionRenderer
    HYBRID_AVAILABLE = True
except ImportError:
    # Fallback: hybrid components not available, use basic generation
    HYBRID_AVAILABLE = False
    
    # Stub DifficultyLevel for standalone use
    from enum import Enum
    class HybridDifficultyLevel(Enum):
        EASY = 1
        MEDIUM = 2
        HARD = 3
        EXPERT = 4

# Import question bank components - DISABLED for now, not needed for generation
# from services.question_bank_loader import QuestionBank, QuestionConstructor

# Import caching - DISABLED for now
# from core.skeleton_cache import get_skeleton_cache


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
        
        # Initialize hybrid components if available
        if HYBRID_AVAILABLE:
            self.sympy_generator = FactorsMultiplesGenerator()
            self.story_generator = KCNagStoryGeneratorLocal()
            self.renderer = RichQuestionRenderer()
        
        # DISABLED: Caching and question bank features not needed for basic generation
        # self.skeleton_cache = get_skeleton_cache()
        # self.question_bank = QuestionBank(...)
        self.use_question_bank = False
    
    # ==================== META + CONCEPT IDS ====================
    # Stable concept IDs for analytics consistency (from taxonomy/math.yaml)
    CONCEPT_IDS = {
        "factors": "math.class5.factors_multiples.factors",
        "multiples": "math.class5.factors_multiples.multiples",
        "gcd": "math.class5.factors_multiples.gcd",
        "lcm": "math.class5.factors_multiples.lcm",
        "divisibility": "math.class5.factors_multiples.divisibility",
        "prime_composite": "math.class5.factors_multiples.prime_composite",
        "factor_pairs": "math.class5.factors_multiples.factor_pairs",
        "prime_factorization": "math.class5.factors_multiples.prime_factorization",
        "word_problem": "math.class5.factors_multiples.word_problem",
        "error_analysis": "math.class5.factors_multiples.error_analysis",
        "assertion_reason": "math.class5.factors_multiples.assertion_reason",
    }
    
    # Problem type → generator method mapping
    PROBLEM_GENERATORS = {
        "factors": "_generate_find_factors_integrated",
        "multiples": "_generate_find_multiples_integrated",
        "gcd": "_generate_find_gcd_integrated",
        "lcm": "_generate_find_lcm_integrated",
        "divisibility": "_generate_divisibility_integrated",
        "prime_composite": "_generate_prime_composite_integrated",
        "factor_pairs": "_generate_factor_pairs_integrated",
        "prime_factorization": "_generate_prime_factorization_integrated",
        "word_problem": "_generate_word_problem_integrated",
        "error_analysis": "_generate_error_analysis_integrated",
        "assertion_reason": "_generate_assertion_reason_integrated",
    }
    
    def _build_meta(self, concept_key: str, difficulty: int, bloom_level: BloomLevel) -> dict:
        """Build standardized meta dict for Question contract compliance."""
        return {
            "subject": "math",
            "grade": 5,
            "chapter": "factors_multiples",
            "chapter_id": "factors_multiples",  # alias for consistency
            "concept_id": self.CONCEPT_IDS.get(concept_key, f"math.class5.factors_multiples.{concept_key}"),
            "concept_key": concept_key,  # short key (e.g., "factors", "gcd")
            "difficulty": difficulty,
            "bloom_level": bloom_level.value if hasattr(bloom_level, 'value') else str(bloom_level),
        }
    
    def _build_misconception_info(self, options: list, distractor_info_list: list, correct_idx: int) -> list:
        """Build misconception_info list with option_index for each option."""
        result = []
        for idx, (option, dist_info) in enumerate(zip(options, distractor_info_list)):
            result.append({
                "option_index": idx,
                "value": option,
                "misconception_type": dist_info.misconception_type.value if hasattr(dist_info.misconception_type, 'value') else str(dist_info.misconception_type),
                "why_wrong": dist_info.why_wrong,
                "teaching_point": dist_info.teaching_point,
                "is_correct": idx == correct_idx,
            })
        return result
    
    # DISABLED: Question bank validation - not needed for basic generation
    # def _validate_question_bank(self) -> bool:
    #     ...
    
    # DISABLED: Generate from question bank - not needed for basic generation  
    # def _generate_from_bank(self, difficulty: int) -> Question:
    #     ...
    
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
        correct_answer = options[0]
        
        # Create distractor info for misconception tracking
        # Note: For correct answer, we use INCOMPLETE_REASONING as placeholder
        distractor_info_list = [
            DistractorInfo(
                value=options[0], 
                misconception_type=MisconceptionType.INCOMPLETE_REASONING, 
                why_wrong="This is the correct answer",
                teaching_point="Well done! You correctly identified both parts."
            ),
            DistractorInfo(
                value=options[1], 
                misconception_type=MisconceptionType.LOGICAL_DISCONNECT, 
                why_wrong="Failed to recognize that the reason directly explains the assertion",
                teaching_point="Look for the logical connection - does the reason provide evidence for the assertion?"
            ),
            DistractorInfo(
                value=options[2], 
                misconception_type=MisconceptionType.SIMILAR_CONCEPT_ERROR, 
                why_wrong="Incorrectly judged the mathematical reason as false",
                teaching_point="Verify each mathematical statement independently before judging their relationship"
            ),
            DistractorInfo(
                value=options[3], 
                misconception_type=MisconceptionType.SIMILAR_CONCEPT_ERROR, 
                why_wrong="Failed to recognize valid mathematical truths",
                teaching_point="Break down complex statements - evaluate assertion and reason separately first"
            ),
        ]
        
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
            rich_html_content=None,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            meta=self._build_meta("assertion_reason", difficulty=3, bloom_level=BloomLevel.ANALYZE),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_option_index),
        )
        
        return question
    
    def generate(self, concept_key: str = None, difficulty: int = None, bloom_level: BloomLevel = None) -> Question:
        """
        Main generation pipeline - supports TARGETED or RANDOM generation.
        
        Args:
            concept_key: Specific concept to generate (e.g., "factors", "gcd", "prime_composite")
                        If None, picks randomly from all available concepts.
            difficulty: Target difficulty 1-5. If None, picks randomly.
            bloom_level: Target Bloom's level. If None, uses concept default.
        
        Returns:
            Question object with full meta and misconception_info.
        
        Usage:
            gen = FactorsMultiplesIntegrated()
            q = gen.generate()  # Random question
            q = gen.generate(concept_key="gcd", difficulty=3)  # Targeted GCD, medium-hard
            q = gen.generate(concept_key="prime_composite")  # Targeted prime/composite
        """
        
        # Determine which concept to generate
        if concept_key is None:
            # Random selection from all problem types
            concept_key = random.choice(list(self.PROBLEM_GENERATORS.keys()))
        
        # Validate concept_key
        if concept_key not in self.PROBLEM_GENERATORS:
            raise ValueError(f"Unknown concept_key: {concept_key}. Valid: {list(self.PROBLEM_GENERATORS.keys())}")
        
        # Get the generator method
        method_name = self.PROBLEM_GENERATORS[concept_key]
        generator_method = getattr(self, method_name)
        
        # Call the generator (difficulty/bloom passed via instance state for now)
        self._target_difficulty = difficulty
        self._target_bloom = bloom_level
        
        return generator_method()
    
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
        
        # Pick difficulty
        hybrid_difficulty = random.choice([
            HybridDifficultyLevel.EASY,
            HybridDifficultyLevel.MEDIUM,
            HybridDifficultyLevel.HARD,
        ])
        
        # Generate target number and factors (with fallback if hybrid unavailable)
        if HYBRID_AVAILABLE:
            skeleton = self.sympy_generator.generate_factor_identification_question(
                difficulty=hybrid_difficulty,
                bloom_level=BloomLevel.UNDERSTAND
            )
            target_number = skeleton.parameters["target_number"]
            factors = skeleton.parameters["factors"]
            latex_problem = skeleton.latex_problem
            solution_steps = skeleton.steps
        else:
            # Standalone fallback generation
            if hybrid_difficulty == HybridDifficultyLevel.EASY:
                target_number = random.choice([6, 8, 10, 12, 15, 18, 20])
            elif hybrid_difficulty == HybridDifficultyLevel.MEDIUM:
                target_number = random.choice([24, 28, 30, 36, 42, 48])
            else:
                target_number = random.choice([56, 60, 72, 84, 90, 100])
            factors = sorted([i for i in range(1, target_number + 1) if target_number % i == 0])
            latex_problem = f"Find all factors of {target_number}."
            solution_steps = [
                f"Test each number from 1 to {target_number}",
                f"If {target_number} ÷ n has no remainder, n is a factor",
                f"Factors: {factors}",
            ]
        
        correct_answer = str(factors)
        
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
        
        # CRITICAL FIX: Ensure options are unique (deduplicate if needed)
        options = self.ensure_unique_option_values(options)
        # Update correct_idx if deduplication changed positions
        if correct_answer in options:
            correct_idx = options.index(correct_answer)
        
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
        from api.models.distractor import DistractorSet
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
            question_text=latex_problem,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=rich_html_content,
            rich_narrative=rich_narrative,
            visual_hints=visual_hints,
            meta=self._build_meta("factors", self._difficulty_level_to_int(hybrid_difficulty), BloomLevel.UNDERSTAND),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
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
        
        # Generate base_number and multiples (with fallback if hybrid unavailable)
        if HYBRID_AVAILABLE:
            skeleton = self.sympy_generator.generate_multiple_identification_question(
                difficulty=hybrid_difficulty,
                bloom_level=BloomLevel.UNDERSTAND
            )
            base_number = skeleton.parameters["base_number"]
            multiples = skeleton.parameters["multiples"]
            latex_problem = skeleton.latex_problem
            solution_steps = skeleton.steps
        else:
            # Standalone fallback generation
            if hybrid_difficulty == HybridDifficultyLevel.EASY:
                base_number = random.choice([2, 3, 4, 5])
                count = 5
            elif hybrid_difficulty == HybridDifficultyLevel.MEDIUM:
                base_number = random.choice([6, 7, 8, 9])
                count = 6
            else:
                base_number = random.choice([11, 12, 13, 15])
                count = 7
            multiples = [base_number * i for i in range(1, count + 1)]
            latex_problem = f"Find the first {count} multiples of {base_number}."
            solution_steps = [
                f"Multiply {base_number} by 1, 2, 3, ... up to {count}",
                f"First {count} multiples: {multiples}",
            ]
        
        correct_answer = str(multiples)
        
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
            question_text=latex_problem,
            solution_steps=solution_steps,
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
            meta=self._build_meta("multiples", self._difficulty_level_to_int(hybrid_difficulty), BloomLevel.UNDERSTAND),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
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
            meta=self._build_meta("gcd", difficulty=2, bloom_level=BloomLevel.APPLY),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
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
        
        # ADAPTIVE: Generate diverse, unique distractors
        # Build pool of potential distractors
        gcd_val = math.gcd(a, b)
        product = a * b
        
        distractor_pool = []
        
        # Distractor 1: Product (common misconception)
        if product != lcm_value:
            distractor_pool.append((
                str(product),
                MisconceptionType.FORMULA_MISAPPLICATION,
                "Multiplying instead of finding LCM",
                "Student multiplied the numbers",
                "LCM is usually smaller than the product; only equal when numbers are coprime"
            ))
        
        # Distractor 2: GCD (formula confusion)
        if gcd_val != lcm_value:
            distractor_pool.append((
                str(gcd_val),
                MisconceptionType.FORMULA_CONFUSION,
                "Finding GCD instead of LCM",
                "Student found GCD instead of LCM",
                "LCM is the smallest multiple, GCD is the largest divisor"
            ))
        
        # Distractor 3: Larger number
        max_val = max(a, b)
        if max_val != lcm_value:
            distractor_pool.append((
                str(max_val),
                MisconceptionType.INCOMPLETE_REASONING,
                "Using the larger number without checking",
                "Student just took the larger number",
                "The larger number may not be a multiple of the smaller one"
            ))
        
        # Distractor 4: Sum (arithmetic confusion)
        sum_val = a + b
        if sum_val != lcm_value and sum_val not in [product, gcd_val, max_val]:
            distractor_pool.append((
                str(sum_val),
                MisconceptionType.ARITHMETIC_ERROR,
                "Adding instead of finding LCM",
                "Student added the numbers instead",
                "LCM is about common multiples, not addition"
            ))
        
        # Distractor 5: Half of product (partial calculation)
        half_product = product // 2
        if half_product != lcm_value and half_product not in [product, gcd_val, max_val, sum_val]:
            distractor_pool.append((
                str(half_product),
                MisconceptionType.INCOMPLETE_REASONING,
                "Incomplete calculation",
                "Student found half the product",
                "Keep looking for the smallest common multiple"
            ))
        
        # Distractor 6: LCM/2 (off by factor)
        if lcm_value > 2:
            half_lcm = lcm_value // 2
            if half_lcm not in [gcd_val, max_val]:
                distractor_pool.append((
                    str(half_lcm),
                    MisconceptionType.ARITHMETIC_ERROR,
                    "Off by a factor",
                    "Student found half the LCM",
                    "This divides one number but not both"
                ))
        
        # Distractor 7: LCM*2 (double the answer)
        double_lcm = lcm_value * 2
        if double_lcm < 200:  # Keep numbers reasonable
            distractor_pool.append((
                str(double_lcm),
                MisconceptionType.ARITHMETIC_ERROR,
                "Double the correct answer",
                "Student found twice the LCM",
                "We want the SMALLEST common multiple"
            ))
        
        # Select 3 unique distractors from pool
        random.shuffle(distractor_pool)
        selected_distractors = []
        seen_values = {correct_answer}
        
        for dist_data in distractor_pool:
            if dist_data[0] not in seen_values:
                selected_distractors.append(dist_data)
                seen_values.add(dist_data[0])
                if len(selected_distractors) == 3:
                    break
        
        # If we still don't have 3, generate arithmetic variations
        while len(selected_distractors) < 3:
            # Try nearby values
            nearby = lcm_value + random.choice([-3, -2, -1, 1, 2, 3])
            if nearby > 0 and str(nearby) not in seen_values:
                selected_distractors.append((
                    str(nearby),
                    MisconceptionType.ARITHMETIC_ERROR,
                    "Close but incorrect",
                    "Off-by-one or calculation error",
                    "Double-check your multiplication and division"
                ))
                seen_values.add(str(nearby))
        
        # Build final options dict
        option_distractors = {
            0: (
                correct_answer,
                None,
                "The smallest number divisible by both",
                None,
                None
            ),
        }
        
        for i, dist_data in enumerate(selected_distractors[:3], start=1):
            option_distractors[i] = dist_data
        
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
            meta=self._build_meta("lcm", difficulty=2, bloom_level=BloomLevel.APPLY),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
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
            meta=self._build_meta("divisibility", difficulty=1, bloom_level=BloomLevel.REMEMBER),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 6: PRIME VS COMPOSITE ====================
    
    def _generate_prime_composite_integrated(self) -> Question:
        """Classify numbers as prime or composite (Remember/Understand level)"""
        
        # Generate a mix of prime and composite numbers
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28]
        
        # Pick a number to classify
        if random.random() < 0.5:
            number = random.choice(primes)
            is_prime = True
            correct_answer = "Prime"
        else:
            number = random.choice(composites)
            is_prime = False
            correct_answer = "Composite"
        
        # Get factors for explanation
        factors = sorted([i for i in range(1, number + 1) if number % i == 0])
        
        option_distractors = {
            0: (correct_answer, None, "Correct classification", None, None),
            1: ("Composite" if is_prime else "Prime", MisconceptionType.OPPOSITE_CONFUSION,
                "Opposite classification", "Student confused prime and composite definitions",
                "Prime = exactly 2 factors (1 and itself); Composite = more than 2 factors"),
            2: ("Neither", MisconceptionType.INCOMPLETE_REASONING,
                "Thinks it's neither", "Student unsure of classification",
                "Every number > 1 is either prime or composite (except 1, which is neither)"),
            3: ("Cannot determine", MisconceptionType.INCOMPLETE_REASONING,
                "Uncertain", "Student doesn't know how to check",
                "Count the factors: if exactly 2 → prime; if more → composite"),
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
                    value=option_text, misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer", why_wrong="This is correct", teaching_point="Well done!"))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text, misconception_type=misconception,
                    description=short_desc, why_wrong=why_wrong, teaching_point=teaching))
        
        trap_info = self.create_trap_info(MisconceptionType.OPPOSITE_CONFUSION, difficulty=1,
            custom_description="Confusing prime and composite definitions",
            custom_why_effective="Both terms sound similar and involve factors",
            custom_how_to_avoid="Prime = exactly 2 factors; Composite = more than 2 factors")
        
        bloom_info = self.create_bloom_info(BloomLevel.REMEMBER, trap_difficulty=1)
        
        steps = [
            f"Number: {number}",
            f"Factors of {number}: {factors}",
            f"Count of factors: {len(factors)}",
            f"If count = 2 → Prime; If count > 2 → Composite",
            f"Result: {number} is {correct_answer.upper()}"
        ]
        
        question = Question(
            chapter=self.chapter,
            topic="Number Theory - Prime and Composite Numbers",
            logical_trap="K.C. Nag Trap: Students confuse prime and composite definitions.",
            data_representation=f"```\nNumber: {number}\nFactors: {factors}\nCount: {len(factors)}\n```",
            question_text=f"Is {number} a prime number or a composite number?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=self._render_prime_composite_diagram(number, factors, is_prime),
            rich_narrative=f"To classify {number}, we count its factors: {factors}. A prime number has exactly 2 factors (1 and itself). A composite number has more than 2 factors. Since {number} has {len(factors)} factors, it is {correct_answer.lower()}.",
            visual_hints=[
                f"List all factors of {number}: {', '.join(map(str, factors))}",
                f"Count them: {len(factors)} factors",
                "Prime = exactly 2 factors (1 and itself)",
                "Composite = more than 2 factors",
                f"{number} has {len(factors)} factors → {correct_answer}"
            ],
            meta=self._build_meta("prime_composite", difficulty=1, bloom_level=BloomLevel.REMEMBER),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 7: FACTOR PAIRS ====================
    
    def _generate_factor_pairs_integrated(self) -> Question:
        """Find all factor pairs of a number (Understand level)"""
        
        # Pick a number with interesting factor pairs
        numbers = [12, 18, 24, 30, 36, 48, 60, 72]
        number = random.choice(numbers)
        
        # Calculate factor pairs
        factor_pairs = []
        for i in range(1, int(number ** 0.5) + 1):
            if number % i == 0:
                factor_pairs.append((i, number // i))
        
        correct_answer = str(factor_pairs)
        
        # Generate distractors
        # Missing some pairs
        distractor1 = str(factor_pairs[:-1])
        # Including invalid pair
        distractor2 = str(factor_pairs + [(number, 1)])  # duplicate in different order
        # Wrong pairs
        distractor3 = str([(1, number), (2, number // 3)])  # incorrect math
        
        option_distractors = {
            0: (correct_answer, None, "All valid factor pairs", None, None),
            1: (distractor1, MisconceptionType.INCOMPLETE_REASONING,
                "Missing factor pairs", "Student didn't find all pairs",
                "Check all numbers from 1 to √n systematically"),
            2: (distractor2, MisconceptionType.CONSTRAINT_VIOLATION,
                "Duplicate pairs in different order", "Student listed (a,b) and (b,a) separately",
                "Each pair should be listed once; (2,6) and (6,2) are the same pair"),
            3: (distractor3, MisconceptionType.ARITHMETIC_ERROR,
                "Incorrect factor pairs", "Student made calculation errors",
                "Verify each pair: a × b should equal the target number"),
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
                    value=option_text, misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer", why_wrong="This is correct", teaching_point="Well done!"))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text, misconception_type=misconception,
                    description=short_desc, why_wrong=why_wrong, teaching_point=teaching))
        
        trap_info = self.create_trap_info(MisconceptionType.INCOMPLETE_REASONING, difficulty=2,
            custom_description="Missing factor pairs or counting duplicates",
            custom_why_effective="Factor pairs require systematic search",
            custom_how_to_avoid="Test 1, 2, 3, ... up to √n; record each pair once")
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        steps = [
            f"Number: {number}",
            f"Find pairs (a, b) where a × b = {number}",
            f"Test: 1 × {number} = {number} ✓ → (1, {number})",
        ] + [f"Test: {p[0]} × {p[1]} = {number} ✓ → {p}" for p in factor_pairs[1:]] + [
            f"All factor pairs: {factor_pairs}"
        ]
        
        question = Question(
            chapter=self.chapter,
            topic="Number Theory - Factor Pairs",
            logical_trap="K.C. Nag Trap: Students miss factor pairs or list duplicates.",
            data_representation=f"```\nNumber: {number}\nFind all (a, b) where a × b = {number}\n```",
            question_text=f"Find all factor pairs of {number}.",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=self._render_factor_pairs_diagram(number, factor_pairs),
            rich_narrative=f"A factor pair of {number} is two numbers that multiply to give {number}. We find all such pairs by testing: 1 × {number}, 2 × ?, etc. The complete set of factor pairs is {factor_pairs}.",
            visual_hints=[
                f"Start with (1, {number}) - always a factor pair",
                f"Try 2: Does 2 divide {number}? {'Yes' if number % 2 == 0 else 'No'}",
                f"Continue up to √{number} ≈ {int(number ** 0.5)}",
                f"Each pair (a, b) should satisfy a × b = {number}",
                f"Don't double-count: (2, 6) and (6, 2) are the same pair"
            ],
            meta=self._build_meta("factor_pairs", difficulty=2, bloom_level=BloomLevel.UNDERSTAND),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 8: PRIME FACTORIZATION ====================
    
    def _generate_prime_factorization_integrated(self) -> Question:
        """Find prime factorization of a number (Apply level)"""
        
        # Numbers with interesting prime factorizations
        numbers = [12, 18, 24, 30, 36, 48, 60, 72, 84, 90, 100, 120]
        number = random.choice(numbers)
        
        # Calculate prime factorization using SymPy
        prime_factors = sympy.factorint(number)
        # Format as list: {2: 3, 3: 1} → [2, 2, 2, 3]
        factor_list = []
        for prime, count in sorted(prime_factors.items()):
            factor_list.extend([prime] * count)
        
        correct_answer = " × ".join(map(str, factor_list))
        
        # Generate distractors
        # Missing a factor
        distractor1 = " × ".join(map(str, factor_list[:-1]))
        # Wrong factors
        distractor2 = " × ".join(map(str, [4] + factor_list[2:])) if len(factor_list) > 2 else "4 × " + str(number // 4)
        # All factors, not just primes
        all_factors = sorted([i for i in range(1, number + 1) if number % i == 0])
        distractor3 = " × ".join(map(str, [all_factors[1], all_factors[-2]])) if len(all_factors) > 2 else "2 × " + str(number // 2)
        
        option_distractors = {
            0: (correct_answer, None, "Complete prime factorization", None, None),
            1: (distractor1, MisconceptionType.INCOMPLETE_REASONING,
                "Incomplete factorization", "Student stopped too early",
                "Keep factoring until all factors are prime"),
            2: (distractor2, MisconceptionType.CONSTRAINT_VIOLATION,
                "Contains composite factors", "Student included non-prime factors",
                "4 is not prime (4 = 2 × 2); break it down further"),
            3: (distractor3, MisconceptionType.FORMULA_CONFUSION,
                "Uses non-prime factors", "Student confused factors with prime factors",
                "Prime factorization uses only prime numbers (2, 3, 5, 7, 11, ...)"),
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
                    value=option_text, misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer", why_wrong="This is correct", teaching_point="Well done!"))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text, misconception_type=misconception,
                    description=short_desc, why_wrong=why_wrong, teaching_point=teaching))
        
        trap_info = self.create_trap_info(MisconceptionType.INCOMPLETE_REASONING, difficulty=2,
            custom_description="Stopping before complete prime factorization",
            custom_why_effective="Students stop when they see small factors",
            custom_how_to_avoid="Keep dividing until all factors are prime numbers")
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        steps = [
            f"Number: {number}",
            f"Start by dividing by smallest prime (2):",
        ]
        temp = number
        for prime in factor_list:
            steps.append(f"{temp} ÷ {prime} = {temp // prime}")
            temp = temp // prime
        steps.append(f"Prime factorization: {correct_answer}")
        
        question = Question(
            chapter=self.chapter,
            topic="Number Theory - Prime Factorization",
            logical_trap="K.C. Nag Trap: Students include composite factors or stop too early.",
            data_representation=f"```\nNumber: {number}\nFind: prime factors only\n```",
            question_text=f"What is the prime factorization of {number}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=self._render_prime_factorization_diagram(number, factor_list),
            rich_narrative=f"Prime factorization breaks {number} into a product of prime numbers only. We repeatedly divide by the smallest prime that divides evenly. The result is {correct_answer}.",
            visual_hints=[
                f"Start: {number}",
                "Divide by 2 repeatedly until odd",
                "Then try 3, 5, 7, ... (primes only)",
                "Stop when you reach 1",
                f"Result: {correct_answer}"
            ],
            meta=self._build_meta("prime_factorization", difficulty=2, bloom_level=BloomLevel.APPLY),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 9: WORD PROBLEMS ====================
    
    def _generate_word_problem_integrated(self) -> Question:
        """Real-world word problems involving factors, multiples, GCD, LCM (Apply/Analyze level)"""
        
        problem_type = random.choice(["lcm_scheduling", "gcd_grouping", "factor_arrangement"])
        
        if problem_type == "lcm_scheduling":
            # Two events with different cycles - when do they coincide?
            cycle1 = random.choice([3, 4, 5, 6])
            cycle2 = random.choice([4, 5, 6, 8])
            while cycle1 == cycle2:
                cycle2 = random.choice([4, 5, 6, 8])
            
            lcm_value = int(sympy.lcm(cycle1, cycle2))
            
            contexts = [
                (f"Bus A comes every {cycle1} minutes. Bus B comes every {cycle2} minutes. If both buses just arrived together, after how many minutes will they arrive together again?",
                 "bus schedules", "minutes"),
                (f"Riya waters her plants every {cycle1} days. She fertilizes them every {cycle2} days. If she did both today, after how many days will she do both together again?",
                 "gardening schedule", "days"),
                (f"A red light blinks every {cycle1} seconds. A blue light blinks every {cycle2} seconds. If they just blinked together, after how many seconds will they blink together again?",
                 "blinking lights", "seconds"),
            ]
            
            question_text, context, unit = random.choice(contexts)
            correct_answer = str(lcm_value)
            concept_key = "word_problem"
            
            steps = [
                f"This is an LCM problem - finding when cycles coincide",
                f"Cycle 1: every {cycle1} {unit}",
                f"Cycle 2: every {cycle2} {unit}",
                f"LCM({cycle1}, {cycle2}) = {lcm_value}",
                f"Answer: {lcm_value} {unit}"
            ]
            
            distractors = [
                (str(cycle1 * cycle2), MisconceptionType.FORMULA_MISAPPLICATION, "Product instead of LCM"),
                (str(cycle1 + cycle2), MisconceptionType.OPERATION_SELECTION, "Added instead of LCM"),
                (str(max(cycle1, cycle2)), MisconceptionType.INCOMPLETE_REASONING, "Took larger cycle"),
            ]
            
        elif problem_type == "gcd_grouping":
            # Divide items into equal groups
            items1 = random.choice([12, 18, 24, 30])
            items2 = random.choice([15, 20, 24, 36])
            while items1 == items2:
                items2 = random.choice([15, 20, 24, 36])
            
            gcd_value = math.gcd(items1, items2)
            
            contexts = [
                (f"A teacher has {items1} pencils and {items2} erasers. She wants to make identical gift bags with the same number of pencils and erasers in each bag (using all items). What is the maximum number of bags she can make?",
                 "gift bags", "bags"),
                (f"A florist has {items1} red roses and {items2} white roses. She wants to make identical bouquets using all the roses. What is the maximum number of bouquets she can make?",
                 "flower bouquets", "bouquets"),
            ]
            
            question_text, context, unit = random.choice(contexts)
            correct_answer = str(gcd_value)
            concept_key = "word_problem"
            
            steps = [
                f"This is a GCD problem - finding maximum equal groups",
                f"Items: {items1} and {items2}",
                f"GCD({items1}, {items2}) = {gcd_value}",
                f"Maximum {unit}: {gcd_value}"
            ]
            
            distractors = [
                (str(items1 * items2), MisconceptionType.FORMULA_MISAPPLICATION, "Product instead of GCD"),
                (str(min(items1, items2)), MisconceptionType.INCOMPLETE_REASONING, "Took smaller number"),
                (str(int(sympy.lcm(items1, items2))), MisconceptionType.FORMULA_CONFUSION, "Found LCM instead of GCD"),
            ]
            
        else:  # factor_arrangement
            # Arrange items in rows/columns
            total = random.choice([24, 30, 36, 48, 60])
            factors = sorted([i for i in range(1, total + 1) if total % i == 0])
            
            question_text = f"A gardener has {total} plants. In how many different ways can she arrange them in equal rows?"
            correct_answer = str(len(factors))
            concept_key = "word_problem"
            
            steps = [
                f"Total plants: {total}",
                f"Find all factors of {total}: {factors}",
                f"Each factor represents a valid row arrangement",
                f"Number of arrangements: {len(factors)}"
            ]
            
            distractors = [
                (str(len(factors) - 2), MisconceptionType.INCOMPLETE_REASONING, "Missing some factors"),
                (str(total), MisconceptionType.CONSTRAINT_VIOLATION, "Used total instead of factor count"),
                (str(factors[-1]), MisconceptionType.FORMULA_CONFUSION, "Gave largest factor"),
            ]
        
        # Build options
        option_distractors = {
            0: (correct_answer, None, "Correct answer", None, None),
        }
        for i, (val, misc, desc) in enumerate(distractors, start=1):
            option_distractors[i] = (val, misc, desc, f"Student {desc.lower()}", f"Review the problem type: GCD for grouping, LCM for schedules")
        
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
                    value=option_text, misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer", why_wrong="This is correct", teaching_point="Well done!"))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text, misconception_type=misconception,
                    description=short_desc, why_wrong=why_wrong or "", teaching_point=teaching or ""))
        
        trap_info = self.create_trap_info(MisconceptionType.OPERATION_SELECTION, difficulty=3,
            custom_description="Choosing wrong operation (GCD vs LCM vs factors)",
            custom_why_effective="Word problems require identifying the underlying concept",
            custom_how_to_avoid="GCD for 'maximum equal groups'; LCM for 'when cycles meet'; Factors for 'arrangement options'")
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=3)
        
        question = Question(
            chapter=self.chapter,
            topic="Word Problems - Factors & Multiples",
            logical_trap="K.C. Nag Trap: Students struggle to identify GCD vs LCM vs factor-counting problems.",
            data_representation=f"```\nProblem Type: {problem_type}\nKey Operation: {'LCM' if 'lcm' in problem_type else 'GCD' if 'gcd' in problem_type else 'Factors'}\n```",
            question_text=question_text,
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=None,
            rich_narrative=f"This is a real-world application of {'LCM' if 'lcm' in problem_type else 'GCD' if 'gcd' in problem_type else 'factors'}. Identifying the correct operation is key to solving word problems.",
            visual_hints=[
                "Read the problem carefully - what are we looking for?",
                "'When will events coincide?' → LCM",
                "'Maximum equal groups?' → GCD",
                "'How many arrangements?' → Count factors",
                "Apply the correct formula"
            ],
            meta=self._build_meta("word_problem", difficulty=3, bloom_level=BloomLevel.APPLY),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PHASE 10: ERROR ANALYSIS ====================
    
    def _generate_error_analysis_integrated(self) -> Question:
        """'Which student is correct?' format (Evaluate level)"""
        
        scenario = random.choice(["factor_error", "multiple_error", "gcd_error", "lcm_error"])
        
        if scenario == "factor_error":
            number = random.choice([24, 36, 48])
            correct_factors = sorted([i for i in range(1, number + 1) if number % i == 0])
            
            student_a = f"The factors of {number} are: {correct_factors}"
            student_b = f"The factors of {number} are: {[f for f in correct_factors if f != 1]}"  # missing 1
            student_c = f"The factors of {number} are: {[f for f in correct_factors if f != number]}"  # missing number
            
            correct_student = "Student A"
            question_text = f"Three students listed the factors of {number}:\n\n**Student A:** {correct_factors}\n**Student B:** {[f for f in correct_factors if f != 1]}\n**Student C:** {[f for f in correct_factors if f != number]}\n\nWhich student is correct?"
            
            explanation = f"Student A is correct. Student B forgot that 1 is always a factor. Student C forgot that {number} is a factor of itself."
            
        elif scenario == "multiple_error":
            base = random.choice([6, 7, 8])
            correct_multiples = [base * i for i in range(1, 6)]
            
            student_a = f"First 5 multiples of {base}: {correct_multiples}"
            student_b = f"First 5 multiples of {base}: {[0] + correct_multiples[:4]}"  # starts with 0
            student_c = f"First 5 multiples of {base}: {[base * i for i in range(2, 7)]}"  # skips first
            
            correct_student = "Student A"
            question_text = f"Three students found the first 5 multiples of {base}:\n\n**Student A:** {correct_multiples}\n**Student B:** {[0] + correct_multiples[:4]}\n**Student C:** {[base * i for i in range(2, 7)]}\n\nWhich student is correct?"
            
            explanation = f"Student A is correct. Student B incorrectly included 0 as a multiple. Student C started from 2 × {base} instead of 1 × {base}."
            
        elif scenario == "gcd_error":
            a, b = random.choice([(12, 18), (24, 36), (15, 25)])
            gcd_val = math.gcd(a, b)
            
            student_a = f"GCD({a}, {b}) = {gcd_val}"
            student_b = f"GCD({a}, {b}) = {min(a, b)}"
            student_c = f"GCD({a}, {b}) = {a * b}"
            
            correct_student = "Student A"
            question_text = f"Three students found the GCD of {a} and {b}:\n\n**Student A:** {gcd_val}\n**Student B:** {min(a, b)}\n**Student C:** {a * b}\n\nWhich student is correct?"
            
            explanation = f"Student A is correct (GCD = {gcd_val}). Student B just took the smaller number without checking. Student C multiplied instead of finding GCD."
            
        else:  # lcm_error
            a, b = random.choice([(4, 6), (3, 5), (6, 8)])
            lcm_val = int(sympy.lcm(a, b))
            
            student_a = f"LCM({a}, {b}) = {lcm_val}"
            student_b = f"LCM({a}, {b}) = {a * b}"
            student_c = f"LCM({a}, {b}) = {math.gcd(a, b)}"
            
            correct_student = "Student A"
            question_text = f"Three students found the LCM of {a} and {b}:\n\n**Student A:** {lcm_val}\n**Student B:** {a * b}\n**Student C:** {math.gcd(a, b)}\n\nWhich student is correct?"
            
            explanation = f"Student A is correct (LCM = {lcm_val}). Student B multiplied (product ≠ LCM unless coprime). Student C found GCD instead of LCM."
        
        option_distractors = {
            0: ("Student A", None, "Correct student", None, None),
            1: ("Student B", MisconceptionType.INCOMPLETE_REASONING, "Student B's error", 
                "Student B made a common error", "Review the definition"),
            2: ("Student C", MisconceptionType.FORMULA_CONFUSION, "Student C's error",
                "Student C confused concepts", "Review the correct formula"),
            3: ("All are correct", MisconceptionType.CONSTRAINT_VIOLATION, "Thinks all are right",
                "Student didn't check carefully", "Only one answer can be correct"),
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
                    value=option_text, misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description="Correct answer", why_wrong="This is correct", teaching_point="Well done!"))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=option_text, misconception_type=misconception,
                    description=short_desc, why_wrong=why_wrong, teaching_point=teaching))
        
        trap_info = self.create_trap_info(MisconceptionType.INCOMPLETE_REASONING, difficulty=3,
            custom_description="Not carefully checking each student's work",
            custom_why_effective="Requires evaluating multiple solutions",
            custom_how_to_avoid="Check each student's answer against the correct method")
        
        bloom_info = self.create_bloom_info(BloomLevel.EVALUATE, trap_difficulty=3)
        
        question = Question(
            chapter=self.chapter,
            topic="Error Analysis - Factors & Multiples",
            logical_trap="K.C. Nag Trap: Students must identify which solution is correct and why others are wrong.",
            data_representation=f"```\nScenario: {scenario}\nCorrect: {correct_student}\n```",
            question_text=question_text,
            solution_steps=[
                "Check each student's answer:",
                f"Student A: {explanation.split('.')[0]}",
                f"Student B: {explanation.split('.')[1] if len(explanation.split('.')) > 1 else 'Made an error'}",
                f"Student C: {explanation.split('.')[2] if len(explanation.split('.')) > 2 else 'Made an error'}",
                f"Answer: {correct_student}"
            ],
            answer=correct_student,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_student, distractors=[d for d in distractor_info_list if d.value != correct_student]),
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=None,
            rich_narrative=explanation,
            visual_hints=[
                "Read each student's answer carefully",
                "Check against the correct definition/method",
                "Identify the specific error in wrong answers",
                "Only one student can be correct"
            ],
            meta=self._build_meta("error_analysis", difficulty=3, bloom_level=BloomLevel.EVALUATE),
            misconception_info=self._build_misconception_info(options, distractor_info_list, correct_idx),
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
    
    def _render_prime_composite_diagram(self, number: int, factors: List[int], is_prime: bool) -> str:
        """Create HTML prime/composite visualization"""
        status = "PRIME" if is_prime else "COMPOSITE"
        status_color = "#4CAF50" if is_prime else "#2196F3"
        factors_display = ', '.join(map(str, factors))
        
        html = f"""
        <div class="diagram prime-composite">
            <h4>Is {number} Prime or Composite?</h4>
            <svg width="500" height="200" style="border: 1px solid #ddd; margin: 10px 0;">
                <circle cx="250" cy="80" r="50" fill="{status_color}" opacity="0.3" stroke="{status_color}" stroke-width="3"/>
                <text x="250" y="90" text-anchor="middle" font-size="24" font-weight="bold">{number}</text>
                
                <text x="250" y="160" text-anchor="middle" font-size="16" font-weight="bold" fill="{status_color}">{status}</text>
                <text x="250" y="185" text-anchor="middle" font-size="12" fill="#666">Factors: {factors_display}</text>
            </svg>
            <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid {status_color};">
                <p><strong>{number}</strong> is <strong style="color: {status_color};">{status}</strong></p>
                <p style="font-size: 12px;">Factors: {factors_display}</p>
                <p style="font-size: 11px; color: #666;">{'Only 2 factors (1 and itself) → Prime' if is_prime else 'More than 2 factors → Composite'}</p>
            </div>
        </div>
        """
        return html
    
    def _render_factor_pairs_diagram(self, number: int, factor_pairs: List[tuple]) -> str:
        """Create HTML factor pairs visualization"""
        pairs_display = ', '.join([f"({a}×{b})" for a, b in factor_pairs])
        
        # Build SVG elements for factor pairs (max 4 shown)
        pair_elements = []
        for i, (a, b) in enumerate(factor_pairs[:4]):
            x_offset = 50 + i * 100
            pair_elements.append(f'''
                <g transform="translate({x_offset}, 70)">
                    <rect width="80" height="60" fill="lightblue" stroke="#2196F3" stroke-width="2" rx="5"/>
                    <text x="40" y="25" text-anchor="middle" font-size="14" font-weight="bold">{a}×{b}</text>
                    <text x="40" y="45" text-anchor="middle" font-size="12">=</text>
                    <text x="40" y="55" text-anchor="middle" font-size="12">{number}</text>
                </g>''')
        svg_pairs = ''.join(pair_elements)
        
        html = f"""
        <div class="diagram factor-pairs">
            <h4>Factor Pairs of {number}</h4>
            <svg width="500" height="220" style="border: 1px solid #ddd; margin: 10px 0;">
                <text x="250" y="30" text-anchor="middle" font-size="16" font-weight="bold">Finding pairs that multiply to {number}</text>
                {svg_pairs}
                <text x="250" y="170" text-anchor="middle" font-size="14" fill="#4CAF50"><tspan font-weight="bold">{len(factor_pairs)}</tspan> factor pair(s)</text>
            </svg>
            <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #2196F3;">
                <p><strong>All Factor Pairs of {number}:</strong></p>
                <p style="font-size: 14px;">{pairs_display}</p>
            </div>
        </div>
        """
        return html
    
    def _render_prime_factorization_diagram(self, number: int, prime_factors: List[int]) -> str:
        """Create HTML prime factorization tree"""
        from collections import Counter
        factor_counts = Counter(prime_factors)
        factorization_str = ' × '.join([f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(factor_counts.items())])
        expanded_str = ' × '.join(map(str, prime_factors))
        
        html = f"""
        <div class="diagram prime-factorization">
            <h4>Prime Factorization of {number}</h4>
            <svg width="500" height="220" style="border: 1px solid #ddd; margin: 10px 0;">
                <text x="250" y="30" text-anchor="middle" font-size="18" font-weight="bold">{number}</text>
                <line x1="250" y1="35" x2="250" y2="55" stroke="black" stroke-width="2"/>
                
                <text x="250" y="80" text-anchor="middle" font-size="14">↓ Factor Tree ↓</text>
                
                <text x="250" y="120" text-anchor="middle" font-size="14" fill="#2196F3">{expanded_str}</text>
                
                <line x1="100" y1="145" x2="400" y2="145" stroke="#ccc" stroke-width="1"/>
                
                <text x="250" y="175" text-anchor="middle" font-size="16" font-weight="bold" fill="#4CAF50">{factorization_str}</text>
                <text x="250" y="200" text-anchor="middle" font-size="11" fill="#666">Prime Factorization</text>
            </svg>
            <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #4CAF50;">
                <p><strong>Prime Factorization of {number}:</strong></p>
                <p style="font-size: 16px; color: #4CAF50;"><strong>{factorization_str}</strong></p>
                <p style="font-size: 12px;">= {expanded_str}</p>
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
    
    def _difficulty_level_to_int(self, hybrid_diff) -> int:
        """Convert hybrid difficulty to 1-5 scale"""
        if not HYBRID_AVAILABLE or HybridDifficultyLevel is None:
            return 2  # Default medium difficulty
        
        mapping = {
            HybridDifficultyLevel.EASY: 1,
            HybridDifficultyLevel.MEDIUM: 2,
            HybridDifficultyLevel.HARD: 3,
            HybridDifficultyLevel.EXPERT: 4,
        }
        return mapping.get(hybrid_diff, 2)
