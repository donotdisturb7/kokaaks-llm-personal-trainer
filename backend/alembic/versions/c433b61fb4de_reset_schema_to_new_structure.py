"""reset_schema_to_new_structure

Revision ID: c433b61fb4de
Revises: fe222be65e91
Create Date: 2025-10-14 08:37:53.008894

Supprime les anciennes tables user-centric et crée la nouvelle structure simplifiée:
- conversations (sans user_id)
- local_stats (statistiques locales uploadées)
- training_examples, datasets, dataset_examples (curation fine-tuning)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'c433b61fb4de'
down_revision = 'fe222be65e91'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Supprimer les anciennes tables dans le bon ordre (dépendances)
    op.drop_table('user_stats', if_exists=True)
    op.drop_table('user_preferences', if_exists=True)
    op.drop_table('training_sessions', if_exists=True)
    op.drop_table('conversations', if_exists=True)
    op.drop_table('users', if_exists=True)
    
    # 2. Créer la nouvelle table conversations (sans user_id)
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('messages', JSONB, nullable=False),
        sa.Column('context_used', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_created', 'conversations', ['created_at'])
    op.create_index('idx_messages', 'conversations', ['messages'], postgresql_using='gin', postgresql_ops={'messages': 'jsonb_ops'})
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    
    # 3. Créer la table local_stats
    op.create_table(
        'local_stats',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('scenario_name', sa.String(255), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('kills', sa.Integer(), nullable=True),
        sa.Column('avg_ttk', sa.Float(), nullable=True),
        sa.Column('sensitivity', sa.Float(), nullable=True),
        sa.Column('fov', sa.Integer(), nullable=True),
        sa.Column('cm360', sa.Float(), nullable=True),
        sa.Column('played_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_scenario', 'local_stats', ['scenario_name'])
    op.create_index('idx_played_at', 'local_stats', ['played_at'])
    op.create_index(op.f('ix_local_stats_id'), 'local_stats', ['id'], unique=False)
    op.create_index(op.f('ix_local_stats_scenario_name'), 'local_stats', ['scenario_name'], unique=False)
    
    # 4. Créer les tables de curation pour le fine-tuning
    op.create_table(
        'training_examples',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source', sa.String(20), nullable=False),
        sa.Column('input_text', sa.Text(), nullable=False),
        sa.Column('target_text', sa.Text(), nullable=False),
        sa.Column('meta', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("source IN ('conversation', 'csv', 'manual')", name='check_source'),
    )
    op.create_index('idx_training_source', 'training_examples', ['source'])
    op.create_index('idx_training_meta', 'training_examples', ['meta'], postgresql_using='gin', postgresql_ops={'meta': 'jsonb_ops'})
    op.create_index(op.f('ix_training_examples_id'), 'training_examples', ['id'], unique=False)
    
    op.create_table(
        'datasets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_datasets_id'), 'datasets', ['id'], unique=False)
    op.create_index(op.f('ix_datasets_name'), 'datasets', ['name'], unique=True)
    
    op.create_table(
        'dataset_examples',
        sa.Column('dataset_id', sa.Integer(), sa.ForeignKey('datasets.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('example_id', sa.Integer(), sa.ForeignKey('training_examples.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade() -> None:
    # Supprimer les nouvelles tables
    op.drop_table('dataset_examples')
    op.drop_table('datasets')
    op.drop_table('training_examples')
    op.drop_table('local_stats')
    op.drop_table('conversations')
    
    # Recréer les anciennes tables (si besoin de rollback)
    # Note: on ne recrée pas les anciennes tables par défaut, car elles sont obsolètes
    # Si vraiment nécessaire, copier le code de fe222be65e91_initial_schema.py

