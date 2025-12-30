"""
MULTIPLICATION & DIVISION - INTEGRATED STRATEGY
===============================================

Hybrid Neuro-Symbolic approach for Multiplication & Division

Integrates:
1. SymPy expression generation and symbolic computation
2. K.C. Nag real-world scenarios (culturally relevant storytelling)
3. Misconception-based distractors (Commutativity overextension, Zero confusion)
4. Rich HTML rendering (visual pedagogical aids)
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any
import sympy
from sympy import symbols, expand, simplify

# Import hybrid system components
from content.generators.multiplication_division import (
    MultiplicationDivisionGenerator,
    MultiplicationDivisionConcept,
    DifficultyLevel as HybridDifficultyLevel,
)


class MultiplicationDivisionIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic sympy logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.MULTIPLICATION_DIVISION
    chapter_name = "Multiplication & Division"
    description = "Multiplication & Division with hybrid neuro-symbolic approach"
    
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
            "multiplication_facts",
            "division_with_remainder",
            "word_problems",
        ])
        
        if problem_type == "multiplication_facts":
            return self._generate_multiplication_facts()
        elif problem_type == "division_with_remainder":
            return self._generate_division_with_remainder()
        else:  # word_problems
            return self._generate_word_problems()
    
    def _generate_multiplication_facts(self) -> Question:
        """
        Multiplication Facts - Using SymPy for symbolic computation
        
        PHASE 1: Deterministic Skeleton (SymPy symbolic expressions)
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton with SymPy
        # ===========================================
        multiplier = random.randint(6, 12)
        multiplicand = random.randint(6, 12)
        
        # Use SymPy to symbolically compute multiplication
        m, d = symbols('m d')
        expression = m * d
        correct_product = int(expression.subs([(m, multiplier), (d, multiplicand)]))
        correct_answer = str(correct_product)
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Ravi arranges {multiplier} rows of chairs with {multiplicand} chairs in each row. How many chairs in total?",
            f"A store has {multiplier} shelves with {multiplicand} books on each shelf. How many books in total?",
            f"The school has {multiplier} classes with {multiplicand} students in each class. How many students?",
            f"A farmer plants {multiplier} groups of {multiplicand} plants each. How many plants altogether?",
            f"A bakery makes {multiplier} batches of {multiplicand} cookies each. How many cookies in total?",
        ])
        
        character = random.choice(["Arjun", "Meera", "Dev", "Priya"])
        misconception_hook = random.choice([
            "tried adding instead of multiplying",
            "confused the order of numbers",
            "miscounted the groups or items",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Adding instead of multiplying
        wrong_add = multiplier + multiplicand
        wrong_options.append((
            str(wrong_add),
            MisconceptionType.FORMULA_CONFUSION,
            "Added instead of multiplied",
            f"You added {multiplier} + {multiplicand} = {wrong_add}, but this is ADDITION, not MULTIPLICATION. Multiplication means 'groups of'.",
            f"Multiplication: {multiplier} groups of {multiplicand} = {multiplier} × {multiplicand} = {correct_product}"
        ))
        
        # Misconception 2: Off by one (counting error)
        wrong_count = correct_product - random.choice([5, 10, 15])
        if wrong_count > 0:
            wrong_options.append((
                str(wrong_count),
                MisconceptionType.INCOMPLETE_REASONING,
                "Counting error",
                f"You might have miscounted or forgotten some items. Double-check by adding: {multiplier} + {multiplier} + ... ({multiplicand} times)",
                f"Systematic check: Use array or repeated addition to verify {multiplier} × {multiplicand} = {correct_product}"
            ))
        
        # Misconception 3: Wrong order or confused operation
        wrong_order = multiplicand * (multiplier - 1)
        wrong_options.append((
            str(wrong_order),
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Miscalculation",
            f"This doesn't match {multiplier} × {multiplicand}. Multiplication is commutative (order doesn't matter), but the COUNT must be exact.",
            f"Always verify: {multiplier} × {multiplicand} = {correct_product}. Use rows and columns to visualize."
        ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
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
            f"Problem: {multiplier} × {multiplicand}",
            f"Interpretation: {multiplier} groups of {multiplicand} items each",
            f"Calculation: {' + '.join([str(multiplicand)] * min(multiplier, 5))} + ...",
            f"Total: {correct_product}"
        ]
        
        visual_diagram = self._render_multiplication_array(multiplier, multiplicand)
        
        hints = [
            f"Hint 1: Multiplication means 'groups of'",
            f"Hint 2: We have {multiplier} groups with {multiplicand} items in each group",
            f"Hint 3: Repeated addition: {multiplicand} + {multiplicand} + ... ({multiplier} times)",
            f"Hint 4: The answer is {correct_product}"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Multiplication Facts",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Remember: × means GROUPS of. A × B = A groups with B items each.",
            data_representation=f"Array with {multiplier} rows and {multiplicand} columns",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.REMEMBER],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s multiplication problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_division_with_remainder(self) -> Question:
        """
        Division With Remainder
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        dividend = random.randint(20, 100)
        divisor = random.randint(4, 12)
        
        quotient = dividend // divisor
        remainder = dividend % divisor
        
        # Create answer in format "quotient R remainder" or "quotient remainder"
        correct_answer = f"{quotient} R {remainder}"
        
        # PHASE 2: K.C. Nag Story
        # =======================
        scenario = random.choice([
            f"Ravi has {dividend} candies to share equally among {divisor} friends. Each friend gets some, with some left over. How many candies does each friend get, and how many are left?",
            f"A baker has {dividend} cookies and wants to pack them into boxes of {divisor}. How many full boxes can be made, and how many cookies remain?",
            f"The school distributes {dividend} pencils equally to {divisor} classrooms. Each classroom gets some pencils, with some extra. How many does each get, and what's left over?",
            f"A farmer has {dividend} apples to put into {divisor} baskets equally. How many apples per basket, and how many are left?",
            f"A toy store has {dividend} toys to arrange on {divisor} shelves. How many toys per shelf, and how many extra?",
        ])
        
        character = random.choice(["Ananya", "Rohan", "Priya", "Dev"])
        misconception_hook = random.choice([
            "forgot about the remainder",
            "used the remainder as the quotient",
            "miscalculated the division",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Ignoring the remainder (just giving quotient)
        wrong_ignore = str(quotient)
        wrong_options.append((
            wrong_ignore,
            MisconceptionType.INCOMPLETE_REASONING,
            "Forgot remainder",
            f"You gave {quotient}, but this ignores the {remainder} items left over. Division with remainders requires both the quotient AND the remainder.",
            f"Complete answer: {quotient} groups of {divisor} with {remainder} left over = {quotient} R {remainder}"
        ))
        
        # Misconception 2: Using remainder as if it's the quotient
        if remainder > 0:
            wrong_remainder_as_quotient = f"{remainder} R {quotient}"
            wrong_options.append((
                wrong_remainder_as_quotient,
                MisconceptionType.FORMULA_CONFUSION,
                "Swapped quotient and remainder",
                f"You wrote {remainder} R {quotient}, but this is backwards. The quotient ({quotient}) should be the main answer.",
                f"Correct format: quotient (how many in each group) R remainder (what's left) = {quotient} R {remainder}"
            ))
        
        # Misconception 3: Wrong calculation (off by 1 or similar)
        wrong_calculation = f"{quotient + 1} R {max(0, remainder - divisor)}"
        wrong_options.append((
            wrong_calculation,
            MisconceptionType.CONSTRAINT_VIOLATION,
            "Miscalculation",
            f"The calculation doesn't match {dividend} ÷ {divisor}. Double-check: {divisor} × {quotient} + {remainder} = {dividend}",
            f"Verify division using: divisor × quotient + remainder = dividend"
        ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
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
            f"Problem: {dividend} ÷ {divisor}",
            f"Step 1: How many groups of {divisor} fit into {dividend}?",
            f"Step 2: {divisor} × {quotient} = {divisor * quotient}",
            f"Step 3: What's left over? {dividend} - {divisor * quotient} = {remainder}",
            f"Answer: {quotient} groups with {remainder} remaining = {quotient} R {remainder}"
        ]
        
        visual_diagram = self._render_division_diagram(dividend, divisor, quotient, remainder)
        
        hints = [
            f"Hint 1: Division means 'sharing equally'",
            f"Hint 2: We're dividing {dividend} by {divisor}",
            f"Hint 3: How many {divisor}s fit into {dividend}? ({quotient} times with {remainder} left)",
            f"Hint 4: Answer format: {quotient} R {remainder} (quotient R remainder)"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Division with Remainder",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Always express both: quotient (how many per group) AND remainder (what's left).",
            data_representation=f"{dividend} items grouped into sets of {divisor}",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.UNDERSTAND],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s division problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question
    
    def _generate_word_problems(self) -> Question:
        """
        Word Problems - Mixed Multiplication & Division
        
        PHASE 1: Deterministic Skeleton
        PHASE 2: K.C. Nag Story
        PHASE 3: Misconception-Based Distractors
        PHASE 4: Rich Rendering
        PHASE 5: Question Object
        """
        # PHASE 1: Deterministic Skeleton
        # ================================
        problem_type = random.choice(["mult_groups", "div_equal_share", "mult_then_compare"])
        
        if problem_type == "mult_groups":
            # Mary buys X boxes with Y items each. How many total?
            num_boxes = random.randint(4, 9)
            items_per_box = random.randint(6, 12)
            correct_total = num_boxes * items_per_box
            scenario = f"Mary buys {num_boxes} boxes of cookies. Each box has {items_per_box} cookies. How many cookies in total?"
            correct_answer = str(correct_total)
            operation = "multiplication"
        elif problem_type == "div_equal_share":
            # David has X items to share equally among Y people. How many each?
            total_items = random.randint(30, 100)
            num_people = random.randint(5, 10)
            correct_per_person = total_items // num_people
            remainder_items = total_items % num_people
            scenario = f"David has {total_items} marbles to share equally among {num_people} friends. How many marbles does each friend get?"
            correct_answer = str(correct_per_person)
            operation = "division"
        else:
            # Raj buys X at $Y each. His brother buys Y at $X each. Who spends more?
            item1_qty = random.randint(3, 8)
            item1_price = random.randint(5, 15)
            item2_qty = item1_price
            item2_price = item1_qty
            
            raj_total = item1_qty * item1_price
            brother_total = item2_qty * item2_price
            
            if raj_total > brother_total:
                scenario = f"Raj buys {item1_qty} notebooks at ${item1_price} each. His brother buys {item2_qty} pens at ${item2_price} each. How much more does Raj spend?"
                correct_answer = str(raj_total - brother_total)
                operation = "comparison"
            else:
                scenario = f"Raj buys {item1_qty} notebooks at ${item1_price} each. His brother buys {item2_qty} pens at ${item2_price} each. How much more does his brother spend?"
                correct_answer = str(brother_total - raj_total)
                operation = "comparison"
        
        # PHASE 2: K.C. Nag Story
        # =======================
        character = random.choice(["Rahul", "Priya", "Vikram", "Sneha"])
        misconception_hook = random.choice([
            "didn't recognize which operation to use",
            "calculated but forgot to answer the actual question",
            "misread the numbers or relationships",
        ])
        
        # PHASE 3: Misconception-Based Distractors
        # ========================================
        wrong_options = []
        
        # Misconception 1: Wrong operation
        if operation == "multiplication":
            wrong_operation = num_boxes + items_per_box
            wrong_options.append((
                str(wrong_operation),
                MisconceptionType.FORMULA_CONFUSION,
                "Added instead of multiplied",
                f"You added {num_boxes} + {items_per_box} = {wrong_operation}, but the problem asks for total cookies (multiply).",
                "Key phrase: 'X groups of Y' means multiply. {num_boxes} boxes × {items_per_box} cookies/box = {correct_total} cookies"
            ))
        elif operation == "division":
            wrong_operation = total_items + num_people
            wrong_options.append((
                str(wrong_operation),
                MisconceptionType.FORMULA_CONFUSION,
                "Added instead of divided",
                f"You added {total_items} + {num_people} = {wrong_operation}, but we need to divide to share equally.",
                f"Key phrase: 'share equally' means divide. {total_items} marbles ÷ {num_people} friends = {correct_per_person} each"
            ))
        else:
            wrong_operation = item1_qty + item1_price
            wrong_options.append((
                str(wrong_operation),
                MisconceptionType.FORMULA_CONFUSION,
                "Wrong operation",
                f"You calculated Raj's cost as {item1_qty} + {item1_price} = {wrong_operation}, but we need {item1_qty} × ${item1_price}.",
                f"Cost = quantity × price. Raj spends ${raj_total}, brother spends ${brother_total}."
            ))
        
        # Misconception 2: Partial calculation (didn't complete the problem)
        if operation == "multiplication":
            partial = num_boxes
            wrong_options.append((
                str(partial),
                MisconceptionType.INCOMPLETE_REASONING,
                "Incomplete answer",
                f"You gave {partial}, but that's just the number of boxes. We need TOTAL cookies: {num_boxes} × {items_per_box} = {correct_total}",
                "Always answer the ACTUAL question being asked, not just an intermediate step."
            ))
        elif operation == "division":
            partial = total_items
            wrong_options.append((
                str(partial),
                MisconceptionType.INCOMPLETE_REASONING,
                "Incomplete answer",
                f"You gave {partial}, but that's the total marbles, not how many each friend gets.",
                f"Share equally: {total_items} ÷ {num_people} = {correct_per_person} per friend"
            ))
        else:
            partial = raj_total
            wrong_options.append((
                str(partial),
                MisconceptionType.INCOMPLETE_REASONING,
                "Incomplete answer",
                f"You gave Raj's cost (${partial}), but the question asks how much MORE he spends.",
                f"Difference: ${raj_total} - ${brother_total} = ${correct_answer}"
            ))
        
        # Misconception 3: Distractor based on problem specifics
        if operation == "multiplication":
            wrong_distractor = num_boxes * (items_per_box - 1)
            wrong_options.append((
                str(wrong_distractor),
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Miscalculation",
                f"This answer uses {items_per_box - 1} instead of {items_per_box} cookies per box.",
                f"Double-check the numbers in the problem: {num_boxes} boxes × {items_per_box} cookies each = {correct_total}"
            ))
        elif operation == "division":
            wrong_distractor = correct_per_person + 1
            wrong_options.append((
                str(wrong_distractor),
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Off by one",
                f"This is close but not exact. Check: {num_people} × {wrong_distractor} = {num_people * wrong_distractor} (too many)",
                f"Exact division: {total_items} ÷ {num_people} = {correct_per_person} with {remainder_items} left over"
            ))
        else:
            wrong_distractor = abs(raj_total - brother_total) + 5
            wrong_options.append((
                str(wrong_distractor),
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Miscalculation",
                f"Recalculate carefully: ${raj_total} - ${brother_total} = ${correct_answer}, not ${wrong_distractor}",
                "Verify by working through each step: Raj buys X at $Y, brother buys Y at $X."
            ))
        
        random.shuffle(wrong_options)
        
        # Prepare options
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
        if operation == "multiplication":
            solution_steps = [
                f"Problem: {scenario}",
                f"Operation: Multiplication (groups)",
                f"Calculation: {num_boxes} × {items_per_box} = {correct_total}",
                f"Answer: {correct_total} cookies"
            ]
        elif operation == "division":
            solution_steps = [
                f"Problem: {scenario}",
                f"Operation: Division (share equally)",
                f"Calculation: {total_items} ÷ {num_people} = {correct_per_person}",
                f"Answer: {correct_per_person} marbles per friend"
            ]
        else:
            solution_steps = [
                f"Problem: {scenario}",
                f"Step 1: Raj's cost: {item1_qty} × ${item1_price} = ${raj_total}",
                f"Step 2: Brother's cost: {item2_qty} × ${item2_price} = ${brother_total}",
                f"Step 3: Difference: ${max(raj_total, brother_total)} - ${min(raj_total, brother_total)} = ${correct_answer}",
                f"Answer: ${correct_answer}"
            ]
        
        visual_diagram = self._render_word_problem_visualization(operation)
        
        hints = [
            f"Hint 1: Read the problem carefully and identify what it's asking",
            f"Hint 2: Look for key words: 'each' (multiply), 'share' (divide), 'how many total' (add/multiply)",
            f"Hint 3: Set up the calculation correctly",
            f"Hint 4: Make sure you answer the ACTUAL question being asked"
        ]
        
        # PHASE 5: Question Object
        # ========================
        question = Question(
            chapter=self.chapter,
            topic="Word Problems - Multiplication & Division",
            logical_trap=f"K.C. Nag Trap: {character} {misconception_hook}. Read carefully: identify the operation and answer the right question!",
            data_representation="Real-world scenario requiring calculation",
            question_text=scenario,
            solution_steps=solution_steps,
            answer=correct_answer,
            options=all_options,
            correct_option_index=correct_idx,
            distractor_info=DistractorSet(correct_answer=correct_answer, distractors=[d for d in distractor_info_list if d.value != correct_answer]),
            trap_info=None,
            bloom_info=BLOOM_DEFINITIONS[BloomLevel.APPLY],
            rich_html_content=visual_diagram.get("html", ""),
            rich_narrative=f"{character}'s word problem: {scenario}",
            visual_hints=hints,
        )
        
        self._validate_question(question)
        return question


    # ==================== HELPER RENDERING METHODS ====================
    
    def _render_multiplication_array(self, rows: int, cols: int) -> Dict[str, str]:
        """
        Render multiplication as an array/grid
        Shows rows × columns visualization
        """
        html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Multiplication Array: {rows} × {cols}</h4>
            
            <div style="margin: 20px auto; display: flex; justify-content: center;">
                <div style="display: grid; grid-template-columns: repeat({min(cols, 12)}, 25px); grid-template-rows: repeat({min(rows, 12)}, 25px); gap: 2px; padding: 10px; background: #fff; border: 2px solid #2196F3;">
        """
        
        for i in range(min(rows * cols, 144)):
            html += f'<div style="background: #2196F3; border: 1px solid #1565c0;"></div>'
        
        html += f"""
                </div>
                
                <div style="margin-left: 20px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">{rows} rows</div>
                    <div style="font-size: 14px; margin: 10px 0;">&times;</div>
                    <div style="font-size: 18px; font-weight: bold; color: #d32f2f;">{cols} per row</div>
                    <div style="font-size: 14px; margin: 10px 0;">=</div>
                    <div style="font-size: 20px; font-weight: bold; color: #4CAF50;">{rows * cols} total</div>
                </div>
            </div>
            
            <div style="margin: 20px 0; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                <strong>Multiplication Fact:</strong> {rows} × {cols} = {rows * cols}<br>
                <strong>What it means:</strong> {rows} groups with {cols} items each = {rows * cols} items total<br>
                <strong>Repeated Addition:</strong> {cols} + {cols} + ... ({rows} times) = {rows * cols}
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_division_diagram(self, dividend: int, divisor: int, quotient: int, remainder: int) -> Dict[str, str]:
        """
        Render division process with groups
        Shows how many complete groups and what's left over
        """
        html = f"""
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Division: {dividend} ÷ {divisor}</h4>
            
            <div style="margin: 20px 0; padding: 10px; background: #fff3e0; border-left: 4px solid #ff9800;">
                <strong>Problem:</strong> Divide {dividend} items into groups of {divisor}<br>
                <strong>Solution:</strong><br>
                &nbsp;&nbsp;• How many complete groups? <span style="color: #d32f2f; font-weight: bold;">{quotient}</span><br>
                &nbsp;&nbsp;• How many left over? <span style="color: #d32f2f; font-weight: bold;">{remainder}</span><br>
                <strong>Answer:</strong> {quotient} groups of {divisor} with {remainder} remaining
            </div>
            
            <div style="margin: 20px 0;">
                <strong>Verification:</strong><br>
                <div style="background: #e8f5e9; padding: 10px; margin: 10px 0; border-radius: 4px;">
                    {divisor} × {quotient} + {remainder} = {divisor * quotient} + {remainder} = {dividend} ✓
                </div>
            </div>
            
            <div style="margin: 20px 0; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                <strong>Division Fact:</strong> {dividend} ÷ {divisor} = {quotient} R {remainder}<br>
                <strong>What it means:</strong> {dividend} items shared among {divisor} people = {quotient} each with {remainder} left<br>
                <strong>Format:</strong> Quotient R Remainder (Quotient = how many each, Remainder = what's left)
            </div>
        </div>
        """
        
        return {"html": html}
    
    def _render_word_problem_visualization(self, operation: str) -> Dict[str, str]:
        """
        Render strategy guide for word problems
        Shows how to identify operations and solve
        """
        if operation == "multiplication":
            html = """
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Word Problem Strategy: Multiplication</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0;">
                <div style="padding: 10px; background: #c8e6c9; border-left: 4px solid #4CAF50;">
                    <strong>Key Words:</strong><br>
                    • "X groups of Y"<br>
                    • "X boxes with Y each"<br>
                    • "X sets of Y"<br>
                    • "X times as many"
                </div>
                
                <div style="padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                    <strong>How to Solve:</strong><br>
                    1. Identify groups (X) and items per group (Y)<br>
                    2. Multiply: X × Y<br>
                    3. State the answer with units
                </div>
            </div>
            
            <div style="padding: 10px; background: #fff9c4; border-left: 4px solid #fbc02d;">
                <strong>Remember:</strong> Multiplication finds the TOTAL when you have equal groups
            </div>
        </div>
        """
        elif operation == "division":
            html = """
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Word Problem Strategy: Division</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0;">
                <div style="padding: 10px; background: #c8e6c9; border-left: 4px solid #4CAF50;">
                    <strong>Key Words:</strong><br>
                    • "Share equally"<br>
                    • "Divide among"<br>
                    • "How many per..."<br>
                    • "Split into groups"
                </div>
                
                <div style="padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                    <strong>How to Solve:</strong><br>
                    1. Identify total and number of groups<br>
                    2. Divide: Total ÷ Groups<br>
                    3. Include remainder if present
                </div>
            </div>
            
            <div style="padding: 10px; background: #fff9c4; border-left: 4px solid #fbc02d;">
                <strong>Remember:</strong> Division shares items equally or makes equal groups
            </div>
        </div>
        """
        else:  # comparison
            html = """
        <div style="border: 2px solid #333; padding: 12px; margin: 10px 0; background: #f9f9f9;">
            <h4>Word Problem Strategy: Compare</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0;">
                <div style="padding: 10px; background: #c8e6c9; border-left: 4px solid #4CAF50;">
                    <strong>Key Words:</strong><br>
                    • "How many more..."<br>
                    • "How much more..."<br>
                    • "Compare..."<br>
                    • "Difference"
                </div>
                
                <div style="padding: 10px; background: #e3f2fd; border-left: 4px solid #2196F3;">
                    <strong>How to Solve:</strong><br>
                    1. Calculate each amount<br>
                    2. Find the difference<br>
                    3. Subtract: Larger - Smaller
                </div>
            </div>
            
            <div style="padding: 10px; background: #fff9c4; border-left: 4px solid #fbc02d;">
                <strong>Remember:</strong> Always answer what the question ASKS for (the difference)
            </div>
        </div>
        """
        
        return {"html": html}

    # ==================== IMPLEMENTATION GUIDE ====================
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

