#!/usr/bin/env python3
"""
Test script to verify rich content is returned by the API.
"""

import sys
sys.path.insert(0, '.')

from services.question_service import QuestionService
from models.question import ChapterEnum
import json

def test_rich_content():
    """Test that rich content is properly populated and returned."""
    
    print("=" * 70)
    print("TESTING RICH CONTENT IN QUESTION SERVICE")
    print("=" * 70)
    
    # Create question service
    qs = QuestionService()
    
    # Create a session properly
    session_id = qs._dedup_service.create_session()
    
    # Generate 5 questions and check for rich content
    print(f"\nGenerating 5 questions from FACTORS_MULTIPLES chapter...")
    
    for i in range(1, 6):
        print(f"\n--- Question {i} ---")
        try:
            question, question_id = qs.generate_question(session_id, ChapterEnum.FACTORS_MULTIPLES)
            
            # Check rich content fields
            rich_narrative = getattr(question, 'rich_narrative', None)
            rich_html = getattr(question, 'rich_html_content', None)
            visual_hints = getattr(question, 'visual_hints', None)
            
            print(f"Question ID: {question_id}")
            print(f"Question Text: {question.question_text[:80]}...")
            print(f"\n📖 rich_narrative:")
            if rich_narrative:
                print(f"   ✓ Present ({len(rich_narrative)} chars)")
                print(f"   Preview: {rich_narrative[:100]}...")
            else:
                print(f"   ✗ MISSING")
            
            print(f"\n🎨 rich_html_content:")
            if rich_html:
                print(f"   ✓ Present ({len(rich_html)} chars)")
                if '<svg' in rich_html:
                    print(f"   ✓ Contains SVG diagram")
                else:
                    print(f"   Preview: {rich_html[:100]}...")
            else:
                print(f"   ✗ MISSING")
            
            print(f"\n💡 visual_hints:")
            if visual_hints:
                print(f"   ✓ Present ({len(visual_hints)} hints)")
                for j, hint in enumerate(visual_hints[:3], 1):
                    print(f"   Hint {j}: {hint[:60]}...")
            else:
                print(f"   ✗ MISSING")
            
            # Check if it's from bank or dynamic
            source = "BANK" if "bank" in question.topic.lower() or len(visual_hints or []) <= 2 else "DYNAMIC"
            print(f"\n📌 Source: {source} question")
            
        except Exception as e:
            print(f"✗ Error generating question: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_rich_content()
