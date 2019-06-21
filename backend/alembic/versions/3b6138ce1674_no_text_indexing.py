"""no_text_indexing

Revision ID: 3b6138ce1674
Revises: b871b611f14a
Create Date: 2019-06-21 07:27:20.790262

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
from sqlalchemy_searchable import drop_trigger

revision = '3b6138ce1674'
down_revision = 'b871b611f14a'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    drop_trigger(
        conn,
        'entry',
        'search_vector',
    )
    op.drop_index('ix_entry_search_vector', table_name='entry')
    op.drop_column('entry', 'search_vector')


def downgrade():
    op.add_column('entry', sa.Column('search_vector', postgresql.TSVECTOR(), autoincrement=False, nullable=True))
    op.create_index('ix_entry_search_vector', 'entry', ['search_vector'], unique=False)
