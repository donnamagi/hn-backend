from app.services.scrape import ProcessService
from app.dependencies import MilvusService, DatabaseService
from app.services.hn import get_top, get_article
from app.services.helpers import get_unique_ids

def process_top():
  db = DatabaseService()
  vector_db = MilvusService()
  processor = ProcessService()

  collection = vector_db.get_all_db_ids()
  top_stories = get_top()

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
  db.insert_articles_batch(articles)
  vector_db.insert(vector_entries)
  return print(len(articles), "articles added.")

