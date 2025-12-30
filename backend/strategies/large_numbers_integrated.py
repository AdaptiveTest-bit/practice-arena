"""
LARGE NUMBERS & PLACE VALUE - INTEGRATED STRATEGY
=================================================

Hybrid Neuro-Symbolic approach for Chapter 1: The Fish Tale

Integrates:
1. Deterministic number logic (Python)
2. K.C. Nag real-world scenarios (place value in daily life)
3. Misconception-based distractors (lakh/crore confusion, reversal errors)
4. Rich HTML rendering with visual place value diagrams
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorSet, DistractorInfo
import random
from typing import List, Tuple, Dict, Any


class LargeNumbersIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic place value logic
    2. K.C. Nag real-world contexts (shopping, population, distances)
    3. Misconception-based distractors (lakh/crore reversal, place confusion)
    4. Rich visual rendering with place value diagrams
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.LARGE_NUMBERS
    chapter_name = "Large Numbers & Place Value"
    description = "Place value (Lakh/Crore), profit-loss, comparisons"
    
    def __init__(self):
        super().__init__()
        # Note: For chapters without SymPy generators, use pure Python logic
        # K.C. Nag story generation and rendering will be integrated similarly
    
    def generate(self) -> Question:
        """Main generation pipeline: skeleton -> story -> misconceptions -> rendering -> question"""
        problem_type = random.choice([
            "place_value_identification",
            "lakh_crore_conversion",
            "profit_loss_calculation",
            "comparison_large_numbers",
            "rounding_nearest_thousand"
        ])
        
        if problem_type == "place_value_identification":
            return self._generate_place_value_identification()
        elif problem_type == "lakh_crore_conversion":
            return self._generate_lakh_crore_conversion()
        elif problem_type == "profit_loss_calculation":
            return self._generate_profit_loss_calculation()
        elif problem_type == "comparison_large_numbers":
            return self._generate_comparison_large_numbers()
        else:
            return self._generate_rounding_nearest_thousand()
    
    # ==================== PLACE VALUE IDENTIFICATION ====================
    
    def _generate_place_value_identification(self) -> Question:
        """Identify place value of a digit in large number (UNDERSTAND level)"""
        
        # PHASE 1: Deterministic skeleton
        # Generate number with specific digit placement
        place_values = {
            "ones": (1, "ones"),
            "tens": (10, "tens"),
            "hundreds": (100, "hundreds"),
            "thousands": (1000, "thousands"),
            "ten_thousands": (10000, "ten thousands"),
            "lakhs": (100000, "lakhs"),
            "ten_lakhs": (1000000, "ten lakhs"),
        }
        
        selected_place, (multiplier, place_name) = random.choice(list(place_values.items()))
        digit = random.randint(1, 9)
        position_value = digit * multiplier
        
        # Build number around this digit
        remaining_digits = []
        for _ in range(7):
            remaining_digits.append(random.randint(0, 9))
        
        number_list = remaining_digits.copy()
        insert_position = {
            "ones": 0,
            "tens": 1,
            "hundreds": 2,
            "thousands": 3,
            "ten_thousands": 4,
            "lakhs": 5,
            "ten_lakhs": 6,
        }[selected_place]
        
        while len(number_list) <= insert_position:
            number_list.append(random.randint(0, 9))
        
        number_list[insert_position] = digit
        number = int("".join(map(str, reversed(number_list[:7]))))
        
        correct_answer = str(position_value)
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"In a village, there are {number} people. A relief program will target every {{digit}} people.",
            f"A school library has {number} books. Students are organized in groups of {{digit}} for inventory.",
            f"A factory produces {number} toys per month. Shipping containers hold {{digit}} units each.",
        ])
        
        # PHASE 3: Misconception-based distractors
        distractor1_val = str(digit)  # Just the digit, not place value
        distractor2_val = str(position_value // 10) if position_value >= 10 else str(position_value)  # Wrong power of 10
        distractor3_val = str(position_value * 10) if position_value < 1000000 else str(1000000)  # One order higher
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct place value",
                None,
                None
            ),
            1: (
                distractor1_val,
                MisconceptionType.INCOMPLETE_REASONING,
                "Just the digit, not its place value",
                "Student forgot to multiply digit by place value",
                "Place value = digit × power of 10. The digit 7 in position 100 has place value 700, not 7"
            ),
            2: (
                distractor2_val,
                MisconceptionType.CONSTRAINT_VIOLATION,
                "Using wrong power of 10",
                "Student got the place wrong",
                "Count positions carefully: ones, tens, hundreds, thousands..."
            ),
            3: (
                distractor3_val,
                MisconceptionType.ARITHMETIC_ERROR,
                "Off by one magnitude",
                "Student used wrong exponent",
                "Each position is 10 times the previous; multiply by correct power"
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = opt_val
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=opt_val,
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description=desc,
                    why_wrong=why_wrong or "Correct",
                    teaching_point=teaching or "Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=opt_val,
                    misconception_type=misconception,
                    description=desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Confusing digit with place value",
            custom_why_effective="Students see the digit and forget to multiply by position",
            custom_how_to_avoid="Always ask: 'What is the power of 10 for this position?' Then multiply digit × power"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        steps = [
            f"Number: {number:,}",
            f"Digit in focus: {digit}",
            f"Position: {place_name}",
            f"Power of 10: {multiplier}",
            f"Place value = {digit} × {multiplier} = {position_value}"
        ]
        
        # PHASE 4: Rich rendering (simplified for template)
        visual_diagram = self._render_place_value_diagram(number, insert_position)
        
        question = Question(
            chapter=self.chapter,
            topic="Place Value - Large Numbers",
            logical_trap="K.C. Nag Trap: Students often confuse the digit itself with its place value. They see the digit 7 and answer 7, forgetting to multiply by the position (tens, hundreds, thousands, etc.)",
            data_representation=f"```\nNumber: {number:,}\nPlace values: Ones | Tens | Hundreds | ...\n```",
            question_text=f"In the number {number:,}, what is the place value of the digit {digit}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Understanding that each position represents a different power of 10 is crucial. Not just 'what digit is here?' but 'how much is that digit worth in this position?'",
            visual_hints=[
                f"The digit {digit} appears in the {place_name} position",
                f"The {place_name} place represents {multiplier}",
                f"Place value = digit × position value = {digit} × {multiplier}",
                f"Answer: {position_value}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    # ==================== LAKH/CRORE CONVERSION ====================
    
    def _generate_lakh_crore_conversion(self) -> Question:
        """Convert between lakh, crore, and standard notation (UNDERSTAND level)"""
        
        # Deterministic generation
        crores = random.randint(1, 9)
        lakhs = random.randint(0, 99)
        total_value = crores * 10000000 + lakhs * 100000
        
        conversion_type = random.choice([
            "crore_to_standard",
            "lakh_to_standard",
            "standard_to_crore"
        ])
        
        if conversion_type == "crore_to_standard":
            question_text = f"Express {crores} crore and {lakhs} lakh in standard form"
            correct_answer = str(total_value)
            misconception_base = crores * 10 + lakhs
        elif conversion_type == "lakh_to_standard":
            question_text = f"What is {lakhs} lakh in standard notation?"
            correct_answer = str(lakhs * 100000)
            misconception_base = lakhs * 1000  # Common 10x error
        else:  # standard_to_crore
            question_text = f"Express {total_value:,} as crore and lakh"
            correct_answer = f"{crores} crore {lakhs} lakh"
            misconception_base = f"{crores} lakh {lakhs} crore"  # Reversed
        
        # Misconceptions
        option_distractors = {
            0: (correct_answer, None, "Correct conversion", None, None),
            1: (
                str(misconception_base) if isinstance(misconception_base, int) else misconception_base,
                MisconceptionType.FORMULA_CONFUSION,
                "Reversed crore and lakh or wrong multiplication",
                "Student confused Indian and Western numbering",
                "Indian: 1 lakh = 1,00,000 | 1 crore = 1,00,00,000 (10 lakhs)"
            ),
            2: (
                str(total_value // 100),
                MisconceptionType.ARITHMETIC_ERROR,
                "Off by magnitude",
                "Student used wrong multiplier",
                "Double-check: 1 lakh = 100,000; 1 crore = 10,000,000"
            ),
            3: (
                str(total_value + random.randint(100000, 1000000)),
                MisconceptionType.INCOMPLETE_REASONING,
                "Added extra zeroes",
                "Student added instead of multiplied",
                "Conversion uses multiplication, not addition"
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = str(opt_val)
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=str(opt_val),
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description=desc,
                    why_wrong="Correct",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=str(opt_val),
                    misconception_type=misconception,
                    description=desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.FORMULA_CONFUSION,
            difficulty=2,
            custom_description="Confusing lakh and crore place values",
            custom_why_effective="Both are Indian numbering; easy to reverse",
            custom_how_to_avoid="Remember: 1 lakh = 100,000 (5 zeros); 1 crore = 10,000,000 (7 zeros)"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=2)
        
        steps = [
            f"Conversion type: {conversion_type}",
            f"Key facts: 1 lakh = 100,000 | 1 crore = 10 lakhs = 10,000,000",
            f"Calculation: {crores} crore = {crores} × 10,000,000 = {crores * 10000000:,}",
            f"Adding: {lakhs} lakh = {lakhs} × 100,000 = {lakhs * 100000:,}",
            f"Total: {total_value:,}"
        ]
        
        question = Question(
            chapter=self.chapter,
            topic="Indian Numbering - Lakh & Crore",
            logical_trap="K.C. Nag Trap: Students reverse crore and lakh, or use wrong multipliers. The Indian system (lakh/crore) is different from Western (thousands/millions).",
            data_representation="```\nIndian Numbering:\n1 Lakh = 100,000 (5 zeros)\n1 Crore = 10,000,000 (7 zeros) = 10 Lakhs\n```",
            question_text=question_text,
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=f"<div style='border:1px solid blue; padding:10px'><h4>Place Value Chart</h4><p>Crore: {crores} | Lakh: {lakhs}</p><p>Standard: {total_value:,}</p></div>",
            rich_narrative="Understanding Indian numbering (lakh, crore) is essential for students in India. These are cultural mathematics - numbers that matter in our daily lives (population, money, distances).",
            visual_hints=[
                "1 lakh = 100,000 (5 zeros after 1)",
                "1 crore = 10,000,000 (7 zeros after 1)",
                "Crore is 100 times bigger than lakh",
                f"Answer: {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    # ==================== PROFIT/LOSS CALCULATION ====================
    
    def _generate_profit_loss_calculation(self) -> Question:
        """Calculate profit or loss (APPLY level)"""
        
        cost_price = random.randint(100, 5000)
        
        # Ensure we actually get profit or loss (not break-even)
        profit_or_loss = random.choice(["profit", "loss"])
        if profit_or_loss == "profit":
            percent = random.randint(10, 50)
            profit = (cost_price * percent) // 100
            selling_price = cost_price + profit
            correct_answer = str(profit)
            question_text = f"Cost price: Rs. {cost_price}, Selling price: Rs. {selling_price}. What is the profit?"
        else:
            percent = random.randint(10, 50)
            loss = (cost_price * percent) // 100
            selling_price = cost_price - loss
            correct_answer = str(loss)
            question_text = f"Cost price: Rs. {cost_price}, Selling price: Rs. {selling_price}. What is the loss?"
        
        # Misconceptions
        option_distractors = {
            0: (correct_answer, None, "Correct profit/loss", None, None),
            1: (
                str(selling_price),
                MisconceptionType.INCOMPLETE_REASONING,
                "Just the selling price, not profit/loss",
                "Student returned SP instead of difference",
                "Profit = SP - CP, not just SP"
            ),
            2: (
                str(abs(cost_price - selling_price) * 2),
                MisconceptionType.ARITHMETIC_ERROR,
                "Doubled the difference",
                "Student miscalculated",
                "Profit/Loss = Selling Price - Cost Price (single difference)"
            ),
            3: (
                str(abs(cost_price - selling_price)) if profit_or_loss == "profit" else str(cost_price),
                MisconceptionType.OPPOSITE_CONFUSION,
                "Reversed profit and loss",
                "Student mixed up direction",
                "Profit: SP > CP (SP - CP = +). Loss: SP < CP (CP - SP = +)"
            ),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = str(opt_val)
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=str(opt_val),
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description=desc,
                    why_wrong="Correct",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=str(opt_val),
                    misconception_type=misconception,
                    description=desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=2,
            custom_description="Confusing profit direction or using wrong formula",
            custom_why_effective="Formula seems arbitrary without understanding purpose",
            custom_how_to_avoid="Profit = SP - CP; Loss = CP - SP; Always check: is SP bigger or smaller?"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        steps = [
            f"Cost Price (CP): Rs. {cost_price}",
            f"Selling Price (SP): Rs. {selling_price}",
            f"Difference: {abs(selling_price - cost_price)}",
            f"Since SP {'>' if profit_or_loss == 'profit' else '<'} CP, this is a {'profit' if profit_or_loss == 'profit' else 'loss'}",
            f"Answer: Rs. {correct_answer}"
        ]
        
        question = Question(
            chapter=self.chapter,
            topic="Profit & Loss Calculation",
            logical_trap="K.C. Nag Trap: Students often reverse profit and loss logic, or simply report the selling price instead of the difference. They forget to check whether selling price is more (profit) or less (loss) than cost price.",
            data_representation=f"```\nCost Price: Rs. {cost_price}\nSelling Price: Rs. {selling_price}\nProfit/Loss: Rs. {abs(cost_price - selling_price)}\n```",
            question_text=question_text,
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=f"<div style='border:1px solid green; padding:10px'><h4>Profit/Loss Formula</h4><p>Profit = SP - CP</p><p>Loss = CP - SP</p><p>Your calculation: {correct_answer}</p></div>",
            rich_narrative="K.C. Nag principle: Make profit/loss real. A shopkeeper buys goods at CP and sells at SP. If SP is higher, it's profit (money gained). If CP is higher, it's loss (money lost).",
            visual_hints=[
                f"Compare: CP = {cost_price}, SP = {selling_price}",
                f"Which is bigger? {max(cost_price, selling_price)}",
                f"Difference: {abs(cost_price - selling_price)}",
                f"This is a {'PROFIT' if profit_or_loss == 'profit' else 'LOSS'}: Rs. {correct_answer}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    # ==================== COMPARISON ====================
    
    def _generate_comparison_large_numbers(self) -> Question:
        """Compare two large numbers (UNDERSTAND level)"""
        
        num1 = random.randint(100000, 10000000)
        num2 = random.randint(100000, 10000000)
        
        # Ensure they're different
        while num1 == num2:
            num2 = random.randint(100000, 10000000)
        
        # Correct answer as actual option text (not symbolic)
        correct_answer = "num1 > num2" if num1 > num2 else "num2 > num1"
        
        question_text = f"Compare: {num1:,} and {num2:,}. Which is greater?"
        
        option_distractors = {
            0: (correct_answer, None, "Correct comparison", None, None),
            1: ("num2 > num1" if num1 > num2 else "num1 > num2", MisconceptionType.OPPOSITE_CONFUSION, "Reversed comparison", "Student flipped the comparison", "Compare digit by digit from left to right"),
            2: ("Equal", MisconceptionType.INCOMPLETE_REASONING, "Claiming they're equal when they're not", "Student didn't check all digits", "Even if first digits match, check remaining digits"),
            3: ("Cannot determine", MisconceptionType.CONSTRAINT_VIOLATION, "Claiming insufficient info", "Student doubts comparison rules", "We can always compare numbers exactly"),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = str(opt_val)
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=str(opt_val),
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description=desc,
                    why_wrong="Correct",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=str(opt_val),
                    misconception_type=misconception,
                    description=desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.OPPOSITE_CONFUSION,
            difficulty=1,
            custom_description="Reversing comparison symbols or not checking all digits",
            custom_why_effective="Large numbers have many digits; students miss details",
            custom_how_to_avoid="Align numbers vertically and compare digit by digit from left to right"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        steps = [
            f"Number 1: {num1:,}",
            f"Number 2: {num2:,}",
            f"Compare place by place (crore, lakh, thousand, ...)",
            f"Result: {num1:,} {'>' if num1 > num2 else '<'} {num2:,}"
        ]
        
        question = Question(
            chapter=self.chapter,
            topic="Comparing Large Numbers",
            logical_trap="K.C. Nag Trap: Students may reverse the comparison symbol or only look at the first digit, missing that subsequent digits matter.",
            data_representation=f"```\nNum1: {num1:,}\nNum2: {num2:,}\nSymbol: {'>' if num1 > num2 else '<'}\n```",
            question_text=question_text,
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=f"<div style='border:1px solid purple; padding:10px'><h4>Number Comparison</h4><p>{num1:,} {'>' if num1 > num2 else '<'} {num2:,}</p></div>",
            rich_narrative="K.C. Nag: Compare numbers like comparing heights. Taller person > shorter person. Bigger number > smaller number.",
            visual_hints=[
                f"Write both numbers aligned",
                f"Compare leftmost digits first",
                f"Result: {num1:,} is {'GREATER' if num1 > num2 else 'SMALLER'}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    # ==================== ROUNDING ====================
    
    def _generate_rounding_nearest_thousand(self) -> Question:
        """Round to nearest thousand (UNDERSTAND level)"""
        
        number = random.randint(1000, 999999)
        nearest_thousand = (number // 1000) * 1000
        if number % 1000 >= 500:
            nearest_thousand += 1000
        
        correct_answer = str(nearest_thousand)
        
        question_text = f"Round {number:,} to the nearest thousand"
        
        option_distractors = {
            0: (correct_answer, None, "Correct rounding", None, None),
            1: (str((number // 1000) * 1000), MisconceptionType.INCOMPLETE_REASONING, "Rounded down without checking", "Student just dropped last 3 digits", "Check if digit in hundreds place is ≥5"),
            2: (str(number // 100 * 100), MisconceptionType.CONSTRAINT_VIOLATION, "Rounded to nearest hundred instead", "Student used wrong place", "Round to NEAREST THOUSAND (1000)"),
            3: (str(nearest_thousand + 1000), MisconceptionType.ARITHMETIC_ERROR, "Rounded up too much", "Student over-rounded", "Only round up if hundreds digit is ≥5"),
        }
        
        shuffled = list(range(4))
        random.shuffle(shuffled)
        options = [""] * 4
        correct_idx = -1
        distractor_info_list = []
        
        for display_idx, source_idx in enumerate(shuffled):
            opt_val, misconception, desc, why_wrong, teaching = option_distractors[source_idx]
            options[display_idx] = str(opt_val)
            
            if misconception is None:
                correct_idx = display_idx
                distractor_info_list.append(DistractorInfo(
                    value=str(opt_val),
                    misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                    description=desc,
                    why_wrong="Correct",
                    teaching_point="Well done!"
                ))
            else:
                distractor_info_list.append(DistractorInfo(
                    value=str(opt_val),
                    misconception_type=misconception,
                    description=desc,
                    why_wrong=why_wrong,
                    teaching_point=teaching
                ))
        
        # Wrap in DistractorSet

        
        distractor_info = DistractorSet(

        
            correct_answer=correct_answer,

        
            distractors=[d for d in distractor_info_list if d.value != correct_answer]

        
        )

        
        

        
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=1,
            custom_description="Not checking the rounding digit (hundreds place)",
            custom_why_effective="Students want to round down by default",
            custom_how_to_avoid="Always check digit to right: ≥5 rounds up, <5 rounds down"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        hundreds_digit = (number % 1000) // 100
        
        steps = [
            f"Number: {number:,}",
            f"Nearest thousands: {(number // 1000) * 1000:,} and {((number // 1000) + 1) * 1000:,}",
            f"Check hundreds digit: {hundreds_digit}",
            f"Since {hundreds_digit} {'≥ 5' if hundreds_digit >= 5 else '< 5'}, round {'UP' if hundreds_digit >= 5 else 'DOWN'}",
            f"Answer: {nearest_thousand:,}"
        ]
        
        question = Question(
            chapter=self.chapter,
            topic="Rounding to Nearest Thousand",
            logical_trap="K.C. Nag Trap: Students often just drop the last three digits without checking the hundreds place. Or they round to the wrong place value (hundred instead of thousand).",
            data_representation=f"```\nNumber: {number:,}\nRound to: Nearest 1,000\nHundreds digit: {hundreds_digit}\n```",
            question_text=question_text,
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=f"<div style='border:1px solid orange; padding:10px'><h4>Rounding Rule</h4><p>Hundreds digit {hundreds_digit}: {'≥5 round up' if hundreds_digit >= 5 else '<5 round down'}</p><p>Answer: {nearest_thousand:,}</p></div>",
            rich_narrative="K.C. Nag: Rounding is about approximation for practical use. When shopping, we often think in round numbers. Learn the rule: look at the digit to the right of the place you're rounding to.",
            visual_hints=[
                f"Find the thousands place",
                f"Look at the digit to the right (hundreds): {hundreds_digit}",
                f"If ≥5, round up; if <5, round down",
                f"Answer: {nearest_thousand:,}"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _render_place_value_diagram(self, number: int, digit_position: int) -> str:
        """Create HTML diagram showing place values"""
        places = ["Ones", "Tens", "Hundreds", "Thousands", "Ten Thousands", "Lakhs", "Ten Lakhs"]
        digits = str(number).zfill(7)[::-1]  # Reverse for display
        
        html = "<table style='border-collapse: collapse; width:100%;'>"
        for i, (place, digit) in enumerate(zip(places, digits)):
            highlight = "background-color: yellow;" if i == digit_position else ""
            html += f"<tr><td style='{highlight} border: 1px solid black; padding: 5px;'>{place}</td><td style='{highlight} border: 1px solid black; padding: 5px;'>{digit}</td></tr>"
        html += "</table>"
        return html
