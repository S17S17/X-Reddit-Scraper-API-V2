import json
import os

from twikit import Client
from app.config import TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD, COOKIES_FILE


client = Client("en-US")


async def login():
    """Login to Twitter and save session cookies."""
    await client.login(
        auth_info_1=TWITTER_USERNAME,
        auth_info_2=TWITTER_EMAIL,
        password=TWITTER_PASSWORD,
    )
    client.save_cookies(COOKIES_FILE)
    return {"status": "ok", "message": "Logged in and session saved."}


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


async def get_user(username: str):
    """Get a user's profile info."""
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


async def get_user_tweets(username: str, count: int = 20):
    """Get recent tweets from a user."""
    user = await client.get_user_by_screen_name(username)
    tweets = await client.get_user_tweets(user.id, "Tweets", count=count)
    results = []
    for tweet in tweets:
        results.append({
            "id": tweet.id,
            "text": tweet.text,
            "created_at": tweet.created_at,
            "favorite_count": tweet.favorite_count,
            "retweet_count": tweet.retweet_count,
            "reply_count": tweet.reply_count,
            "view_count": tweet.view_count,
        })
    return results


async def search_tweets(query: str, count: int = 20):
    """Search tweets by keyword or hashtag."""
    tweets = await client.search_tweet(query, "Latest", count=count)
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
    return results


async def get_trends():
    """Get current trending topics."""
    trends = await client.get_trends("trending", retry=False)
    results = []
    for trend in trends:
        results.append({
            "name": trend.name,
            "tweet_count": trend.tweets_count,
        })
    return results
