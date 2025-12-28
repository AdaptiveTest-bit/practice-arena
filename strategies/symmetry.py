"""Symmetry & Reflection question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
import random
from models.distractor import MisconceptionType


class SymmetryStrategy(BaseChapterStrategy):
    """Generates symmetry and reflection problems."""
    
    chapter = ChapterEnum.SYMMETRY
    chapter_name = "Symmetry"
    description = "Letter & word symmetry"
    
    def generate(self) -> Question:
        """Generate a symmetry question."""
        problem_type = random.choice([
            "letter_symmetry",
            "word_symmetry",
            "shape_reflection",
            "line_symmetry",
            "rotational_symmetry",
            "symmetric_count"
        ])
        
        if problem_type == "letter_symmetry":
            return self._generate_letter_symmetry()
        elif problem_type == "word_symmetry":
            return self._generate_word_symmetry()
        elif problem_type == "shape_reflection":
            return self._generate_shape_reflection()
        elif problem_type == "line_symmetry":
            return self._generate_line_symmetry()
        elif problem_type == "rotational_symmetry":
            return self._generate_rotational_symmetry()
        else:
            return self._generate_symmetric_count()
    
    def _generate_letter_symmetry(self) -> Question:
        """Identify symmetric letters."""
        symmetric_letters = ['A', 'H', 'I', 'M', 'O', 'T', 'U', 'V', 'W', 'X', 'Y']
        asymmetric_letters = ['B', 'C', 'D', 'E', 'F', 'G', 'J', 'K', 'L', 'N', 'P']
        
        test_letter = random.choice(symmetric_letters)
        correct_answer = f"{test_letter} - Symmetric"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"{test_letter} - Not symmetric",  # Denies correct symmetry
            MisconceptionType.SIMILAR_CONCEPT_ERROR: 
                f"{random.choice(asymmetric_letters)} - Symmetric",  # Identifies wrong letter
            MisconceptionType.INCOMPLETE_REASONING: 
                "None"  # Doesn't answer properly
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Letter Symmetry",
            logical_trap="K.C. Nag trap: Students confuse symmetrical letters with asymmetrical ones. "
                        "Check if letter can be folded in half exactly.",
            data_representation=f"```\nSymmetric letters: A, H, I, M, O, T, U, V, W, X, Y\n"
                               f"Asymmetric letters: B, C, D, E, F, G, J, K, L, N, P\n"
                               f"Test letter: {test_letter}\n```",
            question_text=f"Is the letter '{test_letter}' symmetrical?",
            solution_steps=[
                f"Letter: {test_letter}",
                "Check if it has a line of symmetry",
                f"Can fold {test_letter} in half: Yes",
                f"Answer: {test_letter} is symmetric"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.PATTERN_MISIDENTIFICATION, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_word_symmetry(self) -> Question:
        """Identify symmetric words."""
        symmetric_words = ['MOM', 'DAD', 'POP', 'SOS', 'NOON']
        asymmetric_words = ['BAT', 'CAT', 'DOG', 'APPLE', 'TREE']
        
        test_word = random.choice(symmetric_words)
        correct_answer = f"{test_word} - Palindrome (Symmetric)"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"{test_word} - Not symmetric",  # Denies correct palindrome
            MisconceptionType.SIMILAR_CONCEPT_ERROR: 
                f"{random.choice(asymmetric_words)} - Symmetric",  # Wrong word choice
            MisconceptionType.INCOMPLETE_REASONING: 
                "None"  # Doesn't answer
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Word Symmetry",
            logical_trap="Students don't recognize palindromes. Symmetric words read the same forwards and backwards.",
            data_representation=f"```\nSymmetric words (Palindromes): MOM, DAD, POP, SOS, NOON\n"
                               f"Test word: {test_word}\n"
                               f"Reversed: {test_word[::-1]}\nSame? {test_word == test_word[::-1]}\n```",
            question_text=f"Is '{test_word}' a symmetric (palindrome) word?",
            solution_steps=[
                f"Word: {test_word}",
                f"Reverse it: {test_word[::-1]}",
                f"Compare: {test_word} = {test_word[::-1]}? Yes",
                f"Answer: {test_word} is symmetric"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.PATTERN_MISIDENTIFICATION, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_shape_reflection(self) -> Question:
        """Reflect a shape across a line."""
        correct_answer = "Reflected shape matches pattern"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Reflected shape is rotated",  # Confuses reflection with rotation
            MisconceptionType.SIMILAR_CONCEPT_ERROR: 
                "Reflected shape is flipped wrong",  # Reflects incorrectly
            MisconceptionType.INCOMPLETE_REASONING: 
                "No reflection"  # Doesn't apply transformation
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Shape Reflection",
            logical_trap="K.C. Nag trap: Students confuse reflection with rotation.",
            data_representation="```\nOriginal shape: On left\nMirror line: In center\n"
                               "Reflected shape: On right (mirror image)\n```",
            question_text="When a shape is reflected across a vertical line, which image is correct?",
            solution_steps=[
                "Draw mirror line down the center",
                "Reflect each point across the line",
                "Distance from mirror stays same",
                "Answer: Reflected shape matches pattern"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.PATTERN_MISIDENTIFICATION, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_line_symmetry(self) -> Question:
        """Count lines of symmetry."""
        shapes = {"square": 4, "rectangle": 2, "circle": "infinite", "triangle": 1}
        shape = random.choice(list(shapes.keys()))
        line_count = shapes[shape]
        
        correct_answer = f"{line_count} line(s)"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{int(line_count) if isinstance(line_count, (int, float)) else 1} line(s)",  # Misses some lines
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "0 lines",  # Says no symmetry
            MisconceptionType.LOGICAL_DISCONNECT: 
                "No symmetry"  # Doesn't recognize concept
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Line Symmetry Count",
            logical_trap="Students count wrong or miss some symmetry lines.",
            data_representation=f"```\nShape: {shape.capitalize()}\nLines of symmetry: {line_count}\n```",
            question_text=f"How many lines of symmetry does a {shape} have?",
            solution_steps=[
                f"Shape: {shape}",
                f"Draw all possible fold lines",
                f"Count mirror positions: {line_count}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.PATTERN_MISIDENTIFICATION, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_rotational_symmetry(self) -> Question:
        """Rotational symmetry of shapes."""
        shapes = {"square": 4, "equilateral triangle": 3, "circle": "infinite", "rectangle": 2}
        shape = random.choice(list(shapes.keys()))
        order = shapes[shape]
        
        correct_answer = f"{order} (rotational order)"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "0",  # Says no rotational symmetry
            MisconceptionType.INCOMPLETE_REASONING: 
                "1",  # Off by one
            MisconceptionType.LOGICAL_DISCONNECT: 
                "2"  # Wrong order
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Rotational Symmetry",
            logical_trap="K.C. Nag integration: Students confuse rotational with line symmetry.",
            data_representation=f"```\nShape: {shape.capitalize()}\n"
                               f"Rotational order: {order}\n360° ÷ {order} = smallest rotation\n```",
            question_text=f"What is the rotational symmetry order of a {shape}?",
            solution_steps=[
                f"Shape: {shape}",
                f"How many times fits in 360°? {order} times",
                f"Rotational order: {order}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.PATTERN_MISIDENTIFICATION, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_symmetric_count(self) -> Question:
        """Count symmetric shapes from a group."""
        total_shapes = random.randint(5, 10)
        symmetric_count = random.randint(2, total_shapes - 1)
        
        correct_answer = f"{symmetric_count} shapes"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{symmetric_count - 1}",  # Misses one shape
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"{symmetric_count + 1}",  # Counts extra
            MisconceptionType.LOGICAL_DISCONNECT: 
                f"{total_shapes}"  # Counts all shapes instead
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Symmetric Shape Count",
            logical_trap="Students miss some symmetric shapes or count asymmetric ones.",
            data_representation=f"```\nTotal shapes shown: {total_shapes}\nSymmetric shapes: {symmetric_count}\n```",
            question_text=f"Out of {total_shapes} shapes shown, how many are symmetric?",
            solution_steps=[
                f"Total shapes: {total_shapes}",
                "Check each shape for symmetry",
                f"Symmetric shapes: {symmetric_count}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.PATTERN_MISIDENTIFICATION, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
