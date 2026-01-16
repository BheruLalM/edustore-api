"""make object_key nullable

Revision ID: e2f3g4h5i6j7
Revises: f1a2b3c4d5e6
Create Date: 2026-01-17 01:48:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2f3g4h5i6j7'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('documents', 'object_key',
               existing_type=sa.String(length=500),
               nullable=True)


def downgrade() -> None:
    # Caution: this might fail if there are existing nulls
    op.alter_column('documents', 'object_key',
               existing_type=sa.String(length=500),
               nullable=False)
