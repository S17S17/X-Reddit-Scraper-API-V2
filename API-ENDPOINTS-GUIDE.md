# Complete API Endpoints Guide — 22 Endpoints

> **For:** Twitter/X & Reddit Scraper API v3.1.0
> **Your API Base URL:** `YOUR_RAILWAY_URL` (replace with your actual Railway deployment URL)
> **Your API Key:** `YOUR_API_KEY` (replace with your actual API key)

---

## Table of Contents

1. [Understanding URL Structure (READ THIS FIRST)](#understanding-url-structure)
2. [How to Set Up HTTP Request Nodes](#how-to-set-up-http-request-nodes)
3. [Twitter Endpoints (15)](#twitter-endpoints)
4. [Reddit Endpoints (4)](#reddit-endpoints)
5. [Utility Endpoints (3)](#utility-endpoints)
6. [Quick Copy-Paste Templates](#quick-copy-paste-templates)

---

## Understanding URL Structure (READ THIS FIRST)

### Anatomy of an API URL

Let's break down this example step by step:

```
http://localhost:8000/search/tweets?query=AI%20automation&product=Top&count=50
```

Here's what each part means:

| Part | What It Is | Can You Change It? | Example |
|------|------------|-------------------|---------|
| `http://localhost:8000` | **Base URL** (your server address) | ❌ **FIXED** — Use your Railway URL | `https://your-app.railway.app` |
| `/search/tweets` | **Endpoint path** (what action to perform) | ❌ **FIXED** — Each endpoint has its own path | `/search/tweets` or `/user/elonmusk` |
| `?` | **Query string start** | ❌ **FIXED** — Always use `?` before first parameter | `?` |
| `query=` | **Parameter name** | ❌ **FIXED** — API expects this exact name | `query=` |
| `AI%20automation` | **Parameter value** (your input) | ✅ **CHANGE THIS** — Your search term | `Claude%20AI` or `Python%20tips` |
| `&` | **Parameter separator** | ❌ **FIXED** — Use `&` between parameters | `&` |
| `product=` | **Parameter name** | ❌ **FIXED** — API expects this exact name | `product=` |
| `Top` | **Parameter value** (your choice) | ✅ **CHANGE THIS** — Pick from allowed options | `Top`, `Latest`, `Media`, `Photos`, `Videos` |
| `&` | **Parameter separator** | ❌ **FIXED** | `&` |
| `count=` | **Parameter name** | ❌ **FIXED** | `count=` |
| `50` | **Parameter value** (your number) | ✅ **CHANGE THIS** — Any number 1-100 | `10`, `20`, `50`, `100` |

### Visual Color-Coded Example

```
https://YOUR_RAILWAY_URL/search/tweets?query=YOUR_SEARCH&product=Top&count=20
└─────┬─────┘└──────┬──────┘└──────┬──────┘└───┬───┘└────┬────┘└─┬─┘
      │             │               │           │         │       │
   FIXED         FIXED           FIXED      CHANGE    FIXED   CHANGE
```

### What's `%20`?

- **Spaces are not allowed in URLs**
- `%20` = a space character in URL encoding
- `AI automation` → `AI%20automation`
- `Claude AI review` → `Claude%20AI%20review`

**In n8n:** You have two options:
1. **Manual encoding:** Type `%20` yourself → `AI%20automation`
2. **Auto encoding (better):** Use n8n expressions → `{{ encodeURIComponent('AI automation') }}`

---

## How to Set Up HTTP Request Nodes

### Step 1: Create the Credential (One Time Setup)

1. In n8n → **Credentials** → **Add Credential**
2. Search for **Header Auth**
3. Fill in:
   ```
   Name: Twitter Reddit API Key
   Header Name: X-API-Key
   Header Value: YOUR_API_KEY
   ```
4. **Save**

Now you can reuse this credential in every HTTP Request node.

---

### Step 2: Add an HTTP Request Node

1. Click **+** on canvas
2. Search **HTTP Request**
3. Click it to add

---

### Step 3: Configure the Node

| Setting | What to Put |
|---------|-------------|
| **Method** | `GET` (for all 22 endpoints) |
| **URL** | Copy from the templates below |
| **Authentication** | → Predefined Credential Type → Header Auth → Select `Twitter Reddit API Key` |
| **Options → Always Output Data** | ✅ Turn ON |
| **Options → Continue On Fail** | ✅ Turn ON |

---

### Step 4: Understanding URL Templates

Each endpoint below has a template like this:

```
https://YOUR_RAILWAY_URL/user/USERNAME/tweets?count=20
                        └──┬──┘└───┬───┘       └──┬──┘
                        FIXED   REPLACE      REPLACE
```

**What to do:**
1. Copy the entire URL
2. Replace `YOUR_RAILWAY_URL` with your actual Railway URL
3. Replace `USERNAME` with the actual username (no @ symbol)
4. Replace `20` with your desired count (if you want a different number)

---

## Twitter Endpoints

### 1. Search Tweets

**What it does:** Search Twitter for tweets matching your keywords.

**URL Template:**
```
https://YOUR_RAILWAY_URL/search/tweets?query=YOUR_SEARCH_TERM&count=20&product=Latest
```

**What to replace:**

| Part | Replace With | Options/Notes |
|------|--------------|---------------|
| `YOUR_RAILWAY_URL` | Your Railway deployment URL | e.g., `my-api.railway.app` |
| `YOUR_SEARCH_TERM` | Your keyword(s) | Use `%20` for spaces: `AI%20automation` |
| `20` | Number of results | Any number 1-100 |
| `Latest` | Type of results | Options: `Top`, `Latest`, `Media`, `Photos`, `Videos` |

**Real Example:**
```
https://my-api.railway.app/search/tweets?query=Claude%20AI&count=15&product=Top
```

**Response:** You get `$json.tweets` (an array) with each tweet containing:
- `id` — Tweet ID
- `text` — Tweet content
- `user` — User object (`name`, `username`, `followers_count`)
- `favorite_count` — Likes
- `retweet_count` — Retweets
- `reply_count` — Replies
- `view_count` — Views
- `created_at` — When it was posted

---

### 2. Search Users

**What it does:** Find Twitter users by name or topic.

**URL Template:**
```
https://YOUR_RAILWAY_URL/search/users?query=YOUR_SEARCH&count=20
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `YOUR_SEARCH` | Search term | e.g., `AI%20researcher` |
| `20` | Number of users to return | 1-100 |

**Real Example:**
```
https://my-api.railway.app/search/users?query=entrepreneur&count=10
```

**Response:** `$json.users` array with `id`, `name`, `username`, `description`, `followers_count`, `following_count`, `verified`

---

### 3. Get User Profile

**What it does:** Get full profile info for a specific user.

**URL Template:**
```
https://YOUR_RAILWAY_URL/user/USERNAME
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `USERNAME` | Twitter username | **NO @ symbol** — just `elonmusk`, not `@elonmusk` |

**Real Examples:**
```
https://my-api.railway.app/user/elonmusk
https://my-api.railway.app/user/AnthropicAI
```

**Response:** Single object with `id`, `name`, `username`, `description`, `followers_count`, `following_count`, `tweet_count`, `verified`, `profile_image_url`, `created_at`

---

### 4. Get User Tweets

**What it does:** Get recent tweets from a specific user.

**URL Template:**
```
https://YOUR_RAILWAY_URL/user/USERNAME/tweets?count=20
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `USERNAME` | Twitter username | No @ symbol |
| `20` | Number of tweets | 1-100 |

**Real Example:**
```
https://my-api.railway.app/user/AnthropicAI/tweets?count=10
```

**Response:** `$json.tweets` array (same structure as search tweets)

---

### 5. Get User Followers

**What it does:** Get a list of users following a specific account.

**URL Template:**
```
https://YOUR_RAILWAY_URL/user/USERNAME/followers?count=20
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `USERNAME` | Twitter username | No @ symbol |
| `20` | Number of followers | 1-100 |

**Real Example:**
```
https://my-api.railway.app/user/elonmusk/followers?count=50
```

**Response:** `$json.users` array with follower profiles

---

### 6. Get User Following

**What it does:** Get accounts that a user follows.

**URL Template:**
```
https://YOUR_RAILWAY_URL/user/USERNAME/following?count=20
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `USERNAME` | Twitter username | No @ symbol |
| `20` | Number of accounts | 1-100 |

**Real Example:**
```
https://my-api.railway.app/user/naval/following?count=30
```

**Response:** `$json.users` array

---

### 7. Get User Media

**What it does:** Get tweets from a user that contain photos or videos.

**URL Template:**
```
https://YOUR_RAILWAY_URL/user/USERNAME/media?count=20
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `USERNAME` | Twitter username | No @ symbol |
| `20` | Number of media tweets | 1-100 |

**Real Example:**
```
https://my-api.railway.app/user/SpaceX/media?count=15
```

**Response:** `$json.tweets` array with `media` field containing image/video URLs

---

### 8. Get User Likes

**What it does:** Get tweets that a user has liked.

**URL Template:**
```
https://YOUR_RAILWAY_URL/user/USERNAME/likes?count=20
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `USERNAME` | Twitter username | No @ symbol |
| `20` | Number of liked tweets | 1-100 |

**Real Example:**
```
https://my-api.railway.app/user/levelsio/likes?count=25
```

**Response:** `$json.tweets` array

---

### 9. Get User Lists

**What it does:** Get all Twitter lists created by a user.

**URL Template:**
```
https://YOUR_RAILWAY_URL/user/USERNAME/lists
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `USERNAME` | Twitter username | No @ symbol |

**No count parameter** — returns all lists.

**Real Example:**
```
https://my-api.railway.app/user/alexisohanian/lists
```

**Response:** `$json.lists` array with `id`, `name`, `description`, `member_count`, `subscriber_count`

---

### 10. Get Tweet by ID

**What it does:** Get full details of a single tweet.

**URL Template:**
```
https://YOUR_RAILWAY_URL/tweet/TWEET_ID
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `TWEET_ID` | Numeric tweet ID | Find it in the tweet URL or from previous API calls |

**Real Example:**
```
https://my-api.railway.app/tweet/1893374628471234567
```

**How to find tweet ID:** From a tweet URL like `https://x.com/user/status/1893374628471234567`, the ID is `1893374628471234567`

**Response:** Single tweet object with full details

---

### 11. Get Tweet Replies

**What it does:** Get replies to a specific tweet.

**URL Template:**
```
https://YOUR_RAILWAY_URL/tweet/TWEET_ID/replies?count=20
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `TWEET_ID` | Numeric tweet ID | |
| `20` | Number of replies | 1-100 |

**Real Example:**
```
https://my-api.railway.app/tweet/1893374628471234567/replies?count=15
```

**Response:** `$json.replies` array of tweet objects

---

### 12. Get Trends

**What it does:** Get current trending topics on Twitter.

**URL Template:**
```
https://YOUR_RAILWAY_URL/trends?category=trending
```

**What to replace:**

| Part | Replace With | Options |
|------|--------------|---------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `trending` | Category | Options: `trending`, `for-you`, `news`, `sports`, `entertainment` |

**Real Examples:**
```
https://my-api.railway.app/trends
https://my-api.railway.app/trends?category=news
https://my-api.railway.app/trends?category=sports
```

**Response:** `$json.trends` array with `name` (trend text like "#AI") and `tweet_count`

---

### 13. Get List Tweets

**What it does:** Get tweets from a Twitter list.

**URL Template:**
```
https://YOUR_RAILWAY_URL/list/LIST_ID/tweets?count=20
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `LIST_ID` | Numeric list ID | Get from `/user/USERNAME/lists` endpoint |
| `20` | Number of tweets | 1-100 |

**Real Example:**
```
https://my-api.railway.app/list/1234567890/tweets?count=30
```

**Response:** `$json.tweets` array

---

## Reddit Endpoints

### 14. Get Subreddit Posts

**What it does:** Get posts from any subreddit.

**URL Template:**
```
https://YOUR_RAILWAY_URL/reddit/subreddit/SUBREDDIT_NAME?sort=top&time_filter=day&count=25
```

**What to replace:**

| Part | Replace With | Options/Notes |
|------|--------------|---------------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `SUBREDDIT_NAME` | Subreddit name | **NO r/ prefix** — just `artificial`, not `r/artificial` |
| `top` | Sort type | Options: `hot`, `new`, `top`, `rising` |
| `day` | Time filter | Options: `hour`, `day`, `week`, `month`, `year`, `all` |
| `25` | Number of posts | 1-100 |

**Note:** `time_filter` only works when `sort=top`. For hot/new/rising, it's ignored.

**Real Examples:**
```
https://my-api.railway.app/reddit/subreddit/artificial?sort=top&time_filter=day&count=15
https://my-api.railway.app/reddit/subreddit/ChatGPT?sort=hot&count=20
https://my-api.railway.app/reddit/subreddit/ClaudeAI?sort=new&count=10
```

**Response:** `$json.posts` array with:
- `id` — Post ID (use for comments endpoint)
- `title` — Post title
- `selftext` — Post body (first 2000 chars)
- `author` — Username
- `subreddit` — Subreddit name
- `score` — Upvotes minus downvotes
- `upvote_ratio` — Percentage of upvotes (0.0-1.0)
- `num_comments` — Comment count
- `url` — Link (if it's a link post)
- `permalink` — Reddit URL to the post
- `created_at` — Unix timestamp
- `engagement_score` — `score + num_comments` combined

---

### 15. Search Reddit

**What it does:** Search all of Reddit for posts matching your query.

**URL Template:**
```
https://YOUR_RAILWAY_URL/reddit/search?query=YOUR_SEARCH&sort=relevance&time_filter=week&count=25
```

**What to replace:**

| Part | Replace With | Options/Notes |
|------|--------------|---------------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `YOUR_SEARCH` | Search keywords | Use `%20` for spaces |
| `relevance` | Sort type | Options: `relevance`, `hot`, `top`, `new`, `comments` |
| `week` | Time filter | Options: `hour`, `day`, `week`, `month`, `year`, `all` |
| `25` | Number of posts | 1-100 |

**Real Examples:**
```
https://my-api.railway.app/reddit/search?query=Claude%20AI%20review&sort=top&time_filter=week&count=20
https://my-api.railway.app/reddit/search?query=n8n%20automation&sort=relevance&count=15
https://my-api.railway.app/reddit/search?query=best%20AI%20tools%202026&sort=comments&time_filter=month&count=30
```

**Response:** Same format as subreddit posts — `$json.posts` array

---

### 16. Get Post Details

**What it does:** Get details of a specific Reddit post (without comments).

**URL Template:**
```
https://YOUR_RAILWAY_URL/reddit/post/POST_ID
```

**What to replace:**

| Part | Replace With | Notes |
|------|--------------|-------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `POST_ID` | Reddit post ID | The `id` field from search/subreddit results (e.g., `1abc2de`) |

**Real Example:**
```
https://my-api.railway.app/reddit/post/1abc2de
```

**Response:** Single post object (same fields as subreddit posts)

---

### 17. Get Post Comments

**What it does:** Get comments on a Reddit post.

**URL Template:**
```
https://YOUR_RAILWAY_URL/reddit/post/POST_ID/comments?count=25&sort=best
```

**What to replace:**

| Part | Replace With | Options/Notes |
|------|--------------|---------------|
| `YOUR_RAILWAY_URL` | Your Railway URL | |
| `POST_ID` | Reddit post ID | From search/subreddit results |
| `25` | Number of comments | 1-100 |
| `best` | Sort type | Options: `best`, `top`, `new`, `controversial`, `old`, `qa` |

**Real Example:**
```
https://my-api.railway.app/reddit/post/1abc2de/comments?count=20&sort=top
```

**Response:** `$json.comments` array with:
- `id` — Comment ID
- `author` — Username
- `body` — Comment text
- `score` — Upvotes minus downvotes
- `created_at` — Unix timestamp
- `permalink` — Direct link to comment

---

## Utility Endpoints

### 18. Health Check

**What it does:** Check if the API is online.

**URL Template:**
```
https://YOUR_RAILWAY_URL/health
```

**No authentication needed.** No parameters.

**Real Example:**
```
https://my-api.railway.app/health
```

**Response:** `{ "status": "ok", "version": "3.1.0", "endpoints": 22 }`

---

### 19. List Endpoints

**What it does:** Get a full list of all 22 endpoints with descriptions.

**URL Template:**
```
https://YOUR_RAILWAY_URL/endpoints
```

**No authentication needed.** No parameters.

**Real Example:**
```
https://my-api.railway.app/endpoints
```

**Response:** JSON object with all endpoint details organized by category

---

### 20. Auth Status

**What it does:** Check if your Twitter cookies are still valid.

**URL Template:**
```
https://YOUR_RAILWAY_URL/auth/status
```

**Requires authentication** (use Header Auth credential).

**Real Example:**
```
https://my-api.railway.app/auth/status
```

**Response:** `{ "status": "ok", "authenticated": true, "user": { "id": "...", "name": "...", "username": "..." } }`

---

### 21. Login (One-Time Setup)

**What it does:** Login to Twitter with username/password. Saves session cookies.

**URL Template:**
```
https://YOUR_RAILWAY_URL/auth/login
```

**Method:** `POST` (not GET)

**Requires authentication** (API key).

**Use this:** Only for initial setup. After cookies expire, you'll need to re-login or use the set-cookies endpoint.

---

### 22. Set Cookies (Manual Cookie Injection)

**What it does:** Manually set browser cookies to bypass Cloudflare.

**URL Template:**
```
https://YOUR_RAILWAY_URL/auth/set-cookies
```

**Method:** `POST` (not GET)

**Body (JSON):**
```json
{
  "auth_token": "YOUR_AUTH_TOKEN_FROM_BROWSER",
  "ct0": "YOUR_CT0_TOKEN_FROM_BROWSER"
}
```

**Requires authentication** (API key).

**When to use:** When Twitter cookies expire and you need to refresh them. Extract from browser DevTools.

---

## Quick Copy-Paste Templates

### Twitter Templates

```
Search tweets:
https://YOUR_RAILWAY_URL/search/tweets?query=KEYWORD&count=20&product=Latest

Search users:
https://YOUR_RAILWAY_URL/search/users?query=KEYWORD&count=20

User profile:
https://YOUR_RAILWAY_URL/user/USERNAME

User tweets:
https://YOUR_RAILWAY_URL/user/USERNAME/tweets?count=20

User followers:
https://YOUR_RAILWAY_URL/user/USERNAME/followers?count=20

User following:
https://YOUR_RAILWAY_URL/user/USERNAME/following?count=20

User media:
https://YOUR_RAILWAY_URL/user/USERNAME/media?count=20

User likes:
https://YOUR_RAILWAY_URL/user/USERNAME/likes?count=20

User lists:
https://YOUR_RAILWAY_URL/user/USERNAME/lists

Tweet by ID:
https://YOUR_RAILWAY_URL/tweet/TWEET_ID

Tweet replies:
https://YOUR_RAILWAY_URL/tweet/TWEET_ID/replies?count=20

Trends:
https://YOUR_RAILWAY_URL/trends?category=trending

List tweets:
https://YOUR_RAILWAY_URL/list/LIST_ID/tweets?count=20
```

### Reddit Templates

```
Subreddit posts:
https://YOUR_RAILWAY_URL/reddit/subreddit/SUBREDDIT?sort=top&time_filter=day&count=25

Search Reddit:
https://YOUR_RAILWAY_URL/reddit/search?query=KEYWORD&sort=relevance&time_filter=week&count=25

Post details:
https://YOUR_RAILWAY_URL/reddit/post/POST_ID

Post comments:
https://YOUR_RAILWAY_URL/reddit/post/POST_ID/comments?count=25&sort=best
```

### Utility Templates

```
Health:
https://YOUR_RAILWAY_URL/health

List endpoints:
https://YOUR_RAILWAY_URL/endpoints

Auth status:
https://YOUR_RAILWAY_URL/auth/status
```

---

## Common Mistakes & How to Avoid Them

### ❌ Mistake: Including @ in usernames
```
WRONG: https://YOUR_RAILWAY_URL/user/@elonmusk
RIGHT: https://YOUR_RAILWAY_URL/user/elonmusk
```

### ❌ Mistake: Including r/ in subreddit names
```
WRONG: https://YOUR_RAILWAY_URL/reddit/subreddit/r/artificial
RIGHT: https://YOUR_RAILWAY_URL/reddit/subreddit/artificial
```

### ❌ Mistake: Forgetting to URL-encode spaces
```
WRONG: https://YOUR_RAILWAY_URL/search/tweets?query=AI automation
RIGHT: https://YOUR_RAILWAY_URL/search/tweets?query=AI%20automation
```

### ❌ Mistake: Using wrong sort/time_filter combinations
```
WRONG: https://YOUR_RAILWAY_URL/reddit/subreddit/ai?sort=hot&time_filter=day
(time_filter is ignored when sort=hot)

RIGHT: https://YOUR_RAILWAY_URL/reddit/subreddit/ai?sort=top&time_filter=day
(time_filter only works with sort=top)
```

### ❌ Mistake: Not setting "Continue On Fail" in n8n
If one HTTP Request fails, it can crash your whole workflow.

**Fix:** In each HTTP Request node → Settings tab → Turn ON "Continue On Fail" and "Always Output Data"

---

## Need Help?

- **Test endpoints:** Use the `/health` endpoint first to verify your API is online
- **Check authentication:** Use `/auth/status` to verify cookies are valid
- **View all endpoints:** Use `/endpoints` to see the full API structure
- **In n8n:** Always test with the "Test step" button before connecting to the rest of your workflow
