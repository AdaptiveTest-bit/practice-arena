"""
DICE LOGIC - INTEGRATED STRATEGY
================================

Hybrid Neuro-Symbolic approach for Dice Logic

Integrates:
1. 3D spatial logic with 6-face validation
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Opposite face assumption, Rotation confusion)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class DiceLogicIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic 3d logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.DICE_LOGIC
    chapter_name = "Dice Logic"
    description = "Dice Logic with hybrid neuro-symbolic approach"
    
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
            "opposite_faces",
            "face_visibility",
            "rotation_logic",
        ])
        
        if problem_type == "opposite_faces":
            return self._generate_opposite_faces()
        elif problem_type == "face_visibility":
            return self._generate_face_visibility()
        else:  # rotation_logic
            return self._generate_rotation_logic()
    
    def _generate_opposite_faces(self) -> Question:
        """
        Opposite Faces - Find the opposite face of a die given constraints
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Standard die: opposite faces sum to 7
        # But we'll also allow custom dice for more variety
        
        dice_types = [
            {
                "type": "standard",
                "description": "Standard die where opposite faces sum to 7",
                "faces": {1: 6, 2: 5, 3: 4},
                "rule": "sum to 7"
            },
            {
                "type": "custom_a",
                "description": "Custom die with specific opposite pairs: 1-2, 3-4, 5-6",
                "faces": {1: 2, 3: 4, 5: 6},
                "rule": "given pairings"
            },
            {
                "type": "custom_b",
                "description": "Custom die with opposite pairs: 1-3, 2-6, 4-5",
                "faces": {1: 3, 2: 6, 4: 5},
                "rule": "given pairings"
            }
        ]
        
        dice_data = random.choice(dice_types)
        
        # Select a shown face and find its opposite
        shown_face = random.choice(list(dice_data["faces"].keys()))
        correct_opposite = dice_data["faces"][shown_face]
        correct_answer = str(correct_opposite)
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Arjun has a {dice_data['type'].replace('_', ' ').title()} {dice_data['description'].lower()}. If the top face shows {shown_face}, what number is on the bottom (opposite) face?",
            f"A die follows the rule: {dice_data['rule']}. You can see face {shown_face} is on top. What's on the bottom?",
            f"Priya examines a die and notes that {dice_data['rule']}. The visible top face is {shown_face}. Calculate the opposite face.",
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            f"assumed all opposites sum to 7",
            f"confused the opposite pairing rule",
            f"guessed without using the given rule",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Wrong rule application (sum to 7 if it's custom)
        if dice_data["type"] != "standard":
            wrong_answer_1 = str(7 - shown_face)
            wrong_options.append((
                wrong_answer_1,
                MisconceptionType.FORMULA_CONFUSION,
                "Applied sum-to-7 rule instead of given rule",
                f"You calculated {wrong_answer_1} using the 'sum to 7' rule, but this die uses {dice_data['rule']}. The correct answer is {correct_answer}.",
                f"Always use the specific rule given for this die. For {dice_data['type']}: {dice_data['rule']}"
            ))
        else:
            # For standard die, show wrong opposite
            wrong_answer_1 = str(random.choice([x for x in range(1, 7) if x != shown_face and x != correct_opposite]))
            wrong_options.append((
                wrong_answer_1,
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Wrong opposite face",
                f"You said {wrong_answer_1}, but on a standard die, {shown_face} is opposite to {correct_answer} (they sum to 7).",
                f"Rule: Opposite faces on a standard die always sum to 7. So {shown_face} + {correct_answer} = 7"
            ))
        
        # Misconception 2: Same number as shown
        wrong_options.append((
            str(shown_face),
            MisconceptionType.LOGICAL_DISCONNECT,
            "Gave the same face number as the shown face",
            f"The opposite face can't be the same as the visible face! The opposite of {shown_face} is {correct_answer}.",
            f"Every face has exactly one opposite face. The top and bottom can never be the same."
        ))
        
        # Misconception 3: Random wrong number
        wrong_answer_3 = str(random.choice([x for x in range(1, 7) if x != shown_face and x != correct_opposite]))
        wrong_options.append((
            wrong_answer_3,
            MisconceptionType.INCOMPLETE_REASONING,
            "Guessed without checking the rule",
            f"You picked {wrong_answer_3}, but by the {dice_data['rule']}, the opposite of {shown_face} is {correct_answer}.",
            f"Use the specific rule: {dice_data['rule']} for this die."
        ))
        
        random.shuffle(wrong_options)
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
            f"Die Type: {dice_data['type'].replace('_', ' ').title()}",
            f"Rule: {dice_data['rule']}",
            f"Shown Face (top): {shown_face}",
            f"Using the rule, find opposite pair: {shown_face} ↔ {correct_answer}",
            f"Opposite Face (bottom): {correct_answer}",
            f"Answer: {correct_answer}"
        ]
        
        visual_diagram = self._render_opposite_faces_diagram(dice_data, shown_face, correct_opposite)
        
        hints = [
            f"Hint 1: This die uses the rule: {dice_data['rule']}",
            f"Hint 2: The visible top face is {shown_face}",
            f"Hint 3: Look up {shown_face} in the opposite pairs",
            f"Hint 4: The opposite of {shown_face} is {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Finding Opposite Faces on Dice",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Always check the specific rule for this die!",
            data_representation=f"Die with rule: {dice_data['rule']} | Shown face: {shown_face}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s dice logic: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_face_visibility(self) -> Question:
        """
        Face Visibility - Count visible faces from a specific viewpoint
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Different scenarios of dice/cube arrangements
        visibility_scenarios = [
            {
                "arrangement": "single_die",
                "description": "A single die sitting on a table",
                "visible_faces": 5,
                "explanation": "You see: top + 4 sides. Bottom is hidden by table.",
                "faces_list": "top, front, back, left, right"
            },
            {
                "arrangement": "stacked_2",
                "description": "Two dice stacked vertically",
                "visible_faces": 10,
                "explanation": "Top die: 5 visible (top + 4 sides). Bottom die: 5 visible (4 sides + 1 side of stacking = 4 visible sides). Total = 5 + 4 = 9",
                "faces_list": "top die (5) + bottom die (4) = 9 faces"
            },
            {
                "arrangement": "row_3",
                "description": "Three dice in a row on a table",
                "visible_faces": 13,
                "explanation": "Left die: 5 visible. Middle die: 4 visible (top + 2 sides). Right die: 5 visible. Wait, middle die has 2 neighbors = 3 hidden faces = 3 visible. Total = 5 + 3 + 5 = 13",
                "faces_list": "left (5) + middle (3) + right (5) = 13 faces"
            }
        ]
        
        scenario_data = random.choice(visibility_scenarios)
        correct_answer = str(scenario_data["visible_faces"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Priya has {scenario_data['description']}. How many faces can she see in total? Count all visible faces (top and sides, but not bottom/hidden faces).",
            f"A game board shows {scenario_data['description']}. How many cube faces are visible from above the table?",
            f"Dev is counting the visible faces on {scenario_data['description']}. Can you count them? (Remember: hidden faces on table or between cubes don't count!)",
        ])
        
        character = random.choice(["Priya", "Dev", "Arjun", "Sneha"])
        misconception_hook = random.choice([
            "counted the hidden faces too",
            "forgot to subtract hidden faces",
            "counted each die as having 6 visible faces",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: All faces visible (6 per die)
        if "2" in scenario_data["arrangement"]:
            total_faces = 12  # 2 dice * 6 faces
        elif "3" in scenario_data["arrangement"]:
            total_faces = 18  # 3 dice * 6 faces
        else:
            total_faces = 6
        
        wrong_options.append((
            str(total_faces),
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Counted all faces as visible (forgot hidden faces)",
            f"You counted {total_faces} (all faces), but some faces are hidden! The {scenario_data['arrangement'].replace('_', ' ')} has {correct_answer} visible faces.",
            f"Hidden faces: {scenario_data['explanation']}"
        ))
        
        # Misconception 2: Wrong calculation
        wrong_visible = str(scenario_data["visible_faces"] - random.randint(1, 3))
        wrong_options.append((
            wrong_visible,
            MisconceptionType.LOGICAL_DISCONNECT,
            "Miscounted the visible faces",
            f"You calculated {wrong_visible}, but if you count carefully: {scenario_data['explanation']}",
            f"Total visible faces = {correct_answer}. Faces: {scenario_data['faces_list']}"
        ))
        
        # Misconception 3: Included hidden faces
        wrong_visible_3 = str(scenario_data["visible_faces"] + random.randint(1, 2))
        wrong_options.append((
            wrong_visible_3,
            MisconceptionType.INCOMPLETE_REASONING,
            "Included hidden faces in the count",
            f"You said {wrong_visible_3}, but that includes hidden faces on the table or between cubes. Visible faces only = {correct_answer}.",
            f"Only count faces you can actually SEE. Hidden faces (on table, between cubes) don't count!"
        ))
        
        random.shuffle(wrong_options)
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
            f"Arrangement: {scenario_data['description']}",
            f"Each die/cube has 6 faces total",
            f"Faces: {scenario_data['faces_list']}",
            f"Hidden faces (on table or between cubes): determined by position",
            f"Calculation: {scenario_data['explanation']}",
            f"Total Visible Faces: {correct_answer}"
        ]
        
        visual_diagram = self._render_face_visibility_diagram(scenario_data)
        
        hints = [
            f"Hint 1: You're looking at {scenario_data['description']}",
            f"Hint 2: Each die has 6 faces: top, bottom, front, back, left, right",
            f"Hint 3: Some faces are hidden (bottom on table or between stacked/adjacent dice)",
            f"Hint 4: Count only the faces you can SEE. Total visible = {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Counting Visible Faces on Dice Arrangements",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Count only VISIBLE faces!",
            data_representation=f"{scenario_data['arrangement'].replace('_', ' ').title()} arrangement with visible faces: {scenario_data['faces_list']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s visibility count: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_rotation_logic(self) -> Question:
        """
        Rotation Logic - Predict which face appears after rotating a die
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Define rotation scenarios (rolling a die)
        rotation_scenarios = [
            {
                "type": "roll_forward",
                "description": "A die shows 1 on top. Roll it forward once.",
                "initial_top": 1,
                "initial_front": 2,
                "rotation": "forward",
                "final_top": 2,
                "explanation": "Rolling forward: top becomes front, front becomes bottom, bottom becomes back, back becomes top. So 1→front, 2→bottom, (opposite of 1)→back, (opposite of 2)→top"
            },
            {
                "type": "roll_right",
                "description": "A die shows 3 on top and 2 facing you. Roll it to the right once.",
                "initial_top": 3,
                "initial_front": 2,
                "rotation": "right",
                "final_top": 4,
                "explanation": "Rolling right: top→left, left→bottom, bottom→right, right→top. So 3→left, left_face→bottom, right_face→top"
            },
            {
                "type": "roll_left",
                "description": "A die shows 5 on top and 1 facing you. Roll it to the left once.",
                "initial_top": 5,
                "initial_front": 1,
                "rotation": "left",
                "final_top": 2,
                "explanation": "Rolling left is opposite of rolling right: top→right, right→bottom, bottom→left, left→top"
            }
        ]
        
        scenario_data = random.choice(rotation_scenarios)
        correct_answer = str(scenario_data["final_top"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Arjun has a standard die with {scenario_data['initial_top']} showing on top. {scenario_data['description']} What number is now on top?",
            f"A {scenario_data['rotation']} roll of a die: started with {scenario_data['initial_top']} on top. After the roll, which face is now visible on top?",
            f"Dev performs a {scenario_data['rotation']} rotation of a die. Initial: {scenario_data['initial_top']} on top. Final: ? on top.",
        ])
        
        character = random.choice(["Arjun", "Dev", "Priya", "Sneha"])
        misconception_hook = random.choice([
            "didn't properly track the rotation",
            "confused the rotation direction",
            "guessed without visualizing the roll",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Didn't rotate (same answer)
        wrong_options.append((
            str(scenario_data["initial_top"]),
            MisconceptionType.LOGICAL_DISCONNECT,
            "Said the same face (didn't account for rotation)",
            f"You said {scenario_data['initial_top']}, but after rolling {scenario_data['rotation']}, the die rotates and a different face comes to the top!",
            f"After {scenario_data['rotation']} rotation: {scenario_data['explanation']}"
        ))
        
        # Misconception 2: Wrong rotation direction
        if scenario_data["rotation"] == "forward":
            wrong_rotation = 3  # Random wrong answer
        elif scenario_data["rotation"] == "right":
            wrong_rotation = 2
        else:
            wrong_rotation = 4
        wrong_options.append((
            str(wrong_rotation),
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Rotated in wrong direction or miscalculated",
            f"You calculated {wrong_rotation}, but rolling {scenario_data['rotation']} from {scenario_data['initial_top']} gives {correct_answer}.",
            f"Visualize: {scenario_data['explanation']}"
        ))
        
        # Misconception 3: Confused rotation logic
        wrong_rotation_3 = str((int(correct_answer) % 6) + 1) if correct_answer != "6" else "1"
        if wrong_rotation_3 == correct_answer:
            wrong_rotation_3 = str((int(correct_answer) % 5) + 2)
        wrong_options.append((
            wrong_rotation_3,
            MisconceptionType.INCOMPLETE_REASONING,
            "Used wrong transformation rule",
            f"You gave {wrong_rotation_3}, but that's applying the wrong rotation rule. The correct answer is {correct_answer}.",
            f"For {scenario_data['rotation']} rotation: {scenario_data['explanation']}"
        ))
        
        random.shuffle(wrong_options)
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
            f"Initial Die Position: {scenario_data['initial_top']} on top",
            f"Rotation Type: {scenario_data['rotation'].title()} roll",
            f"Rotation Sequence:",
            f"  - {scenario_data['explanation']}",
            f"Step-by-step face tracking through rotation",
            f"Final Top Face: {correct_answer}",
            f"Answer: {correct_answer}"
        ]
        
        visual_diagram = self._render_rotation_logic_diagram(scenario_data)
        
        hints = [
            f"Hint 1: Die starts with {scenario_data['initial_top']} on top",
            f"Hint 2: The die rolls {scenario_data['rotation']}",
            f"Hint 3: Track where the faces move during rotation",
            f"Hint 4: After {scenario_data['rotation']} rotation, {correct_answer} is on top"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Dice Rotation and Face Tracking",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Mentally track each face!",
            data_representation=f"Die rotation: {scenario_data['rotation'].title()} from initial top {scenario_data['initial_top']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s dice rotation challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question


    # ======================================
    # RENDERING HELPER METHODS
    # ======================================
    
    def _render_opposite_faces_diagram(self, dice_data: dict, shown_face: int, opposite_face: int) -> dict:
        """Render a diagram showing the die with marked opposite faces"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Opposite Faces Diagram</h3>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; align-items: center;">
        """
        
        # Draw isometric die view
        html += """
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Visible Die View</p>
                    <svg width="220" height="200" style="border: 1px solid #ccc; background: white;">
                        <!-- Top face (shown face) -->
                        <polygon points="60,50 150,50 180,70 90,70" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
        """
        
        html += f'<text x="115" y="65" font-size="16" text-anchor="middle" font-weight="bold" fill="#2563eb">{shown_face}</text>'
        
        html += f"""
                        <!-- Front face -->
                        <polygon points="60,70 150,70 150,150 60,150" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        <text x="105" y="115" font-size="14" text-anchor="middle">Front</text>
                        
                        <!-- Right face -->
                        <polygon points="150,70 180,70 180,150 150,150" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
                        <text x="165" y="115" font-size="14" text-anchor="middle">Side</text>
                        
                        <!-- Label for hidden bottom face -->
                        <text x="105" y="180" font-size="12" text-anchor="middle" font-weight="bold">Bottom: {opposite_face}</text>
                        <text x="105" y="195" font-size="10" text-anchor="middle" fill="#666">(Hidden - Opposite)</text>
                    </svg>
                </div>
        """
        
        # Show the rule and calculation
        html += f"""
                <div style="padding: 15px; border-radius: 4px; border-left: 4px solid #3b82f6; background: white; min-width: 280px;">
                    <p style="margin: 0 0 10px 0; font-weight: bold;">Rule: {dice_data['rule']}</p>
                    <table style="width: 100%; text-align: left; font-size: 13px;">
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 8px; padding-left: 0;"><strong>Face</strong></td>
                            <td style="padding: 8px;"><strong>Opposite Face</strong></td>
                        </tr>
        """
        
        for face, opposite in sorted(dice_data["faces"].items()):
            highlight = "background: #dbeafe;" if face == shown_face else ""
            html += f"""
                        <tr style="{highlight}border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 8px; padding-left: 0; font-weight: bold;">{face}</td>
                            <td style="padding: 8px;">{opposite}</td>
                        </tr>
            """
        
        html += f"""
                    </table>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #e5e7eb;">
                        <p style="margin: 0; font-weight: bold;">Given: Top face = {shown_face}</p>
                        <p style="margin: 5px 0 0 0; color: #059669; font-weight: bold; font-size: 14px;">Answer: Bottom face = {opposite_face}</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_face_visibility_diagram(self, scenario_data: dict) -> dict:
        """Render face visibility count diagram for different arrangements"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Counting Visible Faces</h3>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
        """
        
        # Visual representation
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Arrangement: {scenario_data['arrangement'].replace('_', ' ').title()}</p>
                    <svg width="200" height="180" style="border: 1px solid #ccc; background: white;">
        """
        
        if "single" in scenario_data["arrangement"]:
            html += """
                        <!-- Single die -->
                        <polygon points="50,50 130,50 160,75 80,75" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <polygon points="50,75 130,75 130,155 50,155" fill="#e0e7ff" stroke="#2563eb" stroke-width="2"/>
                        <polygon points="130,75 160,75 160,155 130,155" fill="#c7d2fe" stroke="#2563eb" stroke-width="2"/>
                        <text x="90" y="120" font-size="12" text-anchor="middle" font-weight="bold">5 Visible</text>
                        <text x="175" y="100" font-size="10" fill="#666">(Bottom hidden)</text>
            """
        elif "2" in scenario_data["arrangement"]:
            html += """
                        <!-- Two stacked dice -->
                        <polygon points="50,40 120,40 145,55 75,55" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <polygon points="50,55 120,55 120,115 50,115" fill="#e0e7ff" stroke="#2563eb" stroke-width="2"/>
                        <polygon points="120,55 145,55 145,115 120,115" fill="#c7d2fe" stroke="#2563eb" stroke-width="2"/>
                        
                        <polygon points="55,115 125,115 150,130 80,130" fill="#fed7aa" stroke="#f59e0b" stroke-width="2"/>
                        <polygon points="55,130 125,130 125,190 55,190" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
                        <polygon points="125,130 150,130 150,190 125,190" fill="#fce7b6" stroke="#f59e0b" stroke-width="2"/>
                        
                        <text x="85" y="85" font-size="11" text-anchor="middle" font-weight="bold">Top: 5</text>
                        <text x="85" y="160" font-size="11" text-anchor="middle" font-weight="bold">Bottom: 4</text>
                        <text x="85" y="175" font-size="10" fill="#666">Total: 9</text>
            """
        else:
            html += """
                        <!-- Three in a row -->
                        <rect x="30" y="60" width="40" height="40" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="50" y="85" font-size="10" text-anchor="middle" font-weight="bold">Left</text>
                        
                        <rect x="80" y="60" width="40" height="40" fill="#e0e7ff" stroke="#2563eb" stroke-width="2"/>
                        <text x="100" y="85" font-size="10" text-anchor="middle" font-weight="bold">Mid</text>
                        
                        <rect x="130" y="60" width="40" height="40" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="150" y="85" font-size="10" text-anchor="middle" font-weight="bold">Right</text>
                        
                        <text x="100" y="120" font-size="11" text-anchor="middle" font-weight="bold">5 + 3 + 5 = 13</text>
                        <text x="100" y="135" font-size="10" fill="#666">(Middle has 2 hidden sides)</text>
            """
        
        html += f"""
                    </svg>
                </div>
        """
        
        # Breakdown table
        html += f"""
                <div style="padding: 15px; border-radius: 4px; border-left: 4px solid #3b82f6; background: white; min-width: 280px;">
                    <p style="margin: 0 0 10px 0; font-weight: bold;">Visibility Breakdown</p>
                    <p style="margin: 5px 0; font-size: 13px;">{scenario_data['explanation']}</p>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #e5e7eb;">
                        <p style="margin: 0; font-weight: bold;">Faces: {scenario_data['faces_list']}</p>
                        <p style="margin: 8px 0 0 0; color: #059669; font-weight: bold; font-size: 14px;">Total Visible = {scenario_data['visible_faces']}</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_rotation_logic_diagram(self, scenario_data: dict) -> dict:
        """Render dice rotation transformation visualization"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Dice Rotation Sequence</h3>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; align-items: center;">
        """
        
        # Show before and after
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Before Rotation</p>
                    <svg width="180" height="160" style="border: 1px solid #ccc; background: white;">
                        <polygon points="40,40 120,40 150,60 70,60" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="80" y="55" font-size="16" text-anchor="middle" font-weight="bold" fill="#2563eb">{scenario_data['initial_top']}</text>
                        
                        <polygon points="40,60 120,60 120,140 40,140" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        <text x="80" y="105" font-size="14" text-anchor="middle" font-weight="bold">{scenario_data['initial_front']}</text>
                        
                        <polygon points="120,60 150,60 150,140 120,140" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
                        
                        <text x="80" y="155" font-size="10" text-anchor="middle" fill="#666">Top: {scenario_data['initial_top']}</text>
                    </svg>
                </div>
        """
        
        # Rotation arrow
        html += f"""
                <div style="display: flex; align-items: center; justify-content: center; padding: 20px;">
                    <p style="font-size: 24px; font-weight: bold; color: #3b82f6;">
                        Roll {scenario_data['rotation'].title()} →
                    </p>
                </div>
        """
        
        # After rotation
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">After Rotation</p>
                    <svg width="180" height="160" style="border: 1px solid #ccc; background: white;">
                        <polygon points="40,40 120,40 150,60 70,60" fill="#dcfce7" stroke="#10b981" stroke-width="2"/>
                        <text x="80" y="55" font-size="16" text-anchor="middle" font-weight="bold" fill="#10b981">{scenario_data['final_top']}</text>
                        
                        <polygon points="40,60 120,60 120,140 40,140" fill="#f5f3ff" stroke="#8b5cf6" stroke-width="2"/>
                        <text x="80" y="105" font-size="14" text-anchor="middle" font-weight="bold">(New)</text>
                        
                        <polygon points="120,60 150,60 150,140 120,140" fill="#fef2f2" stroke="#ef4444" stroke-width="2"/>
                        
                        <text x="80" y="155" font-size="10" text-anchor="middle" fill="#666">Top: {scenario_data['final_top']}</text>
                    </svg>
                </div>
            </div>
        """
        
        # Explanation
        html += f"""
            <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 4px; border-left: 4px solid #3b82f6;">
                <p style="margin: 0 0 8px 0; font-weight: bold;">Rotation Process:</p>
                <p style="margin: 5px 0; font-size: 13px;">{scenario_data['explanation']}</p>
                <p style="margin: 8px 0 0 0; color: #059669; font-weight: bold;">Result: Face {scenario_data['final_top']} is now on top!</p>
            </div>
        </div>
        """
        
        return {"html": html}

    # ==================== SVG RENDERING METHODS ====================
    
    def _render_dice_diagram_svg(self, visible_faces: dict = None) -> str:
        """Render SVG showing dice faces in 3D isometric view"""
        html = '''<div style="border:2px solid #FF5722; border-radius:8px; padding:15px; background:#ffebee; text-align:center;">
            <h4 style="color:#C62828;">Dice Faces (3D View)</h4>
            <svg width="300" height="280" style="border:1px solid #ccc; background:white;">
                <!-- Front face (blue) -->
                <polygon points="50,100 150,100 150,200 50,200" fill="#BBDEFB" stroke="#1976D2" stroke-width="2"/>
                <text x="100" y="155" text-anchor="middle" font-size="14" font-weight="bold" fill="#1565C0">Front</text>
                
                <!-- Top face (light blue) -->
                <polygon points="50,100 120,50 220,50 150,100" fill="#E3F2FD" stroke="#1976D2" stroke-width="2"/>
                <text x="135" y="75" text-anchor="middle" font-size="12" font-weight="bold" fill="#1565C0">Top</text>
                
                <!-- Right face (green) -->
                <polygon points="150,100 220,50 220,150 150,200" fill="#C8E6C9" stroke="#4CAF50" stroke-width="2"/>
                <text x="185" y="130" text-anchor="middle" font-size="12" font-weight="bold" fill="#2E7D32">Right</text>
                
                <!-- Labels -->
                <text x="150" y="250" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">Standard Dice: Opposites Sum to 7</text>
            </svg>
            <p style="padding:10px; color:#333; font-size:13px;">
                <strong>Dice Rules:</strong> 1↔6, 2↔5, 3↔4 (opposite faces sum to 7)
            </p>
        </div>'''
        return html

