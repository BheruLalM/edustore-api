"""Make comment content nullable for GDPR-friendly soft delete

Revision ID: c1d2e3f4g5h6
Revises: 89d48cac96aa
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1d2e3f4g5h6'
down_revision = '89d48cac96aa'  # Updated to current head
branch_labels = None
depends_on = None


def upgrade():
    # Make content column nullable
    op.alter_column('comments', 'content',
               existing_type=sa.Text(),
               nullable=True)


def downgrade():
    # Revert to non-nullable (requires handling NULL values first)
    op.execute("UPDATE comments SET content = '[deleted]' WHERE content IS NULL")
    op.alter_column('comments', 'content',
               existing_type=sa.Text(),
               nullable=False)
