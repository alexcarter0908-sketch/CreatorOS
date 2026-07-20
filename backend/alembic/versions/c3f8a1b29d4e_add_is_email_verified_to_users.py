"""add is_email_verified to users

Revision ID: c3f8a1b29d4e
Revises: bf502524ddd8
Create Date: 2026-07-11 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3f8a1b29d4e'
down_revision = 'bf502524ddd8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'is_email_verified')
