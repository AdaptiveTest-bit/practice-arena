"""merge template schema migrations

Revision ID: bd41af0f9c0f
Revises: 9aa8a735074b, a1b2c3d4e5f6
Create Date: 2026-01-14 17:43:49.512465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd41af0f9c0f'
down_revision: Union[str, None] = ('9aa8a735074b', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
