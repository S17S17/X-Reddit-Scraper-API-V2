import asyncio
import random
import time
from urllib.parse import quote_plus

import httpx

# Realistic browser user agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]
BASE_URL = "https://www.reddit.com"

# Rate limiter
_last_request_time = 0.0
_rate_lock = asyncio.Lock()
RATE_LIMIT_INTERVAL = 7.0  # conservative spacing

# Retry config
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2.0  # seconds


class RedditError(Exception):
    """Wrapper for Reddit scraper errors with HTTP status code mapping."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


def _build_headers() -> dict:
    """Build browser-mimicking request headers with rotating User-Agent."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


async def _rate_limited_get_with_retry(url: str, params: dict | None = None) -> dict:
    """
    Make a rate-limited, retried GET request to Reddit's .json endpoints.
    Retries on 429, 500, 502, 503, 504 with exponential backoff.
    """
    global _last_request_time

    last_exception = None

    for attempt in range(MAX_RETRIES):
        # Rate limiting
        async with _rate_lock:
            now = time.monotonic()
            elapsed = now - _last_request_time
            if elapsed < RATE_LIMIT_INTERVAL:
                await asyncio.sleep(RATE_LIMIT_INTERVAL - elapsed)
            _last_request_time = time.monotonic()

        headers = _build_headers()

        async with httpx.AsyncClient(
            headers=headers,
            follow_redirects=True,
            timeout=20.0,
        ) as client:
            try:
                resp = await client.get(url, params=params)
            except httpx.TimeoutException as e:
                last_exception = RedditError(f"Reddit request timed out: {e}", status_code=504)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_BACKOFF_BASE * (2 ** attempt))
                    continue
                raise last_exception
            except httpx.HTTPError as e:
                last_exception = RedditError(f"Reddit HTTP error: {e}", status_code=502)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_BACKOFF_BASE * (2 ** attempt))
                    continue
                raise last_exception

        # Handle status codes
        if resp.status_code == 200:
            try:
                return resp.json()
            except Exception:
                raise RedditError("Failed to parse Reddit response.", status_code=502)

        if resp.status_code == 429:
            # Aggressive backoff on rate limit
            retry_after = int(resp.headers.get("retry-after", 60))
            wait = max(retry_after, 30)
            last_exception = RedditError(f"Reddit rate limited. Wait ~{wait}s.", status_code=429)
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(wait)
                continue
            raise last_exception

        if resp.status_code == 403:
            # Could be a temporary block — retry once with different UA
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(3 + random.uniform(0, 3))
                continue
            raise RedditError(
                "Reddit returned 403 Forbidden. This can happen if Reddit is temporarily "
                "blocking your IP or if the User-Agent is rejected. "
                "Try again in a few minutes or switch to a different network.",
                status_code=403,
            )

        if resp.status_code == 404:
            raise RedditError("Subreddit or post not found on Reddit.", status_code=404)

        if resp.status_code >= 500:
            last_exception = RedditError(f"Reddit server error ({resp.status_code}). Retrying.", status_code=resp.status_code)
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_BACKOFF_BASE * (2 ** attempt))
                continue
            raise last_exception

        # Any other non-200
        raise RedditError(f"Reddit returned status {resp.status_code}.", status_code=resp.status_code)

    # Should not reach here, but safety net
    if last_exception:
        raise last_exception
    raise RedditError("Reddit request failed after all retries.", status_code=500)


# Alias for backward compatibility
async def _rate_limited_get(url: str, params: dict | None = None) -> dict:
    return await _rate_limited_get_with_retry(url, params)


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
