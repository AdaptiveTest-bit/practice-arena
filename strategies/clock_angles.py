"""Clock Angles question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
from models.cognitive_levels import BloomLevel, BloomInfo
import random
from models.distractor import MisconceptionType


class ClockAnglesStrategy(BaseChapterStrategy):
    """Generates clock angle and time-based problems."""
    
    chapter = ChapterEnum.CLOCK_ANGLES
    chapter_name = "Clock Angles"
    description = "Angles & fractions of rotation"
    
    def generate(self) -> Question:
        """Generate a clock angles question."""
        problem_type = random.choice([
            "hour_angle",
            "minute_angle",
            "angle_between_hands",
            "time_from_angle",
            "fraction_rotation",
            "clock_arithmetic"
        ])
        
        if problem_type == "hour_angle":
            return self._generate_hour_angle()
        elif problem_type == "minute_angle":
            return self._generate_minute_angle()
        elif problem_type == "angle_between_hands":
            return self._generate_angle_between_hands()
        elif problem_type == "time_from_angle":
            return self._generate_time_from_angle()
        elif problem_type == "fraction_rotation":
            return self._generate_fraction_rotation()
        else:
            return self._generate_clock_arithmetic()
    
    def _generate_hour_angle(self) -> Question:
        """Calculate angle of hour hand."""
        hour = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        angle = hour * 30  # 360/12 = 30 degrees per hour
        
        correct_answer = f"{angle}°"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{hour * 6}°",  # Confuses with minute calculation
            MisconceptionType.OPERATION_DIRECTION: 
                f"{hour * 60}°",  # Uses 60 instead of 30
            MisconceptionType.OPPOSITE_CONFUSION: 
                f"{360 - angle}°"  # Computes complement angle
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.ARITHMETIC_ERROR,
            difficulty=1,
            custom_description="Student uses 60 degrees per hour instead of 30; confuses minute/hour division",
            custom_why_effective="Simple arithmetic error; students often multiply by wrong constant without verification",
            custom_how_to_avoid="Remember: 360° ÷ 12 hours = 30° per hour; verify by checking that 12 hours = 360°"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.REMEMBER,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Clock Angles",
            logical_trap="K.C. Nag trap: Students confuse 60 minutes with 60 degrees. "
                        "Clock has 12 hours = 360°, so each hour = 30°.",
            data_representation="```\nClock circle: 360°\nHour divisions: 12\nDegrees per hour: 360÷12 = 30°\n"
                               f"At {hour} o'clock: Hour hand angle = {hour}×30° = {angle}°\n```",
            question_text=f"At {hour} o'clock, what angle does the hour hand make with 12?",
            solution_steps=[
                "Clock is a full circle: 360°",
                "12 hours on a clock",
                "Each hour = 360° ÷ 12 = 30°",
                f"At {hour} o'clock: {hour} × 30° = {angle}°"
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
    
    def _generate_minute_angle(self) -> Question:
        """Calculate angle of minute hand."""
        minutes = random.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        angle = (minutes // 5) * 30  # 60 minutes = 360°, so 5 min = 30°
        
        correct_answer = f"{angle}°"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{minutes}°",  # Confuses minute markers with degrees
            MisconceptionType.OPERATION_DIRECTION: 
                f"{minutes * 6}°",  # Uses wrong multiplier (6 instead of recognizing 30° pattern)
            MisconceptionType.OPPOSITE_CONFUSION: 
                f"{360 - angle}°"  # Computes complement angle
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.ARITHMETIC_ERROR,
            difficulty=1,
            custom_description="Student confuses minute count with degree measure; reports minutes instead of multiplying by 6",
            custom_why_effective="Direct confusion between two different units; surface similarity causes errors",
            custom_how_to_avoid="Remember: 60 minutes = 360°, so 1 minute = 6°; multiply minute count by 6 for degrees"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.REMEMBER,
            trap_difficulty=1
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Minute Hand Angles",
            logical_trap="Students confuse minute markers with degrees. 60 minutes = 360°, not 60°.",
            data_representation=f"```\nMinute hand at: {minutes} minutes\n"
                               "Full rotation (60 min): 360°\nEach minute: 6°\n"
                               f"{minutes} minutes = {minutes}×6° = {angle}°\n```",
            question_text=f"At {minutes} minutes past the hour, what angle is the minute hand at?",
            solution_steps=[
                "60 minutes = 360° (full circle)",
                "Each minute = 360° ÷ 60 = 6°",
                f"At {minutes} minutes: {minutes} × 6° = {angle}°"
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
    
    def _generate_angle_between_hands(self) -> Question:
        """Calculate angle between hour and minute hands."""
        hour = random.choice([1, 2, 3, 4])
        hour_angle = hour * 30
        minute_angle = 0
        angle_diff = abs(hour_angle - minute_angle)
        
        correct_answer = f"{hour_angle}°"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{360 - hour_angle}°",  # Confuses with complement angle
            MisconceptionType.OPERATION_DIRECTION: 
                f"{hour * 60}°",  # Wrong multiplier
            MisconceptionType.OPPOSITE_CONFUSION: 
                "180°"  # Assumes it's always opposite
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.ARITHMETIC_ERROR,
            difficulty=2,
            custom_description="Student computes complement angle instead of the actual angle between hands",
            custom_why_effective="Requires careful attention to what's being asked; students often compute related but wrong value",
            custom_how_to_avoid="Find both hand positions; subtract to get angle between them; verify answer makes sense"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Angle Between Hands",
            logical_trap="Students add angles instead of finding the difference.",
            data_representation=f"```\nAt {hour}:00\nHour hand: {hour_angle}°\n"
                               f"Minute hand: 0°\nAngle between: |{hour_angle} - 0°| = {hour_angle}°\n```",
            question_text=f"At {hour}:00, what is the angle between hour and minute hands?",
            solution_steps=[
                f"Hour hand at {hour}:00 = {hour} × 30° = {hour_angle}°",
                "Minute hand at :00 = 0°",
                f"Angle between = |{hour_angle}° - 0°| = {hour_angle}°"
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
    
    def _generate_time_from_angle(self) -> Question:
        """Find time from given hour hand angle."""
        angle = random.choice([30, 60, 90, 120, 150, 180])
        hour = angle // 30
        
        correct_answer = f"{hour}:00"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.ARITHMETIC_ERROR: 
                f"{hour-1}:00",  # Off-by-one error
            MisconceptionType.OPERATION_DIRECTION: 
                f"{angle // 6}:00",  # Uses wrong divisor
            MisconceptionType.OPPOSITE_CONFUSION: 
                f"{hour+1}:00"  # Off by one in other direction
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.OPERATION_DIRECTION,
            difficulty=2,
            custom_description="Student divides by wrong number (6 instead of 30) when converting angle to time",
            custom_why_effective="Requires correct operation; students confuse minute/hour division rules",
            custom_how_to_avoid="Remember: Each hour = 30°; to find time, divide angle by 30 (not by 6 which is for minutes)"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Time From Angle",
            logical_trap="Students divide by wrong number or confuse with minutes.",
            data_representation=f"```\nHour hand angle: {angle}°\nDegrees per hour: 30°\n"
                               f"Time: {angle}° ÷ 30° = {hour}:00\n```",
            question_text=f"If the hour hand is at {angle}° from 12, what time is it?",
            solution_steps=[
                f"Hour hand angle: {angle}°",
                "Each hour = 30°",
                f"Time = {angle}° ÷ 30° = {hour}:00"
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
    
    def _generate_fraction_rotation(self) -> Question:
        """Express clock movement as fraction of rotation."""
        hours = random.choice([3, 6, 9, 12])
        fraction = hours / 12
        percent = int(fraction * 100)
        
        correct_answer = f"{hours}/12 of rotation ({percent}%)"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{hours}/24 of rotation",  # Uses 24 instead of 12 (confuses with 24-hour clock)
            MisconceptionType.OPERATION_DIRECTION: 
                f"{12-hours}/12 of rotation",  # Inverts the fraction
            MisconceptionType.CONSTRAINT_VIOLATION: 
                "1 full rotation"  # Doesn't capture partial rotation
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.INCOMPLETE_REASONING,
            difficulty=2,
            custom_description="Student forgets that clock has 12-hour cycle; uses 24-hour clock denominator instead",
            custom_why_effective="Students often confuse clock (12 hours) with daily time (24 hours); both are familiar systems",
            custom_how_to_avoid="Remember: Clock fractions use denominator 12, not 24; a full clock rotation = 12 hours"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Clock as Fractions",
            logical_trap="K.C. Nag integration: Students don't connect fractions to clock rotations.",
            data_representation=f"```\nFull rotation: 12 hours\nHours elapsed: {hours}\n"
                               f"Fraction: {hours}/12 = {fraction:.2f} = {percent}%\n```",
            question_text=f"From 12 to {hours} o'clock, what fraction of a full rotation has occurred?",
            solution_steps=[
                "Full rotation = 12 hours",
                f"Hours from 12 to {hours} = {hours}",
                f"Fraction = {hours}/12"
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
    
    def _generate_clock_arithmetic(self) -> Question:
        """Clock arithmetic with modulo 12."""
        start_hour = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        add_hours = random.choice([2, 3, 4, 5])
        result = ((start_hour + add_hours - 1) % 12) + 1
        
        correct_answer = f"{result}:00"
        
        # 🆕 PHASE 1: CATEGORIZED DISTRACTORS
        misconception_map = {
            MisconceptionType.CONSTRAINT_VIOLATION: 
                f"{start_hour + add_hours}:00",  # Forgets modulo 12 rule
            MisconceptionType.OPERATION_DIRECTION: 
                f"{(start_hour + add_hours) % 12}:00",  # Wrong modulo application (off by one)
            MisconceptionType.INCOMPLETE_REASONING: 
                f"{start_hour}:00"  # Doesn't add at all
        }
        
        options, correct_idx, distractor_info = \
            self.create_categorized_distractors(correct_answer, misconception_map)
        
        # 🆕 PHASE 2: TRAP INFO
        trap_info = self.create_trap_info(
            MisconceptionType.CONSTRAINT_VIOLATION,
            difficulty=2,
            custom_description="Student forgets modulo 12 constraint on clock; reports time greater than 12",
            custom_why_effective="Violates the fundamental constraint that clock has only 12 hours; easy oversight",
            custom_how_to_avoid="After adding hours, check if result > 12; if yes, subtract 12 to get actual clock time"
        )
        # 🆕 Phase 3: Assign Bloom's cognitive level
        bloom_info = self.create_bloom_info(
            BloomLevel.APPLY,
            trap_difficulty=2
        )
        
        question = Question(
            chapter=self.chapter,
            topic="Shapes & Angles - Clock Arithmetic",
            logical_trap="Students forget that clock is modulo 12, not 24.",
            data_representation=f"```\nStart: {start_hour}:00\nAdd: {add_hours} hours\n"
                               f"Result: ({start_hour} + {add_hours}) mod 12 = {result}:00\n```",
            question_text=f"If it's {start_hour}:00 now, what time will it be after {add_hours} hours?",
            solution_steps=[
                f"Current time: {start_hour}:00",
                f"Add {add_hours} hours: {start_hour} + {add_hours} = {start_hour + add_hours}",
                f"Since clock cycles after 12: {result}:00"
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
