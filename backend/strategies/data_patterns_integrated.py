"""
DATA PATTERNS - INTEGRATED STRATEGY
===================================

Hybrid Neuro-Symbolic approach for Data Patterns

Integrates:
1. Sequence logic with formula derivation
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Pattern overgeneralization, Index error)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class DataPatternsIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic sequence logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.DATA_PATTERNS
    chapter_name = "Data Patterns"
    description = "Data Patterns with hybrid neuro-symbolic approach"
    
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
            "sequence_continuation",
            "nth_term_finding",
            "pattern_rule_identification",
        ])
        
        if problem_type == "sequence_continuation":
            return self._generate_sequence_continuation()
        elif problem_type == "nth_term_finding":
            return self._generate_nth_term_finding()
        else:  # pattern_rule_identification
            return self._generate_pattern_rule_identification()
    
    def _generate_sequence_continuation(self) -> Question:
        """
        Sequence Continuation - Find the next number(s) in a sequence
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Different sequence types
        sequence_types = [
            {
                "type": "arithmetic",
                "sequence": [2, 5, 8, 11, 14],
                "difference": 3,
                "next_value": 17,
                "description": "Arithmetic sequence with difference 3"
            },
            {
                "type": "arithmetic",
                "sequence": [10, 7, 4, 1, -2],
                "difference": -3,
                "next_value": -5,
                "description": "Decreasing arithmetic sequence"
            },
            {
                "type": "geometric",
                "sequence": [2, 4, 8, 16, 32],
                "ratio": 2,
                "next_value": 64,
                "description": "Geometric sequence with ratio 2"
            },
            {
                "type": "fibonacci",
                "sequence": [1, 1, 2, 3, 5, 8],
                "next_value": 13,
                "description": "Fibonacci sequence (sum of previous two)"
            },
            {
                "type": "squares",
                "sequence": [1, 4, 9, 16, 25],
                "next_value": 36,
                "description": "Perfect squares (1², 2², 3², 4², 5²)"
            }
        ]
        
        seq_data = random.choice(sequence_types)
        correct_answer = str(seq_data["next_value"])
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Arjun sees a pattern in numbers: {', '.join(map(str, seq_data['sequence']))}. What's the next number? ({seq_data['description']})",
            f"A sequence follows a rule: {', '.join(map(str, seq_data['sequence']))} ... Continue the pattern. What comes next?",
            f"Priya observes a data pattern: {', '.join(map(str, seq_data['sequence']))}. If the pattern continues, what's the next value?",
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "didn't identify the correct pattern rule",
            "applied the wrong rule to the sequence",
            "guessed without finding the pattern",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Wrong rule application
        if seq_data["type"] == "arithmetic":
            wrong_diff = seq_data["difference"] + random.choice([-2, -1, 1, 2])
            wrong_value = seq_data["sequence"][-1] + wrong_diff
        elif seq_data["type"] == "geometric":
            wrong_ratio = seq_data["ratio"] + random.choice([-1, 1])
            wrong_value = seq_data["sequence"][-1] * wrong_ratio
        else:
            wrong_value = seq_data["next_value"] + random.choice([-5, -3, 3, 5])
        
        wrong_options.append((
            str(wrong_value),
            MisconceptionType.FORMULA_CONFUSION,
            "Applied wrong pattern rule",
            f"You got {wrong_value}, but the correct pattern gives {correct_answer}. Check the rule: {seq_data['description']}",
            f"Pattern rule: {seq_data['description']}. Follow it consistently to get {correct_answer}"
        ))
        
        # Misconception 2: Off-by-one or similar error
        wrong_value_2 = seq_data["next_value"] + random.choice([-2, -1, 1, 2])
        wrong_options.append((
            str(wrong_value_2),
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Close but made a calculation error",
            f"You said {wrong_value_2}, which is close but not exact. The correct answer is {correct_answer}.",
            f"Carefully apply the pattern: {seq_data['description']} → {correct_answer}"
        ))
        
        # Misconception 3: Confused with a similar sequence
        wrong_value_3 = seq_data["sequence"][-1] + random.choice([1, 2, 4, 5])
        if wrong_value_3 == seq_data["next_value"] or wrong_value_3 in seq_data["sequence"]:
            wrong_value_3 = seq_data["next_value"] + 7
        wrong_options.append((
            str(wrong_value_3),
            MisconceptionType.INCOMPLETE_REASONING,
            "Used a different pattern rule",
            f"You applied a different rule and got {wrong_value_3}. But this sequence follows: {seq_data['description']}, giving {correct_answer}.",
            f"Always verify your rule works for ALL given numbers in the sequence."
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
            f"Given Sequence: {', '.join(map(str, seq_data['sequence']))}",
            f"Pattern Type: {seq_data['description']}",
            f"Find the rule connecting consecutive numbers",
            f"Apply the rule to predict the next number",
            f"Next Number: {correct_answer}",
            f"Verification: Pattern {seq_data['description']} continues correctly"
        ]
        
        visual_diagram = self._render_sequence_diagram(seq_data["sequence"], seq_data["next_value"], seq_data["type"])
        
        hints = [
            f"Hint 1: Look at the differences (or ratios) between consecutive numbers",
            f"Hint 2: This is a {seq_data['type']} sequence",
            f"Hint 3: Pattern: {seq_data['description']}",
            f"Hint 4: The next number is {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Sequence Continuation and Pattern Finding",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Identify the rule first!",
            data_representation=f"{seq_data['type'].title()} sequence: {', '.join(map(str, seq_data['sequence']))}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s pattern challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_nth_term_finding(self) -> Question:
        """
        Nth Term Finding - Calculate a specific term in a sequence using a formula
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Sequences with formulas
        sequence_formulas = [
            {
                "formula": "a_n = 2n + 1",
                "rule": "multiply position by 2, then add 1",
                "terms": [3, 5, 7, 9, 11],
                "position": random.randint(6, 10),
                "calculate": lambda n: 2 * n + 1
            },
            {
                "formula": "a_n = n²",
                "rule": "position squared",
                "terms": [1, 4, 9, 16, 25],
                "position": random.randint(6, 10),
                "calculate": lambda n: n * n
            },
            {
                "formula": "a_n = 3n - 2",
                "rule": "multiply position by 3, then subtract 2",
                "terms": [1, 4, 7, 10, 13],
                "position": random.randint(6, 10),
                "calculate": lambda n: 3 * n - 2
            },
            {
                "formula": "a_n = 10 - n",
                "rule": "subtract position from 10",
                "terms": [9, 8, 7, 6, 5],
                "position": random.randint(6, 10),
                "calculate": lambda n: 10 - n
            }
        ]
        
        formula_data = random.choice(sequence_formulas)
        position = formula_data["position"]
        correct_answer = str(formula_data["calculate"](position))
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"A sequence follows the rule: {formula_data['formula']}. The first 5 terms are {formula_data['terms']}. What is the {position}th term?",
            f"Priya has a pattern where {formula_data['rule']}. Find the {position}th number in the sequence.",
            f"A formula generates a sequence: {formula_data['formula']}. Calculate the value at position {position}.",
        ])
        
        character = random.choice(["Arjun", "Priya", "Dev", "Sneha"])
        misconception_hook = random.choice([
            "forgot to use the correct formula",
            "made a calculation error in the formula",
            "confused position with value",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Wrong formula application
        wrong_answer_1 = str(formula_data["calculate"](position - 1))
        wrong_options.append((
            wrong_answer_1,
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Used wrong position or formula",
            f"You calculated the {position-1}th term instead of {position}th. For position {position}: {formula_data['formula']} = {correct_answer}",
            f"Always double-check: Use the exact position given. For position {position}, apply {formula_data['formula']}"
        ))
        
        # Misconception 2: Arithmetic error
        if position > 6:
            wrong_answer_2 = str(formula_data["calculate"](position) + random.choice([-3, -1, 1, 3]))
        else:
            wrong_answer_2 = str(formula_data["calculate"](position) - 2)
        wrong_options.append((
            wrong_answer_2,
            MisconceptionType.LOGICAL_DISCONNECT,
            "Calculation error in applying the formula",
            f"You got {wrong_answer_2}, but {formula_data['formula']} at position {position} gives {correct_answer}.",
            f"Recalculate carefully: For position {position}, {formula_data['rule']} = {correct_answer}"
        ))
        
        # Misconception 3: Using position from list instead of actual position
        wrong_answer_3 = str(formula_data["terms"][2] if len(formula_data["terms"]) > 2 else formula_data["terms"][-1])
        if wrong_answer_3 == correct_answer:
            wrong_answer_3 = str(int(correct_answer) + 5)
        wrong_options.append((
            wrong_answer_3,
            MisconceptionType.INCOMPLETE_REASONING,
            "Confused a value from the given list with the answer",
            f"You may have picked a number from the sequence list, but you need to calculate position {position}. The answer is {correct_answer}.",
            f"The formula works for ANY position. For position {position}: {correct_answer}"
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
            f"Formula: {formula_data['formula']}",
            f"Rule: {formula_data['rule']}",
            f"Given sequence (first 5 terms): {formula_data['terms']}",
            f"Find: {position}th term",
            f"Substituting n = {position} into {formula_data['formula']}",
            f"Answer: {correct_answer}",
            f"Verification: Using formula confirms {correct_answer} is correct"
        ]
        
        visual_diagram = self._render_nth_term_diagram(formula_data["terms"], position, correct_answer, formula_data["formula"])
        
        hints = [
            f"Hint 1: The formula is {formula_data['formula']}",
            f"Hint 2: We need the {position}th term",
            f"Hint 3: Substitute n = {position} into the formula",
            f"Hint 4: {formula_data['formula']} with n = {position} gives {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Finding Nth Term Using Formulas",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Use the formula carefully!",
            data_representation=f"Formula {formula_data['formula']} | Position {position}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s formula challenge: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_pattern_rule_identification(self) -> Question:
        """
        Pattern Rule Identification - Identify which formula/rule generates a sequence
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        # Multiple rules to choose from
        rules_set = [
            {
                "sequence": [2, 4, 6, 8, 10],
                "correct_rule": "2n (even numbers)",
                "wrong_rules": ["n + 1", "n²", "2n + 1"],
                "description": "All even numbers: each term is 2 times its position"
            },
            {
                "sequence": [1, 3, 5, 7, 9],
                "correct_rule": "2n - 1 (odd numbers)",
                "wrong_rules": ["2n", "n + 2", "3n - 2"],
                "description": "All odd numbers: each term is 2 times position minus 1"
            },
            {
                "sequence": [2, 6, 12, 20, 30],
                "correct_rule": "n(n + 1) (oblong numbers)",
                "wrong_rules": ["n²", "2n + 2", "n³"],
                "description": "Product of consecutive numbers: position times (position + 1)"
            },
            {
                "sequence": [1, 8, 27, 64, 125],
                "correct_rule": "n³ (perfect cubes)",
                "wrong_rules": ["n²", "3n", "2n²"],
                "description": "Perfect cubes: each position cubed"
            }
        ]
        
        rules_data = random.choice(rules_set)
        correct_answer = rules_data["correct_rule"]
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Dev observes a sequence: {rules_data['sequence']}. Which rule generates this pattern? ({rules_data['description']})",
            f"A sequence shows: {rules_data['sequence']}. What formula creates this pattern?",
            f"Priya analyzes numbers: {rules_data['sequence']}. Which mathematical rule is behind this sequence?",
        ])
        
        character = random.choice(["Dev", "Priya", "Arjun", "Sneha"])
        misconception_hook = random.choice([
            "confused similar-looking rules",
            "didn't test the rule on all terms",
            "applied incomplete rule verification",
        ])
        
        # Create multiple choice options
        all_rule_options = [correct_answer] + rules_data["wrong_rules"][:3]
        random.shuffle(all_rule_options)
        correct_idx = all_rule_options.index(correct_answer)
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        for wrong_rule in rules_data["wrong_rules"][:3]:
            if wrong_rule == "n²":
                wrong_options.append((
                    wrong_rule,
                    MisconceptionType.FORMULA_CONFUSION,
                    f"Said {wrong_rule} but that's wrong",
                    f"You chose {wrong_rule}, but that doesn't match the sequence. Check: {rules_data['sequence']}. The correct rule is {correct_answer}.",
                    f"Test the rule on each term: {correct_answer} works for all!"
                ))
            elif wrong_rule == "n + 1":
                wrong_options.append((
                    wrong_rule,
                    MisconceptionType.CONSTRAINT_VIOLATION,
                    f"Said {wrong_rule} but pattern doesn't match",
                    f"The rule {wrong_rule} doesn't produce this sequence. Verify: {correct_answer} gives {rules_data['sequence']}",
                    f"Always test your rule on every term in the sequence."
                ))
            else:
                wrong_options.append((
                    wrong_rule,
                    MisconceptionType.INCOMPLETE_REASONING,
                    f"Used {wrong_rule} without full verification",
                    f"That rule doesn't work. Check: {correct_answer} creates the sequence {rules_data['sequence']}",
                    f"Match formula to sequence: {correct_answer} is the rule."
                ))
        
        distractor_info_list = []
        wrong_count = 0
        for idx, rule in enumerate(all_rule_options):
            if rule != correct_answer and wrong_count < len(wrong_options):
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
            f"Given Sequence: {rules_data['sequence']}",
            f"Analyze each term and its position relationship",
            f"Test possible rules against each term",
            f"Verify rule works for ALL terms",
            f"Correct Rule: {correct_answer}",
            f"Verification: {correct_answer} produces exactly {rules_data['sequence']}"
        ]
        
        visual_diagram = self._render_rule_identification_diagram(rules_data["sequence"], correct_answer, all_rule_options)
        
        hints = [
            f"Hint 1: The sequence is {rules_data['sequence']}",
            f"Hint 2: Analyze the relationship between position and value",
            f"Hint 3: {rules_data['description']}",
            f"Hint 4: The rule is {correct_answer}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Identifying Pattern Rules and Formulas",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Test each rule carefully!",
            data_representation=f"Sequence {rules_data['sequence']} | Rule: {correct_answer}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_rule_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s rule identification: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question


    # ======================================
    # RENDERING HELPER METHODS
    # ======================================
    
    def _render_sequence_diagram(self, sequence: list, next_value: int, seq_type: str) -> dict:
        """Render a sequence diagram with pattern visualization"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Sequence Pattern</h3>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; align-items: flex-start;">
        """
        
        # Show sequence with boxes
        html += """
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Given Sequence</p>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 15px;">
        """
        
        for i, val in enumerate(sequence):
            html += f'''
                        <div style="padding: 10px 15px; border: 2px solid #2563eb; border-radius: 4px; background: #dbeafe; font-weight: bold; min-width: 40px; text-align: center;">
                            {val}
                        </div>
            '''
        
        html += f'''
                    </div>
                    <div style="display: flex; gap: 5px; flex-wrap: wrap; justify-content: center; margin-bottom: 15px; font-size: 12px; color: #666;">
        '''
        
        # Show differences
        for i in range(len(sequence) - 1):
            diff = sequence[i + 1] - sequence[i]
            html += f'<span style="padding: 4px 8px; background: #fef3c7;">+{diff}</span>' if diff > 0 else f'<span style="padding: 4px 8px; background: #fecaca;">{diff}</span>'
        
        html += f"""
                    </div>
                    <div style="padding: 12px; background: white; border-radius: 4px; border-left: 4px solid #10b981;">
                        <p style="margin: 0 0 5px 0; font-weight: bold;">Next value:</p>
                        <p style="margin: 0; font-size: 18px; color: #10b981; font-weight: bold;">{next_value}</p>
                    </div>
                </div>
        """
        
        # Show rule explanation
        html += f"""
                <div style="padding: 15px; background: white; border-radius: 4px; border-left: 4px solid #3b82f6; max-width: 300px;">
                    <p style="margin: 0 0 10px 0; font-weight: bold;">Pattern Analysis</p>
                    <table style="width: 100%; font-size: 12px; text-align: left;">
                        <tr style="border-bottom: 1px solid #e5e7eb;">
                            <td style="padding: 6px 0;">Position</td>
                            <td style="padding: 6px 0;">Value</td>
        """
        
        for i, val in enumerate(sequence, 1):
            html += f"""
                            <tr style="border-bottom: 1px solid #f3f4f6;">
                                <td style="padding: 6px 0;">{i}</td>
                                <td style="padding: 6px 0;"><strong>{val}</strong></td>
                            </tr>
            """
        
        html += f"""
                        <tr style="border-bottom: none; font-weight: bold; color: #10b981;">
                            <td style="padding: 6px 0;">{len(sequence) + 1}</td>
                            <td style="padding: 6px 0;"><strong>{next_value}</strong></td>
                        </tr>
                    </table>
                    <p style="margin: 10px 0 0 0; font-size: 11px; color: #666;">Type: {seq_type}</p>
                </div>
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_nth_term_diagram(self, terms: list, position: int, answer: str, formula: str) -> dict:
        """Render nth term finding diagram with formula application"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Finding the {position}th Term</h3>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
        """
        
        # Show given terms
        html += """
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Given Terms</p>
                    <table style="border-collapse: collapse; background: white; border-radius: 4px; overflow: hidden;">
                        <tr style="background: #e0e7ff;">
                            <td style="padding: 8px 12px; border: 1px solid #c7d2fe; font-weight: bold;">Position (n)</td>
                            <td style="padding: 8px 12px; border: 1px solid #c7d2fe; font-weight: bold;">Term Value</td>
                        </tr>
        """
        
        for i, term in enumerate(terms, 1):
            html += f"""
                        <tr style="background: #f0f9ff;">
                            <td style="padding: 8px 12px; border: 1px solid #c7d2fe;">{i}</td>
                            <td style="padding: 8px 12px; border: 1px solid #c7d2fe;"><strong>{term}</strong></td>
                        </tr>
            """
        
        html += f"""
                    </table>
                </div>
        """
        
        # Show formula application
        html += f"""
                <div style="padding: 15px; background: white; border-radius: 4px; border-left: 4px solid #3b82f6; max-width: 320px;">
                    <p style="margin: 0 0 10px 0; font-weight: bold;">Formula Application</p>
                    <p style="margin: 8px 0; font-size: 14px;"><strong>Formula:</strong> {formula}</p>
                    
                    <div style="margin: 12px 0; padding: 10px; background: #fef3c7; border-radius: 4px;">
                        <p style="margin: 0 0 5px 0; font-size: 12px; color: #666;">For position n = {position}:</p>
                        <p style="margin: 0; font-weight: bold; font-size: 13px;">{formula.replace('n', str(position))}</p>
                    </div>
                    
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #e5e7eb;">
                        <p style="margin: 0 0 5px 0; font-size: 12px; color: #666;">Answer:</p>
                        <p style="margin: 0; font-size: 16px; color: #059669; font-weight: bold;">{answer}</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_rule_identification_diagram(self, sequence: list, correct_rule: str, all_options: list) -> dict:
        """Render rule identification diagram with formula testing"""
        
        html = f"""
        <div style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="text-align: center; margin-top: 0;">Identifying the Rule</h3>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
        """
        
        # Show sequence
        html += """
                <div style="text-align: center;">
                    <p style="font-weight: bold; margin-bottom: 10px;">Sequence Analysis</p>
                    <div style="display: grid; grid-template-columns: auto auto; gap: 10px; background: white; padding: 15px; border-radius: 4px;">
                        <div style="font-weight: bold; color: #666;">Position</div>
                        <div style="font-weight: bold; color: #666;">Value</div>
        """
        
        for i, val in enumerate(sequence, 1):
            html += f"""
                        <div style="padding: 6px 8px; text-align: center; background: #f3f4f6; border-radius: 2px;">{i}</div>
                        <div style="padding: 6px 8px; text-align: center; background: #dbeafe; border-radius: 2px; font-weight: bold;">{val}</div>
            """
        
        html += """
                    </div>
                </div>
        """
        
        # Show rule options
        html += f"""
                <div style="padding: 15px; background: white; border-radius: 4px; border-left: 4px solid #3b82f6; max-width: 300px;">
                    <p style="margin: 0 0 12px 0; font-weight: bold;">Rule Options</p>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
        """
        
        for option in all_options:
            is_correct = option == correct_rule
            html += f"""
                        <div style="padding: 10px; border-radius: 4px; border-left: 4px solid {'#10b981' if is_correct else '#9ca3af'}; background: {'#ecfdf5' if is_correct else '#f3f4f6'};">
                            <div style="font-weight: bold; color: {'#059669' if is_correct else '#4b5563'};">{option}</div>
                            <div style="font-size: 11px; color: #666; margin-top: 3px;">
                                {'✓ Generates the sequence' if is_correct else '✗ Does not match'}
                            </div>
                        </div>
            """
        
        html += f"""
                    </div>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #e5e7eb;">
                        <p style="margin: 0 0 4px 0; font-size: 12px; color: #666;">Correct Rule:</p>
                        <p style="margin: 0; font-weight: bold; color: #059669; font-size: 13px;">{correct_rule}</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return {"html": html}

