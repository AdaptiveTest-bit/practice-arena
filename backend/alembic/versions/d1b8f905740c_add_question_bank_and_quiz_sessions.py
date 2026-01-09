"""add question bank and quiz sessions

Revision ID: d1b8f905740c
Revises:
Create Date: 2026-01-02 00:36:14.750575

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd1b8f905740c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'question_bank_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('chapter', sa.String(length=100), nullable=False),
        sa.Column('concept', sa.String(length=100), nullable=False),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.Column('bloom_level', sa.String(length=20), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'idx_qbank_lookup',
        'question_bank_items',
        ['chapter', 'concept', 'difficulty', 'bloom_level', 'active'],
        unique=False,
    )
    op.create_index(op.f('ix_question_bank_items_active'), 'question_bank_items', ['active'], unique=False)
    op.create_index(op.f('ix_question_bank_items_bloom_level'), 'question_bank_items', ['bloom_level'], unique=False)
    op.create_index(op.f('ix_question_bank_items_chapter'), 'question_bank_items', ['chapter'], unique=False)
    op.create_index(op.f('ix_question_bank_items_concept'), 'question_bank_items', ['concept'], unique=False)
    op.create_index(op.f('ix_question_bank_items_created_at'), 'question_bank_items', ['created_at'], unique=False)
    op.create_index(op.f('ix_question_bank_items_difficulty'), 'question_bank_items', ['difficulty'], unique=False)

    op.create_table(
        'quiz_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.String(length=64), nullable=False),
        sa.Column('grade_level', sa.Integer(), nullable=False),
        sa.Column('mode', sa.String(length=20), nullable=False),
        sa.Column('chapter', sa.String(length=100), nullable=False),
        sa.Column('attempted_count', sa.Integer(), nullable=False),
        sa.Column('correct_count', sa.Integer(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False),
        sa.Column('chapter_transitions', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_quiz_sessions_student_active', 'quiz_sessions', ['student_id', 'is_active'], unique=False)
    op.create_index(op.f('ix_quiz_sessions_created_at'), 'quiz_sessions', ['created_at'], unique=False)
    op.create_index(op.f('ix_quiz_sessions_ended_at'), 'quiz_sessions', ['ended_at'], unique=False)
    op.create_index(op.f('ix_quiz_sessions_is_active'), 'quiz_sessions', ['is_active'], unique=False)
    op.create_index(op.f('ix_quiz_sessions_student_id'), 'quiz_sessions', ['student_id'], unique=False)

    op.create_table(
        'served_questions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.String(length=64), nullable=False),
        sa.Column('question_bank_item_id', sa.String(length=36), nullable=False),
        sa.Column('served_at', sa.DateTime(), nullable=False),
        sa.Column('answered_at', sa.DateTime(), nullable=True),
        sa.Column('selected_index', sa.Integer(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['question_bank_item_id'], ['question_bank_items.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_served_session_student', 'served_questions', ['session_id', 'student_id'], unique=False)
    op.create_index(op.f('ix_served_questions_answered_at'), 'served_questions', ['answered_at'], unique=False)
    op.create_index(op.f('ix_served_questions_question_bank_item_id'), 'served_questions', ['question_bank_item_id'], unique=False)
    op.create_index(op.f('ix_served_questions_served_at'), 'served_questions', ['served_at'], unique=False)
    op.create_index(op.f('ix_served_questions_session_id'), 'served_questions', ['session_id'], unique=False)
    op.create_index(op.f('ix_served_questions_student_id'), 'served_questions', ['student_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_served_questions_student_id'), table_name='served_questions')
    op.drop_index(op.f('ix_served_questions_session_id'), table_name='served_questions')
    op.drop_index(op.f('ix_served_questions_served_at'), table_name='served_questions')
    op.drop_index(op.f('ix_served_questions_question_bank_item_id'), table_name='served_questions')
    op.drop_index(op.f('ix_served_questions_answered_at'), table_name='served_questions')
    op.drop_index('idx_served_session_student', table_name='served_questions')
    op.drop_table('served_questions')

    op.drop_index(op.f('ix_quiz_sessions_student_id'), table_name='quiz_sessions')
    op.drop_index(op.f('ix_quiz_sessions_is_active'), table_name='quiz_sessions')
    op.drop_index(op.f('ix_quiz_sessions_ended_at'), table_name='quiz_sessions')
    op.drop_index(op.f('ix_quiz_sessions_created_at'), table_name='quiz_sessions')
    op.drop_index('idx_quiz_sessions_student_active', table_name='quiz_sessions')
    op.drop_table('quiz_sessions')

    op.drop_index(op.f('ix_question_bank_items_difficulty'), table_name='question_bank_items')
    op.drop_index(op.f('ix_question_bank_items_created_at'), table_name='question_bank_items')
    op.drop_index(op.f('ix_question_bank_items_concept'), table_name='question_bank_items')
    op.drop_index(op.f('ix_question_bank_items_chapter'), table_name='question_bank_items')
    op.drop_index(op.f('ix_question_bank_items_bloom_level'), table_name='question_bank_items')
    op.drop_index(op.f('ix_question_bank_items_active'), table_name='question_bank_items')
    op.drop_index('idx_qbank_lookup', table_name='question_bank_items')
    op.drop_table('question_bank_items')
