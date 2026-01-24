"""
Test for two-phase constraint validation.

Tests the fix for constraints on computed variables like "n1 < 300".
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from domain.template_engine.question_generator import question_generator


def test_hcf_remainder_template():
    """Test the HCF with remainder template that was failing."""
    
    template = {
        "name": "Largest Divisor (Sensible Limits)",
        "concept_id": "math.class5.hcf_remainder_sensible",
        "question_type": "MCQ",
        "question_pattern": "Find the largest number which divides {{n1}} and {{n2}} leaving remainders {{r1}} and {{r2}} respectively.",
        "variables": {
            "base": {
                "ans_hcf": { "type": "integer", "min": 12, "max": 25 },
                "factor_a": { "type": "integer", "min": 3, "max": 6 },
                "factor_b": { "type": "integer", "min": 4, "max": 8 },
                "r1": { "type": "integer", "min": 2, "max": 9 },
                "r2": { "type": "integer", "min": 2, "max": 9 }
            },
            "computed": {
                "n1": { "formula": "(ans_hcf * factor_a) + r1" },
                "n2": { "formula": "(ans_hcf * factor_b) + r2" },
                "diff1": { "formula": "n1 - r1" },
                "diff2": { "formula": "n2 - r2" },
                "wrong_add": { "formula": "ans_hcf + r1" }
            },
            "constraints": [
                "factor_a != factor_b",
                "r1 < ans_hcf",
                "r2 < ans_hcf",
                "r1 != r2",
                "n1 < 300",   # This constraint is on computed variable!
                "n2 < 300"    # This constraint is on computed variable!
            ]
        },
        "options": [
            { "pattern": "{{ans_hcf}}", "is_correct": True },
            { "pattern": "{{ans_hcf - 1}}", "is_correct": False },
            { "pattern": "{{wrong_add}}", "is_correct": False },
            { "pattern": "{{ans_hcf + 2}}", "is_correct": False }
        ],
        "difficulty": 3,
        "solution": {
            "steps": [
                { "number": 1, "text": "Subtract remainders: {{n1}} - {{r1}} = {{diff1}} and {{n2}} - {{r2}} = {{diff2}}" },
                { "number": 2, "text": "Find HCF of {{diff1}} and {{diff2}}" },
                { "number": 3, "text": "Answer is {{ans_hcf}}" }
            ]
        },
        "tags": ["hcf", "olympiad", "class5"]
    }
    
    print("=" * 60)
    print("Testing HCF with Remainder template")
    print("=" * 60)
    
    # Generate 5 questions
    results = question_generator.generate_batch(template, count=5)
    
    success_count = 0
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Question {i} ---")
        
        if not result.success:
            print(f"FAILED: {result.error}")
            continue
        
        success_count += 1
        q = result.question
        vars = result.variables
        
        print(f"Question: {q['question_text']}")
        print(f"Variables: n1={vars['n1']}, n2={vars['n2']}, r1={vars['r1']}, r2={vars['r2']}")
        print(f"Answer: {vars['ans_hcf']}")
        
        # Verify constraints are satisfied
        assert vars['n1'] < 300, f"n1={vars['n1']} should be < 300"
        assert vars['n2'] < 300, f"n2={vars['n2']} should be < 300"
        assert vars['r1'] < vars['ans_hcf'], f"r1={vars['r1']} should be < ans_hcf={vars['ans_hcf']}"
        assert vars['r2'] < vars['ans_hcf'], f"r2={vars['r2']} should be < ans_hcf={vars['ans_hcf']}"
        assert vars['factor_a'] != vars['factor_b'], "factor_a should != factor_b"
        assert vars['r1'] != vars['r2'], "r1 should != r2"
        
        print("✓ All constraints satisfied!")
        
        # Show options
        print("Options:")
        for opt in q['options']:
            mark = "✓" if opt['is_correct'] else " "
            print(f"  [{mark}] {opt['text']}")
    
    print(f"\n{'=' * 60}")
    print(f"Results: {success_count}/{len(results)} questions generated successfully")
    print(f"{'=' * 60}")
    
    return success_count == len(results)


def test_constraint_categorization():
    """Test that constraints are properly categorized."""
    from domain.template_engine.constraint_validator import constraint_validator
    
    constraints = [
        "factor_a != factor_b",  # base only
        "r1 < ans_hcf",          # base only
        "n1 < 300",              # uses computed (n1)
        "n1 != n2",              # uses computed (both)
        "gcd(a, b) > 1",         # base only (with function)
    ]
    
    base_vars = {"factor_a", "factor_b", "r1", "r2", "ans_hcf", "a", "b"}
    computed_vars = {"n1", "n2", "diff1", "diff2"}
    
    base_only, computed = constraint_validator.categorize_constraints(
        constraints, base_vars, computed_vars
    )
    
    print("\n--- Constraint Categorization Test ---")
    print(f"Base-only constraints: {base_only}")
    print(f"Computed constraints: {computed}")
    
    assert "factor_a != factor_b" in base_only
    assert "r1 < ans_hcf" in base_only
    assert "gcd(a, b) > 1" in base_only
    assert "n1 < 300" in computed
    assert "n1 != n2" in computed
    
    print("✓ Constraint categorization correct!")
    return True


def test_available_functions():
    """Test that all expected functions are available."""
    from domain.template_engine.safe_functions import safe_functions
    
    print("\n--- Available Functions Test ---")
    
    functions = safe_functions.list_functions()
    print(f"Total functions available: {len(functions)}")
    
    # Check for key functions
    required = ['gcd', 'lcm', 'factors', 'is_prime', 'sqrt', 'abs', 'min', 'max']
    for func in required:
        assert func in functions, f"Missing required function: {func}"
        print(f"  ✓ {func}")
    
    # Check geometry functions
    geometry = ['area_circle', 'volume_cylinder', 'perimeter_rectangle']
    for func in geometry:
        assert func in functions, f"Missing geometry function: {func}"
        print(f"  ✓ {func}")
    
    print("✓ All required functions available!")
    
    # Show by category
    categories = safe_functions.list_by_category()
    print("\nFunctions by category:")
    for cat, funcs in categories.items():
        print(f"  {cat}: {len(funcs)} functions")
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING TWO-PHASE CONSTRAINT VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Constraint Categorization", test_constraint_categorization),
        ("Available Functions", test_available_functions),
        ("HCF with Remainder Template", test_hcf_remainder_template),
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {name}: PASSED")
            else:
                print(f"\n✗ {name}: FAILED")
        except Exception as e:
            print(f"\n✗ {name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print(f"FINAL: {passed}/{len(tests)} tests passed")
    print(f"{'=' * 60}")
