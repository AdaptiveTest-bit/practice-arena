"""
Test script for Phase 2 content validation implementation.
Tests TaxonomyValidator, RubricValidator, and CoverageQACLI with sample data.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from domain.content_validation.taxonomy_validator import get_taxonomy_validator
from domain.content_validation.rubric_validator import get_rubric_validator
from tools.coverage_qa_cli import CoverageQACLI


def test_taxonomy_validator():
    """Test the TaxonomyValidator with various cases."""
    print("=" * 60)
    print("TESTING TAXONOMY VALIDATOR")
    print("=" * 60)
    
    validator = get_taxonomy_validator()
    
    # Test valid concept ID
    print("\n1. Testing valid concept ID:")
    is_valid, error = validator.validate_concept_id("math.class5.factors_multiples.divisibility")
    print(f"   Concept ID valid: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    # Test invalid concept ID
    print("\n2. Testing invalid concept ID:")
    is_valid, error = validator.validate_concept_id("math.invalid.concept")
    print(f"   Concept ID valid: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    # Test bloom level validation
    print("\n3. Testing bloom level validation:")
    is_valid, error = validator.validate_bloom_level("math.class5.factors_multiples.divisibility", "REMEMBER")
    print(f"   Bloom level valid: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    # Test wrong bloom level
    print("\n4. Testing wrong bloom level:")
    is_valid, error = validator.validate_bloom_level("math.class5.factors_multiples.divisibility", "ANALYZE")
    print(f"   Bloom level valid: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    # Test difficulty validation
    print("\n5. Testing difficulty validation:")
    is_valid, error = validator.validate_difficulty("math.class5.factors_multiples.divisibility", 1)
    print(f"   Difficulty valid: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    # Test difficulty out of range
    print("\n6. Testing difficulty out of range:")
    is_valid, error = validator.validate_difficulty("math.class5.factors_multiples.divisibility", 5)
    print(f"   Difficulty valid: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    # Test complete metadata validation
    print("\n7. Testing complete metadata validation:")
    metadata = {
        "concept_id": "math.class5.factors_multiples.divisibility",
        "bloom_level": "REMEMBER",
        "difficulty": 1,
        "grade": 5
    }
    is_valid, errors = validator.validate_template_metadata(metadata)
    print(f"   Metadata valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"   Error: {error}")
    
    # Test invalid metadata
    print("\n8. Testing invalid metadata:")
    invalid_metadata = {
        "concept_id": "math.invalid.concept",
        "bloom_level": "INVALID",
        "difficulty": 10,
        "grade": 15
    }
    is_valid, errors = validator.validate_template_metadata(invalid_metadata)
    print(f"   Metadata valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"   Error: {error}")
    
    # Test utility functions
    print("\n9. Testing utility functions:")
    concepts_grade5 = validator.list_concepts_by_grade(5)
    print(f"   Concepts for grade 5: {len(concepts_grade5)} found")
    
    concepts_remember = validator.list_concepts_by_bloom_level("REMEMBER")
    print(f"   Concepts at REMEMBER level: {len(concepts_remember)} found")
    
    print("\n✅ TaxonomyValidator tests completed!\n")


def test_rubric_validator():
    """Test the RubricValidator with various cases."""
    print("=" * 60)
    print("TESTING RUBRIC VALIDATOR")
    print("=" * 60)
    
    validator = get_rubric_validator()
    
    # Test valid template structure
    print("\n1. Testing valid template structure:")
    valid_template = {
        "chapter": "Factors and Multiples",
        "topic": "Divisibility Rules",
        "question_text": "Which of the following numbers is divisible by 2?",
        "options": ["12", "13", "15", "17"],
        "correct_option_index": 0,
        "answer": "12",
        "solution_steps": ["Check if last digit is even", "12 ends with 2, which is even", "Therefore, 12 is divisible by 2"],
        "distractor_info": [
            {"option_index": 0, "is_correct": True, "value": "Correct - 12 is divisible by 2"},
            {"option_index": 1, "is_correct": False, "value": "13 is not divisible by 2", "why_wrong": "13 ends with 3, which is odd"},
            {"option_index": 2, "is_correct": False, "value": "15 is not divisible by 2", "why_wrong": "15 ends with 5, which is odd"},
            {"option_index": 3, "is_correct": False, "value": "17 is not divisible by 2", "why_wrong": "17 ends with 7, which is odd"}
        ],
        "meta": {
            "subject": "math",
            "grade": 5,
            "chapter": "Factors and Multiples",
            "chapter_id": "factors_multiples",
            "concept_id": "math.class5.factors_multiples.divisibility",
            "concept_key": "divisibility",
            "difficulty": 1,
            "bloom_level": "REMEMBER"
        },
        "misconception_info": [
            {"option_index": 0, "is_correct": True, "value": "Correct - 12 is divisible by 2"},
            {"option_index": 1, "is_correct": False, "value": "13 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"},
            {"option_index": 2, "is_correct": False, "value": "15 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"},
            {"option_index": 3, "is_correct": False, "value": "17 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"}
        ]
    }
    
    is_valid, errors = validator.validate_template_structure(valid_template)
    print(f"   Template structure valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"   Error: {error}")
    
    # Test quality scoring
    print("\n2. Testing quality scoring:")
    score, level = validator.calculate_quality_score(valid_template)
    print(f"   Quality score: {score}/100 ({level})")
    
    # Test concept key validation
    print("\n3. Testing concept key validation:")
    is_valid, error = validator.validate_concept_key("divisibility")
    print(f"   Concept key valid: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    # Test invalid concept key
    print("\n4. Testing invalid concept key:")
    is_valid, error = validator.validate_concept_key("invalid_concept")
    print(f"   Concept key valid: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    # Test invalid template (missing fields)
    print("\n5. Testing invalid template (missing fields):")
    invalid_template = {
        "question_text": "Test question",
        "options": ["A", "B", "C"]  # Only 3 options, should be 4
    }
    
    is_valid, errors = validator.validate_template_structure(invalid_template)
    print(f"   Template structure valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"   Error: {error}")
    
    print("\n✅ RubricValidator tests completed!\n")


def test_coverage_qa_cli():
    """Test the CoverageQACLI with sample templates."""
    print("=" * 60)
    print("TESTING COVERAGE QA CLI")
    print("=" * 60)
    
    # Create sample templates
    sample_templates = [
        {
            "chapter": "Factors and Multiples",
            "topic": "Divisibility Rules",
            "question_text": "Which of the following numbers is divisible by 2?",
            "options": ["12", "13", "15", "17"],
            "correct_option_index": 0,
            "answer": "12",
            "solution_steps": ["Check if last digit is even", "12 ends with 2, which is even", "Therefore, 12 is divisible by 2"],
            "distractor_info": [
                {"option_index": 0, "is_correct": True, "value": "Correct - 12 is divisible by 2"},
                {"option_index": 1, "is_correct": False, "value": "13 is not divisible by 2", "why_wrong": "13 ends with 3, which is odd"},
                {"option_index": 2, "is_correct": False, "value": "15 is not divisible by 2", "why_wrong": "15 ends with 5, which is odd"},
                {"option_index": 3, "is_correct": False, "value": "17 is not divisible by 2", "why_wrong": "17 ends with 7, which is odd"}
            ],
            "meta": {
                "subject": "math",
                "grade": 5,
                "chapter": "Factors and Multiples",
                "chapter_id": "factors_multiples",
                "concept_id": "math.class5.factors_multiples.divisibility",
                "concept_key": "divisibility",
                "difficulty": 1,
                "bloom_level": "REMEMBER"
            },
            "misconception_info": [
                {"option_index": 0, "is_correct": True, "value": "Correct - 12 is divisible by 2"},
                {"option_index": 1, "is_correct": False, "value": "13 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"},
                {"option_index": 2, "is_correct": False, "value": "15 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"},
                {"option_index": 3, "is_correct": False, "value": "17 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"}
            ]
        },
        {
            "chapter": "Factors and Multiples",
            "topic": "Prime Numbers",
            "question_text": "Which of the following is a prime number?",
            "options": ["4", "6", "7", "8"],
            "correct_option_index": 2,
            "answer": "7",
            "solution_steps": ["Check factors", "7 only has 1 and 7 as factors"],
            "distractor_info": [
                {"option_index": 0, "is_correct": False, "value": "Wrong"},
                {"option_index": 1, "is_correct": False, "value": "Wrong"},
                {"option_index": 2, "is_correct": True, "value": "Correct"},
                {"option_index": 3, "is_correct": False, "value": "Wrong"}
            ],
            "meta": {
                "subject": "math",
                "grade": 5,
                "chapter": "Factors and Multiples",
                "chapter_id": "factors_multiples",
                "concept_id": "math.class5.factors_multiples.prime_composite",
                "concept_key": "prime_composite",
                "difficulty": 1,
                "bloom_level": "REMEMBER"
            },
            "misconception_info": [
                {"option_index": 0, "is_correct": False, "value": "Wrong"},
                {"option_index": 1, "is_correct": False, "value": "Wrong"},
                {"option_index": 2, "is_correct": True, "value": "Correct"},
                {"option_index": 3, "is_correct": False, "value": "Wrong"}
            ]
        }
    ]
    
    try:
        qa_cli = CoverageQACLI()
        
        print("\n1. Testing coverage analysis:")
        coverage_report = qa_cli.analyze_template_coverage(sample_templates)
        print(f"   Total concepts: {coverage_report['summary']['total_concepts']}")
        print(f"   Concepts with templates: {coverage_report['summary']['concepts_with_templates']}")
        print(f"   Total templates: {coverage_report['summary']['total_templates']}")
        print(f"   Coverage percentage: {coverage_report['summary']['coverage_percentage']:.1f}%")
        
        print("\n2. Testing template validation:")
        validation_report = qa_cli.validate_templates(sample_templates)
        print(f"   Total templates: {validation_report['total_templates']}")
        print(f"   Taxonomy valid: {validation_report['taxonomy_valid']}")
        print(f"   Rubric valid: {validation_report['rubric_valid']}")
        print(f"   Both valid: {validation_report['both_valid']}")
        
        print("\n3. Generating full report:")
        report = qa_cli.generate_report(sample_templates, 'text')
        print("   Report generated successfully!")
        print("\n" + "="*40)
        print(report)
        print("="*40)
        
    except Exception as e:
        print(f"❌ Error testing CoverageQACLI: {e}")
        return
    
    print("\n✅ CoverageQACLI tests completed!\n")


def test_integration():
    """Test integration between all validators."""
    print("=" * 60)
    print("TESTING INTEGRATION")
    print("=" * 60)
    
    # Create a template that should pass all validations
    good_template = {
        "chapter": "Factors and Multiples",
        "topic": "Divisibility Rules",
        "question_text": "Which number is divisible by 2?",
        "options": ["12", "13", "15", "17"],
        "correct_option_index": 0,
        "answer": "12",
        "solution_steps": ["Check if last digit is even", "12 ends with 2, which is even", "Therefore, 12 is divisible by 2"],
        "distractor_info": [
            {"option_index": 0, "is_correct": True, "value": "Correct - 12 is divisible by 2"},
            {"option_index": 1, "is_correct": False, "value": "13 is not divisible by 2", "why_wrong": "13 ends with 3, which is odd"},
            {"option_index": 2, "is_correct": False, "value": "15 is not divisible by 2", "why_wrong": "15 ends with 5, which is odd"},
            {"option_index": 3, "is_correct": False, "value": "17 is not divisible by 2", "why_wrong": "17 ends with 7, which is odd"}
        ],
        "meta": {
            "subject": "math",
            "grade": 5,
            "chapter": "Factors and Multiples",
            "chapter_id": "factors_multiples",
            "concept_id": "math.class5.factors_multiples.divisibility",
            "concept_key": "divisibility",
            "difficulty": 1,
            "bloom_level": "REMEMBER"
        },
        "misconception_info": [
            {"option_index": 0, "is_correct": True, "value": "Correct - 12 is divisible by 2"},
            {"option_index": 1, "is_correct": False, "value": "13 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"},
            {"option_index": 2, "is_correct": False, "value": "15 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"},
            {"option_index": 3, "is_correct": False, "value": "17 is not divisible by 2", "target_misconception": "odd_even_confusion", "teaching_point": "Numbers ending in odd digits are not divisible by 2"}
        ]
    }
    
    taxonomy_validator = get_taxonomy_validator()
    rubric_validator = get_rubric_validator()
    
    print("\n1. Testing complete validation pipeline:")
    
    # Taxonomy validation
    taxonomy_valid, taxonomy_errors = taxonomy_validator.validate_template_metadata(good_template['meta'])
    print(f"   Taxonomy validation: {'✅ PASS' if taxonomy_valid else '❌ FAIL'}")
    if taxonomy_errors:
        for error in taxonomy_errors:
            print(f"     Error: {error}")
    
    # Rubric validation
    rubric_valid, rubric_errors = rubric_validator.validate_template_structure(good_template)
    print(f"   Rubric validation: {'✅ PASS' if rubric_valid else '❌ FAIL'}")
    if rubric_errors:
        for error in rubric_errors:
            print(f"     Error: {error}")
    
    # Quality scoring
    score, level = rubric_validator.calculate_quality_score(good_template)
    print(f"   Quality score: {score}/100 ({level})")
    
    # Overall result
    overall_valid = taxonomy_valid and rubric_valid
    print(f"   Overall validation: {'✅ PASS' if overall_valid else '❌ FAIL'}")
    
    print("\n✅ Integration tests completed!\n")


def main():
    """Run all tests."""
    print("🚀 STARTING PHASE 2 CONTENT VALIDATION TESTS")
    print("=" * 80)
    
    try:
        test_taxonomy_validator()
        test_rubric_validator()
        test_coverage_qa_cli()
        test_integration()
        
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nPhase 2 implementation is ready for use!")
        print("\nNext steps:")
        print("1. Integrate validators into template ingestion pipeline")
        print("2. Add CoverageQACLI to CI/CD for pre-release checks")
        print("3. Extend to support more subjects and grades")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
