"""Dice Logic question strategy - Opposite faces sum to 7."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
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
        from models.distractor import MisconceptionType
        
        faces = random.choice([
            {"shown": "1, 2, 3", "answer": "6, 5, 4"},
            {"shown": "2, 5, 6", "answer": "5, 2, 1"},
            {"shown": "3, 4, 5", "answer": "4, 3, 2"}
        ])
        
        correct_answer = faces["answer"]
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPPOSITE_CONFUSION:
                faces["shown"],  # Returns same faces instead of opposite
            MisconceptionType.UNIVERSAL_VS_SPECIFIC:
                "7, 7, 7",  # Thinks all opposites are 7
            MisconceptionType.ARITHMETIC_ERROR:
                "1, 1, 1"  # Off-by-one or wrong calculation
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=3,
            custom_description="Student returns the shown faces instead of calculating their opposites",
            custom_why_effective="Requires understanding that 1↔6, 2↔5, 3↔4 are inverse pairs",
            custom_how_to_avoid="Always calculate: opposite = 7 - shown_face"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=3
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,  # Phase 1
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_logic_trap(self) -> Question:
        """The K.C. Nag logical trap: wrong inference about dice."""
        from models.distractor import MisconceptionType
        
        shown_face = random.choice([1, 2, 3])
        correct_opposite = 7 - shown_face
        
        correct_answer = f"{correct_opposite}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPPOSITE_CONFUSION:
                str(shown_face),  # Returns same face instead of opposite
            MisconceptionType.UNIVERSAL_VS_SPECIFIC:
                "7",  # Thinks opposite is always 7
            MisconceptionType.ARITHMETIC_ERROR:
                str(random.choice([x for x in [1, 2, 3, 4, 5, 6] if x != correct_opposite]))
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=2,
            custom_description="K.C. Nag Trap: Student returns the shown face value instead of its opposite",
            custom_why_effective="Easy to confuse when not carefully thinking through the relationship",
            custom_how_to_avoid="Use subtraction formula: opposite = 7 - shown"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_multiple_faces(self) -> Question:
        """Count visible/hidden faces after rolling."""
        from models.distractor import MisconceptionType
        
        rolls = random.randint(2, 4)
        correct_answer = f"{7 * rolls} (sum of all opposite pairs)"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING:
                f"{rolls * 3} (incorrect calculation)",  # Partial calculation
            MisconceptionType.OPERATION_SELECTION:
                f"{rolls * 6} (wrong method)",  # Uses max face value
            MisconceptionType.UNIVERSAL_VS_SPECIFIC:
                "21 (fixed answer)"  # Hardcoded wrong answer
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(
                MisconceptionType.OPPOSITE_CONFUSION,
                difficulty=2,
                custom_description="Student forgets that opposite faces of a die sum to 7; provides only bottom total without subtraction",
                custom_why_effective="Requires understanding a geometric constraint of dice that students often don't know",
                custom_how_to_avoid="Remember: Standard die has opposite faces summing to 7; top + bottom = 7 per die; multiply by number of dice"
            )
        )
        
        self._validate_question(question)
        return question
    
    def _generate_pattern_dice(self) -> Question:
        """Pattern recognition with dice faces."""
        from models.distractor import MisconceptionType
        
        patterns = [
            {"sequence": "1, 2, 3, 4, 5, 6", "next": "Repeats (1)"},
            {"sequence": "2, 4, 6, 1, 3, 5", "next": "Pattern breaks"}
        ]
        pattern = random.choice(patterns)
        
        correct_answer = pattern["next"]
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.PATTERN_MISIDENTIFICATION:
                "7",  # Thinks sequence continues beyond 6
            MisconceptionType.INCOMPLETE_REASONING:
                "0",  # Wrong boundary thinking
            MisconceptionType.UNIVERSAL_VS_SPECIFIC:
                "Continues forever"  # Doesn't recognize dice limits
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.PATTERN_MISIDENTIFICATION,
            difficulty=2,
            custom_description="Student doesn't recognize that dice only have faces 1-6",
            custom_why_effective="Requires understanding of constraint: dice faces never exceed 6",
            custom_how_to_avoid="Remember: A standard die only has faces numbered 1 through 6"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_rotation_dice(self) -> Question:
        """Dice rotation and spatial reasoning."""
        from models.distractor import MisconceptionType
        
        initial_face = random.choice([1, 2, 3, 4, 5, 6])
        rotations = random.randint(1, 3)
        
        correct_answer = f"Face {7 - initial_face} (rotated {rotations} times)"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPPOSITE_CONFUSION:
                f"Face {initial_face}",  # Returns same face after rotation
            MisconceptionType.INCOMPLETE_REASONING:
                f"Face {7 - initial_face} (wrong rotation)",  # Right opposite, wrong explanation
            MisconceptionType.CONSTRAINT_VIOLATION:
                "Unknown"  # Gives up instead of calculating
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=3,
            custom_description="Student loses track of face identity during rotation",
            custom_why_effective="Requires spatial reasoning and tracking state changes",
            custom_how_to_avoid="Track each rotation carefully: after each turn, note which face is on top"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_profit_dice(self) -> Question:
        """Dice with profit/loss twist (K.C. Nag integration)."""
        from models.distractor import MisconceptionType
        
        dice_value = random.choice([1, 2, 3, 4, 5, 6])
        profit_per_point = random.choice([10, 15, 20])
        
        correct_answer = f"₹{dice_value * profit_per_point}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPPOSITE_CONFUSION: 
                f"₹{(7 - dice_value) * profit_per_point}",  # Uses opposite face
            MisconceptionType.UNIVERSAL_VS_SPECIFIC: 
                f"₹{7 * profit_per_point}",                  # Uses sum not shown value
            MisconceptionType.INCOMPLETE_REASONING: 
                f"₹{dice_value}"                              # Forgot multiplication
        }
        
        # 🆕 USE NEW HELPER
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=2,
            custom_description="Student confuses the shown face value with the opposite face",
            custom_why_effective="Combines dice logic with arithmetic, two potential confusion sources",
            custom_how_to_avoid="Use the correct shown value for the die, not its opposite"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
