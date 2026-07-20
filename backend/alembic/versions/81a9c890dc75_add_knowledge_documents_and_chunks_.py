"""add knowledge documents and chunks tables

Revision ID: 81a9c890dc75
Revises: f5f761f85753
Create Date: 2026-07-09 17:43:33.772992

"""
from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision = '81a9c890dc75'
down_revision = 'f5f761f85753'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table(
        'knowledge_documents',
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('filename', sa.String(length=500), nullable=False),
        sa.Column('file_url', sa.String(length=1000), nullable=True),
        sa.Column('storage_path', sa.String(length=1000), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=False),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_knowledge_documents_id'), 'knowledge_documents', ['id'], unique=True)
    op.create_index(op.f('ix_knowledge_documents_owner_id'), 'knowledge_documents', ['owner_id'], unique=False)
    op.create_index(op.f('ix_knowledge_documents_project_id'), 'knowledge_documents', ['project_id'], unique=False)

    op.create_table(
        'knowledge_chunks',
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['knowledge_documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_knowledge_chunks_document_id'), 'knowledge_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_knowledge_chunks_id'), 'knowledge_chunks', ['id'], unique=True)
    op.create_index(op.f('ix_knowledge_chunks_owner_id'), 'knowledge_chunks', ['owner_id'], unique=False)
    op.create_index(op.f('ix_knowledge_chunks_project_id'), 'knowledge_chunks', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_knowledge_chunks_project_id'), table_name='knowledge_chunks')
    op.drop_index(op.f('ix_knowledge_chunks_owner_id'), table_name='knowledge_chunks')
    op.drop_index(op.f('ix_knowledge_chunks_id'), table_name='knowledge_chunks')
    op.drop_index(op.f('ix_knowledge_chunks_document_id'), table_name='knowledge_chunks')
    op.drop_table('knowledge_chunks')
    op.drop_index(op.f('ix_knowledge_documents_project_id'), table_name='knowledge_documents')
    op.drop_index(op.f('ix_knowledge_documents_owner_id'), table_name='knowledge_documents')
    op.drop_index(op.f('ix_knowledge_documents_id'), table_name='knowledge_documents')
    op.drop_table('knowledge_documents')
    op.execute('DROP EXTENSION IF EXISTS vector')
