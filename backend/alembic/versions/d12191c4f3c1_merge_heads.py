"""merge heads

Revision ID: d12191c4f3c1
Revises: 93dc8a98b882, c2d8f4a6b901
Create Date: 2026-07-21 19:26:41.218551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd12191c4f3c1'
down_revision = ('93dc8a98b882', 'c2d8f4a6b901')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass