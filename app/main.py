from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import jobs, articles, keywords
from app.dependencies import DatabaseService
from app.services.Scheduler import SchedulerService
from contextlib import asynccontextmanager
import sentry_sdk
import os
from sentry_sdk.integrations.logging import LoggingIntegration
import logging


""" Sentry setup to monitor errors in the live app. https://donnamagi.sentry.io/ """
def setup_logging():
  logging.basicConfig(level=logging.INFO,
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
  
  print("Logging configured")

sentry_logging = LoggingIntegration(
  level=logging.INFO,
  event_level=logging.ERROR 
)

sentry_sdk.init(
  dsn=os.getenv("SENTRY_DSN"),
  # Set traces_sample_rate to 1.0 to capture 100%
  # of transactions for performance monitoring.
  traces_sample_rate=1.0,
  # Set profiles_sample_rate to 1.0 to profile 100%
  # of sampled transactions.
  # We recommend adjusting this value in production.
  profiles_sample_rate=1.0,
  integrations=[sentry_logging]
)

""" This code will be executed once, before the application starts (and stops) receiving requests """
@asynccontextmanager
async def lifespan(app: FastAPI):
  # on startup
  db_service = DatabaseService()
  scheduler = SchedulerService()
  setup_logging()


  yield 

  # on shutdown
  db_service.engine.dispose()
  await scheduler.stop()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "https://hackernews.news",
    "https://www.hackernews.news",
    "https://hn-front.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(keywords.router)
app.include_router(jobs.router)

@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/sentry-debug")
async def trigger_error():
  division_by_zero = 1 / 0