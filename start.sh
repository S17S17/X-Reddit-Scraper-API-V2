#!/bin/bash
# ============================================================
# Hermes Scraper — Start + Auto-Cookie Activate
# Reads TWITTER_AUTH_TOKEN and TWITTER_CT0 from .env
# and pushes them to the running scraper automatically.
# ============================================================

set -e

SCRAPER_DIR="$(cd "$(dirname "$0")" && pwd)"
HERMES_ENV="$SCRAPER_DIR/.env"
SCRAPER_ENV="$SCRAPER_DIR/.env"
API_KEY="c7e495f54b09692140c20c1694f5c196ff7e5247826ee514"
PORT=8765
LOG_FILE="/tmp/scraper.log"

cd "$SCRAPER_DIR"

# Load cookies from hermes .env
export $(grep -v '^#' "$HERMES_ENV" | xargs) 2>/dev/null

# Kill any existing scraper on this port
PID=$(lsof -ti:$PORT 2>/dev/null || true)
if [ -n "$PID" ]; then
    echo "[start.sh] Killing existing scraper (PID $PID)..."
    kill -9 $PID 2>/dev/null || true
    sleep 1
fi

echo "[start.sh] Starting scraper on port $PORT..."
source "$SCRAPER_DIR/venv/bin/activate"
PORT=$PORT "$SCRAPER_DIR/venv/bin/python3" -m uvicorn app.main:app --host 0.0.0.0 --port $PORT > "$LOG_FILE" 2>&1 &
SCRAPER_PID=$!
echo "[start.sh] Scraper PID: $SCRAPER_PID"

# Wait for it to be ready
echo "[start.sh] Waiting for scraper to be ready..."
for i in $(seq 1 15); do
    STATUS=$(curl -s http://localhost:$PORT/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || true)
    if [ "$STATUS" = "ok" ]; then
        echo "[start.sh] Scraper is up!"
        break
    fi
    sleep 1
done

# Set cookies automatically
if [ -n "$TWITTER_AUTH_TOKEN" ] && [ -n "$TWITTER_CT0" ]; then
    echo "[start.sh] Injecting Twitter cookies..."
    RESULT=$(curl -s -X POST http://localhost:$PORT/auth/set-cookies \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d "{\"auth_token\": \"$TWITTER_AUTH_TOKEN\", \"ct0\": \"$TWITTER_CT0\"}")
    echo "[start.sh] Cookie inject result: $RESULT"
else
    echo "[start.sh] WARNING: TWITTER_AUTH_TOKEN or TWITTER_CT0 not found in .env"
fi

echo "[start.sh] Done. Scraper running at http://localhost:$PORT"
echo "[start.sh] Logs: $LOG_FILE"
