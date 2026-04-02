#!/bin/bash
# ============================================================
# Update Twitter cookies in .env and push to live scraper
# Usage: ./update-cookies.sh <auth_token> <ct0>
# ============================================================

# Auto-detect home dir — works as root OR as semah_selmi
ACTUAL_HOME=$(eval echo ~${SUDO_USER:-$USER})
HERMES_ENV="$ACTUAL_HOME/.hermes/.env"
SCRAPER_ENV="/root/.hermes/scraper/.env"
API_KEY="c7e495f54b09692140c20c1694f5c196ff7e5247826ee514"
PORT=8765

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <auth_token> <ct0>"
    echo ""
    echo "How to get cookies from browser:"
    echo "  1. Open x.com in Chrome/Firefox"
    echo "  2. Open DevTools (F12) -> Application -> Cookies -> https://x.com"
    echo "  3. Copy auth_token value"
    echo "  4. Copy ct0 value"
    echo "  5. Run: ./update-cookies.sh <auth_token> <ct0>"
    exit 1
fi

AUTH_TOKEN="$1"
CT0="$2"

echo "[update-cookies] Saving to hermes .env..."

# Update or add TWITTER_AUTH_TOKEN
if grep -q "^TWITTER_AUTH_TOKEN=" "$HERMES_ENV"; then
    sed -i "s|^TWITTER_AUTH_TOKEN=.*|TWITTER_AUTH_TOKEN=$AUTH_TOKEN|" "$HERMES_ENV"
else
    echo "TWITTER_AUTH_TOKEN=$AUTH_TOKEN" >> "$HERMES_ENV"
fi

# Update or add TWITTER_CT0
if grep -q "^TWITTER_CT0=" "$HERMES_ENV"; then
    sed -i "s|^TWITTER_CT0=.*|TWITTER_CT0=$CT0|" "$HERMES_ENV"
else
    echo "TWITTER_CT0=$CT0" >> "$HERMES_ENV"
fi

echo "[update-cookies] Saved to .env"

# If scraper is running, push cookies immediately
STATUS=$(curl -s http://localhost:$PORT/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || true)
if [ "$STATUS" = "ok" ]; then
    echo "[update-cookies] Scraper is live — pushing cookies now..."
    RESULT=$(curl -s -X POST http://localhost:$PORT/auth/set-cookies \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d "{\"auth_token\": \"$AUTH_TOKEN\", \"ct0\": \"$CT0\"}")
    echo "[update-cookies] Result: $RESULT"
else
    echo "[update-cookies] Scraper not running — cookies saved, will activate on next start"
fi

# Also update cookies.json directly
python3 -c "
import json
path = '/root/.hermes/scraper/cookies.json'
try:
    with open(path) as f:
        data = json.load(f)
except:
    data = {}
data['auth_token'] = '$AUTH_TOKEN'
data['ct0'] = '$CT0'
with open(path, 'w') as f:
    json.dump(data, f)
print('[update-cookies] cookies.json updated')
"

echo "[update-cookies] Done."
