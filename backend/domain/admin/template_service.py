"""
Admin Service Layer for Phase 5 implementation.

Handles template management, workflow transitions, and validation.
Integrates with Phase 2 validators and Phase 3 database models.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime

from db.models import QuestionTemplate, Misconception, TemplateOptionMisconception, TemplateStatus
from domain.content_validation import TaxonomyValidator, RubricValidator
from domain.template_engine import LeanTemplateEngine


class TemplateValidationError(Exception):
    """Raised when template validation fails."""
    pass


class WorkflowTransitionError(Exception):
    """Raised when workflow transition is invalid."""
    pass


class AdminTemplateService:
    """
    Service layer for admin template management.
    
    Handles ingestion, validation, workflow transitions, and publishing.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.taxonomy_validator = TaxonomyValidator()
        self.rubric_validator = RubricValidator()
        self.template_engine = LeanTemplateEngine(db)
    
    def ingest_template(self, template_data: Dict[str, Any], created_by: str) -> QuestionTemplate:
        """
        Ingest a new template with validation.
        
        Args:
            template_data: Template definition data
            created_by: User who created the template
            
        Returns:
            Created template instance
            
        Raises:
            TemplateValidationError: If validation fails
        """
        # Validate concept ID and bloom level
        concept_id = template_data.get('concept_id', '')
        bloom_level = template_data.get('bloom_level', '')
        
        concept_valid, concept_error = self.taxonomy_validator.validate_concept_id(concept_id)
        if not concept_valid:
            raise TemplateValidationError(f"Concept validation failed: {concept_error}")
        
        bloom_valid, bloom_error = self.taxonomy_validator.validate_bloom_level(concept_id, bloom_level)
        if not bloom_valid:
            raise TemplateValidationError(f"Bloom level validation failed: {bloom_error}")
        
        concept_validation = {'valid': True, 'errors': []}
        
        # Validate template structure and quality (basic validation for now)
        required_fields = [
            'concept_id', 'template_code', 'question_pattern', 
            'variable_schema', 'answer_logic', 'option_patterns',
            'difficulty', 'bloom_level', 'estimated_time'
        ]
        
        errors = []
        for field in required_fields:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")
        
        # Basic field validation
        if 'difficulty' in template_data and not (1 <= template_data['difficulty'] <= 5):
            errors.append("Difficulty must be between 1 and 5")
        
        if 'option_patterns' in template_data and len(template_data['option_patterns']) != 4:
            errors.append("Must have exactly 4 option patterns")
        
        if errors:
            raise TemplateValidationError(f"Template validation failed: {errors}")
        
        rubric_validation = {'valid': True, 'errors': []}
        
        # Create template with validation results
        template = QuestionTemplate(
            concept_id=template_data['concept_id'],
            template_code=template_data['template_code'],
            question_pattern=template_data['question_pattern'],
            variable_schema=template_data['variable_schema'],
            answer_logic=template_data['answer_logic'],
            option_patterns=template_data['option_patterns'],
            difficulty=template_data['difficulty'],
            bloom_level=template_data['bloom_level'],
            estimated_time=template_data['estimated_time'],
            status="DRAFT",
            validation_passed=True,
            validation_errors=None,  # Clear errors since validation passed
            created_by=created_by
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        # Process misconceptions if provided
        if 'misconceptions' in template_data:
            self._process_template_misconceptions(template, template_data['misconceptions'])
        
        return template
    
    def ingest_bulk_templates(self, templates_data: List[Dict[str, Any]], created_by: str) -> Dict[str, Any]:
        """
        Bulk ingest multiple templates.
        
        Args:
            templates_data: List of template definitions
            created_by: User who created the templates
            
        Returns:
            Results summary with success/failure counts
        """
        results = {
            'total': len(templates_data),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'created_templates': []
        }
        
        for i, template_data in enumerate(templates_data):
            try:
                template = self.ingest_template(template_data, created_by)
                results['successful'] += 1
                results['created_templates'].append({
                    'index': i,
                    'template_id': template.id,
                    'concept_id': template.concept_id
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'index': i,
                    'error': str(e),
                    'concept_id': template_data.get('concept_id', 'unknown')
                })
        
        return results
    
    def submit_for_review(self, template_id: int, submitted_by: str) -> QuestionTemplate:
        """
        Submit a template for review.
        
        Args:
            template_id: ID of template to submit
            submitted_by: User submitting for review
            
        Returns:
            Updated template instance
            
        Raises:
            WorkflowTransitionError: If transition is invalid
        """
        template = self._get_template(template_id)
        
        # Validate workflow transition
        if template.status != "DRAFT":
            raise WorkflowTransitionError(f"Cannot submit template with status '{template.status}' for review")
        
        if not template.validation_passed:
            raise WorkflowTransitionError("Cannot submit template that failed validation")
        
        # Update template
        template.status = "REVIEW"
        template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def approve_template(self, template_id: int, approved_by: str) -> QuestionTemplate:
        """
        Approve a template.
        
        Args:
            template_id: ID of template to approve
            approved_by: User approving the template
            
        Returns:
            Updated template instance
            
        Raises:
            WorkflowTransitionError: If transition is invalid
        """
        template = self._get_template(template_id)
        
        # Validate workflow transition
        if template.status != "REVIEW":
            raise WorkflowTransitionError(f"Cannot approve template with status '{template.status}'")
        
        # Update template
        template.status = "APPROVED"
        template.reviewed_by = approved_by
        template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def publish_template(self, template_id: int, published_by: str) -> QuestionTemplate:
        """
        Publish a template for serving.
        
        Args:
            template_id: ID of template to publish
            published_by: User publishing the template
            
        Returns:
            Updated template instance
            
        Raises:
            WorkflowTransitionError: If transition is invalid
        """
        template = self._get_template(template_id)
        
        # Validate workflow transition
        if template.status != "APPROVED":
            raise WorkflowTransitionError(f"Cannot publish template with status '{template.status}'")
        
        if not template.validation_passed:
            raise WorkflowTransitionError("Cannot publish template that failed validation")
        
        # Update template
        template.status = "PUBLISHED"
        template.published_by = published_by
        template.published_at = datetime.utcnow()
        template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def reject_template(self, template_id: int, rejected_by: str, feedback: str) -> QuestionTemplate:
        """
        Reject a template with feedback.
        
        Args:
            template_id: ID of template to reject
            rejected_by: User rejecting the template
            feedback: Rejection feedback
            
        Returns:
            Updated template instance
            
        Raises:
            WorkflowTransitionError: If transition is invalid
        """
        template = self._get_template(template_id)
        
        # Validate workflow transition
        if template.status not in ["REVIEW", "APPROVED"]:
            raise WorkflowTransitionError(f"Cannot reject template with status '{template.status}'")
        
        # Update template
        template.status = "DRAFT"  # Send back to draft for fixes
        template.reviewed_by = rejected_by
        template.validation_errors = [feedback]  # Store feedback as validation error
        template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def archive_template(self, template_id: int, archived_by: str) -> QuestionTemplate:
        """
        Archive a template.
        
        Args:
            template_id: ID of template to archive
            archived_by: User archiving the template
            
        Returns:
            Updated template instance
        """
        template = self._get_template(template_id)
        
        # Update template
        template.status = "ARCHIVED"
        template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def get_templates_by_status(self, status: str, concept_id: Optional[str] = None) -> List[QuestionTemplate]:
        """
        Get templates filtered by status and optionally concept.
        
        Args:
            status: Template status to filter by
            concept_id: Optional concept ID to filter by
            
        Returns:
            List of templates
        """
        query = self.db.query(QuestionTemplate).filter(QuestionTemplate.status == status)
        
        if concept_id:
            query = query.filter(QuestionTemplate.concept_id == concept_id)
        
        return query.order_by(QuestionTemplate.created_at.desc()).all()
    
    def get_template_workflow_summary(self) -> Dict[str, int]:
        """
        Get summary of templates by workflow status.
        
        Returns:
            Dictionary with counts by status
        """
        summary = {}
        
        for status in ["DRAFT", "REVIEW", "APPROVED", "PUBLISHED", "ARCHIVED"]:
            count = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.status == status
            ).count()
            summary[status.lower()] = count
        
        summary['total'] = sum(summary.values())
        
        return summary
    
    def validate_template_for_generation(self, template_id: int) -> Dict[str, Any]:
        """
        Validate that a template can be used for question generation.
        
        Args:
            template_id: ID of template to validate
            
        Returns:
            Validation result with details
        """
        template = self._get_template(template_id)
        
        validation_result = {
            'template_id': template_id,
            'can_generate': False,
            'issues': []
        }
        
        # Check if template is published
        if template.status != "PUBLISHED":
            validation_result['issues'].append(f"Template is not published (current status: {template.status})")
        
        # Check if validation passed
        if not template.validation_passed:
            validation_result['issues'].append("Template failed validation")
        
        # Test question generation
        try:
            question_data = self.template_engine.generate_question(template_id)
            validation_result['can_generate'] = True
            validation_result['sample_question'] = question_data['payload']
        except Exception as e:
            validation_result['issues'].append(f"Question generation failed: {str(e)}")
        
        return validation_result
    
    def _get_template(self, template_id: int) -> QuestionTemplate:
        """Get template by ID or raise exception."""
        template = self.db.query(QuestionTemplate).filter(
            QuestionTemplate.id == template_id
        ).first()
        
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
        
        return template
    
    def _process_template_misconceptions(self, template: QuestionTemplate, misconceptions_data: List[Dict[str, Any]]):
        """Process misconceptions for a template."""
        for misconception_data in misconceptions_data:
            # Find or create misconception
            misconception = self.db.query(Misconception).filter(
                Misconception.code == misconception_data['code']
            ).first()
            
            if not misconception:
                # Create new misconception
                misconception = Misconception(
                    code=misconception_data['code'],
                    title=misconception_data['title'],
                    description=misconception_data['description'],
                    teaching_point=misconception_data['teaching_point'],
                    subject=misconception_data['subject'],
                    concept_tags=misconception_data.get('concept_tags', [])
                )
                self.db.add(misconception)
                self.db.flush()  # Get ID without committing
            
            # Link misconception to template option
            option_misconception = TemplateOptionMisconception(
                template_id=template.id,
                misconception_id=misconception.id,
                option_index=misconception_data['option_index'],
                custom_explanation=misconception_data.get('custom_explanation')
            )
            self.db.add(option_misconception)
        
        self.db.commit()
