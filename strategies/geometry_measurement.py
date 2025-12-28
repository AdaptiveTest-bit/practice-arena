"""Strategy for Geometry & Measurement questions.

Covers:
- Fencing (Perimeter) vs Tiling (Area)
- Volume and cube packing
- Map scaling and coordinates
- Unit conversions (mg, g, kg)
"""

import random
from models.distractor import MisconceptionType
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
from strategies.base import BaseChapterStrategy


class GeometryMeasurementStrategy(BaseChapterStrategy):
    """Generates geometry and measurement problems."""

    chapter = ChapterEnum.GEOMETRY_MEASUREMENT
    chapter_name = "Geometry & Measurement"
    description = "Geometry, area, perimeter, volume, map scaling, and unit conversions"

    def generate(self) -> Question:
        """Generate a geometry/measurement problem."""
        problem_type = random.choice(
            ["fencing_vs_tiling", "volume", "map_scale", "conversions",
             "rectangle_area", "triangle_area", "perimeter_comparison", 
             "composite_shapes", "irregular_shapes"]
        )

        if problem_type == "fencing_vs_tiling":
            return self._generate_fencing_vs_tiling()
        elif problem_type == "volume":
            return self._generate_volume()
        elif problem_type == "map_scale":
            return self._generate_map_scale()
        elif problem_type == "conversions":
            return self._generate_conversions()
        elif problem_type == "rectangle_area":
            return self._generate_rectangle_area()
        elif problem_type == "triangle_area":
            return self._generate_triangle_area()
        elif problem_type == "perimeter_comparison":
            return self._generate_perimeter_comparison()
        elif problem_type == "composite_shapes":
            return self._generate_composite_shapes()
        else:
            return self._generate_irregular_shapes()

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
            
            # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
            misconception_map = {
                MisconceptionType.FORMULA_MISAPPLICATION: 
                    f"₹{int(tiling_total)}",  # Uses area (tiling) instead of perimeter (fencing)
                MisconceptionType.INCOMPLETE_REASONING: 
                    f"₹{int(fencing_total + 1000)}",  # Adds extra without understanding
                MisconceptionType.ARITHMETIC_ERROR: 
                    f"₹{int(fencing_total * 2)}"  # Multiplies result unnecessarily
            }
        else:
            correct_answer = f"₹{int(tiling_total)}"
            question_text = f"A rectangular field is {length}m long and {width}m wide. Tiles cost ₹{tiling_cost_per_sqm} per square meter. What is the total cost to tile the entire field?"
            
            # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
            misconception_map = {
                MisconceptionType.FORMULA_MISAPPLICATION: 
                    f"₹{int(fencing_total)}",  # Uses perimeter (fencing) instead of area (tiling)
                MisconceptionType.INCOMPLETE_REASONING: 
                    f"₹{int(tiling_total - 500)}",  # Subtracts without understanding
                MisconceptionType.ARITHMETIC_ERROR: 
                    f"₹{int(tiling_total // 2)}"  # Divides result without justification
            }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)

        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.FORMULA_MISAPPLICATION,
            difficulty=3,
            custom_description="Student confuses PERIMETER (fencing) with AREA (tiling); applies wrong formula to problem context",
            custom_why_effective="Classic K.C. Nag trap; both use rectangular dimensions but compute very different values",
            custom_how_to_avoid="Perimeter = around edges = 2(l+w); Area = inside = l×w; read problem carefully: fencing goes around, tiling goes inside"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
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
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.FORMULA_MISAPPLICATION: 
                str(box_volume // cube_volume),  # Volume method (may or may not match)
            MisconceptionType.INCOMPLETE_REASONING: 
                str(cubes_along_length * cubes_along_width),  # Forgot height dimension
            MisconceptionType.ARITHMETIC_ERROR: 
                str(total_cubes + 5)  # Off by a few
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)

        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=3,
            custom_description="Student forgets one dimension when packing cubes; multiplies only two of the three dimensions",
            custom_why_effective="3D problem that students try to reduce to 2D; easy to lose track of height",
            custom_how_to_avoid="Packing cubes requires THREE dimensions: length × width × height; check each dimension before multiplying"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
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
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"{map_distance}km",  # Forgot to apply scale
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{actual_distance + 10}km",  # Off by 10
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{actual_distance * 2}km"  # Multiplied twice
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)

        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.CONSTRAINT_VIOLATION,
            difficulty=2,
            custom_description="Student forgets to apply map scale; reports map distance as actual distance",
            custom_why_effective="Scale is essential constraint students often overlook; both values are in same units causing confusion",
            custom_how_to_avoid="Always apply scale factor: Actual Distance = Map Distance × Scale; never report map distance as final answer"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
            # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
            misconception_map = {
                MisconceptionType.UNIT_ERROR: 
                    f"{scenario['qty_mg'] / 100}g",  # Divides by 100 instead of 1000
                MisconceptionType.OPERATION_DIRECTION: 
                    f"{scenario['qty_mg'] * 1000}g",  # Multiplies instead of dividing
                MisconceptionType.INCOMPLETE_REASONING: 
                    f"{answer_g + 0.1}g"  # Off by small amount
            }
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
            # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
            misconception_map = {
                MisconceptionType.UNIT_ERROR: 
                    f"{scenario['qty_g'] / 100}kg",  # Divides by 100 instead of 1000
                MisconceptionType.OPERATION_DIRECTION: 
                    f"{scenario['qty_g'] * 1000}kg",  # Multiplies instead of dividing
                MisconceptionType.INCOMPLETE_REASONING: 
                    f"{answer_kg + 0.1}kg"  # Off by small amount
            }
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
            # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
            misconception_map = {
                MisconceptionType.INCOMPLETE_REASONING: 
                    f"{scenario['qty_kg']}kg",  # Ignored the grams
                MisconceptionType.ARITHMETIC_ERROR: 
                    f"{total_kg + 0.5}kg",  # Calculation error
                MisconceptionType.UNIT_ERROR: 
                    f"{scenario['qty_kg'] + scenario['qty_g']/100}kg"  # Wrong conversion factor
            }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(answer_text, misconception_map)

        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.UNIT_ERROR,
            difficulty=2,
            custom_description="Student uses wrong conversion factor (e.g., divides by 100 instead of 1000 for mg→g)",
            custom_why_effective="Multiple similar conversion factors (1000 for each transition); easy to confuse or misapply",
            custom_how_to_avoid="Memorize: 1kg=1000g, 1g=1000mg; when going smaller→larger divide; larger→smaller multiply; verify units"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        self._validate_question(question)
        return question
    
    def _generate_rectangle_area(self) -> Question:
        """Calculate rectangle area."""
        length = random.randint(5, 15)
        width = random.randint(3, 12)
        
        area = length * width
        correct_answer = f"{area} sq units"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{length + width} sq units",  # Perimeter instead
            MisconceptionType.OPERATION_SELECTION: f"{(length + width) * 2} sq units",  # Wrong perimeter
            MisconceptionType.ARITHMETIC_ERROR: f"{area - 5} sq units"  # Off by constant
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Student calculates perimeter instead of area",
            custom_why_effective="Both use length and width; students confuse formulas",
            custom_how_to_avoid="Area = length × width (square units); Perimeter = 2(l+w) (linear units)"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.REMEMBER, trap_difficulty=1)
        
        question = Question(
            chapter=self.chapter,
            topic="Rectangle Area Calculation",
            logical_trap="Student uses perimeter formula instead of area formula",
            data_representation=f"Rectangle:\nLength = {length} units\nWidth = {width} units",
            question_text=f"What is the area of a rectangle with length {length} and width {width}?",
            solution_steps=[
                f"Formula: Area = length × width",
                f"Area = {length} × {width}",
                f"Area = {area} square units"
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
    
    def _generate_triangle_area(self) -> Question:
        """Calculate triangle area."""
        base = random.randint(6, 14)
        height = random.randint(4, 12)
        
        area = (base * height) // 2
        correct_answer = f"{area} sq units"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{base * height} sq units",  # Forgot to divide by 2
            MisconceptionType.OPERATION_SELECTION: f"{base + height} sq units",  # Addition
            MisconceptionType.CONSTRAINT_VIOLATION: f"{(base + height) // 2} sq units"  # Wrong calculation
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student multiplies base × height but forgets to divide by 2",
            custom_why_effective="Triangle is half of rectangle; dividing by 2 is often forgotten",
            custom_how_to_avoid="Triangle area = (base × height) ÷ 2, NOT base × height"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Triangle Area Calculation",
            logical_trap="Student forgets that triangle is half a rectangle (divide by 2)",
            data_representation=f"Triangle:\nBase = {base} units\nHeight = {height} units",
            question_text=f"What is the area of a triangle with base {base} and height {height}?",
            solution_steps=[
                f"Formula: Area = (base × height) ÷ 2",
                f"Area = ({base} × {height}) ÷ 2",
                f"Area = {base * height} ÷ 2",
                f"Area = {area} square units"
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
    
    def _generate_perimeter_comparison(self) -> Question:
        """Compare perimeters of different shapes."""
        rect_len = random.randint(6, 10)
        rect_width = random.randint(3, 8)
        rect_perim = 2 * (rect_len + rect_width)
        
        square_side = random.randint(4, 9)
        square_perim = 4 * square_side
        
        if rect_perim > square_perim:
            correct_answer = f"Rectangle ({rect_perim} units)"
            bigger = "Rectangle"
            smaller = "Square"
        elif square_perim > rect_perim:
            correct_answer = f"Square ({square_perim} units)"
            bigger = "Square"
            smaller = "Rectangle"
        else:
            correct_answer = "They are equal"
            bigger = None
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{smaller} ({min(rect_perim, square_perim)} units)" if bigger else "They are different",
            MisconceptionType.CONSTRAINT_VIOLATION: f"Rectangle ({rect_perim} units)" if bigger != "Rectangle" else "Square ({square_perim} units)",
            MisconceptionType.OPERATION_SELECTION: f"{rect_len * rect_width} vs {square_side * square_side}"
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student compares areas instead of perimeters",
            custom_why_effective="Both involve the same measurements but different operations",
            custom_how_to_avoid="Perimeter = sum of all sides; Area = length × width"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Perimeter Comparison",
            logical_trap="Student calculates area instead of perimeter for comparison",
            data_representation=f"Rectangle: {rect_len} × {rect_width}\nSquare: {square_side} × {square_side}",
            question_text=f"Which has a larger perimeter: Rectangle ({rect_len}×{rect_width}) or Square ({square_side}×{square_side})?",
            solution_steps=[
                f"Rectangle perimeter = 2({rect_len} + {rect_width}) = {rect_perim} units",
                f"Square perimeter = 4 × {square_side} = {square_perim} units",
                f"Compare: {rect_perim} vs {square_perim}",
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
    
    def _generate_composite_shapes(self) -> Question:
        """Calculate area of composite shapes (rectangle + triangle)."""
        rect_len = random.randint(8, 14)
        rect_width = random.randint(4, 8)
        tri_base = rect_len
        tri_height = random.randint(3, 6)
        
        rect_area = rect_len * rect_width
        tri_area = (tri_base * tri_height) // 2
        total_area = rect_area + tri_area
        
        correct_answer = f"{total_area} sq units"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{rect_area} sq units",  # Only rectangle
            MisconceptionType.OPERATION_SELECTION: f"{tri_area} sq units",  # Only triangle
            MisconceptionType.CONSTRAINT_VIOLATION: f"{rect_area + tri_base * tri_height} sq units"  # Forgot triangle division
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=3,
            custom_description="Student calculates only part of composite shape",
            custom_why_effective="Composite shapes require breaking down and adding parts",
            custom_how_to_avoid="Identify all component shapes, calculate each area, then sum"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=3)
        
        question = Question(
            chapter=self.chapter,
            topic="Composite Shapes Area",
            logical_trap="Student forgets to include triangle part or miscalculates triangle area",
            data_representation=f"Composite shape (Rectangle + Triangle on top):\nRectangle: {rect_len} × {rect_width}\nTriangle: base {tri_base}, height {tri_height}",
            question_text=f"Find total area of a rectangle ({rect_len}×{rect_width}) with triangle on top (base {tri_base}, height {tri_height})",
            solution_steps=[
                f"Rectangle area = {rect_len} × {rect_width} = {rect_area} sq units",
                f"Triangle area = ({tri_base} × {tri_height}) ÷ 2 = {tri_area} sq units",
                f"Total area = {rect_area} + {tri_area} = {total_area} sq units"
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
    
    def _generate_irregular_shapes(self) -> Question:
        """Calculate area using grid method for irregular shapes."""
        complete_squares = random.randint(8, 16)
        half_squares = random.randint(2, 6)
        
        # Grid method: complete squares + (half squares ÷ 2)
        area = complete_squares + (half_squares // 2)
        correct_answer = f"{area} sq units"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{complete_squares} sq units",  # Ignore half squares
            MisconceptionType.OPERATION_SELECTION: f"{complete_squares + half_squares} sq units",  # Count half as full
            MisconceptionType.CONSTRAINT_VIOLATION: f"{complete_squares + half_squares // 2 + 1} sq units"  # Off by one
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student only counts complete squares, ignoring partial squares",
            custom_why_effective="Partial squares are harder to count and easy to forget",
            custom_how_to_avoid="Count complete squares, then add 2 half-squares = 1 full square"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Irregular Shapes Area (Grid Method)",
            logical_trap="Student forgets to count partial squares or counts them as whole squares",
            data_representation=f"Grid with irregular shape:\n{complete_squares} complete squares\n{half_squares} half squares",
            question_text=f"Using grid method, find area: {complete_squares} complete squares + {half_squares} half squares",
            solution_steps=[
                f"Complete squares: {complete_squares}",
                f"Half squares: {half_squares}",
                f"Half square pairs: {half_squares} ÷ 2 = {half_squares // 2}",
                f"Total area = {complete_squares} + {half_squares // 2} = {area} sq units"
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
