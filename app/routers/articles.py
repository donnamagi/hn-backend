from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models import Article
from sqlalchemy.orm import Session
from app.dependencies import get_session, MilvusService, get_milvus_session
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/articles", tags=["articles"])

class ArticleRequest(BaseModel):
  ids: List[int]

@router.post("/", description="Returns a list of articles based on the provided IDs in the request body")
async def get_specific_articles(request: ArticleRequest, db: Session = Depends(get_session)):
  try:
    articles = db.query(Article).filter(Article.id.in_(request.ids)).all()

    found_ids = {article.id for article in articles}
    missing_ids = [id for id in request.ids if id not in found_ids]

    return {
      "message": "Data retrieved", 
      "articles": articles, 
      "missing_ids": missing_ids
    }

  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    ) 

@router.get("/{article_id}", description="Gets a specific article by ID")
async def get_one_article(article_id: int, db: Session = Depends(get_session)):
  try:
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
      return {"message": "Article found", "article": article}
    else:
      return JSONResponse(
        status_code=404,
        content={"message": "Article not found"}
      )
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )

@router.get("/similar/{article_id}", description="Gets similar articles based on a provided article ID")
async def get_similar_articles(article_id: int, milvus: MilvusService = Depends(get_milvus_session), db: Session = Depends(get_session)):
  try:
    res = milvus.get_similar(id=article_id)
    res.pop(0) # first result == same article

    articles = []
    for match in res:
      article = db.query(Article).filter(Article.id == match['id']).first()
      if article:
        articles.append(article)

    if articles:
      return {"message": "Similar articles found", "articles": articles}
    else:
      return JSONResponse(
        status_code=404,
        content={"message": "Article not found"}
      )
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )
