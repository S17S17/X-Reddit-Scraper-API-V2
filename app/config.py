import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")
API_KEY = os.getenv("API_KEY", "change-me").strip()
COOKIES_FILE = os.getenv("COOKIES_FILE", "cookies.json")
