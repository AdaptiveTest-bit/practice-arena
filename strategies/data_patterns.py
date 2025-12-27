"""Strategy for Data & Patterns questions.

Covers:
- Number sequences and patterns
- Missing data in tables
- Pictographs with non-unitary scales
"""

import random
from models.question import Question, ChapterEnum
from strategies.base import BaseChapterStrategy


class DataPatternsStrategy(BaseChapterStrategy):
    """Generates data, patterns, and missing data problems."""

    chapter = ChapterEnum.DATA_PATTERNS
    chapter_name = "Data & Patterns"
    description = "Number sequences, missing data, and pictographs with scaling"

    def generate(self) -> Question:
        """Generate a data/pattern problem."""
        problem_type = random.choice(
            ["pattern_sequence", "missing_table", "scale_pictograph"]
        )

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
            answer = position**2
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
            str(position * 10),
        ]

        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)

        question = Question(
            chapter=self.chapter,
            topic="Data & Patterns - Number Sequences",
            logical_trap="Students try simple addition (+2 or +3) instead of recognizing the actual pattern. This tests logic, not calculation.",
            data_representation=f"```\nPattern Type: {pattern_type.upper()}\nSequence start: {', '.join(map(str, sequence))}\nRule: {rule}\n\nTo find the next term, apply the rule consistently.\n```",
            question_text=f"Find the {position}th number in the pattern: {', '.join(map(str, sequence))}, ...",
            solution_steps=[
                f"Sequence: {', '.join(map(str, sequence))}",
                f"Rule: {rule}",
                f"Position {position}: {answer}",
            ],
            answer=str(answer),
            options=options,
            correct_option_index=correct_idx,
        )
        self._validate_question(question)
        return question

    def _generate_missing_table(self) -> Question:
        """Find missing data given total and other values."""
        categories = random.choice(
            [
                ["Student A", "Student B", "Student C", "Student D"],
                ["Week 1", "Week 2", "Week 3", "Week 4"],
            ]
        )

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
            str(total - sum(values) + 20),
        ]

        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)

        question = Question(
            chapter=self.chapter,
            topic="Data & Patterns - Missing Data in Tables",
            logical_trap="Students add the visible numbers and then try to find the missing value. They must use the total as a constraint.",
            data_representation=table,
            question_text=f"The table shows data for {len(categories)} categories. The total is {total}. Find the missing value for {categories[missing_idx]}.",
            solution_steps=[
                f"Sum of known values: {' + '.join(map(str, [v for v in display_values if v is not None]))} = {sum(values)}",
                f"Total = {total}",
                f"Missing value = {total} - {sum(values)} = {missing_value}",
            ],
            answer=str(missing_value),
            options=options,
            correct_option_index=correct_idx,
        )
        self._validate_question(question)
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

        # MCQ options - ensure uniqueness
        correct_answer = f"{actual_counts[query_item]}"
        count_only = str(symbol_counts[query_item])  # Just counting icons
        wrong_scale = str(
            int(symbol_counts[query_item] * (scale_value // 2))
        )  # Wrong scale (half)
        # Get a different item's actual count to avoid duplication
        other_items = [i for i in items if i != query_item]
        wrong_other = str(actual_counts[other_items[0]])

        options = self.ensure_unique_options(
            [correct_answer, count_only, wrong_scale, wrong_other]
        )
        correct_idx = options.index(correct_answer)

        question = Question(
            chapter=self.chapter,
            topic="Data & Patterns - Pictographs with Non-Unitary Scale",
            logical_trap="Students count the icons (e.g., 3 icons) instead of multiplying by the scale (e.g., 3 × 10 = 30 fruits). The scale is crucial!",
            data_representation=table,
            question_text=f"The pictograph shows fruits sold. 1 icon = {scale_value} fruits. How many {query_item.lower()} were sold?",
            solution_steps=[
                f"Number of icons for {query_item}: {symbol_counts[query_item]}",
                f"Scale: 1 icon = {scale_value} fruits",
                f"Actual count = {symbol_counts[query_item]} × {scale_value} = {actual_counts[query_item]} fruits",
            ],
            answer=f"{actual_counts[query_item]}",
            options=options,
            correct_option_index=correct_idx,
        )
        self._validate_question(question)
        return question
