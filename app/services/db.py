# https://aws.amazon.com/developer/language/python/

import boto3
import psycopg2
import psycopg2.extras
from botocore.exceptions import ClientError
import json
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseService:
  def __init__(self):
    self.secret = self.get_secret()
    self.db_instance = self.connect_to_db()

  def get_secret(self):
    secret_name = os.getenv("AWS_RDS_SECRET")
    region_name = "eu-north-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
      service_name='secretsmanager',
      region_name=region_name,
      aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
      aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
    )

    try:
      get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
      )
    except ClientError as e:
      # For a list of exceptions thrown, see
      # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
      raise e

    secret = get_secret_value_response['SecretString']
    print('got secret')
    return json.loads(secret)

  def connect_to_db(self):
    db_host = os.getenv("AWS_HOST")
    db_port = 5432
    db_user = self.secret['username']
    db_password = self.secret['password']

    if not all([db_host, db_port, db_user, db_password]):
      print("Missing database connection parameters.")
      return None

    try:
      conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
      )

      print("Connected to db")
      return conn

    except Exception as e:
      print(f"Error connecting to the database: {e}")
      return None

  def insert_articles_batch(self, articles):
    try:
      with self.db_instance.cursor() as cursor:
          insert_query = """
          INSERT INTO best_articles (id, deleted, type, by, time, text, dead, parent, poll, kids, url, score, title, parts, descendants, content_summary, keywords) 
          VALUES %s
          """
          values = [
            (
              article.get('id'),
              article.get('deleted', None),
              article.get('type', None),
              article.get('by', None),
              article.get('time', None),
              article.get('text', None),
              article.get('dead', None),
              article.get('parent', None),
              article.get('poll', None),
              article.get('kids', None),
              article.get('url', None),
              article.get('score', None),
              article.get('title', None),
              article.get('parts', None),
              article.get('descendants', None),
              article.get('content_summary', None),
              article.get('keywords', None)
            ) for article in articles
          ]
          psycopg2.extras.execute_values(cursor, insert_query, values)
          self.db_instance.commit()
    except Exception as e:
      print(f"Error inserting articles batch: {e}")
      self.db_instance.rollback()

  def get_articles(self):
    try:
      with self.db_instance.cursor() as cursor:
        cursor.execute("SELECT * FROM best_articles")
        print("fetching articles")
        articles = cursor.fetchall()
        print('works')
        return articles
    except Exception as e:
      print(f"Error getting articles: {e}")
      return None
