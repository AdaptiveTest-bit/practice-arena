"""Clock Angles question strategy."""

from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum
import random


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
        distractors = [f"{hour * 6}°", f"{hour * 60}°", f"{360 - angle}°"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_minute_angle(self) -> Question:
        """Calculate angle of minute hand."""
        minutes = random.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        angle = (minutes // 5) * 30  # 60 minutes = 360°, so 5 min = 30°
        
        correct_answer = f"{angle}°"
        distractors = [f"{minutes}°", f"{minutes * 6}°", f"{360 - angle}°"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
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
        distractors = [f"{360 - hour_angle}°", f"{hour * 60}°", "180°"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_time_from_angle(self) -> Question:
        """Find time from given hour hand angle."""
        angle = random.choice([30, 60, 90, 120, 150, 180])
        hour = angle // 30
        
        correct_answer = f"{hour}:00"
        distractors = [f"{hour-1}:00", f"{hour+1}:00", f"{angle // 6}:00"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_fraction_rotation(self) -> Question:
        """Express clock movement as fraction of rotation."""
        hours = random.choice([3, 6, 9, 12])
        fraction = hours / 12
        percent = int(fraction * 100)
        
        correct_answer = f"{hours}/12 of rotation ({percent}%)"
        distractors = [f"{hours}/24 of rotation", f"{12-hours}/12 of rotation", "1 full rotation"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
    
    def _generate_clock_arithmetic(self) -> Question:
        """Clock arithmetic with modulo 12."""
        start_hour = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        add_hours = random.choice([2, 3, 4, 5])
        result = ((start_hour + add_hours - 1) % 12) + 1
        
        correct_answer = f"{result}:00"
        distractors = [f"{start_hour + add_hours}:00", f"{(start_hour + add_hours) % 12}:00", 
                      f"{start_hour}:00"]
        
        options = self.ensure_unique_options([correct_answer] + distractors)
        correct_idx = options.index(correct_answer)
        
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
            correct_option_index=correct_idx
        )
        
        self._validate_question(question)
        return question
