"""add source_asset_id to assets

Revision ID: d4b8e7f21a33
Revises: a7f3c9e2b451
Create Date: 2026-07-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd4b8e7f21a33'
down_revision = 'a7f3c9e2b451'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nullable, no default - existing rows are unaffected. Only used
    # when a video/thumbnail/etc. asset is generated "from" an existing
    # script asset (Scripts -> Make Video feature).
    op.add_column(
        'assets',
        sa.Column('source_asset_id', sa.String(), nullable=True),
    )
    op.create_foreign_key(
        'fk_assets_source_asset_id',
        'assets',
        'assets',
        ['source_asset_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_assets_source_asset_id', 'assets', type_='foreignkey')
    op.drop_column('assets', 'source_asset_id')
