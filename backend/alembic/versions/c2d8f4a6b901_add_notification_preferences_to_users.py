"""add notification preference columns to users

Revision ID: c2d8f4a6b901
Revises: b7f3c9a1d5e2
Create Date: 2026-07-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c2d8f4a6b901'
down_revision = 'b7f3c9a1d5e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('notify_email_digest', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('users', sa.Column('notify_low_credit_email', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('users', sa.Column('low_credit_alert_sent', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('users', 'low_credit_alert_sent')
    op.drop_column('users', 'notify_low_credit_email')
    op.drop_column('users', 'notify_email_digest')
