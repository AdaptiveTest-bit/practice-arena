"""Dice Logic question strategy - Opposite faces sum to 7."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
import random


class DiceLogicStrategy(BaseChapterStrategy):
    """Generates dice problems using the opposite faces rule (sum = 7)."""
    
    chapter = ChapterEnum.DICE_LOGIC
    chapter_name = "Dice Logic"
    description = "Opposite faces sum to 7"
    
    def generate(self) -> Question:
        """Generate a dice logic question."""
        problem_type = random.choice([
            "standard_dice",
            "logic_trap",
            "multiple_faces",
            "pattern_dice",
            "rotation_dice",
            "profit_dice"
        ])
        
        if problem_type == "standard_dice":
            return self._generate_standard_dice()
        elif problem_type == "logic_trap":
            return self._generate_logic_trap()
        elif problem_type == "multiple_faces":
            return self._generate_multiple_faces()
        elif problem_type == "pattern_dice":
            return self._generate_pattern_dice()
        elif problem_type == "rotation_dice":
            return self._generate_rotation_dice()
        else:  # profit_dice
            return self._generate_profit_dice()
    
    def _generate_standard_dice(self) -> Question:
        """Standard opposite faces (sum = 7) problem."""
        faces = random.choice([
            {"shown": "1, 2, 3", "answer": "6, 5, 4"},
            {"shown": "2, 5, 6", "answer": "5, 2, 1"},
            {"shown": "3, 4, 5", "answer": "4, 3, 2"}
        ])
        
        correct_answer = faces["answer"]
        distractors = [
            faces["shown"],
            "7, 7, 7",
            "1, 1, 1"
        ]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Dice Logic",
            logical_trap="Students forget that opposite faces on a standard die sum to 7. "
                        "If top is 1, bottom is 6. If top is 2, bottom is 5. If top is 3, bottom is 4.",
            data_representation="```\nStandard Dice Rule: Opposite faces always sum to 7\n\n"
                               "If you see: 1 → Opposite is: 6\n"
                               "If you see: 2 → Opposite is: 5\n"
                               "If you see: 3 → Opposite is: 4\n```",
            question_text=f"A die shows {faces['shown']} on three consecutive faces. "
                          "What are the opposite faces?",
            solution_steps=[
                f"Given faces: {faces['shown']}",
                "Using the rule that opposite faces sum to 7:",
                f"Opposite of {faces['shown'].split(',')[0]}: 7 - {faces['shown'].split(',')[0]} = ?",
                f"Opposite faces: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_logic_trap(self) -> Question:
        """The K.C. Nag logical trap: wrong inference about dice."""
        shown_face = random.choice([1, 2, 3])
        correct_opposite = 7 - shown_face
        
        correct_answer = f"{correct_opposite}"
        trap_answers = [
            str(shown_face),
            "7",
            str(random.choice([1, 2, 3, 4, 5, 6]) if random.choice([1, 2, 3, 4, 5, 6]) != correct_opposite else 5)
        ]
        
        options = self.ensure_unique_options([correct_answer] + trap_answers)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Dice Logic (Logical Trap)",
            logical_trap="K.C. Nag Trap: Students think the opposite face is the same as the shown face, "
                        "or they add instead of subtracting from 7.",
            data_representation=f"```\nDie shows: {shown_face}\n\nOpposite faces sum rule:\n"
                               "1 ↔ 6\n2 ↔ 5\n3 ↔ 4\n```",
            question_text=f"When a die shows {shown_face} on top, what number is on the bottom?",
            solution_steps=[
                f"Top face shows: {shown_face}",
                "Opposite faces on a standard die sum to 7",
                f"Bottom = 7 - {shown_face} = {correct_opposite}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_multiple_faces(self) -> Question:
        """Count visible/hidden faces after rolling."""
        rolls = random.randint(2, 4)
        correct_answer = f"{7 * rolls} (sum of all opposite pairs)"
        
        distractors = [
            f"{rolls * 3} (incorrect calculation)",
            f"{rolls * 6} (wrong method)",
            f"21 (fixed answer)"
        ]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Multiple Dice Faces",
            logical_trap="Students add randomly instead of using the sum rule. "
                        "Each opposite pair sums to 7, regardless of which faces are visible.",
            data_representation=f"```\nMultiple Dice Rule:\nWith {rolls} dice, each showing opposite faces:\n"
                               f"Total sum = {rolls} × 7 = {7 * rolls}\n```",
            question_text=f"If you roll {rolls} dice and see random faces on top, "
                          f"what is the sum of their bottom faces?",
            solution_steps=[
                f"Number of dice: {rolls}",
                "Each die has opposite faces that sum to 7",
                f"Total sum of bottom faces = {rolls} × 7 = {7 * rolls}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_pattern_dice(self) -> Question:
        """Pattern recognition with dice faces."""
        patterns = [
            {"sequence": "1, 2, 3, 4, 5, 6", "next": "Repeats (1)"},
            {"sequence": "2, 4, 6, 1, 3, 5", "next": "Pattern breaks"}
        ]
        pattern = random.choice(patterns)
        
        correct_answer = pattern["next"]
        distractors = ["7", "0", "Continues forever"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Dice Pattern Recognition",
            logical_trap="Students think dice faces continue beyond 6 or follow a wrong pattern.",
            data_representation=f"```\nDice faces: 1, 2, 3, 4, 5, 6\nPattern: {pattern['sequence']}\n```",
            question_text=f"In the sequence {pattern['sequence']}, what comes next?",
            solution_steps=[
                f"Given sequence: {pattern['sequence']}",
                "Analyzing the pattern...",
                f"Next: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_rotation_dice(self) -> Question:
        """Dice rotation and spatial reasoning."""
        initial_face = random.choice([1, 2, 3, 4, 5, 6])
        rotations = random.randint(1, 3)
        
        correct_answer = f"Face {7 - initial_face} (rotated {rotations} times)"
        distractors = [f"Face {initial_face}", f"Face {7 - initial_face} (wrong rotation)", "Unknown"]
        
        options, correct_idx = self.shuffle_options_keep_correct(correct_answer, distractors)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Dice Rotation",
            logical_trap="Students lose track of which face is where after rotation. "
                        "Rotation direction matters.",
            data_representation=f"```\nInitial face: {initial_face}\nRotations: {rotations}\n"
                               "Track face position carefully\n```",
            question_text=f"A die showing {initial_face} on top is rotated {rotations} times forward. "
                          "Which face is now on top?",
            solution_steps=[
                f"Starting position: {initial_face}",
                f"Number of rotations: {rotations}",
                f"After rotation: Face {7 - initial_face}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_profit_dice(self) -> Question:
        """Dice with profit/loss twist (K.C. Nag integration)."""
        dice_value = random.choice([1, 2, 3, 4, 5, 6])
        profit_per_point = random.choice([10, 15, 20])
        
        correct_answer = f"₹{dice_value * profit_per_point}"
        distractors = [f"₹{(7 - dice_value) * profit_per_point}", f"₹{7 * profit_per_point}", f"₹{dice_value}"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Dice with Profit",
            logical_trap="Students confuse dice face value with opposite face. "
                        "This is a cross-concept problem combining dice + profit.",
            data_representation=f"```\nDice shows: {dice_value}\nProfit per point: ₹{profit_per_point}\n"
                               f"Profit = Dice × Rate\n```",
            question_text=f"A game gives ₹{profit_per_point} profit per point on a die. "
                          f"If the die shows {dice_value}, what's the profit?",
            solution_steps=[
                f"Die shows: {dice_value}",
                f"Profit rate: ₹{profit_per_point} per point",
                f"Profit = {dice_value} × ₹{profit_per_point} = ₹{dice_value * profit_per_point}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
