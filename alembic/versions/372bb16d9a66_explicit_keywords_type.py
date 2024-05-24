"""explicit keywords type

Revision ID: 372bb16d9a66
Revises: 73bb1091b2a8
Create Date: 2024-05-24 17:55:35.041221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '372bb16d9a66'
down_revision: Union[str, None] = '73bb1091b2a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE best_articles
        ALTER COLUMN keywords TYPE VARCHAR[]
        USING keywords::VARCHAR[];
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE best_articles
        ALTER COLUMN keywords TYPE VARCHAR
        USING array_to_string(keywords, ', ')::VARCHAR;
    """)
