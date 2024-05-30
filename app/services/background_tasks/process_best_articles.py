from app.services.scrape import ProcessService
from app.dependencies import MilvusService, get_session
from app.services.hn import get_best, get_article
from app.services.helpers import get_unique_ids
from app.models import BestArticle

def process_best():
  vector_db = MilvusService()
  processor = ProcessService()

  collection = vector_db.get_all_db_ids()
  top_stories = get_best()

  print(len(collection), "articles in the database.")
  print(len(top_stories), "articles from HN.")

  new_ids = get_unique_ids(collection, top_stories)
  print(len(new_ids), "new articles to process.")

  articles = []
  vector_entries = []

  if not new_ids:
    print("No new articles to process.")
    return

  for id in new_ids:
    article = get_article(id)

    # adds keywords, summary, embedding
    try:
      print("Processing article:", article['title'])
      article = processor.process_article(article) 

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
    with get_session() as session:
      session.bulk_insert_mappings(BestArticle, articles)
      session.commit()
      print("Inserted articles batch")
  except Exception as e:
    print(f"Error inserting articles batch: {e}")
    session.rollback()
    return False
  vector_db.insert(vector_entries)
  return print(len(articles), "articles added.")

