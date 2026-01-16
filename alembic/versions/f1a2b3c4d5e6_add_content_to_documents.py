"""add content to documents

Revision ID: f1a2b3c4d5e6
Revises: a5f4a7340681
Create Date: 2026-01-17 01:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'a5f4a7340681'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('documents', sa.Column('content', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('documents', 'content')
