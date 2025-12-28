"""Phase 4 Integration Tests - Validate sequencing, tracking, and remediation.

Tests the complete Phase 4 system:
1. StudentProgress model and mastery tracking
2. PerformanceTracker calculations
3. AdaptiveSequencingEngine recommendations
4. RemediationGenerator sequences
5. Classroom analytics
"""

import sys
import os
from datetime import datetime

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student_progress import (
    StudentProgress,
    AttemptResult,
    SequencingRecommendation
)
from models.distractor import MisconceptionType
from models.cognitive_levels import BloomLevel
from services.performance_tracker import PerformanceTracker, ClassroomAnalytics
from services.sequencing_engine import AdaptiveSequencingEngine, QuestionSelector
from services.remediation_generator import RemediationGenerator, RemediationTracker


def test_student_progress_tracking():
    """Test StudentProgress model tracks attempts correctly."""
    print("\n✅ Test 1: Student Progress Tracking")
    
    # Create student
    student = StudentProgress(
        student_id="student_001",
        chapter="fractions_decimals"
    )
    
    # Record some attempts
    for i in range(5):
        attempt = AttemptResult(
            attempt_id=f"attempt_{i}",
            student_id="student_001",
            question_id=f"q_{i}",
            chapter="fractions_decimals",
            response_selected=0,
            is_correct=(i % 2 == 0),  # Alternating correct/wrong
            time_spent_seconds=60,
            difficulty_level=2,
            bloom_level=BloomLevel.UNDERSTAND,
            misconception_revealed=(
                MisconceptionType.REFERENCE_POINT_ERROR if i % 2 != 0 else None
            )
        )
        student.record_attempt(attempt)
    
    print(f"  - Total attempts: {student.total_attempts} (expected: 5)")
    print(f"  - Total correct: {student.total_correct} (expected: 3)")
    print(f"  - Overall percentage: {student.overall_percentage:.1f}% (expected: 60%)")
    print(f"  - Misconceptions tracked: {len(student.misconceptions)}")
    
    assert student.total_attempts == 5, "Should have 5 attempts"
    assert student.total_correct == 3, "Should have 3 correct"
    assert student.overall_percentage == 60.0, "Should be 60%"
    assert MisconceptionType.REFERENCE_POINT_ERROR.value in student.misconceptions, "Should track misconception"
    
    print("  ✓ Student progress tracking works correctly")


def test_performance_metrics():
    """Test PerformanceTracker calculations."""
    print("\n✅ Test 2: Performance Metrics Calculation")
    
    student = StudentProgress(
        student_id="student_002",
        chapter="fractions_decimals"
    )
    
    # Simulate improving performance
    correct_sequence = [True, True, False, True, True, True, True, True]  # 7/8 = 87.5%
    
    for i, is_correct in enumerate(correct_sequence):
        attempt = AttemptResult(
            attempt_id=f"attempt_{i}",
            student_id="student_002",
            question_id=f"q_{i}",
            chapter="fractions_decimals",
            response_selected=0,
            is_correct=is_correct,
            time_spent_seconds=60,
            difficulty_level=3,
            bloom_level=BloomLevel.APPLY
        )
        student, metrics = PerformanceTracker.process_attempt(student, attempt)
    
    print(f"  - Final percentage: {student.overall_percentage:.1f}% (expected: 87.5%)")
    print(f"  - Difficulty 3 mastery: {student.difficulty_mastery[3].percentage_correct:.1f}%")
    
    # Check bloom mastery for APPLY level
    bloom_apply_key = BloomLevel.APPLY.value  # Get the actual string key
    if bloom_apply_key in student.bloom_mastery:
        print(f"  - Bloom APPLY mastery: {student.bloom_mastery[bloom_apply_key].percentage_correct:.1f}%")
    
    print(f"  - Is mastered (D3): {student.difficulty_mastery[3].mastered}")
    
    assert student.overall_percentage == 87.5, "Should be 87.5%"
    assert student.difficulty_mastery[3].mastered == True, "Should be mastered at D3"
    
    print("  ✓ Performance metrics calculated correctly")


def test_sequencing_recommendations():
    """Test AdaptiveSequencingEngine provides smart recommendations."""
    print("\n✅ Test 3: Adaptive Sequencing Recommendations")
    
    # Scenario 1: Student struggling - should retreat
    print("\n  Scenario 1: Struggling student")
    student1 = StudentProgress(
        student_id="student_003",
        chapter="fractions_decimals"
    )
    student1.current_difficulty = 3
    student1.difficulty_mastery[3].attempts = 5
    student1.difficulty_mastery[3].correct = 2
    student1.difficulty_mastery[3].percentage_correct = 40.0
    
    rec1 = AdaptiveSequencingEngine.get_next_recommendation(student1)
    print(f"    - Recommendation: {rec1.action}")
    print(f"    - Next difficulty: {rec1.next_difficulty} (expected: 2)")
    print(f"    - Reason: {rec1.reason[:60]}...")
    
    assert rec1.action == "retreat", "Should retreat when struggling"
    assert rec1.next_difficulty == 2, "Should go to D2"
    
    # Scenario 2: Student mastering - should advance
    print("\n  Scenario 2: Mastering student")
    student2 = StudentProgress(
        student_id="student_004",
        chapter="fractions_decimals"
    )
    student2.current_difficulty = 2
    student2.difficulty_mastery[2].attempts = 5
    student2.difficulty_mastery[2].correct = 5
    student2.difficulty_mastery[2].percentage_correct = 100.0
    student2.difficulty_mastery[2].mastered = True
    
    rec2 = AdaptiveSequencingEngine.get_next_recommendation(student2)
    print(f"    - Recommendation: {rec2.action}")
    print(f"    - Next difficulty: {rec2.next_difficulty} (expected: 3)")
    
    assert rec2.action == "advance", "Should advance when mastered"
    assert rec2.next_difficulty == 3, "Should go to D3"
    
    # Scenario 3: Student with misconception - should remediate
    print("\n  Scenario 3: Student with misconception")
    student3 = StudentProgress(
        student_id="student_005",
        chapter="fractions_decimals"
    )
    # Initialize the misconception first
    misc_key = MisconceptionType.REFERENCE_POINT_ERROR.value
    if misc_key not in student3.misconceptions:
        from models.student_progress import MisconceptionEncounter
        student3.misconceptions[misc_key] = MisconceptionEncounter(
            misconception_type=MisconceptionType.REFERENCE_POINT_ERROR
        )
    student3.misconceptions[misc_key].encounter_count = 3
    
    rec3 = AdaptiveSequencingEngine.get_next_recommendation(student3)
    print(f"    - Recommendation: {rec3.action}")
    print(f"    - Target misconception: {rec3.target_misconception}")
    print(f"    - Urgency: {rec3.urgency}")
    
    assert rec3.action == "remediate", "Should remediate with misconception"
    assert rec3.target_misconception == MisconceptionType.REFERENCE_POINT_ERROR
    
    print("  ✓ Sequencing recommendations work correctly")


def test_remediation_generation():
    """Test RemediationGenerator creates targeted help."""
    print("\n✅ Test 4: Remediation Generation")
    
    # Create remediation for a misconception
    bundle = RemediationGenerator.create_remediation_for_misconception(
        misconception=MisconceptionType.REFERENCE_POINT_ERROR,
        student_id="student_006",
        chapter="fractions_decimals"
    )
    
    print(f"  - Misconception: {bundle.misconception.value}")
    print(f"  - Number of remediation steps: {len(bundle.steps)} (expected: 3)")
    print(f"  - Step 1 type: {bundle.steps[0]['question']['type']}")
    print(f"  - Step 2 type: {bundle.steps[1]['question']['type']}")
    print(f"  - Step 3 type: {bundle.steps[2]['question']['type']}")
    print(f"  - Explanation preview: {bundle.explanation[:50]}...")
    
    assert len(bundle.steps) == 3, "Should have 3 remediation steps"
    assert bundle.steps[0]['question']['bloom_level'] == "REMEMBER", "Step 1 should be REMEMBER"
    assert bundle.steps[1]['question']['bloom_level'] == "UNDERSTAND", "Step 2 should be UNDERSTAND"
    assert bundle.steps[2]['question']['bloom_level'] == "UNDERSTAND", "Step 3 should be UNDERSTAND"
    
    print("  ✓ Remediation sequences generated correctly")


def test_classroom_analytics():
    """Test ClassroomAnalytics provides teacher insights."""
    print("\n✅ Test 5: Classroom Analytics")
    
    # Create a small class
    students = []
    for i in range(5):
        student = StudentProgress(
            student_id=f"student_{i:03d}",
            chapter="fractions_decimals"
        )
        
        # Vary performance
        for j in range(10):
            attempt = AttemptResult(
                attempt_id=f"attempt_{j}",
                student_id=f"student_{i:03d}",
                question_id=f"q_{j}",
                chapter="fractions_decimals",
                response_selected=0,
                is_correct=(j % (3 - i % 3) == 0),  # Vary success rate
                time_spent_seconds=60,
                difficulty_level=2,
                bloom_level=BloomLevel.UNDERSTAND,
                misconception_revealed=(
                    MisconceptionType.REFERENCE_POINT_ERROR if j % 5 == 0 else None
                )
            )
            student.record_attempt(attempt)
        
        students.append(student)
    
    # Analyze class
    class_stats = ClassroomAnalytics.get_class_statistics(students)
    print(f"  - Class size: {class_stats['class_size']} (expected: 5)")
    print(f"  - Average percentage: {class_stats['average_percentage']:.1f}%")
    print(f"  - Students above 80%: {class_stats['students_above_80']}")
    
    misconceptions = ClassroomAnalytics.get_misconception_hot_spots(students)
    print(f"  - Hot spot misconceptions: {len(misconceptions['hot_spot_misconceptions'])}")
    if misconceptions['hot_spot_misconceptions']:
        print(f"    - Top: {misconceptions['hot_spot_misconceptions'][0]['type']}")
    
    difficulty_dist = ClassroomAnalytics.get_difficulty_distribution(students)
    print(f"  - Difficulty distribution: {difficulty_dist['distribution']}")
    
    print("  ✓ Classroom analytics generated correctly")


def test_learning_path_optimization():
    """Test LearningPathOptimization provides personalized strategies."""
    print("\n✅ Test 6: Learning Path Optimization")
    
    from services.performance_tracker import LearningPathOptimization
    
    # Create student with moderate performance
    student = StudentProgress(
        student_id="student_007",
        chapter="fractions_decimals"
    )
    
    for i in range(15):
        attempt = AttemptResult(
            attempt_id=f"attempt_{i}",
            student_id="student_007",
            question_id=f"q_{i}",
            chapter="fractions_decimals",
            response_selected=0,
            is_correct=(i < 12),  # 12/15 = 80%
            time_spent_seconds=60,
            difficulty_level=2,
            bloom_level=BloomLevel.UNDERSTAND
        )
        student.record_attempt(attempt)
    
    # Get estimates
    estimate = LearningPathOptimization.estimate_mastery_time(
        student,
        target_percentage=90.0
    )
    print(f"  - Current percentage: {estimate.get('current_percentage', 'N/A')}")
    print(f"  - Estimated attempts to 90%: {estimate.get('estimated_additional_attempts', 'N/A')}")
    
    strategy = LearningPathOptimization.get_personalized_strategy(student)
    print(f"  - Strategy: {strategy['strategy']}")
    print(f"  - Description preview: {strategy['description'][:50]}...")
    
    assert strategy['strategy'] == "Advancement", "80% should be advancement strategy"
    
    print("  ✓ Learning path optimization works correctly")


def test_remediation_effectiveness():
    """Test RemediationTracker evaluates remediation success."""
    print("\n✅ Test 7: Remediation Effectiveness Tracking")
    
    student = StudentProgress(
        student_id="student_008",
        chapter="fractions_decimals"
    )
    
    # Record initial misconception
    attempt = AttemptResult(
        attempt_id="attempt_0",
        student_id="student_008",
        question_id="q_0",
        chapter="fractions_decimals",
        response_selected=0,
        is_correct=False,
        time_spent_seconds=60,
        difficulty_level=2,
        bloom_level=BloomLevel.UNDERSTAND,
        misconception_revealed=MisconceptionType.REFERENCE_POINT_ERROR
    )
    student.record_attempt(attempt)
    
    # Evaluate remediation effectiveness
    score, assessment = RemediationTracker.evaluate_remediation_effectiveness(
        student,
        MisconceptionType.REFERENCE_POINT_ERROR,
        student_correct_after_remediation=True
    )
    
    print(f"  - Effectiveness score: {score} (expected: 100)")
    print(f"  - Assessment: {assessment}")
    print(f"  - Remediation marked effective: {student.misconceptions[MisconceptionType.REFERENCE_POINT_ERROR.value].remediation_effective}")
    
    assert score == 100.0, "Should be 100 for successful remediation"
    assert student.misconceptions[MisconceptionType.REFERENCE_POINT_ERROR.value].remediation_effective == True
    
    print("  ✓ Remediation effectiveness tracking works correctly")


def test_question_selection_criteria():
    """Test QuestionSelector generates proper criteria."""
    print("\n✅ Test 8: Question Selection Criteria")
    
    recommendation = SequencingRecommendation(
        action="advance",
        next_difficulty=3,
        next_bloom_level=BloomLevel.APPLY,
        target_misconception=None,
        reason="Student ready for advancement"
    )
    
    criteria = QuestionSelector.get_selection_criteria(recommendation)
    print(f"  - Difficulty: {criteria['difficulty']} (expected: 3)")
    print(f"  - Bloom level: {criteria['bloom_level']}")
    print(f"  - Action: {criteria['action']}")
    
    context_msg = QuestionSelector.generate_context_message(recommendation)
    print(f"  - Context message preview: {context_msg[:50]}...")
    
    assert criteria['difficulty'] == 3, "Should have correct difficulty"
    assert criteria['bloom_level'] == BloomLevel.APPLY, "Should have correct bloom level"
    
    print("  ✓ Question selection criteria generated correctly")


def main():
    """Run all Phase 4 integration tests."""
    print("\n" + "="*70)
    print("PHASE 4 INTEGRATION TEST SUITE")
    print("Testing: Student Progress, Sequencing, Tracking, Remediation")
    print("="*70)
    
    try:
        test_student_progress_tracking()
        test_performance_metrics()
        test_sequencing_recommendations()
        test_remediation_generation()
        test_classroom_analytics()
        test_learning_path_optimization()
        test_remediation_effectiveness()
        test_question_selection_criteria()
        
        print("\n" + "="*70)
        print("🎉 PHASE 4 INTEGRATION TESTS PASSED!")
        print("="*70)
        print("\n✅ All systems operational:")
        print("  1. Student progress tracking: ✓")
        print("  2. Performance metrics: ✓")
        print("  3. Adaptive sequencing: ✓")
        print("  4. Remediation generation: ✓")
        print("  5. Classroom analytics: ✓")
        print("  6. Learning path optimization: ✓")
        print("  7. Remediation effectiveness: ✓")
        print("  8. Question selection: ✓")
        print("\nPhase 4 Core Intelligence Ready for Deployment! 🚀\n")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
