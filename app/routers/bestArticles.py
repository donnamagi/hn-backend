from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models import BestArticle
from sqlalchemy.orm import Session
from app.dependencies import get_session

router = APIRouter(prefix="/best-articles", tags=["best articles"])

@router.get("/all")
async def get_all(db: Session = Depends(get_session)):
  try:
    articles = db.query(BestArticle).all()
    return {"message": "Data retrieved", "articles_count": len(articles)}
  except Exception as e:
    return JSONResponse(
        status_code=500,
        content={"message": f"Error: {e}"}
    )

