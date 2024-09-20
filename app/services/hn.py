import requests
from app.models import Recent
import json
import re
import html
import unicodedata
import os

HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"


def get_all_recents():
    try:
        top = requests.get(f"{HN_BASE_URL}/topstories.json")
        new = requests.get(f"{HN_BASE_URL}/newstories.json")
        ask = requests.get(f"{HN_BASE_URL}/askstories.json")
        best = requests.get(f"{HN_BASE_URL}/beststories.json")
        show = requests.get(f"{HN_BASE_URL}/showstories.json")
        job = requests.get(f"{HN_BASE_URL}/jobstories.json")

        recent = Recent(
            top=top.json(),
            new=new.json(),
            ask=ask.json(),
            best=best.json(),
            show=show.json(),
            job=job.json(),
        )
        return recent
    except Exception as e:
        print(e)


def get_top():
    try:
        top_stories = requests.get(f"{HN_BASE_URL}/topstories.json")

        return top_stories.json()
    except Exception as e:
        print(e)


def get_best():
    try:
        best_stories = requests.get(f"{HN_BASE_URL}/beststories.json")

        return best_stories.json()
    except Exception as e:
        print(e)


def get_article(id: int):  # all items
    try:
        article = requests.get(f"{HN_BASE_URL}/item/{id}.json")

        return article.json()
    except Exception as e:
        print(e)


def clean_comment(text):
    text = html.unescape(text)

    # HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8", "ignore")
    )

    return text.strip()


def build_comment_tree(comment_id, trees_count):
    comment = get_article(comment_id)
    print("got comment", comment)
    if (
        comment is None
        or comment.get("deleted", False)
        or comment.get("dead", False)
        or comment.get("text") == "[delayed]"
    ):
        return None

    tree = {
        "comment": clean_comment(comment.get("text", "")),
        "replies": [],
    }

    if "kids" in comment:
        for kid_id in comment["kids"][:trees_count]:
            child_tree = build_comment_tree(kid_id, trees_count)
            if child_tree:
                tree["replies"].append(child_tree)

    return tree


def scrape_hn_comments(article_id, trees_count):
    article = get_article(article_id)
    if not article or "kids" not in article:
        print("Article not found or has no comments.")
        return None

    comment_forest = []
    for comment_id in article["kids"][:trees_count]:
        comment_tree = build_comment_tree(comment_id, trees_count)
        if comment_tree:
            comment_forest.append(comment_tree)

    return comment_forest


def save_to_json(comment_forest, filename):
    with open(filename, "w", encoding="utf-8") as jsonfile:
        json.dump(comment_forest, jsonfile, indent=2)

    print(f"Comment tree saved to {filename}")


def create_comments_trace_json(id, trees_count):
    filename = f"hn/{id}_comments.json"

    if os.path.exists(filename):
        print(f"File {filename} already exists. Returning existing content.")
        with open(filename, "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile)

    comment_forest = scrape_hn_comments(id, trees_count)
    if comment_forest:
        save_to_json(comment_forest, filename)
        return comment_forest

    else:
        print("No comments found or error occurred.")
