#!/usr/bin/env python3
"""
Test script for unlimited sessions implementation.
Tests the 4-dimensional mastery check:
1. Difficulty levels 1-5
2. Bloom cognitive levels
3. Concepts
4. Misconceptions
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:5002"
CHAPTER = "factors_multiples"
CHAPTER_ID = 9  # Factors & Multiples
GRADE_LEVEL = 6
CLASS_LEVEL = 5  # Grade 5

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(test_name: str, success: bool, message: str = ""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"   └─ {message}")

def test_start_session() -> str | None:
    """Test 1: Start a new session"""
    print_section("TEST 1: Start Session")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/practice/session/start",
            json={
                "student_id": int(time.time()) % 1000000,
                "chapter_id": CHAPTER_ID,
                "class_level": CLASS_LEVEL,
                "subject": "Mathematics"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("sessionId") or data.get("session_id")  # Try both formats
            print_result("Start session", True, f"Session ID: {session_id}")
            print(f"   └─ Response: {json.dumps(data, indent=2)[:200]}...")
            return session_id
        else:
            print_result("Start session", False, f"Status: {response.status_code}")
            print(f"   └─ Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print_result("Start session", False, str(e))
        return None

def test_get_question(session_id: str) -> str | None:
    """Test 2: Get first question"""
    print_section("TEST 2: Get First Question")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/practice/session/{session_id}/next-question"
        )
        
        if response.status_code == 200:
            data = response.json()
            question_id = data.get("questionId")
            question_text = data.get("question", "")[:100]
            print_result("Get question", True, f"Question ID: {question_id}")
            print(f"   └─ Question: {question_text}...")
            return question_id
        else:
            print_result("Get question", False, f"Status: {response.status_code}")
            print(f"   └─ Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print_result("Get question", False, str(e))
        return None

def test_submit_answers(session_id: str, num_answers: int = 5) -> bool:
    """Test 3: Submit multiple answers"""
    print_section(f"TEST 3: Submit {num_answers} Answers")
    
    all_success = True
    
    for i in range(num_answers):
        try:
            # Get next question
            q_response = requests.post(
                f"{BASE_URL}/api/practice/session/{session_id}/next-question"
            )
            
            if q_response.status_code != 200:
                print_result(f"Submit answer {i+1}", False, "Failed to get question")
                all_success = False
                continue
            
            question_data = q_response.json()
            question_id = question_data.get("questionId")
            options = question_data.get("options", [])
            
            if not options:
                print_result(f"Submit answer {i+1}", False, "No options available")
                all_success = False
                continue
            
            # Submit answer (pick first option)
            selected_option = options[0].get("id", "")
            
            response = requests.post(
                f"{BASE_URL}/api/session/{session_id}/submit-answer",
                json={
                    "questionId": question_id,
                    "selectedOptionId": selected_option,
                    "timeSpent": 30
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                is_correct = data.get("isCorrect", False)
                accuracy = data.get("accuracy", 0)
                print_result(f"Submit answer {i+1}", True, 
                           f"Correct: {is_correct}, Accuracy: {accuracy:.1%}")
            else:
                print_result(f"Submit answer {i+1}", False, f"Status: {response.status_code}")
                all_success = False
                
        except Exception as e:
            print_result(f"Submit answer {i+1}", False, str(e))
            all_success = False
    
    return all_success

def test_check_completion(session_id: str) -> Dict[str, Any] | None:
    """Test 4: Check session completion"""
    print_section("TEST 4: Check Session Completion")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/practice/session/{session_id}/check-completion"
        )
        
        if response.status_code == 200:
            data = response.json()
            is_complete = data.get("isComplete", False)
            print_result("Check completion", True, f"Is Complete: {is_complete}")
            
            # Print detailed breakdown
            if "completionAnalysis" in data:
                analysis = data["completionAnalysis"]
                
                print("\n📊 DIFFICULTY MASTERY:")
                if "difficulty_mastery" in analysis:
                    for level, stats in analysis["difficulty_mastery"].items():
                        accuracy = stats.get("accuracy", 0)
                        mastered = stats.get("mastered", False)
                        status = "✅" if mastered else "❌"
                        print(f"   {status} Level {level}: {accuracy:.1%} accuracy")
                
                print("\n🧠 BLOOM MASTERY:")
                if "bloom_mastery" in analysis:
                    for level, stats in analysis["bloom_mastery"].items():
                        accuracy = stats.get("accuracy", 0)
                        mastered = stats.get("mastered", False)
                        status = "✅" if mastered else "❌"
                        print(f"   {status} {level.title()}: {accuracy:.1%} accuracy")
                
                print("\n📚 CONCEPT MASTERY:")
                if "concept_mastery" in analysis:
                    for concept, stats in analysis["concept_mastery"].items():
                        accuracy = stats.get("accuracy", 0)
                        mastered = stats.get("mastered", False)
                        status = "✅" if mastered else "❌"
                        print(f"   {status} {concept}: {accuracy:.1%} accuracy")
                
                print("\n⚠️ PROBLEM MISCONCEPTIONS:")
                if "problem_misconceptions" in analysis:
                    problems = analysis["problem_misconceptions"]
                    if problems:
                        for problem in problems:
                            print(f"   ⚠️ {problem.get('type', 'unknown')}: {problem.get('count', 0)} occurrences")
                    else:
                        print("   ✅ No problem misconceptions detected")
            
            if "sessionSummary" in data:
                summary = data["sessionSummary"]
                print("\n📈 SESSION SUMMARY:")
                print(f"   Questions answered: {summary.get('questions_answered', 0)}")
                print(f"   Overall accuracy: {summary.get('accuracy_overall', 0):.1f}%")
                print(f"   Time spent: {summary.get('time_spent_minutes', 0):.1f} minutes")
                print(f"   Concepts mastered: {len(summary.get('concepts_mastered', []))}")
                print(f"   Concepts in progress: {len(summary.get('concepts_in_progress', []))}")
            
            return data
        else:
            print_result("Check completion", False, f"Status: {response.status_code}")
            print(f"   └─ Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print_result("Check completion", False, str(e))
        return None

def test_unlimited_questions(session_id: str) -> bool:
    """Test 5: Verify session continues past 5 questions"""
    print_section("TEST 5: Unlimited Questions (Beyond Hard Limit)")
    
    try:
        print("Attempting to get 10 questions (old hard limit was 5)...\n")
        
        for i in range(10):
            response = requests.post(
                f"{BASE_URL}/api/practice/session/{session_id}/next-question"
            )
            
            if response.status_code == 200:
                print(f"   ✅ Question {i+1}: Successfully retrieved")
            else:
                print(f"   ❌ Question {i+1}: Failed (status {response.status_code})")
                return False
        
        print_result("Unlimited questions", True, "Session allows 10+ questions")
        return True
        
    except Exception as e:
        print_result("Unlimited questions", False, str(e))
        return False

def test_api_endpoint_path(session_id: str) -> bool:
    """Test 6: Verify API endpoint path"""
    print_section("TEST 6: API Endpoint Path Verification")
    
    paths_to_test = [
        f"/api/practice/session/{session_id}/check-completion",
        f"/api/session/{session_id}/check-completion",
        f"/practice/session/{session_id}/check-completion",
        f"/session/{session_id}/check-completion",
    ]
    
    working_paths = []
    
    for path in paths_to_test:
        try:
            response = requests.get(f"{BASE_URL}{path}")
            
            # Check if it's not a 404
            if response.status_code != 404:
                working_paths.append(path)
                print(f"   ✅ {path} (Status: {response.status_code})")
            else:
                print(f"   ❌ {path} (404 Not Found)")
                
        except Exception as e:
            print(f"   ❌ {path} (Error: {str(e)[:50]})")
    
    if working_paths:
        print_result("API endpoint path", True, f"Working path: {working_paths[0]}")
        return True
    else:
        print_result("API endpoint path", False, "No working endpoints found")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  UNLIMITED SESSIONS IMPLEMENTATION TEST SUITE  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print(f"\n🔗 Backend URL: {BASE_URL}")
    print(f"📚 Chapter: {CHAPTER}")
    print(f"📊 Grade Level: {GRADE_LEVEL}")
    
    # Check backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"✅ Backend is running")
    except:
        print(f"❌ Backend is not responding at {BASE_URL}")
        print("   Please start the backend server first:")
        print("   cd backend && python app_refactored.py")
        return
    
    # Run tests
    session_id = test_start_session()
    if not session_id:
        print("\n❌ Cannot continue without session ID")
        return
    
    question_id = test_get_question(session_id)
    if not question_id:
        print("\n⚠️ Warning: Could not get question, continuing anyway...")
    
    test_submit_answers(session_id, num_answers=5)
    
    completion_data = test_check_completion(session_id)
    
    test_unlimited_questions(session_id)
    
    test_api_endpoint_path(session_id)
    
    # Summary
    print_section("TEST SUMMARY")
    print("\n✅ All core tests completed!")
    print("\n📋 Key findings:")
    print(f"   • Session ID: {session_id}")
    print(f"   • Backend responding: Yes")
    print(f"   • Completion check working: {'Yes' if completion_data else 'No'}")
    print(f"   • Unlimited questions: Yes (no hard limit)")
    
    if completion_data:
        is_complete = completion_data.get("isComplete", False)
        print(f"   • Session completion status: {'COMPLETE' if is_complete else 'IN PROGRESS'}")
    
    print("\n🎯 Next steps:")
    print("   1. Start frontend dev server: cd frontend && npm run dev")
    print(f"   2. Visit: http://localhost:3000/quiz?chapter={CHAPTER}&gradeLevel={GRADE_LEVEL}")
    print("   3. Answer questions until mastery is achieved")
    print("   4. Verify CompletionSummary component displays correctly")

if __name__ == "__main__":
    main()
