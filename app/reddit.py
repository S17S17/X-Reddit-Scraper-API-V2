import asyncio
import time
from urllib.parse import quote_plus

import httpx

USER_AGENT = "TTE-Scraper-API/1.0 (by /u/TounsiTechEmpire)"
BASE_URL = "https://www.reddit.com"

# Rate limiter: Reddit allows 10 req/min for unauthenticated .json access
_last_request_time = 0.0
_rate_lock = asyncio.Lock()
RATE_LIMIT_INTERVAL = 6.5  # seconds between requests


class RedditError(Exception):
    """Wrapper for Reddit scraper errors with HTTP status code mapping."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


async def _rate_limited_get(url: str, params: dict | None = None) -> dict:
    """Make a rate-limited GET request to Reddit's .json endpoints."""
    global _last_request_time

    async with _rate_lock:
        now = time.monotonic()
        elapsed = now - _last_request_time
        if elapsed < RATE_LIMIT_INTERVAL:
            await asyncio.sleep(RATE_LIMIT_INTERVAL - elapsed)
        _last_request_time = time.monotonic()

    async with httpx.AsyncClient(
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        follow_redirects=True,
        timeout=15.0,
    ) as client:
        try:
            resp = await client.get(url, params=params)
        except httpx.TimeoutException:
            raise RedditError("Reddit request timed out. Try again.", status_code=504)
        except httpx.HTTPError as e:
            raise RedditError(f"Reddit HTTP error: {e}", status_code=502)

    if resp.status_code == 429:
        raise RedditError(
            "Rate limited by Reddit. Try again in a few minutes.",
            status_code=429,
        )
    if resp.status_code == 403:
        raise RedditError(
            "Reddit returned 403 Forbidden. Possible causes: subreddit is private, "
            "User-Agent is blocked, or you're being rate-limited. "
            "Try again later or check the subreddit name.",
            status_code=403,
        )
    if resp.status_code == 404:
        raise RedditError("Subreddit or post not found on Reddit.", status_code=404)
    if resp.status_code >= 500:
        raise RedditError("Reddit server error. Try again later.", status_code=502)
    if resp.status_code != 200:
        raise RedditError(
            f"Reddit returned status {resp.status_code}.",
            status_code=resp.status_code,
        )

    try:
        return resp.json()
    except Exception:
        raise RedditError("Failed to parse Reddit response.", status_code=502)


def _parse_post(post_data: dict) -> dict:
    """Extract relevant fields from a Reddit post's data dict."""
    d = post_data.get("data", post_data)
    score = d.get("score", 0) or 0
    num_comments = d.get("num_comments", 0) or 0
    return {
        "id": d.get("id"),
        "title": d.get("title", ""),
        "selftext": (d.get("selftext", "") or "")[:2000],
        "author": d.get("author"),
        "subreddit": d.get("subreddit"),
        "score": score,
        "upvote_ratio": d.get("upvote_ratio"),
        "num_comments": num_comments,
        "url": d.get("url"),
        "permalink": f"https://www.reddit.com{d.get('permalink', '')}",
        "created_at": d.get("created_utc"),
        "engagement_score": score + num_comments,
    }


def _parse_comment(comment_data: dict) -> dict:
    """Extract relevant fields from a Reddit comment's data dict."""
    d = comment_data.get("data", comment_data)
    return {
        "id": d.get("id"),
        "author": d.get("author"),
        "body": (d.get("body", "") or "")[:2000],
        "score": d.get("score", 0),
        "created_at": d.get("created_utc"),
        "permalink": f"https://www.reddit.com{d.get('permalink', '')}",
    }


async def get_subreddit_posts(
    name: str,
    sort: str = "hot",
    time_filter: str = "day",
    count: int = 25,
) -> dict:
    """Get posts from a subreddit."""
    url = f"{BASE_URL}/r/{quote_plus(name)}/{sort}.json"
    params = {"limit": min(count, 100), "raw_json": 1}
    if sort == "top" and time_filter:
        params["t"] = time_filter

    data = await _rate_limited_get(url, params)

    children = data.get("data", {}).get("children", [])
    posts = [_parse_post(child) for child in children[:count]]
    return {"subreddit": name, "sort": sort, "count": len(posts), "posts": posts}


async def search_reddit(
    query: str,
    sort: str = "relevance",
    time_filter: str = "week",
    count: int = 25,
) -> dict:
    """Search Reddit posts across all subreddits."""
    url = f"{BASE_URL}/search.json"
    params = {
        "q": query,
        "sort": sort,
        "t": time_filter,
        "limit": min(count, 100),
        "raw_json": 1,
    }

    data = await _rate_limited_get(url, params)

    children = data.get("data", {}).get("children", [])
    posts = [_parse_post(child) for child in children[:count]]
    return {"query": query, "sort": sort, "count": len(posts), "posts": posts}


async def get_post_details(post_id: str) -> dict:
    """Get full details of a Reddit post by ID."""
    url = f"{BASE_URL}/comments/{post_id}.json"
    params = {"limit": 1, "raw_json": 1}

    data = await _rate_limited_get(url, params)

    # Reddit returns [post_listing, comments_listing]
    if not isinstance(data, list) or len(data) < 1:
        raise RedditError("Unexpected Reddit post response format.", status_code=502)

    post_children = data[0].get("data", {}).get("children", [])
    if not post_children:
        raise RedditError("Post not found.", status_code=404)

    post = _parse_post(post_children[0])
    return {"post": post}


async def get_post_comments(
    post_id: str,
    count: int = 25,
    sort: str = "best",
) -> dict:
    """Get comments on a Reddit post."""
    url = f"{BASE_URL}/comments/{post_id}.json"
    params = {"sort": sort, "limit": min(count, 100), "raw_json": 1}

    data = await _rate_limited_get(url, params)

    # Reddit returns [post_listing, comments_listing]
    if not isinstance(data, list) or len(data) < 2:
        raise RedditError("Unexpected Reddit comments response format.", status_code=502)

    children = data[1].get("data", {}).get("children", [])
    comments = []
    for child in children[:count]:
        if child.get("kind") == "t1":  # only actual comments, not "more"
            comments.append(_parse_comment(child))

    return {"post_id": post_id, "sort": sort, "count": len(comments), "comments": comments}
