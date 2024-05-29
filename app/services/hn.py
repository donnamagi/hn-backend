from datetime import datetime
import requests

HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"

def get_all_recents():
  try:
    top_stories = requests.get(f"{HN_BASE_URL}/topstories.json")
    new_stories = requests.get(f"{HN_BASE_URL}/newstories.json")
    ask_stories = requests.get(f"{HN_BASE_URL}/askstories.json")

    return {
      "top_stories": top_stories.json(), 
      "new_stories": new_stories.json(), 
      "ask_stories": ask_stories.json(),
      "timestamp": datetime.now().isoformat()
    }
  except Exception as e:
    print(e)

def get_top():
  try:
    top_stories = requests.get(f"{HN_BASE_URL}/topstories.json")

    return top_stories.json()
  except Exception as e:
    print(e)

def get_article(id:int):
  try:
    article = requests.get(f"{HN_BASE_URL}/item/{id}.json")

    return article.json()
  except Exception as e:
    print(e)
