"""add_template_id_to_question_bank

Revision ID: 4c5c17305393
Revises: 9b0f0d3b1a21
Create Date: 2026-01-02 03:13:51.005872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c5c17305393'
down_revision: Union[str, None] = '9b0f0d3b1a21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add template_id column for tracking question variations
    op.add_column(
        'question_bank_items',
        sa.Column('template_id', sa.String(64), nullable=True)
    )
    op.create_index(
        'idx_qbank_template_id',
        'question_bank_items',
        ['template_id']
    )


def downgrade() -> None:
    op.drop_index('idx_qbank_template_id', table_name='question_bank_items')
    op.drop_column('question_bank_items', 'template_id')
