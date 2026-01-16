"""
Phase 10: Template Migration Script

Imports extracted templates into the database and manages the migration
from legacy generators to template-based question generation.

Usage:
    python -m tools.template_migrator --import-all
    python -m tools.template_migrator --concept factors --publish
    python -m tools.template_migrator --status
    python -m tools.template_migrator --rollback --concept factors
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from db.models.templates import (
    QuestionTemplate, 
    Misconception, 
    TemplateOptionMisconception,
    TemplateDiagram,
    TemplateStatus
)
from tools.legacy_extractor import LegacyExtractor, ALL_TEMPLATES, ExtractedTemplate


class TemplateMigrator:
    """Manages migration of legacy generators to template system."""
    
    def __init__(self, db_session: Session = None):
        self.db = db_session
        self._own_session = False
        if self.db is None:
            self.db = SessionLocal()
            self._own_session = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._own_session:
            self.db.close()
    
    def import_templates(
        self, 
        concept_key: str = None, 
        auto_publish: bool = False,
        created_by: str = "migration_script"
    ) -> Dict[str, Any]:
        """
        Import templates for a concept or all concepts.
        
        Args:
            concept_key: Specific concept to import, or None for all
            auto_publish: If True, automatically publish after validation
            created_by: User/system identifier for audit trail
            
        Returns:
            Migration result summary
        """
        extractor = LegacyExtractor()
        
        if concept_key:
            templates = extractor.extract_concept(concept_key)
            concepts_to_import = {concept_key: templates}
        else:
            concepts_to_import = extractor.extract_all()
        
        results = {
            "imported": 0,
            "skipped": 0,
            "errors": [],
            "by_concept": {},
            "template_ids": []
        }
        
        for concept, templates in concepts_to_import.items():
            concept_results = {"imported": 0, "skipped": 0, "errors": []}
            
            for template in templates:
                try:
                    # Check if template already exists
                    existing = self.db.query(QuestionTemplate).filter(
                        QuestionTemplate.template_code == template.template_code
                    ).first()
                    
                    if existing:
                        concept_results["skipped"] += 1
                        results["skipped"] += 1
                        continue
                    
                    # Create new template
                    db_template = self._create_template(template, created_by)
                    self.db.add(db_template)
                    self.db.flush()  # Get ID for relationships
                    
                    # Add misconceptions
                    if template.misconceptions:
                        self._add_misconceptions(db_template, template.misconceptions)
                    
                    # Add diagram reference if needed
                    if template.diagram_type:
                        self._add_diagram(db_template, template.diagram_type)
                    
                    # Validate template
                    validation_result = self._validate_template(db_template)
                    db_template.validation_passed = validation_result["passed"]
                    db_template.validation_errors = validation_result.get("errors", [])
                    
                    # Auto-publish if requested and validation passed
                    if auto_publish and validation_result["passed"]:
                        db_template.status = TemplateStatus.PUBLISHED.value
                        db_template.published_at = datetime.utcnow()
                    
                    results["template_ids"].append(db_template.id)
                    concept_results["imported"] += 1
                    results["imported"] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to import {template.template_code}: {str(e)}"
                    concept_results["errors"].append(error_msg)
                    results["errors"].append(error_msg)
            
            results["by_concept"][concept] = concept_results
        
        self.db.commit()
        return results
    
    def _create_template(self, template: ExtractedTemplate, created_by: str) -> QuestionTemplate:
        """Create a QuestionTemplate from extracted template."""
        return QuestionTemplate(
            concept_id=template.concept_id,
            template_code=template.template_code,
            question_pattern=template.question_pattern,
            variable_schema=template.variable_schema,
            answer_logic=template.answer_logic,
            option_patterns=template.option_patterns,
            difficulty=template.difficulty,
            bloom_level=template.bloom_level,
            estimated_time=template.estimated_time,
            status=TemplateStatus.DRAFT.value,
            validation_passed=False,
            created_by=created_by
        )
    
    def _add_misconceptions(self, db_template: QuestionTemplate, misconceptions: List) -> None:
        """Add misconception mappings for a template."""
        for idx, misc in enumerate(misconceptions):
            # First, ensure the misconception exists in the global table
            existing_misc = self.db.query(Misconception).filter(
                Misconception.code == misc.misconception_code
            ).first()
            
            if not existing_misc:
                existing_misc = Misconception(
                    code=misc.misconception_code,
                    title=misc.misconception_code.replace("_", " ").title(),
                    description=misc.why_wrong,
                    teaching_point=misc.teaching_point,
                    subject="math",
                    concept_tags=[db_template.concept_id]
                )
                self.db.add(existing_misc)
                self.db.flush()
            
            # Create the mapping (option_index is +1 because index 0 is correct answer)
            mapping = TemplateOptionMisconception(
                template_id=db_template.id,
                misconception_id=existing_misc.id,
                option_index=idx + 1,  # Skip correct answer at index 0
                custom_explanation=misc.why_wrong
            )
            self.db.add(mapping)
    
    def _add_diagram(self, db_template: QuestionTemplate, diagram_type: str) -> None:
        """Add diagram reference for a template."""
        diagram = TemplateDiagram(
            template_id=db_template.id,
            diagram_type=diagram_type,
            name=f"{diagram_type}_diagram",
            variables={},
            alt_text=f"Diagram illustrating {diagram_type.replace('_', ' ')}"
        )
        self.db.add(diagram)
    
    def _validate_template(self, template: QuestionTemplate) -> Dict[str, Any]:
        """Validate a template for publishing readiness using content validators."""
        from domain.content_validation import get_taxonomy_validator, get_rubric_validator
        
        errors = []
        warnings = []
        
        # === Basic Field Validation ===
        if not template.concept_id:
            errors.append("Missing concept_id")
        if not template.question_pattern:
            errors.append("Missing question_pattern")
        if not template.answer_logic:
            errors.append("Missing answer_logic")
        if not template.option_patterns or len(template.option_patterns) < 2:
            errors.append("Need at least 2 option patterns")
        
        # Validate variable schema
        if template.variable_schema:
            try:
                if not isinstance(template.variable_schema, dict):
                    errors.append("variable_schema must be a JSON object")
            except:
                errors.append("Invalid variable_schema format")
        
        # Validate answer logic (basic syntax check)
        try:
            compile(template.answer_logic, '<answer_logic>', 'eval')
        except SyntaxError as e:
            errors.append(f"Invalid answer_logic syntax: {e}")
        
        # === Taxonomy Validation (from config/content/taxonomy) ===
        try:
            taxonomy_validator = get_taxonomy_validator()
            
            # Validate concept_id exists in taxonomy
            is_valid, error = taxonomy_validator.validate_concept_id(template.concept_id)
            if not is_valid:
                warnings.append(f"Taxonomy: {error}")  # Warning, not error - concept may be new
            
            # Validate difficulty is in allowed range
            if template.difficulty:
                is_valid, error = taxonomy_validator.validate_difficulty(
                    template.concept_id, template.difficulty
                )
                if not is_valid:
                    warnings.append(f"Taxonomy: {error}")
            
            # Validate bloom level matches concept
            if template.bloom_level:
                is_valid, error = taxonomy_validator.validate_bloom_level(
                    template.concept_id, template.bloom_level
                )
                if not is_valid:
                    warnings.append(f"Taxonomy: {error}")
                    
        except Exception as e:
            warnings.append(f"Taxonomy validation skipped: {e}")
        
        # === Rubric Validation (from config/content/rubrics) ===
        try:
            rubric_validator = get_rubric_validator()
            
            # Build template dict for rubric validation
            template_dict = {
                "question_text": template.question_pattern,
                "options": template.option_patterns,
                "meta": {
                    "concept_id": template.concept_id,
                    "bloom_level": template.bloom_level,
                    "difficulty": template.difficulty,
                },
            }
            
            # Run rubric checks
            is_valid, rubric_errors = rubric_validator.validate_checks(template_dict)
            if not is_valid:
                for err in rubric_errors:
                    warnings.append(f"Rubric: {err}")
                    
        except Exception as e:
            warnings.append(f"Rubric validation skipped: {e}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def publish_templates(self, concept_key: str = None, template_ids: List[int] = None) -> Dict[str, Any]:
        """
        Publish templates that have passed validation.
        
        Args:
            concept_key: Publish all templates for this concept
            template_ids: Specific template IDs to publish
            
        Returns:
            Publishing result summary
        """
        results = {"published": 0, "failed": 0, "errors": []}
        
        query = self.db.query(QuestionTemplate).filter(
            QuestionTemplate.status.in_([
                TemplateStatus.DRAFT.value,
                TemplateStatus.APPROVED.value
            ]),
            QuestionTemplate.validation_passed == True
        )
        
        if concept_key:
            query = query.filter(
                QuestionTemplate.concept_id.like(f"%{concept_key}%")
            )
        
        if template_ids:
            query = query.filter(QuestionTemplate.id.in_(template_ids))
        
        templates = query.all()
        
        for template in templates:
            try:
                template.status = TemplateStatus.PUBLISHED.value
                template.published_at = datetime.utcnow()
                results["published"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Failed to publish {template.id}: {str(e)}")
        
        self.db.commit()
        return results
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        status = {
            "legacy_concepts": list(ALL_TEMPLATES.keys()),
            "legacy_template_count": sum(len(t) for t in ALL_TEMPLATES.values()),
            "db_templates": {
                "total": 0,
                "draft": 0,
                "review": 0,
                "approved": 0,
                "published": 0,
                "archived": 0,
            },
            "by_concept": {},
            "coverage": {}
        }
        
        # Count templates by status
        for s in TemplateStatus:
            count = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.status == s.value
            ).count()
            status["db_templates"][s.value.lower()] = count
            status["db_templates"]["total"] += count
        
        # Count by concept
        concept_counts = self.db.query(
            QuestionTemplate.concept_id
        ).distinct().all()
        
        for (concept_id,) in concept_counts:
            count = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.concept_id == concept_id
            ).count()
            
            published = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.concept_id == concept_id,
                QuestionTemplate.status == TemplateStatus.PUBLISHED.value
            ).count()
            
            status["by_concept"][concept_id] = {
                "total": count,
                "published": published
            }
        
        # Calculate coverage
        for concept_key, legacy_templates in ALL_TEMPLATES.items():
            legacy_count = len(legacy_templates)
            
            # Find matching templates in DB
            matching = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.concept_id.like(f"%{concept_key}%"),
                QuestionTemplate.status == TemplateStatus.PUBLISHED.value
            ).count()
            
            status["coverage"][concept_key] = {
                "legacy": legacy_count,
                "migrated": matching,
                "percentage": round(matching / legacy_count * 100, 1) if legacy_count > 0 else 0
            }
        
        return status
    
    def rollback_concept(self, concept_key: str) -> Dict[str, Any]:
        """
        Archive all templates for a concept (rollback).
        
        Args:
            concept_key: Concept to rollback
            
        Returns:
            Rollback result
        """
        templates = self.db.query(QuestionTemplate).filter(
            QuestionTemplate.concept_id.like(f"%{concept_key}%")
        ).all()
        
        archived_count = 0
        for template in templates:
            template.status = TemplateStatus.ARCHIVED.value
            archived_count += 1
        
        self.db.commit()
        
        return {
            "concept": concept_key,
            "archived": archived_count
        }
    
    def delete_templates(self, concept_key: str = None, template_ids: List[int] = None) -> Dict[str, Any]:
        """
        Delete templates (for cleanup during development).
        
        Args:
            concept_key: Delete all templates for this concept
            template_ids: Specific template IDs to delete
            
        Returns:
            Deletion result
        """
        results = {"deleted": 0, "errors": []}
        
        query = self.db.query(QuestionTemplate)
        
        if concept_key:
            query = query.filter(
                QuestionTemplate.concept_id.like(f"%{concept_key}%")
            )
        
        if template_ids:
            query = query.filter(QuestionTemplate.id.in_(template_ids))
        
        templates = query.all()
        
        for template in templates:
            try:
                self.db.delete(template)
                results["deleted"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to delete {template.id}: {str(e)}")
        
        self.db.commit()
        return results


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate legacy generators to templates")
    parser.add_argument("--import-all", action="store_true", help="Import all templates")
    parser.add_argument("--concept", type=str, help="Specific concept to operate on")
    parser.add_argument("--publish", action="store_true", help="Publish imported templates")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--rollback", action="store_true", help="Rollback (archive) templates")
    parser.add_argument("--delete", action="store_true", help="Delete templates (development only)")
    parser.add_argument("--auto-publish", action="store_true", help="Auto-publish valid templates during import")
    
    args = parser.parse_args()
    
    with TemplateMigrator() as migrator:
        if args.status:
            status = migrator.get_migration_status()
            print("\n📊 Migration Status")
            print("=" * 50)
            print(f"Legacy concepts: {len(status['legacy_concepts'])}")
            print(f"Legacy templates: {status['legacy_template_count']}")
            print(f"\nDatabase templates:")
            for key, count in status['db_templates'].items():
                if key != 'total':
                    print(f"  - {key}: {count}")
            print(f"  TOTAL: {status['db_templates']['total']}")
            print(f"\nCoverage by concept:")
            for concept, cov in status['coverage'].items():
                print(f"  - {concept}: {cov['migrated']}/{cov['legacy']} ({cov['percentage']}%)")
            return
        
        if args.import_all or args.concept:
            print(f"\n🔄 Importing templates...")
            result = migrator.import_templates(
                concept_key=args.concept,
                auto_publish=args.auto_publish
            )
            print(f"✅ Imported: {result['imported']}")
            print(f"⏭️  Skipped: {result['skipped']}")
            if result['errors']:
                print(f"❌ Errors: {len(result['errors'])}")
                for err in result['errors'][:5]:
                    print(f"   - {err}")
        
        if args.publish:
            print(f"\n📤 Publishing templates...")
            result = migrator.publish_templates(concept_key=args.concept)
            print(f"✅ Published: {result['published']}")
            if result['errors']:
                print(f"❌ Errors: {len(result['errors'])}")
        
        if args.rollback:
            if not args.concept:
                print("❌ --rollback requires --concept")
                return
            print(f"\n⏪ Rolling back {args.concept}...")
            result = migrator.rollback_concept(args.concept)
            print(f"✅ Archived: {result['archived']} templates")
        
        if args.delete:
            print(f"\n🗑️  Deleting templates...")
            result = migrator.delete_templates(concept_key=args.concept)
            print(f"✅ Deleted: {result['deleted']}")


if __name__ == "__main__":
    main()
