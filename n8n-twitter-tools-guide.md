# Adding Twitter API Tools to Your n8n Repurpose Content Workflow

## Overview
Add HTTP Request Tool nodes to each of your 3 AI agents.
Each tool connects to your Railway-hosted Twitter scraper API (v2.0.0).

### API v2.0.0 - All Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (no auth) |
| `/endpoints` | GET | List all endpoints (no auth) |
| `/auth/login` | POST | Login with credentials |
| `/auth/set-cookies` | POST | Set browser cookies |
| `/auth/status` | GET | Check if cookies are valid |
| `/user/{username}` | GET | User profile |
| `/user/{username}/tweets` | GET | User's tweets (count) |
| `/user/{username}/followers` | GET | User's followers (count) |
| `/user/{username}/following` | GET | Who user follows (count) |
| `/user/{username}/media` | GET | User's media tweets (count) |
| `/user/{username}/likes` | GET | User's liked tweets (count) |
| `/user/{username}/lists` | GET | User's Twitter lists |
| `/tweet/{tweet_id}` | GET | Tweet details by ID |
| `/tweet/{tweet_id}/replies` | GET | Replies to a tweet (count) |
| `/search/tweets` | GET | Search tweets (query, count, product) |
| `/search/users` | GET | Search users (query, count) |
| `/trends` | GET | Trending topics (category) |
| `/list/{list_id}/tweets` | GET | Tweets from a list (count) |

---

## STEP 1: Add the 3 Tool Nodes (then duplicate for each agent)

### Tool 1: Twitter Search Tweets

In n8n, add a new node: **HTTP Request Tool** (under AI > Tools)

| Setting | Value |
|---|---|
| **Name** | `Twitter Search` |
| **Method** | GET |
| **URL** | `https://your-app.up.railway.app/search/tweets` |
| **Description** | `Search Twitter/X for live tweets about any topic. Use this to find real-time public reactions, trending discussions, and what people are saying RIGHT NOW about a subject. Returns tweet text, author info, and engagement metrics. Input a search query keyword or hashtag.` |

**Headers:**
| Header Name | Value |
|---|---|
| `X-API-Key` | `YOUR_API_KEY` (your actual API key) |

**Query Parameters:**
| Parameter | Value |
|---|---|
| `query` | `{fromAI}` (let the agent decide the search query) |
| `count` | `10` |

---

### Tool 2: Twitter User Tweets

Add another **HTTP Request Tool** node:

| Setting | Value |
|---|---|
| **Name** | `Twitter User Tweets` |
| **Method** | GET |
| **URL** | Use expression: `https://your-app.up.railway.app/user/{{ $fromAI('username', 'Twitter username without @', 'string') }}/tweets` |
| **Description** | `Get recent tweets from a specific Twitter/X user. Use this to analyze what a person or company has been tweeting about recently. Useful for competitor analysis or checking a creator's recent activity. Input: username without the @ symbol.` |

**Headers:**
| Header Name | Value |
|---|---|
| `X-API-Key` | `YOUR_API_KEY` (your actual API key) |

**Query Parameters:**
| Parameter | Value |
|---|---|
| `count` | `10` |

---

### Tool 3: Twitter User Profile

Add another **HTTP Request Tool** node:

| Setting | Value |
|---|---|
| **Name** | `Twitter User Profile` |
| **Method** | GET |
| **URL** | Use expression: `https://your-app.up.railway.app/user/{{ $fromAI('username', 'Twitter username without @', 'string') }}` |
| **Description** | `Get a Twitter/X user's profile info including bio, follower count, following count, and verified status. Use this when the content mentions a specific person or brand and you need their social proof data. Input: username without the @ symbol.` |

**Headers:**
| Header Name | Value |
|---|---|
| `X-API-Key` | `YOUR_API_KEY` (your actual API key) |

No query parameters needed.

---

## STEP 2: Connect Tools to Each Agent

For each of the 3 agents, drag a connection from each Twitter tool's output to the agent's **ai_tool** input (same place where Tavily and Firecrawl connect).

### TUTORIAL Agent (The Tech Writer)
Connect: `Twitter Search` + `Twitter User Tweets` + `Twitter User Profile`
(You'll need to create 3 separate tool nodes for this agent, or use the same ones if n8n allows shared tools)

### NEWS Agent (The Analyst)
Connect: `Twitter Search 1` + `Twitter User Tweets 1` + `Twitter User Profile 1`

### CASE_STUDY AGENT
Connect: `Twitter Search 2` + `Twitter User Tweets 2` + `Twitter User Profile 2`

**Total: 9 new HTTP Request Tool nodes** (3 per agent, unless you can share them)

---

## STEP 3: Update System Prompts

Add the following section to each agent's system prompt (in the "System Message" field).

### For TUTORIAL Agent (The Tech Writer) - ADD this section:

```
## 4. TWITTER/X RESEARCH PROTOCOL
You have three Twitter tools: `twitter_search`, `twitter_user_tweets`, `twitter_user_profile`.

**Step 1: Community Pulse Check (Twitter Search)**
- Before writing, search Twitter for the main tool/topic from the tutorial.
- Query examples: "n8n tutorial", "Make.com vs Zapier", tool name + "automation"
- Goal: Find REAL user pain points and reactions to fuel your "Contrarian Take" and hook.

**Step 2: Competitor Voice Check (Twitter User Tweets)**
- Check what the original YouTuber or related creators tweet about this topic.
- Goal: Ensure YOUR content adds something their tweets didn't cover.

**Step 3: Social Proof (Twitter User Profile)**
- If the tutorial mentions a specific tool creator or company, pull their profile.
- Goal: Add credibility data ("@founder has 50K followers building this tool") to your posts.

IMPORTANT: Use Twitter tools BEFORE writing. The live data should influence your tone, hook, and contrarian angle.
```

### For NEWS Agent (The Analyst) - ADD this section:

```
## 4. TWITTER/X RESEARCH PROTOCOL
You have three Twitter tools: `twitter_search`, `twitter_user_tweets`, `twitter_user_profile`.

**Step 1: Real-Time Reaction Scan (Twitter Search)**
- IMMEDIATELY search Twitter for the news topic (model name, company, feature).
- Query examples: "Claude 4 release", "OpenAI update", "Gemini pricing"
- Goal: Capture the LIVE public reaction. Quote real tweets in your "Plus..." section.

**Step 2: Official Source Check (Twitter User Tweets)**
- Get recent tweets from the official company account (e.g., @AnthropicAI, @OpenAI).
- Goal: Find the ORIGINAL announcement tweet. Link or reference it for credibility.

**Step 3: Key Figure Context (Twitter User Profile)**
- Pull profiles of key people mentioned (CEO, researcher who published the paper).
- Goal: Add context like "announced by @sama (3.2M followers)" to boost authority.

IMPORTANT: For NEWS content, Twitter data is CRITICAL. Real-time reactions and official tweets make your news posts 10x more credible than just summarizing a transcript. Always use twitter_search first.
```

### For CASE_STUDY AGENT - ADD this section:

```
## 4. TWITTER/X RESEARCH PROTOCOL
You have three Twitter tools: `twitter_search`, `twitter_user_tweets`, `twitter_user_profile`.

**Step 1: Credibility Verification (Twitter Search)**
- Search Twitter for the person/business in the case study.
- Query examples: "founder name + tool name", "company revenue claims"
- Goal: Find social proof OR red flags. Are real users praising this? Any complaints?

**Step 2: Subject's Own Voice (Twitter User Tweets)**
- Get recent tweets from the case study subject's Twitter account.
- Goal: Find their OWN claims, metrics, or testimonials they've shared publicly. Use these as verified data points in your audit.

**Step 3: Authority Data (Twitter User Profile)**
- Pull the subject's Twitter profile.
- Goal: Use follower count, bio, and verified status for the "Social Proof" section. A founder with 100K followers is more credible than one with 200.

IMPORTANT: The Revenue Auditor must VERIFY before amplifying. Use twitter_search to cross-check any revenue or success claims from the transcript. Never promote unverified numbers.
```

---

## STEP 4: Quick Test

1. Pick a video that's in "Re-purpose Content" status in Airtable
2. Run the workflow manually
3. Check the agent execution logs - you should see it calling:
   - Tavily (web search) - as before
   - Firecrawl (page scraping) - as before
   - Twitter Search (NEW) - live tweet data
   - Twitter User Tweets (NEW) - creator's tweets
   - Twitter User Profile (NEW) - profile data

The agent will decide on its own which Twitter tools to call based on the content.

---

## Naming Convention for the 9 Tool Nodes

| Agent | Tool Nodes |
|---|---|
| TUTORIAL Agent | `Twitter Search`, `Twitter User Tweets`, `Twitter User Profile` |
| NEWS Agent | `Twitter Search 1`, `Twitter User Tweets 1`, `Twitter User Profile 1` |
| CASE_STUDY Agent | `Twitter Search 2`, `Twitter User Tweets 2`, `Twitter User Profile 2` |

This matches your existing pattern: `Firecrawl tool`, `Firecrawl tool1`, `Firecrawl tool2`.
