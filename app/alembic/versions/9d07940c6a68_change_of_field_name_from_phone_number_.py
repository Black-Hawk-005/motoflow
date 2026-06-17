"""Change of field name from phone_number to phone in Users table

Revision ID: 9d07940c6a68
Revises: efa617217c2f
Create Date: 2026-06-17 19:53:09.556960

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9d07940c6a68'
down_revision: Union[str, Sequence[str], None] = 'efa617217c2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'phone_number', new_column_name='phone')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'phone', new_column_name='phone_number')
