from fastapi import FastAPI
from app.routers import jobs, articles, keywords
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
  await scheduler.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(articles.router)
app.include_router(keywords.router)
app.include_router(jobs.router)

@app.get("/")
async def root():
  return {"message": "Hello World"}
