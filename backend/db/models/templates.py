"""
SQLAlchemy models for Phase 3 lean template architecture.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base
import enum


class TemplateStatus(enum.Enum):
    """Template workflow status."""
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    
    @classmethod
    def values(cls):
        """Get all string values for the enum."""
        return [e.value for e in cls]
    
    @classmethod
    def is_valid(cls, value):
        """Check if a value is a valid status."""
        return value in cls.values()


class QuestionTemplate(Base):
    """
    Lean template for question generation with review lifecycle.
    
    Stores template definitions with minimal fields required for generating
    question instances while maintaining workflow state and validation.
    """
    __tablename__ = "question_templates"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(String(255), nullable=False, index=True, comment="Concept ID from taxonomy")
    
    # Template definition fields
    template_code = Column(Text, nullable=False, comment="Python template code for variable generation")
    question_pattern = Column(Text, nullable=False, comment="Question text template with variable placeholders")
    variable_schema = Column(JSON, nullable=False, comment="Schema defining variables and their generation rules")
    answer_logic = Column(Text, nullable=False, comment="Logic to compute correct answer from variables")
    option_patterns = Column(JSON, nullable=False, comment="Patterns for generating answer options")
    
    # Metadata fields
    difficulty = Column(Integer, nullable=False, comment="Difficulty level 1-5")
    bloom_level = Column(String(50), nullable=False, comment="Bloom's taxonomy level")
    estimated_time = Column(Integer, nullable=False, comment="Estimated time in seconds")
    
    # Workflow fields - using String instead of Enum to avoid database conflicts
    status = Column(String(20), nullable=False, default="DRAFT", index=True)
    
    # Validation fields
    validation_passed = Column(Boolean, default=False, nullable=False)
    validation_errors = Column(JSON, comment="List of validation errors if any")
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(255), comment="User or system that created the template")
    reviewed_by = Column(String(255), comment="User who reviewed the template")
    published_at = Column(DateTime(timezone=True), comment="When template was published")
    
    # Relationships
    misconceptions = relationship("TemplateOptionMisconception", back_populates="template", cascade="all, delete-orphan")
    diagrams = relationship("TemplateDiagram", back_populates="template", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<QuestionTemplate(id={self.id}, concept_id='{self.concept_id}', status='{self.status}')>"
    
    @property
    def is_published(self):
        """Check if template is in published status."""
        return self.status == TemplateStatus.PUBLISHED.value
    
    def can_be_published(self):
        """Check if template meets criteria for publishing."""
        return (
            self.validation_passed and 
            self.status in [TemplateStatus.APPROVED.value, TemplateStatus.PUBLISHED.value]
        )
    
    def set_status(self, status):
        """Set status with validation."""
        if TemplateStatus.is_valid(status):
            self.status = status
        else:
            raise ValueError(f"Invalid status: {status}. Must be one of {TemplateStatus.values()}")


class Misconception(Base):
    """
    Normalized misconceptions that can be referenced across templates.
    
    Central repository of common misconceptions to avoid duplication
    and enable analytics.
    """
    __tablename__ = "misconceptions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True, comment="Unique misconception code")
    title = Column(String(255), nullable=False, comment="Brief misconception title")
    description = Column(Text, nullable=False, comment="Detailed explanation of misconception")
    teaching_point = Column(Text, nullable=False, comment="How to correct this misconception")
    subject = Column(String(50), nullable=False, comment="Subject area (math, science, etc.)")
    concept_tags = Column(JSON, comment="Related concept IDs for targeting")
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    template_references = relationship("TemplateOptionMisconception", back_populates="misconception")
    
    def __repr__(self):
        return f"<Misconception(code='{self.code}', title='{self.title}')>"


class TemplateOptionMisconception(Base):
    """
    Links templates to misconceptions for specific answer options.
    
    Associates each incorrect option in a template with a specific misconception
    that the option targets, enabling targeted teaching when students select it.
    """
    __tablename__ = "template_option_misconceptions"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("question_templates.id"), nullable=False)
    misconception_id = Column(Integer, ForeignKey("misconceptions.id"), nullable=False)
    option_index = Column(Integer, nullable=False, comment="0-based index of the option")
    custom_explanation = Column(Text, comment="Template-specific explanation if needed")
    
    # Relationships
    template = relationship("QuestionTemplate", back_populates="misconceptions")
    misconception = relationship("Misconception", back_populates="template_references")
    
    def __repr__(self):
        return f"<TemplateOptionMisconception(template_id={self.template_id}, option_index={self.option_index})>"


class TemplateDiagram(Base):
    """
    Diagram metadata and rendering information for templates.
    
    Stores information about diagrams that can be referenced in templates,
    with support for both pre-rendered and dynamic generation.
    """
    __tablename__ = "template_diagrams"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("question_templates.id"), nullable=False)
    diagram_type = Column(String(50), nullable=False, comment="Type: static, dynamic, svg, png, etc.")
    name = Column(String(255), nullable=False, comment="Diagram identifier for template reference")
    
    # Rendering information
    render_pattern = Column(Text, comment="Pattern for dynamic rendering if applicable")
    variables = Column(JSON, comment="Variables used in diagram generation")
    
    # CDN/storage information
    cdn_url_base = Column(String(500), comment="Base URL for CDN access")
    file_path = Column(String(500), comment="Storage path for static diagrams")
    width = Column(Integer, comment="Diagram width in pixels")
    height = Column(Integer, comment="Diagram height in pixels")
    
    # Metadata
    alt_text = Column(Text, comment="Accessibility description")
    caption = Column(Text, comment="Diagram caption")
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    template = relationship("QuestionTemplate", back_populates="diagrams")
    
    def __repr__(self):
        return f"<TemplateDiagram(name='{self.name}', type='{self.diagram_type}')>"
