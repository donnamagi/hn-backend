from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models import Article
from sqlalchemy.orm import Session
from app.dependencies import get_session, MilvusService, get_milvus_session
from datetime import datetime, timedelta

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/")
async def get_all(db: Session = Depends(get_session)):
  try:
    articles = db.query(Article).all()
    return {"message": "Data retrieved", "articles": articles}
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )

@router.get("/week")
async def get_all_from_past_week(db: Session = Depends(get_session)):
  try:
    week = datetime.now() - timedelta(days=7)
    articles = db.query(Article).filter(Article.created_at >= week).all()
    return {"message": "Data retrieved", "articles": articles}
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )
  
@router.get("/best")
async def get_best(db: Session = Depends(get_session)):
  try:
    articles = db.query(Article).filter(Article.category.in_([1, 12]))\
              .order_by(Article.time.desc())\
              .limit(500)\
              .all()
    return {"message": "Data retrieved", "articles": articles}
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )

@router.get("/top")
async def get_top(db: Session = Depends(get_session)):
  try:
    articles = db.query(Article).filter(Article.category.in_([2, 12]))\
                    .order_by(Article.time.desc())\
                    .limit(500)\
                    .all()
    return {"message": "Data retrieved", "articles": articles}
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={"message": f"Error: {e}"}
    )

@router.get("/{article_id}")
async def get_article(article_id: int, db: Session = Depends(get_session)):
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

@router.get("/similar/{article_id}")
async def get_article(article_id: int, milvus: MilvusService = Depends(get_milvus_session), db: Session = Depends(get_session)):
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
