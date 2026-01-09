"""add concept taxonomy and events

Revision ID: 9b0f0d3b1a21
Revises: d1b8f905740c
Create Date: 2026-01-02

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9b0f0d3b1a21"
down_revision: Union[str, None] = "d1b8f905740c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # Concept taxonomy
    # -------------------------------------------------------------------------
    op.create_table(
        "concept_catalog",
        sa.Column("concept_id", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.String(length=32), nullable=False),
        sa.Column("grade_level", sa.Integer(), nullable=False),
        sa.Column("chapter_key", sa.String(length=100), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("concept_id"),
    )
    op.create_index(
        "idx_concept_catalog_chapter_order",
        "concept_catalog",
        ["chapter_key", "order_index"],
        unique=False,
    )
    op.create_index(op.f("ix_concept_catalog_active"), "concept_catalog", ["active"], unique=False)
    op.create_index(op.f("ix_concept_catalog_chapter_key"), "concept_catalog", ["chapter_key"], unique=False)
    op.create_index(op.f("ix_concept_catalog_created_at"), "concept_catalog", ["created_at"], unique=False)
    op.create_index(op.f("ix_concept_catalog_grade_level"), "concept_catalog", ["grade_level"], unique=False)
    op.create_index(op.f("ix_concept_catalog_order_index"), "concept_catalog", ["order_index"], unique=False)
    op.create_index(op.f("ix_concept_catalog_subject"), "concept_catalog", ["subject"], unique=False)

    # -------------------------------------------------------------------------
    # Student concept state (Leitner)
    # -------------------------------------------------------------------------
    op.create_table(
        "student_concept_state",
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("concept_id", sa.String(length=64), nullable=False),
        sa.Column("leitner_box", sa.Integer(), nullable=False),
        sa.Column("due_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("last_bloom_served", sa.String(length=20), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("student_id", "concept_id"),
    )
    op.create_index("idx_student_concept_due", "student_concept_state", ["student_id", "due_at"], unique=False)
    op.create_index("idx_student_concept_box", "student_concept_state", ["student_id", "leitner_box"], unique=False)
    op.create_index(op.f("ix_student_concept_state_due_at"), "student_concept_state", ["due_at"], unique=False)
    op.create_index(op.f("ix_student_concept_state_last_seen_at"), "student_concept_state", ["last_seen_at"], unique=False)
    op.create_index(op.f("ix_student_concept_state_leitner_box"), "student_concept_state", ["leitner_box"], unique=False)
    op.create_index(op.f("ix_student_concept_state_updated_at"), "student_concept_state", ["updated_at"], unique=False)

    # -------------------------------------------------------------------------
    # Student breakpoints
    # -------------------------------------------------------------------------
    op.create_table(
        "student_breakpoints",
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("concept_id", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=False),
        sa.Column("wrong_streak", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("student_id", "concept_id"),
    )
    op.create_index(
        "idx_breakpoints_student_active",
        "student_breakpoints",
        ["student_id", "active"],
        unique=False,
    )
    op.create_index(op.f("ix_student_breakpoints_active"), "student_breakpoints", ["active"], unique=False)
    op.create_index(op.f("ix_student_breakpoints_last_triggered_at"), "student_breakpoints", ["last_triggered_at"], unique=False)
    op.create_index(op.f("ix_student_breakpoints_severity"), "student_breakpoints", ["severity"], unique=False)
    op.create_index(op.f("ix_student_breakpoints_updated_at"), "student_breakpoints", ["updated_at"], unique=False)

    # -------------------------------------------------------------------------
    # Learning events
    # -------------------------------------------------------------------------
    op.create_table(
        "learning_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("subject", sa.String(length=32), nullable=True),
        sa.Column("chapter_key", sa.String(length=100), nullable=True),
        sa.Column("concept_id", sa.String(length=64), nullable=True),
        sa.Column("bloom_level", sa.String(length=20), nullable=True),
        sa.Column("difficulty", sa.String(length=20), nullable=True),
        sa.Column("served_question_id", sa.String(length=36), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_events_student_time", "learning_events", ["student_id", "timestamp"], unique=False)
    op.create_index(op.f("ix_learning_events_chapter_key"), "learning_events", ["chapter_key"], unique=False)
    op.create_index(op.f("ix_learning_events_concept_id"), "learning_events", ["concept_id"], unique=False)
    op.create_index(op.f("ix_learning_events_event_type"), "learning_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_learning_events_served_question_id"), "learning_events", ["served_question_id"], unique=False)
    op.create_index(op.f("ix_learning_events_session_id"), "learning_events", ["session_id"], unique=False)
    op.create_index(op.f("ix_learning_events_student_id"), "learning_events", ["student_id"], unique=False)
    op.create_index(op.f("ix_learning_events_subject"), "learning_events", ["subject"], unique=False)
    op.create_index(op.f("ix_learning_events_timestamp"), "learning_events", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_learning_events_timestamp"), table_name="learning_events")
    op.drop_index(op.f("ix_learning_events_subject"), table_name="learning_events")
    op.drop_index(op.f("ix_learning_events_student_id"), table_name="learning_events")
    op.drop_index(op.f("ix_learning_events_session_id"), table_name="learning_events")
    op.drop_index(op.f("ix_learning_events_served_question_id"), table_name="learning_events")
    op.drop_index(op.f("ix_learning_events_event_type"), table_name="learning_events")
    op.drop_index(op.f("ix_learning_events_concept_id"), table_name="learning_events")
    op.drop_index(op.f("ix_learning_events_chapter_key"), table_name="learning_events")
    op.drop_index("idx_events_student_time", table_name="learning_events")
    op.drop_table("learning_events")

    op.drop_index(op.f("ix_student_breakpoints_updated_at"), table_name="student_breakpoints")
    op.drop_index(op.f("ix_student_breakpoints_severity"), table_name="student_breakpoints")
    op.drop_index(op.f("ix_student_breakpoints_last_triggered_at"), table_name="student_breakpoints")
    op.drop_index(op.f("ix_student_breakpoints_active"), table_name="student_breakpoints")
    op.drop_index("idx_breakpoints_student_active", table_name="student_breakpoints")
    op.drop_table("student_breakpoints")

    op.drop_index(op.f("ix_student_concept_state_updated_at"), table_name="student_concept_state")
    op.drop_index(op.f("ix_student_concept_state_leitner_box"), table_name="student_concept_state")
    op.drop_index(op.f("ix_student_concept_state_last_seen_at"), table_name="student_concept_state")
    op.drop_index(op.f("ix_student_concept_state_due_at"), table_name="student_concept_state")
    op.drop_index("idx_student_concept_box", table_name="student_concept_state")
    op.drop_index("idx_student_concept_due", table_name="student_concept_state")
    op.drop_table("student_concept_state")

    op.drop_index(op.f("ix_concept_catalog_subject"), table_name="concept_catalog")
    op.drop_index(op.f("ix_concept_catalog_order_index"), table_name="concept_catalog")
    op.drop_index(op.f("ix_concept_catalog_grade_level"), table_name="concept_catalog")
    op.drop_index(op.f("ix_concept_catalog_created_at"), table_name="concept_catalog")
    op.drop_index(op.f("ix_concept_catalog_chapter_key"), table_name="concept_catalog")
    op.drop_index(op.f("ix_concept_catalog_active"), table_name="concept_catalog")
    op.drop_index("idx_concept_catalog_chapter_order", table_name="concept_catalog")
    op.drop_table("concept_catalog")
