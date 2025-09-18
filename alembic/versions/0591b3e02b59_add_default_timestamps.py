"""add default timestamps

Revision ID: 0591b3e02b59
Revises: a46925cd8965
Create Date: 2025-07-02 11:11:36.947834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0591b3e02b59'
down_revision: Union[str, Sequence[str], None] = 'a46925cd8965'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Update existing NULL values
    op.execute("UPDATE kagyur_news SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE kagyur_news SET updated_at = NOW() WHERE updated_at IS NULL")
    
    # Apply the schema changes (if any)
    # Alembic should auto-detect your server_default changes

def downgrade():
    # Remove defaults if rolling back
    pass