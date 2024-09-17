from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models import Article
from sqlalchemy.orm import Session
from app.dependencies import get_session, MilvusService, get_milvus_session
from typing import List
from pydantic import BaseModel
from app.services.background_tasks.process_articles import ProcessService

router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleRequest(BaseModel):
    ids: List[int]


@router.post(
    "/",
    description="Returns a list of articles based on the provided IDs in the request body",
)
async def get_specific_articles(
    request: ArticleRequest, db: Session = Depends(get_session)
):
    try:
        articles = db.query(Article).filter(Article.id.in_(request.ids)).all()

        found_ids = {article.id for article in articles}
        missing_ids = [id for id in request.ids if id not in found_ids]

        return {
            "message": "Data retrieved",
            "articles": articles,
            "missing_ids": missing_ids,
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {e}"})


@router.get("/{article_id}", description="Gets a specific article by ID")
async def get_one_article(article_id: int, db: Session = Depends(get_session)):
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            return {"message": "Article found", "article": article}
        else:
            return JSONResponse(
                status_code=404, content={"message": "Article not found"}
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {e}"})


@router.get(
    "/similar/{article_id}",
    description="Gets similar articles based on a provided article ID",
)
async def get_similar_articles(
    article_id: int,
    milvus: MilvusService = Depends(get_milvus_session),
    db: Session = Depends(get_session),
):
    try:
        res = milvus.get_similar(id=article_id)
        res.pop(0)  # first result == same article

        articles = []
        for match in res:
            article = db.query(Article).filter(Article.id == match["id"]).first()
            if article:
                articles.append(article)

        if articles:
            return {"message": "Similar articles found", "articles": articles}
        else:
            return JSONResponse(
                status_code=404, content={"message": "Article not found"}
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {e}"})


class ShowRequest(BaseModel):
    input: str


@router.post(
    "/similar/show",
    description="Returns similar show HN articles based on the pitch provided in the request body",
)
async def get_similar_articles_show(
    request: ShowRequest,
    milvus: MilvusService = Depends(get_milvus_session),
    db: Session = Depends(get_session),
    process: ProcessService = Depends(ProcessService),
):

    try:
        embedding = process.get_embedding(request.input)

        res = milvus.get_similar_shows(embedding)
        db_res = milvus.get_similar_new_shows(embedding)

        res.extend(db_res)
        res = sorted(res, key=lambda x: x["distance"], reverse=True)

        ids_to_fetch = [hit["id"] for hit in res if "title" not in hit["entity"]]

        articles_from_db = (
            db.query(Article.id, Article.title, Article.content_summary)
            .filter(Article.id.in_(ids_to_fetch))
            .all()
        )
        article_dict_map = {
            article.id: {
                "id": article.id,
                "title": article.title,
                "content_summary": article.content_summary,
            }
            for article in articles_from_db
        }

        articles = []
        for hit in res:
            if "title" in hit["entity"]:
                # older articles already have 'title' and other details on Zilliz
                articles.append(dict(hit["entity"]))
            else:
                article_id = hit["id"]
                if article_id in article_dict_map:
                    articles.append(article_dict_map[article_id])

        if articles:
            return {
                "message": "Similar articles found",
                "articles": articles,
            }
        else:
            return JSONResponse(status_code=404, content={"message": "None found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {e}"})
