from app.dependencies import get_db
from app.services.hn import get_article
from app.models import Article
from datetime import datetime, timedelta
import logging
import concurrent.futures
from sentry_sdk import start_transaction


def fetch_hn_article_score(article_id):
  try:
    hn_article = get_article(article_id)
    return hn_article['score']
  except Exception as e:
    logging.error(f"Error fetching score for article {article_id}: {str(e)}")
    return None

def update_article_scores(db_article, hn_score):
  if hn_score is not None and hn_score != db_article.score:
    return {'id': db_article.id, 'score': hn_score}

def parallel_fetch_scores_from_hn(articles):
  with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    future_to_article = {executor.submit(fetch_hn_article_score, article.id): article for article in articles}
    for future in concurrent.futures.as_completed(future_to_article):
      article = future_to_article[future]
      try:
        hn_score = future.result()
        result = update_article_scores(article, hn_score)
        if result:
          yield result
      except Exception as e:
        logging.error(f"Failed to process article {article.id}: {str(e)}")

def update_scores():
    logging.info("Starting update_scores task")
    week = datetime.now() - timedelta(days=7)
    
    with get_db() as session:
      articles = session.query(Article).filter(Article.created_at >= week).all()

    logging.info(f"{len(articles)} articles from the past week.")

    updated_articles = list(parallel_fetch_scores_from_hn(articles))

    if updated_articles:
      with get_db() as session:
        try:
          session.bulk_update_mappings(Article, updated_articles)
          session.commit()
          logging.info(f"{len(updated_articles)} article scores updated.")
        except Exception as e:
          logging.error(f"Error updating articles batch: {str(e)}")
          session.rollback()
