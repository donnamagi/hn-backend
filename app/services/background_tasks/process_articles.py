from app.services.scrape import ProcessService
from app.dependencies import MilvusService, get_db
from app.services.hn import get_top, get_article, get_best
from app.services.helpers import get_unique_ids
from app.models import Article
from datetime import datetime, timedelta
import psycopg2
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_with_timeout(coroutine, seconds):
    try:
        return await asyncio.wait_for(coroutine, timeout=seconds)
    except asyncio.TimeoutError:
        raise Exception("Function call timed out")


async def process_articles():
    vector_db = MilvusService()
    processor = ProcessService()

    week = datetime.now() - timedelta(days=7)
    with get_db() as session:
        collection = [
            id[0]
            for id in session.query(Article.id).filter(Article.created_at >= week).all()
        ]
        logger.info(f"{len(collection)} articles from the past week.")
        logger.info(f"{collection[:5]}")

    top_stories = get_top()
    best_stories = get_best()

    new_top_ids = get_unique_ids(collection, top_stories)
    new_best_ids = get_unique_ids(collection, best_stories)

    all_new_ids = list(set(new_top_ids + new_best_ids))
    logger.info(f"{len(all_new_ids)} new articles to process.")

    articles = []
    vector_entries = []

    if not all_new_ids:
        logger.info("No new articles to process.")
        return

    for id in all_new_ids:
        article = get_article(id)

        if article["score"] < 50:
            continue

        if id in new_top_ids and id in new_best_ids:
            category = 12  # both
        elif id in new_top_ids:
            category = 2  # top
        elif id in new_best_ids:
            category = 1  # best

        try:
            logger.info(f"Processing article: {article['title']}")
            # adds keywords, summary, embedding

            try:
                article = await run_with_timeout(
                    asyncio.to_thread(processor.process_article, article), 120
                )
            except Exception as e:
                logger.info(f"Error processing article {id}: {str(e)}")
                continue

            if not article:
                logger.info(f"Article processing failed for: {id}")
                continue

            article["category"] = category

            vector_entry = {"id": article["id"], "vector": article["vector"]}
            vector_entries.append(vector_entry)

            article.pop("vector")
            articles.append(article)
        except Exception as e:
            logger.info(f"Error processing article {id}: {str(e)}")
            continue

    if not articles:
        logger.info("No new articles to process.")
        return True

    def insert_articles_batch(session, articles):
        session.bulk_insert_mappings(Article, articles)
        session.commit()
        logger.info(f"Inserted {len(articles)} articles")

    try:
        with get_db() as session:
            insert_articles_batch(session, articles)

        vector_db.insert(vector_entries)

    except Exception as e:
        if not isinstance(e, psycopg2.errors.UniqueViolation):
            logger.error(f"Error inserting articles batch: {e}")
            session.rollback()
            return False

        logger.info("Duplicate article detected, retrying one by one...")
        with get_db() as session:
            for article in articles:
                try:
                    session.add(Article(**article))
                    session.commit()

                    vector_entry = vector_entries[articles.index(article)]
                    vector_db.insert([vector_entry])
                except Exception as insert_error:
                    logger.error(
                        f"Error inserting article {article['id']}: {insert_error}"
                    )
                    session.rollback()
                    continue
    return True
