"""Rotation and 3D orientation question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
import random
from models.distractor import MisconceptionType


class RotationStrategy(BaseChapterStrategy):
    """Generates rotation and 3D orientation problems."""
    
    chapter = ChapterEnum.ROTATION
    chapter_name = "Rotation"
    description = "2D and 3D rotation problems"
    
    def generate(self) -> Question:
        """Generate a rotation question."""
        problem_type = random.choice([
            "simple_rotation",
            "figure_rotation",
            "3d_rotation",
            "rotation_angle",
            "clock_rotation",
            "reflection_rotation"
        ])
        
        if problem_type == "simple_rotation":
            return self._generate_simple_rotation()
        elif problem_type == "figure_rotation":
            return self._generate_figure_rotation()
        elif problem_type == "3d_rotation":
            return self._generate_3d_rotation()
        elif problem_type == "rotation_angle":
            return self._generate_rotation_angle()
        elif problem_type == "clock_rotation":
            return self._generate_clock_rotation()
        else:
            return self._generate_reflection_rotation()
    
    def _generate_simple_rotation(self) -> Question:
        """Rotate a simple shape by 90 degrees."""
        rotations = {
            "90° clockwise": "Right",
            "180°": "Upside down",
            "270° clockwise": "Left",
            "90° counter-clockwise": "Left"
        }
        
        rotation = random.choice(list(rotations.keys()))
        correct_answer = f"Rotated {rotation}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPERATION_DIRECTION: 
                "No change",  # Ignores rotation
            MisconceptionType.INCOMPLETE_REASONING: 
                "Reflected only",  # Confuses rotation with reflection
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Moved only"  # Confuses with translation
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPERATION_DIRECTION,
            difficulty=1,
            custom_description="Student ignores rotation instruction or confuses rotation direction with reflection/translation",
            custom_why_effective="Basic transformation; students often report 'no change' when rotation occurs",
            custom_how_to_avoid="Rotation changes orientation; 90° turns shape quarter turn; track how many degrees and which direction"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.REMEMBER,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Simple Rotation",
            logical_trap="K.C. Nag trap: Students confuse rotation with reflection or translation.",
            data_representation=f"```\nOriginal shape: Arrow pointing up ↑\nRotation: {rotation}\nResult: Position changes\n```",
            question_text=f"If a shape is rotated {rotation}, what happens?",
            solution_steps=[
                f"Original orientation",
                f"Apply rotation: {rotation}",
                f"Shape position changes to {rotations[rotation]}",
                f"Answer: {correct_answer}"
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
    
    def _generate_figure_rotation(self) -> Question:
        """Match rotated figure."""
        angles = [90, 180, 270]
        angle = random.choice(angles)
        
        correct_answer = f"Figure rotated {angle}°"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"Figure rotated {random.choice([a for a in angles if a != angle])}°",  # Wrong angle
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Figure reflected",  # Confuses rotation with reflection
            MisconceptionType.OPERATION_DIRECTION: 
                "Figure translated"  # Confuses with translation
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
            topic="Shapes & Angles - Figure Rotation",
            logical_trap="Students misidentify which option is correctly rotated.",
            data_representation=f"```\nOriginal figure: [Shape shown]\nRotated by: {angle}°\n"
                               f"Which option matches?\n```",
            question_text=f"Which figure shows the original shape rotated {angle}°?",
            solution_steps=[
                f"Original shape orientation",
                f"Rotate each point {angle}° around center",
                f"Match with given options",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.INCOMPLETE_REASONING, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_3d_rotation(self) -> Question:
        """3D object rotation around axis."""
        axes = ["X-axis (left-right)", "Y-axis (up-down)", "Z-axis (front-back)"]
        axis = random.choice(axes)
        rotation_amount = random.choice([90, 180, 270])
        
        correct_answer = f"Rotated {rotation_amount}° around {axis}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"Rotated {rotation_amount}° around different axis",  # Wrong axis
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Reflected in plane",  # Confuses with reflection
            MisconceptionType.OPERATION_DIRECTION: 
                "Translated in space"  # Confuses with translation
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - 3D Rotation",
            logical_trap="K.C. Nag trap: Students don't correctly visualize 3D rotations.",
            data_representation=f"```\n3D Object: Cube\nAxis of rotation: {axis}\n"
                               f"Amount: {rotation_amount}°\n```",
            question_text=f"A cube is rotated {rotation_amount}° around the {axis}. Which view matches?",
            solution_steps=[
                f"Original 3D position",
                f"Rotate around {axis}",
                f"Amount: {rotation_amount}°",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.INCOMPLETE_REASONING, difficulty=3),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_rotation_angle(self) -> Question:
        """Find rotation angle needed."""
        start_position = "Top"
        positions = ["Top", "Right", "Bottom", "Left"]
        end_position = random.choice([p for p in positions if p != start_position])
        
        angle_map = {"Right": 90, "Bottom": 180, "Left": 270}
        angle = angle_map[end_position]
        
        correct_answer = f"{angle}°"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{(angle + 90) % 360}°",  # Off by 90 degrees
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{(angle + 180) % 360}°",  # Wrong calculation
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "360°"  # Full rotation
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
            topic="Shapes & Angles - Rotation Angle",
            logical_trap="Students miscalculate the angle between two positions.",
            data_representation=f"```\nStart position: {start_position}\nEnd position: {end_position}\n"
                               f"Rotation angle: {angle}°\n```",
            question_text=f"How many degrees must a shape rotate from {start_position} to {end_position}?",
            solution_steps=[
                f"Start: {start_position}",
                f"End: {end_position}",
                f"Calculate: {angle}° clockwise",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.ARITHMETIC_ERROR, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_clock_rotation(self) -> Question:
        """Clock hand rotation."""
        hour = random.randint(1, 11)
        steps = random.randint(1, 3)
        new_hour = (hour + steps) % 12 if (hour + steps) % 12 != 0 else 12
        
        correct_answer = f"{new_hour} o'clock"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{(new_hour % 12) + 1 if new_hour != 12 else 1} o'clock",  # Off by one
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{(new_hour - 1) if new_hour > 1 else 12} o'clock",  # Wrong direction
            MisconceptionType.OPERATION_DIRECTION: 
                "6 o'clock"  # Opposite position
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.REMEMBER,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Clock Rotation",
            logical_trap="Students miscalculate hour hand position after rotation.",
            data_representation=f"```\nHour hand: Points to {hour}\nRotates by: {steps} hours\nNew position: {new_hour}\n```",
            question_text=f"If the hour hand points to {hour}, and rotates {steps} hours clockwise, where does it point?",
            solution_steps=[
                f"Start position: {hour}",
                f"Rotate by: {steps} hours",
                f"Each hour = 30°",
                f"New position: {new_hour}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.ARITHMETIC_ERROR, difficulty=1),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_reflection_rotation(self) -> Question:
        """Combination of rotation and reflection."""
        operation1 = "Rotate 90°"
        operation2 = "Reflect horizontally"
        
        correct_answer = f"{operation1}, then {operation2}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPERATION_DIRECTION: 
                f"{operation2}, then {operation1}",  # Reverses order (order matters!)
            MisconceptionType.INCOMPLETE_REASONING: 
                "Just rotate",  # Misses one step
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Just reflect"  # Misses one step
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
            topic="Shapes & Angles - Rotation + Reflection",
            logical_trap="K.C. Nag integration: Order matters in combined transformations.",
            data_representation=f"```\nOriginal shape: [Shown]\nStep 1: {operation1}\nStep 2: {operation2}\n```",
            question_text=f"Apply {operation1} and then {operation2}. Which figure is the result?",
            solution_steps=[
                "Start with original shape",
                f"Step 1: {operation1}",
                f"Step 2: {operation2}",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=self.create_trap_info(MisconceptionType.OPERATION_DIRECTION, difficulty=2),  # Phase 2
        bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
