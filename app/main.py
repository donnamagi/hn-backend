from fastapi import FastAPI
from app.routers import bestArticles
from app.dependencies import DatabaseService
from app.services.Scheduler import SchedulerService
from contextlib import asynccontextmanager


""" This code will be executed once, before the application starts (and stops) receiving requests """
@asynccontextmanager
async def lifespan(app: FastAPI):
  # on startup
  db_service = DatabaseService()
  scheduler = SchedulerService()

  yield 

  # on shutdown
  db_service.engine.dispose()
  scheduler.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(bestArticles.router)

@app.get("/")
async def root():
  return {"message": "Hello World"}
