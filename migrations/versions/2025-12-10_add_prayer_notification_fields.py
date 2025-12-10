"""add_prayer_notification_fields

Revision ID: add_prayer_notification_fields
Revises: update_unsupported_languages
Create Date: 2025-12-10 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_prayer_notification_fields'
down_revision = 'update_unsupported_languages'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поля для уведомлений о намазах
    op.add_column('settings', sa.Column('notify_fajr', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('notify_dhuhr', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('notify_asr', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('notify_maghrib', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('notify_isha', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('madhab', sa.String(), server_default='Hanafi', nullable=False))
    
    # Обновляем существующие записи: если prayer_notifications_on = true, то все уведомления true
    op.execute("""
        UPDATE settings 
        SET notify_fajr = prayer_notifications_on,
            notify_dhuhr = prayer_notifications_on,
            notify_asr = prayer_notifications_on,
            notify_maghrib = prayer_notifications_on,
            notify_isha = prayer_notifications_on
    """)


def downgrade() -> None:
    # Удаляем добавленные колонки
    op.drop_column('settings', 'madhab')
    op.drop_column('settings', 'notify_isha')
    op.drop_column('settings', 'notify_maghrib')
    op.drop_column('settings', 'notify_asr')
    op.drop_column('settings', 'notify_dhuhr')
    op.drop_column('settings', 'notify_fajr')
