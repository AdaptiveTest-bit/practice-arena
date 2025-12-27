"""Nets & Folding question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
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
        distractors = ["Net B (invalid)", "Net C (invalid)", "None of them"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_net_matching(self) -> Question:
        """Match net to its 3D shape."""
        correct_answer = "Cube 1"
        distractors = ["Cube 2", "Cube 3", "None"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_fold_sequence(self) -> Question:
        """Fold a net step by step."""
        steps = random.randint(3, 5)
        correct_answer = f"{steps} folds"
        distractors = [f"{steps-1} folds", f"{steps+1} folds", f"{steps*2} folds"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_unfold_box(self) -> Question:
        """Unfold a box mentally."""
        correct_answer = "Net shows all 6 faces connected"
        distractors = ["Net shows only 5 faces", "Net has overlaps", "Disconnected faces"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_net_calculation(self) -> Question:
        """Calculate dimensions from net."""
        side = random.choice([2, 3, 5])
        area = side * side * 6
        
        correct_answer = f"{area} square units"
        distractors = [f"{side * side}", f"{side * 6}", f"{area // 2}"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_spatial_folding(self) -> Question:
        """Complex spatial folding task."""
        folds = random.randint(2, 4)
        correct_answer = f"Position {folds}"
        distractors = [f"Position {folds-1}", f"Position {folds+1}", "Indeterminate"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
