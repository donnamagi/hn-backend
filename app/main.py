from fastapi import FastAPI
from app.routers import jobs, articles, keywords
from app.dependencies import DatabaseService
from app.services.Scheduler import SchedulerService
from contextlib import asynccontextmanager
import sentry_sdk
import os


""" Sentry setup to monitor errors in the live app. https://hacker-news.sentry.io/ """
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


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

@app.get("/sentry-debug")
async def trigger_error():
  division_by_zero = 1 / 0