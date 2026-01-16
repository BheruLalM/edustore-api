"""add likes and bookmark tables

Revision ID: 877c32e852ec
Revises: 124c66072fdf
Create Date: 2025-12-28 09:41:31.166728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '877c32e852ec'
down_revision: Union[str, Sequence[str], None] = '124c66072fdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'bookmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id',
            'document_id',
            name='uq_user_document_bookmark',
        ),
    )

    op.create_index('ix_bookmarks_user_id', 'bookmarks', ['user_id'])
    op.create_index('ix_bookmarks_document_id', 'bookmarks', ['document_id'])

    op.create_table(
        'likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id',
            'document_id',
            name='uq_user_document_like',
        ),
    )

    op.create_index('ix_likes_user_id', 'likes', ['user_id'])
    op.create_index('ix_likes_document_id', 'likes', ['document_id'])



def downgrade() -> None:
    op.drop_index('ix_likes_document_id', table_name='likes')
    op.drop_index('ix_likes_user_id', table_name='likes')
    op.drop_table('likes')

    op.drop_index('ix_bookmarks_document_id', table_name='bookmarks')
    op.drop_index('ix_bookmarks_user_id', table_name='bookmarks')
    op.drop_table('bookmarks')

