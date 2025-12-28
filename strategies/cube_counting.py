"""Cube Counting question strategy - 3D spatial reasoning."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
from models.distractor import MisconceptionType
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPPOSITE_CONFUSION: 
                f"{original}",  # Shows original count, not remaining
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{removed}",    # Shows removed count, not remaining
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{size * size}" # Wrong calculation using size only
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Student forgets to subtract removed cubes, providing only the count of what was removed",
            custom_why_effective="Simple math problem with a clear subtraction step that students miss",
            custom_how_to_avoid="Always subtract the removed amount from the original total"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=1
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{layer_size}",  # Shows layer size, not remaining
            MisconceptionType.UNIVERSAL_VS_SPECIFIC: 
                f"{original}",     # Shows original, not remaining
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{remaining + layer_size}"  # Double-counted
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student counts the layer size instead of the remaining cubes after removal",
            custom_why_effective="Combines 2D and 3D calculations; students often report intermediate step values",
            custom_how_to_avoid="Always work through: calculate layer, then subtract from total"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{corners}",  # Shows corners count, not remaining
            MisconceptionType.UNIVERSAL_VS_SPECIFIC: 
                f"{original}", # Shows original, not remaining
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"{size * size * size - corners + 1}"  # Off-by-one error
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.CONSTRAINT_VIOLATION,
            difficulty=3,
            custom_description="Student misrembers or miscounts the number of corners on a cube (should be exactly 8)",
            custom_why_effective="Spatial reasoning with a specific geometric constraint that's easy to forget",
            custom_how_to_avoid="Remember: a cube always has exactly 8 corners (vertices), 12 edges, 6 faces"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{12 * size}",  # Counts edges but not subtract corners
            MisconceptionType.UNIVERSAL_VS_SPECIFIC: 
                f"{size * size * 6}",  # Counts all surface cubes
            MisconceptionType.LOGICAL_DISCONNECT: 
                f"{size}"  # Just reports size
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student counts edges but forgets to subtract corners which are counted multiple times",
            custom_why_effective="Multi-step spatial counting that requires understanding of overlap and deduplication",
            custom_how_to_avoid="When counting edges, always remember corners belong to 3 edges each; subtract them appropriately"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_painted_cubes(self) -> Question:
        """Paint cubes on surface, count unpainted."""
        size = random.choice([3, 4, 5])
        original = size ** 3
        unpainted = (size - 2) ** 3
        
        correct_answer = f"{unpainted}"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.UNIVERSAL_VS_SPECIFIC: 
                f"{original}",  # Shows all cubes, not unpainted
            MisconceptionType.OPPOSITE_CONFUSION: 
                f"{original - unpainted}",  # Shows painted count, not unpainted
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{size * size * 6}"  # Shows only surface formula
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=3,
            custom_description="Student confuses painted (surface) cubes with unpainted (interior) cubes, reporting opposite value",
            custom_why_effective="Classic K.C. Nag trap; students often compute painted correctly but answer wrong question",
            custom_how_to_avoid="Read carefully: are we counting painted or unpainted? For unpainted interior: use (n-2)³"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.OPERATION_DIRECTION: 
                f"{large * small}",  # Multiply instead of divide
            MisconceptionType.OPERATION_SELECTION: 
                f"{(large + small) ** 3}",  # Add instead of divide
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{large ** 3}"  # Shows large cube, not packing
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPERATION_SELECTION,
            difficulty=3,
            custom_description="Student chooses wrong operation: multiplies or adds dimensions instead of dividing",
            custom_why_effective="Tests both spatial reasoning and operation selection; multiple plausible wrong operations",
            custom_how_to_avoid="Remember: packing smaller into larger requires division: divide each dimension, then cube the result"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
