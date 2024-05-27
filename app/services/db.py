# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, orm
from app.models import Base, BestArticle

load_dotenv()

class DatabaseService:
  def __init__(self):
    self.secret = self.get_secret()
    self.engine = self.connect_to_db()
    self.Session = orm.sessionmaker(bind=self.engine)
    Base.metadata.create_all(self.engine)

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
      connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres'
      engine = create_engine(connection_string, pool_pre_ping=True)
      return engine
    except Exception as e:
      print(f"Error connecting to the database: {e}")
      return None

  def insert_articles_batch(self, articles):
    session = self.Session()
    try:
      session.bulk_insert_mappings(BestArticle, articles)
      session.commit()
      print("Inserted articles batch")
    except Exception as e:
      print(f"Error inserting articles batch: {e}")
      session.rollback()
    finally:
      session.close()

  def get_articles(self):
    session = self.Session()
    try:
      articles = session.query(BestArticle).all()
      return articles
    except Exception as e:
      raise e
    finally:
      session.close()
