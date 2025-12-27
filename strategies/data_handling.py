"""Data Handling question strategy - Tables, scales, and comparisons."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
import random


class DataHandlingStrategy(BaseChapterStrategy):
    """Generates data handling problems with scales and missing data."""
    
    chapter = ChapterEnum.DATA_HANDLING
    chapter_name = "Data Handling"
    description = "Tables, scales & comparisons"
    
    def generate(self) -> Question:
        """Generate a data handling question."""
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
        scale = random.choice([8, 10, 12, 15])
        
        data = {day: random.randint(2, 6) for day in days}
        price_per_item = random.choice([5, 8, 10, 12, 15])
        query_day = random.choice(days)
        
        actual_items = data[query_day] * scale
        earnings = actual_items * price_per_item
        
        table = f"| Day | Symbols (1 Icon = {scale} Items) | Actual Items |\n"
        table += "|-----|--------------------------------------|---------------|\n"
        for day in days:
            symbols = "⭐" * data[day]
            items = data[day] * scale
            table += f"| {day} | {symbols} | {items} |\n"
        
        correct_answer = str(actual_items)
        distractors = [
            str(data[query_day]),
            str(actual_items + 10),
            str(actual_items * scale)
        ]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Data Handling - Pictographs (Scale Trap)",
            logical_trap=f"Scale is non-unitary (1 symbol = {scale} items, NOT 1). "
                        "Students forget to multiply by the scale factor.",
            data_representation=table,
            question_text=f"On {query_day}, the shopkeeper earned ₹{earnings}. Each item costs ₹{price_per_item}. "
                          f"How many items were sold?",
            solution_steps=[
                f"Symbols shown on {query_day}: {data[query_day]}",
                f"Scale: 1 symbol = {scale} items",
                f"Actual items = {data[query_day]} × {scale} = {actual_items}",
                f"Verify: {actual_items} × ₹{price_per_item} = ₹{earnings} ✓"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_missing_value(self) -> Question:
        """Generate a table with missing data to calculate."""
        categories = random.choice([
            ["A", "B", "C", "D"],
            ["Class 1", "Class 2", "Class 3", "Class 4"],
            ["Item X", "Item Y", "Item Z"]
        ])
        
        missing_idx = random.randint(0, len(categories) - 1)
        total_sum = random.randint(100, 300)
        
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
        
        table = "| Category | Value |\n|----------|-------|\n"
        for i, cat in enumerate(categories):
            if i == missing_idx:
                table += f"| {cat} | ? |\n"
            else:
                table += f"| {cat} | {values[i]} |\n"
        table += f"| **Total** | **{total_sum}** |\n"
        
        query_cat = categories[missing_idx]
        correct_answer = str(missing_value)
        distractors = [
            str(missing_value + 10),
            str(total_sum - running_sum - 5),
            str(running_sum)
        ]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Data Handling - Missing Data",
            logical_trap="Student must use subtraction (Total - Known Sum) to find missing. "
                        "Don't confuse sum of known with the missing value.",
            data_representation=table,
            question_text=f"The total is {total_sum}. What is the missing value for {query_cat}?",
            solution_steps=[
                f"Known values: {', '.join(str(v) for i, v in enumerate(values) if i != missing_idx)}",
                f"Sum of known = {sum(v for i, v in enumerate(values) if i != missing_idx)}",
                f"Missing = {total_sum} - {sum(v for i, v in enumerate(values) if i != missing_idx)} = {missing_value}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_comparison(self) -> Question:
        """Generate a comparison problem (How many MORE/LESS)."""
        items = ["Apples", "Bananas", "Oranges", "Mangoes"]
        item1, item2 = random.sample(items, 2)
        
        val1 = random.randint(40, 120)
        val2 = random.randint(40, 120)
        
        difference = abs(val1 - val2)
        more_or_less = "more" if val1 > val2 else "less"
        
        table = f"| Item | Quantity |\n|------|----------|\n"
        table += f"| {item1} | {val1} |\n"
        table += f"| {item2} | {val2} |\n"
        
        correct_answer = str(difference)
        distractors = [
            str(difference + 5),
            str(val1),
            str(val1 + val2)
        ]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
        question = Question(
            chapter=self.chapter,
            topic="Data Handling - Comparison",
            logical_trap="Student must compute the difference AND use correct language. "
                        "Don't use addition instead of subtraction.",
            data_representation=table,
            question_text=f"How many {more_or_less} {item2.lower()} compared to {item1.lower()}?",
            solution_steps=[
                f"Quantity of {item1} = {val1}",
                f"Quantity of {item2} = {val2}",
                f"Difference = |{val1} - {val2}| = {difference}",
                f"{item2} has {difference} {more_or_less} than {item1}"
            ],
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
