from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, FileResponse
from app.models import Article
from sqlalchemy.orm import Session
from app.dependencies import get_session
from datetime import datetime, timedelta
from collections import Counter
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel
from sqlalchemy import desc

router = APIRouter(prefix="/keywords", tags=["keywords"])


# helper function to count keyword occurrences from db query returns
def count_keyword_occurrences(query):
    keywords = [row[0] for row in query]

    flat_keywords = [keyword for sublist in keywords for keyword in sublist]

    return Counter(flat_keywords)


@router.get(
    "/top/{n}", description="Gets the top n keywords from the last 300 articles"
)
async def get_top_n(db: Session = Depends(get_session), n: int = 10):
    try:
        query = (
            db.query(Article.keywords)
            .filter(Article.keywords.isnot(None))
            .order_by(desc(Article.created_at))
            .limit(300)
            .all()
        )

        counted_keywords = count_keyword_occurrences(query)

        top_keywords = counted_keywords.most_common(n)
        keys_only = [key for key, _ in top_keywords]

        return {"message": "Data retrieved", "top_keywords": keys_only}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {e}"})


@router.get(
    "/top-weekly/{n}",
    description="Gets a time series analysis of keyword occurrences per week",
)
async def get_top_n_weekly(db: Session = Depends(get_session), n: int = 10):
    try:
        end_date = datetime.now()
        keyword_occurrences = {}

        while True:
            start_date = end_date - timedelta(days=7)
            query = (
                db.query(Article.keywords)
                .filter(
                    Article.keywords.isnot(None),
                    Article.created_at >= start_date,
                    Article.created_at < end_date,
                )
                .all()
            )

            if not query:
                break

            keyword_counts = count_keyword_occurrences(query)

            keyword_occurrences[start_date] = keyword_counts.most_common(n)

            end_date = start_date  # loop continues, prev week

        return {"message": "Data retrieved", "keyword_occurrences": keyword_occurrences}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {e}"})


class KeywordRequest(BaseModel):
    keywords: List[str]


@router.post(
    "/", description="Fetches articles that contain any of the specified keywords."
)
async def get_specific_articles(
    request: KeywordRequest, db: Session = Depends(get_session)
):
    try:

        articles = []
        for keyword in request.keywords:
            query = (
                db.query(Article)
                .filter(Article.keywords.any(keyword))
                .order_by(desc(Article.time))
                .limit(100)
                .all()
            )
            articles.extend(query)

        return {
            "message": "Data retrieved",
            "articles": articles,
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {e}"})
