# n8n HTTP Request Node Guide — All 21 API Endpoints (v3.0.0)

> **API Base URL:** `https://your-app.up.railway.app`
> **Auth:** Header `X-API-Key: YOUR_API_KEY`

---

## Table of Contents

1. [Authentication Setup (Do This First)](#1-authentication-setup)
2. [Two Types of HTTP Request Nodes](#2-two-types-of-http-request-nodes)
3. [Twitter Endpoints (15)](#3-twitter-endpoints)
4. [Reddit Endpoints (3)](#4-reddit-endpoints)
5. [Utility Endpoints (3)](#5-utility-endpoints)
6. [Quick Reference Table](#6-quick-reference-table)
7. [Common Mistakes & Fixes](#7-common-mistakes--fixes)

---

## 1. Authentication Setup

Every endpoint (except `/health` and `/endpoints`) requires your API key.

### Option A: Credential (Recommended — Reusable)

1. In n8n, go to **Credentials** → **Add Credential**
2. Search for **Header Auth**
3. Configure:
   | Field | Value |
   |-------|-------|
   | **Name** | `Twitter Reddit API Key` |
   | **Header Name** | `X-API-Key` |
   | **Header Value** | `YOUR_API_KEY` |
4. Save. Now every HTTP Request node can reuse this credential.

### Option B: Manual Header (Per Node)

In each HTTP Request node:
1. Scroll to **Headers**
2. Click **Add Header**
3. Name: `X-API-Key`, Value: `YOUR_API_KEY`

> **Use Option A** — you set it once, and every node just selects the credential from a dropdown.

---

## 2. Two Types of HTTP Request Nodes

### Type 1: Regular HTTP Request Node

- **What:** Standard node in the workflow canvas
- **When:** For fetching data in a pipeline (e.g., daily intelligence feed, data collection)
- **Node type:** `HTTP Request` (find it in the node panel)
- **All query params go in the URL directly** — this is the most reliable approach

### Type 2: HTTP Request Tool Node

- **What:** AI agent tool — the agent decides when/how to call it
- **When:** Connected to an AI Agent node as a tool (e.g., repurpose content workflow)
- **Node type:** `HTTP Request Tool` (find it under AI → Tools)
- **Uses `$fromAI()` expressions** so the agent fills in dynamic values
- **URL must start with `=`** to enable expression mode

> This guide covers **Type 1** (regular nodes). For Type 2 (AI agent tools), see `n8n-twitter-tools-guide.md`.

---

## 3. Twitter Endpoints

### 3.1 Search Tweets

The most useful endpoint. Search any topic and get live tweets.

**Node Configuration:**

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/search/tweets?query=YOUR_QUERY&count=20` |
| **Authentication** | Predefined Credential Type → Header Auth → `Twitter Reddit API Key` |
| **Options → Always Output Data** | ON (recommended) |
| **Options → Never Error** | ON (recommended for pipelines) |

**URL Parameters:**

| Param | Required | Default | Options | Example |
|-------|----------|---------|---------|---------|
| `query` | Yes | — | Any text | `AI automation tools` |
| `count` | No | 20 | 1-100 | `15` |
| `product` | No | Latest | `Top`, `Latest`, `Media`, `Photos`, `Videos` | `Latest` |

**Example URLs:**
```
# Basic search
https://your-app.up.railway.app/search/tweets?query=AI%20automation%20tools&count=15

# Search with product type
https://your-app.up.railway.app/search/tweets?query=Claude%20AI&count=20&product=Top

# OR query (use %20OR%20 for spaces around OR)
https://your-app.up.railway.app/search/tweets?query=n8n%20workflow%20OR%20n8n%20automation&count=15
```

**Response format:**
```json
{
  "query": "AI automation tools",
  "count": 15,
  "tweets": [
    {
      "id": "YOUR_API_KEY7890",
      "text": "Just discovered this amazing AI automation...",
      "created_at": "Mon Feb 09 10:30:00 +0000 2026",
      "user": { "name": "John", "username": "john_ai" },
      "favorite_count": 42,
      "retweet_count": 12,
      "reply_count": 5,
      "view_count": 1500
    }
  ]
}
```

**To access tweets in the next node:** `{{ $json.tweets }}` (array) or loop with a Code node.

---

### 3.2 Search Users

Find Twitter users by name or topic.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/search/users?query=YOUR_QUERY&count=20` |
| **Auth** | Header Auth credential |

**URL Parameters:**

| Param | Required | Default | Example |
|-------|----------|---------|---------|
| `query` | Yes | — | `AI researcher` |
| `count` | No | 20 | `10` |

**Example URL:**
```
https://your-app.up.railway.app/search/users?query=AI%20researcher&count=10
```

**Response:** `{ "query": "...", "count": N, "users": [{ "id", "name", "username", "description", "followers_count", "following_count", "tweet_count", "verified", "profile_image_url" }] }`

---

### 3.3 Get User Profile

Get a specific user's full profile info.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/user/USERNAME` |
| **Auth** | Header Auth credential |

**Replace `USERNAME` with the actual username (no @ symbol).**

**Example URLs:**
```
https://your-app.up.railway.app/user/elonmusk
https://your-app.up.railway.app/user/AnthropicAI
```

**Response:**
```json
{
  "id": "YOUR_API_KEY",
  "name": "Anthropic",
  "username": "AnthropicAI",
  "description": "AI safety company...",
  "followers_count": 250000,
  "following_count": 50,
  "tweet_count": 1200,
  "verified": true,
  "profile_image_url": "https://...",
  "created_at": "..."
}
```

---

### 3.4 Get User Tweets

Get recent tweets from a specific user.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/user/USERNAME/tweets?count=20` |
| **Auth** | Header Auth credential |

**URL Parameters:**

| Param | Required | Default | Example |
|-------|----------|---------|---------|
| `count` | No | 20 | `10` |

**Example URL:**
```
https://your-app.up.railway.app/user/AnthropicAI/tweets?count=10
```

**Response:** `{ "username": "AnthropicAI", "count": 10, "tweets": [{ "id", "text", "created_at", "favorite_count", "retweet_count", "reply_count", "view_count" }] }`

---

### 3.5 Get User Followers

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/user/USERNAME/followers?count=20` |
| **Auth** | Header Auth credential |

**Response:** `{ "username": "...", "count": N, "users": [{ "id", "name", "username", "description", "followers_count", ... }] }`

---

### 3.6 Get User Following

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/user/USERNAME/following?count=20` |
| **Auth** | Header Auth credential |

**Response:** `{ "username": "...", "count": N, "users": [{ ... }] }`

---

### 3.7 Get User Media

Get a user's tweets that contain photos/videos.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/user/USERNAME/media?count=20` |
| **Auth** | Header Auth credential |

**Response:** `{ "username": "...", "count": N, "tweets": [{ "id", "text", "media": [{ "type", "url", "expanded_url" }], ... }] }`

---

### 3.8 Get User Likes

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/user/USERNAME/likes?count=20` |
| **Auth** | Header Auth credential |

**Response:** `{ "username": "...", "count": N, "tweets": [{ ... }] }`

---

### 3.9 Get User Lists

Get all Twitter lists a user has created.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/user/USERNAME/lists` |
| **Auth** | Header Auth credential |

No query parameters.

**Response:** `{ "username": "...", "count": N, "lists": [{ "id", "name", "description", "member_count", "subscriber_count", "mode" }] }`

---

### 3.10 Get Tweet by ID

Get full details of a specific tweet.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/tweet/TWEET_ID` |
| **Auth** | Header Auth credential |

**Replace `TWEET_ID` with the numeric tweet ID.**

**Example URL:**
```
https://your-app.up.railway.app/tweet/189337462847YOUR_API_KEY7
```

**Response:** Full tweet object with `id`, `text`, `created_at`, `user`, `favorite_count`, `retweet_count`, `reply_count`, `view_count`, `quote_count`, `bookmark_count`, `lang`, `hashtags`, `media`, etc.

---

### 3.11 Get Tweet Replies

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/tweet/TWEET_ID/replies?count=20` |
| **Auth** | Header Auth credential |

**Response:** `{ "tweet_id": "...", "count": N, "replies": [{ full tweet objects }] }`

---

### 3.12 Get Trends

Get current trending topics on Twitter.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/trends?category=trending` |
| **Auth** | Header Auth credential |

**URL Parameters:**

| Param | Required | Default | Options |
|-------|----------|---------|---------|
| `category` | No | `trending` | `trending`, `for-you`, `news`, `sports`, `entertainment` |

**Example URLs:**
```
https://your-app.up.railway.app/trends
https://your-app.up.railway.app/trends?category=news
https://your-app.up.railway.app/trends?category=entertainment
```

**Response:** `{ "category": "trending", "count": N, "trends": [{ "name": "#AI", "tweet_count": 15000 }] }`

---

### 3.13 Get List Tweets

Get tweets from a specific Twitter list.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/list/LIST_ID/tweets?count=20` |
| **Auth** | Header Auth credential |

**Replace `LIST_ID` with the list's numeric ID** (get it from `/user/USERNAME/lists`).

**Response:** `{ "list_id": "...", "count": N, "tweets": [{ full tweet objects }] }`

---

## 4. Reddit Endpoints

### 4.1 Get Subreddit Posts

The main Reddit endpoint. Get top/hot/new posts from any subreddit.

**Node Configuration:**

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/reddit/subreddit/SUBREDDIT_NAME?sort=top&time_filter=day&count=25` |
| **Authentication** | Predefined Credential Type → Header Auth → `Twitter Reddit API Key` |
| **Options → Always Output Data** | ON |
| **Options → Never Error** | ON |

**Replace `SUBREDDIT_NAME` with the subreddit name (no r/ prefix).**

**URL Parameters:**

| Param | Required | Default | Options | Example |
|-------|----------|---------|---------|---------|
| `sort` | No | `hot` | `hot`, `new`, `top`, `rising` | `top` |
| `time_filter` | No | `day` | `hour`, `day`, `week`, `month`, `year`, `all` | `day` |
| `count` | No | 25 | 1-100 | `15` |

> **Note:** `time_filter` only applies when `sort=top`. For hot/new/rising it's ignored.

**Example URLs:**
```
# Top posts today from r/artificial
https://your-app.up.railway.app/reddit/subreddit/artificial?sort=top&time_filter=day&count=15

# Hot posts from r/ChatGPT
https://your-app.up.railway.app/reddit/subreddit/ChatGPT?sort=hot&count=20

# New posts from r/ClaudeAI
https://your-app.up.railway.app/reddit/subreddit/ClaudeAI?sort=new&count=15

# Top posts this week from r/LocalLLaMA
https://your-app.up.railway.app/reddit/subreddit/LocalLLaMA?sort=top&time_filter=week&count=25
```

**Response format:**
```json
{
  "subreddit": "artificial",
  "sort": "top",
  "count": 15,
  "posts": [
    {
      "id": "1abc2de",
      "title": "New breakthrough in AI reasoning...",
      "selftext": "Full post text here (max 2000 chars)...",
      "author": "ai_researcher",
      "subreddit": "artificial",
      "score": 1542,
      "upvote_ratio": 0.95,
      "num_comments": 234,
      "url": "https://...",
      "permalink": "https://www.reddit.com/r/artificial/comments/...",
      "created_at": 1707436800,
      "engagement_score": 1776
    }
  ]
}
```

**Key fields for n8n:**
- `{{ $json.posts }}` — the array of posts
- `{{ $json.posts[0].title }}` — first post's title
- `{{ $json.posts[0].engagement_score }}` — score + num_comments combined
- `{{ $json.posts[0].permalink }}` — direct link to Reddit post

---

### 4.2 Search Reddit

Search across ALL of Reddit for posts matching a query.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/reddit/search?query=YOUR_QUERY&sort=relevance&time_filter=week&count=25` |
| **Auth** | Header Auth credential |

**URL Parameters:**

| Param | Required | Default | Options | Example |
|-------|----------|---------|---------|---------|
| `query` | Yes | — | Any text | `Claude AI review` |
| `sort` | No | `relevance` | `relevance`, `hot`, `top`, `new`, `comments` | `top` |
| `time_filter` | No | `week` | `hour`, `day`, `week`, `month`, `year`, `all` | `week` |
| `count` | No | 25 | 1-100 | `20` |

**Example URLs:**
```
# Search for Claude AI discussions this week
https://your-app.up.railway.app/reddit/search?query=Claude%20AI%20review&sort=top&time_filter=week&count=20

# Search for n8n automation posts
https://your-app.up.railway.app/reddit/search?query=n8n%20automation&sort=relevance&count=15

# Search for AI tools sorted by most comments
https://your-app.up.railway.app/reddit/search?query=best%20AI%20tools%202026&sort=comments&time_filter=month&count=25
```

**Response:** Same format as subreddit posts — `{ "query": "...", "sort": "...", "count": N, "posts": [{ ... }] }`

---

### 4.3 Get Post Comments

Get comments on a specific Reddit post.

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/reddit/post/POST_ID/comments?count=25&sort=best` |
| **Auth** | Header Auth credential |

**Replace `POST_ID` with the Reddit post ID** (the `id` field from subreddit/search results).

**URL Parameters:**

| Param | Required | Default | Options | Example |
|-------|----------|---------|---------|---------|
| `count` | No | 25 | 1-100 | `20` |
| `sort` | No | `best` | `best`, `top`, `new`, `controversial`, `old`, `qa` | `top` |

**Example URL:**
```
https://your-app.up.railway.app/reddit/post/1abc2de/comments?count=20&sort=top
```

**Response:**
```json
{
  "post_id": "1abc2de",
  "sort": "top",
  "count": 15,
  "comments": [
    {
      "id": "kx4m9p2",
      "author": "commenter123",
      "body": "This is really interesting because...",
      "score": 89,
      "created_at": 1707440000,
      "permalink": "https://www.reddit.com/r/..."
    }
  ]
}
```

---

## 5. Utility Endpoints

### 5.1 Health Check (No Auth)

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/health` |
| **Auth** | None |

**Response:** `{ "status": "ok", "version": "3.0.0", "endpoints": 21 }`

Use this to check if the API is online before running a workflow.

---

### 5.2 List Endpoints (No Auth)

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/endpoints` |
| **Auth** | None |

Returns full list of all 21 endpoints with descriptions and parameters.

---

### 5.3 Auth Status

| Setting | Value |
|---------|-------|
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/auth/status` |
| **Auth** | Header Auth credential |

**Response:** `{ "status": "ok", "authenticated": true, "user": { "id": "...", "name": "...", "username": "..." } }`

Use this to verify Twitter cookies are still valid.

---

## 6. Quick Reference Table

| # | Endpoint | URL to Copy-Paste |
|---|----------|--------------------|
| 1 | Search Tweets | `https://your-app.up.railway.app/search/tweets?query=QUERY&count=20` |
| 2 | Search Users | `https://your-app.up.railway.app/search/users?query=QUERY&count=20` |
| 3 | User Profile | `https://your-app.up.railway.app/user/USERNAME` |
| 4 | User Tweets | `https://your-app.up.railway.app/user/USERNAME/tweets?count=20` |
| 5 | User Followers | `https://your-app.up.railway.app/user/USERNAME/followers?count=20` |
| 6 | User Following | `https://your-app.up.railway.app/user/USERNAME/following?count=20` |
| 7 | User Media | `https://your-app.up.railway.app/user/USERNAME/media?count=20` |
| 8 | User Likes | `https://your-app.up.railway.app/user/USERNAME/likes?count=20` |
| 9 | User Lists | `https://your-app.up.railway.app/user/USERNAME/lists` |
| 10 | Tweet by ID | `https://your-app.up.railway.app/tweet/TWEET_ID` |
| 11 | Tweet Replies | `https://your-app.up.railway.app/tweet/TWEET_ID/replies?count=20` |
| 12 | Trends | `https://your-app.up.railway.app/trends?category=trending` |
| 13 | List Tweets | `https://your-app.up.railway.app/list/LIST_ID/tweets?count=20` |
| 14 | Subreddit Posts | `https://your-app.up.railway.app/reddit/subreddit/NAME?sort=top&time_filter=day&count=25` |
| 15 | Reddit Search | `https://your-app.up.railway.app/reddit/search?query=QUERY&sort=relevance&time_filter=week&count=25` |
| 16 | Post Comments | `https://your-app.up.railway.app/reddit/post/POST_ID/comments?count=25&sort=best` |

> Replace `QUERY`, `USERNAME`, `TWEET_ID`, `LIST_ID`, `NAME`, `POST_ID` with actual values.
> URL-encode spaces as `%20` (e.g., `AI%20automation`).

---

## 7. Common Mistakes & Fixes

### Mistake 1: Query params in separate config instead of URL

**Wrong:** Putting `query` and `count` in n8n's "Query Parameters" section separately.
**Right:** Put everything directly in the URL: `?query=AI%20tools&count=15`

> n8n's HTTP Request node sometimes doesn't send separate query params reliably, especially in Tool mode. Always put them in the URL.

---

### Mistake 2: Forgetting to URL-encode spaces

**Wrong:** `?query=AI automation tools`
**Right:** `?query=AI%20automation%20tools`

> In n8n, if you type the URL manually, use `%20` for spaces. If using expressions, use `{{ encodeURIComponent('AI automation tools') }}`.

---

### Mistake 3: Using `r/` prefix in subreddit name

**Wrong:** `https://...api.../reddit/subreddit/r/artificial`
**Right:** `https://...api.../reddit/subreddit/artificial`

> The API already adds `r/` internally. Just use the bare subreddit name.

---

### Mistake 4: Not enabling "Never Error"

If one API call fails (e.g., rate limit), it can kill your entire workflow.

**Fix:** In each HTTP Request node → **Settings** tab (gear icon) → **Always Output Data** = ON, **Continue On Fail** = ON.

Or in the **Options** section → set **Batching** or error handling as needed.

---

### Mistake 5: Forgetting `=` prefix for expressions in Tool nodes

When using HTTP Request **Tool** nodes (for AI agents), the URL must start with `=` to enable expression mode.

**Wrong:** `https://...api.../user/{{ $fromAI('username') }}/tweets`
**Right:** `=https://...api.../user/{{ $fromAI('username') }}/tweets`

> This only applies to Tool nodes. Regular HTTP Request nodes handle expressions automatically.

---

### Mistake 6: Twitter cookies expired

**Symptom:** All Twitter endpoints return 401 errors.
**Fix:** Re-extract cookies from your browser and call `POST /auth/set-cookies` with the new `auth_token` and `ct0` values.

> Reddit endpoints don't need cookies — they work independently.

---

### Mistake 7: Reddit rate limiting (429 errors)

**Symptom:** Reddit endpoints return 429 after rapid calls.
**Why:** Reddit allows max 10 requests per minute for unauthenticated access.
**Fix:** The API has a built-in 6.5s rate limiter, but if you fire 10+ Reddit nodes in parallel they'll queue up. This is normal — just takes a bit longer (~65s for 10 calls).

> In the Daily Intelligence workflow, the 8 Reddit nodes run in parallel but the rate limiter serializes them internally. No action needed.

---

### Mistake 8: Getting empty results from Twitter search

**Symptom:** `{ "query": "...", "count": 0, "tweets": [] }`
**Possible causes:**
1. Cookies expired (check with `/auth/status`)
2. Very niche query with no results
3. Twitter rate limit (try again in a few minutes)

**Fix:** The API automatically tries "Latest" first, then falls back to "Top" if Latest returns 404. If both return empty, the query just has no matches.

---

## Step-by-Step: Adding a New HTTP Request Node in n8n

Here's the exact click-by-click process:

1. **Open your n8n workflow**
2. Click **+** (Add Node) on the canvas
3. Search for **HTTP Request** → click it
4. In the node panel:
   - **Method:** `GET`
   - **URL:** Paste the full URL with params (from the table above)
5. **Authentication:**
   - Click the **Authentication** dropdown
   - Select **Predefined Credential Type**
   - Credential Type: **Header Auth**
   - Select your saved `Twitter Reddit API Key` credential
6. **Settings tab** (gear icon at top):
   - **Always Output Data:** Toggle ON
   - **Continue On Fail:** Toggle ON
7. Click **Test step** (play button) to verify it works
8. Connect the node to the rest of your workflow

Done. Repeat for each endpoint you need.
