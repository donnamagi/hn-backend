import requests
from app.models import Recent

HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"

def get_all_recents():
  try:
    top = requests.get(f"{HN_BASE_URL}/topstories.json")
    new = requests.get(f"{HN_BASE_URL}/newstories.json")
    ask = requests.get(f"{HN_BASE_URL}/askstories.json")
    best = requests.get(f"{HN_BASE_URL}/beststories.json")
    show = requests.get(f"{HN_BASE_URL}/showstories.json")
    job = requests.get(f"{HN_BASE_URL}/jobstories.json")

    recent = Recent(
      top=top.json(), 
      new=new.json(), 
      ask=ask.json(), 
      best=best.json(), 
      show=show.json(), 
      job=job.json()
    )
    return recent
  except Exception as e:
    print(e)

def get_top():
  try:
    top_stories = requests.get(f"{HN_BASE_URL}/topstories.json")

    return top_stories.json()
  except Exception as e:
    print(e)

def get_best():
  try:
    best_stories = requests.get(f"{HN_BASE_URL}/beststories.json")

    return best_stories.json()
  except Exception as e:
    print(e)

def get_article(id:int):
  try:
    article = requests.get(f"{HN_BASE_URL}/item/{id}.json")

    return article.json()
  except Exception as e:
    print(e)
