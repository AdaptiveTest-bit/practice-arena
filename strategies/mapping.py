"""Strategy for Chapter 8: Mapping Your Way - Map Reading and Spatial Reasoning."""

import random
from models.question import Question, ChapterEnum
from models.distractor import MisconceptionType
from models.cognitive_levels import BloomLevel
from strategies.base import BaseChapterStrategy


class MappingStrategy(BaseChapterStrategy):
    """Generate questions for map reading and spatial reasoning."""
    
    chapter = ChapterEnum.MAPPING
    chapter_name = "Chapter 8: Mapping Your Way"
    description = "Map reading, coordinates, grid positioning, and distance with scales"
    
    def generate(self) -> Question:
        """Generate a random mapping question from available types."""
        question_type = random.choice([
            self._generate_coordinate_identification,
            self._generate_grid_positioning,
            self._generate_distance_with_scale,
            self._generate_direction_navigation,
            self._generate_map_key_interpretation,
            self._generate_relative_position
        ])
        return question_type()
    
    def _generate_coordinate_identification(self) -> Question:
        """Identify coordinates of location on grid.
        
        'What are the coordinates of the school?'
        """
        # Create grid with points
        grid_size = 5
        location_x = random.randint(1, grid_size)
        location_y = random.randint(1, grid_size)
        
        correct_answer = f"({location_x}, {location_y})"
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"({location_y}, {location_x})",  # Reversed
            MisconceptionType.OPERATION_SELECTION: f"({location_x + 1}, {location_y})",  # Off by one
            MisconceptionType.CONSTRAINT_VIOLATION: f"{location_x}, {location_y}"  # Missing parentheses
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Student reverses x and y coordinates (row/column confusion)",
            custom_why_effective="X (horizontal) and Y (vertical) are often confused",
            custom_how_to_avoid="Remember: (x, y) = (column, row) or (horizontal, vertical)"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.REMEMBER, trap_difficulty=1)
        
        grid_visual = self._create_coordinate_grid(grid_size, location_x, location_y)
        
        question = Question(
            chapter=self.chapter,
            topic="Coordinate Identification",
            logical_trap="Student confuses x and y coordinates (horizontal vs vertical)",
            data_representation=grid_visual,
            question_text=f"What are the coordinates of the star (★) on the grid?",
            solution_steps=[
                f"Count horizontally from left: {location_x}",
                f"Count vertically from bottom: {location_y}",
                f"Write as (x, y): ({location_x}, {location_y})"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_grid_positioning(self) -> Question:
        """Place location at given coordinates.
        
        'Where is the location at (3, 2)?'
        """
        location_x = random.randint(1, 5)
        location_y = random.randint(1, 5)
        
        # Create grid with labeled locations
        locations = {
            "Park": (random.randint(1, 5), random.randint(1, 5)),
            "School": (random.randint(1, 5), random.randint(1, 5)),
            "Library": (location_x, location_y),
            "Hospital": (random.randint(1, 5), random.randint(1, 5))
        }
        
        correct_answer = "Library"
        
        # PHASE 1: Misconceptions
        wrong_places = [k for k in locations.keys() if k != "Library"]
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: wrong_places[0],
            MisconceptionType.CONSTRAINT_VIOLATION: wrong_places[1] if len(wrong_places) > 1 else "Unknown",
            MisconceptionType.OPERATION_SELECTION: wrong_places[2] if len(wrong_places) > 2 else "Unknown"
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Student picks wrong location or misreads coordinates",
            custom_why_effective="Multiple locations make it easy to pick wrong one",
            custom_how_to_avoid="Always verify: move right to x position, then up to y position"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        grid_visual = self._create_labeled_grid(locations)
        
        question = Question(
            chapter=self.chapter,
            topic="Grid Positioning",
            logical_trap="Student misidentifies which location matches the given coordinates",
            data_representation=grid_visual,
            question_text=f"Which location is at coordinates ({location_x}, {location_y})?",
            solution_steps=[
                f"Find x-coordinate: {location_x} (move right)",
                f"Find y-coordinate: {location_y} (move up)",
                f"Identify location at ({location_x}, {location_y}): Library"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_distance_with_scale(self) -> Question:
        """Calculate actual distance using map scale.
        
        'If scale is 1 cm = 5 km, and distance on map is 3 cm, actual distance is?'
        """
        map_distance_cm = random.randint(2, 5)
        scale_km = random.randint(3, 10)
        
        actual_distance = map_distance_cm * scale_km
        correct_answer = f"{actual_distance} km"
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{map_distance_cm} km",  # Just map distance
            MisconceptionType.OPERATION_SELECTION: f"{map_distance_cm + scale_km} km",  # Addition
            MisconceptionType.UNIT_ERROR: f"{actual_distance} cm"  # Wrong units
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets to apply scale or misunderstands scale ratio",
            custom_why_effective="Scale multiplication is often skipped",
            custom_how_to_avoid="Always multiply map distance by scale factor"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        scale_visual = f"""
Map Scale:
1 cm on map = {scale_km} km in reality

Measured on map: {map_distance_cm} cm
Actual distance = {map_distance_cm} cm × {scale_km} = {actual_distance} km
        """
        
        question = Question(
            chapter=self.chapter,
            topic="Distance Calculation with Scale",
            logical_trap="Student forgets to multiply by scale factor",
            data_representation=scale_visual,
            question_text=f"A map has scale 1 cm = {scale_km} km. If distance on map is {map_distance_cm} cm, what is actual distance?",
            solution_steps=[
                f"Map scale: 1 cm = {scale_km} km",
                f"Distance measured on map: {map_distance_cm} cm",
                f"Actual distance = {map_distance_cm} × {scale_km} = {actual_distance} km"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_direction_navigation(self) -> Question:
        """Navigate using compass directions.
        
        'From school, go north 2 blocks and east 1 block. Where do you end up?'
        """
        start_x, start_y = 3, 3
        
        # Generate moves
        directions = ["North", "South", "East", "West"]
        move1_dir = random.choice(directions)
        move1_dist = random.randint(1, 3)
        
        remaining_dirs = [d for d in directions if d not in [move1_dir, self._opposite(move1_dir)]]
        move2_dir = random.choice(remaining_dirs)
        move2_dist = random.randint(1, 3)
        
        # Calculate final position
        x, y = start_x, start_y
        x += self._direction_x_delta(move1_dir) * move1_dist
        y += self._direction_y_delta(move1_dir) * move1_dist
        x += self._direction_x_delta(move2_dir) * move2_dist
        y += self._direction_y_delta(move2_dir) * move2_dist
        
        correct_answer = f"({x}, {y})"
        
        # PHASE 1: Misconceptions
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"({start_x}, {start_y})",  # No movement
            MisconceptionType.OPERATION_SELECTION: f"({x - self._direction_x_delta(move2_dir) * move2_dist}, {y})",  # First move only
            MisconceptionType.CONSTRAINT_VIOLATION: f"({y}, {x})"  # Reversed
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets second move or doesn't track position changes",
            custom_why_effective="Multi-step navigation requires tracking intermediate positions",
            custom_how_to_avoid="Track each move separately: update x for East/West, y for North/South"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        nav_visual = f"""
Start position: ({start_x}, {start_y})
Move 1: {move1_dist} blocks {move1_dir}
Move 2: {move2_dist} blocks {move2_dir}
        """
        
        question = Question(
            chapter=self.chapter,
            topic="Direction Navigation",
            logical_trap="Student forgets second move or miscounts steps",
            data_representation=nav_visual,
            question_text=f"Starting at ({start_x}, {start_y}), go {move1_dist} blocks {move1_dir}, then {move2_dist} blocks {move2_dir}. Where are you?",
            solution_steps=[
                f"Start: ({start_x}, {start_y})",
                f"After {move1_dir}: ({start_x + self._direction_x_delta(move1_dir) * move1_dist}, {start_y + self._direction_y_delta(move1_dir) * move1_dist})",
                f"After {move2_dir}: ({x}, {y})"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_map_key_interpretation(self) -> Question:
        """Interpret map key/legend.
        
        'According to the map key, what does the blue line represent?'
        """
        key_items = {
            "●": "City",
            "━": "Highway",
            "≋": "River",
            "▲": "Mountain",
            "🌲": "Forest"
        }
        
        correct_symbol = random.choice(list(key_items.keys()))
        correct_answer = key_items[correct_symbol]
        
        # PHASE 1: Misconceptions
        wrong_answers = [v for v in key_items.values() if v != correct_answer]
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: wrong_answers[0],
            MisconceptionType.CONSTRAINT_VIOLATION: wrong_answers[1],
            MisconceptionType.OPERATION_SELECTION: wrong_answers[2]
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Student misreads or confuses map symbols",
            custom_why_effective="Similar symbols can be easily confused",
            custom_how_to_avoid="Always check map key carefully for each symbol"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.REMEMBER, trap_difficulty=1)
        
        key_visual = "Map Key:\n" + "\n".join([f"{k} = {v}" for k, v in key_items.items()])
        
        question = Question(
            chapter=self.chapter,
            topic="Map Key Interpretation",
            logical_trap="Student confuses symbols in map key",
            data_representation=key_visual,
            question_text=f"According to the map key, what does '{correct_symbol}' represent?",
            solution_steps=[
                f"Find symbol '{correct_symbol}' in map key",
                f"Read corresponding meaning",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_relative_position(self) -> Question:
        """Describe relative positions on map.
        
        'The school is _______ of the park.'
        """
        locations = {
            "Park": (2, 2),
            "School": (4, 4),
            "Library": (2, 4),
            "Hospital": (4, 2)
        }
        
        school_x, school_y = locations["School"]
        park_x, park_y = locations["Park"]
        
        # Determine relative position
        if school_x > park_x and school_y > park_y:
            correct_answer = "northeast"
        elif school_x < park_x and school_y > park_y:
            correct_answer = "northwest"
        elif school_x > park_x and school_y < park_y:
            correct_answer = "southeast"
        else:
            correct_answer = "southwest"
        
        # PHASE 1: Misconceptions
        directions = ["northeast", "northwest", "southeast", "southwest"]
        wrong_dirs = [d for d in directions if d != correct_answer]
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: wrong_dirs[0],
            MisconceptionType.CONSTRAINT_VIOLATION: wrong_dirs[1],
            MisconceptionType.OPERATION_SELECTION: wrong_dirs[2]
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        # PHASE 2: Trap info
        trap_info = self.create_trap_info(
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student picks wrong compass direction for relative position",
            custom_why_effective="Diagonal directions require thinking about both x and y",
            custom_how_to_avoid="Check both horizontal and vertical differences"
        )
        
        # PHASE 3: Bloom info
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        position_visual = self._create_relative_position_grid(locations)
        
        question = Question(
            chapter=self.chapter,
            topic="Relative Positioning",
            logical_trap="Student miscalculates compass direction by ignoring one dimension",
            data_representation=position_visual,
            question_text=f"The school is _______ of the park.",
            solution_steps=[
                f"School position: {school_x}, {school_y}",
                f"Park position: {park_x}, {park_y}",
                f"Compare: School is {'right' if school_x > park_x else 'left'} and {'above' if school_y > park_y else 'below'} park",
                f"Answer: {correct_answer}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    # ============================================================================
    # VISUALIZATION HELPERS
    # ============================================================================
    
    @staticmethod
    def _create_coordinate_grid(size: int, x: int, y: int) -> str:
        """Create labeled coordinate grid with marked point."""
        grid = []
        grid.append("    " + " ".join(str(i) for i in range(1, size + 1)))
        
        for row in range(size, 0, -1):
            line = f"{row}  "
            for col in range(1, size + 1):
                if col == x and row == y:
                    line += "★ "
                else:
                    line += "□ "
            grid.append(line)
        
        return "\n".join(grid)
    
    @staticmethod
    def _create_labeled_grid(locations: dict) -> str:
        """Create grid with labeled locations."""
        grid = []
        grid.append("    1   2   3   4   5")
        
        for row in range(5, 0, -1):
            line = f"{row}  "
            for col in range(1, 6):
                found = False
                for name, (x, y) in locations.items():
                    if x == col and y == row:
                        line += f"{name[0]} "
                        found = True
                        break
                if not found:
                    line += ". "
            grid.append(line)
        
        return "\n".join(grid)
    
    @staticmethod
    def _create_relative_position_grid(locations: dict) -> str:
        """Create grid showing relative positions."""
        grid = []
        grid.append("    1   2   3   4   5")
        
        for row in range(5, 0, -1):
            line = f"{row}  "
            for col in range(1, 6):
                found = False
                for name, (x, y) in locations.items():
                    if x == col and y == row:
                        line += f"{name[0:2]} "
                        found = True
                        break
                if not found:
                    line += ".  "
            grid.append(line)
        
        return "\n".join(grid)
    
    @staticmethod
    def _direction_x_delta(direction: str) -> int:
        """Get x change for direction."""
        deltas = {"East": 1, "West": -1, "North": 0, "South": 0}
        return deltas.get(direction, 0)
    
    @staticmethod
    def _direction_y_delta(direction: str) -> int:
        """Get y change for direction."""
        deltas = {"East": 0, "West": 0, "North": 1, "South": -1}
        return deltas.get(direction, 0)
    
    @staticmethod
    def _opposite(direction: str) -> str:
        """Get opposite direction."""
        opposites = {"East": "West", "West": "East", "North": "South", "South": "North"}
        return opposites.get(direction, "")
    
    def _validate_question(self, question: Question) -> None:
        """Validate question has all required fields."""
        assert question.question_text
        assert question.answer
        assert len(question.options) == 4
        assert 0 <= question.correct_option_index < 4
        assert question.distractor_info
        assert question.trap_info
        assert question.bloom_info
