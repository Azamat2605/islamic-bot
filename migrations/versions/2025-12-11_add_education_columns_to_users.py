"""add education columns to users

Revision ID: f53f56289e57
Revises: 84d148710529
Create Date: 2025-12-11 10:16:32.087436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f53f56289e57'
down_revision: Union[str, None] = '84d148710529'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем столбцы для обучения в таблицу users
    op.add_column('users', sa.Column('education_level', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('total_courses_completed', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('total_tests_passed', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('learning_streak_days', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('last_learning_activity', sa.DateTime(), nullable=True))
    
    # Добавляем столбцы для уведомлений об обучении в таблицу settings (если их нет)
    op.add_column('settings', sa.Column('notify_course_reminders', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('notify_test_results', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('notify_new_courses', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('daily_learning_goal_minutes', sa.Integer(), server_default='30', nullable=False))
    op.add_column('settings', sa.Column('preferred_learning_time', sa.String(length=50), nullable=True))
    op.add_column('settings', sa.Column('auto_continue_courses', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    # Удаляем добавленные столбцы
    op.drop_column('users', 'education_level')
    op.drop_column('users', 'total_courses_completed')
    op.drop_column('users', 'total_tests_passed')
    op.drop_column('users', 'learning_streak_days')
    op.drop_column('users', 'last_learning_activity')
    
    op.drop_column('settings', 'notify_course_reminders')
    op.drop_column('settings', 'notify_test_results')
    op.drop_column('settings', 'notify_new_courses')
    op.drop_column('settings', 'daily_learning_goal_minutes')
    op.drop_column('settings', 'preferred_learning_time')
    op.drop_column('settings', 'auto_continue_courses')
