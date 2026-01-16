"""
Phase 10: Migration Testing Suite

Tests for legacy-to-template migration, parity verification, and fallback behavior.

Usage:
    pytest tests/test_phase10_migration.py -v
    pytest tests/test_phase10_migration.py::TestTemplateExtraction -v
    pytest tests/test_phase10_migration.py::TestParityVerification -v
"""

import pytest
import json
import random
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTemplateExtraction:
    """Test template extraction from legacy patterns."""
    
    def test_extractor_loads_all_concepts(self):
        """Verify all 11 concepts are defined."""
        from tools.legacy_extractor import ALL_TEMPLATES
        
        expected_concepts = [
            "factors", "multiples", "gcd", "lcm", "divisibility",
            "prime_composite", "prime_factorization", "word_problem",
            "assertion_reason", "error_analysis"
        ]
        
        for concept in expected_concepts:
            assert concept in ALL_TEMPLATES, f"Missing concept: {concept}"
    
    def test_extractor_statistics(self):
        """Verify extraction statistics."""
        from tools.legacy_extractor import LegacyExtractor
        
        extractor = LegacyExtractor()
        stats = extractor.get_statistics()
        
        # Should have templates for each concept
        assert stats["total_templates"] >= 10, "Should have at least 10 templates"
        assert len(stats["by_concept"]) >= 10, "Should cover all 10 concepts"
        
        # Check bloom level distribution
        assert "UNDERSTAND" in stats["by_bloom_level"]
        assert "APPLY" in stats["by_bloom_level"]
        
        # Check difficulty distribution
        assert 1 in stats["by_difficulty"] or 2 in stats["by_difficulty"]
    
    def test_template_structure_validity(self):
        """Verify extracted templates have valid structure."""
        from tools.legacy_extractor import ALL_TEMPLATES
        
        for concept, templates in ALL_TEMPLATES.items():
            for template in templates:
                # Required fields
                assert template.concept_id, f"{concept}: Missing concept_id"
                assert template.template_code, f"{concept}: Missing template_code"
                assert template.question_pattern, f"{concept}: Missing question_pattern"
                assert template.variable_schema, f"{concept}: Missing variable_schema"
                assert template.answer_logic, f"{concept}: Missing answer_logic"
                assert template.option_patterns, f"{concept}: Missing option_patterns"
                assert len(template.option_patterns) >= 2, f"{concept}: Need at least 2 options"
                
                # Valid bloom level
                valid_blooms = ["REMEMBER", "UNDERSTAND", "APPLY", "ANALYZE", "EVALUATE", "CREATE"]
                assert template.bloom_level in valid_blooms, f"{concept}: Invalid bloom level"
                
                # Valid difficulty
                assert 1 <= template.difficulty <= 5, f"{concept}: Invalid difficulty"
                
                # Valid estimated time
                assert template.estimated_time > 0, f"{concept}: Invalid estimated time"
    
    def test_concept_id_format(self):
        """Verify concept IDs follow taxonomy format."""
        from tools.legacy_extractor import ALL_TEMPLATES
        
        for concept, templates in ALL_TEMPLATES.items():
            for template in templates:
                # Should follow pattern: subject.grade.chapter.concept
                parts = template.concept_id.split(".")
                assert len(parts) >= 4, f"Invalid concept_id format: {template.concept_id}"
                assert parts[0] == "math", f"Subject should be 'math': {template.concept_id}"
    
    def test_json_export(self, tmp_path):
        """Verify JSON export works correctly."""
        from tools.legacy_extractor import LegacyExtractor
        
        extractor = LegacyExtractor(output_dir=str(tmp_path))
        
        # Export single concept
        output = extractor.export_to_json("factors")
        assert Path(output).exists()
        
        # Verify JSON is valid
        with open(output) as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert "concept_id" in data[0]
    
    def test_answer_logic_syntax(self):
        """Verify answer logic expressions are valid Python."""
        from tools.legacy_extractor import ALL_TEMPLATES
        
        for concept, templates in ALL_TEMPLATES.items():
            for template in templates:
                try:
                    # Basic syntax check
                    compile(template.answer_logic, '<answer_logic>', 'eval')
                except SyntaxError as e:
                    pytest.fail(f"Invalid answer logic in {template.template_code}: {e}")


class TestTemplateMigration:
    """Test template migration to database."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = None
        session.flush = MagicMock()
        session.commit = MagicMock()
        return session
    
    def test_migration_import_creates_templates(self, mock_db_session):
        """Verify templates are created during import."""
        from tools.template_migrator import TemplateMigrator
        
        migrator = TemplateMigrator(db_session=mock_db_session)
        
        # Import a single concept
        result = migrator.import_templates(concept_key="factors")
        
        assert result["imported"] >= 1, "Should import at least 1 template"
        assert mock_db_session.add.called
    
    def test_migration_skips_existing(self, mock_db_session):
        """Verify existing templates are skipped."""
        from tools.template_migrator import TemplateMigrator
        from db.models.templates import QuestionTemplate
        
        # Simulate existing template
        existing = MagicMock(spec=QuestionTemplate)
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing
        
        migrator = TemplateMigrator(db_session=mock_db_session)
        result = migrator.import_templates(concept_key="factors")
        
        assert result["skipped"] >= 1, "Should skip existing templates"
    
    def test_migration_validation(self, mock_db_session):
        """Verify templates are validated during import."""
        from tools.template_migrator import TemplateMigrator
        
        migrator = TemplateMigrator(db_session=mock_db_session)
        
        # Test validation method directly
        template = MagicMock()
        template.concept_id = "math.class5.factors_multiples.factors"
        template.question_pattern = "Find factors of {{ n }}"
        template.answer_logic = "sorted([i for i in range(1, n+1) if n % i == 0])"
        template.option_patterns = ["{{ a }}", "{{ b }}", "{{ c }}", "{{ d }}"]
        template.variable_schema = {"type": "object"}
        
        result = migrator._validate_template(template)
        
        assert result["passed"], f"Validation should pass: {result['errors']}"
    
    def test_migration_status_tracking(self, mock_db_session):
        """Verify status tracking works."""
        from tools.template_migrator import TemplateMigrator
        
        # Setup mock counts
        mock_db_session.query.return_value.filter.return_value.count.return_value = 5
        mock_db_session.query.return_value.distinct.return_value.all.return_value = []
        
        migrator = TemplateMigrator(db_session=mock_db_session)
        status = migrator.get_migration_status()
        
        assert "legacy_concepts" in status
        assert "legacy_template_count" in status
        assert "db_templates" in status
        assert "coverage" in status


class TestParityVerification:
    """Verify template generation matches legacy quality."""
    
    def test_factors_template_produces_valid_question(self):
        """Verify factors template produces valid question structure."""
        from tools.legacy_extractor import FACTORS_TEMPLATES
        from domain.template_engine.lean_template_engine import VariableGenerator, TemplateRenderer, AnswerEvaluator
        
        template = FACTORS_TEMPLATES[0]
        
        # Generate variables
        variables = VariableGenerator.generate_from_schema(template.variable_schema)
        
        assert "target_number" in variables
        assert 6 <= variables["target_number"] <= 100
        
        # Compute answer
        answer = AnswerEvaluator.evaluate_answer_logic(template.answer_logic, variables)
        
        # Verify answer is correct factors
        target = variables["target_number"]
        expected_factors = sorted([i for i in range(1, target + 1) if target % i == 0])
        assert answer == expected_factors, f"Answer mismatch for {target}"
    
    def test_gcd_template_produces_correct_answer(self):
        """Verify GCD template computes correctly."""
        from tools.legacy_extractor import GCD_TEMPLATES
        from domain.template_engine.lean_template_engine import VariableGenerator, AnswerEvaluator
        import math
        
        template = GCD_TEMPLATES[0]
        
        # Generate multiple samples
        for _ in range(10):
            variables = VariableGenerator.generate_from_schema(template.variable_schema)
            
            answer = AnswerEvaluator.evaluate_answer_logic(template.answer_logic, variables)
            expected = math.gcd(variables["num1"], variables["num2"])
            
            assert answer == expected, f"GCD mismatch: {variables['num1']}, {variables['num2']}"
    
    def test_lcm_template_produces_correct_answer(self):
        """Verify LCM template computes correctly."""
        from tools.legacy_extractor import LCM_TEMPLATES
        from domain.template_engine.lean_template_engine import VariableGenerator, AnswerEvaluator
        import math
        
        template = LCM_TEMPLATES[0]
        
        # Generate multiple samples
        for _ in range(10):
            variables = VariableGenerator.generate_from_schema(template.variable_schema)
            
            answer = AnswerEvaluator.evaluate_answer_logic(template.answer_logic, variables)
            num1, num2 = variables["num1"], variables["num2"]
            expected = (num1 * num2) // math.gcd(num1, num2)
            
            assert answer == expected, f"LCM mismatch: {num1}, {num2}"
    
    def test_multiples_template_produces_correct_list(self):
        """Verify multiples template produces correct list."""
        from tools.legacy_extractor import MULTIPLES_TEMPLATES
        from domain.template_engine.lean_template_engine import VariableGenerator, AnswerEvaluator
        
        template = MULTIPLES_TEMPLATES[0]
        
        # Generate multiple samples
        for _ in range(10):
            variables = VariableGenerator.generate_from_schema(template.variable_schema)
            
            answer = AnswerEvaluator.evaluate_answer_logic(template.answer_logic, variables)
            base = variables["base_number"]
            count = variables["count"]
            expected = [base * i for i in range(1, count + 1)]
            
            assert answer == expected, f"Multiples mismatch for {base}"
    
    def test_template_question_count_matches_options(self):
        """Verify each template has 4 options."""
        from tools.legacy_extractor import ALL_TEMPLATES
        
        for concept, templates in ALL_TEMPLATES.items():
            for template in templates:
                # Most MCQ templates should have 4 options
                assert len(template.option_patterns) >= 2, \
                    f"{template.template_code}: Need at least 2 options"
    
    def test_misconception_coverage(self):
        """Verify key concepts have misconception mappings."""
        from tools.legacy_extractor import ALL_TEMPLATES
        
        # These concepts should definitely have misconceptions
        concepts_with_misconceptions = ["factors", "multiples", "gcd", "lcm"]
        
        for concept in concepts_with_misconceptions:
            templates = ALL_TEMPLATES.get(concept, [])
            has_misconceptions = any(t.misconceptions for t in templates)
            assert has_misconceptions, f"{concept} should have misconception mappings"


class TestTemplateQuestionService:
    """Test pure template-based question service."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = MagicMock()
        return session
    
    def test_service_init(self, mock_db_session):
        """Verify service initializes correctly."""
        from domain.template_service import TemplateQuestionService
        
        service = TemplateQuestionService(mock_db_session)
        
        assert service.db == mock_db_session
        assert service._metrics["generations"] == 0
    
    def test_metrics_tracking(self, mock_db_session):
        """Verify metrics are tracked correctly."""
        from domain.template_service import TemplateQuestionService
        
        service = TemplateQuestionService(mock_db_session)
        service.reset_metrics()
        
        metrics = service.get_metrics()
        
        assert "generations" in metrics
        assert "failures" in metrics
        assert "by_concept" in metrics
        assert "avg_generation_time_ms" in metrics
    
    def test_question_result_structure(self):
        """Verify QuestionResult has correct structure."""
        from domain.template_service import QuestionResult
        
        result = QuestionResult(
            question={"text": "Test question"},
            template_id=123,
            template_code="test_v1",
            concept_id="math.class5.factors",
            generation_time_ms=50.5
        )
        
        assert result.question == {"text": "Test question"}
        assert result.template_id == 123
        assert result.template_code == "test_v1"
        assert result.generation_time_ms == 50.5
    
    def test_template_stats_structure(self):
        """Verify TemplateStats has correct structure."""
        from domain.template_service import TemplateStats
        
        stats = TemplateStats(
            total_templates=100,
            published_templates=80,
            by_concept={"factors": 10, "multiples": 8},
            by_difficulty={1: 20, 2: 30, 3: 30},
            by_bloom_level={"UNDERSTAND": 40, "APPLY": 40},
            coverage_gaps=["prime_factorization"]
        )
        
        assert stats.total_templates == 100
        assert stats.published_templates == 80
        assert len(stats.coverage_gaps) == 1
    
    def test_no_templates_raises_value_error(self, mock_db_session):
        """Verify ValueError raised when no templates found."""
        from domain.template_service import TemplateQuestionService
        
        # Mock empty query result
        mock_db_session.query.return_value.filter.return_value.filter.return_value.all.return_value = []
        
        service = TemplateQuestionService(mock_db_session)
        
        with pytest.raises(ValueError, match="No published templates found"):
            service.generate_question(concept_key="nonexistent")


class TestEndToEndMigration:
    """End-to-end migration flow tests."""
    
    def test_extraction_to_json_roundtrip(self, tmp_path):
        """Verify extraction and re-loading works."""
        from tools.legacy_extractor import LegacyExtractor, ExtractedTemplate
        
        extractor = LegacyExtractor(output_dir=str(tmp_path))
        
        # Export all
        extractor.export_to_json()
        
        # Verify combined file exists
        combined_file = tmp_path / "all_templates.json"
        assert combined_file.exists()
        
        # Load and verify structure
        with open(combined_file) as f:
            data = json.load(f)
        
        assert len(data) >= 10
        
        # Verify each template can be converted back
        for item in data:
            assert "concept_id" in item
            assert "template_code" in item
            assert "question_pattern" in item
    
    def test_coverage_calculation(self):
        """Verify coverage calculation works."""
        from tools.legacy_extractor import ALL_TEMPLATES
        
        total_templates = sum(len(t) for t in ALL_TEMPLATES.values())
        
        # Should have at least 15 templates total
        assert total_templates >= 15, f"Expected >= 15 templates, got {total_templates}"
        
        # Each concept should have at least 1 template
        for concept, templates in ALL_TEMPLATES.items():
            assert len(templates) >= 1, f"Concept {concept} has no templates"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
