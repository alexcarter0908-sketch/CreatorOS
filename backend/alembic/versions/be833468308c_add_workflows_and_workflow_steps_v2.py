"""add workflows and workflow_steps v2

Revision ID: be833468308c
Revises: f1a6f361aa74
Create Date: 2026-07-07 16:33:13.475782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be833468308c'
down_revision = 'f1a6f361aa74'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'workflows',
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_workflows_id'), 'workflows', ['id'], unique=True)
    op.create_index(op.f('ix_workflows_owner_id'), 'workflows', ['owner_id'], unique=False)
    op.create_index(op.f('ix_workflows_project_id'), 'workflows', ['project_id'], unique=False)
    op.create_index(op.f('ix_workflows_status'), 'workflows', ['status'], unique=False)

    op.create_table(
        'workflow_steps',
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('asset_type', sa.String(length=20), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_workflow_steps_id'), 'workflow_steps', ['id'], unique=True)
    op.create_index(op.f('ix_workflow_steps_workflow_id'), 'workflow_steps', ['workflow_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_workflow_steps_workflow_id'), table_name='workflow_steps')
    op.drop_index(op.f('ix_workflow_steps_id'), table_name='workflow_steps')
    op.drop_table('workflow_steps')
    op.drop_index(op.f('ix_workflows_status'), table_name='workflows')
    op.drop_index(op.f('ix_workflows_project_id'), table_name='workflows')
    op.drop_index(op.f('ix_workflows_owner_id'), table_name='workflows')
    op.drop_index(op.f('ix_workflows_id'), table_name='workflows')
    op.drop_table('workflows')
