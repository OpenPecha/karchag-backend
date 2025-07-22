"""add_publication_status_to_kagyur_news

Revision ID: 4be6ae6a9dfb
Revises: c27e5378e7d8
Create Date: 2025-07-03 10:41:37.333239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4be6ae6a9dfb'
down_revision: Union[str, Sequence[str], None] = 'c27e5378e7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the publication status enum if it doesn't exist
    publication_status_enum = sa.Enum('draft', 'published', 'unpublished', name='publicationstatus')
    try:
        publication_status_enum.create(op.get_bind())
    except Exception:
        # Enum already exists, continue
        pass
    
    # Add publication_status column to kagyur_news table
    op.add_column('kagyur_news', sa.Column('publication_status', sa.Enum('draft', 'published', 'unpublished', name='publicationstatus'), nullable=True))
    
    # Set default value for existing records
    op.execute("UPDATE kagyur_news SET publication_status = 'published' WHERE published_date IS NOT NULL")
    op.execute("UPDATE kagyur_news SET publication_status = 'draft' WHERE published_date IS NULL")
    
    # Make the column not nullable after setting default values
    op.alter_column('kagyur_news', 'publication_status', nullable=False)
    
    # Make published_date nullable (it was not nullable before)
    op.alter_column('kagyur_news', 'published_date', nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove publication_status column
    op.drop_column('kagyur_news', 'publication_status')
    
    # Drop the enum
    publication_status_enum = sa.Enum('draft', 'published', 'unpublished', name='publicationstatus')
    publication_status_enum.drop(op.get_bind())
    
    # Make published_date not nullable again
    op.alter_column('kagyur_news', 'published_date', nullable=False)
