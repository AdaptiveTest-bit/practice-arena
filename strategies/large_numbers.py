"""Large Numbers & Place Value question strategy.

This strategy implements K.C. Nag-style questions on:
- Place value in Indian numbering (Lakh/Crore)
- Profit & Loss calculations
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
import random
from models.distractor import MisconceptionType


class LargeNumbersStrategy(BaseChapterStrategy):
    """Generates problems on large numbers and place value."""
    
    chapter = ChapterEnum.LARGE_NUMBERS
    chapter_name = "Large Numbers"
    description = "Place value, profit & loss"
    
    def generate(self) -> Question:
        """Generate a large numbers question using strategy pattern."""
        problem_type = random.choice([
            "place_value",
            "profit_loss",
            "speed_calculation",
            "time_distance",
            "comparison_large",
            "rounding"
        ])
        
        if problem_type == "place_value":
            return self._generate_place_value()
        elif problem_type == "profit_loss":
            return self._generate_profit_loss()
        elif problem_type == "speed_calculation":
            return self._generate_speed_calculation()
        elif problem_type == "time_distance":
            return self._generate_time_distance()
        elif problem_type == "comparison_large":
            return self._generate_comparison_large()
        else:  # rounding
            return self._generate_rounding_large_numbers()
    
    # =========================================================================
    # QUESTION TYPE IMPLEMENTATIONS
    # =========================================================================
    
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
        
        # Generate unique MCQ options
        correct_answer = scenario['words']
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.UNIVERSAL_VS_SPECIFIC: 
                scenario['words'].replace("lakh", "million") if "lakh" in scenario['words'] 
                    else scenario['words'].replace("crore", "billion"),
            MisconceptionType.CONSTRAINT_VIOLATION: 
                scenario['words'].replace("hundred", "crore") if "hundred" in scenario['words'] 
                    else scenario['words'] + " (doubled)",
            MisconceptionType.LOGICAL_DISCONNECT: 
                scenario['words'] + " (reading right to left instead of groups)"
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.UNIVERSAL_VS_SPECIFIC,
            difficulty=2,
            custom_description="Student confuses Indian numbering (Lakh/Crore) with Western (Million/Billion) systems",
            custom_why_effective="Both systems use place value but group digits differently; surface similarity causes confusion",
            custom_how_to_avoid="Memorize: 1 Lakh = 100,000 (5 zeros); 1 Crore = 10 Lakhs (7 zeros); NOT millions or billions"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Number Systems - Large Numbers & Place Value",
            logical_trap="Students confuse the Indian system (Lakh/Crore) with Western (Million/Billion). "
                        "1 Lakh = 100,000, NOT 1 Million.",
            data_representation=f"""```
Indian Numbering System:
1 Crore = 10 Lakhs = 1,00,00,000
1 Lakh = 1,00,000
1 Ten-thousand = 10,000

Place Value Positions (Right to Left):
Ones, Tens, Hundreds, Thousands, Ten-thousands, Lakhs, Ten-lakhs, Crores
```""",
            question_text=f"What is the place value of each digit in {scenario['number']:,}? "
                          "Express your answer in the Indian numbering system.",
            solution_steps=[
                f"Number: {scenario['number']:,}",
                f"Word form: {scenario['words']}",
                f"Breakdown: {scenario['breakdown']}",
                "This demonstrates the Indian place value system with Lakhs and Ten-lakhs"
            ],
            answer=scenario['words'],
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
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
            scenario_desc = f"{profit_percent}% profit"
        else:
            sell_per_unit = cost_per_unit * (1 - loss_percent / 100)
            total_sell = units * sell_per_unit
            total_loss = total_cost - total_sell
            answer_value = int(total_loss)
            answer_text = f"₹{answer_value:,}"
            scenario_desc = f"{loss_percent}% loss"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        wrong_total_cost = f"₹{int(total_cost):,}"
        wrong_total_sell = f"₹{int(total_sell):,}"
        wrong_profit = f"₹{int(answer_value * 0.75):,}"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                wrong_total_cost,  # Shows cost, not profit/loss
            MisconceptionType.OPPOSITE_CONFUSION: 
                wrong_total_sell,   # Shows selling price, not profit/loss
            MisconceptionType.ARITHMETIC_ERROR: 
                wrong_profit       # Wrong calculation
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(answer_text, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=3,
            custom_description="Student calculates cost or selling price but forgets final subtraction step to find actual profit/loss",
            custom_why_effective="Multi-step calculation; students often get intermediate values correct but miss final step",
            custom_how_to_avoid="Always perform final subtraction: Profit = Selling - Cost; Loss = Cost - Selling; don't stop early"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.ANALYZE,
            trap_difficulty=3
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Number Systems - Profit & Loss",
            logical_trap="Students confuse total cost or total selling price with profit/loss. "
                        "Profit = Selling Price - Cost Price, NOT the absolute amounts.",
            data_representation=f"""```
Profit & Loss Formulas:
Profit = Selling Price - Cost Price
Loss = Cost Price - Selling Price
Profit % = (Profit / Cost Price) × 100
Loss % = (Loss / Cost Price) × 100

Given:
- Units: {units}
- Cost per unit: ₹{cost_per_unit}
- Total Cost: ₹{int(total_cost):,}
- Selling per unit: ₹{int(sell_per_unit)}
- Total Selling: ₹{int(total_sell):,}
- Scenario: {scenario_desc}
```""",
            question_text=f"A shopkeeper buys {units} items at ₹{cost_per_unit} each and sells at {scenario_desc}. "
                          f"What is the total {scenario_type}?",
            solution_steps=[
                f"Total Cost = {units} × ₹{cost_per_unit} = ₹{int(total_cost):,}",
                f"Selling Price per unit = ₹{cost_per_unit} × (1 + {profit_percent if scenario_type == 'profit' else -loss_percent}/100) "
                    f"= ₹{int(sell_per_unit)}",
                f"Total Selling Price = {units} × ₹{int(sell_per_unit)} = ₹{int(total_sell):,}",
                f"Total {scenario_type.capitalize()} = ₹{int(total_sell):,} - ₹{int(total_cost):,} = ₹{answer_value:,}"
            ],
            answer=answer_text,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
    
    def _generate_speed_calculation(self) -> Question:
        """Calculate speed given distance and time.
        
        Speed = Distance / Time
        """
        distance = random.choice([100, 150, 200, 250, 300, 400, 500])
        time = random.choice([2, 3, 4, 5])
        
        speed = distance // time
        correct_answer = f"{speed} km/h"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{distance} km/h",  # Just distance
            MisconceptionType.OPERATION_SELECTION: f"{distance + time} km/h",  # Addition
            MisconceptionType.OPERATION_DIRECTION: f"{time}/{distance} km/h"  # Reversed
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets to divide distance by time",
            custom_why_effective="Speed requires division; students may only remember the distance",
            custom_how_to_avoid="Speed = Distance ÷ Time. Always divide."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Speed Calculation",
            logical_trap="Student provides distance instead of speed, or forgets to divide",
            data_representation=f"Distance: {distance} km\nTime: {time} hours",
            question_text=f"A vehicle travels {distance} km in {time} hours. What is its speed?",
            solution_steps=[
                f"Formula: Speed = Distance ÷ Time",
                f"Speed = {distance} ÷ {time} = {speed} km/h"
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
    
    def _generate_time_distance(self) -> Question:
        """Calculate time or distance given speed.
        
        Time = Distance / Speed or Distance = Speed × Time
        """
        speed = random.choice([50, 60, 75, 80, 100])
        time_or_dist = random.choice(["time", "distance"])
        
        if time_or_dist == "time":
            distance = random.choice([200, 300, 400, 500])
            time = distance // speed
            correct_answer = f"{time} hours"
            question_text = f"A vehicle travels at {speed} km/h. How long to travel {distance} km?"
            solution = f"Time = Distance ÷ Speed = {distance} ÷ {speed} = {time} hours"
        else:
            time = random.choice([2, 3, 4, 5, 6])
            distance = speed * time
            correct_answer = f"{distance} km"
            question_text = f"A vehicle travels at {speed} km/h for {time} hours. How far?"
            solution = f"Distance = Speed × Time = {speed} × {time} = {distance} km"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{speed} {'hours' if time_or_dist == 'time' else 'km'}",
            MisconceptionType.OPERATION_SELECTION: f"{distance if time_or_dist == 'time' else time}",
            MisconceptionType.OPERATION_DIRECTION: f"{time if time_or_dist == 'time' else distance}"
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets to multiply/divide to get final answer",
            custom_why_effective="Speed problems require understanding relationship between D, S, T",
            custom_how_to_avoid="Use triangle: Distance at top, Speed and Time at bottom"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Time/Distance Problem",
            logical_trap="Student provides given information instead of calculating missing value",
            data_representation=f"Speed: {speed} km/h\n{'Distance: ' + str(distance) + ' km' if time_or_dist == 'time' else 'Time: ' + str(time) + ' hours'}",
            question_text=question_text,
            solution_steps=[question_text, solution],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info
        )
        
        self._validate_question(question)
        return question
    
    def _generate_comparison_large(self) -> Question:
        """Compare two large numbers.
        
        Which is bigger: 1,23,456 or 1,32,456?
        """
        num1 = random.randint(100000, 9999999)
        num2 = random.randint(100000, 9999999)
        
        if num1 > num2:
            correct_answer = f"{num1:,}"
            bigger = num1
            smaller = num2
        else:
            correct_answer = f"{num2:,}"
            bigger = num2
            smaller = num1
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{smaller:,}",  # Smaller number
            MisconceptionType.CONSTRAINT_VIOLATION: f"They are equal",
            MisconceptionType.OPERATION_SELECTION: f"{num1 + num2:,}"  # Sum
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Student doesn't carefully compare digit by digit",
            custom_why_effective="Large numbers can look similar; requires careful comparison",
            custom_how_to_avoid="Compare from leftmost digit: if equal, move right"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        question = Question(
            chapter=self.chapter,
            topic="Comparing Large Numbers",
            logical_trap="Student doesn't systematically compare from left to right",
            data_representation=f"Compare:\nNumber 1: {num1:,}\nNumber 2: {num2:,}",
            question_text=f"Which is larger: {num1:,} or {num2:,}?",
            solution_steps=[
                f"Number 1: {num1:,}",
                f"Number 2: {num2:,}",
                f"Comparing digit by digit from left",
                f"Answer: {correct_answer} is larger"
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
    
    def _generate_rounding_large_numbers(self) -> Question:
        """Round large numbers to nearest 10, 100, 1000, etc.
        
        Round 456,789 to nearest lakh
        """
        number = random.randint(100000, 9999999)
        rounding_places = random.choice([
            ("10", 10),
            ("100", 100),
            ("1000", 1000),
            ("10,000", 10000),
            ("1,00,000", 100000)
        ])
        
        place_name, place_value = rounding_places
        rounded = round(number / place_value) * place_value
        correct_answer = f"{rounded:,}"
        
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: f"{number:,}",  # Original number
            MisconceptionType.CONSTRAINT_VIOLATION: f"{round(number / (place_value * 10)) * (place_value * 10):,}",  # Wrong place
            MisconceptionType.ARITHMETIC_ERROR: f"{rounded + place_value:,}"  # Off by one unit
        }
        
        options, correct_idx, distractor_info = self.create_categorized_distractors(
            correct_answer, misconception_map
        )
        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets to round or rounds to wrong place value",
            custom_why_effective="Rounding requires understanding place value and decision rule",
            custom_how_to_avoid="Look at digit in place you're rounding to. If next digit ≥5, round up"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        question = Question(
            chapter=self.chapter,
            topic="Rounding Large Numbers",
            logical_trap="Student rounds to wrong place value or forgets to round",
            data_representation=f"Original: {number:,}\nRound to nearest: {place_name}",
            question_text=f"Round {number:,} to the nearest {place_name}",
            solution_steps=[
                f"Original number: {number:,}",
                f"Rounding to: {place_name}",
                f"Look at digit in {place_name} place",
                f"Decision: Check next digit (≥5 means round up)",
                f"Rounded number: {correct_answer}"
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
