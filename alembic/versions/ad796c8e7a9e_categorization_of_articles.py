"""categorization of articles

Revision ID: ad796c8e7a9e
Revises: a008c6e5c63a
Create Date: 2024-06-14 11:14:49.825320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = 'ad796c8e7a9e'
down_revision: Union[str, None] = 'a008c6e5c63a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('articles', sa.Column('category', sa.Integer(), nullable=True))
    op.drop_table('best_articles')

def downgrade():
    op.drop_column('articles', 'category')
    op.create_table('best_articles')
