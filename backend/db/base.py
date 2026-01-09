"""SQLAlchemy declarative base for all ORM models.

Single source of truth for metadata so Alembic can autogenerate migrations.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
