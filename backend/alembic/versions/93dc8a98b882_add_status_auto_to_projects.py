"""add status_auto to projects

Revision ID: 93dc8a98b882
Revises: a7f3c9e2b451
Create Date: 2026-07-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '93dc8a98b882'
down_revision = 'a7f3c9e2b451'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'projects',
        sa.Column(
            'status_auto',
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column('projects', 'status_auto')
