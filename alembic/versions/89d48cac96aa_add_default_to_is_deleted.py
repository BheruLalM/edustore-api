"""add default to is_deleted

Revision ID: 89d48cac96aa
Revises: 877c32e852ec
Create Date: 2025-12-29 18:41:51.641259
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "89d48cac96aa"
down_revision: Union[str, Sequence[str], None] = "877c32e852ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # set default false on is_deleted
    op.alter_column(
        "documents",
        "is_deleted",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )


def downgrade() -> None:
    # remove default
    op.alter_column(
        "documents",
        "is_deleted",
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )
