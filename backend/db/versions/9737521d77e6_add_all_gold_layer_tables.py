"""add all gold layer tables

Revision ID: 9737521d77e6
Revises: 7969ab1c8749
Create Date: 2025-04-17 15:24:10.070368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9737521d77e6'
down_revision: Union[str, None] = '7969ab1c8749'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
