"""add auto_targets table

Revision ID: e9a4d9ab1281
Revises: a18bd66fc183
Create Date: 2026-07-06 17:48:02.015194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9a4d9ab1281'
down_revision = 'a18bd66fc183'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'auto_targets',
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('interval_days', sa.Integer(), nullable=False),
        sa.Column('run_at_hour', sa.Integer(), nullable=False),
        sa.Column('run_at_minute', sa.Integer(), nullable=False),
        sa.Column('last_run_date', sa.String(length=20), nullable=True),
        sa.Column('auto_publish', sa.Boolean(), nullable=False),
        sa.Column('platforms', sa.String(length=255), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_run_at', sa.String(length=50), nullable=True),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_auto_targets_id'), 'auto_targets', ['id'], unique=True)
    op.create_index(op.f('ix_auto_targets_owner_id'), 'auto_targets', ['owner_id'], unique=False)
    op.create_index(op.f('ix_auto_targets_project_id'), 'auto_targets', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_auto_targets_project_id'), table_name='auto_targets')
    op.drop_index(op.f('ix_auto_targets_owner_id'), table_name='auto_targets')
    op.drop_index(op.f('ix_auto_targets_id'), table_name='auto_targets')
    op.drop_table('auto_targets')
