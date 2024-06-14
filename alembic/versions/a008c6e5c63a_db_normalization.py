"""db normalization

Revision ID: a008c6e5c63a
Revises: 26f7e104e60b
Create Date: 2024-06-14 10:33:22.425896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a008c6e5c63a'
down_revision: Union[str, None] = '26f7e104e60b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Rename top_articles to articles
    op.rename_table('top_articles', 'articles')

    # Transfer all entries from best_articles to articles
    connection = op.get_bind()
    connection.execute(sa.text("""
      INSERT INTO articles (
          deleted, type, by, time, text, dead, parent, poll, kids, url, score, title, parts, 
          descendants, content_summary, keywords, created_at, updated_at
      )
      SELECT 
          deleted, type, by, time, text, dead, parent, poll, kids, url, score, title, parts, 
          descendants, content_summary, keywords, created_at, updated_at
      FROM best_articles
    """))

def downgrade():
    op.rename_table('articles', 'top_articles')
    
    connection = op.get_bind()
    connection.execute(sa.text("""
      DELETE FROM articles
      WHERE id IN (
        SELECT id FROM best_articles
      )
    """))
