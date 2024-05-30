from fastapi import FastAPI
from app.routers import bestArticles
from app.dependencies import DatabaseService
from contextlib import asynccontextmanager


""" This code will be executed once, before the application starts (and stops) receiving requests """
@asynccontextmanager
async def lifespan(app: FastAPI):
  # on startup
  db_service = DatabaseService()

  yield 

  # on shutdown
  db_service.engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(bestArticles.router)

@app.get("/")
async def root():
  return {"message": "Hello World"}
