"""
CUBE COUNTING - INTEGRATED STRATEGY
===================================

Hybrid Neuro-Symbolic approach for Cube Counting

Integrates:
1. 3D enumeration with spatial reasoning
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Hidden cube miscounting, Surface area formula error)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class CubeCountingIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic 3d logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.CUBE_COUNTING
    chapter_name = "Cube Counting"
    description = "Cube Counting with hybrid neuro-symbolic approach"
    
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
            "visible_cubes",
            "hidden_cubes",
            "surface_area_cubes",
        ])
        
        if problem_type == "visible_cubes":
            return self._generate_visible_cubes()
        elif problem_type == "hidden_cubes":
            return self._generate_hidden_cubes()
        else:  # surface_area_cubes
            return self._generate_surface_area_cubes()
    
    def _generate_visible_cubes(self) -> Question:
        """
        Visible Cubes - Count all visible cubes in a structure
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Create simple 3D structure: 2×2, 2×3, or 3×3 arrangement
        length = random.choice([2, 3])
        width = random.choice([2, 3])
        height = random.choice([2, 3])
        
        # Count all visible cubes in the rectangular structure
        correct_count = length * width * height
        correct_answer = str(correct_count)
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A builder stacks sugar cubes in a structure that is {length} cubes long, {width} cubes wide, and {height} cubes tall. How many sugar cubes in total?",
            f"Ravi arranges wooden blocks in a rectangular box: {length} × {width} × {height}. How many blocks did he use?",
            f"A toy has building blocks arranged as a {length} × {width} × {height} rectangular stack. How many blocks are there?",
            f"A classroom storage unit has shelves arranged as {length} rows, {width} columns, and {height} layers high. How many cubes can fit?",
            f"A chocolate bar is divided into a {length} × {width} × {height} cube structure. How many chocolate pieces total?",
        ])
        
        character = random.choice(["Vikram", "Ananya", "Rohan", "Priya"])
        misconception_hook = random.choice([
            "only counted visible faces, not all cubes",
            "forgot to count cubes in the middle",
            "miscalculated the dimensions",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Only counting visible faces (most common trap)
        # A face of a 3×3×3 structure has 9 visible, but interior has more
        visible_on_surface = 2 * (length * width) + 2 * (length * height) + 2 * (width * height) - 4 * (length + width + height - 3)
        # Simpler: just count surface which is less than total
        if length == 2 and width == 2 and height == 2:
            surface_only = 8  # All are on corners
        elif length == 2:
            surface_only = (length * width * 2) + ((width - 2) * height * 2) + (length * (height - 2) * 2)
        else:
            surface_only = (length * width) * 2 + (length * height - length) * 2 + (width * height - width) * 2 // 2
        
        wrong_options.append((
            str(surface_only + random.randint(2, 5)),
            MisconceptionType.INCOMPLETE_REASONING,
            "Only counted visible cubes",
            f"You may have only counted the cubes on the outside surface, but the problem asks for ALL cubes (including hidden ones inside).",
            f"Total = length × width × height = {length} × {width} × {height} = {correct_count}"
        ))
        
        # Misconception 2: Miscalculation (off by one)
        wrong_calc = correct_count - random.choice([2, 3, 4])
        wrong_options.append((
            str(wrong_calc),
            MisconceptionType.FORMULA_CONFUSION,
            "Miscalculation",
            f"This is close but not exact. Double-check: {length} × {width} × {height} = {correct_count}, not {wrong_calc}.",
            f"Verify by using the formula: Volume = length × width × height = {correct_count}"
        ))
        
        # Misconception 3: Confusion with surface area or perimeter concept
        perimeter_like = 2 * (length + width + height)
        wrong_options.append((
            str(perimeter_like),
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Used formula for perimeter/edges",
            f"You calculated {perimeter_like}, which looks like a perimeter or edge formula, not volume.",
            f"Remember: Volume (total cubes) = length × width × height = {correct_count}"
        ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"3D Structure: {length} × {width} × {height}",
            f"Interpretation: {length} long, {width} wide, {height} tall",
            f"Total cubes = length × width × height",
            f"Total cubes = {length} × {width} × {height}",
            f"Total cubes = {correct_count}"
        ]
        
        visual_diagram = self._render_cube_structure(length, width, height)
        
        hints = [
            f"Hint 1: You're counting ALL cubes in a 3D structure",
            f"Hint 2: The structure is {length} × {width} × {height}",
            f"Hint 3: Use the volume formula: length × width × height",
            f"Hint 4: {length} × {width} × {height} = {correct_count} cubes"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Counting All Visible Cubes",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Count ALL cubes including those inside, not just the surface!",
            data_representation=f"{length}×{width}×{height} rectangular 3D structure",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s cube counting problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_hidden_cubes(self) -> Question:
        """
        Hidden Cubes - Count cubes you can't see (internal/hidden)
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # 3×3×3 or 4×4×4 structure (larger for hidden cubes to be meaningful)
        size = random.choice([3, 4])
        
        # Total cubes in structure
        total_cubes = size * size * size
        
        # Hidden cubes = cubes not on any surface
        # For a size×size×size structure:
        # Hidden cubes = (size-2)×(size-2)×(size-2)
        hidden_cubes = (size - 2) ** 3
        
        correct_answer = str(hidden_cubes)
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A large cube is made of {total_cubes} smaller cubes ({size}×{size}×{size}). The outer surface is painted red. How many cubes are NOT painted (hidden inside)?",
            f"A cube stack is {size}×{size}×{size}. The outside layers are visible, but some are hidden completely inside. How many are completely hidden?",
            f"A gift box is filled with {total_cubes} small cubes ({size}×{size}×{size}). After removing the outer layer, how many cubes remain inside?",
            f"A {size}×{size}×{size} Rubik's cube has cubes that you can see and cubes hidden inside. How many are hidden?",
            f"A decorative structure has {total_cubes} cubes ({size}×{size}×{size}). The outside is decorated, but how many cubes are never visible?",
        ])
        
        character = random.choice(["Dev", "Priya", "Arjun", "Sneha"])
        misconception_hook = random.choice([
            "forgot some hidden layers",
            "confused total with hidden",
            "miscounted the inner structure",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Confusing total cubes with hidden cubes
        wrong_options.append((
            str(total_cubes),
            MisconceptionType.FORMULA_CONFUSION,
            "Used total instead of hidden",
            f"You gave {total_cubes} (the total), but the question asks for hidden cubes only. Hidden = {hidden_cubes}.",
            f"Formula: Hidden cubes = (size-2)³ = ({size}-2)³ = {hidden_cubes}"
        ))
        
        # Misconception 2: Surface cubes (opposite of what's asked)
        surface_cubes = total_cubes - hidden_cubes
        wrong_options.append((
            str(surface_cubes),
            MisconceptionType.INCOMPLETE_REASONING,
            "Counted visible instead of hidden",
            f"You gave {surface_cubes} (the visible/surface cubes), but we need the HIDDEN cubes inside = {hidden_cubes}.",
            f"Hidden cubes = Total - Surface = {total_cubes} - {surface_cubes} = {hidden_cubes}"
        ))
        
        # Misconception 3: Off by one or calculation error
        wrong_calc = hidden_cubes + random.choice([-2, -1, 1, 2])
        if wrong_calc > 0 and wrong_calc != hidden_cubes:
            wrong_options.append((
                str(wrong_calc),
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Miscalculation",
                f"This is close but not exact. Hidden cubes = (size-2)³ = ({size}-2)³ = {hidden_cubes}, not {wrong_calc}.",
                f"Double-check: ({size}-2) × ({size}-2) × ({size}-2) = {size-2} × {size-2} × {size-2} = {hidden_cubes}"
            ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Total structure: {size} × {size} × {size} = {total_cubes} cubes",
            f"Remove outer layer on all sides",
            f"Remaining inner structure: {size-2} × {size-2} × {size-2}",
            f"Hidden cubes = ({size}-2) × ({size}-2) × ({size}-2) = {size-2} × {size-2} × {size-2} = {hidden_cubes}"
        ]
        
        visual_diagram = self._render_hidden_cubes_diagram(size, total_cubes, hidden_cubes)
        
        hints = [
            f"Hint 1: Start with total structure: {size}×{size}×{size} = {total_cubes} cubes",
            f"Hint 2: Remove the outer layer on all sides",
            f"Hint 3: The inner hidden part is smaller: ({size}-2)×({size}-2)×({size}-2)",
            f"Hint 4: Hidden cubes = {hidden_cubes}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Counting Hidden Cubes",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. The hidden cubes are inside after you remove the outer layer!",
            data_representation=f"{size}×{size}×{size} cube with outer layer visible and inner layer hidden",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s hidden cube problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_surface_area_cubes(self) -> Question:
        """
        Surface Area Cubes - Count visible surface area in cube units
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Rectangular structure dimensions
        length = random.randint(3, 5)
        width = random.randint(3, 5)
        height = random.randint(3, 5)
        
        # Surface area of rectangular structure (counting unit cube faces)
        # Each face has unit cube faces visible
        # Front/Back: length × height
        # Left/Right: width × height
        # Top/Bottom: length × width
        
        front_back = 2 * (length * height)
        left_right = 2 * (width * height)
        top_bottom = 2 * (length * width)
        
        correct_surface_area = front_back + left_right + top_bottom
        correct_answer = str(correct_surface_area)
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A rectangular block of cubes is {length} × {width} × {height}. How many unit cube faces are visible on the surface?",
            f"A wooden block structure is {length} units long, {width} units wide, and {height} units tall. How many square units are on its surface?",
            f"A rectangular tank is {length} × {width} × {height} unit cubes. The outside needs to be painted. How many unit square faces need paint?",
            f"A decorative wall uses unit cubes in a {length} × {width} × {height} arrangement. How many faces are on the outside?",
            f"A {length} × {width} × {height} cube structure is covered with tiles (one tile per unit face). How many tiles are needed?",
        ])
        
        character = random.choice(["Rahul", "Ananya", "Vikram", "Priya"])
        misconception_hook = random.choice([
            "multiplied dimensions instead of using surface area formula",
            "only counted one face",
            "miscalculated the formula",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Using volume instead of surface area
        volume = length * width * height
        wrong_options.append((
            str(volume),
            MisconceptionType.FORMULA_CONFUSION,
            "Used volume formula instead",
            f"You calculated {volume}, which is the VOLUME (space inside), not surface area (faces outside).",
            f"Surface Area = 2(lw + lh + wh) = 2({length}×{width} + {length}×{height} + {width}×{height}) = {correct_surface_area}"
        ))
        
        # Misconception 2: Only counting one face
        one_face = length * width
        wrong_options.append((
            str(one_face),
            MisconceptionType.INCOMPLETE_REASONING,
            "Only counted one face",
            f"You counted {one_face} (one face), but the structure has 6 faces! Surface area must account for all faces.",
            f"All 6 faces: Front + Back + Left + Right + Top + Bottom = {correct_surface_area} square units"
        ))
        
        # Misconception 3: Wrong formula or calculation
        wrong_formula = (length + width + height) * 2
        wrong_options.append((
            str(wrong_formula),
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Wrong formula",
            f"You used a formula that gives {wrong_formula}, but that's not the surface area of a rectangle.",
            f"Correct formula: Surface Area = 2(length×width + length×height + width×height) = {correct_surface_area}"
        ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Rectangular structure: {length} × {width} × {height}",
            f"Surface Area Formula: 2(lw + lh + wh)",
            f"Front & Back faces: 2 × ({length} × {height}) = {front_back}",
            f"Left & Right faces: 2 × ({width} × {height}) = {left_right}",
            f"Top & Bottom faces: 2 × ({length} × {width}) = {top_bottom}",
            f"Total Surface Area = {front_back} + {left_right} + {top_bottom} = {correct_surface_area}"
        ]
        
        visual_diagram = self._render_surface_area_diagram(length, width, height, correct_surface_area)
        
        hints = [
            f"Hint 1: Surface area counts all faces on the outside (6 faces for a rectangle)",
            f"Hint 2: The dimensions are {length} × {width} × {height}",
            f"Hint 3: Formula: 2(lw + lh + wh) = 2({length}×{width} + {length}×{height} + {width}×{height})",
            f"Hint 4: Total surface area = {correct_surface_area} square units"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Surface Area of Rectangular Cubes",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Surface area means ALL outer faces, not volume inside!",
            data_representation=f"{length}×{width}×{height} rectangular structure with all 6 faces labeled",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s surface area problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question


    # ==================== IMPLEMENTATION GUIDE ====================
    #
    # For each _generate_* method:
    #
    # PHASE 1: Deterministic Skeleton
    # --------------------------------
    # def _generate_xxx(self) -> Question:
    #     # Generate parameters using pure Python/SymPy
    #     # Validate answer is correct (critical!)
    #     # Create MathSkeleton with parameters, solution, steps
    #     skeleton = MathSkeleton(...)
    #
    # PHASE 2: K.C. Nag Story
    # ----------------------
    # story_context = self.story_generator.generate_story_context(skeleton)
    # Or manually create StoryContext with:
    #   - concept_name: what we're learning
    #   - real_world_scenario: something from student's life
    #   - character_names: people in the story
    #   - narrative: the K.C. Nag story text
    #   - misconception_hooks: phrases that reveal traps
    #   - teaching_principles: how K.C. Nag would teach it
    #
    # PHASE 3: Misconception-Based Distractors
    # ----------------------------------------
    # For each of 3 misconceptions:
    #   distractor_info.append(DistractorInfo(
    #       value="...",  # What student sees
    #       misconception_type=MisconceptionType.XXX,
    #       description="...",  # Short label
    #       why_wrong="...",  # Why this is wrong
    #       teaching_point="..."  # What to learn instead
    #   ))
    #
    # PHASE 4: Rich Rendering
    # -----------------------
    # rich_content = self.renderer.render_rich_question(
    #     question_text=...,
    #     story_context=story_context,
    #     solution_steps=steps,
    #     explanation=...,
    #     visual_hint=...,
    #     progressive_hints=[hint1, hint2, hint3, hint4]
    # )
    #
    # PHASE 5: Question Object
    # -----------------------
    # question = Question(
    #     chapter=self.chapter,
    #     topic="...",
    #     logical_trap="K.C. Nag Trap: ...",
    #     data_representation="...",
    #     question_text=...,
    #     solution_steps=steps,
    #     answer=correct_answer,
    #     options=options,
    #     correct_option_index=correct_idx,
    #     distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
    #     trap_info=trap_info,
    #     bloom_info=bloom_info,
    #     rich_html_content=rich_content.get("html"),
    #     rich_narrative=rich_content.get("narrative"),
    #     visual_hints=rich_content.get("hints"),
    # )
    # self._validate_question(question)
    # return question
    
    # ======================================
    # RENDERING HELPER METHODS
    # ======================================
    
    def _render_cube_structure(self, length: int, width: int, height: int) -> dict:
        """Render a 3D cube structure visualization for total cube counting"""
        
        # HTML grid representation of the 3D structure
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">3D Cube Structure</h3>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
        """
        
        # Show dimensions
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Dimensions: {length} × {width} × {height}</p>
                    <svg width="200" height="200" style="border: 1px solid #ccc; background: white;">
                        <!-- Front face -->
                        <rect x="20" y="40" width="120" height="120" fill="none" stroke="#2563eb" stroke-width="2"/>
                        <!-- Depth lines -->
                        <line x1="20" y1="40" x2="40" y2="20" stroke="#2563eb" stroke-width="1"/>
                        <line x1="140" y1="40" x2="160" y2="20" stroke="#2563eb" stroke-width="1"/>
                        <line x1="140" y1="160" x2="160" y2="140" stroke="#2563eb" stroke-width="1"/>
                        <!-- Back face (isometric) -->
                        <polyline points="40,20 160,20 160,140 40,140" fill="none" stroke="#2563eb" stroke-width="1"/>
                        <!-- Label -->
                        <text x="100" y="180" font-size="12" text-anchor="middle">Front: {length}×{height}</text>
                    </svg>
                </div>
        """
        
        # Grid representation
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Top View: {length} × {width}</p>
                    <table style="margin: auto; border-collapse: collapse;">
        """
        
        # Create top view grid
        for row in range(width):
            html += "<tr>"
            for col in range(length):
                html += f'<td style="width: 25px; height: 25px; border: 1px solid #999; background: #dbeafe;"></td>'
            html += "</tr>"
        
        html += """
                    </table>
                </div>
        """
        
        total = length * width * height
        html += f"""
                <div style="text-align: center; margin-top: 10px;">
                    <p><strong>Total Cubes = {length} × {width} × {height} = {total}</strong></p>
                    <p style="font-size: 12px; color: #666;">Each small square represents one unit cube</p>
                </div>
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_hidden_cubes_diagram(self, size: int, total: int, hidden: int) -> dict:
        """Render visualization showing hidden vs visible cubes"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Hidden vs Visible Cubes ({size}×{size}×{size})</h3>
            <div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;">
        """
        
        # Left side: Total cubes
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Total Cubes</p>
                    <svg width="150" height="150" style="border: 1px solid #ccc; background: white;">
                        <!-- Grid of cubes -->
        """
        
        # Draw grid of all cubes
        cube_size = 40
        spacing = 5
        for i in range(size):
            for j in range(size):
                x = 20 + i * (cube_size + spacing)
                y = 20 + j * (cube_size + spacing)
                html += f'<rect x="{x}" y="{y}" width="{cube_size}" height="{cube_size}" fill="#dbeafe" stroke="#2563eb" stroke-width="1"/>'
        
        html += f"""
                        <text x="75" y="135" font-size="12" text-anchor="middle" font-weight="bold">{total}</text>
                    </svg>
                    <p style="margin-top: 10px;"><strong>Formula: {size}³ = {total}</strong></p>
                </div>
        """
        
        # Right side: Hidden cubes
        visible = total - hidden
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Hidden Cubes (Interior Only)</p>
                    <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                        <svg width="150" height="150" style="border: 1px solid #ccc; background: white;">
                            <!-- Outer layer (transparent) -->
        """
        
        # Draw outer layer as empty
        for i in range(size):
            for j in range(size):
                x = 20 + i * (cube_size + spacing)
                y = 20 + j * (cube_size + spacing)
                html += f'<rect x="{x}" y="{y}" width="{cube_size}" height="{cube_size}" fill="none" stroke="#ccc" stroke-width="1" stroke-dasharray="2,2"/>'
        
        # Inner layer (hidden)
        inner_size = size - 2
        inner_offset = 20 + (cube_size + spacing)
        for i in range(inner_size):
            for j in range(inner_size):
                x = inner_offset + i * (cube_size + spacing)
                y = inner_offset + j * (cube_size + spacing)
                html += f'<rect x="{x}" y="{y}" width="{cube_size}" height="{cube_size}" fill="#fca5a5" stroke="#dc2626" stroke-width="1"/>'
        
        html += f"""
                            <text x="75" y="135" font-size="12" text-anchor="middle" font-weight="bold">{hidden}</text>
                        </svg>
                    </div>
                    <p style="margin-top: 10px;"><strong>Formula: ({size}-2)³ = {hidden}</strong></p>
                </div>
        """
        
        html += f"""
            </div>
            <div style="margin-top: 20px; padding: 15px; background: #fef3c7; border-radius: 4px; border-left: 4px solid #f59e0b;">
                <p style="margin: 0;"><strong>Key Insight:</strong> Only the interior cubes are hidden!</p>
                <p style="margin: 5px 0 0 0; font-size: 12px;">Visible + Hidden = Total: {visible} + {hidden} = {total}</p>
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_surface_area_diagram(self, length: int, width: int, height: int, surface_area: int) -> dict:
        """Render surface area visualization with all 6 faces labeled"""
        
        front_back = 2 * (length * height)
        left_right = 2 * (width * height)
        top_bottom = 2 * (length * width)
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Surface Area Calculation ({length}×{width}×{height})</h3>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; align-items: center;">
        """
        
        # Isometric 3D representation
        html += """
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">3D View (Isometric)</p>
                    <svg width="200" height="220" style="border: 1px solid #ccc; background: white;">
                        <!-- Top face (yellow) -->
                        <polygon points="50,50 150,50 180,80 80,80" fill="#fef08a" stroke="#ca8a04" stroke-width="2"/>
                        <text x="115" y="70" font-size="11" text-anchor="middle" font-weight="bold" fill="#ca8a04">Top: l×w</text>
                        
                        <!-- Front face (blue) -->
                        <polygon points="50,80 150,80 150,180 50,180" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="100" y="135" font-size="11" text-anchor="middle" font-weight="bold" fill="#2563eb">Front: l×h</text>
                        
                        <!-- Right face (red) -->
                        <polygon points="150,80 180,80 180,180 150,180" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        <text x="165" y="135" font-size="10" text-anchor="middle" font-weight="bold" fill="#dc2626">Right: w×h</text>
                    </svg>
                </div>
        """
        
        # Calculation breakdown
        html += f"""
                <div style="background: white; padding: 15px; border-radius: 4px; border: 1px solid #e5e7eb; min-width: 250px;">
                    <p style="margin: 0 0 10px 0; font-weight: bold;">Formula Breakdown:</p>
                    <table style="width: 100%; text-align: left; font-size: 12px;">
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 8px; padding-left: 0;"><strong>Face</strong></td>
                            <td style="padding: 8px;"><strong>Count</strong></td>
                            <td style="padding: 8px;"><strong>Calculation</strong></td>
                        </tr>
                        <tr style="background: #dbeafe; border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 8px; padding-left: 0;">Front & Back</td>
                            <td style="padding: 8px;">2</td>
                            <td style="padding: 8px;">2 × ({length}×{height}) = {front_back}</td>
                        </tr>
                        <tr style="background: #fecaca; border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 8px; padding-left: 0;">Left & Right</td>
                            <td style="padding: 8px;">2</td>
                            <td style="padding: 8px;">2 × ({width}×{height}) = {left_right}</td>
                        </tr>
                        <tr style="background: #fef08a;">
                            <td style="padding: 8px; padding-left: 0;">Top & Bottom</td>
                            <td style="padding: 8px;">2</td>
                            <td style="padding: 8px;">2 × ({length}×{width}) = {top_bottom}</td>
                        </tr>
                    </table>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #e5e7eb;">
                        <p style="margin: 0; font-weight: bold; font-size: 13px;">Total Surface Area = {front_back} + {left_right} + {top_bottom} = <span style="color: #dc2626; font-size: 14px;">{surface_area}</span></p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return {"html": html}
    
    # ==================== SVG RENDERING METHODS ====================
    
    def _render_cube_structure_svg(self, dimension: int, visible_cubes: int, hidden_cubes: int) -> str:
        """
        Render SVG diagram showing 3D cube structure
        
        Args:
            dimension: Size of the cube (e.g., 3 for 3×3×3)
            visible_cubes: Number of visible cubes on surface
            hidden_cubes: Number of hidden/interior cubes
            
        Returns:
            HTML string with SVG 3D cube visualization
        """
        total = dimension ** 3
        
        html = f"""
<div style="border:2px solid #1976D2; border-radius:8px; padding:15px; background:#e3f2fd; text-align:center;">
    <h4 style="color:#1976D2; margin-top:0;">Cube Structure: {dimension}×{dimension}×{dimension}</h4>
    
    <svg width="300" height="300" style="border:1px solid #ccc; background:white; display:inline-block; margin:10px 0;">
        <!-- 3D cube representation (isometric view) -->
        <defs>
            <pattern id="cubeGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                <rect x="0" y="0" width="40" height="40" fill="none" stroke="#e0e0e0" stroke-width="0.5"/>
            </pattern>
        </defs>
        
        <!-- Visible faces of cube -->
        <!-- Front face (blue) -->
        <g>
            <polygon points="50,80 190,80 190,220 50,220" fill="#BBDEFB" stroke="#1976D2" stroke-width="2"/>
            <text x="120" y="155" text-anchor="middle" font-size="14" font-weight="bold" fill="#1565C0">Visible</text>
        </g>
        
        <!-- Top face (lighter blue) -->
        <g>
            <polygon points="50,80 120,40 260,40 190,80" fill="#E3F2FD" stroke="#1976D2" stroke-width="2"/>
        </g>
        
        <!-- Right face (green for interior hint) -->
        <g>
            <polygon points="190,80 260,40 260,180 190,220" fill="#C8E6C9" stroke="#4CAF50" stroke-width="2"/>
            <text x="220" y="130" text-anchor="middle" font-size="11" font-weight="bold" fill="#2E7D32">Interior</text>
        </g>
        
        <!-- Dimension labels -->
        <text x="120" y="250" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">{dimension}×{dimension}×{dimension}</text>
    </svg>
    
    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:15px;">
        <div style="background:white; padding:10px; border:1px solid #e0e0e0; border-radius:4px;">
            <p style="margin:0; font-size:12px; font-weight:bold; color:#1976D2;">Total Cubes</p>
            <p style="margin:5px 0 0 0; font-size:18px; font-weight:bold; color:#1976D2;">{total}</p>
            <p style="margin:5px 0 0 0; font-size:11px; color:#666;">{dimension}³ = {total}</p>
        </div>
        <div style="background:white; padding:10px; border:1px solid #e0e0e0; border-radius:4px;">
            <p style="margin:0; font-size:12px; font-weight:bold; color:#4CAF50;">Visible (Surface)</p>
            <p style="margin:5px 0 0 0; font-size:18px; font-weight:bold; color:#4CAF50;">{visible_cubes}</p>
            <p style="margin:5px 0 0 0; font-size:11px; color:#666;">You can see</p>
        </div>
        <div style="background:white; padding:10px; border:1px solid #e0e0e0; border-radius:4px;">
            <p style="margin:0; font-size:12px; font-weight:bold; color:#FF5722;">Hidden (Interior)</p>
            <p style="margin:5px 0 0 0; font-size:18px; font-weight:bold; color:#FF5722;">{hidden_cubes}</p>
            <p style="margin:5px 0 0 0; font-size:11px; color:#666;">Inside structure</p>
        </div>
    </div>
    
    <p style="background:white; padding:10px; border-left:4px solid #1976D2; color:#333; margin-top:10px; text-align:left; font-size:13px;">
        <strong>How to count:</strong><br>
        • Visible = cubes on the surface (you can see)<br>
        • Hidden = cubes inside (you cannot see)<br>
        • Formula for hidden in {dimension}×{dimension}×{dimension}: ({dimension}-2)³ = {hidden_cubes}
    </p>
</div>
"""
        return html

