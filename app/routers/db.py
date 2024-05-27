from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.db import DatabaseService

router = APIRouter(prefix="/db", tags=["db"])
db = DatabaseService()

@router.get("/all")
async def get_all():
  try:
    articles = db.get_articles()
    return JSONResponse(content={"message": "Data retrieved", "articles_count": len(articles)})
  except Exception as e:
    return JSONResponse(content={"message": f"Error: {e}"})

