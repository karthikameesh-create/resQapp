"""add_ai_processing_status

Revision ID: 4114599c45cc
Revises: 072c276c6ffa
Create Date: 2026-08-08 16:50:59.145564

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4114599c45cc"
down_revision: Union[str, Sequence[str], None] = "072c276c6ffa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "incidents",
        sa.Column(
            "ai_status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
    )

    # Remove the database-level default after existing rows
    # have been populated with "pending".
    op.alter_column(
        "incidents",
        "ai_status",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "incidents",
        "ai_status",
    )