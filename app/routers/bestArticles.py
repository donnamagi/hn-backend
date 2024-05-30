from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models import BestArticle
from app.main import get_db
from sqlalchemy.orm import Session
from app.dependencies import get_db

router = APIRouter(prefix="/best-articles", tags=["best articles"])

@router.get("/all")
async def get_all(db: Session = Depends(get_db)):
  try:
    articles = db.query(BestArticle).all()
    return JSONResponse(
      content={"message": "Data retrieved", "articles_count": len(articles)}
    )
  except Exception as e:
    return JSONResponse(
      status_code=500, 
      content={"message": f"Error: {e}"}
    )

