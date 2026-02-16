# Twitter/X & Reddit Scraper API

A free, self-hosted REST API that scrapes **Twitter/X** and **Reddit** data. Built with FastAPI, designed for automation workflows (n8n, Make, Zapier) and AI agent pipelines.

**No paid API keys needed.** Twitter uses your own session cookies. Reddit uses public endpoints.

## Features

- **22 API endpoints** across Twitter/X and Reddit
- **Twitter/X**: User profiles, tweets, followers, following, media, likes, lists, search, trends, tweet details, replies
- **Reddit**: Subreddit posts, cross-platform search, post details, comments
- **API key auth** via `X-API-Key` header
- **Auto-generated Swagger docs** at `/docs`
- **Endpoint discovery** at `/endpoints` (no auth required)
- **Search fallback**: Tweet search auto-retries with alternate product type on 404
- **Rate limiting**: Built-in Reddit rate limiter (6.5s between requests)
- **n8n-ready**: Clean JSON responses, designed for HTTP Request nodes and AI agent tools

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Twitter Scraper | [twikit](https://github.com/d60/twikit) |
| Reddit Scraper | [httpx](https://www.python-httpx.org/) + Reddit `.json` endpoints |
| Server | Uvicorn |
| Hosting | [Railway](https://railway.app/) (free tier) |

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/S17S17/twitter-scraper-api.git
cd twitter-scraper-api
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
TWITTER_USERNAME=your_twitter_handle
TWITTER_EMAIL=your_email@example.com
TWITTER_PASSWORD=your_password
API_KEY=pick-any-secret-string
COOKIES_FILE=cookies.json
```

### 3. Run

```bash
python -m uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger UI.

### 4. Authenticate Twitter

Twitter's Cloudflare blocks programmatic login. Use browser cookie injection instead:

1. Open Chrome, go to [x.com](https://x.com) (logged in)
2. Press **F12** > **Application** > **Cookies** > `https://x.com`
3. Copy the `auth_token` and `ct0` values
4. Send them to the API:

```bash
curl -X POST http://localhost:8000/auth/set-cookies \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"auth_token": "YOUR_AUTH_TOKEN", "ct0": "YOUR_CT0"}'
```

### 5. Test Reddit (works immediately)

Reddit endpoints need no cookies — just your API key:

```bash
curl http://localhost:8000/reddit/subreddit/artificial?sort=hot&count=5 \
  -H "X-API-Key: YOUR_API_KEY"
```

## All 22 Endpoints

### Utility (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/endpoints` | List all endpoints with descriptions and params |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login with Twitter credentials |
| POST | `/auth/set-cookies` | Manual cookie injection (recommended) |
| GET | `/auth/status` | Check if cookies are valid |

### Twitter - Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user/{username}` | User profile |
| GET | `/user/{username}/tweets` | User's tweets |
| GET | `/user/{username}/followers` | User's followers |
| GET | `/user/{username}/following` | Who the user follows |
| GET | `/user/{username}/media` | User's media tweets |
| GET | `/user/{username}/likes` | Tweets liked by user |
| GET | `/user/{username}/lists` | User's Twitter lists |

### Twitter - Tweets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tweet/{tweet_id}` | Full tweet details |
| GET | `/tweet/{tweet_id}/replies` | Replies to a tweet |

### Twitter - Search & Discovery

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search/tweets` | Search tweets (supports Top/Latest/Media/Photos/Videos) |
| GET | `/search/users` | Search users |
| GET | `/trends` | Trending topics (trending/for-you/news/sports/entertainment) |
| GET | `/list/{list_id}/tweets` | Tweets from a Twitter list |

### Reddit

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reddit/subreddit/{name}` | Subreddit posts (hot/new/top/rising) |
| GET | `/reddit/search` | Search all of Reddit |
| GET | `/reddit/post/{post_id}` | Post details by ID |
| GET | `/reddit/post/{post_id}/comments` | Post comments |

Most endpoints accept `count` (1-100) as a query parameter. Reddit endpoints also accept `sort` and `time_filter`.

## Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app/) > **New Project** > **Deploy from GitHub**
3. Add environment variables in the Railway dashboard (same as `.env`)
4. Generate a domain
5. Call `/auth/set-cookies` on the Railway URL to authenticate Twitter

> **Note:** Railway's filesystem resets on each deploy. You'll need to re-inject Twitter cookies after every deployment.

## n8n Integration

This API is designed for [n8n](https://n8n.io/) workflow automation.

### Setup in n8n

1. Go to **Credentials** > **Add Credential** > **Header Auth**
2. Set **Name** to `Scraper API Key`
3. Set **Header Name** to `X-API-Key` and **Header Value** to your API key
4. Use this credential in all HTTP Request nodes

### HTTP Request Node Example

```
Method: GET
URL: https://your-app.up.railway.app/search/tweets?query=AI%20automation&count=15
Authentication: Predefined Credential Type > Header Auth > Scraper API Key
```

See the included guide docs for detailed n8n configurations:
- `n8n-http-request-guide.md` — Full guide for all 22 endpoints as HTTP Request nodes
- `n8n-twitter-tools-guide.md` — Guide for adding endpoints as AI agent tool nodes

## Project Structure

```
app/
  __init__.py       # Package marker
  main.py           # FastAPI app, all routes, API key auth, error handlers
  scraper.py        # Twitter scraper wrapping twikit
  reddit.py         # Reddit scraper using httpx + .json endpoints
  config.py         # Environment variable loading
requirements.txt    # Python dependencies
Procfile            # Railway deployment command
runtime.txt         # Python version for Railway
.env.example        # Environment variable template
```

## Security Notes

- **API key auth**: Every endpoint (except `/health` and `/endpoints`) requires the `X-API-Key` header
- **No credentials in code**: All secrets live in environment variables
- **Cookie-based Twitter auth**: Uses your own browser session — no Twitter API developer account needed
- **Reddit is public**: Uses Reddit's public `.json` endpoints with a User-Agent header — no Reddit API registration
- **Rate limiting**: Reddit requests are rate-limited to ~10/min internally to avoid 429 errors

### Important

- **Change your API key** from the default. Use a strong, random string.
- **Never commit `.env` or `cookies.json`** — they're in `.gitignore` by default.
- **Twitter cookies expire** — re-extract from your browser periodically.
- **This is for personal/educational use.** Respect Twitter and Reddit's terms of service.

## Known Limitations

| Limitation | Workaround |
|-----------|-----------|
| Cloudflare blocks Twitter login | Use `/auth/set-cookies` with browser cookies |
| Railway resets filesystem on deploy | Re-inject cookies after each deploy |
| `/trends` may return empty | Twitter limitation with cookie-only auth |
| Reddit selftext truncated at 2000 chars | By design, to keep responses manageable |

## License

[MIT](LICENSE)

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-endpoint`)
3. Commit your changes
4. Push to the branch (`git push origin feature/new-endpoint`)
5. Open a Pull Request

## Built With

Built using [Claude Code](https://claude.ai/claude-code) by Anthropic.
