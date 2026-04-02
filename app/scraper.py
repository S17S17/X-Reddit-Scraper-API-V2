import asyncio
import json
import os
import time
from functools import wraps

import base64
import twikit
from twikit import Client
from twikit.errors import (
    TwitterException,
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    RequestTimeout,
    TooManyRequests,
    ServerError,
    UserNotFound,
    UserUnavailable,
    AccountSuspended,
    AccountLocked,
    TweetNotAvailable,
)
from app.config import TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD, COOKIES_FILE

# --- twikit 2.3.x bug fix ---
# When cookies are loaded but client_transaction.init() hasn't run (or failed),
# generate_transaction_id() crashes with "Couldn't get KEY_BYTE indices" or
# AttributeError: 'ClientTransaction' has no attribute 'key'.
# Fix: initialize safe defaults in __init__ AND patch generate_transaction_id
# to fall back to a random value instead of crashing.
_twikit_version = getattr(twikit, '__version__', '0.0.0')
_twikit_major = int(_twikit_version.split('.')[0])
_twikit_minor = int(_twikit_version.split('.')[1])
if _twikit_major == 2 and _twikit_minor >= 3:
    import secrets as _secrets
    from twikit.x_client_transaction.transaction import ClientTransaction
    _original_ct_init = ClientTransaction.__init__
    def _patched_ct_init(self):
        try:
            _original_ct_init(self)
        except Exception:
            pass
        if not getattr(self, 'key', None):
            self.key = base64.b64encode(b'\x00' * 48).decode()
        if not hasattr(self, 'animation_key'):
            self.animation_key = ""
        # KEY_BYTE_INDICES is a class attribute set after animation parsing;
        # if it's missing the transaction ID generation will crash.
        if not getattr(ClientTransaction, 'KEY_BYTE_INDICES', None):
            ClientTransaction.KEY_BYTE_INDICES = list(range(16))
    ClientTransaction.__init__ = _patched_ct_init

    # Patch generate_transaction_id: try the real method, fall back to random.
    _original_gen_tx = ClientTransaction.generate_transaction_id
    def _patched_gen_tx(self, *args, **kwargs):
        try:
            return _original_gen_tx(self, *args, **kwargs)
        except Exception:
            return base64.b64encode(_secrets.token_bytes(32)).decode().rstrip('=')
    ClientTransaction.generate_transaction_id = _patched_gen_tx
# --------------------------------

TWITTER_MAX_RETRIES = 3
TWITTER_RETRY_BACKOFF = 3.0  # seconds

client = Client("en-US")


class ScraperError(Exception):
    """Wrapper for scraper errors with HTTP status code mapping."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


def handle_twitter_error(e: Exception) -> ScraperError:
    """Map twikit exceptions to ScraperError with appropriate status codes."""
    if isinstance(e, (Unauthorized, AccountLocked)):
        return ScraperError(
            "Cookies expired or invalid. Call POST /auth/set-cookies to re-authenticate.",
            status_code=401,
        )
    if isinstance(e, (Forbidden, AccountSuspended)):
        return ScraperError(
            "Access forbidden. Account may be suspended or cookies expired. "
            "Call POST /auth/set-cookies to re-authenticate.",
            status_code=403,
        )
    if isinstance(e, (NotFound, UserNotFound, TweetNotAvailable)):
        return ScraperError("Resource not found on Twitter.", status_code=404)
    if isinstance(e, UserUnavailable):
        return ScraperError("User is unavailable on Twitter.", status_code=404)
    if isinstance(e, TooManyRequests):
        reset_time = getattr(e, 'rate_limit_reset', None)
        if reset_time:
            wait_seconds = max(0, int(reset_time - time.time()))
            minutes = max(1, wait_seconds // 60)
            return ScraperError(
                f"Rate limited by Twitter. Try again in ~{minutes} minute(s).",
                status_code=429,
            )
        return ScraperError(
            "Rate limited by Twitter. Try again in a few minutes.",
            status_code=429,
        )
    if isinstance(e, BadRequest):
        return ScraperError(f"Bad request to Twitter: {e}", status_code=400)
    if isinstance(e, RequestTimeout):
        return ScraperError(
            "Twitter request timed out. The Twitter browser session may be stale. "
            "Try refreshing cookies via POST /auth/set-cookies.",
            status_code=504,
        )
    if isinstance(e, ServerError):
        return ScraperError("Twitter server error. Try again later.", status_code=502)
    if isinstance(e, TwitterException):
        return ScraperError(f"Twitter API error: {e}", status_code=500)
    # Catchall for any other exception (including ConnectTimeout which twikit may raise as generic errors)
    error_msg = str(e)
    if "timeout" in error_msg.lower() or "connect" in error_msg.lower():
        return ScraperError(
            f"Twitter connection issue: {e}. Try refreshing cookies via POST /auth/set-cookies.",
            status_code=504,
        )
    return ScraperError(f"Unexpected error: {type(e).__name__}: {e}", status_code=500)


def _retry_on_timeout(func):
    """
    Decorator that retries twikit async functions up to TWITTER_MAX_RETRIES times
    on RequestTimeout and connection errors with exponential backoff.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(TWITTER_MAX_RETRIES):
            try:
                return await func(*args, **kwargs)
            except (RequestTimeout, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < TWITTER_MAX_RETRIES - 1:
                    await asyncio.sleep(TWITTER_RETRY_BACKOFF * (2 ** attempt))
                    continue
            except Exception as e:
                # Only retry on connection-related errors
                error_str = str(e).lower()
                if any(k in error_str for k in ["timeout", "connect", "connection", "network"]):
                    last_error = e
                    if attempt < TWITTER_MAX_RETRIES - 1:
                        await asyncio.sleep(TWITTER_RETRY_BACKOFF * (2 ** attempt))
                        continue
                # Non-connection error — don't retry, raise immediately
                raise
        # All retries exhausted
        raise handle_twitter_error(last_error)
    return wrapper


async def login():
    """Login to Twitter and save session cookies."""
    try:
        await client.login(
            auth_info_1=TWITTER_USERNAME,
            auth_info_2=TWITTER_EMAIL,
            password=TWITTER_PASSWORD,
        )
        client.save_cookies(COOKIES_FILE)
        return {"status": "ok", "message": "Logged in and session saved."}
    except Exception as e:
        raise handle_twitter_error(e)


def set_cookies(auth_token: str, ct0: str):
    """Manually set browser cookies and save them (Cloudflare bypass)."""
    client.set_cookies({
        "auth_token": auth_token,
        "ct0": ct0,
    })
    client.save_cookies(COOKIES_FILE)
    return {"status": "ok", "message": "Cookies saved. You are now logged in."}


async def load_session():
    """Load saved session cookies if they exist."""
    if os.path.exists(COOKIES_FILE):
        client.load_cookies(COOKIES_FILE)
        return True
    return False


@_retry_on_timeout
async def check_auth():
    """Check if current cookies are valid by fetching the authenticated user."""
    try:
        user = await client.user()
        return {
            "status": "ok",
            "authenticated": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "username": user.screen_name,
            },
        }
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_user(username: str):
    """Get a user's profile info."""
    try:
        user = await client.get_user_by_screen_name(username)
        return {
            "id": user.id,
            "name": user.name,
            "username": user.screen_name,
            "description": user.description,
            "followers_count": user.followers_count,
            "following_count": user.following_count,
            "tweet_count": user.statuses_count,
            "verified": user.is_blue_verified,
            "profile_image_url": user.profile_image_url,
            "created_at": user.created_at,
        }
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_user_tweets(username: str, count: int = 20):
    """Get recent tweets from a user."""
    try:
        user = await client.get_user_by_screen_name(username)
        tweets = await client.get_user_tweets(user.id, "Tweets", count=count)
        results = []
        for tweet in tweets:
            try:
                results.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "favorite_count": tweet.favorite_count,
                    "retweet_count": tweet.retweet_count,
                    "reply_count": tweet.reply_count,
                    "view_count": tweet.view_count,
                })
            except Exception:
                # Skip malformed tweets — don't let one bad tweet crash the whole request
                continue
        return {"username": username, "count": len(results), "tweets": results}
    except Exception as e:
        raise handle_twitter_error(e)


SEARCH_PRODUCTS = ("Top", "Latest", "Media", "Photos", "Videos")


@_retry_on_timeout
async def search_tweets(query: str, count: int = 20, product: str = "Latest"):
    """Search tweets by keyword or hashtag with fallback logic."""
    if product not in SEARCH_PRODUCTS:
        raise ScraperError(
            f"Invalid product '{product}'. Must be one of: {', '.join(SEARCH_PRODUCTS)}",
            status_code=400,
        )

    try:
        tweets = await client.search_tweet(query, product, count=count)
    except NotFound:
        # Fallback: if requested product returns 404, try the other option
        fallback = "Top" if product == "Latest" else "Latest"
        try:
            tweets = await client.search_tweet(query, fallback, count=count)
        except Exception as e:
            raise handle_twitter_error(e)
    except Exception as e:
        raise handle_twitter_error(e)

    results = []
    for tweet in tweets:
        results.append({
            "id": tweet.id,
            "text": tweet.text,
            "created_at": tweet.created_at,
            "user": {
                "name": tweet.user.name,
                "username": tweet.user.screen_name,
            },
            "favorite_count": tweet.favorite_count,
            "retweet_count": tweet.retweet_count,
            "reply_count": tweet.reply_count,
            "view_count": tweet.view_count,
        })
    return {"query": query, "count": len(results), "tweets": results}


@_retry_on_timeout
async def get_trends(category: str = "trending"):
    """Get current trending topics by category."""
    try:
        trends = await client.get_trends(category)
        results = []
        for trend in trends:
            results.append({
                "name": trend.name,
                "tweet_count": trend.tweets_count,
            })
        return {"category": category, "count": len(results), "trends": results}
    except Exception as e:
        raise handle_twitter_error(e)


def _serialize_tweet_full(tweet):
    """Serialize a tweet object with all available fields."""
    data = {
        "id": tweet.id,
        "text": tweet.text,
        "created_at": tweet.created_at,
        "user": {
            "name": tweet.user.name,
            "username": tweet.user.screen_name,
            "profile_image_url": tweet.user.profile_image_url,
        },
        "favorite_count": tweet.favorite_count,
        "retweet_count": tweet.retweet_count,
        "reply_count": tweet.reply_count,
        "view_count": tweet.view_count,
        "quote_count": tweet.quote_count,
        "bookmark_count": tweet.bookmark_count,
        "lang": tweet.lang,
        "hashtags": tweet.hashtags,
        "is_quote_status": tweet.is_quote_status,
        "in_reply_to": tweet.in_reply_to,
        "media": [
            {
                "type": getattr(m, "type", None) or (m.get("type") if isinstance(m, dict) else None),
                "url": getattr(m, "media_url_https", None) or (m.get("media_url_https") if isinstance(m, dict) else None),
                "expanded_url": getattr(m, "expanded_url", None) or (m.get("expanded_url") if isinstance(m, dict) else None),
            }
            for m in (tweet.media or [])
        ],
    }
    return data


def _serialize_user(user):
    """Serialize a user object with profile fields."""
    return {
        "id": user.id,
        "name": user.name,
        "username": user.screen_name,
        "description": user.description,
        "followers_count": user.followers_count,
        "following_count": user.following_count,
        "tweet_count": user.statuses_count,
        "verified": user.is_blue_verified,
        "profile_image_url": user.profile_image_url,
    }


@_retry_on_timeout
async def get_tweet_by_id(tweet_id: str):
    """Get a single tweet by its ID."""
    try:
        tweet = await client.get_tweet_by_id(tweet_id)
        return _serialize_tweet_full(tweet)
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_tweet_replies(tweet_id: str, count: int = 20):
    """Get replies to a specific tweet."""
    try:
        tweet = await client.get_tweet_by_id(tweet_id)
        replies = tweet.replies
        results = []
        for reply in (replies or [])[:count]:
            results.append(_serialize_tweet_full(reply))
        return {"tweet_id": tweet_id, "count": len(results), "replies": results}
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def search_users(query: str, count: int = 20):
    """Search users by query string."""
    try:
        users = await client.search_user(query, count=count)
        results = []
        for user in users:
            results.append(_serialize_user(user))
        return {"query": query, "count": len(results), "users": results}
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_user_followers(username: str, count: int = 20):
    """Get a user's followers."""
    try:
        user = await client.get_user_by_screen_name(username)
        followers = await client.get_user_followers(user.id, count=count)
        results = []
        for u in followers:
            results.append(_serialize_user(u))
        return {"username": username, "count": len(results), "users": results}
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_user_following(username: str, count: int = 20):
    """Get users that a user is following."""
    try:
        user = await client.get_user_by_screen_name(username)
        following = await client.get_user_following(user.id, count=count)
        results = []
        for u in following:
            results.append(_serialize_user(u))
        return {"username": username, "count": len(results), "users": results}
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_user_media(username: str, count: int = 20):
    """Get a user's media tweets."""
    try:
        user = await client.get_user_by_screen_name(username)
        tweets = await client.get_user_tweets(user.id, "Media", count=count)
        results = []
        for tweet in tweets:
            results.append(_serialize_tweet_full(tweet))
        return {"username": username, "count": len(results), "tweets": results}
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_user_likes(username: str, count: int = 20):
    """Get tweets liked by a user."""
    try:
        user = await client.get_user_by_screen_name(username)
        tweets = await client.get_liked_tweets(user.id, count=count)
        results = []
        for tweet in tweets:
            results.append(_serialize_tweet_full(tweet))
        return {"username": username, "count": len(results), "tweets": results}
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_user_lists(username: str):
    """Get a user's Twitter lists."""
    try:
        user = await client.get_user_by_screen_name(username)
        lists = await client.get_lists(user.id)
        results = []
        for lst in lists:
            results.append({
                "id": lst.id,
                "name": lst.name,
                "description": lst.description,
                "member_count": lst.member_count,
                "subscriber_count": lst.subscriber_count,
                "mode": lst.mode,
            })
        return {"username": username, "count": len(results), "lists": results}
    except Exception as e:
        raise handle_twitter_error(e)


@_retry_on_timeout
async def get_list_tweets(list_id: str, count: int = 20):
    """Get tweets from a specific Twitter list."""
    try:
        tweets = await client.get_list_tweets(list_id, count=count)
        results = []
        for tweet in tweets:
            results.append(_serialize_tweet_full(tweet))
        return {"list_id": list_id, "count": len(results), "tweets": results}
    except Exception as e:
        raise handle_twitter_error(e)
