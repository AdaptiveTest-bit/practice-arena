"""
SYMMETRY - INTEGRATED STRATEGY
==============================

Hybrid Neuro-Symbolic approach for Symmetry with SVG rendering

Integrates:
1. Visual spatial with SVG diagrams
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Line placement error, Reflection confusion)
4. Rich SVG rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class SymmetryIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic visual logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich SVG visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.SYMMETRY
    chapter_name = "Symmetry"
    description = "Symmetry with hybrid neuro-symbolic approach and SVG rendering"
    
    def __init__(self):
        super().__init__()
        # Initialize hybrid system components here
        pass
    
    def generate(self) -> Question:
        """
        Main generation pipeline:
        1. Select problem type
        2. Generate skeleton (PHASE 1)
        3. Generate K.C. Nag story (PHASE 2)
        4. Generate misconception options (PHASE 3)
        5. Render rich question with SVG (PHASE 4)
        6. Create trackable Question (PHASE 5)
        """
        problem_type = random.choice([
            "line_symmetry_identification",
            "count_lines_of_symmetry",
            "draw_line_of_symmetry",
        ])
        
        if problem_type == "line_symmetry_identification":
            return self._generate_line_symmetry_identification()
        elif problem_type == "count_lines_of_symmetry":
            return self._generate_count_lines_of_symmetry()
        else:  # draw_line_of_symmetry
            return self._generate_draw_line_of_symmetry()
    
    def _generate_line_symmetry_identification(self) -> Question:
        """
        Line Symmetry Identification - Does shape have line symmetry?
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich SVG Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic skeleton
        symmetric_shapes = [
            ("Square", "Yes", 4),
            ("Rectangle", "Yes", 2),
            ("Circle", "Yes", "Infinite"),
            ("Equilateral Triangle", "Yes", 3),
            ("Isosceles Triangle", "Yes", 1),
        ]
        
        asymmetric_shapes = [
            ("Right Triangle", "No", 0),
            ("Scalene Triangle", "No", 0),
            ("Irregular Quadrilateral", "No", 0),
            ("Letter F", "No", 0),
            ("Leaf (simple)", "No", 0),
        ]
        
        # Randomly pick symmetric or asymmetric
        if random.random() > 0.5:
            shape_name, has_symmetry, num_lines = random.choice(symmetric_shapes)
            correct_answer = "Yes"
        else:
            shape_name, has_symmetry, num_lines = random.choice(asymmetric_shapes)
            correct_answer = "No"
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A butterfly has the shape of a {shape_name}. When you fold the paper in half, do the two sides match perfectly?",
            f"Your mirror shows a {shape_name}. Does it look the same on both sides of an imaginary line?",
            f"A {shape_name} is drawn on paper. If you fold it in half, do both halves match?",
        ])
        
        # PHASE 3: Misconception-based distractors
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct answer",
                None,
                None
            ),
            1: (
                "No" if correct_answer == "Yes" else "Yes",
                MisconceptionType.INCOMPLETE_REASONING,
                "Flipped the correct answer",
                "Student didn't carefully check if both sides match",
                "Fold the shape mentally along different lines. If even one line makes both halves match, it has line symmetry."
            ),
            2: (
                "Maybe",
                MisconceptionType.FORMULA_CONFUSION,
                "Unsure between line and rotational symmetry",
                "Student confused line symmetry with rotational symmetry",
                "Line symmetry: fold along a line and both halves match. Rotational symmetry: spin around a point and shape looks same."
            ),
            3: (
                "Partially",
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Thinks partial match is enough",
                "Student thinks some parts matching means the shape has line symmetry",
                "For true line symmetry, EVERY point on one side must have a matching point on the other side when folded."
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
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description=desc,
                    why_wrong=why_wrong or "Correct",
                    teaching_point=teaching or "Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=opt_val,
                    misconception_type=misconception,
                    description=desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Not checking all possible fold lines",
            custom_why_effective="Students often don't systematically test different lines",
            custom_how_to_avoid="Try folding along horizontal, vertical, AND diagonal lines. If even one works, shape has line symmetry."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        steps = [
            f"Shape: {shape_name}",
            f"Test folding along a line (horizontal, vertical, or diagonal)",
            f"Check: Do both halves match exactly?",
            f"If yes, shape has line symmetry",
            f"Answer: {correct_answer}"
        ]
        
        # PHASE 4: Rich rendering with SVG
        visual_diagram = self._render_symmetry_identification_svg(shape_name, correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Line Symmetry - Identification",
            logical_trap="K.C. Nag Trap: Students don't systematically check all possible fold lines. They often assume all closed shapes are symmetric or confuse line symmetry with rotational symmetry.",
            data_representation=f"```\nShape: {shape_name}\nHas line symmetry?\n```",
            question_text=f"Does a {shape_name} have line symmetry? (Does it look the same when folded along a line?)",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Understanding symmetry requires careful observation. A shape has line symmetry if you can fold it along a line so that both halves match perfectly.",
            visual_hints=[
                f"Think about folding a {shape_name} in half",
                "Would the two halves match exactly?",
                "Try different fold directions: horizontal, vertical, diagonal",
                f"A {shape_name} has line symmetry: {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _generate_count_lines_of_symmetry(self) -> Question:
        """
        Count Lines Of Symmetry - How many lines of symmetry does this shape have?
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich SVG Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic skeleton
        shapes_with_counts = [
            ("Square", 4),
            ("Rectangle (not square)", 2),
            ("Equilateral Triangle", 3),
            ("Isosceles Triangle (not equilateral)", 1),
            ("Rhombus", 2),
            ("Regular Pentagon", 5),
            ("Regular Hexagon", 6),
        ]
        
        shape_name, num_lines = random.choice(shapes_with_counts)
        correct_answer = str(num_lines)
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A {shape_name} is drawn on a paper. You want to fold it so both halves match. How many different fold lines can you draw?",
            f"A mirror reflects a {shape_name}. How many different mirror positions show the same shape?",
            f"A {shape_name} can be folded in different ways. Count how many fold lines make the two halves match perfectly.",
        ])
        
        # PHASE 3: Misconception-based distractors
        wrong_answer_1 = str(num_lines + 1)
        wrong_answer_2 = str(max(0, num_lines - 1))
        wrong_answer_3 = str(2) if num_lines != 2 else "3"
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct count",
                None,
                None
            ),
            1: (
                wrong_answer_1,
                MisconceptionType.INCOMPLETE_REASONING,
                "Counted one extra line",
                "Student included a line that doesn't actually create symmetry",
                "Check each line carefully: fold along it mentally and see if both halves match exactly."
            ),
            2: (
                wrong_answer_2,
                MisconceptionType.INCOMPLETE_REASONING,
                "Missed one symmetry line",
                "Student didn't check all possible directions (horizontal, vertical, diagonal)",
                "Systematically check: horizontal through center, vertical through center, and all diagonals."
            ),
            3: (
                wrong_answer_3,
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Confused with a different shape",
                f"Student thought {shape_name} has the same number of lines as a rectangle or other shape",
                f"Every shape has a unique number of symmetry lines. {shape_name} has exactly {num_lines}."
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
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description=desc,
                    why_wrong=why_wrong or "Correct",
                    teaching_point=teaching or "Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=opt_val,
                    misconception_type=misconception,
                    description=desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Not checking all fold directions",
            custom_why_effective="Students forget to check horizontal, vertical, AND diagonals",
            custom_how_to_avoid="Systematically check every possible line through the center. Count them all."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        steps = [
            f"Shape: {shape_name}",
            f"Test different fold lines (horizontal, vertical, diagonal)",
            f"Count how many fold lines create perfect matching halves",
            f"Each successful fold = one line of symmetry",
            f"Answer: {num_lines} line(s) of symmetry"
        ]
        
        # PHASE 4: Rich rendering with SVG
        visual_diagram = self._render_symmetry_count_svg(shape_name, num_lines)
        
        question = Question(
            chapter=self.chapter,
            topic="Line Symmetry - Count Lines",
            logical_trap="K.C. Nag Trap: Students often miss symmetry lines by not checking all directions. They might check only horizontal/vertical and forget diagonals.",
            data_representation=f"```\nShape: {shape_name}\nNumber of symmetry lines: ?\n```",
            question_text=f"How many lines of symmetry does a {shape_name} have?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Some shapes have many symmetry lines! Count carefully by testing each possible fold direction.",
            visual_hints=[
                f"Check fold along horizontal through center",
                f"Check fold along vertical through center",
                f"Check fold along both diagonals",
                f"Count all the fold lines that work"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _generate_draw_line_of_symmetry(self) -> Question:
        """
        Draw Line Of Symmetry - Which of these is a line of symmetry?
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich SVG Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic skeleton
        valid_lines = [
            ("Rectangle", "Vertical through center", "Vertical"),
            ("Rectangle", "Horizontal through center", "Horizontal"),
            ("Square", "Diagonal from corner to corner", "Diagonal"),
            ("Square", "Horizontal through center", "Horizontal"),
            ("Equilateral Triangle", "Vertical from top vertex to base", "Vertical"),
            ("Isosceles Triangle", "Vertical from top vertex to base", "Vertical"),
            ("Diamond (Rhombus)", "Horizontal through center", "Horizontal"),
            ("Diamond (Rhombus)", "Vertical through center", "Vertical"),
        ]
        
        shape_name, line_description, line_type = random.choice(valid_lines)
        correct_answer = line_description
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A {shape_name} is drawn on paper. Which line, if you fold along it, would make both halves match perfectly?",
            f"Looking at a {shape_name}, which direction can you fold it for the two sides to match?",
            f"A {shape_name} can be folded along different lines. Which of these is a true fold line of symmetry?",
        ])
        
        # PHASE 3: Misconception-based distractors
        wrong_line_1 = "Horizontal through center" if line_type != "Horizontal" else "Vertical through center"
        wrong_line_2 = "Diagonal from corner to corner" if line_type != "Diagonal" else "Horizontal through center"
        wrong_line_3 = "Along one edge" if line_type not in ["Along one edge"] else "Off-center fold"
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "True line of symmetry",
                None,
                None
            ),
            1: (
                wrong_line_1,
                MisconceptionType.INCOMPLETE_REASONING,
                "Wrong line direction",
                "Student chose a direction that doesn't create symmetry for this shape",
                f"The correct fold direction for a {shape_name} is {line_description.lower()}."
            ),
            2: (
                wrong_line_2,
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Confused which direction is symmetric",
                "Student thought a different fold direction works for this shape",
                f"For a {shape_name}, a {line_type.lower()} fold creates a line of symmetry."
            ),
            3: (
                wrong_line_3,
                MisconceptionType.FORMULA_CONFUSION,
                "Folded along edge instead of through middle",
                "Student thought folding along the perimeter creates symmetry",
                "Line symmetry requires folding through the middle so both halves are equal."
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
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description=desc,
                    why_wrong=why_wrong or "Correct",
                    teaching_point=teaching or "Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=opt_val,
                    misconception_type=misconception,
                    description=desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Visualizing fold incorrectly or positioning line off-center",
            custom_why_effective="Students visualize folding incorrectly or position the line off-center",
            custom_how_to_avoid="Imagine carefully bringing one half on top of the other. They must match exactly."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        steps = [
            f"Shape: {shape_name}",
            f"Test fold line: {line_description}",
            "Imagine folding along this line",
            "Do both halves match exactly?",
            f"Answer: {correct_answer}"
        ]
        
        # PHASE 4: Rich rendering with SVG
        visual_diagram = self._render_line_of_symmetry_svg(shape_name, line_type)
        
        question = Question(
            chapter=self.chapter,
            topic="Line Symmetry - Identify Correct Line",
            logical_trap="K.C. Nag Trap: Students often choose the wrong line because they don't visualize folding correctly. They may position the line off-center or use the wrong direction.",
            data_representation=f"```\nShape: {shape_name}\nWhich line creates symmetry?\n```",
            question_text=f"Which of the following is a line of symmetry for a {shape_name}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Finding a line of symmetry requires careful visualization. Imagine folding the shape along that line carefully.",
            visual_hints=[
                f"Mentally fold the {shape_name} along each given line",
                "Do the two halves match exactly when folded?",
                f"The line must go through the center/middle of the {shape_name}",
                f"The correct fold direction for a {shape_name} is {line_description.lower()}"
            ]
        )
        
        self._validate_question(question)
        return question


    # ==================== SVG RENDERING METHODS ====================
    
    def _render_symmetry_identification_svg(self, shape_name: str, has_symmetry: str) -> str:
        """
        Render SVG diagram showing shape with symmetry indication
        """
        symbol = "✓" if has_symmetry == "Yes" else "✗"
        color = "#4CAF50" if has_symmetry == "Yes" else "#f44336"
        
        shape_svg = self._get_shape_svg(shape_name, "#2196F3", 2)
        
        html = f"""
<div style="border:2px solid {color}; border-radius:8px; padding:15px; background:#f5f5f5; text-align:center;">
    <h4 style="color:{color}; margin-top:0;">Shape: {shape_name}</h4>
    
    <svg width="250" height="250" style="border:1px solid #ccc; background:white; display:inline-block; margin:10px 0;">
        {shape_svg}
    </svg>
    
    <p style="font-size:28px; color:{color}; margin:10px 0;">{symbol}</p>
    
    <p style="background:white; padding:10px; border-left:4px solid {color}; color:#333; text-align:left;">
        <strong>Has line symmetry?</strong> {has_symmetry}<br>
        A shape has line symmetry if you can fold it so both halves match perfectly.
    </p>
</div>
"""
        return html
    
    def _render_symmetry_count_svg(self, shape_name: str, num_lines: int) -> str:
        """
        Render SVG diagram showing symmetry line count with visual
        """
        shape_svg = self._get_shape_with_symmetry_lines_svg(shape_name, num_lines)
        
        html = f"""
<div style="border:2px solid #2196F3; border-radius:8px; padding:15px; background:#f0f7ff; text-align:center;">
    <h4 style="color:#1976D2; margin-top:0;">Lines of Symmetry: {shape_name}</h4>
    
    <svg width="280" height="280" style="border:1px solid #ccc; background:white; display:inline-block; margin:10px 0;">
        {shape_svg}
    </svg>
    
    <p style="font-size:20px; font-weight:bold; text-align:center; color:#1976D2; margin:10px 0;">
        {num_lines} line(s) of symmetry
    </p>
    
    <p style="background:white; padding:10px; border-left:4px solid #2196F3; color:#333; text-align:left; font-size:13px;">
        <strong>How to find:</strong> Check fold directions:<br>
        • Horizontal through center<br>
        • Vertical through center<br>
        • Diagonal corners (if applicable)
    </p>
</div>
"""
        return html
    
    def _render_line_of_symmetry_svg(self, shape_name: str, line_type: str = "vertical") -> str:
        """
        Render SVG diagram showing a shape with one highlighted line of symmetry
        """
        shape_svg = self._get_shape_svg(shape_name, "#E3F2FD", 2)
        symmetry_line_svg = self._get_symmetry_line_svg(line_type)
        
        line_label = line_type.capitalize()
        
        html = f"""
<div style="border:2px solid #1976D2; border-radius:8px; padding:15px; background:#f0f7ff; text-align:center;">
    <h4 style="color:#1976D2; margin-top:0;">Line of Symmetry: {shape_name}</h4>
    
    <svg width="300" height="300" style="border:1px solid #ccc; background:white; display:inline-block;">
        <!-- Grid background -->
        <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e0e0e0" stroke-width="0.5"/>
            </pattern>
        </defs>
        <rect width="300" height="300" fill="url(#grid)" />
        
        <!-- Shape -->
        {shape_svg}
        
        <!-- Symmetry line -->
        {symmetry_line_svg}
        
        <!-- Label -->
        <text x="150" y="285" text-anchor="middle" font-size="12" fill="#D32F2F" font-weight="bold">{line_label} Line</text>
    </svg>
    
    <p style="background:white; padding:10px; border-left:4px solid #D32F2F; color:#333; margin-top:10px; text-align:left; font-size:13px;">
        <strong>How to verify:</strong><br>
        Fold the shape along the <span style="color:#D32F2F;"><strong>{line_label.lower()}</strong></span> line.<br>
        If both halves match perfectly, it is a true line of symmetry. ✓
    </p>
</div>
"""
        return html
    
    def _get_shape_svg(self, shape_name: str, fill_color: str, stroke_width: int) -> str:
        """Generate SVG for a shape"""
        center_x, center_y = 125, 125
        
        if "Square" in shape_name:
            return f'<rect x="50" y="50" width="150" height="150" fill="{fill_color}" stroke="#1976D2" stroke-width="{stroke_width}"/>'
        elif "Rectangle" in shape_name:
            return f'<rect x="40" y="60" width="170" height="130" fill="{fill_color}" stroke="#1976D2" stroke-width="{stroke_width}"/>'
        elif "Triangle" in shape_name:
            return f'<polygon points="125,40 70,180 180,180" fill="{fill_color}" stroke="#1976D2" stroke-width="{stroke_width}"/>'
        elif "Diamond" in shape_name or "Rhombus" in shape_name:
            return f'<polygon points="125,40 180,125 125,210 70,125" fill="{fill_color}" stroke="#1976D2" stroke-width="{stroke_width}"/>'
        elif "Circle" in shape_name:
            return f'<circle cx="{center_x}" cy="{center_y}" r="65" fill="{fill_color}" stroke="#1976D2" stroke-width="{stroke_width}"/>'
        else:
            return f'<rect x="50" y="50" width="150" height="150" fill="{fill_color}" stroke="#1976D2" stroke-width="{stroke_width}"/>'
    
    def _get_symmetry_line_svg(self, line_type: str) -> str:
        """Generate SVG for a symmetry line"""
        if line_type.lower() == "horizontal":
            return '<line x1="30" y1="125" x2="220" y2="125" stroke="#D32F2F" stroke-width="3" stroke-dasharray="5,5"/>'
        elif line_type.lower() == "diagonal":
            return '<line x1="50" y1="50" x2="200" y2="200" stroke="#D32F2F" stroke-width="3" stroke-dasharray="5,5"/>'
        else:  # vertical
            return '<line x1="125" y1="30" x2="125" y2="220" stroke="#D32F2F" stroke-width="3" stroke-dasharray="5,5"/>'
    
    def _get_shape_with_symmetry_lines_svg(self, shape_name: str, num_lines: int) -> str:
        """Generate SVG for a shape with all its symmetry lines shown"""
        center_x, center_y = 140, 140
        
        shape_svg = self._get_shape_svg(shape_name, "#E3F2FD", 2)
        
        lines_svg = ""
        
        if "Square" in shape_name and num_lines == 4:
            lines_svg = f'''
            <line x1="30" y1="140" x2="250" y2="140" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
            <line x1="140" y1="30" x2="140" y2="250" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
            <line x1="50" y1="50" x2="230" y2="230" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
            <line x1="230" y1="50" x2="50" y2="230" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
            '''
        elif "Rectangle" in shape_name and num_lines == 2:
            lines_svg = f'''
            <line x1="30" y1="140" x2="250" y2="140" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
            <line x1="140" y1="30" x2="140" y2="250" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
            '''
        elif "Triangle" in shape_name:
            if num_lines == 3:
                lines_svg = f'''
                <line x1="140" y1="30" x2="140" y2="250" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
                <line x1="50" y1="230" x2="190" y2="90" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
                <line x1="230" y1="230" x2="90" y2="90" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>
                '''
            else:
                lines_svg = f'<line x1="140" y1="30" x2="140" y2="250" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>'
        else:
            lines_svg = f'<line x1="140" y1="30" x2="140" y2="250" stroke="#D32F2F" stroke-width="2" stroke-dasharray="4,4" opacity="0.7"/>'
        
        return f"{shape_svg}\n{lines_svg}"
    
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
