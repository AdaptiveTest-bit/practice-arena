"""Large Numbers & Place Value question strategy.

This strategy implements K.C. Nag-style questions on:
- Place value in Indian numbering (Lakh/Crore)
- Profit & Loss calculations
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
import random


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
        ])
        
        if problem_type == "place_value":
            return self._generate_place_value()
        else:  # profit_loss
            return self._generate_profit_loss()
    
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
        distractors = [
            scenario['words'].replace("lakh", "million") if "lakh" in scenario['words'] 
                else scenario['words'].replace("crore", "billion"),
            scenario['words'].replace("hundred", "crore") if "hundred" in scenario['words'] 
                else scenario['words'] + " (doubled)",
            scenario['words'] + " (reading right to left instead of groups)"
        ]
        
        options, correct_idx = self.shuffle_options_keep_correct(correct_answer, distractors)
        
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
            correct_option_index=correct_idx
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
        
        # Generate unique distractors
        wrong_total_cost = f"₹{int(total_cost):,}"
        wrong_total_sell = f"₹{int(total_sell):,}"
        wrong_profit = f"₹{int(answer_value * 0.75):,}"  # 75% of correct answer
        
        options = self.ensure_unique_options([answer_text, wrong_total_cost, wrong_total_sell, wrong_profit])
        correct_idx = options.index(answer_text)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
