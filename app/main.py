from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from app.config import API_KEY
from app import scraper, reddit
from app.scraper import ScraperError
from app.reddit import RedditError

api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key


@asynccontextmanager
async def lifespan(app: FastAPI):
    loaded = await scraper.load_session()
    if loaded:
        print("Session cookies loaded.")
    else:
        print("No saved session. Call POST /auth/login first.")
    yield


app = FastAPI(
    title="Twitter/X & Reddit Scraper API",
    description=(
        "Free, self-hosted Twitter/X + Reddit scraper API. "
        "Replaces paid services like Apify ($29/mo). "
        "22 endpoints: Twitter (user profiles, tweets, followers, following, likes, media, "
        "lists, search, trends, replies) + Reddit (subreddits, search, post details, comments). "
        "Built for n8n workflow automation and the TTE Intelligence Pipeline."
    ),
    version="3.1.0",
    lifespan=lifespan,
)


@app.exception_handler(ScraperError)
async def scraper_error_handler(request: Request, exc: ScraperError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


@app.exception_handler(RedditError)
async def reddit_error_handler(request: Request, exc: RedditError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


class CookiesInput(BaseModel):
    auth_token: str
    ct0: str


# --- Health & Auth ---


@app.get("/health")
async def health():
    """Basic health check. No auth required."""
    return {"status": "ok", "version": "3.1.0", "endpoints": 22}


@app.get("/endpoints")
async def list_endpoints():
    """List all available API endpoints. No auth required. Useful for n8n agent discovery."""
    return {
        "version": "3.1.0",
        "total_endpoints": 22,
        "auth": [
            {"method": "POST", "path": "/auth/login", "description": "Login with credentials"},
            {"method": "POST", "path": "/auth/set-cookies", "description": "Set browser cookies (Cloudflare bypass)"},
            {"method": "GET", "path": "/auth/status", "description": "Check if cookies are valid"},
        ],
        "users": [
            {"method": "GET", "path": "/user/{username}", "description": "Get user profile"},
            {"method": "GET", "path": "/user/{username}/tweets", "description": "Get user's tweets", "params": "count"},
            {"method": "GET", "path": "/user/{username}/followers", "description": "Get user's followers", "params": "count"},
            {"method": "GET", "path": "/user/{username}/following", "description": "Get who user follows", "params": "count"},
            {"method": "GET", "path": "/user/{username}/media", "description": "Get user's media tweets", "params": "count"},
            {"method": "GET", "path": "/user/{username}/likes", "description": "Get user's liked tweets", "params": "count"},
            {"method": "GET", "path": "/user/{username}/lists", "description": "Get user's Twitter lists"},
        ],
        "tweets": [
            {"method": "GET", "path": "/tweet/{tweet_id}", "description": "Get tweet by ID with full details"},
            {"method": "GET", "path": "/tweet/{tweet_id}/replies", "description": "Get replies to a tweet", "params": "count"},
        ],
        "search": [
            {"method": "GET", "path": "/search/tweets", "description": "Search tweets", "params": "query, count, product (Top/Latest/Media/Photos/Videos)"},
            {"method": "GET", "path": "/search/users", "description": "Search users", "params": "query, count"},
        ],
        "trends": [
            {"method": "GET", "path": "/trends", "description": "Get trending topics", "params": "category (trending/for-you/news/sports/entertainment)"},
        ],
        "lists": [
            {"method": "GET", "path": "/list/{list_id}/tweets", "description": "Get tweets from a list", "params": "count"},
        ],
        "reddit": [
            {"method": "GET", "path": "/reddit/subreddit/{name}", "description": "Get subreddit posts", "params": "sort (hot/new/top/rising), time_filter, count"},
            {"method": "GET", "path": "/reddit/search", "description": "Search Reddit posts", "params": "query, sort, time_filter, count"},
            {"method": "GET", "path": "/reddit/post/{post_id}", "description": "Get post details by ID"},
            {"method": "GET", "path": "/reddit/post/{post_id}/comments", "description": "Get post comments", "params": "count, sort"},
        ],
    }


@app.get("/auth/status")
async def auth_status(_: str = Security(verify_api_key)):
    """Check if current cookies are valid."""
    return await scraper.check_auth()


@app.post("/auth/login")
async def login(_: str = Security(verify_api_key)):
    """Login to Twitter with your credentials (one-time). Saves session cookies."""
    return await scraper.login()


@app.post("/auth/set-cookies")
async def set_cookies(cookies: CookiesInput, _: str = Security(verify_api_key)):
    """Manually set browser cookies to bypass Cloudflare. See /docs for instructions."""
    result = scraper.set_cookies(cookies.auth_token, cookies.ct0)
    return result


# --- User endpoints ---


@app.get("/user/{username}")
async def get_user(username: str, _: str = Security(verify_api_key)):
    """Get a user's profile info."""
    return await scraper.get_user(username)


@app.get("/user/{username}/tweets")
async def get_user_tweets(
    username: str,
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get recent tweets from a user."""
    return await scraper.get_user_tweets(username, count)


@app.get("/user/{username}/followers")
async def get_user_followers(
    username: str,
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get a user's followers."""
    return await scraper.get_user_followers(username, count)


@app.get("/user/{username}/following")
async def get_user_following(
    username: str,
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get users that a user is following."""
    return await scraper.get_user_following(username, count)


@app.get("/user/{username}/media")
async def get_user_media(
    username: str,
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get a user's media tweets (photos, videos)."""
    return await scraper.get_user_media(username, count)


@app.get("/user/{username}/likes")
async def get_user_likes(
    username: str,
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get tweets liked by a user."""
    return await scraper.get_user_likes(username, count)


@app.get("/user/{username}/lists")
async def get_user_lists(
    username: str,
    _: str = Security(verify_api_key),
):
    """Get a user's Twitter lists."""
    return await scraper.get_user_lists(username)


# --- Tweet endpoints ---


@app.get("/tweet/{tweet_id}")
async def get_tweet_by_id(tweet_id: str, _: str = Security(verify_api_key)):
    """Get a single tweet by its ID with full details."""
    return await scraper.get_tweet_by_id(tweet_id)


@app.get("/tweet/{tweet_id}/replies")
async def get_tweet_replies(
    tweet_id: str,
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get replies to a specific tweet."""
    return await scraper.get_tweet_replies(tweet_id, count)


# --- Search endpoints ---


@app.get("/search/tweets")
async def search_tweets(
    query: str = Query(..., min_length=1),
    count: int = Query(default=20, ge=1, le=100),
    product: str = Query(default="Latest", pattern="^(Top|Latest|Media|Photos|Videos)$"),
    _: str = Security(verify_api_key),
):
    """Search tweets by keyword or hashtag. Product: Top, Latest, Media, Photos, Videos."""
    return await scraper.search_tweets(query, count, product)


@app.get("/search/users")
async def search_users(
    query: str = Query(..., min_length=1),
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Search for users by query string."""
    return await scraper.search_users(query, count)


# --- Trends ---


@app.get("/trends")
async def get_trends(
    category: str = Query(default="trending", pattern="^(trending|for-you|news|sports|entertainment)$"),
    _: str = Security(verify_api_key),
):
    """Get current trending topics. Categories: trending, for-you, news, sports, entertainment."""
    return await scraper.get_trends(category)


# --- Lists ---


@app.get("/list/{list_id}/tweets")
async def get_list_tweets(
    list_id: str,
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get tweets from a specific Twitter list."""
    return await scraper.get_list_tweets(list_id, count)


# --- Reddit endpoints ---


@app.get("/reddit/subreddit/{name}")
async def get_subreddit_posts(
    name: str,
    sort: str = Query(default="hot", pattern="^(hot|new|top|rising)$"),
    time_filter: str = Query(default="day", pattern="^(hour|day|week|month|year|all)$"),
    count: int = Query(default=25, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get posts from a subreddit. Sort: hot, new, top, rising. Time filter applies to 'top' sort."""
    return await reddit.get_subreddit_posts(name, sort, time_filter, count)


@app.get("/reddit/search")
async def search_reddit(
    query: str = Query(..., min_length=1),
    sort: str = Query(default="relevance", pattern="^(relevance|hot|top|new|comments)$"),
    time_filter: str = Query(default="week", pattern="^(hour|day|week|month|year|all)$"),
    count: int = Query(default=25, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Search Reddit posts across all subreddits."""
    return await reddit.search_reddit(query, sort, time_filter, count)


@app.get("/reddit/post/{post_id}")
async def get_post_details(
    post_id: str,
    _: str = Security(verify_api_key),
):
    """Get full details of a Reddit post by ID (without comments)."""
    return await reddit.get_post_details(post_id)


@app.get("/reddit/post/{post_id}/comments")
async def get_post_comments(
    post_id: str,
    count: int = Query(default=25, ge=1, le=100),
    sort: str = Query(default="best", pattern="^(best|top|new|controversial|old|qa)$"),
    _: str = Security(verify_api_key),
):
    """Get comments on a Reddit post."""
    return await reddit.get_post_comments(post_id, count, sort)
