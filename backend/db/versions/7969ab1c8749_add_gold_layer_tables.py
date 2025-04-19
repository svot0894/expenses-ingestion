"""add gold layer tables

Revision ID: 7969ab1c8749
Revises: b3497b68bab9
Create Date: 2025-04-17 15:12:17.730474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7969ab1c8749'
down_revision: Union[str, None] = 'b3497b68bab9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
