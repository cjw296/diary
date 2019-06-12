"""initial

Revision ID: 192907bbbed1
Revises: 
Create Date: 2019-05-16 08:27:06.878004

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '192907bbbed1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('type', postgresql.ENUM('event', 'done', 'cancelled', 'postponed', name='types_enum'), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('entry')
