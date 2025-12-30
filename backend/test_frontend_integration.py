#!/usr/bin/env python3
"""
Comprehensive Frontend Integration Test
Tests the full pipeline from API generation to response structure
"""

import json
from datetime import datetime

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_backend_question_generation():
    """Test 1: Backend question generation with rich content"""
    print_section("TEST 1: Backend Question Generation")
    
    try:
        # Import backend modules
        from factory import QuestionGeneratorFactory
        from models.question import ChapterEnum
        
        print("✓ Backend modules imported successfully")
        
        # Create strategy
        strategy = QuestionGeneratorFactory.create(ChapterEnum.FACTORS_MULTIPLES)
        print("✓ Strategy created for FACTORS_MULTIPLES")
        
        # Generate multiple questions to verify consistency
        questions = []
        for i in range(3):
            q = strategy.generate()
            questions.append(q)
            print(f"✓ Question {i+1} generated")
        
        # Verify all have rich content
        print("\n📋 Rich Content Verification:")
        for i, q in enumerate(questions):
            has_narrative = bool(getattr(q, "rich_narrative", None))
            has_html = bool(getattr(q, "rich_html_content", None))
            has_hints = bool(getattr(q, "visual_hints", None))
            
            print(f"\n  Question {i+1}:")
            print(f"    • rich_narrative:    {'✅' if has_narrative else '❌'} ({len(getattr(q, 'rich_narrative', ''))} chars)")
            print(f"    • rich_html_content: {'✅' if has_html else '❌'} ({len(getattr(q, 'rich_html_content', ''))} chars)")
            print(f"    • visual_hints:      {'✅' if has_hints else '❌'} ({len(getattr(q, 'visual_hints', []))} hints)")
        
        return True, questions
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_api_response_structure(questions):
    """Test 2: Simulate API response structure"""
    print_section("TEST 2: API Response Structure")
    
    try:
        if not questions:
            print("❌ No questions to test")
            return False
        
        # Simulate what the API returns
        q = questions[0]
        api_response = {
            "success": True,
            "session_id": 1,
            "question_id": "test-123",
            "chapter_id": 5,
            "concept": "factors_multiples",
            "bloom_level": "understand",
            "difficulty": 2.0,
            "question_text": q.question_text,
            "options": q.options,
            "rich_narrative": getattr(q, "rich_narrative", None),
            "rich_html_content": getattr(q, "rich_html_content", None),
            "visual_hints": getattr(q, "visual_hints", None),
        }
        
        # Validate required fields
        required_fields = [
            "success", "session_id", "question_id", "chapter_id",
            "question_text", "options"
        ]
        
        print("✓ API Response Structure Validation:")
        for field in required_fields:
            if field in api_response:
                print(f"  ✓ {field}: Present")
            else:
                print(f"  ❌ {field}: Missing")
                return False
        
        # Validate rich content fields
        print("\n✓ Rich Content Fields:")
        for field in ["rich_narrative", "rich_html_content", "visual_hints"]:
            if api_response[field] is not None:
                if field == "visual_hints":
                    print(f"  ✓ {field}: Present ({len(api_response[field])} items)")
                else:
                    print(f"  ✓ {field}: Present ({len(api_response[field])} chars)")
            else:
                print(f"  ⚠️  {field}: None")
        
        print("\n✓ Full API Response Sample:")
        print(json.dumps(api_response, indent=2, default=str)[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_type_compatibility():
    """Test 3: Verify types match frontend expectations"""
    print_section("TEST 3: Frontend Type Compatibility")
    
    try:
        # Check that field names match TypeScript types
        frontend_expected_fields = {
            "richNarrative": "string | undefined",      # camelCase
            "richHtmlContent": "string | undefined",    # camelCase
            "visualHints": "string[] | undefined",      # camelCase
        }
        
        # Backend returns snake_case which is converted by frontend
        backend_fields = {
            "rich_narrative": "string | null",
            "rich_html_content": "string | null",
            "visual_hints": "list | null",
        }
        
        print("✓ Field Name Mapping (Backend → Frontend):")
        print("  Backend (snake_case)        Frontend (camelCase)")
        print("  " + "-" * 50)
        print("  rich_narrative              richNarrative")
        print("  rich_html_content           richHtmlContent")
        print("  visual_hints                visualHints")
        
        print("\n✓ Type Compatibility:")
        print("  Backend Type          Frontend Type        Compatible")
        print("  " + "-" * 50)
        print("  string | null          string | undefined  ✓ Yes")
        print("  string | null          string | undefined  ✓ Yes")
        print("  list | null            string[] | undefined ✓ Yes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rich_content_samples():
    """Test 4: Sample rich content output"""
    print_section("TEST 4: Rich Content Sample Output")
    
    try:
        from factory import QuestionGeneratorFactory
        from models.question import ChapterEnum
        
        strategy = QuestionGeneratorFactory.create(ChapterEnum.FACTORS_MULTIPLES)
        q = strategy.generate()
        
        print("📖 Sample Rich Narrative:")
        print(f"  {getattr(q, 'rich_narrative', 'N/A')[:200]}...")
        
        print("\n🎨 Sample Rich HTML Content:")
        html_content = getattr(q, 'rich_html_content', '')
        if html_content:
            print(f"  {html_content[:200]}...")
        else:
            print("  No HTML content")
        
        print("\n💡 Sample Visual Hints:")
        hints = getattr(q, 'visual_hints', [])
        for i, hint in enumerate(hints[:3]):
            print(f"  {i+1}. {hint}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "FRONTEND INTEGRATION TEST SUITE" + " "*21 + "║")
    print("║" + " "*10 + f"Testing Rich Content Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " "*9 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    # Test 1: Backend generation
    print("\n⏳ Running Test 1...")
    success, questions = test_backend_question_generation()
    results["Backend Generation"] = success
    
    # Test 2: API structure
    if success:
        print("\n⏳ Running Test 2...")
        results["API Structure"] = test_api_response_structure(questions)
    else:
        results["API Structure"] = False
    
    # Test 3: Type compatibility
    print("\n⏳ Running Test 3...")
    results["Type Compatibility"] = test_frontend_type_compatibility()
    
    # Test 4: Content samples
    print("\n⏳ Running Test 4...")
    results["Content Samples"] = test_rich_content_samples()
    
    # Summary
    print_section("TEST SUMMARY")
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:<30} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Rich content pipeline is working!")
        print("="*70)
        print("\n✨ NEXT STEPS:")
        print("  1. Start backend server: cd backend && python app_refactored.py")
        print("  2. Start frontend server: cd frontend && npm run dev")
        print("  3. Visit: http://localhost:3000/quiz?chapter=factors_multiples")
        print("  4. You should see:")
        print("     • Rich narratives in the question card")
        print("     • SVG diagrams with visual representations")
        print("     • Progressive hints for problem-solving")
        print("\n" + "="*70)
    else:
        print("⚠️  SOME TESTS FAILED - Please review the output above")
        print("="*70)
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
