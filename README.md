<img width="1024" height="572" alt="github repo thumbnail" src="https://github.com/user-attachments/assets/e423913b-2481-4197-9955-d06e41c800e4" />

# FREE Twitter/X & Reddit Scraper API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet)](https://railway.app)
[![n8n Compatible](https://img.shields.io/badge/n8n-Compatible-orange)](https://n8n.io)

⭐ **Star this repo if it saves you time!**

A free, self-hosted REST API that scrapes **Twitter/X** and **Reddit** data. Built with FastAPI, designed for automation workflows (n8n, Make, Zapier) and AI agent pipelines.

**No paid API keys needed.** Twitter uses your own session cookies. Reddit uses public endpoints.

## What You Can Build

- 🤖 **AI Agent Tools** - Turn all 22 endpoints into MCP tools for Claude/ChatGPT
- 📊 **Daily Intelligence Feeds** - Auto-scrape Twitter + Reddit into Airtable
- 📈 **Trend Monitors** - Track keywords and get Slack alerts
- 🧵 **Thread Generators** - Find trending topics → write threads automatically
- 🔍 **Competitor Spies** - Monitor accounts and hashtags in real-time

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
| Hosting | [Railway](https://railway.app/) (free tier) or Local + ngrok |

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

## Local Hosting + ngrok (Recommended for Twitter)

> **Why run locally?** Cloud providers use datacenter IPs that Twitter actively flags and blocks (403 errors). Your home IP is a residential IP — platforms trust it. Running locally is stealth mode. **This is especially important for Twitter endpoints.** Reddit works fine on Railway since it uses public endpoints.

### Why Local Beats Cloud for Twitter

| | Cloud (Railway) | Local + ngrok |
|---|---|---|
| IP Type | Datacenter (flagged) | Residential (trusted) |
| Block Rate | High | Low |
| Cost | Free tier | Free |
| Setup | Easy, but fails | Requires tunnel |

### Setup: Local + ngrok in 4 Steps

**Step 1 — Run the API locally**

```bash
python -m uvicorn app.main:app --reload
```

You should see: `Uvicorn running on http://127.0.0.1:8000`

**Step 2 — Install and run ngrok**

[Download ngrok](https://ngrok.com/download), then in a **new terminal**:

```bash
ngrok http 8000
```

Copy the `Forwarding` URL — it looks like:
```
https://YOUR-ID.ngrok-free.app -> http://localhost:8000
```

**Step 3 — Use the ngrok URL in n8n**

Replace your Railway URL with the ngrok URL in all HTTP Request nodes:

```
https://YOUR-ID.ngrok-free.app/search/tweets?query=AI&count=15
```

**Step 4 — Handle the changing URL**

Free ngrok generates a new URL every restart. To avoid updating every n8n node each time:

1. Create a **Global Variable** in n8n called `SCRAPER_URL`
2. Set its value to your current ngrok URL
3. Reference it in all nodes as `{{ $vars.SCRAPER_URL }}/search/tweets?...`

Now when ngrok restarts, you only update one place.

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `403 Forbidden` | Datacenter IP blocked | Switch to Local + ngrok |
| `ModuleNotFoundError` | Missing dependencies | Run `pip install -r requirements.txt` |
| `Connection Refused` | Server not running | Check Terminal 1 — restart uvicorn |
| `502 Bad Gateway` | Python server crashed | Restart uvicorn, keep ngrok running |
| `ERR_NGROK_6022` | Free URL expired | Run `ngrok http 8000` again, update n8n |

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
- [API-ENDPOINTS-GUIDE.md](API-ENDPOINTS-GUIDE.md) — Complete guide for all 22 endpoints with visual URL breakdowns and step-by-step instructions
- [n8n-http-request-guide.md](n8n-http-request-guide.md) — Quick reference for HTTP Request nodes in n8n workflows

### Ready-to-Import Workflows

Download these from the [/workflows](workflows/) folder and import directly into n8n:

| Workflow | Description |
|---|---|
| [Daily AI Intelligence Feed](workflows/Daily_AI_Intelligence_Feed.json) | Scrapes Twitter + Reddit + HN + Google News every morning into Airtable |
| [Twitter & Reddit MCP Server](workflows/Twitter%20%26%20Reddit%20Scraper%20MCP%20%28tuto%29.json) | Turns all 22 endpoints into AI agent tools for Claude/ChatGPT |

## Project Structure

```
app/
  __init__.py       # Package marker
  main.py           # FastAPI app, all routes, API key auth, error handlers
  scraper.py        # Twitter scraper wrapping twikit
  reddit.py         # Reddit scraper using httpx + .json endpoints
  config.py         # Environment variable loading
workflows/
  Daily_AI_Intelligence_Feed.json
  Twitter & Reddit Scraper MCP (tuto).json
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
| Twitter blocked on cloud IPs | Use Local + ngrok setup |

## License

[MIT](LICENSE)

## Contributing

Pull requests are welcome! Areas where contributions would be especially valuable:

- Additional Reddit endpoints (user profiles, comment threads)
- Twitter Spaces support
- Rate limiting improvements
- Error handling enhancements
- Additional n8n workflow examples

**How to contribute:**

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-endpoint`)
3. Commit your changes
4. Push to the branch (`git push origin feature/new-endpoint`)
5. Open a Pull Request

## Get Support & Exclusive Workflows

- 💬 [Join Agentic AI Society](https://skool.com/eye-on-ai-9025) for premium workflows and automation deep dives
- 🐦 Follow [@Semah____](https://twitter.com/Semah____) for AI automation tips
- ⭐ Star this repo to support the project
- 🐛 Report issues on [GitHub Issues](https://github.com/S17S17/twitter-scraper-api/issues)

---

**Built by [Semah AI](https://skool.com/eye-on-ai-9025)** — Automating the future, one API at a time.
