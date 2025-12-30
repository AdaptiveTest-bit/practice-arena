"""
CLOCK ANGLES - INTEGRATED STRATEGY
==================================

Hybrid Neuro-Symbolic approach for Clock Angles

Integrates:
1. Pure Python angle calculations
2. K.C. Nag real-world scenarios
3. Misconception-based distractors (Angle direction confusion, Hand speed formula error)
4. Rich HTML rendering
5. Adaptive tracking (Bloom's progression, misconception detection)
"""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo, BLOOM_DEFINITIONS
from models.distractor import MisconceptionType, DistractorInfo, DistractorSet
import random
from typing import List, Tuple, Dict, Any


class ClockAnglesIntegrated(BaseChapterStrategy):
    """
    Seamlessly merges:
    1. Deterministic pure logic
    2. K.C. Nag real-world contexts
    3. Misconception-based distractors
    4. Rich visual rendering
    5. Adaptive tracking with Bloom's progression
    """
    
    chapter = ChapterEnum.CLOCK_ANGLES
    chapter_name = "Clock Angles"
    description = "Clock Angles with hybrid neuro-symbolic approach"
    
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
            "angle_between_hands",
            "time_to_angle",
            "angle_to_time",
        ])
        
        if problem_type == "angle_between_hands":
            return self._generate_angle_between_hands()
        elif problem_type == "time_to_angle":
            return self._generate_time_to_angle()
        else:  # angle_to_time
            return self._generate_angle_to_time()
    
    def _generate_angle_between_hands(self) -> Question:
        """
        Angle Between Hands
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters
        - Validate correctness
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        # Generate valid time (hour and minute)
        hour = random.randint(1, 12)
        minute = random.randint(0, 59)
        
        # Calculate angle of hour hand
        # Hour hand moves 30° per hour (360°/12)
        # Hour hand also moves 0.5° per minute (30°/60)
        hour_angle = (hour % 12) * 30 + minute * 0.5
        
        # Calculate angle of minute hand
        # Minute hand moves 6° per minute (360°/60)
        minute_angle = minute * 6
        
        # Calculate angle between hands (smaller angle)
        angle_diff = abs(hour_angle - minute_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        correct_answer = str(int(angle_diff))
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"Your classroom clock shows {hour}:{minute:02d}. What is the angle between the hour and minute hands?",
            f"At {hour}:{minute:02d}, a clock's hands form an angle. Can you calculate it?",
            f"During school assembly at {hour}:{minute:02d}, students notice the clock. What angle do the hands make?",
        ])
        
        # PHASE 3: Misconception-based distractors
        # Misconception 1: Using wrong formula for hour hand (just hour * 30, ignoring minutes)
        hour_only_angle = (hour % 12) * 30
        wrong_angle_1 = abs(hour_only_angle - minute_angle)
        if wrong_angle_1 > 180:
            wrong_angle_1 = 360 - wrong_angle_1
        
        # Misconception 2: Confusing minute calculation (using minute directly instead of minute * 6)
        wrong_angle_2 = abs(hour_angle - minute)
        if wrong_angle_2 > 180:
            wrong_angle_2 = 360 - wrong_angle_2
        
        # Misconception 3: Not taking the smaller angle (always greater than 180)
        larger_angle = abs(hour_angle - minute_angle)
        if larger_angle < 180:
            wrong_angle_3 = 360 - larger_angle
        else:
            wrong_angle_3 = larger_angle
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct angle",
                None,
                None
            ),
            1: (
                str(int(wrong_angle_1)),
                MisconceptionType.FORMULA_CONFUSION,
                "Ignored minute component of hour hand",
                "Student forgot that hour hand moves continuously, not in jumps",
                "Hour hand moves 30° per hour AND 0.5° per minute. Don't forget the minute component!"
            ),
            2: (
                str(int(wrong_angle_2)),
                MisconceptionType.ARITHMETIC_ERROR,
                "Used wrong multiplier for minute hand",
                "Student used minute value directly instead of multiplying by 6",
                "Minute hand moves 6° for every minute (360°/60 = 6°). Multiply minute by 6!"
            ),
            3: (
                str(int(wrong_angle_3)),
                MisconceptionType.INCOMPLETE_REASONING,
                "Used the larger angle instead of smaller",
                "Student calculated the reflex angle instead of the acute/obtuse angle",
                "There are always 2 angles between clock hands. Choose the smaller one (≤180°)"
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
            MisconceptionType.FORMULA_CONFUSION,
            difficulty=1,
            custom_description="Forgetting hour hand moves continuously",
            custom_why_effective="Students think hour hand jumps exactly at hour marks",
            custom_how_to_avoid="Remember: hour hand moves 30° per hour (360°/12) AND 0.5° per minute (30°/60)"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.UNDERSTAND, trap_difficulty=1)
        
        steps = [
            f"Time: {hour}:{minute:02d}",
            f"Hour hand angle: {hour}° × 30° + {minute} × 0.5° = {hour_angle}°",
            f"Minute hand angle: {minute} × 6° = {minute_angle}°",
            f"Difference: |{hour_angle}° - {minute_angle}°| = {abs(hour_angle - minute_angle)}°",
            f"Smaller angle: {int(angle_diff)}°"
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = self._render_clock_diagram(hour, minute, int(angle_diff))
        
        question = Question(
            chapter=self.chapter,
            topic="Clock Angles - Angle Between Hands",
            logical_trap="K.C. Nag Trap: Students often forget that the hour hand moves continuously throughout the hour, not just at hour marks. They calculate only the hour component and ignore the minute contribution.",
            data_representation=f"```\nTime: {hour}:{minute:02d}\nHour hand: {hour_angle}°\nMinute hand: {minute_angle}°\n```",
            question_text=f"What is the angle between the hour and minute hands at {hour}:{minute:02d}?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Understanding how clock hands move is key. The hour hand doesn't wait at the hour mark—it smoothly moves as minutes pass. This continuous motion is what makes clock angle problems interesting!",
            visual_hints=[
                f"Hour hand: moves 30° per hour (360°/12) plus extra from minutes",
                f"Minute hand: moves 6° per minute (360°/60)",
                f"At {hour}:{minute:02d}, hour hand is at {hour_angle}° and minute hand is at {minute_angle}°",
                f"Angle between them: {int(angle_diff)}° (take the smaller angle)"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _generate_time_to_angle(self) -> Question:
        """
        Time To Angle
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters
        - Validate correctness
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        # Given an angle, find the time (reverse problem)
        angle = random.randint(0, 180) * (1 if random.random() > 0.5 else 0.5)
        angle = int(angle) if angle == int(angle) else angle
        
        # For simplicity, we'll use times where we can calculate valid times
        # Standard times: 12:00, 3:00, 6:00, 9:00, etc
        base_times = [
            (3, 0),   # 90°
            (6, 0),   # 180°
            (9, 0),   # 90°
            (12, 0),  # 0°
            (1, 0),   # 30°
            (2, 0),   # 60°
            (4, 0),   # 120°
            (5, 0),   # 150°
        ]
        
        selected_time = random.choice(base_times)
        hour, minute = selected_time
        
        # Recalculate actual angle for this time
        hour_angle = (hour % 12) * 30 + minute * 0.5
        minute_angle = minute * 6
        angle_diff = abs(hour_angle - minute_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        correct_answer = f"{hour}:{minute:02d}"
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"A clock's hands form an angle of {int(angle_diff)}°. What time is it?",
            f"At what time do the clock hands make an angle of {int(angle_diff)}°?",
            f"If the angle between clock hands is {int(angle_diff)}°, what is the time?",
        ])
        
        # PHASE 3: Misconception-based distractors
        # Common wrong answers
        wrong_times = []
        for h in range(1, 13):
            if h != hour:
                wrong_times.append((h, 0))
        
        distractor_times = random.sample(wrong_times, min(3, len(wrong_times)))
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct time",
                None,
                None
            ),
            1: (
                f"{distractor_times[0][0]}:{distractor_times[0][1]:02d}",
                MisconceptionType.INCOMPLETE_REASONING,
                "Wrong hour calculation",
                "Student guessed without calculating hand positions",
                f"Hour {distractor_times[0][0]} would give a different angle. Check: (hour%12)*30 + minute*0.5 for hour hand"
            ),
            2: (
                f"{distractor_times[1][0]}:{distractor_times[1][1]:02d}",
                MisconceptionType.FORMULA_CONFUSION,
                "Confused hour-minute relationship",
                "Student used wrong formula to work backwards from angle",
                "To go from angle to time, use: angle = |hour_angle - minute_angle|, then solve"
            ),
            3: (
                f"{distractor_times[2][0]}:{distractor_times[2][1]:02d}",
                MisconceptionType.ARITHMETIC_ERROR,
                "Calculation error",
                "Student made an arithmetic mistake while reversing the formula",
                "Double-check your calculation: hour_angle = (hour%12)*30, minute_angle = minute*6"
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
            difficulty=2,
            custom_description="Working backwards from angle to time",
            custom_why_effective="Reversing the calculation is harder than forward calculation",
            custom_how_to_avoid="Know all standard angles: 3:00=90°, 6:00=180°, 9:00=90°, etc."
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        steps = [
            f"Angle between hands: {int(angle_diff)}°",
            f"Check each option by calculating its angle",
            f"Hour hand at {hour}:00 = ({hour}%12)*30 = {hour_angle}°",
            f"Minute hand at {minute} min = {minute}*6 = {minute_angle}°",
            f"Difference: {int(angle_diff)}° ✓ Matches!"
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = self._render_clock_diagram(hour, minute, int(angle_diff))
        
        question = Question(
            chapter=self.chapter,
            topic="Clock Angles - Given Angle Find Time",
            logical_trap="K.C. Nag Trap: Working backwards from angle to time requires understanding the relationship between hand positions and angles. Many students cannot reverse their thinking.",
            data_representation=f"```\nAngle: {int(angle_diff)}°\nFind the time\n```",
            question_text=f"At what time do the clock hands form an angle of {int(angle_diff)}°?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Reverse thinking is powerful! If we know how to calculate angles from time, we can also work backwards. This teaches flexibility in mathematical thinking.",
            visual_hints=[
                f"Given angle: {int(angle_diff)}°",
                f"Check each time option by calculating its hand positions",
                f"Hour hand at {hour} = 30° × {hour}",
                f"Minute hand at {minute} = 6° × {minute}, Angle = {int(angle_diff)}°"
            ]
        )
        
        self._validate_question(question)
        return question
    
    def _generate_angle_to_time(self) -> Question:
        """
        Angle To Time
        
        PHASE 1: Deterministic Skeleton
        - Generate valid problem parameters
        - Validate correctness
        
        PHASE 2: K.C. Nag Story
        - Create real-world context
        - Embed misconception hook
        
        PHASE 3: Misconception-Based Distractors
        - Generate 3 misconception-aligned options
        - Use 5-tuple DistractorInfo format
        
        PHASE 4: Rich Rendering
        - Create HTML/visual representation
        - Add 3-4 progressive hints
        
        PHASE 5: Question Object
        - Set logical_trap description
        - Configure Bloom's & misconception metadata
        - Return Question for database
        """
        # PHASE 1: Deterministic skeleton
        # Find what happens to angle as time passes
        start_hour = random.randint(1, 12)
        start_minute = random.choice([0, 15, 30, 45])
        
        # Calculate initial angle
        start_hour_angle = (start_hour % 12) * 30 + start_minute * 0.5
        start_minute_angle = start_minute * 6
        start_angle = abs(start_hour_angle - start_minute_angle)
        if start_angle > 180:
            start_angle = 360 - start_angle
        
        # Time progression (in minutes)
        time_passed = random.choice([5, 10, 15, 20, 30])
        
        # Calculate new time
        new_minute = (start_minute + time_passed) % 60
        new_hour = start_hour if (start_minute + time_passed) < 60 else (start_hour % 12) + 1
        
        # Calculate new angle
        new_hour_angle = (new_hour % 12) * 30 + new_minute * 0.5
        new_minute_angle = new_minute * 6
        new_angle = abs(new_hour_angle - new_minute_angle)
        if new_angle > 180:
            new_angle = 360 - new_angle
        
        angle_change = new_angle - start_angle
        correct_answer = str(int(abs(angle_change)))
        
        # PHASE 2: K.C. Nag story context
        story_scenario = random.choice([
            f"At {start_hour}:{start_minute:02d}, the clock hands form a {int(start_angle)}° angle. After {time_passed} minutes, how much does this angle change?",
            f"Between {start_hour}:{start_minute:02d} and {new_hour}:{new_minute:02d}, how much does the angle between clock hands change?",
            f"A clock's hand angle is {int(start_angle)}° at {start_hour}:{start_minute:02d}. What's the new angle after {time_passed} minutes pass?",
        ])
        
        # PHASE 3: Misconception-based distractors
        # Misconception 1: Only minute hand movement (6° per minute)
        minute_only_change = time_passed * 6
        
        # Misconception 2: Ignoring hour hand movement
        wrong_change_1 = abs(minute_only_change)
        
        # Misconception 3: Using absolute initial angle without direction
        wrong_change_2 = (time_passed * 6) - (time_passed * 0.5)
        wrong_change_2 = abs(wrong_change_2)
        
        option_distractors = {
            0: (
                correct_answer,
                None,
                "Correct change",
                None,
                None
            ),
            1: (
                str(int(minute_only_change)),
                MisconceptionType.FORMULA_CONFUSION,
                "Only counted minute hand movement",
                "Student forgot that hour hand also moves as time passes",
                "Both hands move! Minute hand moves 6°/min, hour hand moves 0.5°/min. Don't ignore the hour hand!"
            ),
            2: (
                str(int(wrong_change_1)),
                MisconceptionType.INCOMPLETE_REASONING,
                "Wrong rate calculation",
                "Student used wrong rate for angle change",
                "Rate of angle change = |minute_rate - hour_rate| = |6 - 0.5| = 5.5°/minute"
            ),
            3: (
                str(int(abs(wrong_change_2))),
                MisconceptionType.ARITHMETIC_ERROR,
                "Calculation error",
                "Student made an arithmetic mistake",
                "Double-check: (6 - 0.5) × minutes = 5.5 × {time_passed} = {int(5.5 * time_passed)}°"
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
            MisconceptionType.FORMULA_CONFUSION,
            difficulty=2,
            custom_description="Forgetting both hands move at different rates",
            custom_why_effective="Students focus only on minute hand (more visible) and forget hour hand also moves",
            custom_how_to_avoid="Always ask: 'What moves?' Answer: BOTH hands! Minute hand 6°/min, hour hand 0.5°/min"
        )
        
        bloom_info = self.create_bloom_info(BloomLevel.APPLY, trap_difficulty=2)
        
        steps = [
            f"Start time: {start_hour}:{start_minute:02d}",
            f"Initial angle: {int(start_angle)}°",
            f"Time passed: {time_passed} minutes",
            f"Minute hand moves: {time_passed} × 6° = {int(time_passed * 6)}°",
            f"Hour hand moves: {time_passed} × 0.5° = {int(time_passed * 0.5)}°",
            f"Net angle change: |{int(time_passed * 6)}° - {int(time_passed * 0.5)}°| = {int(abs(angle_change))}°"
        ]
        
        # PHASE 4: Rich rendering
        visual_diagram = f"""
<div style='border:2px solid #2196F3; border-radius:8px; padding:15px; background:#f0f7ff;'>
    <h4 style='color:#1976D2; margin-top:0;'>Clock Angle Change</h4>
    <p><strong>Start Time:</strong> {start_hour}:{start_minute:02d} → Angle: {int(start_angle)}°</p>
    <p><strong>After {time_passed} min:</strong> {new_hour}:{new_minute:02d} → Angle: {int(new_angle)}°</p>
    <p><strong>Change:</strong> {int(abs(angle_change))}°</p>
    <p style='background:white; padding:10px; border-left:4px solid #2196F3; color:#1565C0;'>
        Both hands move continuously!<br>
        Minute hand: 6°/minute<br>
        Hour hand: 0.5°/minute<br>
        Combined rate: 5.5°/minute
    </p>
</div>
"""
        
        question = Question(
            chapter=self.chapter,
            topic="Clock Angles - Rate of Change",
            logical_trap="K.C. Nag Trap: Students focus only on the obvious minute hand and forget that the hour hand also moves continuously. This leads to incomplete calculations.",
            data_representation=f"```\nStart: {start_hour}:{start_minute:02d} ({int(start_angle)}°)\nAfter {time_passed} min: {new_hour}:{new_minute:02d} ({int(new_angle)}°)\n```",
            question_text=f"At {start_hour}:{start_minute:02d}, the angle between clock hands is {int(start_angle)}°. After {time_passed} minutes, the angle is {int(new_angle)}°. By how many degrees did the angle change?",
            solution_steps=steps,
            answer=correct_answer,
            options=options,
            correct_option_index=correct_idx,
            distractor_info=distractor_info,
            trap_info=trap_info,
            bloom_info=bloom_info,
            rich_html_content=visual_diagram,
            rich_narrative="K.C. Nag approach: Understanding rate of change is powerful! When both hands move at different speeds, their relative separation changes predictably. Minute hand (fast) moves 6°/min, hour hand (slow) moves 0.5°/min, so the angle changes at 5.5°/min.",
            visual_hints=[
                f"Initial angle: {int(start_angle)}° at {start_hour}:{start_minute:02d}",
                f"Time passed: {time_passed} minutes",
                f"Minute hand moves: {time_passed} × 6° = {int(time_passed * 6)}°",
                f"Hour hand moves: {time_passed} × 0.5° = {int(time_passed * 0.5)}°, Angle change: {int(abs(angle_change))}°"
            ]
        )
        
        self._validate_question(question)
        return question


    # ==================== HELPER METHODS ====================
    
    def _render_clock_diagram(self, hour: int, minute: int, angle: int) -> str:
        """
        Render HTML visual representation of clock with hands and angle
        
        Args:
            hour: Hour on clock (1-12)
            minute: Minute on clock (0-59)
            angle: Angle between hands in degrees
            
        Returns:
            HTML string with clock visual
        """
        # Calculate hand angles
        hour_angle = (hour % 12) * 30 + minute * 0.5
        minute_angle = minute * 6
        
        # HTML with inline SVG
        html = f"""
<div style='border:2px solid #2196F3; border-radius:8px; padding:15px; background:#f0f7ff;'>
    <h4 style='color:#1976D2; margin-top:0;'>Clock at {hour}:{minute:02d}</h4>
    
    <svg width='200' height='200' viewBox='0 0 200 200' style='display:block; margin:10px auto;'>
        <!-- Clock face -->
        <circle cx='100' cy='100' r='90' fill='white' stroke='#2196F3' stroke-width='2'/>
        
        <!-- Hour markers -->
        <text x='100' y='20' text-anchor='middle' font-size='14' font-weight='bold'>12</text>
        <text x='180' y='105' text-anchor='middle' font-size='14' font-weight='bold'>3</text>
        <text x='100' y='190' text-anchor='middle' font-size='14' font-weight='bold'>6</text>
        <text x='20' y='105' text-anchor='middle' font-size='14' font-weight='bold'>9</text>
        
        <!-- Hour hand (shorter) -->
        <line x1='100' y1='100' 
              x2='{100 + 50 * __import__("math").sin(__import__("math").radians(hour_angle))}'
              y2='{100 - 50 * __import__("math").cos(__import__("math").radians(hour_angle))}'
              stroke='#1976D2' stroke-width='6' stroke-linecap='round'/>
        
        <!-- Minute hand (longer) -->
        <line x1='100' y1='100' 
              x2='{100 + 70 * __import__("math").sin(__import__("math").radians(minute_angle))}'
              y2='{100 - 70 * __import__("math").cos(__import__("math").radians(minute_angle))}'
              stroke='#D32F2F' stroke-width='4' stroke-linecap='round'/>
        
        <!-- Center dot -->
        <circle cx='100' cy='100' r='6' fill='#424242'/>
    </svg>
    
    <div style='background:white; padding:10px; border-left:4px solid #2196F3; color:#1565C0;'>
        <p><strong>Time:</strong> {hour}:{minute:02d}</p>
        <p><strong>Angle between hands:</strong> {angle}°</p>
    </div>
</div>
"""
        return html
    
    def _render_angle_calc(self, hour: int, minute: int, hour_angle: float, minute_angle: float, final_angle: float) -> str:
        """Create angle calculation visualization"""
        html = f"""
<div style='border:2px solid #FF9800; border-radius:8px; padding:15px; background:#fff3e0;'>
    <h4 style='color:#E65100; margin-top:0;'>Angle Calculation</h4>
    
    <svg width='500' height='200' viewBox='0 0 500 200' style='display:block; margin:10px auto;'>
        <!-- Title -->
        <text x='250' y='25' text-anchor='middle' font-size='16' font-weight='bold' fill='#E65100'>
            Time: {hour}:{minute:02d}
        </text>
        
        <!-- Hour hand calculation -->
        <text x='20' y='65' font-size='12' font-weight='bold' fill='#1976D2'>Hour Hand:</text>
        <text x='20' y='85' font-size='11' fill='#1976D2'>
            Position = ({hour} × 30°) + ({minute} × 0.5°) = {hour_angle:.1f}°
        </text>
        
        <!-- Minute hand calculation -->
        <text x='20' y='120' font-size='12' font-weight='bold' fill='#D32F2F'>Minute Hand:</text>
        <text x='20' y='140' font-size='11' fill='#D32F2F'>
            Position = {minute} × 6° = {minute_angle:.1f}°
        </text>
        
        <!-- Final calculation -->
        <line x1='10' y1='155' x2='490' y2='155' stroke='#ccc' stroke-width='1'/>
        <text x='20' y='185' font-size='13' font-weight='bold' fill='#4CAF50'>
            Angle = |{minute_angle:.1f}° - {hour_angle:.1f}°| = {final_angle:.1f}°
        </text>
    </svg>
</div>
"""
        return html
    
    def _render_time_relationship(self, hours_elapsed: int, minutes_elapsed: int, angle_change: float) -> str:
        """Create time to angle relationship visualization"""
        html = f"""
<div style='border:2px solid #9C27B0; border-radius:8px; padding:15px; background:#f3e5f5;'>
    <h4 style='color:#6A1B9A; margin-top:0;'>Time and Angle Relationship</h4>
    
    <svg width='500' height='220' viewBox='0 0 500 220' style='display:block; margin:10px auto;'>
        <!-- Title -->
        <text x='250' y='25' text-anchor='middle' font-size='15' font-weight='bold' fill='#6A1B9A'>
            How Angle Changes with Time
        </text>
        
        <!-- Key facts -->
        <text x='20' y='65' font-size='12' font-weight='bold' fill='#424242'>Key Facts:</text>
        <text x='20' y='85' font-size='11' fill='#424242'>• Minute hand: 6° per minute</text>
        <text x='20' y='105' font-size='11' fill='#424242'>• Hour hand: 0.5° per minute</text>
        <text x='20' y='125' font-size='11' fill='#424242'>• Relative speed: 5.5° per minute</text>
        
        <!-- Calculation -->
        <line x1='10' y1='140' x2='490' y2='140' stroke='#ccc' stroke-width='1'/>
        <text x='20' y='165' font-size='12' font-weight='bold' fill='#6A1B9A'>Change in angle:</text>
        <text x='20' y='185' font-size='11' fill='#6A1B9A'>
            {hours_elapsed}h {minutes_elapsed}m = {hours_elapsed * 60 + minutes_elapsed} minutes
        </text>
        <text x='20' y='205' font-size='12' font-weight='bold' fill='#C2185B'>
            Angle change = {hours_elapsed * 60 + minutes_elapsed} × 5.5° = {angle_change:.1f}°
        </text>
    </svg>
</div>
"""
        return html
    
    # ==================== UTILITY METHODS ====================
    
    def _difficulty_level_to_int(self, difficulty: str) -> int:
        """Convert difficulty string to 1-5 scale"""
        mapping = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
            "expert": 4,
        }
        return mapping.get(difficulty.lower(), 2) if difficulty else 2
