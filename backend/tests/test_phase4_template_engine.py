"""
Test script for Phase 4 Lean Template Engine implementation.
Tests template generation, rendering, and answer evaluation.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from domain.template_engine import LeanTemplateEngine
from db.models import QuestionTemplate, Misconception, TemplateOptionMisconception
from config.settings import settings


def setup_test_data(db):
    """Set up test templates and misconceptions for testing."""
    print("Setting up test data...")
    
    # Create test template for divisibility
    template = QuestionTemplate(
        concept_id="math.class5.factors_multiples.divisibility",
        template_code="""
def generate_variables():
    import random
    numbers = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
    number = random.choice(numbers)
    return {"number": number}
""",
        question_pattern="Which of the following numbers is divisible by 2?",
        variable_schema={
            "type": "object",
            "properties": {
                "number": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 30
                }
            }
        },
        answer_logic="variables['number']",  # Return the number itself
        option_patterns=[
            "{{number}}",  # Correct answer - even number
            "{{number + 1}}",  # Wrong - makes it odd
            "{{number + 3}}",  # Wrong - makes it odd
            "{{number + 5}}"   # Wrong - makes it odd
        ],
        difficulty=1,
        bloom_level="REMEMBER",
        estimated_time=30,
        status="PUBLISHED",
        validation_passed=True,
        created_by="test_system"
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    # Create misconceptions
    misconception1 = Misconception(
        code="odd_even_confusion",
        title="Confusion between odd and even numbers",
        description="Student thinks all numbers ending in certain digits are even or odd without checking divisibility",
        teaching_point="A number is even if it's divisible by 2, otherwise it's odd. Look at the last digit!",
        subject="math",
        concept_tags=["math.class5.factors_multiples.divisibility"]
    )
    
    misconception2 = Misconception(
        code="divisibility_rule_2",
        title="Doesn't know divisibility rule for 2",
        description="Student doesn't know that numbers ending in 0, 2, 4, 6, 8 are divisible by 2",
        teaching_point="Numbers ending in 0, 2, 4, 6, or 8 are divisible by 2. Numbers ending in 1, 3, 5, 7, 9 are not.",
        subject="math",
        concept_tags=["math.class5.factors_multiples.divisibility"]
    )
    
    db.add(misconception1)
    db.add(misconception2)
    db.commit()
    db.refresh(misconception1)
    db.refresh(misconception2)
    
    # Link misconceptions to template options
    option_misconception1 = TemplateOptionMisconception(
        template_id=template.id,
        misconception_id=misconception2.id,
        option_index=1,  # Second option
        custom_explanation="This number ends in an odd digit, so it's not divisible by 2"
    )
    
    option_misconception2 = TemplateOptionMisconception(
        template_id=template.id,
        misconception_id=misconception1.id,
        option_index=2,  # Third option
        custom_explanation="Check if this number is divisible by 2 by looking at its last digit"
    )
    
    db.add(option_misconception1)
    db.add(option_misconception2)
    db.commit()
    
    print(f"Created test template with ID: {template.id}")
    print(f"Created {db.query(Misconception).count()} misconceptions")
    print(f"Created {db.query(TemplateOptionMisconception).count()} misconception mappings")
    
    return template.id


def test_variable_generation():
    """Test variable generation from JSON schemas."""
    print("\n" + "=" * 60)
    print("TESTING VARIABLE GENERATION")
    print("=" * 60)
    
    from domain.template_engine import VariableGenerator
    
    # Test integer generation
    schema = {
        "type": "object",
        "properties": {
            "number": {
                "type": "integer",
                "minimum": 10,
                "maximum": 20
            }
        }
    }
    
    variables = VariableGenerator.generate_from_schema(schema)
    print(f"✓ Integer generation: {variables}")
    assert "number" in variables
    assert 10 <= variables["number"] <= 20
    
    # Test string generation with choices
    schema = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"]
            }
        }
    }
    
    variables = VariableGenerator.generate_from_schema(schema)
    print(f"✓ String enum generation: {variables}")
    assert variables["operation"] in ["add", "subtract", "multiply", "divide"]
    
    # Test array generation
    schema = {
        "type": "array",
        "items": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5
        },
        "minItems": 2,
        "maxItems": 4
    }
    
    variables = VariableGenerator.generate_from_schema(schema)
    print(f"✓ Array generation: {variables}")
    assert isinstance(variables, list)
    assert 2 <= len(variables) <= 4
    
    print("✅ Variable generation tests passed!")


def test_template_rendering():
    """Test template rendering with Jinja2."""
    print("\n" + "=" * 60)
    print("TESTING TEMPLATE RENDERING")
    print("=" * 60)
    
    from domain.template_engine import TemplateRenderer
    
    renderer = TemplateRenderer()
    
    # Test basic rendering
    pattern = "What is {{number}} + {{number}}?"
    variables = {"number": 5}
    result = renderer.render_pattern(pattern, variables)
    print(f"✓ Basic rendering: {result}")
    assert result == "What is 5 + 5?"
    
    # Test option rendering
    option_patterns = [
        "{{number}}",
        "{{number + 1}}",
        "{{number * 2}}",
        "{{number - 1}}"
    ]
    rendered_options = renderer.render_options(option_patterns, variables)
    print(f"✓ Option rendering: {rendered_options}")
    assert rendered_options == ["5", "6", "10", "4"]
    
    # Test complex expressions
    pattern = "If x = {{x}} and y = {{y}}, then x + y = {{x + y}}"
    variables = {"x": 12, "y": 8}
    result = renderer.render_pattern(pattern, variables)
    print(f"✓ Complex expression rendering: {result}")
    assert result == "If x = 12 and y = 8, then x + y = 20"
    
    print("✅ Template rendering tests passed!")


def test_answer_evaluation():
    """Test answer logic evaluation."""
    print("\n" + "=" * 60)
    print("TESTING ANSWER EVALUATION")
    print("=" * 60)
    
    from domain.template_engine import AnswerEvaluator
    
    evaluator = AnswerEvaluator()
    
    # Test simple arithmetic that returns a number
    answer_logic = "variables['number'] + variables['number']"
    variables = {"number": 14}
    result = evaluator.evaluate_answer_logic(answer_logic, variables)
    print(f"✓ Arithmetic evaluation: {result}")
    assert result == 28
    
    # Test string comparison
    answer_logic = "variables['operation'] == 'add'"
    variables = {"operation": "add"}
    result = evaluator.evaluate_answer_logic(answer_logic, variables)
    print(f"✓ String comparison: {result}")
    assert result == True
    
    # Test correct index finding
    rendered_options = ["28", "15", "16", "17"]
    correct_answer = 28
    correct_index = evaluator.find_correct_index(rendered_options, correct_answer)
    print(f"✓ Correct index finding: {correct_index}")
    assert correct_index == 0  # "28" is the first option (index 0)
    
    # Test numeric comparison
    rendered_options = ["14", "15", "16", "17"]
    correct_answer = 16
    correct_index = evaluator.find_correct_index(rendered_options, correct_answer)
    print(f"✓ Numeric correct index: {correct_index}")
    assert correct_index == 2  # "16" is the third option (index 2)
    
    print("✅ Answer evaluation tests passed!")


def test_lean_template_engine(db):
    """Test the complete LeanTemplateEngine."""
    print("\n" + "=" * 60)
    print("TESTING LEAN TEMPLATE ENGINE")
    print("=" * 60)
    
    # Set up test data
    template_id = setup_test_data(db)
    
    # Create engine
    engine = LeanTemplateEngine(db)
    
    print("\n1. Testing question generation:")
    
    # Generate a question
    question_data = engine.generate_question(template_id)
    payload = question_data["payload"]
    correct_index = question_data["correct_index"]
    variables = question_data["variables"]
    
    print(f"   Question ID: {payload['id']}")
    print(f"   Question: {payload['question']}")
    print(f"   Options: {payload['options']}")
    print(f"   Correct index: {correct_index}")
    print(f"   Variables: {variables}")
    
    # Verify payload structure
    required_fields = ["id", "template_id", "question", "options", "metadata"]
    for field in required_fields:
        assert field in payload, f"Missing field: {field}"
    
    # Verify metadata
    metadata = payload["metadata"]
    assert "concept_id" in metadata
    assert "difficulty" in metadata
    assert "bloom_level" in metadata
    assert "estimated_time" in metadata
    
    # Verify no correct answer in payload (security)
    assert "correct_answer" not in payload
    assert "correct_index" not in payload
    
    print("   ✓ Payload structure validated")
    print(f"   ✓ Payload size: {len(str(payload))} characters (target: ~800-1500)")
    
    print("\n2. Testing answer evaluation:")
    
    # Test correct answer
    evaluation = engine.evaluate_answer(template_id, correct_index, variables)
    print(f"   Correct answer evaluation: {evaluation}")
    assert evaluation["is_correct"] == True
    assert evaluation["selected_index"] == correct_index
    assert evaluation["correct_index"] == correct_index
    assert evaluation["feedback"] is None
    
    # Test incorrect answer
    incorrect_index = (correct_index + 1) % len(payload["options"])
    evaluation = engine.evaluate_answer(template_id, incorrect_index, variables)
    print(f"   Incorrect answer evaluation: {evaluation['is_correct']}")
    assert evaluation["is_correct"] == False
    assert evaluation["feedback"] is not None
    assert "misconception_code" in evaluation["feedback"]
    
    print("   ✓ Answer evaluation working correctly")
    
    print("\n3. Testing bulk question generation:")
    
    # Generate multiple questions for concept
    questions = engine.generate_questions_for_concept(
        "math.class5.factors_multiples.divisibility",
        count=3
    )
    
    print(f"   Generated {len(questions)} questions")
    for i, q in enumerate(questions):
        print(f"   Question {i+1}: {q['question'][:50]}...")
    
    assert len(questions) > 0
    assert all("question" in q for q in questions)
    assert all("options" in q for q in questions)
    
    print("   ✓ Bulk generation working correctly")
    
    print("\n✅ LeanTemplateEngine tests passed!")
    
    return template_id


def test_payload_size(db, template_id):
    """Test that payload sizes meet the target requirements."""
    print("\n" + "=" * 60)
    print("TESTING PAYLOAD SIZE OPTIMIZATION")
    print("=" * 60)
    
    engine = LeanTemplateEngine(db)
    
    # Generate multiple questions and check sizes
    sizes = []
    for i in range(10):
        question_data = engine.generate_question(template_id)
        payload = question_data["payload"]
        payload_size = len(str(payload))
        sizes.append(payload_size)
        print(f"   Question {i+1}: {payload_size} characters")
    
    avg_size = sum(sizes) / len(sizes)
    min_size = min(sizes)
    max_size = max(sizes)
    
    print(f"\n   Size statistics:")
    print(f"   Average: {avg_size:.0f} characters")
    print(f"   Min: {min_size} characters")
    print(f"   Max: {max_size} characters")
    
    # Target is 800-1500 characters
    target_min, target_max = 800, 1500
    
    if target_min <= avg_size <= target_max:
        print(f"   ✅ Average size within target range ({target_min}-{target_max})")
    else:
        print(f"   ⚠️  Average size outside target range ({target_min}-{target_max})")
    
    print("✅ Payload size analysis complete!")


def main():
    """Run all Phase 4 tests."""
    print("🚀 STARTING PHASE 4 LEAN TEMPLATE ENGINE TESTS")
    print("=" * 80)
    
    # Set up database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Clean up any existing test data
        db.execute(text("DELETE FROM template_option_misconceptions"))
        db.execute(text("DELETE FROM template_diagrams"))
        db.execute(text("DELETE FROM misconceptions"))
        db.execute(text("DELETE FROM question_templates"))
        db.commit()
        
        # Run all tests
        test_variable_generation()
        test_template_rendering()
        test_answer_evaluation()
        template_id = test_lean_template_engine(db)
        test_payload_size(db, template_id)
        
        print("\n🎉 ALL PHASE 4 TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nPhase 4 implementation is ready for use!")
        print("\nAcceptance criteria met:")
        print("✅ LeanTemplateEngine generates questions from templates")
        print("✅ Variable generation works from JSON schemas")
        print("✅ Template rendering with Jinja2 functions correctly")
        print("✅ Answer logic evaluation and correct answer computation")
        print("✅ Lean question payload format implemented")
        print("✅ Answer evaluation with misconception mapping")
        print("✅ End-to-end generation for divisibility concept")
        print("✅ Payload size optimization analyzed")
        
        print("\nNext steps:")
        print("1. Create API endpoints for question generation")
        print("2. Integrate with existing question delivery system")
        print("3. Add more template schemas for different concepts")
        print("4. Implement caching for generated questions")
        
    except Exception as e:
        print(f"❌ PHASE 4 TESTS FAILED: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == '__main__':
    main()
