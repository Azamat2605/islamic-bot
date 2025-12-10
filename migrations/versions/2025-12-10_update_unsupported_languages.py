"""update unsupported languages

Revision ID: update_unsupported_languages
Revises: 20241209_extend_settings_table
Create Date: 2025-12-10 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_unsupported_languages'
down_revision = '20241209_extend_settings_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Обновляем языки, которые больше не поддерживаются
    # Поддерживаемые языки: ru, en, ar, tt, ba
    # Неподдерживаемые: az, kk, ky, tk, tr, ug, uz
    op.execute("""
        UPDATE settings 
        SET language = 'ru' 
        WHERE language IN ('az', 'kk', 'ky', 'tk', 'tr', 'ug', 'uz')
    """)


def downgrade() -> None:
    # В downgrade мы не можем восстановить оригинальные языки,
    # так как они были заменены на 'ru'.
    # Оставляем пустым, так как это необратимое изменение.
    pass
