#!/usr/bin/env python
"""
Quick test script to verify all services are working correctly.

This script:
1. Creates a test session
2. Simulates student answering questions
3. Tracks progress through all systems
4. Generates reports

Run with: python test_implementation.py
"""

from datetime import datetime
from services.session_manager import SessionManager
from services.bloom_level_enforcer import BloomLevelEnforcer
from services.concept_mastery_tracker import ConceptMasteryTracker
from services.break_point_tracker import BreakPointTracker


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_session_management():
    """Test session creation and management."""
    print_header("TEST 1: Session Management")
    
    sm = SessionManager()
    
    # Use a unique student ID for testing
    import random
    test_student_id = 10000 + random.randint(0, 9999)
    
    # Test 1: Create new session
    print("\n✓ Creating new practice session...")
    result = sm.start_session(
        student_id=test_student_id,
        chapter_id=5,
        class_level=5,
        subject="Mathematics"
    )
    
    assert result["success"], "Failed to create session"
    assert result["status"] == "new", "Session should be new"
    session_id = result["session_id"]
    print(f"  Session ID: {session_id}")
    print(f"  Status: {result['status']}")
    print(f"  Current Bloom Level: {result['current_bloom_level']}")
    
    # Test 2: Resume session
    print("\n✓ Attempting to resume same session...")
    result2 = sm.start_session(student_id=test_student_id, chapter_id=5)
    assert result2["status"] == "resumed", "Should resume existing session"
    assert result2["session_id"] == session_id, "Should return same session ID"
    print(f"  Status: {result2['status']} ✓")
    
    # Test 3: Get progress
    print("\n✓ Getting session progress...")
    progress = sm.get_session_progress(session_id)
    assert progress is not None, "Should get progress"
    print(f"  Completion: {progress['completion_percentage']}%")
    print(f"  Session Duration: {progress['session_duration_minutes']} minutes")
    print(f"  Concepts Covered: {progress['concepts_covered']}")
    
    return session_id


def test_bloom_level_progression(session_id):
    """Test Bloom's level progression logic."""
    print_header("TEST 2: Bloom's Level Progression")
    
    be = BloomLevelEnforcer()
    
    # Test 1: Check current level
    print("\n✓ Checking current Bloom level...")
    current = be.get_current_level(session_id)
    print(f"  Current Level: {current}")
    assert current == "remember", "Should start at remember"
    
    # Test 2: Try to advance (should fail - no accuracy)
    print("\n✓ Attempting premature advancement...")
    result = be.can_advance_to_next_level(session_id, "remember")
    assert not result["can_advance"], "Should not be able to advance without accuracy"
    print(f"  Can Advance: {result['can_advance']}")
    print(f"  Message: {result['message']}")
    
    # Test 3: Update accuracy (simulate answers)
    print("\n✓ Simulating 7 correct answers out of 7...")
    for i in range(7):
        be.update_level_accuracy(session_id, "remember", is_correct=True)
    
    # Test 4: Check advancement eligibility
    print("\n✓ Checking advancement after practicing...")
    result = be.can_advance_to_next_level(session_id, "remember")
    assert result["can_advance"], "Should be able to advance now"
    print(f"  Can Advance: {result['can_advance']} ✓")
    print(f"  Current Accuracy: {result['current_accuracy']}")
    
    # Test 5: Advance level
    print("\n✓ Advancing to next level...")
    advance_result = be.advance_to_next_level(session_id, "remember")
    assert advance_result["success"], "Advancement failed"
    print(f"  Previous: {advance_result['previous_level']}")
    print(f"  Current: {advance_result['current_level']} ✓")
    
    # Test 6: Verify new level is unlocked
    print("\n✓ Verifying new level status...")
    new_current = be.get_current_level(session_id)
    assert new_current == "understand", "Should now be at understand"
    print(f"  New Current Level: {new_current} ✓")


def test_concept_mastery(session_id):
    """Test concept mastery tracking."""
    print_header("TEST 3: Concept Mastery Tracking")
    
    ct = ConceptMasteryTracker()
    
    # Test 1: Track concept accuracy (weak)
    print("\n✓ Simulating weak concept performance...")
    for i in range(5):
        correct = i < 3  # 3 out of 5 correct = 60%
        result = ct.update_concept_accuracy(
            session_id,
            "place_value",
            is_correct=correct,
            bloom_level="remember"
        )
    
    assert result["accuracy"] == 0.6, "Should be 60% accuracy"
    assert result["is_weak"], "Should be marked weak"
    print(f"  Concept: place_value")
    print(f"  Accuracy: {result['accuracy']*100:.0f}%")
    print(f"  Status: {result['mastery_status']} ✓")
    
    # Test 2: Track mastered concept
    print("\n✓ Simulating mastered concept performance...")
    for i in range(5):
        result = ct.update_concept_accuracy(
            session_id,
            "rounding",
            is_correct=True,  # All correct = 100%
            bloom_level="remember"
        )
    
    assert result["is_mastered"], "Should be marked mastered"
    print(f"  Concept: rounding")
    print(f"  Accuracy: {result['accuracy']*100:.0f}%")
    print(f"  Status: {result['mastery_status']} ✓")
    
    # Test 3: Get all accuracies
    print("\n✓ Querying all concept accuracies...")
    all_acc = ct.get_all_concepts_accuracy(session_id)
    print(f"  Total Concepts: {len(all_acc)}")
    for concept, data in all_acc.items():
        print(f"    • {concept}: {data['accuracy']*100:.0f}% ({data['mastery_status']})")
    
    # Test 4: Get recommendations
    print("\n✓ Getting concept recommendations...")
    recs = ct.get_concept_recommendations(session_id)
    print(f"  Focus On: {recs['focus_on']}")
    print(f"  Continue Practicing: {recs['continue_practicing']}")
    print(f"  Celebrate Mastery: {recs['celebrate_mastery']}")


def test_break_point_detection(session_id):
    """Test break point and misconception tracking."""
    print_header("TEST 4: Break Point Detection")
    
    bt = BreakPointTracker()
    
    # Test 1: Record break point (< 70%)
    print("\n✓ Recording break point (40% accuracy)...")
    bp = bt.record_break_point(
        session_id,
        concept="fractions",
        bloom_level="understand",
        accuracy=0.40,
        questions_attempted=5,
        questions_correct=2
    )
    
    assert bp is not None, "Should record break point"
    assert bp["severity"] == "high", "Should be high severity"
    print(f"  Concept: {bp['concept']}")
    print(f"  Accuracy: {bp['accuracy']*100:.0f}%")
    print(f"  Severity: {bp['severity']} ✓")
    
    # Test 2: Record misconception
    print("\n✓ Recording misconception...")
    misc = bt.record_misconception(
        session_id,
        misconception_type="fraction_addition_error",
        concept="fractions",
        bloom_level="understand",
        details="Student adds numerators and denominators separately"
    )
    
    assert misc is not None, "Should record misconception"
    print(f"  Type: fraction_addition_error")
    print(f"  Concept: {misc['concept']}")
    print(f"  Count: {misc['count']} ✓")
    
    # Test 3: Get remediation plan
    print("\n✓ Generating remediation plan...")
    plan = bt.get_remediation_plan(session_id)
    assert plan is not None, "Should generate plan"
    print(f"  Total Break Points: {plan['total_break_points']}")
    print(f"  Critical Issues: {plan['critical_break_points']}")
    print(f"  Concepts to Fix: {plan['critical_concepts']}")
    print(f"  Recommendations: {len(plan['recommendations'])} items")
    for i, rec in enumerate(plan['recommendations'][:2], 1):
        print(f"    {i}. {rec}")


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  PRACTICE ENGINE - IMPLEMENTATION VERIFICATION TEST".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Test all systems
        session_id = test_session_management()
        test_bloom_level_progression(session_id)
        test_concept_mastery(session_id)
        test_break_point_detection(session_id)
        
        # Final summary
        print_header("FINAL SUMMARY")
        print("\n✅ All tests passed successfully!")
        print("\nImplementation Status:")
        print("  ✓ Session Management: WORKING")
        print("  ✓ Bloom Level Progression: WORKING")
        print("  ✓ Concept Mastery Tracking: WORKING")
        print("  ✓ Break Point Detection: WORKING")
        print("\n🎉 Phase 1 Implementation Complete and Verified!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
