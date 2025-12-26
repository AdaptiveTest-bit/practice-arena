import random
from typing import Dict, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Question:
    """Represents a single question with all its components."""
    topic: str
    logical_trap: str
    data_representation: str
    question_text: str
    solution_steps: List[str]
    answer: str
    options: List[str] = None  # MCQ options (4 choices including correct answer)
    correct_option_index: int = None  # Index of correct answer in options (0-3)

    def format_output(self) -> str:
        """Format the question in the specified output format."""
        output = []
        output.append(f"## TOPIC: {self.topic}")
        output.append(f"\n**The Logical Trap:** {self.logical_trap}")
        output.append(f"\n**Data Representation:**\n{self.data_representation}")
        output.append(f"\n**Question:**\n{self.question_text}")
        
        # Add MCQ options if available
        if self.options:
            output.append(f"\n**Options:**")
            for i, option in enumerate(self.options, 1):
                output.append(f"{chr(64+i)}) {option}")
        
        output.append(f"\n**Solution:**")
        for i, step in enumerate(self.solution_steps, 1):
            output.append(f"{i}. {step}")
        output.append(f"\n**Answer:** {self.answer}\n")
        output.append("---\n")
        return "\n".join(output)


class QuestionGenerator(ABC):
    """Abstract base class for question generators."""
    
    @abstractmethod
    def generate(self) -> Question:
        pass


class DiceLogicGenerator(QuestionGenerator):
    """Generates dice problems using the opposite faces rule (sum = 7)."""
    
    def generate(self) -> Question:
        """Generate a dice logic problem."""
        problem_type = random.choice(["standard", "multiple_faces", "logic_trap"])
        
        if problem_type == "standard":
            return self._generate_standard_dice()
        elif problem_type == "multiple_faces":
            return self._generate_multiple_faces()
        else:
            return self._generate_logic_trap()
    
    def _generate_standard_dice(self) -> Question:
        """Standard dice problem: given top and one side, find others."""
        top_face = random.randint(1, 6)
        side_faces = [i for i in range(1, 7) if i != top_face and i != (7 - top_face)]
        visible_side = random.choice(side_faces)
        bottom_face = 7 - top_face
        opposite_visible = 7 - visible_side
        direction = random.choice(["North", "South", "East", "West"])
        
        # Create distractors
        wrong1 = random.choice([i for i in range(1, 7) if i not in [bottom_face, opposite_visible]])
        wrong2 = random.choice([i for i in range(1, 7) if i not in [bottom_face, opposite_visible, wrong1]])
        wrong3 = random.choice([i for i in range(1, 7) if i not in [bottom_face, opposite_visible, wrong1, wrong2]])
        
        options = [f"({bottom_face}, {opposite_visible})", f"({wrong1}, {wrong2})", f"({bottom_face}, {wrong3})", f"({wrong2}, {opposite_visible})"]
        random.shuffle(options)
        correct_idx = options.index(f"({bottom_face}, {opposite_visible})")
        
        question = Question(
            topic="Boxes & Sketches - Dice Logic",
            logical_trap="Student must remember that opposite faces sum to 7, and distinguish between visible and hidden faces.",
            data_representation=f"```\nStandard Die Rule: Opposite faces sum to 7\nTop face: {top_face}\nVisible side ({direction}): {visible_side}\n```",
            question_text=f"A standard die is placed on a table. The face showing on top is {top_face}. If you look at the die from the {direction} side, you see the number {visible_side}.\n\nWhat number is on:\n(a) The face touching the table (bottom)?\n(b) The {self._get_opposite_direction(direction)} face?",
            solution_steps=[
                f"Top face = {top_face}, so Bottom face = 7 - {top_face} = {bottom_face}",
                f"Visible side ({direction}) = {visible_side}, so Opposite side ({self._get_opposite_direction(direction)}) = 7 - {visible_side} = {opposite_visible}",
                f"Verify: Top={top_face}, Bottom={bottom_face}, {direction}={visible_side}, {self._get_opposite_direction(direction)}={opposite_visible}"
            ],
            answer=f"({bottom_face}, {opposite_visible})",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_multiple_faces(self) -> Question:
        """Problem involving 3 visible faces of a cube."""
        faces = [random.randint(1, 6) for _ in range(3)]
        while len(set(faces)) < 3:  # Ensure all different
            faces = [random.randint(1, 6) for _ in range(3)]
        
        # The hidden face (one that doesn't appear and sums with one of the visible faces to 7)
        visible_set = set(faces)
        hidden_options = [i for i in range(1, 7) if i not in visible_set]
        hidden = random.choice(hidden_options)
        
        # Create distractors
        wrong_opts = [i for i in range(1, 7) if i not in visible_set and i != hidden]
        distractors = random.sample(wrong_opts, min(3, len(wrong_opts)))
        
        options = [str(hidden)] + [str(d) for d in distractors] + [str(random.randint(1, 6)) for _ in range(max(0, 4 - len(distractors) - 1))]
        options = list(set(options))[:4]
        random.shuffle(options)
        correct_idx = options.index(str(hidden))
        
        question = Question(
            topic="Boxes & Sketches - Dice Logic (Multiple Faces)",
            logical_trap="When you see 3 faces of a die, there are 3 hidden faces. Students might confuse which faces are opposite to the visible ones.",
            data_representation=f"```\nThree Visible Faces: {faces[0]}, {faces[1]}, {faces[2]}\n\nRule: Opposite faces sum to 7\nIf you see face X, the opposite (hidden) face is 7 - X\n```",
            question_text=f"On a cube, you can see three faces showing {faces[0]}, {faces[1]}, and {faces[2]}. Which number is on a hidden face opposite to one of these visible faces?",
            solution_steps=[
                f"Visible faces: {faces[0]}, {faces[1]}, {faces[2]}",
                f"Using the rule (opposite faces sum to 7):",
                f"Opposite to {faces[0]} is {7-faces[0]}",
                f"Opposite to {faces[1]} is {7-faces[1]}",
                f"Opposite to {faces[2]} is {7-faces[2]}",
                f"The hidden face must be one of: {7-faces[0]}, {7-faces[1]}, {7-faces[2]}"
            ],
            answer=str(hidden),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_logic_trap(self) -> Question:
        """Trap: Students might use wrong logic (e.g., "6 - x" instead of "7 - x")."""
        top_face = random.choice([2, 3, 4, 5])  # Avoid 1 and 6 for clarity
        bottom_face = 7 - top_face
        
        # Create trap options
        wrong_logic_1 = 6 - top_face  # Student uses sum=6
        wrong_logic_2 = top_face  # Student thinks same as top
        wrong_logic_3 = 8 - top_face  # Student uses sum=8
        
        options = [str(bottom_face), str(wrong_logic_1), str(wrong_logic_2), str(wrong_logic_3)]
        random.shuffle(options)
        correct_idx = options.index(str(bottom_face))
        
        question = Question(
            topic="Boxes & Sketches - Dice Logic (The Sum Rule)",
            logical_trap="CRITICAL TRAP: Students might think opposite faces sum to 6 or 8, or that the bottom face is the same as the top. It's ALWAYS 7!",
            data_representation=f"```\nDICE RULE - MEMORIZE:\nOPPOSITE FACES ALWAYS SUM TO 7\n\nNot 6, not 8, not anything else.\nIt's a fundamental property of standard dice.\n\nIf top = {top_face}, then bottom = 7 - {top_face} = {bottom_face}\n```",
            question_text=f"A standard die shows {top_face} on top. What number is on the bottom face?",
            solution_steps=[
                f"Apply the rule: Opposite faces sum to 7",
                f"Top face = {top_face}",
                f"Bottom face = 7 - {top_face} = {bottom_face}",
                f"The answer is {bottom_face}, NOT {wrong_logic_1} or {wrong_logic_2}"
            ],
            answer=str(bottom_face),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    @staticmethod
    def _get_opposite_direction(direction: str) -> str:
        opposites = {
            "North": "South",
            "South": "North",
            "East": "West",
            "West": "East"
        }
        return opposites.get(direction, direction)


class CubeCountingGenerator(QuestionGenerator):
    """Generates 3D cube counting problems."""
    
    def generate(self) -> Question:
        """Generate a cube counting problem."""
        problem_type = random.choice(["simple_removal", "layer_removal", "corner_removal", "edge_counting"])
        
        if problem_type == "simple_removal":
            return self._generate_simple_removal()
        elif problem_type == "layer_removal":
            return self._generate_layer_removal()
        elif problem_type == "corner_removal":
            return self._generate_corner_removal()
        else:
            return self._generate_edge_counting()
    
    def _generate_simple_removal(self) -> Question:
        """Single cube removal from corner or edge."""
        total = 27
        removed = 1
        answer = 26
        
        # Create distractors
        wrong1 = 25
        wrong2 = 24
        wrong3 = 27
        
        options = [str(answer), str(wrong1), str(wrong2), str(wrong3)]
        random.shuffle(options)
        correct_idx = options.index(str(answer))
        
        question = Question(
            topic="Boxes & Sketches - Cube Counting (Simple)",
            logical_trap="Student might think removing a corner cube affects multiple layers, but it only affects that one cube.",
            data_representation=f"```\n3×3×3 block = 27 cubes total\nRemoving 1 corner cube removes only 1 cube\nRemaining = 27 - 1 = 26\n```",
            question_text=f"A 3×3×3 block has 27 unit cubes. If you remove one corner cube, how many cubes remain?",
            solution_steps=[
                f"Total cubes = 3 × 3 × 3 = 27",
                f"Removed = 1 corner cube",
                f"Remaining = 27 - 1 = 26"
            ],
            answer=str(answer),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_layer_removal(self) -> Question:
        """Entire top or bottom layer removal."""
        size = random.choice([3, 4])
        total = size ** 3
        removed = size ** 2
        answer = total - removed
        
        # Create distractors
        wrong1 = answer - 1
        wrong2 = answer + 1
        wrong3 = removed
        
        options = [str(answer), str(wrong1), str(wrong2), str(wrong3)]
        random.shuffle(options)
        correct_idx = options.index(str(answer))
        
        question = Question(
            topic="Boxes & Sketches - Cube Counting (Layer Removal)",
            logical_trap="A LAYER is a complete horizontal slice. For a 4×4×4, removing one layer removes 16 cubes, not 4!",
            data_representation=f"```\n{size}×{size}×{size} block = {total} cubes\nOne layer = {size}×{size} = {removed} cubes\nRemaining = {total} - {removed} = {answer}\n```",
            question_text=f"A {size}×{size}×{size} block of unit cubes has its entire top layer removed. How many cubes remain?",
            solution_steps=[
                f"Total cubes = {size} × {size} × {size} = {total}",
                f"Top layer = {size} × {size} = {removed} cubes",
                f"Remaining = {total} - {removed} = {answer}"
            ],
            answer=str(answer),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_corner_removal(self) -> Question:
        """Multiple corner cubes removal."""
        total = 27
        removed = 4
        answer = 23
        
        wrong1 = 24
        wrong2 = 22
        wrong3 = 25
        
        options = [str(answer), str(wrong1), str(wrong2), str(wrong3)]
        random.shuffle(options)
        correct_idx = options.index(str(answer))
        
        question = Question(
            topic="Boxes & Sketches - Cube Counting (Corner Removal)",
            logical_trap="Removing corners from just the TOP layer doesn't affect lower layers. Count carefully which cubes are actually removed.",
            data_representation=f"```\n3×3×3 block = 27 cubes\nRemoving 4 corners from TOP only = 4 cubes removed\nThe layers below are untouched\nRemaining = 27 - 4 = 23\n```",
            question_text=f"A 3×3×3 block of cubes has all four corner cubes of the top layer removed. How many cubes remain?",
            solution_steps=[
                f"Total cubes = 27",
                f"Only 4 corner cubes from the TOP layer are removed",
                f"The 3 layers below are completely intact",
                f"Remaining = 27 - 4 = 23"
            ],
            answer=str(answer),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_edge_counting(self) -> Question:
        """Counting visible cubes (surface) vs total."""
        size = 4
        total = size ** 3
        # Surface cubes = total - interior
        interior = (size - 2) ** 3 if size > 2 else 0
        surface = total - interior
        
        answer = surface
        wrong1 = interior
        wrong2 = total
        wrong3 = total - 8
        
        options = [str(answer), str(wrong1), str(wrong2), str(wrong3)]
        random.shuffle(options)
        correct_idx = options.index(str(answer))
        
        question = Question(
            topic="Boxes & Sketches - Cube Counting (Surface vs Interior)",
            logical_trap="Students count all cubes instead of only VISIBLE (surface) ones. Interior cubes are hidden inside.",
            data_representation=f"```\n4×4×4 block = {total} cubes total\nInterior cubes (hidden) = 2×2×2 = {interior}\nVISIBLE cubes (surface) = {total} - {interior} = {answer}\n```",
            question_text=f"In a 4×4×4 block of unit cubes, how many cubes are VISIBLE (on the surface)?",
            solution_steps=[
                f"Total cubes = 4 × 4 × 4 = {total}",
                f"Interior (hidden) cubes = (4-2) × (4-2) × (4-2) = 2 × 2 × 2 = {interior}",
                f"Visible (surface) cubes = {total} - {interior} = {answer}"
            ],
            answer=str(answer),
            options=options,
            correct_option_index=correct_idx
        )
        return question


class NetsGenerator(QuestionGenerator):
    """Generates net folding problems."""
    
    def generate(self) -> Question:
        """Generate a nets problem (mental folding)."""
        nets_data = [
            {
                "shape": "T-shaped net (6 squares arranged as: 4 in a row, 1 above middle-left, 1 below middle-right)",
                "center": "The square directly below the vertical middle of the 4-row",
                "opposite": "The square that is 3 steps away along the fold path",
                "question_desc": "Which square ends up opposite to the marked center square when folded into a cube?",
                "answer": "The farthest square in the opposite direction of fold",
                "correct_answer_text": "Farthest square (opposite to center)"
            },
            {
                "shape": "Cross-shaped net (1 center square surrounded by 4 squares on all sides, 1 more on top)",
                "center": "The center square",
                "opposite": "The topmost square in the extended row",
                "question_desc": "Which square ends up opposite to the center square when folded into a cube?",
                "answer": "The outermost square of the 6-square net",
                "correct_answer_text": "The topmost square"
            }
        ]
        
        net = random.choice(nets_data)
        
        # MCQ options
        if random.choice([True, False]):
            # Option 1: Correct answer
            correct_answer = net['correct_answer_text']
            distractors = [
                "An adjacent square in the net",
                "The center square itself",
                "A square perpendicular to the fold"
            ]
        else:
            # Option 2: Alternate scenario
            correct_answer = "The outermost square"
            distractors = [
                "The center square",
                "An adjacent square",
                "The nearest horizontal square"
            ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Boxes & Sketches - Nets",
            logical_trap="Student must visualize 3D folding mentally without physical manipulation. Easy to reverse directions.",
            data_representation=f"```\n{net['shape']}\n\nFolding Pattern:\n- The 6 squares will form the 6 faces of a cube\n- Adjacent squares in the net become adjacent faces\n- Non-adjacent squares in the net become opposite faces\n```",
            question_text=f"{net['question_desc']}\n\nAssuming the net is folded into a standard cube:",
            solution_steps=[
                "Identify the center square and trace the folding sequence",
                "In a net, if you count the minimum steps (edges) between two squares, they are opposite if the count is 3",
                "The marked square connects to 4 faces in the net, leaving 1 face opposite"
            ],
            answer=net['answer'],
            options=options,
            correct_option_index=correct_idx
        )
        return question


class DataHandlingGenerator(QuestionGenerator):
    """Generates data handling problems with non-unitary scales and missing data."""
    
    def generate(self) -> Question:
        """Generate a data handling problem."""
        
        # Define problem types
        problem_type = random.choice(["scale_trap", "missing_value", "comparison"])
        
        if problem_type == "scale_trap":
            return self._generate_scale_trap()
        elif problem_type == "missing_value":
            return self._generate_missing_value()
        else:
            return self._generate_comparison()
    
    def _generate_scale_trap(self) -> Question:
        """Generate a pictograph problem with non-unitary scale."""
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
        scale = random.choice([8, 10, 12, 15])  # 1 symbol = x items
        
        # Generate data ensuring integer results
        data = {day: random.randint(2, 6) for day in days}
        
        price_per_item = random.choice([5, 8, 10, 12, 15])
        
        # Pick a day for earning calculation
        query_day = random.choice(days)
        
        # Calculate earnings
        actual_items = data[query_day] * scale
        earnings = actual_items * price_per_item
        
        # Create table
        table = "| Day | Symbols (1 Icon = {} Items) | Actual Items |\n".format(scale)
        table += "|-----|----------------------------|------------|\n"
        for day in days:
            symbols = "⭐" * data[day]
            items = data[day] * scale
            table += f"| {day} | {symbols} | {items} |\n"
        
        # MCQ options
        correct_answer = str(actual_items)
        wrong1 = str(data[query_day])  # Forgot to multiply by scale
        wrong2 = str(actual_items + 10)  # Calculation error
        wrong3 = str(actual_items * scale)  # Multiplied twice
        
        options = [correct_answer, wrong1, wrong2, wrong3]
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Data Handling - Pictographs (Scale Trap)",
            logical_trap=f"Scale is non-unitary (1 symbol = {scale} items, NOT 1 item). Students often forget to multiply by the scale factor.",
            data_representation=table,
            question_text=f"The shopkeeper earned ₹{earnings} on {query_day}. Each item costs ₹{price_per_item}.\n\nHow many items were sold on {query_day}?",
            solution_steps=[
                f"Symbols shown on {query_day} = {data[query_day]}",
                f"Scale: 1 symbol = {scale} items",
                f"Actual items sold = {data[query_day]} × {scale} = {actual_items}",
                f"Verify: {actual_items} items × ₹{price_per_item}/item = ₹{earnings} ✓"
            ],
            answer=str(actual_items),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_missing_value(self) -> Question:
        """Generate a table with missing data that must be calculated."""
        
        categories = random.choice([
            ["A", "B", "C", "D"],
            ["Class 1", "Class 2", "Class 3", "Class 4"],
            ["Item X", "Item Y", "Item Z"]
        ])
        
        missing_idx = random.randint(0, len(categories) - 1)
        total_sum = random.randint(100, 300)
        
        # Generate values for all except missing
        values = []
        running_sum = 0
        for i in range(len(categories)):
            if i == missing_idx:
                values.append(None)
            else:
                val = random.randint(20, 80)
                values.append(val)
                running_sum += val
        
        missing_value = total_sum - running_sum
        values[missing_idx] = missing_value
        
        # Create table
        table = "| Category | Value |\n|----------|-------|\n"
        for i, cat in enumerate(categories):
            if i == missing_idx:
                table += f"| {cat} | ? |\n"
            else:
                table += f"| {cat} | {values[i]} |\n"
        table += f"| **Total** | **{total_sum}** |\n"
        
        query_cat = categories[missing_idx]
        
        # MCQ options
        correct_answer = str(missing_value)
        wrong1 = str(missing_value + 10)  # Off by 10
        wrong2 = str(total_sum - running_sum - 5)  # Calculation error
        wrong3 = str(running_sum)  # Confused sum of known with missing
        
        options = [correct_answer, wrong1, wrong2, wrong3]
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Data Handling - Missing Data",
            logical_trap="Student must realize that the total is a constraint. They must use subtraction (Total - Sum of Known) to find the missing value.",
            data_representation=table,
            question_text=f"The total value is {total_sum}. What is the missing value for {query_cat}?",
            solution_steps=[
                f"Known values: {', '.join(str(v) for i, v in enumerate(values) if i != missing_idx)}",
                f"Sum of known values = {sum(v for i, v in enumerate(values) if i != missing_idx)}",
                f"Missing value = Total - Sum of known = {total_sum} - {sum(v for i, v in enumerate(values) if i != missing_idx)} = {missing_value}"
            ],
            answer=str(missing_value),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_comparison(self) -> Question:
        """Generate a comparison problem asking 'How many MORE/LESS'."""
        
        items = ["Apples", "Bananas", "Oranges", "Mangoes"]
        item1, item2 = random.sample(items, 2)
        
        val1 = random.randint(40, 120)
        val2 = random.randint(40, 120)
        
        difference = abs(val1 - val2)
        more_or_less = "more" if val1 > val2 else "less"
        
        table = f"| Item | Quantity |\n|------|----------|\n"
        table += f"| {item1} | {val1} |\n"
        table += f"| {item2} | {val2} |\n"
        
        # MCQ options
        correct_answer = str(difference)
        wrong1 = str(difference + 5)  # Off by 5
        wrong2 = str(val1)  # Used one value instead of difference
        wrong3 = str(val1 + val2)  # Added instead of subtracted
        
        options = [correct_answer, wrong1, wrong2, wrong3]
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Data Handling - Comparison",
            logical_trap="Student must compute the absolute difference AND use correct language ('more' vs 'less') to compare two quantities.",
            data_representation=table,
            question_text=f"How many {more_or_less} {item2.lower()} are there compared to {item1.lower()}?",
            solution_steps=[
                f"Quantity of {item1} = {val1}",
                f"Quantity of {item2} = {val2}",
                f"Difference = |{val1} - {val2}| = {difference}",
                f"Since {val1} {'>' if val1 > val2 else '<'} {val2}, {item2} are {difference} {more_or_less} than {item1}"
            ],
            answer=str(difference),
            options=options,
            correct_option_index=correct_idx
        )
        return question


class ClockAnglesGenerator(QuestionGenerator):
    """Generates angle problems using clock face logic."""
    
    def generate(self) -> Question:
        """Generate a clock-based angle problem."""
        problem_type = random.choice(["simple_time", "rotation_fraction", "angle_name"])
        
        if problem_type == "simple_time":
            return self._generate_simple_time_angles()
        elif problem_type == "rotation_fraction":
            return self._generate_rotation_fractions()
        else:
            return self._generate_angle_names()
    
    def _generate_simple_time_angles(self) -> Question:
        """Clock hand angles at specific times."""
        times = [
            {"hour": 3, "minute": 0, "angle": 90, "name": "Right Angle"},
            {"hour": 6, "minute": 0, "angle": 180, "name": "Straight Angle"},
            {"hour": 9, "minute": 0, "angle": 90, "name": "Right Angle"},
            {"hour": 12, "minute": 0, "angle": 0, "name": "No angle (Same position)"},
            {"hour": 3, "minute": 30, "angle": 75, "name": "Acute Angle"},
        ]
        
        time_data = random.choice(times)
        
        # MCQ options
        correct_answer = f"{time_data['angle']}° ({time_data['name']})"
        distractors = [
            f"{time_data['angle'] + 15}° (Wrong calculation)",
            f"{time_data['angle'] - 15}° (Off by 15°)",
            "30° (Forgot minute hand moves)"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Clock Angles",
            logical_trap="Students often forget that both hands move. At times like 3:30, the hour hand is NOT exactly at 3—it's halfway between 3 and 4.",
            data_representation=f"```\nClock Face Reference:\n12 at top\n3 at right\n6 at bottom\n9 at left\n\nAngle Measurement:\nEach hour = 30° (360° ÷ 12 hours)\nEach minute = 6° (360° ÷ 60 minutes)\n```",
            question_text=f"At {time_data['hour']}:{time_data['minute']:02d}, what is the angle between the hour and minute hands of a clock? Name the angle type.",
            solution_steps=[
                f"At {time_data['hour']}:{time_data['minute']:02d}:",
                f"Minute hand points to: {time_data['minute'] // 5 if time_data['minute'] != 0 else 12}",
                f"Hour hand is at: {time_data['hour'] % 12 if time_data['hour'] % 12 != 0 else 12}",
                f"The angle between them: {time_data['angle']}°",
                f"Angle type: {time_data['name']}"
            ],
            answer=f"{time_data['angle']}° ({time_data['name']})",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_rotation_fractions(self) -> Question:
        """Fractions of a full rotation."""
        rotations = [
            {"fraction": "1/4", "degrees": 90, "turn": "quarter turn", "description": "Right angle"},
            {"fraction": "1/2", "degrees": 180, "turn": "half turn", "description": "Straight angle"},
            {"fraction": "3/4", "degrees": 270, "turn": "three-quarter turn", "description": "Reflex angle"},
            {"fraction": "1/8", "degrees": 45, "turn": "eighth turn", "description": "Acute angle"},
        ]
        
        rotation = random.choice(rotations)
        
        # MCQ options
        correct_answer = f"{rotation['degrees']}° ({rotation['description']})"
        distractors = [
            f"{360 // 4}° (Mistake: only quarter of 360, not fraction calculation)",
            f"{rotation['degrees'] + 45}° (Off by 45°)",
            "180° (Wrong calculation)"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Rotations",
            logical_trap="Students confuse fractions of a turn with angle measures. A 1/4 turn is 90°, NOT 1/4 of something else.",
            data_representation=f"```\nRotation Conversion:\nFull rotation = 360°\n\nCommon Fractions:\n1/2 rotation = ?\n1/4 rotation = ?\n1/8 rotation = ?\n3/4 rotation = ?\n```",
            question_text=f"If you make a {rotation['fraction']} turn (a {rotation['turn']}), through how many degrees have you rotated? What is the angle classification?",
            solution_steps=[
                f"A complete rotation = 360°",
                f"{rotation['fraction']} of a full rotation = {rotation['fraction']} × 360°",
                f"= {rotation['degrees']}°",
                f"This is a {rotation['description']}."
            ],
            answer=f"{rotation['degrees']}° ({rotation['description']})",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_angle_names(self) -> Question:
        """Classify angles by their measures."""
        angles = [
            {"measure": 45, "name": "Acute Angle", "reason": "Less than 90°"},
            {"measure": 90, "name": "Right Angle", "reason": "Exactly 90°"},
            {"measure": 135, "name": "Obtuse Angle", "reason": "Between 90° and 180°"},
            {"measure": 180, "name": "Straight Angle", "reason": "Exactly 180°"},
        ]
        
        angle = random.choice(angles)
        
        # MCQ options
        correct_answer = angle['name']
        distractors_list = [
            "Reflex Angle",
            "Acute Angle",
            "Obtuse Angle"
        ]
        distractors = [d for d in distractors_list if d != correct_answer][:3]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Angle Classification",
            logical_trap="Students often confuse angle names. Remember: Acute < 90, Right = 90, Obtuse is between 90-180, Straight = 180.",
            data_representation=f"```\nAngle Types (Study the ranges):\nAcute: Less than 90°\nRight: Exactly 90°\nObtuse: Greater than 90° but less than 180°\nStraight: Exactly 180°\nReflex: Greater than 180°\n```",
            question_text=f"An angle measures {angle['measure']}°. What type of angle is it?",
            solution_steps=[
                f"Given angle = {angle['measure']}°",
                f"Checking the classification:",
                f"{angle['reason']}",
                f"Therefore, this is a {angle['name']}."
            ],
            answer=angle['name'],
            options=options,
            correct_option_index=correct_idx
        )
        return question


class SymmetryGenerator(QuestionGenerator):
    """Generates symmetry problems using letters and words."""
    
    def generate(self) -> Question:
        """Generate a symmetry problem."""
        problem_type = random.choice(["letter_symmetry", "word_mirror", "both_symmetries"])
        
        if problem_type == "letter_symmetry":
            return self._generate_letter_symmetry()
        elif problem_type == "word_mirror":
            return self._generate_word_mirror()
        else:
            return self._generate_both_symmetries()
    
    def _generate_letter_symmetry(self) -> Question:
        """Test symmetry of capital letters."""
        letters_data = [
            {
                "letter": "A",
                "vertical": True,
                "horizontal": False,
                "description": "Triangle shape, symmetric top-to-bottom"
            },
            {
                "letter": "H",
                "vertical": True,
                "horizontal": True,
                "description": "Two vertical lines with horizontal bar"
            },
            {
                "letter": "I",
                "vertical": True,
                "horizontal": True,
                "description": "Single straight line (if perfectly vertical)"
            },
            {
                "letter": "M",
                "vertical": True,
                "horizontal": False,
                "description": "Two peaks with valley in middle"
            },
            {
                "letter": "X",
                "vertical": True,
                "horizontal": True,
                "description": "Two diagonal lines crossing"
            },
        ]
        
        letter = random.choice(letters_data)
        
        symmetries = []
        if letter["vertical"]:
            symmetries.append("vertical (left-right)")
        if letter["horizontal"]:
            symmetries.append("horizontal (top-bottom)")
        if not symmetries:
            symmetries.append("no line of symmetry")
        
        answer_text = " and ".join(symmetries)
        
        # MCQ options
        correct_answer = f"{letter['letter']} has {answer_text} symmetry"
        distractors = [
            f"{letter['letter']} has no line of symmetry",
            f"{letter['letter']} has both vertical and horizontal symmetry",
            f"{letter['letter']} has only horizontal symmetry"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Letter Symmetry",
            logical_trap="Students confuse vertical and horizontal symmetry. Vertical symmetry = mirror down the middle (left-right). Horizontal symmetry = mirror across middle (top-bottom).",
            data_representation=f"```\nSymmetry Definitions:\nVertical symmetry = Left and right halves are mirror images\nHorizontal symmetry = Top and bottom halves are mirror images\n\nTest Method:\nFold the letter down the middle (vertical)\nFold the letter across the middle (horizontal)\nDo the halves match?\n```",
            question_text=f"Does the capital letter '{letter['letter']}' have any line of symmetry? If so, which type?",
            solution_steps=[
                f"Examining the letter '{letter['letter']}':",
                f"{letter['description']}",
                f"Checking vertical symmetry (fold down middle): {'YES' if letter['vertical'] else 'NO'}",
                f"Checking horizontal symmetry (fold across middle): {'YES' if letter['horizontal'] else 'NO'}",
                f"Therefore, '{letter['letter']}' has {answer_text} symmetry."
            ],
            answer=f"{letter['letter']} has {answer_text} symmetry",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_word_mirror(self) -> Question:
        """Test mirror writing of words."""
        words_data = [
            {
                "word": "MOM",
                "is_palindrome": True,
                "reason": "M→M, O→O, M→M (all letters are vertically symmetric)"
            },
            {
                "word": "DAD",
                "is_palindrome": False,
                "reason": "D is not vertically symmetric (it's not the same when mirrored)"
            },
            {
                "word": "BOB",
                "is_palindrome": False,
                "reason": "B is not vertically symmetric; it faces one direction"
            },
            {
                "word": "NOON",
                "is_palindrome": True,
                "reason": "N→N (symmetric), O→O, O→O, N→N (reads same in mirror)"
            },
        ]
        
        word = random.choice(words_data)
        
        # MCQ options
        correct_answer = f"{'YES' if word['is_palindrome'] else 'NO'} - {word['word']} {'reads the same' if word['is_palindrome'] else 'does NOT read the same'} in mirror"
        distractors = [
            f"{'NO' if word['is_palindrome'] else 'YES'} - {word['word']} {'reads the same' if not word['is_palindrome'] else 'does NOT read the same'} in mirror",
            f"{'YES' if not word['is_palindrome'] else 'NO'} - Only palindromes can be mirrored",
            "Cannot determine without drawing it"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Word Symmetry & Mirror Writing",
            logical_trap="Students think palindromes are the same as mirror-symmetric words. A word is mirror-symmetric only if each letter is vertically symmetric AND the word reads the same.",
            data_representation=f"```\nMirror Writing Analysis:\nFor a word to look the same in a mirror:\n1. Check if each letter is vertically symmetric\n2. Check if the word is a palindrome\n3. Both conditions must be TRUE\n\nSymmetric letters: A, H, I, M, O, T, U, V, W, X, Y\nNon-symmetric: B, C, D, E, F, G, J, K, L, N, P, Q, R, S, Z\n```",
            question_text=f"Which word reads the same if you hold it in front of a mirror? (Word: {word['word']})",
            solution_steps=[
                f"Checking '{word['word']}':",
                f"{word['reason']}",
                f"Mirror reading: {word['word'] if word['is_palindrome'] else 'DIFFERENT from original'}"
            ],
            answer=f"{'YES' if word['is_palindrome'] else 'NO'} - {word['word']} {'reads the same' if word['is_palindrome'] else 'does NOT read the same'} in mirror",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_both_symmetries(self) -> Question:
        """Find letters with BOTH symmetries."""
        letters = [
            {"letter": "H", "has_both": True},
            {"letter": "I", "has_both": True},
            {"letter": "X", "has_both": True},
            {"letter": "A", "has_both": False},
            {"letter": "M", "has_both": False},
        ]
        
        letter = random.choice(letters)
        
        # MCQ options
        correct_answer = f"{'YES' if letter['has_both'] else 'NO'} - '{letter['letter']}' {'has' if letter['has_both'] else 'does NOT have'} both symmetries"
        distractors = [
            f"{'NO' if letter['has_both'] else 'YES'} - All letters have both symmetries",
            "Only letters on horizontal axis can have both",
            "Both vertical and horizontal exist only in crosses"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Both Symmetries",
            logical_trap="Very few capital letters have BOTH vertical AND horizontal symmetry. Students often miss this distinction.",
            data_representation=f"```\nDual Symmetry Concept:\nVertical symmetry = Left and right halves mirror each other\nHorizontal symmetry = Top and bottom halves mirror each other\n\nA letter has BOTH if it looks the same when folded both ways.\nThis is VERY RARE among capital letters.\n```",
            question_text=f"Does the letter '{letter['letter']}' have BOTH vertical and horizontal symmetry?",
            solution_steps=[
                f"Checking '{letter['letter']}':",
                f"Vertical symmetry (left-right): {'YES' if letter['has_both'] else 'Check'},",
                f"Horizontal symmetry (top-bottom): {'YES' if letter['has_both'] else 'Check'},",
                f"Both symmetries present: {'YES' if letter['has_both'] else 'NO'}"
            ],
            answer=f"{'YES' if letter['has_both'] else 'NO'} - '{letter['letter']}' {'has' if letter['has_both'] else 'does NOT have'} both symmetries",
            options=options,
            correct_option_index=correct_idx
        )
        return question


class RotationGenerator(QuestionGenerator):
    """Generates rotation and direction problems."""
    
    def generate(self) -> Question:
        """Generate a rotation problem."""
        problem_type = random.choice(["quarter_turn", "half_turn", "direction_rotation"])
        
        if problem_type == "quarter_turn":
            return self._generate_quarter_turn()
        elif problem_type == "half_turn":
            return self._generate_half_turn()
        else:
            return self._generate_direction_rotation()
    
    def _generate_quarter_turn(self) -> Question:
        """Quarter turn rotation problems."""
        directions = [
            {"start": "North", "clockwise": "East", "counter": "West"},
            {"start": "East", "clockwise": "South", "counter": "North"},
            {"start": "South", "clockwise": "West", "counter": "East"},
            {"start": "West", "clockwise": "North", "counter": "South"},
        ]
        
        direction = random.choice(directions)
        rotation_dir = random.choice(["clockwise", "counter-clockwise"])
        result = direction["clockwise"] if rotation_dir == "clockwise" else direction["counter"]
        
        # MCQ options
        correct_answer = result
        wrong_turns = [k for k in direction.keys() if k != "start"]
        distractors = [d for d in ["North", "South", "East", "West"] if d != result][:3]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Quarter Turns",
            logical_trap="Students confuse clockwise with counter-clockwise. Clockwise = same direction as clock hands. Counter-clockwise = opposite.",
            data_representation=f"```\nCompass Reference:\nNorth (N) ↑\nEast (E) →\nSouth (S) ↓\nWest (W) ←\n\nRotation Rules:\nQuarter turn = 90° (one position)\nClockwise = Turn like clock hands\nCounter-clockwise = Opposite direction\n```",
            question_text=f"Starting facing {direction['start']}, if you make a quarter turn {rotation_dir}, which direction are you facing?",
            solution_steps=[
                f"Start facing: {direction['start']}",
                f"Quarter turn = 90° rotation",
                f"{rotation_dir.capitalize()} from {direction['start']}:",
                f"Follow the compass circle: {' → '.join([direction['start'], ('East' if rotation_dir == 'clockwise' else 'West')])}",
                f"After quarter turn: {result}"
            ],
            answer=result,
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_half_turn(self) -> Question:
        """Half turn (180°) rotation."""
        directions = {
            "North": "South",
            "East": "West",
            "South": "North",
            "West": "East"
        }
        
        start = random.choice(list(directions.keys()))
        result = directions[start]
        
        # MCQ options
        correct_answer = result
        distractors = [d for d in list(directions.keys()) if d != result]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Half Turns",
            logical_trap="A half turn is always the opposite direction, regardless of starting point. Students sometimes try to count steps.",
            data_representation=f"```\nHalf Turn Concept:\n180° = Complete reversal\n\nA half turn from any direction gives you the OPPOSITE direction.\n\nCompute using compass circle:\nCount 2 steps clockwise\nOr count 2 steps counter-clockwise\n```",
            question_text=f"If you face {start} and make a half turn, what direction are you facing?",
            solution_steps=[
                f"Start facing: {start}",
                f"Half turn = 180° = Complete reversal",
                f"Opposite of {start} = {result}",
                f"Therefore, you are facing {result}"
            ],
            answer=result,
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_direction_rotation(self) -> Question:
        """Multiple quarter turns."""
        times = random.randint(2, 4)
        total_degrees = times * 90
        
        # Calculate net rotation
        if total_degrees % 360 == 0:
            effect = "Complete spin (back to start)"
        elif total_degrees % 360 == 90:
            effect = "Quarter turn (one step clockwise)"
        elif total_degrees % 360 == 180:
            effect = "Half turn (opposite direction)"
        else:
            effect = "Three-quarter turn"
        
        # MCQ options
        correct_answer = f"{total_degrees}° total ({effect})"
        distractors = [
            f"{(times+1)*90}° total (Off by one turn)",
            f"{total_degrees // 2}° total (Half the actual)",
            f"{360}° total (Full circle)"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Shapes and Angles - Multiple Rotations",
            logical_trap="Students forget that rotations are cumulative and that 360° = full circle = back to start.",
            data_representation=f"```\nRotation Calculation:\n1 quarter turn = 90°\nTotal degrees = Number of turns × 90°\n\nReminder: 360° = Full circle = Back to start\nUse this to find the net effect.\n```",
            question_text=f"If you make {times} quarter turns (starting from any direction), what is the total rotation? Are you back where you started?",
            solution_steps=[
                f"Number of quarter turns: {times}",
                f"Degrees per quarter turn: 90°",
                f"Total rotation: {times} × 90° = {total_degrees}°",
                f"Net effect: {effect}"
            ],
            answer=f"{total_degrees}° total ({effect})",
            options=options,
            correct_option_index=correct_idx
        )
        return question


class LargeNumbersGenerator(QuestionGenerator):
    """Generates problems with large numbers, place value, and profit/loss in Indian system."""
    
    def generate(self) -> Question:
        """Generate a large numbers problem."""
        problem_type = random.choice(["place_value", "profit_loss", "unitary"])
        
        if problem_type == "place_value":
            return self._generate_place_value()
        elif problem_type == "profit_loss":
            return self._generate_profit_loss()
        else:
            return self._generate_unitary()
    
    def _generate_place_value(self) -> Question:
        """Place value in Indian numbering system (Lakh/Crore)."""
        scenarios = [
            {
                "number": 523468,
                "words": "Five lakh, twenty-three thousand, four hundred sixty-eight",
                "breakdown": "5 lakhs + 2 ten-thousands + 3 thousands + 4 hundreds + 6 tens + 8 ones"
            },
            {
                "number": 9876543,
                "words": "Ninety-eight lakh, seventy-six thousand, five hundred forty-three",
                "breakdown": "9 ten-lakhs + 8 lakhs + 7 ten-thousands + 6 thousands + 5 hundreds + 4 tens + 3 ones"
            },
            {
                "number": 1000000,
                "words": "Ten lakh (or 1 million)",
                "breakdown": "10 lakhs = 1 ten-lakh"
            }
        ]
        
        scenario = random.choice(scenarios)
        
        # MCQ options
        correct_answer = scenario['words']
        distractors = [
            scenario['words'].replace("lakh", "million"),  # Common mistake: using western system
            scenario['words'].replace("hundred", "thousand"),  # Wrong place value
            scenario['words'] + " (reading right to left instead of groups)"  # Wrong direction
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Number Systems - Large Numbers & Place Value",
            logical_trap="Students confuse the Indian system (Lakh/Crore) with the Western system (Million/Billion). 1 Lakh = 100,000, NOT 1 Million.",
            data_representation=f"```\nIndian Numbering System:\n1 Crore = 10 Lakhs = 1,00,00,000\n1 Lakh = 1,00,000\n1 Ten-thousand = 10,000\n\nPlace Value Positions (Right to Left):\nOnes, Tens, Hundreds, Thousands, Ten-thousands, Lakhs, Ten-lakhs, Crores\n```",
            question_text=f"What is the place value of each digit in {scenario['number']:,}? Express your answer in the Indian numbering system.",
            solution_steps=[
                f"Number: {scenario['number']:,}",
                f"Word form: {scenario['words']}",
                f"Breakdown: {scenario['breakdown']}",
                "This demonstrates the Indian place value system with Lakhs and Ten-lakhs"
            ],
            answer=scenario['words'],
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_profit_loss(self) -> Question:
        """Multi-step buying and selling with profit/loss calculation."""
        units = random.randint(500, 2000)
        cost_per_unit = random.choice([10, 12, 15, 20, 25])
        total_cost = units * cost_per_unit
        
        # Selling price with profit or loss
        profit_percent = random.choice([10, 15, 20, 25])
        loss_percent = random.choice([5, 10, 15])
        
        scenario_type = random.choice(["profit", "loss"])
        
        if scenario_type == "profit":
            sell_per_unit = cost_per_unit * (1 + profit_percent / 100)
            total_sell = units * sell_per_unit
            total_profit = total_sell - total_cost
            answer_value = int(total_profit)
            answer_text = f"₹{answer_value:,}"
        else:
            sell_per_unit = cost_per_unit * (1 - loss_percent / 100)
            total_sell = units * sell_per_unit
            total_loss = total_cost - total_sell
            answer_value = int(total_loss)
            answer_text = f"₹{answer_value:,}"
        
        # Create distractors
        wrong1 = answer_value + 1000
        wrong2 = answer_value - 1000
        wrong3 = int(total_cost * 0.1)  # 10% of cost (common mistake)
        
        options = [answer_text, f"₹{wrong1:,}", f"₹{wrong2:,}", f"₹{wrong3:,}"]
        random.shuffle(options)
        correct_idx = options.index(answer_text)
        
        question = Question(
            topic="Number Systems - Profit & Loss",
            logical_trap="Students forget to calculate TOTAL cost (quantity × price per unit) before computing profit/loss. They sometimes use only unit profit instead of total.",
            data_representation=f"```\nProfit & Loss Formula:\nProfit = Selling Price - Cost Price\nLoss = Cost Price - Selling Price\nProfit% = (Profit / Cost Price) × 100\n\nCost Breakdown:\n{units} units × ₹{cost_per_unit}/unit = ₹{total_cost:,}\n```",
            question_text=f"A merchant bought {units:,} kg of fish at ₹{cost_per_unit} per kg. He sold them at a {profit_percent if scenario_type == 'profit' else loss_percent}% {'profit' if scenario_type == 'profit' else 'loss'}. What is the total {'profit' if scenario_type == 'profit' else 'loss'}?",
            solution_steps=[
                f"Total Cost = {units:,} × ₹{cost_per_unit} = ₹{total_cost:,}",
                f"Selling price per unit = ₹{cost_per_unit} × (1 + {profit_percent if scenario_type == 'profit' else -loss_percent}%) = ₹{int(sell_per_unit)}" if scenario_type == "profit" else f"Selling price per unit = ₹{cost_per_unit} × (1 - {loss_percent}%) = ₹{int(sell_per_unit)}",
                f"Total Selling Price = {units:,} × ₹{int(sell_per_unit)} = ₹{int(total_sell):,}",
                f"{'Profit' if scenario_type == 'profit' else 'Loss'} = ₹{int(total_sell):,} - ₹{total_cost:,} = ₹{answer_value:,}"
            ],
            answer=answer_text,
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_unitary(self) -> Question:
        """Unitary method problem."""
        items = random.choice(["apples", "books", "meters of cloth", "kg of rice"])
        quantity = random.randint(5, 12)
        price_per_item = random.choice([10, 12, 15, 20, 25, 30])
        
        if random.choice([True, False]):
            # Given quantity, find cost
            query_qty = random.randint(quantity + 5, quantity + 15)
            answer_cost = query_qty * price_per_item
            answer_text = f"₹{answer_cost}"
            question_text = f"If {quantity} {items} cost ₹{quantity * price_per_item}, what is the cost of {query_qty} {items}?"
            
            # MCQ options
            wrong1 = str(answer_cost + 100)
            wrong2 = str(answer_cost - 100)
            wrong3 = str(query_qty * (price_per_item - 2))
            options = [answer_text, f"₹{wrong1}", f"₹{wrong2}", f"₹{wrong3}"]
        else:
            # Given cost, find quantity
            total_cost = random.randint(200, 500)
            query_qty = total_cost // price_per_item
            answer_text = f"{query_qty} {items}"
            question_text = f"If {quantity} {items} cost ₹{quantity * price_per_item}, how many {items} can you buy for ₹{total_cost}?"
            
            # MCQ options
            wrong1 = str(query_qty + 1)
            wrong2 = str(query_qty - 1)
            wrong3 = str(total_cost // (price_per_item + 2))
            options = [answer_text, f"{wrong1} {items}", f"{wrong2} {items}", f"{wrong3} {items}"]
        
        random.shuffle(options)
        correct_idx = options.index(answer_text)
        
        question = Question(
            topic="Number Systems - Unitary Method",
            logical_trap="Students confuse which quantity to divide and which to multiply. Always find the cost/quantity of ONE unit first.",
            data_representation=f"```\nUnitary Method Steps:\n1. Find the cost/quantity of ONE unit\n2. Multiply by the desired quantity\n\nGiven: {quantity} {items} = ₹{quantity * price_per_item}\nFind: Cost per item = ₹{quantity * price_per_item} ÷ {quantity} = ₹{price_per_item}\n```",
            question_text=question_text,
            solution_steps=[
                f"Cost of {quantity} {items} = ₹{quantity * price_per_item}",
                f"Cost of 1 item = ₹{quantity * price_per_item} ÷ {quantity} = ₹{price_per_item}",
                f"Cost/Quantity of {query_qty if 'cost' in question_text.lower() else total_cost} = {query_qty if 'cost' in question_text.lower() else total_cost} × ₹{price_per_item}" if "cost" in question_text.lower() else f"Quantity = ₹{total_cost} ÷ ₹{price_per_item} = {query_qty}"
            ],
            answer=answer_text,
            options=options,
            correct_option_index=correct_idx
        )
        return question


class FactorsMultiplesGenerator(QuestionGenerator):
    """Generates HCF/LCM problems in real-world contexts."""
    
    def generate(self) -> Question:
        """Generate a factors/multiples problem."""
        problem_type = random.choice(["hcf_real", "lcm_real", "divisibility"])
        
        if problem_type == "hcf_real":
            return self._generate_hcf()
        elif problem_type == "lcm_real":
            return self._generate_lcm()
        else:
            return self._generate_divisibility()
    
    def _generate_hcf(self) -> Question:
        """HCF (GCD) in real-world grouping scenarios."""
        scenarios = [
            {"num1": 24, "num2": 36, "item": "students", "context": "divided into groups"},
            {"num1": 48, "num2": 60, "item": "chocolates", "context": "distributed equally"},
            {"num1": 32, "num2": 40, "item": "books", "context": "arranged in stacks"}
        ]
        
        scenario = random.choice(scenarios)
        num1, num2 = scenario["num1"], scenario["num2"]
        
        # Calculate HCF
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        hcf = gcd(num1, num2)
        
        # MCQ options
        correct_answer = f"{hcf} {scenario['item']} per group"
        distractors = [
            f"{num1} {scenario['item']} per group (No grouping done)",
            f"{hcf * 2} {scenario['item']} per group (Doubled HCF)",
            f"{(num1 * num2) // hcf} {scenario['item']} per group (Confused with LCM)"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Factors & Multiples - HCF (Highest Common Factor)",
            logical_trap="Students find LCM instead of HCF. HCF is the LARGEST number that divides BOTH. It's the 'largest group size' not the 'total after combining.'",
            data_representation=f"```\nFinding HCF:\n1. List factors of {num1}: 1, ..., {num1}\n2. List factors of {num2}: 1, ..., {num2}\n3. Find COMMON factors (appear in both lists)\n4. The HIGHEST common factor is the HCF\n\nMethod: Divide repeatedly by common divisors\n```",
            question_text=f"You have {num1} {scenario['item']} and {num2} other {scenario['item']} that need to be {scenario['context']} into the largest equal groups. How many {scenario['item']} will be in each group?",
            solution_steps=[
                f"Need to find the largest number that divides both {num1} and {num2}",
                f"Factors of {num1}: {', '.join(str(i) for i in range(1, num1 + 1) if num1 % i == 0)}",
                f"Factors of {num2}: {', '.join(str(i) for i in range(1, num2 + 1) if num2 % i == 0)}",
                f"Common factors: {', '.join(str(i) for i in range(1, hcf + 1) if num1 % i == 0 and num2 % i == 0)}",
                f"HCF (Highest Common Factor) = {hcf}"
            ],
            answer=f"{hcf} {scenario['item']} per group",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_lcm(self) -> Question:
        """LCM in periodic/timing scenarios."""
        scenarios = [
            {"num1": 12, "num2": 15, "item": "seconds", "object": "traffic lights", "context": "change together"},
            {"num1": 10, "num2": 12, "item": "laps", "object": "runners", "context": "meet at the starting point"},
            {"num1": 8, "num2": 6, "item": "hours", "object": "bells", "context": "toll together"}
        ]
        
        scenario = random.choice(scenarios)
        num1, num2 = scenario["num1"], scenario["num2"]
        
        # Calculate LCM
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        def lcm(a, b):
            return (a * b) // gcd(a, b)
        
        lcm_value = lcm(num1, num2)
        
        # MCQ options
        correct_answer = f"{lcm_value} {scenario['item']}"
        distractors = [
            f"{max(num1, num2)} {scenario['item']} (Chose larger number)",
            f"{num1 * num2} {scenario['item']} (Just multiplied)",
            f"{gcd(num1, num2)} {scenario['item']} (Confused with HCF)"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Factors & Multiples - LCM (Least Common Multiple)",
            logical_trap="Students confuse LCM with HCF. LCM is the SMALLEST number divisible by BOTH. It's 'when will they meet/repeat together', not 'how to split them equally.'",
            data_representation=f"```\nFinding LCM:\n1. List multiples of {num1}: {num1}, {2*num1}, {3*num1}, ...\n2. List multiples of {num2}: {num2}, {2*num2}, {3*num2}, ...\n3. Find the SMALLEST number in BOTH lists\n\nLCM = (num1 × num2) / HCF\n```",
            question_text=f"Two {scenario['object']} {scenario['context']}. One changes every {num1} {scenario['item']}, the other every {num2} {scenario['item']}. After how many {scenario['item']} will they {scenario['context']}?",
            solution_steps=[
                f"Find the LCM of {num1} and {num2}",
                f"Multiples of {num1}: {', '.join(str(num1*i) for i in range(1, lcm_value//num1 + 1))}",
                f"Multiples of {num2}: {', '.join(str(num2*i) for i in range(1, lcm_value//num2 + 1))}",
                f"LCM (smallest common multiple) = {lcm_value}"
            ],
            answer=f"{lcm_value} {scenario['item']}",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_divisibility(self) -> Question:
        """Divisibility rules and finding remainders."""
        rules = [
            {"divisor": 2, "rule": "A number is divisible by 2 if its last digit is even (0, 2, 4, 6, 8)"},
            {"divisor": 5, "rule": "A number is divisible by 5 if its last digit is 0 or 5"},
            {"divisor": 10, "rule": "A number is divisible by 10 if its last digit is 0"},
            {"divisor": 3, "rule": "A number is divisible by 3 if the sum of its digits is divisible by 3"}
        ]
        
        rule = random.choice(rules)
        
        if rule["divisor"] == 3:
            # Generate number where sum of digits is divisible by 3
            num = random.choice([123, 234, 345, 456, 567, 678, 789, 891, 912])
            digit_sum = sum(int(d) for d in str(num))
            divisible = digit_sum % 3 == 0
        else:
            num = random.randint(100, 999)
            divisible = num % rule["divisor"] == 0
        
        # MCQ options
        correct_answer = f"{'YES' if divisible else 'NO'}, {num} is {'divisible' if divisible else 'NOT divisible'} by {rule['divisor']}"
        distractors = [
            f"{'NO' if divisible else 'YES'}, {num} is {'divisible' if not divisible else 'NOT divisible'} by {rule['divisor']}",
            "Need to calculate to know",
            "Divisibility rules don't work for all numbers"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Factors & Multiples - Divisibility Rules",
            logical_trap="Students try to divide every number instead of applying the quick divisibility rules. This tests understanding, not calculation.",
            data_representation=f"```\nDivisibility Rules Quick Reference:\nBy 2: Last digit is even\nBy 5: Last digit is 0 or 5\nBy 10: Last digit is 0\nBy 3: Sum of digits is divisible by 3\nBy 9: Sum of digits is divisible by 9\n```",
            question_text=f"Is {num} divisible by {rule['divisor']}? Use the divisibility rule, don't just divide.",
            solution_steps=[
                f"Rule for divisibility by {rule['divisor']}: {rule['rule']}",
                f"Checking {num}..." if rule["divisor"] != 3 else f"Checking {num}: Sum of digits = {' + '.join(str(d) for d in str(num))} = {digit_sum}",
                f"{'YES' if divisible else 'NO'}, {num} is {'divisible' if divisible else 'NOT divisible'} by {rule['divisor']}"
            ],
            answer=f"{'YES' if divisible else 'NO'} - {num} is {'divisible' if divisible else 'not divisible'} by {rule['divisor']}",
            options=options,
            correct_option_index=correct_idx
        )
        return question


class FractionsDecimalsGenerator(QuestionGenerator):
    """Generates fraction and decimal problems with the 'remaining' trap."""
    
    def generate(self) -> Question:
        """Generate a fractions/decimals problem."""
        problem_type = random.choice(["remaining_trap", "equivalent", "decimal_money", "visual"])
        
        if problem_type == "remaining_trap":
            return self._generate_remaining_trap()
        elif problem_type == "equivalent":
            return self._generate_equivalent()
        elif problem_type == "decimal_money":
            return self._generate_decimal_money()
        else:
            return self._generate_visual_fractions()
    
    def _generate_remaining_trap(self) -> Question:
        """The classic K.C. Nag trap: operations on remaining amounts."""
        total_amount = random.choice([500, 600, 800, 1000, 1200])
        
        # First fraction
        frac1_num = random.choice([1, 2, 3])
        frac1_den = random.choice([4, 5, 6])
        first_spend = (frac1_num / frac1_den) * total_amount
        remaining = total_amount - first_spend
        
        # Second fraction of REMAINING (not original)
        frac2_num = random.choice([1, 2])
        frac2_den = random.choice([3, 4, 5])
        second_spend = (frac2_num / frac2_den) * remaining
        final_remaining = remaining - second_spend
        
        # MCQ options
        correct_answer = f"₹{int(final_remaining)}"
        # Common trap: using second fraction on original
        trap_answer = total_amount - first_spend - (frac2_num / frac2_den) * total_amount
        
        distractors = [
            f"₹{int(trap_answer)}",
            f"₹{int(remaining)}",
            f"₹{int(first_spend + second_spend)}"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Fractions & Decimals - Fractional Spending (The Remaining Trap)",
            logical_trap="Students spend 1/4 and then 1/5 of the ORIGINAL amount, NOT the REMAINING amount. This is THE K.C. Nag differentiator.",
            data_representation=f"```\nStep-by-step spending problem:\nStart with: ₹{int(total_amount)}\nFirst spend: {frac1_num}/{frac1_den} of original\nSecond spend: {frac2_num}/{frac2_den} of REMAINING (not original)\n\nFormula:\nAmount remaining after first = Original - (Fraction × Original)\nAmount remaining after second = Remaining - (Fraction × Remaining)\n```",
            question_text=f"Ram had ₹{int(total_amount)}. He spent {frac1_num}/{frac1_den} of it on books. Of the REMAINING money, he spent {frac2_num}/{frac2_den} on food. How much money does he have left?",
            solution_steps=[
                f"Starting amount: ₹{int(total_amount)}",
                f"Spent on books: {frac1_num}/{frac1_den} × ₹{int(total_amount)} = ₹{int(first_spend)}",
                f"Remaining after books: ₹{int(total_amount)} - ₹{int(first_spend)} = ₹{int(remaining)}",
                f"Spent on food: {frac2_num}/{frac2_den} × ₹{int(remaining)} = ₹{int(second_spend)} (NOTE: This is {frac2_num}/{frac2_den} of REMAINING, not original)",
                f"Final remaining: ₹{int(remaining)} - ₹{int(second_spend)} = ₹{int(final_remaining)}"
            ],
            answer=f"₹{int(final_remaining)}",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_equivalent(self) -> Question:
        """Equivalent fractions: find the missing number."""
        base_num = random.randint(1, 5)
        base_den = random.randint(base_num + 1, 10)
        multiplier = random.randint(2, 5)
        
        scenario = random.choice(["find_numerator", "find_denominator"])
        
        if scenario == "find_numerator":
            given_den = base_den * multiplier
            answer_num = base_num * multiplier
            question_text = f"Find x: {base_num}/{base_den} = x/{given_den}"
        else:
            given_num = base_num * multiplier
            answer_den = base_den * multiplier
            question_text = f"Find x: {base_num}/{base_den} = {given_num}/x"
        
        # MCQ options
        correct_answer = f"x = {answer_num if scenario == 'find_numerator' else answer_den}"
        distractors = [
            f"x = {answer_num + 1 if scenario == 'find_numerator' else answer_den + 1}",
            f"x = {(answer_num if scenario == 'find_numerator' else answer_den) * 2}",
            f"x = {base_num if scenario == 'find_numerator' else base_den}"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Fractions & Decimals - Equivalent Fractions",
            logical_trap="Students think multiplying only the numerator makes equivalent fractions. You must multiply BOTH numerator AND denominator by the same number.",
            data_representation=f"```\nEquivalent Fractions Rule:\n{base_num}/{base_den} = ({base_num} × k) / ({base_den} × k)\n\nEach side of the fraction MUST be multiplied by the SAME number.\n\nExample:\n{base_num}/{base_den} = {base_num * 2}/{base_den * 2} = {base_num * 3}/{base_den * 3}\n```",
            question_text=question_text,
            solution_steps=[
                f"Equivalent fractions have the same value",
                f"To find the pattern: Check what {base_num}/{base_den} was multiplied by",
                f"If {base_num} → {answer_num if scenario == 'find_numerator' else given_num}, then multiply by {multiplier}",
                f"Apply the same multiplier to both: {base_num} × {multiplier} = {answer_num if scenario == 'find_numerator' else given_num}, and {base_den} × {multiplier} = {answer_den if scenario == 'find_denominator' else given_den}"
            ],
            answer=f"x = {answer_num if scenario == 'find_numerator' else answer_den}",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_decimal_money(self) -> Question:
        """Decimals with mixed units: Rupees and Paise."""
        # Amount in Rupees (as decimal)
        rupees = random.randint(10, 50)
        paise = random.choice([0.10, 0.25, 0.50, 0.75])
        total_amount = rupees + paise
        
        # Number of items
        num_items = random.randint(5, 12)
        cost_per_item = total_amount / num_items
        
        # MCQ options
        correct_answer = f"₹{cost_per_item:.2f} per item"
        distractors = [
            f"₹{cost_per_item + 0.5:.2f} per item",
            f"₹{cost_per_item - 0.1:.2f} per item",
            f"₹{total_amount:.2f} per item (No division)"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Fractions & Decimals - Money & Decimals (Rupees & Paise)",
            logical_trap="Students forget that 100 paise = 1 Rupee. They might write ₹10.100 instead of converting properly.",
            data_representation=f"```\nMoney Conversion:\n100 paise = 1 Rupee\n1 Rupee = ₹1.00\n1 Paise = ₹0.01\n\nExample:\n₹10.50 = 10 Rupees + 50 Paise\n₹5.25 = 5 Rupees + 25 Paise\n```",
            question_text=f"A shopkeeper has ₹{rupees}.{int(paise * 100):02d}. She buys {num_items} equal items. What is the cost of each item (in ₹)?",
            solution_steps=[
                f"Total money: ₹{rupees} + ₹{paise:.2f} = ₹{total_amount:.2f}",
                f"Number of items: {num_items}",
                f"Cost per item: ₹{total_amount:.2f} ÷ {num_items} = ₹{cost_per_item:.2f}"
            ],
            answer=f"₹{cost_per_item:.2f} per item",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_visual_fractions(self) -> Question:
        """Visual fraction problem on a grid."""
        grid_size = random.choice([4, 5, 6])
        total_squares = grid_size * grid_size
        
        colored = random.randint(5, total_squares - 3)
        uncolored = total_squares - colored
        
        from math import gcd
        g = gcd(uncolored, total_squares)
        answer_num = uncolored // g
        answer_den = total_squares // g
        correct_answer = f"{answer_num}/{answer_den}"
        
        # MCQ options
        distractors = [
            f"{uncolored}/{colored}",  # Inverted fraction
            f"{colored}/{total_squares}",  # Colored instead of uncolored
            f"{answer_num}/{answer_den + 1}"  # Off by 1
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Fractions & Decimals - Visual Fractions on Grids",
            logical_trap="Students count the colored squares but don't identify the fraction correctly. They might say 'colored is 6' instead of '6/25 is colored'.",
            data_representation=f"```\nVisual Grid Problem:\n{grid_size} × {grid_size} grid = {total_squares} total squares\n\n[Imagine {colored} squares colored, {uncolored} squares uncolored]\n\nFraction colored: {colored}/{total_squares}\nFraction uncolored: {uncolored}/{total_squares}\n```",
            question_text=f"A {grid_size}×{grid_size} grid has {colored} colored squares and {uncolored} uncolored squares. What fraction of the grid is uncolored?",
            solution_steps=[
                f"Total squares in grid: {grid_size} × {grid_size} = {total_squares}",
                f"Uncolored squares: {uncolored}",
                f"Fraction uncolored: {uncolored}/{total_squares}",
                f"Simplify: {uncolored}/{total_squares} = {answer_num}/{answer_den}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        return question


class GeometryMeasurementGenerator(QuestionGenerator):
    """Generates geometry and measurement problems: Area vs Perimeter, Volume, Maps, Conversions."""
    
    def generate(self) -> Question:
        """Generate a geometry/measurement problem."""
        problem_type = random.choice(["fencing_vs_tiling", "volume", "map_scale", "conversions"])
        
        if problem_type == "fencing_vs_tiling":
            return self._generate_fencing_vs_tiling()
        elif problem_type == "volume":
            return self._generate_volume()
        elif problem_type == "map_scale":
            return self._generate_map_scale()
        else:
            return self._generate_conversions()
    
    def _generate_fencing_vs_tiling(self) -> Question:
        """Perimeter (fencing cost) vs Area (tiling cost)."""
        area = random.choice([24, 36, 48])
        
        # Find two rectangular dimensions
        factor_pairs = []
        for i in range(1, int(area**0.5) + 1):
            if area % i == 0:
                factor_pairs.append((i, area // i))
        
        length, width = random.choice(factor_pairs)
        perimeter = 2 * (length + width)
        
        fencing_cost_per_meter = random.choice([50, 75, 100])
        tiling_cost_per_sqm = random.choice([200, 250, 300])
        
        fencing_total = perimeter * fencing_cost_per_meter
        tiling_total = area * tiling_cost_per_sqm
        
        question_type = random.choice(["fencing", "tiling"])
        
        if question_type == "fencing":
            correct_answer = f"₹{int(fencing_total)}"
            question_text = f"A rectangular field is {length}m long and {width}m wide. Fencing costs ₹{fencing_cost_per_meter} per meter. What is the total cost to fence the entire field?"
            distractors = [f"₹{int(tiling_total)}", f"₹{int(fencing_total + 1000)}", f"₹{int(fencing_total * 2)}"]
        else:
            correct_answer = f"₹{int(tiling_total)}"
            question_text = f"A rectangular field is {length}m long and {width}m wide. Tiles cost ₹{tiling_cost_per_sqm} per square meter. What is the total cost to tile the entire field?"
            distractors = [f"₹{int(fencing_total)}", f"₹{int(tiling_total - 500)}", f"₹{int(tiling_total // 2)}"]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Geometry & Measurement - Fencing (Perimeter) vs Tiling (Area)",
            logical_trap="Students confuse PERIMETER (Fencing) with AREA (Tiling). Perimeter = around the edges. Area = inside the shape. For the same area, different rectangles have different perimeters.",
            data_representation=f"```\nKey Difference:\nPerimeter = Total distance AROUND the shape (for fencing)\nArea = Total space INSIDE the shape (for tiling/painting)\n\nFor a {length}m × {width}m rectangle:\nPerimeter = 2 × ({length} + {width}) = {perimeter}m\nArea = {length} × {width} = {area} sq m\n```",
            question_text=question_text,
            solution_steps=[
                f"Field dimensions: {length}m × {width}m",
                f"{'Perimeter' if question_type == 'fencing' else 'Area'} = {'2 × (' + str(length) + ' + ' + str(width) + ') = ' + str(perimeter) + 'm' if question_type == 'fencing' else str(length) + ' × ' + str(width) + ' = ' + str(area) + ' sq m'}",
                f"Cost per {'meter' if question_type == 'fencing' else 'sq m'}: ₹{fencing_cost_per_meter if question_type == 'fencing' else tiling_cost_per_sqm}",
                f"Total cost = {perimeter if question_type == 'fencing' else area} × ₹{fencing_cost_per_meter if question_type == 'fencing' else tiling_cost_per_sqm} = ₹{int(fencing_total if question_type == 'fencing' else tiling_total)}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_volume(self) -> Question:
        """Volume problem: Packing cubes in a box."""
        box_length = random.choice([10, 12, 15, 20])
        box_width = random.choice([10, 12, 15, 20])
        box_height = random.choice([4, 6, 8, 10])
        
        cube_size = random.choice([2, 3, 4])
        
        # Calculate how many cubes fit
        cubes_along_length = box_length // cube_size
        cubes_along_width = box_width // cube_size
        cubes_along_height = box_height // cube_size
        total_cubes = cubes_along_length * cubes_along_width * cubes_along_height
        
        # MCQ options
        correct_answer = str(total_cubes)
        box_volume = box_length * box_width * box_height
        cube_volume = cube_size ** 3
        wrong1 = str(box_volume // cube_volume)  # Volume method (may or may not match)
        wrong2 = str(total_cubes + 5)  # Off by a few
        wrong3 = str(cubes_along_length * cubes_along_width)  # Forgot height dimension
        
        options = [correct_answer, wrong1, wrong2, wrong3]
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Geometry & Measurement - Volume & Cube Packing",
            logical_trap="Students calculate the volume of the box and divide by the volume of one cube. This only works if cubes pack PERFECTLY with no gaps or overlap.",
            data_representation=f"```\nCube Packing Logic:\nBox dimensions: {box_length}cm × {box_width}cm × {box_height}cm\nCube size: {cube_size}cm × {cube_size}cm × {cube_size}cm\n\nNumber of cubes along each dimension:\nLength: {box_length} ÷ {cube_size} = {cubes_along_length}\nWidth: {box_width} ÷ {cube_size} = {cubes_along_width}\nHeight: {box_height} ÷ {cube_size} = {cubes_along_height}\n```",
            question_text=f"How many {cube_size}cm × {cube_size}cm × {cube_size}cm sugar cubes can fit into a box measuring {box_length}cm × {box_width}cm × {box_height}cm?",
            solution_steps=[
                f"Box volume: {box_length} × {box_width} × {box_height} = {box_length * box_width * box_height} cubic cm",
                f"Cube volume: {cube_size} × {cube_size} × {cube_size} = {cube_size**3} cubic cm",
                f"Cubes along length: {box_length} ÷ {cube_size} = {cubes_along_length}",
                f"Cubes along width: {box_width} ÷ {cube_size} = {cubes_along_width}",
                f"Cubes along height: {box_height} ÷ {cube_size} = {cubes_along_height}",
                f"Total cubes: {cubes_along_length} × {cubes_along_width} × {cubes_along_height} = {total_cubes}"
            ],
            answer=str(total_cubes),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_map_scale(self) -> Question:
        """Map scale problem using grid logic."""
        map_distance = random.randint(5, 20)
        scale_km = random.choice([1, 2, 5])
        
        actual_distance = map_distance * scale_km
        
        # MCQ options
        correct_answer = f"{actual_distance}km"
        distractors = [
            f"{map_distance}km (Forgot to apply scale)",
            f"{actual_distance + 10}km (Off by 10)",
            f"{actual_distance * 2}km (Multiplied twice)"
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Geometry & Measurement - Map Scaling & Coordinates",
            logical_trap="Students confuse 'map distance' with 'actual distance.' They forget to apply the scale factor. If 1cm = 5km, then 10cm = 50km, NOT 10km.",
            data_representation=f"```\nMap Scale Logic:\nScale means: 1 unit on map = X units in reality\n\nIf scale is 1cm = {scale_km}km:\n1cm map = {scale_km}km actual\n2cm map = {2*scale_km}km actual\n{map_distance}cm map = {map_distance * scale_km}km actual\n```",
            question_text=f"On a map, the distance between School and Park is {map_distance}cm. The scale of the map is 1cm = {scale_km}km. What is the actual distance between the School and Park?",
            solution_steps=[
                f"Map distance: {map_distance}cm",
                f"Map scale: 1cm = {scale_km}km",
                f"Actual distance = Map distance × Scale",
                f"Actual distance = {map_distance} × {scale_km} = {actual_distance}km"
            ],
            answer=f"{actual_distance}km",
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_conversions(self) -> Question:
        """Unit conversions: mg, g, kg in same problem."""
        scenarios = [
            {"item": "medicine tablet", "qty_mg": 500, "need_g": True},
            {"item": "flour", "qty_g": 750, "need_kg": True},
            {"item": "weight", "qty_kg": 2, "qty_g": 500, "combine": True}
        ]
        
        scenario = random.choice(scenarios)
        
        if scenario.get("need_g"):
            # Convert mg to g
            answer_g = scenario["qty_mg"] / 1000
            question_text = f"A medicine tablet contains {scenario['qty_mg']}mg of medicine. How many grams is this?"
            answer_text = f"{answer_g}g"
            steps = [
                f"Given: {scenario['qty_mg']}mg",
                f"Conversion: 1g = 1000mg, so 1mg = 1/1000 g",
                f"Therefore: {scenario['qty_mg']}mg = {scenario['qty_mg']} ÷ 1000 = {answer_g}g"
            ]
            # MCQ options
            wrong1 = f"{scenario['qty_mg'] / 100}g"
            wrong2 = f"{scenario['qty_mg'] * 1000}g"
            wrong3 = f"{answer_g + 0.1}g"
        elif scenario.get("need_kg"):
            # Convert g to kg
            answer_kg = scenario["qty_g"] / 1000
            question_text = f"A recipe needs {scenario['qty_g']}g of flour. How many kilograms is this?"
            answer_text = f"{answer_kg}kg"
            steps = [
                f"Given: {scenario['qty_g']}g",
                f"Conversion: 1kg = 1000g",
                f"Therefore: {scenario['qty_g']}g = {scenario['qty_g']} ÷ 1000 = {answer_kg}kg"
            ]
            # MCQ options
            wrong1 = f"{scenario['qty_g'] / 100}kg"
            wrong2 = f"{scenario['qty_g'] * 1000}kg"
            wrong3 = f"{answer_kg + 0.1}kg"
        else:
            # Combine kg and g
            total_g = scenario["qty_kg"] * 1000 + scenario["qty_g"]
            total_kg = total_g / 1000
            question_text = f"Add {scenario['qty_kg']}kg and {scenario['qty_g']}g. Express the answer in kilograms."
            answer_text = f"{total_kg}kg"
            steps = [
                f"Given: {scenario['qty_kg']}kg + {scenario['qty_g']}g",
                f"{scenario['qty_kg']}kg = {scenario['qty_kg'] * 1000}g",
                f"Total: {scenario['qty_kg'] * 1000}g + {scenario['qty_g']}g = {total_g}g",
                f"Convert back: {total_g}g = {total_g} ÷ 1000 = {total_kg}kg"
            ]
            # MCQ options
            wrong1 = f"{scenario['qty_kg']}kg (Ignored the grams)"
            wrong2 = f"{total_kg + 0.5}kg"
            wrong3 = f"{scenario['qty_kg'] + scenario['qty_g']/100}kg"
        
        options = [answer_text, wrong1, wrong2, wrong3]
        random.shuffle(options)
        correct_idx = options.index(answer_text)
        
        question = Question(
            topic="Geometry & Measurement - Unit Conversions (mg, g, kg)",
            logical_trap="Students forget the conversion factors. They might multiply by 1000 when they should divide, or vice versa. Reminder: mg→g→kg (divide by 1000 each step).",
            data_representation=f"```\nUnit Conversion Chart:\n1 kilogram (kg) = 1000 grams (g)\n1 gram (g) = 1000 milligrams (mg)\n\nDirection matters:\nSmaller to larger unit → DIVIDE\nLarger to smaller unit → MULTIPLY\n```",
            question_text=question_text,
            solution_steps=steps,
            answer=answer_text,
            options=options,
            correct_option_index=correct_idx
        )
        return question


class DataPatternsGenerator(QuestionGenerator):
    """Generates data, patterns, and missing data problems."""
    
    def generate(self) -> Question:
        """Generate a data/pattern problem."""
        problem_type = random.choice(["pattern_sequence", "missing_table", "scale_pictograph"])
        
        if problem_type == "pattern_sequence":
            return self._generate_pattern_sequence()
        elif problem_type == "missing_table":
            return self._generate_missing_table()
        else:
            return self._generate_scale_pictograph()
    
    def _generate_pattern_sequence(self) -> Question:
        """Complete number patterns (squares, triangular numbers)."""
        pattern_type = random.choice(["square", "triangular", "fibonacci_simple"])
        
        if pattern_type == "square":
            # 1, 4, 9, 16, 25, ...
            position = random.randint(5, 8)
            answer = position ** 2
            sequence = [i**2 for i in range(1, 6)]
            rule = "Each number is a perfect square (n²)"
        elif pattern_type == "triangular":
            # 1, 3, 6, 10, 15, ...
            position = random.randint(5, 7)
            answer = (position * (position + 1)) // 2
            sequence = [(i * (i + 1)) // 2 for i in range(1, 6)]
            rule = "Each number is triangular (1 + 2 + 3 + ... + n)"
        else:
            # 1, 1, 2, 3, 5, 8, 13, ...
            position = random.randint(6, 8)
            seq = [1, 1]
            for _ in range(10):
                seq.append(seq[-1] + seq[-2])
            answer = seq[position - 1]
            sequence = seq[:6]
            rule = "Each number is the sum of the previous two"
        
        # MCQ options
        correct_answer = str(answer)
        distractors = [
            str(answer + 5),
            str(answer - 5),
            str(position * 10)
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Data & Patterns - Number Sequences",
            logical_trap="Students try simple addition (+2 or +3) instead of recognizing the actual pattern. This tests logic, not calculation.",
            data_representation=f"```\nPattern Type: {pattern_type.upper()}\nSequence start: {', '.join(map(str, sequence))}\nRule: {rule}\n\nTo find the next term, apply the rule consistently.\n```",
            question_text=f"Find the {position}th number in the pattern: {', '.join(map(str, sequence))}, ...",
            solution_steps=[
                f"Sequence: {', '.join(map(str, sequence))}",
                f"Rule: {rule}",
                f"Position {position}: {answer}"
            ],
            answer=str(answer),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_missing_table(self) -> Question:
        """Find missing data given total and other values."""
        categories = random.choice([
            ["Student A", "Student B", "Student C", "Student D"],
            ["Week 1", "Week 2", "Week 3", "Week 4"]
        ])
        
        total = random.choice([150, 200, 250])
        values = [random.randint(30, 70) for _ in range(len(categories) - 1)]
        missing_value = total - sum(values)
        missing_idx = random.randint(0, len(categories) - 1)
        
        # Build table
        table = "| Category | Value |\n|----------|-------|\n"
        display_values = values[:missing_idx] + [None] + values[missing_idx:]
        for i, cat in enumerate(categories):
            if display_values[i] is None:
                table += f"| {cat} | ? |\n"
            else:
                table += f"| {cat} | {display_values[i]} |\n"
        table += f"| **TOTAL** | **{total}** |\n"
        
        # MCQ options
        correct_answer = str(missing_value)
        distractors = [
            str(missing_value + 10),
            str(missing_value - 10),
            str(total - sum(values) + 20)
        ]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Data & Patterns - Missing Data in Tables",
            logical_trap="Students add the visible numbers and then try to find the missing value. They must use the total as a constraint.",
            data_representation=table,
            question_text=f"The table shows data for {len(categories)} categories. The total is {total}. Find the missing value for {categories[missing_idx]}.",
            solution_steps=[
                f"Sum of known values: {' + '.join(map(str, [v for v in display_values if v is not None]))} = {sum(values)}",
                f"Total = {total}",
                f"Missing value = {total} - {sum(values)} = {missing_value}"
            ],
            answer=str(missing_value),
            options=options,
            correct_option_index=correct_idx
        )
        return question
    
    def _generate_scale_pictograph(self) -> Question:
        """Pictograph with non-unitary scale."""
        scale_value = random.choice([5, 10, 12, 15])
        items = ["Apples", "Bananas", "Oranges"]
        
        symbol_counts = {item: random.randint(2, 5) for item in items}
        actual_counts = {item: symbol_counts[item] * scale_value for item in items}
        
        query_item = random.choice(items)
        
        table = f"| Fruit | Icons (1 🍎 = {scale_value} fruits) | Actual Count |\n"
        table += "|-------|---------------------------------------|---------------|\n"
        for item in items:
            icons = "🍎" * symbol_counts[item]
            table += f"| {item} | {icons} | {actual_counts[item]} |\n"
        
        # MCQ options
        correct_answer = f"{actual_counts[query_item]}"
        count_only = str(symbol_counts[query_item])  # Just counting icons
        wrong_scale = str(symbol_counts[query_item] * (scale_value // 2))  # Wrong scale
        wrong_other = str(actual_counts[[i for i in items if i != query_item][0]])  # Different item
        
        options = [correct_answer, count_only, wrong_scale, wrong_other]
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            topic="Data & Patterns - Pictographs with Non-Unitary Scale",
            logical_trap="Students count the icons (e.g., 3 icons) instead of multiplying by the scale (e.g., 3 × 10 = 30 fruits). The scale is crucial!",
            data_representation=table,
            question_text=f"The pictograph shows fruits sold. 1 icon = {scale_value} fruits. How many {query_item.lower()} were sold?",
            solution_steps=[
                f"Number of icons for {query_item}: {symbol_counts[query_item]}",
                f"Scale: 1 icon = {scale_value} fruits",
                f"Actual count = {symbol_counts[query_item]} × {scale_value} = {actual_counts[query_item]} fruits"
            ],
            answer=f"{actual_counts[query_item]}",
            options=options,
            correct_option_index=correct_idx
        )
        return question


def main():
    """Main function to generate and display questions."""
    generators: List[QuestionGenerator] = [
        DiceLogicGenerator(),
        CubeCountingGenerator(),
        NetsGenerator(),
        DataHandlingGenerator(),
        ClockAnglesGenerator(),
        SymmetryGenerator(),
        RotationGenerator(),
        LargeNumbersGenerator(),
        FactorsMultiplesGenerator(),
        FractionsDecimalsGenerator(),
        GeometryMeasurementGenerator(),
        DataPatternsGenerator()
    ]
    
    print("=" * 80)
    print("CBSE CLASS 5 MATHEMATICS - STRICT LOGIC-BASED QUESTION GENERATOR")
    print("K.C. Nag Style (Comprehensive Coverage: All 7 Chapter Modules)")
    print("=" * 80)
    print()
    
    # Generate 2 questions from each category
    for generator in generators:
        for i in range(2):
            question = generator.generate()
            print(question.format_output())
            print()


if __name__ == "__main__":
    main()
