"""add comments table

Revision ID: 124c66072fdf
Revises: 6449282fafe6
Create Date: 2025-12-27 18:38:27.800862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '124c66072fdf'
down_revision: Union[str, Sequence[str], None] = '6449282fafe6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            onupdate=sa.text('now()'),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index(op.f('ix_comments_document_id'), 'comments', ['document_id'])
    op.create_index(op.f('ix_comments_user_id'), 'comments', ['user_id'])
    op.create_index(op.f('ix_comments_parent_id'), 'comments', ['parent_id'])
    op.create_index(
        'ix_comments_document_created',
        'comments',
        ['document_id', 'created_at'],
    )



def downgrade() -> None:
    op.drop_index('ix_comments_document_created', table_name='comments')
    op.drop_index(op.f('ix_comments_parent_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_user_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_document_id'), table_name='comments')
    op.drop_table('comments')
