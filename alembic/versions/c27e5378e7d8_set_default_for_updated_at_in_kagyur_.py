"""Set default for updated_at in kagyur_news

Revision ID: c27e5378e7d8
Revises: 0591b3e02b59
Create Date: 2025-07-02 11:25:04.869586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c27e5378e7d8'
down_revision: Union[str, Sequence[str], None] = '0591b3e02b59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        'kagyur_news', 'updated_at',
        server_default=sa.text('now()'),
        existing_type=sa.DateTime(timezone=True)
    )

def downgrade():
    op.alter_column(
        'kagyur_news', 'updated_at',
        server_default=None,
        existing_type=sa.DateTime(timezone=True)
    )