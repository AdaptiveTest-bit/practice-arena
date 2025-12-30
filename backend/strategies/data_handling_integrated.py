"""
DATA HANDLING - INTEGRATED STRATEGY
===================================

Hybrid Neuro-Symbolic approach for Data Handling

Integrates:
1. Statistical calculations
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Average/median confusion, Probability misunderstanding)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class DataHandlingIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic statistical logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.DATA_HANDLING
    chapter_name = "Data Handling"
    description = "Data Handling with hybrid neuro-symbolic approach"
    
    def __init__(self):
        super().__init__()
        # Initialize hybrid system components here
        # self.sympy_generator = ...
        # self.story_generator = ...
        # self.renderer = ...
    
    def generate(self) -> Question:
        """
        Main generation pipeline:
        1. Select problem type
        2. Generate skeleton (PHASE 1)
        3. Generate K.C. Nag story (PHASE 2)
        4. Generate misconception options (PHASE 3)
        5. Render rich question (PHASE 4)
        6. Create trackable Question (PHASE 5)
        """
        problem_type = random.choice([
            "average_calculation",
            "median_finding",
            "mode_identification",
        ])
        
        if problem_type == "average_calculation":
            return self._generate_average_calculation()
        elif problem_type == "median_finding":
            return self._generate_median_finding()
        else:  # mode_identification
            return self._generate_mode_identification()
    
    def _generate_average_calculation(self) -> Question:
        """
        Average Calculation - Finding the mean of a dataset
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Average calculation scenarios
        average_scenarios = [
            {
                "context": "test scores",
                "data": [45, 52, 68, 75],
                "sum": 240,
                "count": 4,
                "average": 60,
                "description": "4 students' math test scores"
            },
            {
                "context": "daily temperatures",
                "data": [28, 32, 30, 26, 29],
                "sum": 145,
                "count": 5,
                "average": 29,
                "description": "temperatures over 5 days"
            },
            {
                "context": "heights of friends",
                "data": [140, 145, 150, 155],
                "sum": 590,
                "count": 4,
                "average": 147.5,
                "description": "heights of 4 friends in cm"
            },
            {
                "context": "exam marks",
                "data": [72, 84, 80, 76],
                "sum": 312,
                "count": 4,
                "average": 78,
                "description": "4 subject exam marks"
            }
        ]
        
        avg_data = random.choice(average_scenarios)
        correct_answer = str(avg_data["average"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Arjun has {avg_data['description']}: {', '.join(map(str, avg_data['data']))}. What is the average?",
            f"To find the average {avg_data['context']}, add them up and divide by how many. The values are {', '.join(map(str, avg_data['data']))}. What's the average?",
            f"Average of {avg_data['context']}: {', '.join(map(str, avg_data['data']))}. Calculate the mean."
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "forgot to divide by the count",
            "used only the sum",
            "divided by wrong number"
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Only sum, forgot division
        wrong_options.append((
            str(avg_data["sum"]),
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Used sum instead of average",
            f"You said {avg_data['sum']}, but that's just the sum! Average = Sum ÷ Count = {avg_data['sum']} ÷ {avg_data['count']} = {avg_data['average']}.",
            f"Average requires two steps: sum all values, then divide by count"
        ))
        
        # Misconception 2: Wrong divisor
        wrong_divisor = avg_data["count"] - 1
        wrong_average_2 = avg_data["sum"] / wrong_divisor if wrong_divisor > 0 else 0
        wrong_options.append((
            str(wrong_average_2),
            MisconceptionType.LOGICAL_DISCONNECT,
            f"Divided by {wrong_divisor} instead of {avg_data['count']}",
            f"You got {wrong_average_2}, but count {avg_data['count']} values, not {wrong_divisor}. Correct average: {avg_data['sum']} ÷ {avg_data['count']} = {avg_data['average']}.",
            f"Make sure you divide by the total number of values"
        ))
        
        # Misconception 3: Partial calculation
        wrong_average_3 = avg_data["data"][0]  # Just first value
        wrong_options.append((
            str(wrong_average_3),
            MisconceptionType.INCOMPLETE_REASONING,
            f"Used only one value",
            f"You said {wrong_average_3}, but that's just one value! Average needs all values: {' + '.join(map(str, avg_data['data']))} = {avg_data['sum']}, then ÷ {avg_data['count']} = {avg_data['average']}.",
            f"Average must include every single value in the calculation"
        ))
        
        random.shuffle(wrong_options)
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Data: {', '.join(map(str, avg_data['data']))}",
            f"Step 1: Add all values = {' + '.join(map(str, avg_data['data']))} = {avg_data['sum']}",
            f"Step 2: Count how many values = {avg_data['count']}",
            f"Step 3: Divide sum by count = {avg_data['sum']} ÷ {avg_data['count']} = {avg_data['average']}",
            f"Average: {avg_data['average']}"
        ]
        
        visual_diagram = self._render_average_diagram(avg_data)
        
        hints = [
            f"Hint 1: Add all the values: {' + '.join(map(str, avg_data['data']))} = {avg_data['sum']}",
            f"Hint 2: Count the values: {avg_data['count']}",
            f"Hint 3: Divide: {avg_data['sum']} ÷ {avg_data['count']}",
            f"Hint 4: Average = {avg_data['average']}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Calculating Averages",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Two steps: sum AND divide!",
            data_representation=f"Data: {avg_data['data']} | Sum: {avg_data['sum']} | Count: {avg_data['count']} | Average: {avg_data['average']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s average challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_median_finding(self) -> Question:
        """
        Median Finding - Finding the middle value in a sorted dataset
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Median finding scenarios (odd-length datasets for simplicity)
        median_scenarios = [
            {
                "context": "test marks",
                "unsorted": [85, 60, 75, 95, 70],
                "sorted": [60, 70, 75, 85, 95],
                "count": 5,
                "median_idx": 2,
                "median": 75,
                "description": "5 students' test scores"
            },
            {
                "context": "ages of children",
                "unsorted": [8, 12, 7, 9, 11],
                "sorted": [7, 8, 9, 11, 12],
                "count": 5,
                "median_idx": 2,
                "median": 9,
                "description": "ages of 5 children"
            },
            {
                "context": "book pages read",
                "unsorted": [120, 95, 140, 110, 125],
                "sorted": [95, 110, 120, 125, 140],
                "count": 5,
                "median_idx": 2,
                "median": 120,
                "description": "pages read from 5 books"
            },
            {
                "context": "daily steps",
                "unsorted": [5000, 8000, 6000, 7000, 9000],
                "sorted": [5000, 6000, 7000, 8000, 9000],
                "count": 5,
                "median_idx": 2,
                "median": 7000,
                "description": "daily steps over 5 days"
            }
        ]
        
        median_data = random.choice(median_scenarios)
        correct_answer = str(median_data["median"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"To find the median of {median_data['description']}, first sort them. The values are {', '.join(map(str, median_data['unsorted']))}. What's the median?",
            f"Arrange in order: {', '.join(map(str, median_data['sorted']))}. The median of {median_data['context']} is the middle value. What is it?",
            f"Given unsorted data {', '.join(map(str, median_data['unsorted']))}, find the median {median_data['context']}."
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "didn't sort the data first",
            "confused median with average",
            "picked the wrong middle position"
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Used unsorted first value
        wrong_options.append((
            str(median_data["unsorted"][0]),
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Used first unsorted value",
            f"You said {median_data['unsorted'][0]}, but median requires sorting first! Sorted: {', '.join(map(str, median_data['sorted']))}. Middle value: {median_data['median']}.",
            f"Always sort the data before finding the median"
        ))
        
        # Misconception 2: Average instead of median
        average_val = sum(median_data['sorted']) / len(median_data['sorted'])
        wrong_options.append((
            str(average_val),
            MisconceptionType.LOGICAL_DISCONNECT,
            f"Calculated average instead of median",
            f"You got {average_val}, but that's the average! Median is the middle of sorted data: {', '.join(map(str, median_data['sorted']))} → {median_data['median']}.",
            f"Median = middle value (not average)"
        ))
        
        # Misconception 3: Wrong position in sorted list
        wrong_idx = (median_data["median_idx"] + 1) % len(median_data['sorted'])
        wrong_median = median_data['sorted'][wrong_idx]
        wrong_options.append((
            str(wrong_median),
            MisconceptionType.INCOMPLETE_REASONING,
            f"Wrong middle position",
            f"You said {wrong_median}, but the middle of {', '.join(map(str, median_data['sorted']))} is {median_data['median']} (position {median_data['median_idx'] + 1}).",
            f"For {median_data['count']} values, the median is at position {median_data['median_idx'] + 1}"
        ))
        
        random.shuffle(wrong_options)
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Given data: {', '.join(map(str, median_data['unsorted']))}",
            f"Step 1: Sort the data = {', '.join(map(str, median_data['sorted']))}",
            f"Step 2: Find middle position = position {median_data['median_idx'] + 1} of {median_data['count']}",
            f"Step 3: Read the middle value = {median_data['median']}",
            f"Median: {median_data['median']}"
        ]
        
        visual_diagram = self._render_median_diagram(median_data)
        
        hints = [
            f"Hint 1: Unsorted: {', '.join(map(str, median_data['unsorted']))}",
            f"Hint 2: Sort first: {', '.join(map(str, median_data['sorted']))}",
            f"Hint 3: Find the middle position",
            f"Hint 4: Median = {median_data['median']}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Finding Median Values",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Sort first, then find middle!",
            data_representation=f"Unsorted: {median_data['unsorted']} | Sorted: {median_data['sorted']} | Median: {median_data['median']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s median challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_mode_identification(self) -> Question:
        """
        Mode Identification - Finding the most frequently occurring value
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Mode identification scenarios
        mode_scenarios = [
            {
                "context": "favorite colors",
                "data": ["red", "blue", "red", "green", "red", "blue"],
                "mode": "red",
                "frequency": 3,
                "description": "colors chosen by 6 students",
                "counts": {"red": 3, "blue": 2, "green": 1}
            },
            {
                "context": "shoe sizes",
                "data": [5, 5, 6, 5, 7, 6, 5],
                "mode": 5,
                "frequency": 4,
                "description": "shoe sizes of 7 people",
                "counts": {5: 4, 6: 2, 7: 1}
            },
            {
                "context": "ice cream flavors",
                "data": ["vanilla", "chocolate", "vanilla", "strawberry", "vanilla"],
                "mode": "vanilla",
                "frequency": 3,
                "description": "flavors chosen by 5 people",
                "counts": {"vanilla": 3, "chocolate": 1, "strawberry": 1}
            },
            {
                "context": "number of siblings",
                "data": [2, 1, 2, 2, 0, 1, 2],
                "mode": 2,
                "frequency": 4,
                "description": "number of siblings for 7 students",
                "counts": {2: 4, 1: 2, 0: 1}
            }
        ]
        
        mode_data = random.choice(mode_scenarios)
        correct_answer = str(mode_data["mode"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"In {mode_data['description']}, the values are {', '.join(map(str, mode_data['data']))}. What is the mode (most frequent)?",
            f"Finding the mode of {mode_data['context']}: {', '.join(map(str, mode_data['data']))}. Which appears most often?",
            f"Mode = most frequently occurring value. From {', '.join(map(str, mode_data['data']))}, what's the mode?"
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "confused mode with average",
            "didn't count frequencies correctly",
            "picked the first value"
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: First value
        wrong_options.append((
            str(mode_data["data"][0]),
            MisconceptionType.CONSTRAINT_VIOLATION,
            f"Used the first value",
            f"You said {mode_data['data'][0]}, but that's not the most frequent! {mode_data['mode']} appears {mode_data['frequency']} times, which is most often.",
            f"Mode = the value that appears most frequently"
        ))
        
        # Misconception 2: Used average instead of mode
        if isinstance(mode_data["data"][0], (int, float)):
            avg_val = sum(mode_data["data"]) / len(mode_data["data"])
            wrong_options.append((
                str(avg_val),
                MisconceptionType.LOGICAL_DISCONNECT,
                f"Calculated average instead of mode",
                f"You calculated {avg_val}, but that's the average! Mode is the most frequent value: {mode_data['mode']} (appears {mode_data['frequency']} times).",
                f"Mode ≠ average. Mode = most frequent value"
            ))
        else:
            wrong_options.append((
                mode_data["data"][1],
                MisconceptionType.LOGICAL_DISCONNECT,
                f"Picked a less frequent value",
                f"You said {mode_data['data'][1]}, but {mode_data['mode']} appears more often ({mode_data['frequency']} times vs {mode_data['counts'].get(mode_data['data'][1], 1)}).",
                f"Count frequencies carefully"
            ))
        
        # Misconception 3: Wrong frequency count
        other_values = [v for v in mode_data["counts"].keys() if v != mode_data["mode"]]
        if other_values:
            wrong_value = other_values[0]
            wrong_options.append((
                str(wrong_value),
                MisconceptionType.INCOMPLETE_REASONING,
                f"Miscounted frequencies",
                f"You said {wrong_value}, which appears {mode_data['counts'][wrong_value]} times. But {mode_data['mode']} appears {mode_data['frequency']} times (more frequent)!",
                f"The mode is always the value with the highest count"
            ))
        else:
            wrong_options.append((
                "No mode",
                MisconceptionType.INCOMPLETE_REASONING,
                f"Didn't find a mode",
                f"Every dataset has a mode! {mode_data['mode']} appears {mode_data['frequency']} times, making it the mode.",
                f"Mode = most frequent value (always exists)"
            ))
        
        random.shuffle(wrong_options)
        all_options = [correct_answer] + [opt[0] for opt in wrong_options[:3]]
        correct_idx = all_options.index(correct_answer)
        
        distractor_info_list = []
        wrong_count = 0
        for idx, option in enumerate(all_options):
            if idx != correct_idx and wrong_count < len(wrong_options):
                distractor_info_list.append(DistractorInfo(
                    value=wrong_options[wrong_count][0],
                    misconception_type=wrong_options[wrong_count][1],
                    description=wrong_options[wrong_count][2],
                    why_wrong=wrong_options[wrong_count][3],
                    teaching_point=wrong_options[wrong_count][4]
                ))
                wrong_count += 1
        
        # PHASE 4: Rich Rendering
        # =======================
        solution_steps = [
            f"Data: {', '.join(map(str, mode_data['data']))}",
            f"Count frequencies:",
            *[f"  {value}: appears {count} times" for value, count in sorted(mode_data['counts'].items(), key=lambda x: -x[1])],
            f"Most frequent: {mode_data['mode']} ({mode_data['frequency']} times)",
            f"Mode: {mode_data['mode']}"
        ]
        
        visual_diagram = self._render_mode_diagram(mode_data)
        
        hints = [
            f"Hint 1: Data: {', '.join(map(str, mode_data['data']))}",
            f"Hint 2: Count each value's frequency",
            f"Hint 3: {mode_data['mode']} appears {mode_data['frequency']} times",
            f"Hint 4: Mode = {mode_data['mode']} (most frequent)"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Finding the Mode",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Count carefully - mode is MOST frequent!",
            data_representation=f"Data: {mode_data['data']} | Frequencies: {mode_data['counts']} | Mode: {mode_data['mode']}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s mode challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question

    # ============================================================================
    # RENDERING HELPERS
    # ============================================================================

    def _render_average_diagram(self, avg_data: dict) -> dict:
        """
        Render average calculation visualization
        
        Args:
            avg_data: Dict with data, sum, count, average
        
        Returns:
            Dict with 'html' key containing visualization
        """
        html_content = f"""
        <div style="margin: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <h3 style="text-align: center;">Average Calculation</h3>
            
            <div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0;">
                <strong>Data:</strong> {', '.join(map(str, avg_data['data']))}
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background-color: #e3f2fd;">
                    <th style="border: 1px solid #999; padding: 8px;">Step</th>
                    <th style="border: 1px solid #999; padding: 8px;">Operation</th>
                    <th style="border: 1px solid #999; padding: 8px;">Result</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #999; padding: 8px;">1. Sum</td>
                    <td style="border: 1px solid #999; padding: 8px;">{' + '.join(map(str, avg_data['data']))}</td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{avg_data['sum']}</strong></td>
                </tr>
                <tr style="background-color: #f5f5f5;">
                    <td style="border: 1px solid #999; padding: 8px;">2. Count</td>
                    <td style="border: 1px solid #999; padding: 8px;">How many values?</td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{avg_data['count']}</strong></td>
                </tr>
                <tr style="background-color: #c8e6c9;">
                    <td style="border: 1px solid #999; padding: 8px;"><strong>3. Average</strong></td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong>{avg_data['sum']} ÷ {avg_data['count']}</strong></td>
                    <td style="border: 1px solid #999; padding: 8px;"><strong style="color: green;">{avg_data['average']}</strong></td>
                </tr>
            </table>
            
            <div style="background-color: #fff3e0; padding: 10px; border-left: 4px solid #ff9800;">
                <strong>Formula:</strong> Average = Sum of all values ÷ Number of values
            </div>
        </div>
        """
        
        return {"html": html_content}

    def _render_median_diagram(self, median_data: dict) -> dict:
        """
        Render median finding visualization
        
        Args:
            median_data: Dict with unsorted, sorted data, and median
        
        Returns:
            Dict with 'html' key containing visualization
        """
        # Build sorted values HTML with highlight on median
        sorted_values_html = ""
        for i, val in enumerate(median_data['sorted']):
            bg_color = "#c8e6c9" if i == median_data['median_idx'] else "white"
            sorted_values_html += f'<span style="display: inline-block; padding: 5px; margin: 3px; background-color: {bg_color}; border: 1px solid #999;">{val}</span>'
        
        html_content = f"""
        <div style="margin: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <h3 style="text-align: center;">Finding the Median</h3>
            
            <div style="background-color: #ffe0e0; padding: 10px; margin: 10px 0;">
                <strong>Unsorted:</strong> {', '.join(map(str, median_data['unsorted']))}
            </div>
            
            <div style="background-color: #e0f0ff; padding: 10px; margin: 10px 0;">
                <strong>Sorted:</strong> {', '.join(map(str, median_data['sorted']))}
            </div>
            
            <div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0; text-align: center;">
                {sorted_values_html}
            </div>
            
            <div style="background-color: #c8e6c9; padding: 10px; text-align: center;">
                <strong>Middle value (position {median_data['median_idx'] + 1} of {median_data['count']}):</strong> <span style="color: green; font-size: 18px;"><strong>{median_data['median']}</strong></span>
            </div>
            
            <div style="background-color: #fff3e0; padding: 10px; border-left: 4px solid #ff9800; margin-top: 10px;">
                <strong>Key:</strong> Sort first! Median = middle value of sorted data
            </div>
        </div>
        """
        
        return {"html": html_content}

    def _render_mode_diagram(self, mode_data: dict) -> dict:
        """
        Render mode identification visualization
        
        Args:
            mode_data: Dict with data and frequency counts
        
        Returns:
            Dict with 'html' key containing visualization
        """
        # Build frequency list HTML
        frequency_html = ""
        for v, count in sorted(mode_data['counts'].items(), key=lambda x: -x[1]):
            bg_color = "#c8e6c9" if v == mode_data['mode'] else "#f5f5f5"
            border_color = "green" if v == mode_data['mode'] else "#ccc"
            mode_label = "  ← MODE" if v == mode_data['mode'] else ""
            frequency_html += f'<li style="padding: 8px; margin: 5px 0; background-color: {bg_color}; border-radius: 3px; border-left: 4px solid {border_color};"><strong>{v}</strong>: {count} times{mode_label}</li>'
        
        html_content = f"""
        <div style="margin: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <h3 style="text-align: center;">Finding the Mode</h3>
            
            <div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0;">
                <strong>Data:</strong> {', '.join(map(str, mode_data['data']))}
            </div>
            
            <div style="margin: 15px 0;">
                <strong>Frequency Count:</strong>
                <ul style="list-style-type: none; padding: 0;">
                    {frequency_html}
                </ul>
            </div>
            
            <div style="background-color: #c8e6c9; padding: 10px; text-align: center; border-radius: 3px;">
                <strong>Mode = {mode_data['mode']}</strong> (appears {mode_data['frequency']} times - most frequent!)
            </div>
            
            <div style="background-color: #fff3e0; padding: 10px; border-left: 4px solid #ff9800; margin-top: 10px;">
                <strong>Key:</strong> Mode = value that appears MOST frequently
            </div>
        </div>
        """
        
        return {"html": html_content}
    #
    # For each _generate_* method:
    #
    # PHASE 1: Deterministic Skeleton
    # --------------------------------
    # def _generate_xxx(self) -> Question:
    #     # Generate parameters using pure Python/SymPy
    #     # Validate answer is correct (critical!)
    #     # Create MathSkeleton with parameters, solution, steps
    #     skeleton = MathSkeleton(...)
    #
    # PHASE 2: K.C. Nag Story
    # ----------------------
    # story_context = self.story_generator.generate_story_context(skeleton)
    # Or manually create StoryContext with:
    #   - concept_name: what we're learning
    #   - real_world_scenario: something from student's life
    #   - character_names: people in the story
    #   - narrative: the K.C. Nag story text
    #   - misconception_hooks: phrases that reveal traps
    #   - teaching_principles: how K.C. Nag would teach it
    #
    # PHASE 3: Misconception-Based Distractors
    # ----------------------------------------
    # For each of 3 misconceptions:
    #   distractor_info.append(DistractorInfo(
    #       value="...",  # What student sees
    #       misconception_type=MisconceptionType.XXX,
    #       description="...",  # Short label
    #       why_wrong="...",  # Why this is wrong
    #       teaching_point="..."  # What to learn instead
    #   ))
    #
    # PHASE 4: Rich Rendering
    # -----------------------
    # rich_content = self.renderer.render_rich_question(
    #     question_text=...,
    #     story_context=story_context,
    #     solution_steps=steps,
    #     explanation=...,
    #     visual_hint=...,
    #     progressive_hints=[hint1, hint2, hint3, hint4]
    # )
    #
    # PHASE 5: Question Object
    # -----------------------
    # question = Question(
    #     chapter=self.chapter,
    #     topic="...",
    #     logical_trap="K.C. Nag Trap: ...",
    #     data_representation="...",
    #     question_text=...,
    #     solution_steps=steps,
    #     answer=correct_answer,
    #     options=options,
    #     correct_option_index=correct_idx,
    #     distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
    #     trap_info=trap_info,
    #     bloom_info=bloom_info,
    #     rich_html_content=rich_content.get("html"),
    #     rich_narrative=rich_content.get("narrative"),
    #     visual_hints=rich_content.get("hints"),
    # )
    # self._validate_question(question)
    # return question

