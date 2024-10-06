from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.routers import jobs, articles, keywords
from app.dependencies import DatabaseService
from app.services.Scheduler import SchedulerService
from app.log import setup_sentry_and_logging
import os


""" This code will be executed once, before the application starts (and stops) receiving requests """


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    setup_sentry_and_logging()
    db_service = DatabaseService()
    scheduler = SchedulerService()

    yield

    # on shutdown
    db_service.engine.dispose()
    await scheduler.stop()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "https://hackernews.news",
    "https://www.hackernews.news",
    "https://perrichat.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=[],
)

app.include_router(articles.router)
app.include_router(keywords.router)
app.include_router(jobs.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
