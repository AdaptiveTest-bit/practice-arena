"""
Test Universal Template Ingestor.

Run with: python -m pytest tests/test_universal_ingestor.py -v
Or standalone: python tests/test_universal_ingestor.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.template_engine.universal_schema import (
    UniversalTemplate,
    UniversalTemplateBatch,
    QuestionType,
    VariableSchema,
    BaseVariable,
    ComputedVariable,
    OptionDefinition,
)
from domain.template_engine.lean_template_engine import VariableGenerator


def test_schema_validation():
    """Test that Universal Schema validates correctly."""
    template_data = {
        "name": "Test - Quadratic Roots by Factorization",
        "concept_id": "math.class10.quadratic.solve_factorization",
        "question_type": "MCQ",
        "question_pattern": "Find the roots of x² − {{sum}}x + {{product}} = 0",
        "variables": {
            "base": {
                "root1": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                "root2": {"type": "integer", "enum": [2, 3, 4, 5, 6]}
            },
            "computed": {
                "sum": {"formula": "root1 + root2"},
                "product": {"formula": "root1 * root2"}
            },
            "constraints": ["root1 < root2"]
        },
        "options": [
            {"pattern": "{{root1}}, {{root2}}", "is_correct": True},
            {"pattern": "{{root1}}, -{{root2}}", "is_correct": False, "misconception_id": "SIGN_ERROR"},
            {"pattern": "{{sum}}, {{product}}", "is_correct": False, "misconception_id": "SUM_PRODUCT_CONFUSION"},
            {"pattern": "{{root1 + 1}}, {{root2 - 1}}", "is_correct": False}
        ],
        "difficulty": 2,
        "bloom_level": "APPLY",
        "estimated_time": 60,
        "hints": [
            "Think about what two numbers add up to {{sum}}",
            "Those same numbers should multiply to give {{product}}"
        ],
        "tags": ["quadratic", "factorization", "roots"]
    }
    
    # Validate schema
    template = UniversalTemplate.model_validate(template_data)
    
    assert template.name == "Test - Quadratic Roots by Factorization"
    assert template.concept_id == "math.class10.quadratic.solve_factorization"
    assert template.question_type == QuestionType.MCQ
    assert len(template.variables.base) == 2
    assert len(template.variables.computed) == 2
    assert len(template.options) == 4
    assert template.difficulty == 2
    
    print("✅ Schema validation passed")
    return template


def test_variable_generation(template):
    """Test that variables generate correctly from schema."""
    # Build schema for VariableGenerator
    schema = {
        "type": "object",
        "properties": {
            name: {
                "type": var.type,
                **({"enum": var.enum} if var.enum else {}),
                **({"minimum": var.minimum} if var.minimum else {}),
                **({"maximum": var.maximum} if var.maximum else {}),
            }
            for name, var in template.variables.base.items()
        },
        "computed": {
            name: {
                "formula": var.formula if hasattr(var, 'formula') else var.get('formula', '')
            }
            for name, var in template.variables.computed.items()
        }
    }
    
    # Generate variables 10 times
    for i in range(10):
        variables = VariableGenerator.generate_from_schema(schema)
        
        assert "root1" in variables
        assert "root2" in variables
        assert "sum" in variables
        assert "product" in variables
        
        # Verify computed values
        assert variables["sum"] == variables["root1"] + variables["root2"]
        assert variables["product"] == variables["root1"] * variables["root2"]
    
    print("✅ Variable generation passed (10 iterations)")
    return variables


def test_pattern_rendering(template, variables):
    """Test that patterns render correctly."""
    import re
    
    def render_pattern(pattern, variables):
        def replace_var(match):
            expr = match.group(1).strip()
            try:
                if expr in variables:
                    return str(variables[expr])
                safe_funcs = VariableGenerator._get_safe_functions()
                eval_context = {**variables, **safe_funcs}
                return str(eval(expr, {"__builtins__": {}}, eval_context))
            except:
                return match.group(0)
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, pattern)
    
    # Render question
    question = render_pattern(template.question_pattern, variables)
    assert "{{" not in question  # All variables should be replaced
    
    # Render options
    options = []
    for opt in template.options:
        rendered = render_pattern(opt.pattern, variables)
        options.append(rendered)
        assert "{{" not in rendered
    
    # Check no duplicates
    assert len(options) == len(set(options)), "Duplicate options detected!"
    
    print(f"✅ Pattern rendering passed")
    print(f"   Question: {question}")
    print(f"   Options: {options}")
    return question, options


def test_assertion_reason_template():
    """Test Assertion-Reason question type."""
    template_data = {
        "name": "Test - A-R Discriminant",
        "concept_id": "math.class10.quadratic.assertion_reason",
        "question_type": "ASSERTION_REASON",
        "parts": [
            {
                "type": "assertion",
                "label": "A",
                "pattern": "The equation x² − {{b}}x + {{c}} = 0 has two real roots."
            },
            {
                "type": "reason",
                "label": "R", 
                "pattern": "The discriminant D = {{discriminant}} is non-negative."
            }
        ],
        "variables": {
            "base": {
                "b": {"type": "integer", "enum": [5, 6, 7, 8]},
                "c": {"type": "integer", "enum": [1, 2, 3, 4, 5]}
            },
            "computed": {
                "discriminant": {"formula": "b*b - 4*c"}
            },
            "constraints": []
        },
        "options": [
            {"pattern": "Both A and R are true and R explains A", "is_correct": True},
            {"pattern": "Both A and R are true but R does not explain A", "is_correct": False},
            {"pattern": "A is true but R is false", "is_correct": False},
            {"pattern": "A is false but R is true", "is_correct": False}
        ],
        "difficulty": 3
    }
    
    template = UniversalTemplate.model_validate(template_data)
    assert template.question_type == QuestionType.ASSERTION_REASON
    assert len(template.parts) == 2
    
    print("✅ Assertion-Reason template validated")


def test_case_study_template():
    """Test Case Study question type."""
    template_data = {
        "name": "Test - Projectile Case Study",
        "concept_id": "math.class10.quadratic.applications",
        "question_type": "CASE_STUDY",
        "parts": [
            {
                "type": "context",
                "pattern": "A ball is thrown and follows path h = -x² + {{b}}x"
            },
            {
                "type": "sub_question",
                "label": "i",
                "pattern": "At what x does the ball reach maximum height?",
                "options": [
                    {"pattern": "{{max_x}} m", "is_correct": True},
                    {"pattern": "{{b}} m", "is_correct": False}
                ]
            }
        ],
        "variables": {
            "base": {
                "b": {"type": "integer", "enum": [4, 6, 8, 10]}
            },
            "computed": {
                "max_x": {"formula": "b / 2"}
            },
            "constraints": []
        },
        "options": [
            {"pattern": "See sub-questions", "is_correct": True},
            {"pattern": "N/A", "is_correct": False}
        ],
        "difficulty": 4
    }
    
    template = UniversalTemplate.model_validate(template_data)
    assert template.question_type == QuestionType.CASE_STUDY
    assert len(template.parts) == 2
    
    print("✅ Case Study template validated")


def test_batch_validation():
    """Test batch template validation."""
    batch_data = {
        "templates": [
            {
                "name": "Batch Test 1",
                "concept_id": "math.test",
                "question_pattern": "What is {{a}} + {{b}}?",
                "variables": {
                    "base": {"a": {"type": "integer", "minimum": 1, "maximum": 10}},
                    "computed": {"b": {"formula": "a + 1"}}
                },
                "options": [
                    {"pattern": "{{a + b}}", "is_correct": True},
                    {"pattern": "{{a}}", "is_correct": False}
                ]
            },
            {
                "name": "Batch Test 2",
                "concept_id": "math.test",
                "question_pattern": "What is {{x}} * {{y}}?",
                "variables": {
                    "base": {
                        "x": {"type": "integer", "minimum": 2, "maximum": 5},
                        "y": {"type": "integer", "minimum": 2, "maximum": 5}
                    },
                    "computed": {"product": {"formula": "x * y"}}
                },
                "options": [
                    {"pattern": "{{product}}", "is_correct": True},
                    {"pattern": "{{x + y}}", "is_correct": False}
                ]
            }
        ]
    }
    
    batch = UniversalTemplateBatch.model_validate(batch_data)
    assert len(batch.templates) == 2
    
    print("✅ Batch validation passed (2 templates)")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Universal Template Schema Tests")
    print("="*60 + "\n")
    
    # Test 1: Schema validation
    template = test_schema_validation()
    
    # Test 2: Variable generation
    variables = test_variable_generation(template)
    
    # Test 3: Pattern rendering
    test_pattern_rendering(template, variables)
    
    # Test 4: Assertion-Reason type
    test_assertion_reason_template()
    
    # Test 5: Case Study type
    test_case_study_template()
    
    # Test 6: Batch validation
    test_batch_validation()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
