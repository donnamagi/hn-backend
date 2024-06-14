from sqlalchemy import update
from app.models import Article, Recent
from app.dependencies import get_session

db = get_session()

def add_categories():
  try:
      with db as session:
        recent_entries = session.query(Recent).all()
        nulls = session.query(Article.id).filter(Article.category == None).all()

        best = set()
        top = set()

        for entry in recent_entries:
          best.update(entry.best[:50])
          top.update(entry.top[:50])

        best = [int(x) for x in best]
        top = [int(x) for x in top]
        both = [int(x) for x in best if x in top] 

        session.execute(
          update(Article).where(Article.id.in_(best)).values(category=1)
        )

        session.execute(
          update(Article).where(Article.id.in_(top)).values(category=2)
        )

        session.execute(
          update(Article).where(Article.id.in_(both)).values(category=12)
        )

        session.commit()  

        nulls = session.query(Article.id).filter(Article.category == None).all()
        
        print(len(nulls), "nulls left.") # 241 atm
        # the recents got collected less frequently than articles. not much I can do
        # assigning the remaining nulls to top, as its most likely
        session.execute(
          update(Article).where(Article.category == None).values(category=2)
        )

        session.commit()

  except Exception as e:
      session.rollback()  # Rollback in case of any error
      print(f"An error occurred: {e}")
  finally:
      session.close()

  print("Category update completed.")

add_categories() # ran on 14-06-2024 with around 670 articles to reassign
