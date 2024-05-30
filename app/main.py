from fastapi import FastAPI, Depends
from app.routers import bestArticles
from app.dependencies import DatabaseService

app = FastAPI()

db_service = DatabaseService()

def get_db():
  db = db_service.Session()
  try:
    yield db
  finally:
    db.close()

app.include_router(bestArticles.router, prefix="/best", dependencies=[Depends(get_db)])

@app.get("/")
async def root():
  return {"message": "Hello World"}
