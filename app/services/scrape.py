import os
from dotenv import load_dotenv
from groq import Groq
import voyageai
from bs4 import BeautifulSoup
from app.services.helpers import clean_text, clean_llm_text
import requests
import ast
from datetime import datetime, timezone


load_dotenv()

class ProcessService:
  def __init__(self):
    self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    self.embeddings_client = voyageai.Client()

  def get_content(self, url: str) -> str:
    content = requests.get(url)
    if content.status_code == 200:
      soup = BeautifulSoup(content.text, 'html.parser')
      return clean_text(soup)
    else:
      return None

  def get_summary(self, content: str) -> str:
    chat_completion = self.groq_client.chat.completions.create(
      messages=[
        {
          "role": "user",
          "content": f"Summarize the text in 2-3 sentences. Be precise, no introduction needed: {content}",
        }
      ],
      model="llama3-70b-8192",
    )

    reply = chat_completion.choices[0].message.content
    return clean_llm_text(reply)

  def get_keywords(self, summary: str) -> str:
    try: 
      chat_completion = self.groq_client.chat.completions.create(
        messages=[
          {
            "role": "user",
            "content": 
              f""" 
                Generate 5 relevant keywords for an article's general topic. What areas of interest does the article cover?
                Avoid repetition, and keep the keywords general.
                This is the article's summary: {summary}.
                Answer ONLY with the keywords. Every keyword should be 1-2 words only. 
                Answer with a list of strings. Example format: ['keyword', 'keyword', 'keyword']
              """,
          }
        ],
        model="llama3-70b-8192",
      )
      # convert str into list
      list = ast.literal_eval(chat_completion.choices[0].message.content)
      return list
    except:
      return None

  def get_embedding(self, summary: str) -> list:
    result = self.embeddings_client.embed(summary, model="voyage-2")
    return result.embeddings[0]
  
  def process_article(self, article:dict) -> dict:
    try:
      article['time'] = datetime.fromtimestamp(article['time'], timezone.utc)
      
      if 'text' in article:
        summary = self.get_summary(article['text'])
      else:
        content = self.get_content(article['url'])
        summary = self.get_summary(content) if content else None

      if summary and len(summary) > 0:
        keywords = self.get_keywords(summary)
        embedding = self.get_embedding(summary)
      else:
        keywords = None
        embedding = self.get_embedding(article['title'])

      article['content_summary'] = summary
      article['keywords'] = keywords
      article['vector'] = embedding

      return article
    except Exception as e:
      print(e)
      return None

