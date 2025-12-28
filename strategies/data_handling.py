"""Data Handling question strategy - Tables, scales, and comparisons."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
import random
from models.distractor import MisconceptionType


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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                str(data[query_day]),  # Forgot to multiply by scale
            MisconceptionType.ARITHMETIC_ERROR: 
                str(actual_items + 10),  # Off-by-one arithmetic
            MisconceptionType.OPERATION_SELECTION: 
                str(actual_items * scale)  # Double multiplied
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student sees the scale (1 symbol = N items) but forgets to multiply; reports only symbol count",
            custom_why_effective="Non-unitary scale is a classic trap; students often read the scale but apply it incorrectly",
            custom_how_to_avoid="Always check the scale legend; multiply symbol count by scale; verify multiplication"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR: 
                str(missing_value + 10),  # Off-by-10 error
            MisconceptionType.INCOMPLETE_REASONING: 
                str(total_sum - running_sum - 5),  # Subtraction error
            MisconceptionType.OPPOSITE_CONFUSION: 
                str(running_sum)  # Shows known sum instead of missing
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.ARITHMETIC_ERROR,
            difficulty=2,
            custom_description="Student makes computational error when subtracting known sum from total; off-by-N mistakes",
            custom_why_effective="Subtraction itself is error-prone; students often make mistakes in multi-step computation",
            custom_how_to_avoid="Write out: Total = Known1 + Known2 + ... + Missing; Rearrange; Subtract step-by-step; Verify"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
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
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR: 
                str(difference + 5),  # Off-by-5
            MisconceptionType.INCOMPLETE_REASONING: 
                str(val1),             # Shows first value, not difference
            MisconceptionType.OPERATION_SELECTION: 
                str(val1 + val2)       # Adds instead of subtracts
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPERATION_SELECTION,
            difficulty=1,
            custom_description="Student adds quantities instead of subtracting when finding 'how many more/less' difference",
            custom_why_effective="Simple error showing confusion about 'difference' vs 'total'; basic operation selection",
            custom_how_to_avoid="'Difference' always means subtract: larger minus smaller; 'How many more/less' = subtraction"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.UNDERSTAND,
            trap_difficulty=1
        )
        
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
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,  # Phase 2
            bloom_info=bloom_info  # 🆕 Phase 3
        )
        
        self._validate_question(question)
        return question
