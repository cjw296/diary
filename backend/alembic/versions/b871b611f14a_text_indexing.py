"""text indexing

Revision ID: b871b611f14a
Revises: cd5c889dd418
Create Date: 2019-06-12 08:26:19.343617

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy_searchable import sync_trigger, drop_trigger

revision = 'b871b611f14a'
down_revision = 'cd5c889dd418'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('entry', sa.Column('search_vector', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))
    op.create_index('ix_entry_search_vector', 'entry', ['search_vector'], unique=False, postgresql_using='gin')
    conn = op.get_bind()
    sync_trigger(conn, 'entry', 'search_vector', ['text'])


def downgrade():
    conn = op.get_bind()
    drop_trigger(
        conn,
        'entry',
        'search_vector',
    )
    op.drop_index('ix_entry_search_vector', table_name='entry')
    op.drop_column('entry', 'search_vector')
