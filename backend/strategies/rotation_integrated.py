"""
ROTATION - INTEGRATED STRATEGY
==============================

Hybrid Neuro-Symbolic approach for Rotation

Integrates:
1. Visual spatial with coordinate math
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Direction confusion, Center point error)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class RotationIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic visual logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.ROTATION
    chapter_name = "Rotation"
    description = "Rotation with hybrid neuro-symbolic approach"
    
    def __init__(self):
        super().__init__()
        # Initialize hybrid system components here
        # self.sympy_generator = ...
        # self.story_generator = ...
        # self.renderer = ...
    
    def generate(self) -> Question:
        """
        Main generation pipeline:
        1. Select problem type
        2. Generate skeleton (PHASE 1)
        3. Generate K.C. Nag story (PHASE 2)
        4. Generate misconception options (PHASE 3)
        5. Render rich question (PHASE 4)
        6. Create trackable Question (PHASE 5)
        """
        problem_type = random.choice([
            "clockwise_rotation",
            "counterclockwise_rotation",
            "rotation_center_effect",
        ])
        
        if problem_type == "clockwise_rotation":
            return self._generate_clockwise_rotation()
        elif problem_type == "counterclockwise_rotation":
            return self._generate_counterclockwise_rotation()
        else:  # rotation_center_effect
            return self._generate_rotation_center_effect()
    
    def _generate_clockwise_rotation(self) -> Question:
        """
        Clockwise Rotation - Where does point end up?
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters (center, point, angle)
        - Calculate correct new position
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        angles = [90, 180, 270]
        rotation_angle = random.choice(angles)
        
        points = [
            ("A", "Top-right"),
            ("B", "Right"),
            ("C", "Bottom-right"),
            ("D", "Bottom"),
            ("E", "Left"),
            ("F", "Top"),
            ("G", "Top-left"),
        ]
        
        point_name, initial_position = random.choice(points)
        center = "center O"
        
        # Clockwise rotation mapping
        position_mapping = {
            90: {
                "Top-right": "Bottom-right",
                "Right": "Top",
                "Bottom-right": "Bottom-left",
                "Bottom": "Right",
                "Left": "Bottom",
                "Top": "Left",
                "Top-left": "Top",
            },
            180: {
                "Top-right": "Bottom-left",
                "Right": "Left",
                "Bottom-right": "Top-left",
                "Bottom": "Top",
                "Left": "Right",
                "Top": "Bottom",
                "Top-left": "Bottom-right",
            },
            270: {
                "Top-right": "Top-left",
                "Right": "Bottom",
                "Bottom-right": "Top-right",
                "Bottom": "Left",
                "Left": "Top",
                "Top": "Right",
                "Top-left": "Bottom-left",
            },
        }
        
        correct_answer = position_mapping[rotation_angle][initial_position]
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A spinner shows point {point_name} at the {initial_position} position. When you spin it {rotation_angle}° clockwise around center O, where does point {point_name} move to?",
            f"A wheel has a mark at {initial_position}. After rotating {rotation_angle}° clockwise around its center, where is the mark now?",
            f"You're looking at a compass with point {point_name} at {initial_position}. Rotate your view {rotation_angle}° clockwise. Where is point {point_name} now?",
        ])
        
        # PHASE 3: Misconception-based distractors
        wrong_positions = [position_mapping[270][initial_position] if rotation_angle == 90 else position_mapping[90][initial_position],
                          initial_position,
                          position_mapping[180][initial_position] if rotation_angle != 180 else position_mapping[90][initial_position]]
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct rotated position",
                None,
                None
            ),
            1: (
                wrong_positions[0],
                MisconceptionType.OPERATION_DIRECTION,
                "Rotated counterclockwise instead of clockwise",
                "Student rotated in the opposite direction",
                "Be careful: clockwise and counterclockwise are opposite. Clockwise: top → right → bottom → left."
            ),
            2: (
                wrong_positions[1],
                MisconceptionType.FORMULA_CONFUSION,
                "Point didn't rotate at all",
                "Student forgot to apply the rotation",
                f"Remember: when you rotate point {point_name}, it MUST move. Only the center stays in place."
            ),
            3: (
                wrong_positions[2],
                MisconceptionType.INCOMPLETE_REASONING,
                "Applied wrong rotation angle",
                "Student used a different angle than {rotation_angle}°",
                f"Make sure you rotate exactly {rotation_angle}° clockwise around center O."
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = opt_val
            
            if misconception is None:
                correct_idx = display_idx
            
            distractor_info_list.append(DistractorInfo(
                value=opt_val,
                misconception_type=misconception or MisconceptionType.INCOMPLETE_REASONING,
                description=desc,
                why_wrong=why_wrong or "Correct",
                teaching_point=teaching or "Well done!"
            ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.OPERATION_DIRECTION,
            difficulty=2,
            custom_description="Clockwise vs counterclockwise direction confusion",
            custom_why_effective="Students often confuse rotation direction",
            custom_how_to_avoid="Use memory aid: clock hands go clockwise. Top → right → bottom → left."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        steps = [
            f"Initial position: Point {point_name} at {initial_position}",
            f"Rotation: {rotation_angle}° clockwise around {center}",
            f"Trace clockwise: every 90°, move to next position",
            f"After {rotation_angle}°: {correct_answer}",
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = self._render_clockwise_rotation_diagram(point_name, initial_position, rotation_angle, correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Rotation - Clockwise",
            logical_trap="K.C. Nag Trap: Students confuse clockwise with counterclockwise, leading to the wrong position. They may also forget to apply the full rotation angle.",
            data_representation=f"```\nPoint: {point_name} at {initial_position}\nRotation: {rotation_angle}° clockwise\nNew position: ?\n```",
            question_text=f"Point {point_name} is at {initial_position}. After rotating {rotation_angle}° clockwise around center O, where is point {point_name}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Rotation moves a point around a center. Clockwise rotation follows the direction of clock hands. Trace carefully: each 90° rotation moves to the next position clockwise.",
            visual_hints=[
                f"Point {point_name} starts at {initial_position}",
                f"Rotate {rotation_angle}° CLOCKWISE around center O",
                "Remember: clockwise = top → right → bottom → left",
                f"Point {point_name} ends at {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _generate_counterclockwise_rotation(self) -> Question:
        """
        Counterclockwise Rotation - Where does point end up?
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters
        - Calculate correct new position
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        angles = [90, 180, 270]
        rotation_angle = random.choice(angles)
        
        points = [
            ("A", "Top"),
            ("B", "Top-right"),
            ("C", "Right"),
            ("D", "Bottom-right"),
            ("E", "Bottom"),
            ("F", "Bottom-left"),
            ("G", "Left"),
        ]
        
        point_name, initial_position = random.choice(points)
        center = "center O"
        
        # Counterclockwise rotation mapping
        position_mapping = {
            90: {
                "Top": "Right",
                "Top-right": "Bottom-right",
                "Right": "Bottom",
                "Bottom-right": "Bottom-left",
                "Bottom": "Left",
                "Bottom-left": "Top-left",
                "Left": "Top",
            },
            180: {
                "Top": "Bottom",
                "Top-right": "Bottom-left",
                "Right": "Left",
                "Bottom-right": "Top-left",
                "Bottom": "Top",
                "Bottom-left": "Top-right",
                "Left": "Right",
            },
            270: {
                "Top": "Left",
                "Top-right": "Top-left",
                "Right": "Top",
                "Bottom-right": "Top-right",
                "Bottom": "Right",
                "Bottom-left": "Bottom-right",
                "Left": "Bottom",
            },
        }
        
        correct_answer = position_mapping[rotation_angle][initial_position]
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A wheel rotates point {point_name} counterclockwise {rotation_angle}° from {initial_position}. Where does it end up?",
            f"Looking at a spinning wheel, point {point_name} starts at {initial_position}. After a counterclockwise turn of {rotation_angle}°, where is it?",
            f"A shape rotates counterclockwise {rotation_angle}° around center O. Point {point_name} was at {initial_position}. Where is it now?",
        ])
        
        # PHASE 3: Misconception-based distractors
        wrong_positions = [position_mapping[270][initial_position] if rotation_angle == 90 else position_mapping[90][initial_position],
                          initial_position,
                          position_mapping[180][initial_position] if rotation_angle != 180 else position_mapping[90][initial_position]]
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct rotated position",
                None,
                None
            ),
            1: (
                wrong_positions[0],
                MisconceptionType.OPERATION_DIRECTION,
                "Rotated clockwise instead of counterclockwise",
                "Student rotated in the opposite direction",
                "Counterclockwise is OPPOSITE to clock direction: top → left → bottom → right."
            ),
            2: (
                wrong_positions[1],
                MisconceptionType.FORMULA_CONFUSION,
                "Point didn't rotate at all",
                "Student forgot to apply the rotation",
                f"When you rotate point {point_name}, it MUST move to a new position."
            ),
            3: (
                wrong_positions[2],
                MisconceptionType.INCOMPLETE_REASONING,
                "Applied wrong rotation angle",
                "Student used a different angle",
                f"Apply exactly {rotation_angle}° counterclockwise rotation."
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = opt_val
            
            if misconception is None:
                correct_idx = display_idx
            
            distractor_info_list.append(DistractorInfo(
                value=opt_val,
                misconception_type=misconception or MisconceptionType.INCOMPLETE_REASONING,
                description=desc,
                why_wrong=why_wrong or "Correct",
                teaching_point=teaching or "Well done!"
            ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.OPERATION_DIRECTION,
            difficulty=2,
            custom_description="Confusing clockwise and counterclockwise directions",
            custom_why_effective="Students reverse directions without consistent reference",
            custom_how_to_avoid="Counterclockwise is OPPOSITE to clock: top → left → bottom → right."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        steps = [
            f"Initial position: Point {point_name} at {initial_position}",
            f"Rotation: {rotation_angle}° counterclockwise around {center}",
            f"Trace counterclockwise (opposite to clock)",
            f"After {rotation_angle}°: {correct_answer}",
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = self._render_counterclockwise_rotation_diagram(point_name, initial_position, rotation_angle, correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Rotation - Counterclockwise",
            logical_trap="K.C. Nag Trap: Students confuse counterclockwise with clockwise. Counterclockwise is OPPOSITE to clock direction, which many students forget.",
            data_representation=f"```\nPoint: {point_name} at {initial_position}\nRotation: {rotation_angle}° counterclockwise\nNew position: ?\n```",
            question_text=f"Point {point_name} is at {initial_position}. After rotating {rotation_angle}° counterclockwise around center O, where is point {point_name}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Counterclockwise rotation goes OPPOSITE to clock hands. Remember: clockwise is top → right → bottom → left. Counterclockwise is the opposite: top → left → bottom → right.",
            visual_hints=[
                f"Point {point_name} starts at {initial_position}",
                f"Rotate {rotation_angle}° COUNTERCLOCKWISE (opposite to clock)",
                "Counterclockwise: top → left → bottom → right",
                f"Point {point_name} ends at {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _generate_rotation_center_effect(self) -> Question:
        """
        Rotation Center Effect - Does changing center change the result?
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters
        - Determine effect of different centers
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        # Question type: does rotation center matter?
        questions = [
            {
                "question": "If you rotate a point 90° clockwise around center A, and another point the same amount around center B (different location), do both points end up at the same position?",
                "answer": "No",
                "reason": "Different centers produce different rotated positions",
            },
            {
                "question": "When you rotate a shape around different centers with the same angle, does the shape end up in the same location?",
                "answer": "No",
                "reason": "The rotation center changes the final position",
            },
            {
                "question": "If you rotate point P by 180° around center O, will rotating the same point 180° around a different center C give the same result?",
                "answer": "No",
                "reason": "The center of rotation affects the final position",
            },
        ]
        
        selected = random.choice(questions)
        correct_answer = selected["answer"]
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            "A door can be opened from different hinge points. If you rotate it around the left hinge vs the right hinge, does the door end up in the same position?",
            "A merry-go-round rotates around a center pole. If two horses on different radii rotate together, do they end up at the same distance from where they started?",
            "You spin a wheel around its center. If you spun it around a different point, would the same spot on the wheel end up in the same place?",
        ])
        
        # PHASE 3: Misconception-based distractors
        # Common mistake: thinking rotation center doesn't matter
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct understanding of rotation centers",
                None,
                None
            ),
            1: (
                "Yes",
                MisconceptionType.INCOMPLETE_REASONING,
                "Thought rotation center doesn't affect the result",
                "Student didn't understand that center determines the final position",
                "The rotation center is critical! Different centers produce different results, even with the same angle."
            ),
            2: (
                "Sometimes",
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Gave a non-definitive answer",
                "Student wasn't sure about the relationship between center and position",
                "Rotation center ALWAYS affects the result. Every rotation center produces a different outcome."
            ),
            3: (
                "It depends on the angle",
                MisconceptionType.FORMULA_CONFUSION,
                "Thought angle determines the result, not center",
                "Student confused the role of angle vs center",
                "Both angle AND center matter! Different centers always produce different final positions."
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = opt_val
            
            if misconception is None:
                correct_idx = display_idx
            
            distractor_info_list.append(DistractorInfo(
                value=opt_val,
                misconception_type=misconception or MisconceptionType.INCOMPLETE_REASONING,
                description=desc,
                why_wrong=why_wrong or "Correct",
                teaching_point=teaching or "Well done!"
            ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=3,
            custom_description="Not understanding rotation center's critical role",
            custom_why_effective="Students think only angle matters, ignoring the center's effect",
            custom_how_to_avoid="Remember: rotation center is as important as rotation angle. Different centers = different results."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=3)
        
        steps = [
            "Rotation requires TWO things: center and angle",
            "Changing the center changes where points end up",
            "Same angle, different center = different result",
            "Answer: No, different centers produce different positions",
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = self._render_center_effect_diagram(selected["reason"])
        
        question = Question(
            chapter=self.chapter,
            topic="Rotation - Center Effect",
            logical_trap="K.C. Nag Trap: Students often think that only the rotation angle matters, ignoring the center's critical role. They may assume different centers produce the same result if the angle is the same.",
            data_representation=f"```\n{selected['question']}\nAnswer: {correct_answer}\n```",
            question_text=selected["question"],
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Rotation is completely defined by two things: the center point and the angle. Change either one, and you get a different result. The center is not optional—it's essential.",
            visual_hints=[
                "Rotation requires TWO parameters: center AND angle",
                "Changing the center changes the result",
                f"Two rotations with different centers are completely different",
                f"Answer: {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question


    # ==================== HELPER METHODS ====================
    
    def _render_clockwise_rotation_diagram(self, point_name: str, initial_pos: str, angle: int, final_pos: str) -> str:
        """
        Render HTML visual representation of clockwise point rotation
        
        Args:
            point_name: Name of the point
            initial_pos: Initial position
            angle: Rotation angle in degrees
            final_pos: Final position after rotation
            
        Returns:
            HTML string with rotation diagram
        """
        html = f"""
<div style='border:2px solid #2196F3; border-radius:8px; padding:15px; background:#e3f2fd;'>
    <h4 style='color:#1976D2; margin-top:0;'>Clockwise Rotation: {point_name}</h4>
    
    <div style='background:white; padding:10px; border-left:4px solid #2196F3; color:#333; margin-bottom:10px;'>
        <p style='margin:5px 0;'><strong>Initial position:</strong> {initial_pos}</p>
        <p style='margin:5px 0;'><strong>Rotation:</strong> {angle}° clockwise around center O</p>
        <p style='margin:5px 0;'><strong>Final position:</strong> {final_pos}</p>
    </div>
    
    <p style='background:#fff9c4; padding:10px; border-left:4px solid #FBC02D; color:#000;'>
        <strong>Remember:</strong> Clockwise rotation: top → right → bottom → left
    </p>
</div>
"""
        return html
    
    def _render_counterclockwise_rotation_diagram(self, point_name: str, initial_pos: str, angle: int, final_pos: str) -> str:
        """
        Render HTML visual representation of counterclockwise point rotation
        
        Args:
            point_name: Name of the point
            initial_pos: Initial position
            angle: Rotation angle in degrees
            final_pos: Final position after rotation
            
        Returns:
            HTML string with rotation diagram
        """
        html = f"""
<div style='border:2px solid #FF5722; border-radius:8px; padding:15px; background:#ffebee;'>
    <h4 style='color:#C62828; margin-top:0;'>Counterclockwise Rotation: {point_name}</h4>
    
    <div style='background:white; padding:10px; border-left:4px solid #FF5722; color:#333; margin-bottom:10px;'>
        <p style='margin:5px 0;'><strong>Initial position:</strong> {initial_pos}</p>
        <p style='margin:5px 0;'><strong>Rotation:</strong> {angle}° counterclockwise around center O</p>
        <p style='margin:5px 0;'><strong>Final position:</strong> {final_pos}</p>
    </div>
    
    <p style='background:#f3e5f5; padding:10px; border-left:4px solid #7B1FA2; color:#4a148c;'>
        <strong>Remember:</strong> Counterclockwise (opposite to clock): top → left → bottom → right
    </p>
</div>
"""
        return html
    
    def _render_center_effect_diagram(self, explanation: str) -> str:
        """
        Render HTML visual for rotation center effect
        
        Args:
            explanation: Why center matters
            
        Returns:
            HTML string with diagram
        """
        html = f"""
<div style='border:2px solid #4CAF50; border-radius:8px; padding:15px; background:#e8f5e9;'>
    <h4 style='color:#2E7D32; margin-top:0;'>Rotation Center Effect</h4>
    
    <div style='background:white; padding:10px; border-left:4px solid #4CAF50; color:#333; margin-bottom:10px;'>
        <p style='margin:5px 0;'><strong>Key insight:</strong></p>
        <p style='margin:5px 0;'>{explanation}</p>
    </div>
    
    <p style='background:#c8e6c9; padding:10px; border-left:4px solid #388E3C; color:#1b5e20;'>
        <strong>Important:</strong> Rotation center is ESSENTIAL. Different centers always produce different results, even with the same angle.
    </p>
</div>
"""
        return html
    
    # ==================== SVG RENDERING METHODS ====================
    
    def _render_rotation_diagram_svg(self, angle: int, direction: str = "clockwise") -> str:
        """
        Render SVG diagram showing rotation around center point
        
        Args:
            angle: Rotation angle in degrees (90, 180, 270)
            direction: "clockwise" or "counterclockwise"
            
        Returns:
            HTML string with SVG diagram
        """
        center_x, center_y = 150, 150
        radius = 80
        
        # Calculate initial point position (top)
        initial_angle = 90  # Start from top
        final_angle = initial_angle - angle if direction == "clockwise" else initial_angle + angle
        
        # Convert to radians for calculation
        import math
        final_angle_rad = math.radians(final_angle)
        initial_angle_rad = math.radians(initial_angle)
        
        # Calculate point positions
        x1 = center_x + radius * math.cos(initial_angle_rad)
        y1 = center_y - radius * math.sin(initial_angle_rad)
        x2 = center_x + radius * math.cos(final_angle_rad)
        y2 = center_y - radius * math.sin(final_angle_rad)
        
        # Direction and color
        is_clockwise = direction.lower() == "clockwise"
        arc_color = "#2196F3" if is_clockwise else "#FF5722"
        direction_label = "Clockwise" if is_clockwise else "Counterclockwise"
        direction_arrow = "⟳" if is_clockwise else "⟲"
        
        # Build SVG
        html = f"""
<div style="border:2px solid {arc_color}; border-radius:8px; padding:15px; background:{'#e3f2fd' if is_clockwise else '#ffebee'}; text-align:center;">
    <h4 style="color:{'#1976D2' if is_clockwise else '#C62828'}; margin-top:0;">Rotation: {angle}° {direction_label} {direction_arrow}</h4>
    
    <svg width="350" height="350" style="border:1px solid #ccc; background:white; display:inline-block;">
        <!-- Grid background -->
        <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e0e0e0" stroke-width="0.5"/>
            </pattern>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="{arc_color}" />
            </marker>
        </defs>
        <rect width="350" height="350" fill="url(#grid)" />
        
        <!-- Rotation circle -->
        <circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="#ccc" stroke-width="2" stroke-dasharray="4,4"/>
        
        <!-- Center point -->
        <circle cx="{center_x}" cy="{center_y}" r="4" fill="#000"/>
        <text x="{center_x+10}" y="{center_y-5}" font-size="12" font-weight="bold">O</text>
        
        <!-- Initial point and line -->
        <circle cx="{x1}" cy="{y1}" r="6" fill="#4CAF50"/>
        <line x1="{center_x}" y1="{center_y}" x2="{x1}" y2="{y1}" stroke="#4CAF50" stroke-width="2"/>
        <text x="{x1-15}" y="{y1-5}" font-size="11" font-weight="bold" fill="#4CAF50">Start</text>
        
        <!-- Final point and line -->
        <circle cx="{x2}" cy="{y2}" r="6" fill="#D32F2F"/>
        <line x1="{center_x}" y1="{center_y}" x2="{x2}" y2="{y2}" stroke="#D32F2F" stroke-width="2"/>
        <text x="{x2+5}" y="{y2+15}" font-size="11" font-weight="bold" fill="#D32F2F">End</text>
        
        <!-- Rotation arc (approximated with circle segment indicator) -->
        <text x="{center_x}" y="{center_y-50}" text-anchor="middle" font-size="14" font-weight="bold" fill="{arc_color}">
            {angle}°
        </text>
    </svg>
    
    <p style="background:white; padding:10px; border-left:4px solid {arc_color}; color:#333; margin-top:10px; text-align:left; font-size:13px;">
        <strong>How rotation works:</strong><br>
        • Point starts at the <span style="color:#4CAF50;"><strong>green position</strong></span><br>
        • Rotate {angle}° {direction_label.lower()} around center O<br>
        • Point ends at the <span style="color:#D32F2F;"><strong>red position</strong></span><br>
        • Distance from center stays the same!
    </p>
</div>
"""
        return html
    
    # ==================== UTILITY METHODS ====================
    
    def _difficulty_level_to_int(self, difficulty: str) -> int:
        """Convert difficulty string to 1-5 scale"""
        mapping = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
            "expert": 4,
        }
        return mapping.get(difficulty.lower(), 2) if difficulty else 2