"""add_publication_status_to_kangyur_video

Revision ID: df155954f118
Revises: 4be6ae6a9dfb
Create Date: 2024-07-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'df155954f118'
down_revision = '4be6ae6a9dfb'
branch_labels = None
depends_on = None

def upgrade():
    # Add publication_status column to kangyur_video table
    op.add_column('kangyur_video', sa.Column('publication_status', sa.String(), nullable=True))
    
    # Set default values based on existing data
    op.execute("UPDATE kangyur_video SET publication_status = 'published' WHERE published_date IS NOT NULL")
    op.execute("UPDATE kangyur_video SET publication_status = 'draft' WHERE published_date IS NULL")
    
    # Make column non-nullable with default
    op.alter_column('kangyur_video', 'publication_status', nullable=False, server_default='draft')

def downgrade():
    # Remove publication_status column
    op.drop_column('kangyur_video', 'publication_status')
