"""
Quick Start: Using the Question Bank Loader
============================================

This guide shows how to use the newly created question bank system.
"""

# ============================================================================
# EXAMPLE 1: Load and Query the Question Bank
# ============================================================================

from services.question_bank_loader import QuestionBank

# Initialize the question bank
bank = QuestionBank('/backend/data/class5_chapter5_bank.yaml')

# Get statistics
stats = bank.stats()
print(f"Total questions: {stats['total_questions']}")
print(f"By category: {stats['by_category']}")
print(f"By difficulty: {stats['by_difficulty']}")
print(f"By Bloom's level: {stats['by_bloom_level']}")

# Get all factors_multiples questions
all_factors = bank.get_by_category('factors_multiples')
print(f"Found {len(all_factors)} factors/multiples questions")

# Get medium difficulty factors_multiples questions
medium_factors = bank.get_by_category_difficulty('factors_multiples', difficulty=2)
print(f"Found {len(medium_factors)} medium difficulty questions")

# Get all APPLY level questions
apply_questions = bank.get_by_bloom_level('APPLY')
print(f"Found {len(apply_questions)} APPLY level questions")

# Get questions about a specific concept
hcf_questions = bank.get_by_concept('HCF')
print(f"Found {len(hcf_questions)} HCF questions")

# Get random sample
sample = bank.get_random_sample(count=5, difficulty=1)
print(f"Random sample: {len(sample)} questions")

# Get random sample with filters
hard_apply_sample = bank.get_random_sample(
    count=10,
    difficulty=3,
    bloom_level='APPLY'
)

# ============================================================================
# EXAMPLE 2: Convert YAML to Question Objects
# ============================================================================

from services.question_bank_loader import QuestionConstructor

# Get a question from the bank
yaml_question = bank.get_by_category('factors_multiples')[0]

# Convert to Question object with all rich content
question = QuestionConstructor.construct_from_yaml(yaml_question)

# Access the rich content
print(question.question_text)
print(question.rich_narrative)  # NOT None!
print(question.rich_html_content)  # NOT None!
print(question.visual_hints)  # Populated!

# Access pedagogical metadata
print(f"Bloom's level: {question.bloom_info.bloom_level}")
print(f"Difficulty: {question.difficulty}")
print(f"Trap type: {question.trap_info.trap_type}")
print(f"Teaching point: {question.trap_info.description}")

# Access distractors with misconceptions
for distractor in question.distractor_info.distractors:
    print(f"Distractor: {distractor.value}")
    print(f"Misconception: {distractor.misconception_type}")
    print(f"Teaching point: {distractor.teaching_point}")

# ============================================================================
# EXAMPLE 3: Integrate with Strategy (in factors_multiples_integrated.py)
# ============================================================================

# This example shows how to modify the strategy to use the question bank

class FactorsMultiplesIntegrated(BaseChapterStrategy):
    
    def __init__(self):
        super().__init__()
        # Load question bank (60% of questions come from here)
        self.question_bank = QuestionBank(
            '/backend/data/class5_chapter5_bank.yaml'
        )
    
    def _generate_from_bank(self, chapter: str, difficulty: int) -> Question:
        """
        Generate a question from the pre-authored bank.
        This provides 60% of all questions.
        """
        # Get questions at this difficulty level
        bank_questions = self.question_bank.get_by_category_difficulty(
            'factors_multiples', difficulty
        )
        
        if not bank_questions:
            # Fallback to dynamic generation if nothing at this difficulty
            return self._generate_find_factors_integrated(difficulty)
        
        # Pick random question from bank
        import random
        selected = random.choice(bank_questions)
        
        # Convert YAML to Question object with all rich content
        return QuestionConstructor.construct_from_yaml(selected)
    
    def generate(self, chapter: str, difficulty: int) -> Question:
        """
        Generate a question with 60/40 weighting:
        - 60% from pre-authored question bank
        - 40% from dynamic generation (ensures variety)
        """
        import random
        
        if random.random() < 0.6:
            # 60% from bank
            return self._generate_from_bank(chapter, difficulty)
        else:
            # 40% from dynamic generation
            # Use existing methods: _generate_find_factors_integrated, etc.
            methods = [
                self._generate_find_factors_integrated,
                self._generate_find_multiples_integrated,
                self._generate_find_gcd_integrated,
                self._generate_find_lcm_integrated,
                self._generate_divisibility_integrated,
            ]
            method = random.choice(methods)
            return method(difficulty)

# ============================================================================
# EXAMPLE 4: Adaptive Learning with Filters
# ============================================================================

# Example: Get questions for a student who struggles with HCF/LCM confusion

from models.distractor import MisconceptionType

# Get questions that specifically test the misconception the student struggles with
student_misconception = 'INCOMPLETE_REASONING'
remedial_questions = bank.get_by_misconception(student_misconception)

print(f"Found {len(remedial_questions)} questions targeting this misconception")

# Get progressively harder versions
easy_versions = bank.get_by_category_difficulty('factors_multiples', 1)
medium_versions = bank.get_by_category_difficulty('factors_multiples', 2)
hard_versions = bank.get_by_category_difficulty('factors_multiples', 3)

# Create adaptive sequence
adaptive_path = [
    QuestionConstructor.construct_from_yaml(q)
    for q in (easy_versions + medium_versions + hard_versions)[:5]
]

# ============================================================================
# EXAMPLE 5: Analytics - Track Misconceptions
# ============================================================================

# Example: Analyze which misconceptions are tested most

from collections import Counter

all_questions = bank.get_all_questions()

misconception_counts = Counter()
for q in all_questions:
    misconception_counts[q.get('misconception_type', 'UNKNOWN')] += 1

print("Misconception distribution:")
for misconception, count in misconception_counts.most_common():
    print(f"  {misconception}: {count} questions")

# By Bloom's level
bloom_counts = Counter()
for q in all_questions:
    bloom_counts[q.get('bloom_level', 'UNKNOWN')] += 1

print("Bloom's level distribution:")
for level, count in bloom_counts.most_common():
    print(f"  {level}: {count} questions")

# ============================================================================
# EXAMPLE 6: Export for Frontend
# ============================================================================

import json

# Get a question and format for API response
question_yaml = bank.get_by_category('factors_multiples')[0]
question = QuestionConstructor.construct_from_yaml(question_yaml)

# Build API response
api_response = {
    'id': question_yaml['id'],
    'questionText': question.question_text,
    'options': question.options,
    'correctAnswer': question.answer,
    'difficulty': question.difficulty,
    'bloomLevel': question.bloom_info.bloom_level,
    # Rich content for enhanced UI
    'richNarrative': question.rich_narrative,
    'richHtmlContent': question.rich_html_content,
    'visualHints': question.visual_hints,
    # Pedagogical metadata
    'concept': question.topic,
    'trapInfo': {
        'trapType': question.trap_info.trap_type,
        'description': question.trap_info.description,
        'howToAvoid': question.trap_info.how_to_avoid,
    },
    'distractors': [
        {
            'value': d.value,
            'misconception': d.misconception_type,
            'teachingPoint': d.teaching_point,
        }
        for d in question.distractor_info.distractors
    ]
}

print(json.dumps(api_response, indent=2))

# ============================================================================
# EXAMPLE 7: Batch Generation
# ============================================================================

# Generate 30 questions of mixed difficulty for a practice set

practice_set = []
for _ in range(30):
    difficulty = random.choices([1, 2, 3, 4, 5], weights=[10, 15, 20, 25, 30])[0]
    question_yaml = random.choice(
        bank.get_by_category_difficulty('factors_multiples', difficulty)
    )
    question = QuestionConstructor.construct_from_yaml(question_yaml)
    practice_set.append(question)

print(f"Created practice set with {len(practice_set)} questions")

# Verify all have rich content
for i, q in enumerate(practice_set):
    assert q.rich_narrative is not None, f"Question {i} missing narrative"
    assert q.rich_html_content is not None, f"Question {i} missing HTML"
    assert len(q.visual_hints) > 0, f"Question {i} missing hints"

print("✓ All questions have complete rich content!")
