"""managing timestamps

Revision ID: 73bb1091b2a8
Revises: f3578cff7884
Create Date: 2024-05-24 16:40:56.384199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73bb1091b2a8'
down_revision: Union[str, None] = 'f3578cff7884'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('best_articles', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True))
    op.add_column('best_articles', sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True))
    
    # (psycopg2.errors.CannotCoerce) cannot cast type bigint to timestamp with time zone
    # https://stackoverflow.com/questions/54193335/how-to-cast-bigint-to-timestamp-with-time-zone-in-postgres-in-an-update
    op.execute("""
        ALTER TABLE best_articles 
        ALTER COLUMN time 
        TYPE TIMESTAMP WITH TIME ZONE 
        USING TO_TIMESTAMP(time) AT TIME ZONE 'UTC'
    """)

def downgrade():
    op.drop_column('best_articles', 'created_at')
    op.drop_column('best_articles', 'updated_at')
    
    op.execute("""
        ALTER TABLE best_articles 
        ALTER COLUMN time 
        TYPE BIGINT 
        USING EXTRACT(epoch FROM time)::bigint
    """)
