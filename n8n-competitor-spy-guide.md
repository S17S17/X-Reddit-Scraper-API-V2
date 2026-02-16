# Competitor Spy Workflow — Setup Guide

> **File:** `n8n-competitor-spy.json`
> **Endpoints used:** 3 (`/user/{username}`, `/user/{username}/tweets`, `/search/tweets`)
> **Nodes:** 7 (Manual Trigger → Set Competitor → Get Profile → [Get Tweets + Search Mentions] → Merge → Build Spy Report)
> **Build time:** ~5 minutes

---

## What It Does

Enter any Twitter/X username and get a full spy report:

- **Profile snapshot** — name, bio, follower count, verified status
- **Engagement stats** — avg likes, retweets, replies, views across their last 20 tweets
- **Top performing tweet** — their best tweet by engagement
- **Engagement rate** — (likes + RTs + replies) / views as a percentage
- **Public mentions** — what other people are saying about them (buzz level)

---

## How to Import

1. Open n8n
2. Click **+ Add Workflow** (or the three dots → Import from File)
3. Select `n8n-competitor-spy.json`
4. Done — the workflow appears on your canvas

---

## Setup Steps (2 things to configure)

### Step 1: Set Up the API Key Credential

If you already have a `Header Auth` credential from other workflows, skip this.

1. Go to **Credentials** → **Add Credential**
2. Search for **Header Auth**
3. Configure:
   | Field | Value |
   |-------|-------|
   | **Name** | `Twitter Reddit API Key` |
   | **Header Name** | `X-API-Key` |
   | **Header Value** | `YOUR_API_KEY` |
4. Save

### Step 2: Assign the Credential to Each HTTP Request Node

After importing, the 3 HTTP nodes need the credential linked:

1. **Double-click "Get Profile"** → Authentication → Predefined Credential Type → Header Auth → select `Twitter Reddit API Key`
2. **Double-click "Get Tweets"** → same thing
3. **Double-click "Search Mentions"** → same thing

### Step 3 (Optional): Change the Competitor Username

1. **Double-click "Set Competitor"** node
2. Change `AnthropicAI` to any username you want to spy on
3. No `@` symbol needed

---

## Workflow Architecture

```
Manual Trigger
      │
      ▼
  Set Competitor ──── (username: "AnthropicAI")
      │
      ▼
  Get Profile ──────── GET /user/{username}
      │
      ├──────────────────────────┐
      ▼                          ▼
  Get Tweets                Search Mentions
  GET /user/{username}/     GET /search/tweets
  tweets?count=20           ?query={username}&product=Top
      │                          │
      ▼                          ▼
  ┌──────────────────────────────┘
  │
  ▼
  Merge (combine all data)
  │
  ▼
  Build Spy Report (Code node — calculates everything)
```

**Key design:** Get Tweets and Search Mentions run **in parallel** (both branch from Get Profile), then Merge combines the results before the final report.

---

## The 3 API Endpoints Used

| # | Node | Endpoint | What It Gets |
|---|------|----------|--------------|
| 1 | Get Profile | `GET /user/{username}` | Bio, followers, tweet count, verified |
| 2 | Get Tweets | `GET /user/{username}/tweets?count=20` | Their last 20 tweets with engagement data |
| 3 | Search Mentions | `GET /search/tweets?query={username}&product=Top` | What others say about them |

---

## Output

The "Build Spy Report" node outputs a single JSON object with:

```json
{
  "report": "COMPETITOR SPY REPORT\n=====================\n...",
  "profile": {
    "name": "Anthropic",
    "username": "AnthropicAI",
    "bio": "AI safety company...",
    "followers": 250000,
    "following": 50,
    "verified": true
  },
  "top_tweet": {
    "text": "We just released Claude 4...",
    "likes": 5200,
    "retweets": 1300,
    "views": 890000
  },
  "engagement": {
    "avg_likes": 420,
    "avg_retweets": 85,
    "avg_replies": 32,
    "avg_views": 65000,
    "engagement_rate_percent": 0.83
  },
  "mentions": {
    "count": 20,
    "buzz_level": "high buzz",
    "top_5": [...]
  },
  "tweets_analyzed": 20
}
```

The `report` field is a human-readable text version you can send via email, Slack, or paste anywhere.

---

## Ideas to Extend (After the Demo)

- **Add a Schedule Trigger** — run daily at 9am to track competitor changes over time
- **Save to Google Sheets** — append the report row daily to build a trend dashboard
- **Compare multiple competitors** — loop over an array of usernames
- **Add an AI summary** — feed the report into an AI agent to get strategic insights
- **Send to Slack/Email** — auto-deliver the report to your team
