from app.models import Article
from app.dependencies import get_db

from app.services.scrape import ProcessService
from app.services.hn import create_comments_trace_json, get_best, get_article

# from app.services.audio import AudioService

from datetime import datetime, timedelta
from sqlalchemy import desc
from typing import List

import json
import requests
import os


def summarize_comments(summary, comments):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    prompt = f"""
You are an AI assistant specializing in content curation. Your task is to analyze an article summary and its associated comments, then create a concise summary of the most insightful comments.

Instructions:
1. Carefully read the article summary and all comments.
2. Identify 5-10 of the most interesting, insightful, or thought-provoking comments that add value to the discussion.
3. For each selected comment:
   a. Extract the core idea or quote.
   b. Provide brief context or explanation if needed.

4. Compose your summary following these guidelines:
   a. Start with a brief introduction setting the context.
   b. Present each selected comment in a separate paragraph.
   c. Use quotation marks only for direct, word-for-word quotes.
   d. Ensure proper punctuation for optimal TTS performance.
   e. Simplify complex sentences or technical jargon if present.

Your goal is to create a coherent, engaging overview of the comment section that captures the most interesting points of the discussion.
The article: {summary}
The comments: {comments}
    """
    data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]})
    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()
    if "candidates" in response_json and response_json["candidates"]:
        return response_json["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return "No valid response received from the API."


def summarize_everything(summary, comments):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    prompt = f"""
You are an AI assistant specializing in content synthesis and text-to-speech (TTS) optimization. Your task is to create a final, cohesive narrative that combines an article summary with insights from its comment section, optimized for TTS delivery.

Instructions:
1. Carefully read the original summary and recapped comments.
2. Create a seamless narrative that flows from the article summary to the community's thoughts. Use the original summary, and do not make generic statements. 
3. Optimize the entire text for TTS delivery:
- Ensure proper punctuation.
- Use em dashes (—) for parenthetical phrases instead of parentheses.
- Spell out numbers and symbols (e.g., "percent" instead of "%").
- Maintain a conversational tone suitable for audio content.

4. Additional guidelines:
- Aim for a total length of 400-600 words.
- Simplify complex sentences or technical jargon if present.

Your goal is to create an engaging, coherent narrative that presents both the article's content and the community's insights in a way that's optimized for TTS delivery. The final product should feel like a well-rounded audio report on both the article and its reception.

Original Summary: {summary}
Recapped Comments: {comments}
    """
    data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]})
    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()
    if "candidates" in response_json and response_json["candidates"]:
        return response_json["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return "No valid response received from the API."


def articles_str_to_txt(articles):
    a_str = "Hacker News News - September 15th 2024 \n\n"
    for article in articles:
        a_str += f"{article['title']}\n\n"
        a_str += f"{article['recap']}\n\n\n"

    filename = f"hn/recap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(a_str)
    except Exception as e:
        print(e)
        print(a_str)


def make_recap(keywords: List[str]):
    try:

        if keywords[0] == "all":
            best_stories = get_best()
            articles = [get_article(id) for id in best_stories[:3]]

            processor = ProcessService()
            articles = [processor.add_summary(article) for article in articles]
        else:
            with get_db() as db:
                articles = []
                for keyword in keywords:
                    two_weeks = datetime.now() - timedelta(weeks=2)
                    query = (
                        db.query(Article)
                        .filter(Article.keywords.any(keyword))
                        .filter(Article.time >= two_weeks)
                        .order_by(desc(Article.time))
                        .limit(3)
                        .all()
                    )
                    articles.extend(query)
        content = [
            {
                "id": article.id,
                "title": article.title,
                "content_summary": article.content_summary,
                "url": article.url,
                "time": article.time,
            }
            for article in articles
        ]

        for article in content:
            comment_dict = create_comments_trace_json(article["id"], trees_count=5)
            comments_recap = summarize_comments(
                summary=article["content_summary"], comments=comment_dict
            )
            article["recap"] = summarize_everything(
                summary=article["content_summary"], comments=comments_recap
            )

        articles_str_to_txt(content)
        return content

    except Exception as e:
        print(e)
