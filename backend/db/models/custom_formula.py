"""
Custom Formula Model for Template Editor Gateway.

Allows content writers to create reusable formulas without code changes.
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum

from db.base import Base


class FormulaStatus(str, enum.Enum):
    """Status of a custom formula."""
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"


class FormulaCategory(str, enum.Enum):
    """Categories for organizing formulas."""
    NUMBER_THEORY = "Number Theory"
    FRACTIONS = "Fractions"
    GEOMETRY = "Geometry"
    ALGEBRA = "Algebra"
    STATISTICS = "Statistics"
    GENERAL = "General"


class CustomFormula(Base):
    """
    Custom formulas created by content team.
    
    These formulas become available in the template editor
    and can be used in computed variables.
    
    Example:
        name: "add_fractions"
        display_name: "Add Two Fractions"
        parameters: [
            {"name": "n1", "type": "integer", "description": "Numerator 1"},
            {"name": "d1", "type": "integer", "description": "Denominator 1"},
            {"name": "n2", "type": "integer", "description": "Numerator 2"},
            {"name": "d2", "type": "integer", "description": "Denominator 2"}
        ]
        return_type: "tuple"
        code: '''
            from math import gcd
            num = n1 * d2 + n2 * d1
            den = d1 * d2
            g = gcd(num, den)
            return (num // g, den // g)
        '''
    """
    
    __tablename__ = "custom_formulas"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identity
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, default=FormulaCategory.GENERAL.value)
    
    # Definition
    parameters = Column(JSONB, nullable=False, default=list)
    return_type = Column(String(50), nullable=False, default="any")
    code = Column(Text, nullable=False)
    
    # Documentation
    description = Column(Text)
    example_usage = Column(Text)
    
    # Validation
    test_cases = Column(JSONB, default=list)
    
    # Metadata
    status = Column(String(20), default=FormulaStatus.DRAFT.value, index=True)
    created_by = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CustomFormula(name='{self.name}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "category": self.category,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "code": self.code,
            "description": self.description,
            "example_usage": self.example_usage,
            "test_cases": self.test_cases,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_function_signature(self) -> str:
        """Generate function signature for documentation."""
        params = ", ".join([p["name"] for p in self.parameters])
        return f"{self.name}({params})"
