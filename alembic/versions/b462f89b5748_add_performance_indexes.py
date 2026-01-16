"""add performance indexes

Revision ID: b462f89b5748
Revises: e2f3g4h5i6j7
Create Date: 2026-01-17 01:53:33.176857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b462f89b5748'
down_revision: Union[str, Sequence[str], None] = 'e2f3g4h5i6j7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Documents: Optimized for feed filtering and user profile views
    op.create_index('ix_documents_user_visibility_deleted', 'documents', ['user_id', 'visibility', 'is_deleted'])
    
    # 2. Likes: Optimized for "Is Liked" checks and count aggregations
    # Note: UniqueConstraint already exists, but a composite index can help with specific query plans
    op.create_index('ix_likes_composite', 'likes', ['user_id', 'document_id'])
    
    # 3. Bookmarks: Optimized for "Is Bookmarked" checks
    op.create_index('ix_bookmarks_composite', 'bookmarks', ['user_id', 'document_id'])
    
    # 4. Follows: Optimized for "Am I Following" checks
    op.create_index('ix_follows_composite', 'follows', ['follower_id', 'following_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_follows_composite', table_name='follows')
    op.drop_index('ix_bookmarks_composite', table_name='bookmarks')
    op.drop_index('ix_likes_composite', table_name='likes')
    op.drop_index('ix_documents_user_visibility_deleted', table_name='documents')
