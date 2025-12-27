"""Strategy for Geometry & Measurement questions.

Covers:
- Fencing (Perimeter) vs Tiling (Area)
- Volume and cube packing
- Map scaling and coordinates
- Unit conversions (mg, g, kg)
"""

import random
from models.question import Question, ChapterEnum
from strategies.base import BaseChapterStrategy


class GeometryMeasurementStrategy(BaseChapterStrategy):
    """Generates geometry and measurement problems."""

    chapter = ChapterEnum.GEOMETRY_MEASUREMENT
    chapter_name = "Geometry & Measurement"
    description = "Geometry, area, perimeter, volume, map scaling, and unit conversions"

    def generate(self) -> Question:
        """Generate a geometry/measurement problem."""
        problem_type = random.choice(
            ["fencing_vs_tiling", "volume", "map_scale", "conversions"]
        )

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
            distractors = [
                f"₹{int(tiling_total)}",
                f"₹{int(fencing_total + 1000)}",
                f"₹{int(fencing_total * 2)}",
            ]
        else:
            correct_answer = f"₹{int(tiling_total)}"
            question_text = f"A rectangular field is {length}m long and {width}m wide. Tiles cost ₹{tiling_cost_per_sqm} per square meter. What is the total cost to tile the entire field?"
            distractors = [
                f"₹{int(fencing_total)}",
                f"₹{int(tiling_total - 500)}",
                f"₹{int(tiling_total // 2)}",
            ]

        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)

        question = Question(
            chapter=self.chapter,
            topic="Geometry & Measurement - Fencing (Perimeter) vs Tiling (Area)",
            logical_trap="Students confuse PERIMETER (Fencing) with AREA (Tiling). Perimeter = around the edges. Area = inside the shape. For the same area, different rectangles have different perimeters.",
            data_representation=f"```\nKey Difference:\nPerimeter = Total distance AROUND the shape (for fencing)\nArea = Total space INSIDE the shape (for tiling/painting)\n\nFor a {length}m × {width}m rectangle:\nPerimeter = 2 × ({length} + {width}) = {perimeter}m\nArea = {length} × {width} = {area} sq m\n```",
            question_text=question_text,
            solution_steps=[
                f"Field dimensions: {length}m × {width}m",
                f"{'Perimeter' if question_type == 'fencing' else 'Area'} = {'2 × (' + str(length) + ' + ' + str(width) + ') = ' + str(perimeter) + 'm' if question_type == 'fencing' else str(length) + ' × ' + str(width) + ' = ' + str(area) + ' sq m'}",
                f"Cost per {'meter' if question_type == 'fencing' else 'sq m'}: ₹{fencing_cost_per_meter if question_type == 'fencing' else tiling_cost_per_sqm}",
                f"Total cost = {perimeter if question_type == 'fencing' else area} × ₹{fencing_cost_per_meter if question_type == 'fencing' else tiling_cost_per_sqm} = ₹{int(fencing_total if question_type == 'fencing' else tiling_total)}",
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
        )
        self._validate_question(question)
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
        total_cubes = (
            cubes_along_length * cubes_along_width * cubes_along_height
        )

        # MCQ options
        correct_answer = str(total_cubes)
        box_volume = box_length * box_width * box_height
        cube_volume = cube_size**3
        wrong1 = str(box_volume // cube_volume)  # Volume method (may or may not match)
        wrong2 = str(total_cubes + 5)  # Off by a few
        wrong3 = str(
            cubes_along_length * cubes_along_width
        )  # Forgot height dimension

        options = self.ensure_unique_options(
            [correct_answer, wrong1, wrong2, wrong3]
        )
        correct_idx = options.index(correct_answer)

        question = Question(
            chapter=self.chapter,
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
                f"Total cubes: {cubes_along_length} × {cubes_along_width} × {cubes_along_height} = {total_cubes}",
            ],
            answer=str(total_cubes),
            options=options,
            correct_option_index=correct_idx,
        )
        self._validate_question(question)
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
            f"{actual_distance * 2}km (Multiplied twice)",
        ]

        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)

        question = Question(
            chapter=self.chapter,
            topic="Geometry & Measurement - Map Scaling & Coordinates",
            logical_trap="Students confuse 'map distance' with 'actual distance.' They forget to apply the scale factor. If 1cm = 5km, then 10cm = 50km, NOT 10km.",
            data_representation=f"```\nMap Scale Logic:\nScale means: 1 unit on map = X units in reality\n\nIf scale is 1cm = {scale_km}km:\n1cm map = {scale_km}km actual\n2cm map = {2*scale_km}km actual\n{map_distance}cm map = {map_distance * scale_km}km actual\n```",
            question_text=f"On a map, the distance between School and Park is {map_distance}cm. The scale of the map is 1cm = {scale_km}km. What is the actual distance between the School and Park?",
            solution_steps=[
                f"Map distance: {map_distance}cm",
                f"Map scale: 1cm = {scale_km}km",
                f"Actual distance = Map distance × Scale",
                f"Actual distance = {map_distance} × {scale_km} = {actual_distance}km",
            ],
            answer=f"{actual_distance}km",
            options=options,
            correct_option_index=correct_idx,
        )
        self._validate_question(question)
        return question

    def _generate_conversions(self) -> Question:
        """Unit conversions: mg, g, kg in same problem."""
        scenarios = [
            {"item": "medicine tablet", "qty_mg": 500, "need_g": True},
            {"item": "flour", "qty_g": 750, "need_kg": True},
            {"item": "weight", "qty_kg": 2, "qty_g": 500, "combine": True},
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
                f"Therefore: {scenario['qty_mg']}mg = {scenario['qty_mg']} ÷ 1000 = {answer_g}g",
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
                f"Therefore: {scenario['qty_g']}g = {scenario['qty_g']} ÷ 1000 = {answer_kg}kg",
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
                f"Convert back: {total_g}g = {total_g} ÷ 1000 = {total_kg}kg",
            ]
            # MCQ options
            wrong1 = f"{scenario['qty_kg']}kg (Ignored the grams)"
            wrong2 = f"{total_kg + 0.5}kg"
            wrong3 = f"{scenario['qty_kg'] + scenario['qty_g']/100}kg"

        options = self.ensure_unique_options([answer_text, wrong1, wrong2, wrong3])
        correct_idx = options.index(answer_text)

        question = Question(
            chapter=self.chapter,
            topic="Geometry & Measurement - Unit Conversions (mg, g, kg)",
            logical_trap="Students forget the conversion factors. They might multiply by 1000 when they should divide, or vice versa. Reminder: mg→g→kg (divide by 1000 each step).",
            data_representation=f"```\nUnit Conversion Chart:\n1 kilogram (kg) = 1000 grams (g)\n1 gram (g) = 1000 milligrams (mg)\n\nDirection matters:\nSmaller to larger unit → DIVIDE\nLarger to smaller unit → MULTIPLY\n```",
            question_text=question_text,
            solution_steps=steps,
            answer=answer_text,
            options=options,
            correct_option_index=correct_idx,
        )
        self._validate_question(question)
        return question
