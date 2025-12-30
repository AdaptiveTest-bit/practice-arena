"""
NETS - INTEGRATED STRATEGY
==========================

Hybrid Neuro-Symbolic approach for Nets

Integrates:
1. 3D visualization with folding logic
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Net connectivity error, Orientation mistake)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class NetsIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic 3d logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.NETS
    chapter_name = "Nets"
    description = "Nets with hybrid neuro-symbolic approach"
    
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
            "net_validation",
            "fold_prediction",
            "matching_nets",
        ])
        
        if problem_type == "net_validation":
            return self._generate_net_validation()
        elif problem_type == "fold_prediction":
            return self._generate_fold_prediction()
        else:  # matching_nets
            return self._generate_matching_nets()
    
    def _generate_net_validation(self) -> Question:
        """
        Net Validation - Determine if a 2D net can fold into a valid 3D cube
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Define valid and invalid nets
        valid_nets = [
            {
                "name": "T-Shape",
                "description": "4 in a row with 1 on top and 1 on bottom",
                "is_valid": True,
                "reason": "Forms a cube with correct connectivity"
            },
            {
                "name": "Cross-Shape",
                "description": "One center square with 4 adjacent squares (up, down, left, right) and 1 more attached",
                "is_valid": True,
                "reason": "Folds into a cube correctly"
            },
            {
                "name": "Straight Line",
                "description": "All 6 squares in a straight line",
                "is_valid": True,
                "reason": "Can fold to form a cube"
            }
        ]
        
        invalid_nets = [
            {
                "name": "2x3 Rectangle",
                "description": "6 squares arranged in a 2×3 grid",
                "is_valid": False,
                "reason": "Overlaps when folded - two faces would occupy same space"
            },
            {
                "name": "Square with 2 Gaps",
                "description": "Four corner squares missing from a 4×4 arrangement",
                "is_valid": False,
                "reason": "Not enough faces (need 6, have 4)"
            },
            {
                "name": "Pentagon with 1",
                "description": "5 connected squares plus 1 isolated square",
                "is_valid": False,
                "reason": "Has disconnected square - can't form single cube"
            }
        ]
        
        # Select a net
        if random.choice([True, False]):
            selected_net = random.choice(valid_nets)
        else:
            selected_net = random.choice(invalid_nets)
        
        correct_answer = "Yes" if selected_net["is_valid"] else "No"
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A packaging company needs to check if a design pattern can fold into a cube-shaped box. They show you a {selected_net['name'].lower()} pattern of 6 squares. Can this net fold into a cube?",
            f"Arjun is creating a dice from paper. He draws a {selected_net['name'].lower()} pattern. His teacher asks: 'Will this fold into a perfect cube?' What do you think?",
            f"A toy manufacturer has a {selected_net['name'].lower()} template. When folded, should it create a valid cube without overlapping faces?",
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "didn't mentally fold the net",
            "guessed without checking connectivity",
            "counted squares instead of visualizing folding",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Opposite answer
        opposite_answer = "No" if correct_answer == "Yes" else "Yes"
        wrong_options.append((
            opposite_answer,
            MisconceptionType.LOGICAL_DISCONNECT,
            "Opposite of correct answer",
            f"You said '{opposite_answer}', but '{correct_answer}' is correct. {selected_net['reason']}",
            f"To validate a net: Check if all 6 faces are present, connected, and don't overlap when folded."
        ))
        
        # Misconception 2: Visual confusion (surface area)
        wrong_options.append((
            str(len(selected_net['description'].split())),  # Wrong metric
            MisconceptionType.FORMULA_CONFUSION,
            "Counted description words instead of checking foldability",
            f"You might have counted words instead of analyzing the net's geometry.",
            f"A valid net must have exactly 6 connected squares with no overlaps when folded into a cube."
        ))
        
        # Misconception 3: Connectivity confusion
        wrong_options.append((
            "Maybe" if correct_answer != "Maybe" else "No",
            MisconceptionType.INCOMPLETE_REASONING,
            "Uncertain - didn't fully visualize the folding",
            f"A net either folds into a cube or it doesn't. There's no 'maybe' - you must check all faces.",
            f"Mentally fold each face: Does it overlap? Are all 6 present? Are they all connected?"
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
            f"Net Pattern: {selected_net['name']}",
            f"Description: {selected_net['description']}",
            f"Check: Does it have 6 faces? Yes" if selected_net['is_valid'] else f"Check: Does it have 6 faces? Yes, but...",
            f"Check: Are they all connected? {'Yes' if selected_net['is_valid'] else 'No - Disconnected!'}",
            f"Check: Will faces overlap when folded? {'No - Valid net!' if selected_net['is_valid'] else 'Yes - Invalid!'}",
            f"Answer: {correct_answer} - {selected_net['reason']}"
        ]
        
        visual_diagram = self._render_net_diagram(selected_net['name'], selected_net['is_valid'])
        
        hints = [
            f"Hint 1: A valid net must have exactly 6 squares (for 6 faces of a cube)",
            f"Hint 2: All squares must be connected (touching edge-to-edge)",
            f"Hint 3: When folded, no two faces should overlap or go outside the cube",
            f"Hint 4: Mentally fold this {selected_net['name'].lower()} - does it work? {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Net Validation and Folding",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Always check: 6 faces, connected, no overlaps!",
            data_representation=f"{selected_net['name']} net pattern with {len([c for c in selected_net['description'] if c.isdigit()])} squares",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s net validation: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_fold_prediction(self) -> Question:
        """
        Fold Prediction - Predict what 3D shape results from folding a 2D net
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Net folding scenarios with orientation
        fold_scenarios = [
            {
                "description": "A net with a marked face on top and a different marked face on bottom",
                "folding_type": "opposite_faces",
                "answer": "opposite",
                "explanation": "Top and bottom faces become opposite sides of the cube"
            },
            {
                "description": "A net with adjacent marked faces in the pattern",
                "folding_type": "adjacent_faces",
                "answer": "adjacent",
                "explanation": "Connected faces in the net remain connected (but perpendicular) in the cube"
            },
            {
                "description": "A net with faces separated by 2 intermediate squares",
                "folding_type": "separated_faces",
                "answer": "adjacent_or_opposite",
                "explanation": "Depends on exact positions - could be adjacent or opposite"
            }
        ]
        
        scenario_data = random.choice(fold_scenarios)
        
        # Surface markings to track
        marked_faces = random.choice([
            {"face1": "A (top)", "face2": "B (bottom)", "relation": "opposite"},
            {"face1": "X (left)", "face2": "Y (right)", "relation": "opposite"},
            {"face1": "P (connected left)", "face2": "Q (connected down)", "relation": "adjacent"},
        ])
        
        correct_answer = marked_faces["relation"]
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Priya is folding a paper net with two marked faces. When she folds it completely, face {marked_faces['face1']} and face {marked_faces['face2']} will be on which positions of the cube? Are they opposite, adjacent, or can they meet?",
            f"A toy company marks two corners of a cube net before folding. When folded into a cube, these marked points will be: {correct_answer}. What should the workers expect?",
            f"Dev has a net with two colored squares marked. After folding it into a cube, what will be the relationship between these two faces - will they be on opposite sides, next to each other, or somewhere else?",
        ])
        
        character = random.choice(["Priya", "Dev", "Arjun", "Sneha"])
        misconception_hook = random.choice([
            "didn't rotate the net mentally while folding",
            "lost track of which face goes where",
            "confused adjacent with opposite",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Opposite of correct relationship
        opposite_relationship = "adjacent" if correct_answer == "opposite" else "opposite"
        wrong_options.append((
            opposite_relationship,
            MisconceptionType.LOGICAL_DISCONNECT,
            f"Said '{opposite_relationship}' instead of '{correct_answer}'",
            f"You confused the spatial relationship. When you fold this net, the faces are {correct_answer}, not {opposite_relationship}.",
            f"Trace each face while folding: {marked_faces['face1']} and {marked_faces['face2']} will be {correct_answer} in the cube."
        ))
        
        # Misconception 2: Incorrect distance calculation
        wrong_distance = "2 faces apart"
        wrong_options.append((
            wrong_distance,
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Counted distance in net instead of 3D position",
            f"You might have counted faces in the net layout, but that's not the same as 3D position in the folded cube.",
            f"The 3D relationship after folding is: {correct_answer}"
        ))
        
        # Misconception 3: Missing orientation
        wrong_orientation = "undefined" if correct_answer != "undefined" else "adjacent"
        wrong_options.append((
            wrong_orientation,
            MisconceptionType.INCOMPLETE_REASONING,
            "Couldn't determine the relationship",
            f"The relationship can be determined by careful mental folding. It's definitely {correct_answer}.",
            f"Use the net pattern: Face positions follow consistent folding rules. These faces are {correct_answer}."
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
            f"Marked Faces: {marked_faces['face1']} and {marked_faces['face2']}",
            f"Net Pattern Type: {scenario_data['folding_type']}",
            f"Step 1: Trace face 1 position in the net",
            f"Step 2: Trace face 2 position in the net",
            f"Step 3: Mentally fold - how do they move relative to each other?",
            f"Answer: {correct_answer} - {scenario_data['explanation']}"
        ]
        
        visual_diagram = self._render_fold_prediction_diagram(marked_faces, scenario_data)
        
        hints = [
            f"Hint 1: In the net, mark where faces {marked_faces['face1']} and {marked_faces['face2']} are located",
            f"Hint 2: Start folding from one face and track the other's position",
            f"Hint 3: Remember: opposite faces are separated by exactly one face layer",
            f"Hint 4: When fully folded, these faces will be {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Fold Prediction - Face Relationships",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Mentally fold step-by-step!",
            data_representation=f"Net with marked faces: {marked_faces['face1']} and {marked_faces['face2']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s fold prediction: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_matching_nets(self) -> Question:
        """
        Matching Nets - Match a 3D cube to its corresponding 2D net
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Define cube patterns and their corresponding nets
        cube_patterns = [
            {
                "id": "A",
                "description": "Cube with numbered faces 1-6 in a specific arrangement",
                "correct_net": "T-shaped with 1 on top, 6 on bottom, 2-3-4-5 in a row",
                "faces": {"top": 1, "bottom": 6, "sides": "2,3,4,5"}
            },
            {
                "id": "B",
                "description": "Cube with colored faces: Red opposite to Green, Blue opposite to Yellow",
                "correct_net": "Cross pattern with Red-Blue-Green in a column, Yellow-White on sides",
                "faces": {"opposite_1": "Red-Green", "opposite_2": "Blue-Yellow"}
            },
            {
                "id": "C",
                "description": "Cube with pattern faces: Star, Circle, Diamond, Heart, Line, Dot",
                "correct_net": "Straight line net with specific face ordering",
                "faces": {"pattern": "Star-Circle-Diamond-Heart-Line-Dot"}
            }
        ]
        
        cube_data = random.choice(cube_patterns)
        correct_answer = f"Net {cube_data['id']}"
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A packaging designer has drawn a 3D cube pattern and several 2D nets on paper. The cube shows faces with {cube_data['faces']}. Which net will fold into this exact cube without rotating?",
            f"Arjun's teacher shows him a 3D cube with specific markings and asks him to find the matching net from several options. The cube has {cube_data['description']}. Which net is correct?",
            f"A toy factory needs to match 3D cubes to their net templates. Given a cube showing {cube_data['description']}, identify which 2D net pattern will produce it.",
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "matched a similar-looking but incorrectly oriented net",
            "confused which faces are opposite",
            "rotated the net mentally but got the orientation wrong",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Similar net with wrong face arrangement
        wrong_net_1 = f"Net {chr(ord(cube_data['id']) + 1)}" if cube_data['id'] != 'C' else "Net A"
        wrong_options.append((
            wrong_net_1,
            MisconceptionType.LOGICAL_DISCONNECT,
            f"Chose {wrong_net_1} which looks similar but has wrong face arrangement",
            f"You picked {wrong_net_1}, but that has {cube_data['description']} arranged differently. The correct net is {correct_answer}.",
            f"Check: In the net, are opposite faces in the correct positions? {correct_answer} has them right!"
        ))
        
        # Misconception 2: Rotated net (flipped orientation)
        wrong_net_2 = f"Net {chr(ord(cube_data['id']) - 1) if cube_data['id'] != 'A' else 'C'}"
        wrong_options.append((
            wrong_net_2,
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Chose {wrong_net_2} which is a rotation of the correct net",
            f"That net is a 180° rotation of the correct one. When you rotate {wrong_net_2}, faces don't align properly. {correct_answer} is correct.",
            f"Always check: Are the adjacent faces in the net adjacent in the 3D cube? {correct_answer} satisfies this!"
        ))
        
        # Misconception 3: Mirror image confusion
        wrong_net_3 = f"Net X"
        wrong_options.append((
            wrong_net_3,
            MisconceptionType.INCOMPLETE_REASONING,
            "Chose a mirror image of the correct net",
            f"That's the mirror image of the correct net - it would create a cube with reversed face positions. {correct_answer} is the accurate match.",
            f"Don't just use visuals - trace each face systematically to confirm the match is correct."
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
            f"3D Cube Shown: {cube_data['description']}",
            f"Key Face Relationships: {cube_data['faces']}",
            f"Step 1: Identify opposite faces in the cube",
            f"Step 2: Check each net - are opposite faces positioned correctly?",
            f"Step 3: Verify adjacent faces match in both 2D and 3D",
            f"Answer: {correct_answer} - All face relationships match perfectly!"
        ]
        
        visual_diagram = self._render_matching_nets_diagram(cube_data, all_options)
        
        hints = [
            f"Hint 1: The cube has {cube_data['description']}",
            f"Hint 2: Opposite faces in the cube must be in valid opposite positions in the net",
            f"Hint 3: Adjacent faces in the cube must connect properly when the net is folded",
            f"Hint 4: The correct answer is {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Matching 3D Cubes to 2D Nets",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Check all face relationships!",
            data_representation=f"3D cube with faces: {cube_data['description']} matching to net options",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s net matching challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question


    # ======================================
    # RENDERING HELPER METHODS
    # ======================================
    
    def _render_net_diagram(self, net_name: str, is_valid: bool) -> dict:
        """Render a 2D net diagram and indicate if it's valid"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Net Diagram: {net_name}</h3>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; align-items: center;">
        """
        
        # Draw the net based on type
        if net_name == "T-Shape":
            html += """
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">T-Shape Net</p>
                    <svg width="200" height="220" style="border: 1px solid #ccc; background: white;">
                        <!-- Top square -->
                        <rect x="75" y="20" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="100" y="50" font-size="12" text-anchor="middle" font-weight="bold">1</text>
                        
                        <!-- Row of 4 squares -->
                        <rect x="25" y="70" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="50" y="100" font-size="12" text-anchor="middle" font-weight="bold">2</text>
                        
                        <rect x="75" y="70" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="100" y="100" font-size="12" text-anchor="middle" font-weight="bold">3</text>
                        
                        <rect x="125" y="70" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="150" y="100" font-size="12" text-anchor="middle" font-weight="bold">4</text>
                        
                        <rect x="175" y="70" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="200" y="100" font-size="12" text-anchor="middle" font-weight="bold">5</text>
                        
                        <!-- Bottom square -->
                        <rect x="75" y="120" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="100" y="150" font-size="12" text-anchor="middle" font-weight="bold">6</text>
                        
                        <!-- Label -->
                        <text x="100" y="200" font-size="11" text-anchor="middle" fill="#666">6 connected squares</text>
                    </svg>
                </div>
            """
        else:
            html += """
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Cross-Shape Net</p>
                    <svg width="200" height="200" style="border: 1px solid #ccc; background: white;">
                        <!-- Center square -->
                        <rect x="75" y="75" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="100" y="105" font-size="12" text-anchor="middle" font-weight="bold">C</text>
                        
                        <!-- Top -->
                        <rect x="75" y="25" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        
                        <!-- Bottom -->
                        <rect x="75" y="125" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        
                        <!-- Left -->
                        <rect x="25" y="75" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        
                        <!-- Right -->
                        <rect x="125" y="75" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        
                        <!-- Extra square -->
                        <rect x="125" y="25" width="50" height="50" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        
                        <text x="100" y="170" font-size="11" text-anchor="middle" fill="#666">6 squares total</text>
                    </svg>
                </div>
            """
        
        # Validation result
        html += f"""
                <div style="padding: 15px; border-radius: 4px; border-left: 4px solid {'#10b981' if is_valid else '#dc2626'}; background: {'#ecfdf5' if is_valid else '#fef2f2'}; min-width: 250px;">
                    <p style="margin: 0 0 8px 0; font-weight: bold; color: {'#059669' if is_valid else '#991b1b'};">
                        {'✓ VALID NET' if is_valid else '✗ INVALID NET'}
                    </p>
                    <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px;">
                        <li>Has 6 connected squares: {'Yes' if is_valid else 'No/Disconnected'}</li>
                        <li>No overlaps when folded: {'Yes' if is_valid else 'Overlaps occur'}</li>
                        <li>Forms a cube: {'Yes' if is_valid else 'No'}</li>
                    </ul>
                    <p style="margin: 8px 0 0 0; font-size: 12px; color: {'#059669' if is_valid else '#991b1b'};">
                        {'This net successfully folds into a cube!' if is_valid else 'This net cannot fold into a cube without errors.'}
                    </p>
                </div>
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_fold_prediction_diagram(self, marked_faces: dict, scenario_data: dict) -> dict:
        """Render fold prediction visualization with marked faces"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Fold Prediction: Marked Face Relationship</h3>
            <div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; align-items: center;">
        """
        
        # Show the net with marked positions
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">2D Net with Marked Faces</p>
                    <svg width="200" height="180" style="border: 1px solid #ccc; background: white;">
                        <!-- Simple T-net representation -->
                        <rect x="75" y="10" width="50" height="50" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="100" y="40" font-size="11" text-anchor="middle" font-weight="bold">{marked_faces['face1'][:1]}</text>
                        
                        <rect x="25" y="60" width="50" height="50" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        <text x="50" y="90" font-size="11" text-anchor="middle" font-weight="bold">1</text>
                        
                        <rect x="75" y="60" width="50" height="50" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        <text x="100" y="90" font-size="11" text-anchor="middle" font-weight="bold">2</text>
                        
                        <rect x="125" y="60" width="50" height="50" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        <text x="150" y="90" font-size="11" text-anchor="middle" font-weight="bold">3</text>
                        
                        <rect x="75" y="110" width="50" height="50" fill="#fef08a" stroke="#ca8a04" stroke-width="2"/>
                        <text x="100" y="140" font-size="11" text-anchor="middle" font-weight="bold">{marked_faces['face2'][:1]}</text>
                        
                        <text x="100" y="170" font-size="10" text-anchor="middle" fill="#666">Marked: Blue & Yellow</text>
                    </svg>
                </div>
        """
        
        # Show the 3D cube result
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">3D Cube After Folding</p>
                    <svg width="200" height="200" style="border: 1px solid #ccc; background: white;">
                        <!-- Isometric cube -->
                        <!-- Top face (yellow) -->
                        <polygon points="50,60 120,60 155,85 85,85" fill="#fef08a" stroke="#ca8a04" stroke-width="2"/>
                        
                        <!-- Front face (blue) -->
                        <polygon points="50,60 120,60 120,130 50,130" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="85" y="100" font-size="12" text-anchor="middle" font-weight="bold">A</text>
                        
                        <!-- Right face (yellow) -->
                        <polygon points="120,60 155,85 155,155 120,130" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        <text x="135" y="105" font-size="12" text-anchor="middle" font-weight="bold">B</text>
                        
                        <text x="100" y="175" font-size="11" text-anchor="middle" font-weight="bold">Relationship: {marked_faces['relation'].upper()}</text>
                    </svg>
                </div>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 4px; border-left: 4px solid #3b82f6;">
                <p style="margin: 0 0 8px 0; font-weight: bold;">Folding Process:</p>
                <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px;">
                    <li>Face {marked_faces['face1'][:1]} is in the net at the top</li>
                    <li>Face {marked_faces['face2'][:1]} is in the net at the bottom</li>
                    <li>When folded, they become {marked_faces['relation']} faces</li>
                    <li>This relationship is determined by their positions in the net</li>
                </ul>
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_matching_nets_diagram(self, cube_data: dict, all_options: list) -> dict:
        """Render 3D cube to net matching visualization"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Matching 3D Cube to 2D Nets</h3>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; align-items: center;">
        """
        
        # Show the 3D cube
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">3D Cube to Match</p>
                    <svg width="180" height="180" style="border: 1px solid #ccc; background: white;">
                        <!-- Top face (yellow) -->
                        <polygon points="45,50 120,50 150,70 75,70" fill="#fef08a" stroke="#ca8a04" stroke-width="2"/>
                        <text x="97" y="65" font-size="10" text-anchor="middle" font-weight="bold">Top</text>
                        
                        <!-- Front face (blue) -->
                        <polygon points="45,50 120,50 120,130 45,130" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
                        <text x="82" y="95" font-size="10" text-anchor="middle" font-weight="bold">Front</text>
                        
                        <!-- Right face (red) -->
                        <polygon points="120,50 150,70 150,150 120,130" fill="#fecaca" stroke="#dc2626" stroke-width="2"/>
                        <text x="135" y="95" font-size="10" text-anchor="middle" font-weight="bold">Right</text>
                        
                        <text x="90" y="160" font-size="11" text-anchor="middle" fill="#666">{cube_data['description'][:30]}...</text>
                    </svg>
                </div>
        """
        
        # Show net options
        html += f"""
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Net Options</p>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
        """
        
        for i, option in enumerate(all_options):
            is_correct = option == all_options[0]  # First is always correct
            html += f"""
                        <div style="padding: 8px 12px; border-radius: 4px; border-left: 4px solid {'#10b981' if is_correct else '#9ca3af'}; background: {'#ecfdf5' if is_correct else '#f3f4f6'};">
                            <strong>{option}</strong> {'✓' if is_correct else ''}
                        </div>
            """
        
        html += """
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 4px; border-left: 4px solid #3b82f6;">
                <p style="margin: 0 0 8px 0; font-weight: bold;">How to Match:</p>
                <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px;">
                    <li>Identify all 6 faces on the 3D cube</li>
                    <li>Note which faces are opposite to each other</li>
                    <li>For each net option, check if opposite faces are in valid positions</li>
                    <li>Verify that adjacent faces in 3D remain properly connected in 2D</li>
                </ul>
            </div>
        </div>
        """
        
        return {"html": html}

    # ==================== SVG RENDERING METHODS ====================
    
    def _render_net_diagram_svg(self) -> str:
        """Render SVG showing cube net unfolded"""
        html = '''<div style="border:2px solid #2196F3; border-radius:8px; padding:15px; background:#e3f2fd; text-align:center;">
            <h4 style="color:#1976D2;">Cube Net Visualization</h4>
            <svg width="300" height="300" style="border:1px solid #ccc; background:white;">
                <rect x="100" y="100" width="50" height="50" fill="#E3F2FD" stroke="#1976D2" stroke-width="2"/>
                <rect x="100" y="50" width="50" height="50" fill="#BBDEFB" stroke="#1976D2" stroke-width="2"/>
                <rect x="100" y="150" width="50" height="50" fill="#BBDEFB" stroke="#1976D2" stroke-width="2"/>
                <rect x="50" y="100" width="50" height="50" fill="#C8E6C9" stroke="#4CAF50" stroke-width="2"/>
                <rect x="150" y="100" width="50" height="50" fill="#C8E6C9" stroke="#4CAF50" stroke-width="2"/>
                <rect x="200" y="100" width="50" height="50" fill="#FFF9C4" stroke="#FBC02D" stroke-width="2"/>
            </svg>
            <p style="padding:10px; color:#333; font-size:13px;">Nets: 3D shape unfolded • Check face connections</p>
        </div>'''
        return html

