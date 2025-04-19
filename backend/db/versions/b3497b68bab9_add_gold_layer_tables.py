"""add gold layer tables

Revision ID: b3497b68bab9
Revises: 5b6c01cd5a71
Create Date: 2025-04-17 15:09:34.455615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3497b68bab9'
down_revision: Union[str, None] = '5b6c01cd5a71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
