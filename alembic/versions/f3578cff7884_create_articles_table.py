"""create articles table

Revision ID: f3578cff7884
Revises: 
Create Date: 2024-05-24 16:01:26.865987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3578cff7884'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('best_articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('by', sa.String(length=255), nullable=True),
    sa.Column('time', sa.BigInteger(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('dead', sa.Boolean(), nullable=True),
    sa.Column('parent', sa.Integer(), nullable=True),
    sa.Column('poll', sa.Integer(), nullable=True),
    sa.Column('kids', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('parts', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('descendants', sa.Integer(), nullable=True),
    sa.Column('content_summary', sa.Text(), nullable=True),
    sa.Column('keywords', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_best_articles_id'), 'best_articles', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_best_articles_id'), table_name='best_articles')
    op.drop_table('best_articles')
    # ### end Alembic commands ###
