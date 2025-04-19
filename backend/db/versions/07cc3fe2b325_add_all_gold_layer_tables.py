"""add all gold layer tables

Revision ID: 07cc3fe2b325
Revises: 9737521d77e6
Create Date: 2025-04-17 15:29:29.363677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07cc3fe2b325'
down_revision: Union[str, None] = '9737521d77e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
