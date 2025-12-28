"""Nets & Folding question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
from models.distractor import MisconceptionType
import random


class NetsStrategy(BaseChapterStrategy):
    """Generates net folding and unfolding problems."""
    
    chapter = ChapterEnum.NETS
    chapter_name = "Nets"
    description = "Mental folding exercises"
    
    def generate(self) -> Question:
        """Generate a nets and folding question."""
        problem_type = random.choice([
            "cube_net",
            "net_matching",
            "fold_sequence",
            "unfold_box",
            "net_calculation",
            "spatial_folding"
        ])
        
        if problem_type == "cube_net":
            return self._generate_cube_net()
        elif problem_type == "net_matching":
            return self._generate_net_matching()
        elif problem_type == "fold_sequence":
            return self._generate_fold_sequence()
        elif problem_type == "unfold_box":
            return self._generate_unfold_box()
        elif problem_type == "net_calculation":
            return self._generate_net_calculation()
        else:
            return self._generate_spatial_folding()
    
    def _generate_cube_net(self) -> Question:
        """Identify which net forms a valid cube."""
        correct_answer = "Net A (valid cube)"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.PATTERN_MISIDENTIFICATION: 
                "Net B (invalid)",  # Overlaps when folded
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Net C (invalid)",   # Doesn't connect properly
            MisconceptionType.LOGICAL_DISCONNECT: 
                "None of them"       # Student can't visualize any
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.PATTERN_MISIDENTIFICATION,
            difficulty=2,
            custom_description="Student misidentifies valid vs invalid cube nets; overlooks overlapping faces",
            custom_why_effective="Requires spatial visualization that many students struggle with; visual inspection is unreliable",
            custom_how_to_avoid="Systematically check: count 6 squares, verify no overlaps when mentally folding, check connectivity"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Cube Nets",
            logical_trap="Students don't visualize folding correctly. "
                        "A valid cube net has exactly 6 connected squares with no overlaps.",
            data_representation="```\nValid Cube Net: 6 connected squares\nNo overlapping faces\n"
                               "Follows cube folding rules\n```",
            question_text="Which of these nets can fold into a cube without overlapping?",
            solution_steps=[
                "A cube has 6 faces (squares)",
                "Valid net: 6 squares connected",
                "Invalid: Overlaps when folded",
                "Answer: Net A is valid"
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
    
    def _generate_net_matching(self) -> Question:
        """Match net to its 3D shape."""
        correct_answer = "Cube 1"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.PATTERN_MISIDENTIFICATION: 
                "Cube 2",  # Wrong folding visualization
            MisconceptionType.LOGICAL_DISCONNECT: 
                "Cube 3",   # Lost track during folding
            MisconceptionType.UNIVERSAL_VS_SPECIFIC: 
                "None"      # Can't generalize pattern
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.PATTERN_MISIDENTIFICATION,
            difficulty=2,
            custom_description="Student can't correctly match a net to its folded 3D cube; wrong visualization",
            custom_why_effective="Classic K.C. Nag trap; requires precise mental rotation and folding visualization",
            custom_how_to_avoid="Fold one face at a time mentally; track which faces become adjacent; verify opposite faces exist"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Net Matching",
            logical_trap="K.C. Nag trap: Students don't mentally fold nets correctly. "
                        "Adjacent faces matter.",
            data_representation="```\nNet unfolded → Cube folded\n"
                               "Match faces: opposite faces shouldn't be adjacent\n```",
            question_text="Which cube does this net fold into?",
            solution_steps=[
                "Identify adjacent faces in the net",
                "Fold mentally to see 3D shape",
                "Match with given cube",
                "Answer: Cube 1"
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
    
    def _generate_fold_sequence(self) -> Question:
        """Fold a net step by step."""
        steps = random.randint(3, 5)
        correct_answer = f"{steps} folds"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{steps-1} folds",  # Undercounts folds
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{steps+1} folds",   # Off-by-one error
            MisconceptionType.OPERATION_SELECTION: 
                f"{steps*2} folds"    # Doubling instead of counting
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student doesn't count all folds needed; often undercounts or misses one step",
            custom_why_effective="Sequential process that requires careful tracking of each step; easy to lose count",
            custom_how_to_avoid="List each fold explicitly; verify you move from current state to next; count total movements"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Fold Sequence",
            logical_trap="Students don't track each fold correctly. "
                        "Count each folding motion.",
            data_representation=f"```\nFlat net → Sequence of {steps} folds\n"
                               "Track position after each fold\n```",
            question_text=f"How many folds are needed to form this net into a complete cube?",
            solution_steps=[
                f"Start: Flat net with {steps} faces visible",
                f"Fold 1: Bring two faces together",
                f"Fold 2: Join more faces",
                f"Total folds needed: {steps}"
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
    
    def _generate_unfold_box(self) -> Question:
        """Unfold a box mentally."""
        correct_answer = "Net shows all 6 faces connected"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                "Net shows only 5 faces",  # Forgot one face
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "Net has overlaps",         # Doesn't understand connectivity
            MisconceptionType.LOGICAL_DISCONNECT: 
                "Disconnected faces"        # Can't visualize unfolding
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets that a cube has 6 faces; provides incomplete net with only 5 or fewer squares",
            custom_why_effective="Common oversight; students visualize unfolding but lose count of faces",
            custom_how_to_avoid="Remember: cube has exactly 6 faces; verify your net shows 6 connected squares; count explicitly"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Box Unfolding",
            logical_trap="Students forget that an unfolded box must show exactly 6 connected squares.",
            data_representation="```\nClosed cube → Unfold all 6 faces\nMaintain connectivity\n```",
            question_text="If you unfold all faces of a cube, what shape is the resulting net?",
            solution_steps=[
                "A cube has 6 faces",
                "Unfold all faces flat",
                "Net shows 6 connected squares",
                "Arrangement varies but faces remain connected"
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
    
    def _generate_net_calculation(self) -> Question:
        """Calculate dimensions from net."""
        side = random.choice([2, 3, 5])
        area = side * side * 6
        
        correct_answer = f"{area} square units"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{side * side}",  # Counts only one face
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{side * 6}",      # Wrong multiplication
            MisconceptionType.FORMULA_MISAPPLICATION: 
                f"{area // 2}"      # Halves the result
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student counts only one or two faces instead of all 6 when calculating total surface area",
            custom_why_effective="Combines spatial reasoning (6 faces) with arithmetic (multiply and sum)",
            custom_how_to_avoid="Always remember: cube has 6 faces; calculate one face area; multiply by 6; verify your final answer"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Net Area Calculation",
            logical_trap="Students count only some faces or calculate face area wrong.",
            data_representation=f"```\nCube side: {side} units\nEach face area: {side}² = {side*side}\n"
                               f"Total surface area: 6 × {side*side} = {area}\n```",
            question_text=f"A cube has sides of {side} units. "
                          f"If unfolded, what's the total area of all faces?",
            solution_steps=[
                f"Cube side length: {side} units",
                f"Each face area: {side} × {side} = {side*side}",
                f"Number of faces: 6",
                f"Total area: 6 × {side*side} = {area}"
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
    
    def _generate_spatial_folding(self) -> Question:
        """Complex spatial folding task."""
        folds = random.randint(2, 4)
        correct_answer = f"Position {folds}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"Position {folds-1}",  # Undercounts folds
            MisconceptionType.ARITHMETIC_ERROR: 
                f"Position {folds+1}",   # Off-by-one
            MisconceptionType.LOGICAL_DISCONNECT: 
                "Indeterminate"           # Lost track
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.LOGICAL_DISCONNECT,
            difficulty=3,
            custom_description="Student loses spatial awareness after multiple folds; can't track position through sequence",
            custom_why_effective="K.C. Nag complex trap; requires maintaining mental model through multiple transformations",
            custom_how_to_avoid="After each fold, pause and visualize current position before proceeding; track systematically on paper"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Complex Spatial Folding",
            logical_trap="K.C. Nag complex: Students lose spatial track after multiple folds.",
            data_representation=f"```\nMultiple folds ({folds} total)\nTrack marker position\n"
                               "Visualize 3D result\n```",
            question_text=f"After {folds} folds, where is the marked point?",
            solution_steps=[
                f"Start: Marker at position 0",
                f"Fold {folds} times, tracking position",
                f"Final position: Position {folds}"
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
