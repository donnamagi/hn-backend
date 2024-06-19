from app.dependencies import get_db
from app.services.hn import get_all_recents

def store_all_recents():
  recents = get_all_recents()

  if not recents:
    print("Something went wrong with the API.")
    return False
  
  try:
    with get_db() as db:
      # store all new articles in db table 'recents'
      db.add(recents)
      db.commit()  
    return True
  except Exception as e:
    print(e)
    return False
