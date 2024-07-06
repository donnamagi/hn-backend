from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models import Article
from sqlalchemy.orm import Session
from app.dependencies import get_session
from datetime import datetime, timedelta
from collections import Counter
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/keywords", tags=["keywords"])

@router.get("/top/{n}")
async def get_top_n(db: Session = Depends(get_session), n: int = 10):
  try:
    query = db.query(Article.keywords).filter(Article.keywords != None).all()
    keywords = [row[0] for row in query]

    flat_keywords = [
      keyword
      for sublist in keywords
      for keyword in sublist
    ]

    top_keywords = Counter(flat_keywords).most_common(n)

    return {"message": "Data retrieved", "top_keywords": top_keywords}
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )

@router.get("/top-weekly/{n}")
async def get_top_n_weekly(db: Session = Depends(get_session), n: int = 10):
  try:
    end_date = datetime.now()
    keyword_occurrences = {}

    while True:
      start_date = end_date - timedelta(days=7)
      query = db.query(Article.keywords).filter(
        Article.keywords != None,
        Article.created_at >= start_date,
        Article.created_at < end_date
      ).all()

      if not query:
        break

      keywords = [row[0] for row in query]

      flat_keywords = [
        keyword
        for sublist in keywords
        for keyword in sublist
      ]

      keyword_counts = Counter(flat_keywords)

      keyword_occurrences[start_date] = keyword_counts.most_common(n)

      end_date = start_date # loop continues, prev week

    return {"message": "Data retrieved", "keyword_occurrences": keyword_occurrences}
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )

class KeywordRequest(BaseModel):
  keywords: List[str]

@router.post("/")
async def get_specific_articles(request: KeywordRequest, db: Session = Depends(get_session)):
  try:

    articles = set()
    for keyword in request.keywords:
      query = db.query(Article).filter(Article.keywords.any(keyword)).all()
      articles.update(query)

    # recents first
    articles = sorted(articles, key=lambda x: x.created_at, reverse=True)


    return {
      "message": "Data retrieved", 
      "articles": articles, 
    }

  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )