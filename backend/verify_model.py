#!/usr/bin/env python3
"""
Simple test to verify rich content fields exist in Question model
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Test 1: Check QuestionResponse model has the new fields
print("\n" + "="*70)
print("TEST: Verify QuestionResponse model has rich content fields")
print("="*70)

try:
    from models.question import QuestionResponse
    from pydantic import Field
    import inspect
    
    # Get all fields from QuestionResponse
    fields = QuestionResponse.model_fields
    
    print("\n✅ QuestionResponse fields:")
    for name, field in fields.items():
        if 'rich' in name.lower() or 'hint' in name.lower():
            print(f"   ✨ {name}: {field.annotation}")
    
    # Check specifically for our new fields
    expected_fields = ['richNarrative', 'richHtmlContent', 'visualHints']
    found_fields = []
    missing_fields = []
    
    for field_name in expected_fields:
        if field_name in fields:
            found_fields.append(field_name)
            print(f"\n✅ Found: {field_name}")
            field = fields[field_name]
            print(f"   Type: {field.annotation}")
            print(f"   Description: {field.description}")
        else:
            missing_fields.append(field_name)
            print(f"\n❌ Missing: {field_name}")
    
    # Summary
    print("\n" + "="*70)
    print(f"Summary: Found {len(found_fields)}/{len(expected_fields)} fields")
    
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
        sys.exit(1)
    else:
        print("✅ ALL RICH CONTENT FIELDS PRESENT IN API MODEL")
        print("\nThe backend is now ready to return rich content to the frontend!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("="*70 + "\n")
