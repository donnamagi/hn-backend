from pymilvus import MilvusClient
from dotenv import load_dotenv
import os

load_dotenv()

class MilvusService:
  def __init__(self):
    self.client = MilvusClient(
      uri=os.getenv("MILVUS_CLUSTER_ENDPOINT"),
      token=os.getenv("MILVUS_API_KEY")
    )
    self.collection_name = 'HackerNews'
    self.res_limit = 5
    self.output_fields = ['hn_id', 'title', 'content', 'date', 'url']

  def insert(self, data):
    return self.client.insert(
      collection_name=self.collection_name,
      data=data
    )

  def delete(self, ids):
    return self.client.delete(
      collection_name=self.collection_name,
      pks=ids
    )

  def search_vector(self, vectors, fields=None, limit=None):
    if fields is None:
      fields = self.output_fields
    if limit is None:
      limit = self.res_limit
    return self.client.search(
      collection_name=self.collection_name,
      data=vectors,
      filter="content != ''",
      output_fields=fields,
      limit=limit
    )[0]

  def search_query(self, query, fields=None, limit=None):
    if fields is None:
      fields = self.output_fields
    if limit is None:
      limit = self.res_limit
    return self.client.query(
      collection_name=self.collection_name,
      filter=query,
      output_fields=fields,
      limit=limit
    )

  def search_get(self, ids):
    return self.client.get(
      collection_name=self.collection_name,
      ids=ids
    )

  def get_all_db_ids(self):
    res = self.client.query(
      collection_name=self.collection_name,
      filter="id > 0",
      output_fields=["id"],
      limit=1000
    )
    if len(res) == 1000:
      print("Limit reached. Only first 1000 items returned.")
    return res

  def get_all_db_data(self):
    res = self.client.query(
      collection_name=self.collection_name,
      filter="id > 0",
      output_fields=["id", "title", "keywords", "url", "content_summary", "time", "processing_date", "score", "type"],
      limit=1000
    )
    if len(res) == 1000:
      print("Limit reached. Only first 1000 items returned.")
    return res

  def get_all_with_comments(self):
    res = self.client.query(
      collection_name=self.collection_name,
      filter="id > 0",
      output_fields=["id", "title", "keywords", "time", "score", "kids"],
      limit=1000
    )
    if len(res) == 1000:
      print("Limit reached. Only first 1000 items returned.")
    return res
