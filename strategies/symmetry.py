"""Symmetry & Reflection question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
import random


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
        distractors = [f"{test_letter} - Not symmetric", f"{random.choice(asymmetric_letters)} - Symmetric", 
                      "None"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_word_symmetry(self) -> Question:
        """Identify symmetric words."""
        symmetric_words = ['MOM', 'DAD', 'POP', 'SOS', 'NOON']
        asymmetric_words = ['BAT', 'CAT', 'DOG', 'APPLE', 'TREE']
        
        test_word = random.choice(symmetric_words)
        correct_answer = f"{test_word} - Palindrome (Symmetric)"
        distractors = [f"{test_word} - Not symmetric", f"{random.choice(asymmetric_words)} - Symmetric",
                      "None"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_shape_reflection(self) -> Question:
        """Reflect a shape across a line."""
        correct_answer = "Reflected shape matches pattern"
        distractors = ["Reflected shape is rotated", "Reflected shape is flipped wrong", "No reflection"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_line_symmetry(self) -> Question:
        """Count lines of symmetry."""
        shapes = {"square": 4, "rectangle": 2, "circle": "infinite", "triangle": 1}
        shape = random.choice(list(shapes.keys()))
        line_count = shapes[shape]
        
        correct_answer = f"{line_count} line(s)"
        distractors = [f"{int(line_count) if isinstance(line_count, (int, float)) else 1} line(s)", 
                      "0 lines", "No symmetry"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_rotational_symmetry(self) -> Question:
        """Rotational symmetry of shapes."""
        shapes = {"square": 4, "equilateral triangle": 3, "circle": "infinite", "rectangle": 2}
        shape = random.choice(list(shapes.keys()))
        order = shapes[shape]
        
        correct_answer = f"{order} (rotational order)"
        distractors = ["0", "1", "2"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_symmetric_count(self) -> Question:
        """Count symmetric shapes from a group."""
        total_shapes = random.randint(5, 10)
        symmetric_count = random.randint(2, total_shapes - 1)
        
        correct_answer = f"{symmetric_count} shapes"
        distractors = [f"{symmetric_count - 1}", f"{symmetric_count + 1}", f"{total_shapes}"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
