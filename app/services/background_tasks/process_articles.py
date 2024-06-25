from app.services.scrape import ProcessService
from app.dependencies import MilvusService, get_db
from app.services.hn import get_top, get_article, get_best
from app.services.helpers import get_unique_ids
from app.models import Article
from datetime import datetime, timedelta

def process_articles():
  vector_db = MilvusService()
  processor = ProcessService()
    
  week = datetime.now() - timedelta(days=7)
  with get_db() as session:
    collection = [id[0] for id in session.query(Article.id).filter(Article.created_at >= week).all()]
    print(len(collection), "articles from the past week.")
    print(collection[:5])

  top_stories = get_top()
  best_stories = get_best()

  new_top_ids = get_unique_ids(collection, top_stories)
  new_best_ids = get_unique_ids(collection, best_stories)

  all_new_ids = list(set(new_top_ids + new_best_ids))
  print(len(all_new_ids), "new articles to process.")

  articles = []
  vector_entries = []

  if not all_new_ids:
    print("No new articles to process.")
    return

  for id in all_new_ids:
    article = get_article(id)

    if article['score'] < 50:
      continue

    if id in new_top_ids and id in new_best_ids:
        category = 12  # both
    elif id in new_top_ids:
        category = 2  # top
    elif id in new_best_ids:
        category = 1  # best

    try:
      print("Processing article:", article['title'])
      # adds keywords, summary, embedding
      article = processor.process_article(article) 
      if not article:
        print("Article processing failed for:", id)
        continue

      article['category'] = category

      vector_entry = {
        "id": article['id'],
        "vector": article['vector']
      }
      vector_entries.append(vector_entry)
      
      article.pop('vector')
      articles.append(article)
    except:
      print("Error processing article:", article['id'])
      continue

  # batch insert
  try:
    with get_db() as session:
      session.bulk_insert_mappings(Article, articles)
      session.commit()
      print("Inserted articles batch")
  except Exception as e:
    print(f"Error inserting articles batch: {e}")
    session.rollback()
    return False
  vector_db.insert(vector_entries)
  return print(len(articles), "articles added.")

