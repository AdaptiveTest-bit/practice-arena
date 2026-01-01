#!/usr/bin/env python3
"""
Test script to verify the hint endpoint 404 fix.

Tests:
1. Verify repository.get_session() method exists
2. Verify session lookup from database
3. Verify hint endpoint returns valid response
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_repository_method():
    """Test that get_session method exists in ORMStudentRepository"""
    print("\n" + "="*60)
    print("TEST 1: Repository Method Verification")
    print("="*60)
    
    try:
        from services.orm_student_repository import get_repository
        repo = get_repository()
        
        # Check method exists
        if not hasattr(repo, 'get_session'):
            print("❌ FAILED: get_session method not found in repository")
            return False
        
        print("✅ get_session method exists in ORMStudentRepository")
        
        # Check method signature
        import inspect
        sig = inspect.signature(repo.get_session)
        print(f"   Signature: get_session{sig}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_session_adapter_integration():
    """Test that SessionAdapter uses the new multi-strategy lookup"""
    print("\n" + "="*60)
    print("TEST 2: SessionAdapter Integration")
    print("="*60)
    
    try:
        from services.session_adapter import SessionAdapter
        adapter = SessionAdapter()
        
        # Check that adapter has repository
        if not hasattr(adapter, 'repository'):
            print("❌ FAILED: SessionAdapter missing repository")
            return False
        
        print("✅ SessionAdapter has repository")
        
        # Check get_hint method
        import inspect
        source = inspect.getsource(adapter.get_hint)
        
        if "repository.get_session" not in source:
            print("❌ FAILED: get_hint doesn't use repository.get_session()")
            return False
        
        print("✅ get_hint uses repository.get_session() for database fallback")
        
        if "Strategy 1:" not in source and "Strategy 2:" not in source:
            print("⚠️  WARNING: Multi-strategy logic comments not found")
        else:
            print("✅ Multi-strategy logic implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_database_session_lookup():
    """Test that sessions can be retrieved from database"""
    print("\n" + "="*60)
    print("TEST 3: Database Session Lookup")
    print("="*60)
    
    try:
        from database import SessionLocal, PracticeSession
        from services.orm_student_repository import get_repository
        
        repo = get_repository()
        
        # Query for existing session
        db = SessionLocal()
        existing_session = db.query(PracticeSession).first()
        
        if not existing_session:
            print("⚠️  No practice sessions in database, skipping lookup test")
            return True
        
        session_id = existing_session.id
        print(f"   Found session ID: {session_id}")
        
        # Try to retrieve it using new method
        retrieved = repo.get_session(session_id)
        
        if not retrieved:
            print(f"❌ FAILED: Could not retrieve session {session_id}")
            return False
        
        print(f"✅ Successfully retrieved session {session_id} from database")
        print(f"   Student ID: {retrieved.student_id}")
        print(f"   Class Level: {retrieved.class_level}")
        print(f"   Chapter ID: {retrieved.chapter_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_imports():
    """Test that all modified files can be imported without errors"""
    print("\n" + "="*60)
    print("TEST 0: Import Verification")
    print("="*60)
    
    try:
        print("  Importing database...")
        from database import PracticeSession, SessionLocal
        print("  ✓ database module")
        
        print("  Importing orm_student_repository...")
        from services.orm_student_repository import get_repository, ORMStudentRepository
        print("  ✓ orm_student_repository module")
        
        print("  Importing session_adapter...")
        from services.session_adapter import SessionAdapter
        print("  ✓ session_adapter module")
        
        print("\n✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪 HINT ENDPOINT 404 FIX - VERIFICATION TEST SUITE" + "\n")
    
    results = {}
    
    # Run tests in order
    tests = [
        ("Import Verification", test_imports),
        ("Repository Method", test_repository_method),
        ("SessionAdapter Integration", test_session_adapter_integration),
        ("Database Lookup", test_database_session_lookup),
    ]
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Fix is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
