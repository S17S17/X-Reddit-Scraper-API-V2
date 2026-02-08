from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from app.config import API_KEY
from app import scraper

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
    title="Twitter/X Scraper API",
    description="Scrapes Twitter/X data for n8n workflows. Replaces paid services like Apify.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Health check - shows if env vars are loaded (no auth needed)."""
    return {
        "status": "ok",
        "api_key_set": API_KEY != "change-me",
        "api_key_length": len(API_KEY),
        "api_key_preview": API_KEY[:3] + "***" if len(API_KEY) > 3 else "***",
    }


class CookiesInput(BaseModel):
    auth_token: str
    ct0: str


@app.post("/auth/login")
async def login(_: str = Security(verify_api_key)):
    """Login to Twitter with your credentials (one-time). Saves session cookies."""
    try:
        result = await scraper.login()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/set-cookies")
async def set_cookies(cookies: CookiesInput, _: str = Security(verify_api_key)):
    """Manually set browser cookies to bypass Cloudflare. See /docs for instructions."""
    try:
        result = scraper.set_cookies(cookies.auth_token, cookies.ct0)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{username}")
async def get_user(username: str, _: str = Security(verify_api_key)):
    """Get a user's profile info."""
    try:
        return await scraper.get_user(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{username}/tweets")
async def get_user_tweets(
    username: str,
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Get recent tweets from a user."""
    try:
        return await scraper.get_user_tweets(username, count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/tweets")
async def search_tweets(
    query: str = Query(..., min_length=1),
    count: int = Query(default=20, ge=1, le=100),
    _: str = Security(verify_api_key),
):
    """Search tweets by keyword or hashtag."""
    try:
        return await scraper.search_tweets(query, count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trends")
async def get_trends(_: str = Security(verify_api_key)):
    """Get current trending topics."""
    try:
        return await scraper.get_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
