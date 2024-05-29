from db_vector import MilvusService
from scrape import ProcessService
from db import DatabaseService
from hn import get_top, get_article
from helpers import get_unique_ids
from pprint import pprint

def process_articles():
  vector_db = MilvusService()
  db = DatabaseService()
  processor = ProcessService()

  collection = vector_db.get_all_db_ids()
  top_stories = get_top()

  print(len(collection), "articles in the database.")
  print(len(top_stories), "articles from HN.")

  new_ids = get_unique_ids(collection, top_stories)
  print(len(new_ids), "new articles to process.")

  articles = []
  vector_entries = []

  for id in new_ids[:10]:
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
      pprint(article)
      articles.append(article)
    except:
      print("Error processing article:", article['id'])
      continue

  # batch insert
  db.insert_articles_batch(articles)
  vector_db.insert(vector_entries)
  print(len(articles), "articles added.")

process_articles()
