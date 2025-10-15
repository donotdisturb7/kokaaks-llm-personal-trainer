"""add_rag_tables_and_vector_extension

Revision ID: 0a2f121dc56d
Revises: c433b61fb4de
Create Date: 2025-10-14 11:32:49.131547

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '0a2f121dc56d'
down_revision = 'c433b61fb4de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension (already enabled manually)
    # op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create rag_documents table
    op.create_table(
        'rag_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('doc_type', sa.String(length=50), nullable=True),
        sa.Column('topics', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('safety', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_rag_docs_title', 'rag_documents', ['title'], unique=False)
    op.create_index('idx_rag_docs_type', 'rag_documents', ['doc_type'], unique=False)

    # Create rag_document_chunks table
    op.create_table(
        'rag_document_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_metadata', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['rag_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_rag_chunks_doc_idx', 'rag_document_chunks', ['document_id', 'chunk_index'], unique=False)
    # Create vector index for similarity search
    op.execute('CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding ON rag_document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);')


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS idx_rag_chunks_embedding;')
    op.drop_index('idx_rag_chunks_doc_idx', table_name='rag_document_chunks')
    op.drop_table('rag_document_chunks')
    op.drop_index('idx_rag_docs_type', table_name='rag_documents')
    op.drop_index('idx_rag_docs_title', table_name='rag_documents')
    op.drop_table('rag_documents')

