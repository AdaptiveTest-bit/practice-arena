"""Remediation Generator - Creates targeted help for misconceptions.

When a student shows a misconception pattern, this service:
1. Creates simplified questions to target the specific error
2. Builds 2-3 step remediation bundles
3. Provides step-by-step explanations
4. Tracks remediation effectiveness
"""

from typing import List, Optional, Dict, Tuple
from models.distractor import MisconceptionType, DistractorSet
from models.cognitive_levels import BloomLevel, BloomInfo
from models.student_progress import StudentProgress, MisconceptionEncounter


class RemediationStrategy:
    """Base class for remediation approaches."""
    
    def __init__(self, misconception: MisconceptionType):
        self.misconception = misconception
    
    def create_simplified_question(self) -> Dict:
        """Create a simpler version targeting this misconception."""
        raise NotImplementedError
    
    def create_bridge_question(self) -> Dict:
        """Create intermediate complexity question."""
        raise NotImplementedError
    
    def create_follow_up_question(self) -> Dict:
        """Create final verification question."""
        raise NotImplementedError


class RemediationBundle:
    """Multi-step remediation sequence for a misconception."""
    
    def __init__(
        self,
        misconception: MisconceptionType,
        student_id: str,
        chapter: str
    ):
        self.misconception = misconception
        self.student_id = student_id
        self.chapter = chapter
        self.steps: List[Dict] = []
        self.explanation: str = ""
        self.completed_steps: int = 0
        self.effectiveness_score: float = 0.0  # Will be updated after completion
    
    def add_step(self, question: Dict, hint: str, explanation: str):
        """Add a step to remediation sequence."""
        self.steps.append({
            "question": question,
            "hint": hint,
            "explanation": explanation,
            "step_number": len(self.steps) + 1,
            "total_steps": 3  # Standard 3-step remediation
        })
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable format."""
        return {
            "misconception": self.misconception.value,
            "student_id": self.student_id,
            "chapter": self.chapter,
            "steps": self.steps,
            "explanation": self.explanation,
            "completed_steps": self.completed_steps,
            "total_steps": len(self.steps),
            "effectiveness_score": self.effectiveness_score
        }


class RemediationGenerator:
    """
    Generates remediation sequences for identified misconceptions.
    
    Uses these remediation patterns:
    
    1. REFERENCE_POINT_ERROR:
       - Step 1: Find reference points on number line
       - Step 2: Compare distances from reference
       - Step 3: Place new number correctly
    
    2. FRACTION_PART_WHOLE:
       - Step 1: Identify what "whole" is
       - Step 2: Count equal parts
       - Step 3: Express as fraction
    
    3. DECIMAL_PLACE_VALUE:
       - Step 1: Identify place values (tenths, hundredths)
       - Step 2: Read decimal correctly
       - Step 3: Compare decimals using place value
    
    ... and so on for all 14 misconceptions
    """
    
    # Remediation templates for each misconception
    REMEDIATION_TEMPLATES = {
        "REFERENCE_POINT_ERROR": {
            "name": "Reference Point Identification",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "Look for numbers you know (0, 1, 0.5, etc.) and measure from there",
            "explanation": "When comparing or placing numbers, find a reference point you know well, then measure how far the target number is from that point."
        },
        "FRACTION_PART_WHOLE": {
            "name": "Understanding Fractions as Parts of a Whole",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "First identify what the 'whole' is, then count how many equal parts",
            "explanation": "A fraction is always relative to a whole. The denominator tells you how many equal parts the whole is divided into."
        },
        "DECIMAL_PLACE_VALUE": {
            "name": "Decimal Place Value Understanding",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "Think: tenths, hundredths, thousandths... each place is 1/10 of the previous",
            "explanation": "In decimals, each place value to the right is 10 times smaller: 0.1 is 1/10, 0.01 is 1/100, etc."
        },
        "PERCENTAGE_CONFUSION": {
            "name": "Understanding Percentages",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "Percent means 'out of 100'. So 25% = 25/100",
            "explanation": "Percentages are just fractions with 100 as the denominator. 50% means 50 out of 100."
        },
        "OPERATION_ORDER_ERROR": {
            "name": "Order of Operations (PEMDAS/BODMAS)",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "Remember: Parentheses, Exponents, Multiply/Divide (left to right), Add/Subtract (left to right)",
            "explanation": "Always follow the order: Parentheses first, then Exponents, then Multiply/Divide from left to right, then Add/Subtract from left to right."
        },
        "NEGATIVE_NUMBER_ERROR": {
            "name": "Understanding Negative Numbers",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "Think of a thermometer or number line. Below zero = negative.",
            "explanation": "Negative numbers represent amounts less than zero, like temperatures below freezing or debts."
        },
        "RATIO_PROPORTION_ERROR": {
            "name": "Ratios and Proportions",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "A ratio compares two quantities. A proportion says two ratios are equal.",
            "explanation": "If a recipe needs 2 cups flour for 1 cup sugar, then 4 cups flour needs 2 cups sugar (proportional)."
        },
        "MULTIPLICATION_MEANING_ERROR": {
            "name": "Multiplication as Repeated Addition",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "3 × 4 means '3 groups of 4' or '4 added together 3 times'",
            "explanation": "Multiplication is a shorthand for repeated addition. 3 × 4 = 4 + 4 + 4"
        },
        "DIVISION_MEANING_ERROR": {
            "name": "Understanding Division",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "12 ÷ 3 asks: 'How many 3s are in 12?' or 'If I split 12 into 3 equal groups, how many in each?'",
            "explanation": "Division answers: 'How many groups?' or 'How many in each group?'"
        },
        "EQUIVALENCE_ERROR": {
            "name": "Equivalent Fractions and Decimals",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "1/2 = 2/4 = 0.5 = 50%. They're the same amount, just written differently.",
            "explanation": "Different representations can show the same value. Multiply or divide both top and bottom by the same number to create equivalent fractions."
        },
        "ESTIMATION_ERROR": {
            "name": "Reasonable Estimation",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "Round to friendly numbers first, then calculate. Check if answer makes sense.",
            "explanation": "Estimation helps verify your answer. 23 × 5 ≈ 20 × 5 = 100 (reasonable check)."
        },
        "COMPARING_NUMBERS_ERROR": {
            "name": "Comparing and Ordering Numbers",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "Place numbers on a number line. Remember: > means 'to the right', < means 'to the left'",
            "explanation": "To compare numbers, place them on a number line or use place value. The greater value is to the right."
        },
        "ROUNDING_ERROR": {
            "name": "Rounding Rules",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "Look at the digit to the right. If it's 5 or more, round up. If it's less than 5, round down.",
            "explanation": "Rounding rule: Look at the digit to the right of where you're rounding. 5-9 round up, 0-4 round down."
        },
        "VARIABLE_MEANING_ERROR": {
            "name": "Understanding Variables",
            "level": BloomLevel.UNDERSTAND,
            "steps": 3,
            "hint": "A variable is just a box or container that holds an unknown number. 'x' could be any number!",
            "explanation": "Variables represent unknown quantities. In 2x + 3 = 7, 'x' is a number we need to find (x = 2)."
        }
    }
    
    @staticmethod
    def create_remediation_for_misconception(
        misconception: MisconceptionType,
        student_id: str,
        chapter: str,
        student_progress: Optional[StudentProgress] = None
    ) -> RemediationBundle:
        """
        Create a 3-step remediation bundle for a misconception.
        
        Returns: RemediationBundle with simplified, bridge, and follow-up questions
        """
        
        template = RemediationGenerator.REMEDIATION_TEMPLATES.get(
            misconception.value,
            RemediationGenerator.REMEDIATION_TEMPLATES["REFERENCE_POINT_ERROR"]  # Default
        )
        
        bundle = RemediationBundle(misconception, student_id, chapter)
        bundle.explanation = template["explanation"]
        
        # Step 1: Simplified question (REMEMBER level)
        step1_question = RemediationGenerator._create_step1_simplified(
            misconception, chapter, template
        )
        bundle.add_step(
            step1_question,
            hint="Focus on the basic concept first.",
            explanation=template["explanation"]
        )
        
        # Step 2: Bridge question (UNDERSTAND level)
        step2_question = RemediationGenerator._create_step2_bridge(
            misconception, chapter, template
        )
        bundle.add_step(
            step2_question,
            hint=template["hint"],
            explanation="You're doing great! Now let's apply the concept a bit differently."
        )
        
        # Step 3: Follow-up question (similar to original misconception)
        step3_question = RemediationGenerator._create_step3_followup(
            misconception, chapter, student_progress
        )
        bundle.add_step(
            step3_question,
            hint="Remember the concept from the previous steps!",
            explanation="Now try the original type of problem with your new understanding."
        )
        
        return bundle
    
    @staticmethod
    def _create_step1_simplified(
        misconception: MisconceptionType,
        chapter: str,
        template: Dict
    ) -> Dict:
        """Create very simple question targeting misconception concept."""
        
        return {
            "type": "step1_simplified",
            "misconception": misconception.value,
            "difficulty": 1,  # Easiest
            "bloom_level": "REMEMBER",
            "estimated_time": 30,  # seconds
            "guidance": "This is a basic question to check understanding of the concept",
            "content": f"Simple {misconception.value} remediation question for {chapter}",
            "options": [
                "Option A (explanation: correct concept)",
                "Option B (explanation: common misconception)",
                "Option C (explanation: alternate error)",
                "Option D (explanation: plausible but wrong)"
            ]
        }
    
    @staticmethod
    def _create_step2_bridge(
        misconception: MisconceptionType,
        chapter: str,
        template: Dict
    ) -> Dict:
        """Create intermediate question building on misconception understanding."""
        
        return {
            "type": "step2_bridge",
            "misconception": misconception.value,
            "difficulty": 2,  # Easy-medium
            "bloom_level": "UNDERSTAND",
            "estimated_time": 45,  # seconds
            "guidance": template["hint"],
            "content": f"Intermediate {misconception.value} remediation question for {chapter}",
            "options": [
                "Option A (explanation: correct concept)",
                "Option B (explanation: related misconception)",
                "Option C (explanation: different error)",
                "Option D (explanation: plausible but wrong)"
            ]
        }
    
    @staticmethod
    def _create_step3_followup(
        misconception: MisconceptionType,
        chapter: str,
        student_progress: Optional[StudentProgress] = None
    ) -> Dict:
        """Create follow-up matching original difficulty."""
        
        difficulty = 2  # Default medium
        if student_progress:
            # Use student's current difficulty, but ensure not too hard during remediation
            difficulty = min(student_progress.current_difficulty, 3)
        
        return {
            "type": "step3_followup",
            "misconception": misconception.value,
            "difficulty": difficulty,
            "bloom_level": "UNDERSTAND",
            "estimated_time": 60,  # seconds
            "guidance": "You've practiced the concept. Let's see if it sticks!",
            "content": f"Follow-up {misconception.value} remediation question for {chapter}",
            "options": [
                "Option A (explanation: correct concept)",
                "Option B (explanation: original misconception)",
                "Option C (explanation: related error)",
                "Option D (explanation: plausible but wrong)"
            ]
        }
    
    @staticmethod
    def create_multi_misconception_remediation(
        misconceptions: List[MisconceptionType],
        student_id: str,
        chapter: str
    ) -> List[RemediationBundle]:
        """
        Create remediation bundles for multiple misconceptions.
        
        Returns: List of RemediationBundle objects, prioritized by frequency
        """
        
        bundles = []
        for misconception in misconceptions:
            bundle = RemediationGenerator.create_remediation_for_misconception(
                misconception, student_id, chapter
            )
            bundles.append(bundle)
        
        return bundles
    
    @staticmethod
    def get_misconception_explanation(
        misconception: MisconceptionType
    ) -> Dict:
        """Get detailed explanation of a misconception for teachers."""
        
        template = RemediationGenerator.REMEDIATION_TEMPLATES.get(
            misconception.value,
            {}
        )
        
        return {
            "misconception": misconception.value,
            "name": template.get("name", "Unknown Misconception"),
            "explanation": template.get("explanation", ""),
            "hint": template.get("hint", ""),
            "recommended_bloom_level": template.get("level", BloomLevel.UNDERSTAND).value,
            "remediation_steps": template.get("steps", 3),
            "why_students_make_this_error": (
                "Students often apply rules from one context to another inappropriately, "
                "or misunderstand the fundamental concept. Targeted practice with "
                "simplified examples helps build correct understanding."
            )
        }


class RemediationTracker:
    """Track effectiveness of remediation attempts."""
    
    @staticmethod
    def evaluate_remediation_effectiveness(
        student_progress: StudentProgress,
        misconception: MisconceptionType,
        student_correct_after_remediation: bool
    ) -> Tuple[float, str]:
        """
        Evaluate if remediation worked.
        
        Returns: (effectiveness_score: 0-100, assessment: str)
        """
        
        misc_record = student_progress.misconceptions.get(misconception.value)
        if not misc_record:
            return (0.0, "No prior record of this misconception")
        
        if student_correct_after_remediation:
            effectiveness_score = 100.0
            assessment = "✅ Remediation successful! Misconception appears resolved."
            misc_record.mark_remediation_complete(effective=True)
        else:
            # Student still got it wrong after remediation
            effectiveness_score = 25.0
            assessment = "⚠️ Remediation didn't fully work. May need different approach."
            misc_record.mark_remediation_complete(effective=False)
        
        return (effectiveness_score, assessment)
    
    @staticmethod
    def get_remediation_summary(
        student_progress: StudentProgress
    ) -> Dict:
        """Get summary of remediation attempts for this student."""
        
        remediated_misconceptions = [
            {
                "misconception": misc_type,
                "attempts": misc.encounter_count,
                "remediation_provided": misc.remediation_provided,
                "remediation_effective": misc.remediation_effective
            }
            for misc_type, misc in student_progress.misconceptions.items()
        ]
        
        effective_remediations = sum(
            1 for m in remediated_misconceptions
            if m["remediation_effective"]
        )
        
        total_remediations = sum(
            1 for m in remediated_misconceptions
            if m["remediation_provided"]
        )
        
        return {
            "total_misconceptions": len(remediated_misconceptions),
            "remediations_provided": total_remediations,
            "remediations_effective": effective_remediations,
            "effectiveness_rate": (
                effective_remediations / total_remediations * 100
                if total_remediations > 0 else 0
            ),
            "details": remediated_misconceptions
        }
