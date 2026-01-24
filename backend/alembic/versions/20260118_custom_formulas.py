"""add custom_formulas table

Revision ID: 20260118_formulas
Revises: 
Create Date: 2026-01-18

Creates the custom_formulas table for the Template Editor Gateway.
Content writers can create custom formulas without code changes.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260118_formulas'
down_revision = None  # Update this to point to your latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'custom_formulas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, 
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(200), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, server_default='General'),
        sa.Column('parameters', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('return_type', sa.String(50), nullable=False, server_default='any'),
        sa.Column('code', sa.Text, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('example_usage', sa.Text, nullable=True),
        sa.Column('test_cases', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('status', sa.String(20), nullable=False, server_default='DRAFT'),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create indexes
    op.create_index('ix_custom_formulas_name', 'custom_formulas', ['name'])
    op.create_index('ix_custom_formulas_status', 'custom_formulas', ['status'])
    op.create_index('ix_custom_formulas_category', 'custom_formulas', ['category'])


def downgrade() -> None:
    op.drop_index('ix_custom_formulas_category')
    op.drop_index('ix_custom_formulas_status')
    op.drop_index('ix_custom_formulas_name')
    op.drop_table('custom_formulas')
