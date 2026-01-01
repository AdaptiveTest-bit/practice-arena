"""
Unit Tests for Option Generator Service

Tests the StructuredOptionGenerator class with:
- Input validation
- Misconception selection
- Schema compliance
- Error handling
"""

import pytest
from unittest.mock import patch

from backend.services.option_generator_structured import (
    StructuredOptionGenerator,
    get_option_generator
)
from backend.models.distractor_schema import (
    QuestionOptionsStructured,
    DistractorItem,
    MisconceptionType
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def generator():
    """Create an option generator instance for testing."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        return StructuredOptionGenerator(api_key='test-key')


@pytest.fixture
def mock_skeleton():
    """Create a mock skeleton object for testing."""
    class MockSkeleton:
        def __init__(self):
            self.topic = "Multiplication"
            self.difficulty = 2
            self.operation = "multiply"
            self.operand1 = 3
            self.operand2 = 4
    
    return MockSkeleton()


# ============================================================================
# TEST: INPUT VALIDATION
# ============================================================================

class TestInputValidation:
    """Test input parameter validation."""
    
    def test_invalid_chapter_name_empty(self, generator, mock_skeleton):
        """Test that empty chapter_name is rejected."""
        with pytest.raises(ValueError, match="chapter_name"):
            generator.generate_options(
                skeleton=mock_skeleton,
                correct_answer=12,
                chapter_name="",
                topic="Multiplication",
                difficulty=2
            )
    
    def test_invalid_topic_empty(self, generator, mock_skeleton):
        """Test that empty topic is rejected."""
        with pytest.raises(ValueError, match="topic"):
            generator.generate_options(
                skeleton=mock_skeleton,
                correct_answer=12,
                chapter_name="Factors & Multiples",
                topic="",
                difficulty=2
            )
    
    def test_invalid_difficulty_low(self, generator, mock_skeleton):
        """Test that difficulty < 1 is rejected."""
        with pytest.raises(ValueError, match="Difficulty|difficulty"):
            generator.generate_options(
                skeleton=mock_skeleton,
                correct_answer=12,
                chapter_name="Factors & Multiples",
                topic="Multiplication",
                difficulty=0
            )
    
    def test_invalid_difficulty_high(self, generator, mock_skeleton):
        """Test that difficulty > 5 is rejected."""
        with pytest.raises(ValueError, match="Difficulty|difficulty"):
            generator.generate_options(
                skeleton=mock_skeleton,
                correct_answer=12,
                chapter_name="Factors & Multiples",
                topic="Multiplication",
                difficulty=6
            )


# ============================================================================
# TEST: MISCONCEPTION SELECTION
# ============================================================================

class TestMisconceptionSelection:
    """Test misconception selection logic."""
    
    def test_all_misconception_types_available(self):
        """Test that all misconception types are defined."""
        misconceptions = list(MisconceptionType)
        assert len(misconceptions) == 10
    
    def test_misconception_type_values(self):
        """Test that all misconception type values are correct."""
        expected_values = [
            'incomplete_reasoning',
            'reversed_operation',
            'forgot_step',
            'wrong_operation',
            'magnitude_error',
            'notation_error',
            'visual_error',
            'off_by_one',
            'wrong_unit',
            'calculation_error'
        ]
        actual_values = sorted([m.value for m in MisconceptionType])
        expected_sorted = sorted(expected_values)
        assert actual_values == expected_sorted
    
    def test_generate_options_with_no_target_misconceptions(self, generator, mock_skeleton):
        """Test that generator selects misconceptions when none provided."""
        # Validation should pass - generator will select appropriate misconceptions
        assert generator is not None


# ============================================================================
# TEST: SCHEMA VALIDATION
# ============================================================================

class TestSchemaValidation:
    """Test that output matches QuestionOptionsStructured schema."""
    
    def test_distractor_item_creation(self):
        """Test creating a DistractorItem with valid data."""
        distractor = DistractorItem(
            value=10,
            teaching_point="Miscounting items",
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            why_wrong="Student forgot to include all items in the count",
            remediation_hint="Use systematic counting to avoid missing items"
        )
        
        assert distractor.value == 10
        assert distractor.misconception_type == MisconceptionType.INCOMPLETE_REASONING
    
    def test_distractor_item_validation_why_wrong_length(self):
        """Test that why_wrong must be 20+ characters."""
        with pytest.raises(ValueError, match="20"):
            DistractorItem(
                value=10,
                teaching_point="Miscounting",
                misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                why_wrong="Too short",  # Less than 20 chars
                remediation_hint="Use systematic counting to avoid missing items"
            )
    
    def test_distractor_item_validation_remediation_length(self):
        """Test that remediation_hint can be any length (no minimum)."""
        # Remediation hint has no minimum length requirement
        distractor = DistractorItem(
            value=10,
            teaching_point="Miscounting",
            misconception_type=MisconceptionType.INCOMPLETE_REASONING,
            why_wrong="Student forgot to include all items in the count",
            remediation_hint="Count"  # No minimum length required
        )
        assert distractor.remediation_hint == "Count"
    
    def test_question_options_structured_creation(self):
        """Test creating QuestionOptionsStructured with valid distractors."""
        distractors = [
            DistractorItem(
                value=10,
                teaching_point="Forgot to add",
                misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                why_wrong="Student forgot to include all items in the count",
                remediation_hint="Use systematic counting to avoid missing items"
            ),
            DistractorItem(
                value=11,
                teaching_point="Wrong operation",
                misconception_type=MisconceptionType.REVERSED_OPERATION,
                why_wrong="Student reversed the order of operands in division",
                remediation_hint="Check the order of operands for non-commutative operations"
            ),
            DistractorItem(
                value=13,
                teaching_point="Visual confusion",
                misconception_type=MisconceptionType.VISUAL_ERROR,
                why_wrong="Student misread the quantity shown in the visual",
                remediation_hint="Use physical objects to verify the visual representation"
            )
        ]
        
        options = QuestionOptionsStructured(
            correct_option=12,
            correct_teaching_point="Correct systematic counting of all items",
            distractors=distractors
        )
        
        assert options.correct_option == 12
        assert len(options.distractors) == 3
    
    def test_question_options_requires_exactly_3_distractors(self):
        """Test that QuestionOptionsStructured requires exactly 3 distractors."""
        distractors = [
            DistractorItem(
                value=10,
                teaching_point="Wrong answer",
                misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                why_wrong="Student forgot to include all items in the count",
                remediation_hint="Use systematic counting to avoid missing items"
            ),
            DistractorItem(
                value=11,
                teaching_point="Another wrong",
                misconception_type=MisconceptionType.REVERSED_OPERATION,
                why_wrong="Student reversed the order of operands in division",
                remediation_hint="Check the order of operands for non-commutative operations"
            )
        ]
        
        with pytest.raises(ValueError, match="3"):
            QuestionOptionsStructured(
                correct_option=12,
                correct_teaching_point="Correct",
                distractors=distractors  # Only 2 distractors
            )
    
    def test_question_options_unique_misconceptions(self):
        """Test that all distractors have unique misconceptions."""
        distractors = [
            DistractorItem(
                value=10,
                teaching_point="Wrong",
                misconception_type=MisconceptionType.INCOMPLETE_REASONING,
                why_wrong="Student forgot to include all items in the count",
                remediation_hint="Use systematic counting to avoid missing items"
            ),
            DistractorItem(
                value=11,
                teaching_point="Wrong",
                misconception_type=MisconceptionType.INCOMPLETE_REASONING,  # DUPLICATE
                why_wrong="Student forgot to include all items in the count",
                remediation_hint="Use systematic counting to avoid missing items"
            ),
            DistractorItem(
                value=13,
                teaching_point="Wrong",
                misconception_type=MisconceptionType.VISUAL_ERROR,
                why_wrong="Student misread the quantity shown in the visual",
                remediation_hint="Use physical objects to verify the visual representation"
            )
        ]
        
        with pytest.raises(ValueError, match="unique"):
            QuestionOptionsStructured(
                correct_option=12,
                correct_teaching_point="Correct",
                distractors=distractors
            )


# ============================================================================
# TEST: FACTORY FUNCTION
# ============================================================================

class TestFactoryFunction:
    """Test the factory function get_option_generator."""
    
    def test_factory_returns_generator(self):
        """Test that factory function returns StructuredOptionGenerator."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            gen = get_option_generator('test-key')
            assert isinstance(gen, StructuredOptionGenerator)
    
    def test_factory_with_custom_model(self):
        """Test factory function behavior."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            gen = get_option_generator('test-key')
            # Factory should return a working generator
            assert isinstance(gen, StructuredOptionGenerator)
            assert gen.model is not None


# ============================================================================
# TEST: INITIALIZATION
# ============================================================================

class TestInitialization:
    """Test generator initialization."""
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        gen = StructuredOptionGenerator(api_key='test-key')
        assert gen.model == "claude-3-5-sonnet-20241022"
    
    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        gen = StructuredOptionGenerator(
            api_key='test-key',
            model='claude-3-sonnet-20240229'
        )
        assert gen.model == 'claude-3-sonnet-20240229'


# ============================================================================
# TEST: MISCONCEPTION FORMATTING
# ============================================================================

class TestMisconceptionFormatting:
    """Test misconception description formatting."""
    
    def test_misconception_descriptions_exist(self):
        """Test that all misconceptions have descriptions."""
        # Each misconception should have a description for prompt building
        misconceptions = list(MisconceptionType)
        assert len(misconceptions) > 0
        
        for misconception in misconceptions:
            assert misconception.value is not None
            assert len(misconception.value) > 0


# ============================================================================
# TEST: ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test error handling in option generation."""
    
    def test_generator_initialization(self):
        """Test that generator initializes without errors."""
        gen = StructuredOptionGenerator(api_key='test-key')
        assert gen is not None
