"""add documents table with production-grade defaults

Revision ID: 2784fc090fc4
Revises: b02a83e39edb
Create Date: 2025-12-26 19:01:39.342678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2784fc090fc4'
down_revision: Union[str, Sequence[str], None] = 'b02a83e39edb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 🔧 ENUM definition
document_visibility_enum = postgresql.ENUM(
    'private',
    'public',
    name='document_visibility'
)


def upgrade() -> None:
    """Upgrade schema."""
    # 1️ CREATE ENUM TYPE FIRST
    document_visibility_enum.create(op.get_bind(), checkfirst=True)

    # 2️ ADD COLUMNS
    op.add_column(
        'documents',
        sa.Column('object_key', sa.String(length=500), nullable=False)
    )
    op.add_column(
        'documents',
        sa.Column('original_filename', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'documents',
        sa.Column('content_type', sa.String(length=100), nullable=True)
    )
    op.add_column(
        'documents',
        sa.Column('file_size', sa.BigInteger(), nullable=True)
    )

    # 🔧 visibility with temporary server_default
    op.add_column(
        'documents',
        sa.Column(
            'visibility',
            document_visibility_enum,
            nullable=False,
            server_default='private'
        )
    )
    # remove default immediately after migration
    op.alter_column('documents', 'visibility', server_default=None)

    # 🔧 is_deleted with temporary server_default
    op.add_column(
        'documents',
        sa.Column(
            'is_deleted',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )
    op.alter_column('documents', 'is_deleted', server_default=None)

    # 3️ Update created_at column type if needed
    op.alter_column('documents', 'created_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=True,
                    existing_server_default=sa.text('now()'))

    # 4️ Drop old index if exists
    op.drop_index(op.f('ix_documents_id'), table_name='documents')

    # 5️ Create new indexes
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
    op.create_index(op.f('ix_documents_visibility'), 'documents', ['visibility'], unique=False)

    # 6️ Create unique constraint
    op.create_unique_constraint(None, 'documents', ['object_key'])

    # 7️ Drop old column
    op.drop_column('documents', 'doc_url')


def downgrade() -> None:
    """Downgrade schema."""
    # 1️ Add old column back
    op.add_column(
        'documents',
        sa.Column('doc_url', sa.VARCHAR(), autoincrement=False, nullable=False)
    )

    # 2️ Drop constraints & indexes
    op.drop_constraint(None, 'documents', type_='unique')
    op.drop_index(op.f('ix_documents_visibility'), table_name='documents')
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)

    # 3️ Revert created_at column type
    op.alter_column('documents', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=postgresql.TIMESTAMP(timezone=True),
                    existing_nullable=True,
                    existing_server_default=sa.text('now()'))

    # 4️ Drop newly added columns
    op.drop_column('documents', 'is_deleted')
    op.drop_column('documents', 'visibility')
    op.drop_column('documents', 'file_size')
    op.drop_column('documents', 'content_type')
    op.drop_column('documents', 'original_filename')
    op.drop_column('documents', 'object_key')

    # 5️ DROP ENUM TYPE LAST
    document_visibility_enum.drop(op.get_bind(), checkfirst=True)
