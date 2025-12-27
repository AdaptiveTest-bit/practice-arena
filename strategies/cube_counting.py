"""Cube Counting question strategy - 3D spatial reasoning."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
import random


class CubeCountingStrategy(BaseChapterStrategy):
    """Generates cube counting and 3D spatial reasoning problems."""
    
    chapter = ChapterEnum.CUBE_COUNTING
    chapter_name = "Cube Counting"
    description = "3D spatial reasoning"
    
    def generate(self) -> Question:
        """Generate a cube counting question."""
        problem_type = random.choice([
            "simple_removal",
            "layer_removal",
            "corner_removal",
            "edge_counting",
            "painted_cubes",
            "packing_problem"
        ])
        
        if problem_type == "simple_removal":
            return self._generate_simple_removal()
        elif problem_type == "layer_removal":
            return self._generate_layer_removal()
        elif problem_type == "corner_removal":
            return self._generate_corner_removal()
        elif problem_type == "edge_counting":
            return self._generate_edge_counting()
        elif problem_type == "painted_cubes":
            return self._generate_painted_cubes()
        else:  # packing_problem
            return self._generate_packing_problem()
    
    def _generate_simple_removal(self) -> Question:
        """Remove cubes from a structure."""
        original = random.choice([27, 64, 125])  # 3³, 4³, 5³
        size = int(original ** (1/3))
        removed = random.randint(1, 5)
        remaining = original - removed
        
        correct_answer = f"{remaining}"
        distractors = [
            f"{original}",
            f"{removed}",
            f"{size * size}"  # Wrong calculation
        ]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Cube Removal",
            logical_trap="Students count the removed cubes instead of remaining cubes, "
                        "or forget to subtract correctly.",
            data_representation=f"```\nOriginal structure: {size}×{size}×{size} = {original} cubes\n"
                               f"Cubes removed: {removed}\nRemaining: {remaining}\n```",
            question_text=f"A {size}×{size}×{size} cube structure has {removed} cubes removed. "
                          f"How many remain?",
            solution_steps=[
                f"Original cubes: {size} × {size} × {size} = {original}",
                f"Removed: {removed}",
                f"Remaining: {original} - {removed} = {remaining}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_layer_removal(self) -> Question:
        """Remove a complete layer."""
        size = random.choice([3, 4, 5])
        original = size ** 3
        layer_size = size * size
        remaining = original - layer_size
        
        correct_answer = f"{remaining}"
        distractors = [f"{layer_size}", f"{original}", f"{remaining + layer_size}"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Layer Removal",
            logical_trap="Students count layers incorrectly or multiply wrong dimensions.",
            data_representation=f"```\nCube: {size}×{size}×{size} = {original} cubes\n"
                               f"Remove 1 layer: {size}×{size} = {layer_size} cubes\n"
                               f"Remaining: {remaining} cubes\n```",
            question_text=f"Remove the top layer from a {size}×{size}×{size} cube. "
                          f"How many cubes remain?",
            solution_steps=[
                f"Total cubes: {size}³ = {original}",
                f"Top layer size: {size} × {size} = {layer_size}",
                f"Remaining: {original} - {layer_size} = {remaining}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_corner_removal(self) -> Question:
        """Remove corner cubes."""
        size = random.choice([3, 4, 5])
        original = size ** 3
        corners = 8
        remaining = original - corners
        
        correct_answer = f"{remaining}"
        distractors = [f"{corners}", f"{original}", f"{size * size * size - corners + 1}"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Corner Removal",
            logical_trap="K.C. Nag trap: Students forget that a cube has exactly 8 corners. "
                        "They might count edges or faces instead.",
            data_representation=f"```\nCube: {size}×{size}×{size} = {original} cubes\n"
                               f"Corners on a cube: 8\nRemaining: {remaining}\n```",
            question_text=f"Remove the 8 corner cubes from a {size}×{size}×{size} cube. "
                          f"How many remain?",
            solution_steps=[
                f"Total cubes: {original}",
                "A cube has 8 corners (vertex points)",
                f"Removing 8 corners: {original} - 8 = {remaining}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_edge_counting(self) -> Question:
        """Count cubes along edges."""
        size = random.choice([3, 4, 5])
        cubes_per_edge = size
        # A cube has 12 edges, but corners are counted 3 times
        total_edge_cubes = (12 * cubes_per_edge) - (12 + 8)
        
        correct_answer = f"{total_edge_cubes}"
        distractors = [f"{12 * size}", f"{size * size * 6}", f"{size}"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Edge Cube Counting",
            logical_trap="Students count all edge cubes multiple times or forget the corners.",
            data_representation=f"```\nCube dimensions: {size}×{size}×{size}\n"
                               f"Cubes per edge: {size}\nTotal edges: 12\n"
                               f"Edge cubes (excluding corners): {total_edge_cubes}\n```",
            question_text=f"How many cubes are along the edges of a {size}×{size}×{size} cube "
                          "(excluding corners)?",
            solution_steps=[
                f"A cube has {size} cubes per edge",
                "A cube has 12 edges",
                f"Total: 12 × {size} = {12 * size}",
                f"Subtract 8 corners (counted multiple times): {12 * size} - 8 = {total_edge_cubes}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_painted_cubes(self) -> Question:
        """Paint cubes on surface, count unpainted."""
        size = random.choice([3, 4, 5])
        original = size ** 3
        unpainted = (size - 2) ** 3
        
        correct_answer = f"{unpainted}"
        distractors = [f"{original}", f"{original - unpainted}", f"{size * size * 6}"]
        
        options, correct_idx = self.shuffle_options_keep_correct(correct_answer, distractors)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Painted Cubes",
            logical_trap="K.C. Nag trap: Students count all cubes or only surface cubes instead of "
                        "the internal unpainted cubes.",
            data_representation=f"```\nCube: {size}×{size}×{size} = {original} total\n"
                               f"Paint all surfaces\nUnpainted (interior): ({size}-2)³ = {unpainted}\n```",
            question_text=f"Paint all surfaces of a {size}×{size}×{size} cube. "
                          f"How many unit cubes have NO paint?",
            solution_steps=[
                f"Total cubes: {size}³ = {original}",
                "Paint all 6 faces",
                f"Interior unpainted cubes: ({size} - 2)³ = {(size-2)}³ = {unpainted}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_packing_problem(self) -> Question:
        """Pack smaller cubes into a larger container."""
        large = random.choice([2, 3, 4])
        small = random.choice([1, 2])
        if small >= large:
            small = 1
        
        cubes_fit = (large // small) ** 3
        
        correct_answer = f"{cubes_fit}"
        distractors = [f"{large * small}", f"{(large + small) ** 3}", f"{large ** 3}"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Boxes & Sketches - Cube Packing",
            logical_trap="Students add dimensions instead of dividing. "
                        "They might count 2D instead of 3D packing.",
            data_representation=f"```\nLarge cube: {large}×{large}×{large}\n"
                               f"Small cube: {small}×{small}×{small}\n"
                               f"Fit per dimension: {large // small}\n"
                               f"Total fit: ({large // small})³ = {cubes_fit}\n```",
            question_text=f"How many {small}×{small}×{small} cubes fit inside a "
                          f"{large}×{large}×{large} cube?",
            solution_steps=[
                f"Large cube: {large}×{large}×{large}",
                f"Small cube: {small}×{small}×{small}",
                f"Cubes fit per dimension: {large} ÷ {small} = {large // small}",
                f"Total fit: ({large // small})³ = {cubes_fit}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
