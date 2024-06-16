# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, orm
from pymilvus import MilvusClient
import threading
from app.models import Base
from contextlib import contextmanager

load_dotenv()

class DatabaseService:
  _instance = None
  _lock = threading.Lock()

  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      print("Creating new DB instance")
      with cls._lock:
        if not cls._instance:
          cls._instance = super(DatabaseService, cls).__new__(cls, *args, **kwargs)
    return cls._instance

  def __init__(self):
    if hasattr(self, 'initialized') and self.initialized:
      return
    print("Initializing DB")
    self.secret = self._get_secret()
    self.engine = self._connect_to_db()
    self.Session = orm.sessionmaker(
      bind=self.engine,
      autocommit=False,
      autoflush=False
      )
    Base.metadata.create_all(self.engine)
    self.initialized = True

  def _get_secret(self):
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
    return json.loads(secret)

  def _connect_to_db(self):
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


class MilvusService:
  _instance = None
  _lock = threading.Lock()
  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      print("Creating new Milvus instance")
      with cls._lock:
        if not cls._instance:
          cls._instance = super(MilvusService, cls).__new__(cls, *args, **kwargs)
    return cls._instance

  def __init__(self):
    if hasattr(self, 'initialized') and self.initialized:
      return
    print("Initializing Milvus")
    self.client = MilvusClient(
      uri=os.getenv("MILVUS_CLUSTER_ENDPOINT"),
      token=os.getenv("MILVUS_API_KEY")
    )
    self.collection_name = 'HackerNews'
    self.initialized = True

  def insert(self, data):
    return self.client.insert(
      collection_name=self.collection_name,
      data=data
    )
  
  def search_vector(self, vectors, fields=['id'], limit=5):
    return self.client.search(
      collection_name=self.collection_name,
      data=vectors,
      filter="content != ''",
      output_fields=fields,
      limit=limit
    )[0]
  
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

def get_session():
  db_service = DatabaseService()
  session = db_service.Session()
  print("Session created")
  try:
    yield session
  finally:
    session.close()
