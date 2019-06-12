"""not nullable

Revision ID: cd5c889dd418
Revises: 192907bbbed1
Create Date: 2019-06-12 08:22:35.412890

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cd5c889dd418'
down_revision = '192907bbbed1'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('entry', 'date',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('entry', 'text',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('entry', 'type',
               existing_type=postgresql.ENUM('event', 'done', 'cancelled', 'postponed', name='types_enum'),
               nullable=False)


def downgrade():
    op.alter_column('entry', 'type',
               existing_type=postgresql.ENUM('event', 'done', 'cancelled', 'postponed', name='types_enum'),
               nullable=True)
    op.alter_column('entry', 'text',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('entry', 'date',
               existing_type=sa.DATE(),
               nullable=True)
