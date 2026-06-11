#!/bin/bash
set -e

# ============================================================
# JARVIS Cloud — Hermes Agent Entrypoint
# Generates config, .env, and starts the gateway
# ============================================================

echo "=== JARVIS Cloud Hermes Agent starting ==="

# Set up Hermes home
HERMES_HOME="${HERMES_HOME:-/app/.hermes}"
export HERMES_HOME

mkdir -p "$HERMES_HOME/skills"
mkdir -p "$HERMES_HOME/data"
mkdir -p "$HERMES_HOME/cache"
mkdir -p "$HERMES_HOME/logs"
mkdir -p "$HERMES_HOME/audio_cache"

# If skills were copied into the image, symlink them
if [ -d "/app/skills" ]; then
    cp -r /app/skills/* "$HERMES_HOME/skills/" 2>/dev/null || true
    echo "✓ Skills copied to $HERMES_HOME/skills/"
fi

# Generate .env from Railway environment
cat > "$HERMES_HOME/.env" << EOENV
# === JARVIS Cloud — Auto-generated .env ===
# Generated at $(date -u +"%Y-%m-%dT%H:%M:%SZ")

# DeepSeek
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"

# Telegram
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_HOME_CHANNEL="${TELEGRAM_HOME_CHANNEL:-7044443781}"
TELEGRAM_HOME_CHANNEL_NAME="${TELEGRAM_HOME_CHANNEL_NAME:-Elias Lamseyah}"

# Gateway
GATEWAY_ALLOW_ALL_USERS="${GATEWAY_ALLOW_ALL_USERS:-false}"

# API Server config (cloud Hermes internal API)
API_SERVER_ENABLED=true
API_SERVER_PORT="${PORT:-8080}"
API_SERVER_HOST=0.0.0.0

# Railway service URLs
RAILWAY_SERVICE_API_SERVER_URL="${RAILWAY_SERVICE_API_SERVER_URL:-}"
RAILWAY_SERVICE_POSTGRES_DB_URL="${RAILWAY_SERVICE_POSTGRES_DB_URL:-}"

# Optional integrations (set via Railway env vars)
ELEVENLABS_API_KEY="${ELEVENLABS_API_KEY:-}"
CANVA_CLIENT_ID="${CANVA_CLIENT_ID:-}"
CANVA_CLIENT_SECRET="${CANVA_CLIENT_SECRET:-}"
TIKTOK_CLIENT_KEY="${TIKTOK_CLIENT_KEY:-}"
TIKTOK_CLIENT_SECRET="${TIKTOK_CLIENT_SECRET:-}"
LEMON_SQUEEZY_API_KEY="${LEMON_SQUEEZY_API_KEY:-}"
MAILCHIMP_API_KEY="${MAILCHIMP_API_KEY:-}"
VERCEL_TOKEN="${VERCEL_TOKEN:-}"
EOENV

echo "✓ .env generated ($(wc -l < "$HERMES_HOME/.env") lines)"

# Generate config.yaml from template
if [ -f "/app/config.template.yaml" ]; then
    # Substitute {{PORT}} with actual port
    PORT="${PORT:-8080}"
    sed "s/{{PORT}}/$PORT/g" /app/config.template.yaml > "$HERMES_HOME/config.yaml"
    echo "✓ config.yaml generated from template"
else
    echo "⚠ No config.template.yaml found, using default"
fi

# Check required env vars
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠ WARNING: DEEPSEEK_API_KEY not set. The agent won't be able to use DeepSeek models."
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠ WARNING: TELEGRAM_BOT_TOKEN not set. Telegram platform will be disabled."
fi

echo ""
echo "=== Starting Hermes Gateway ==="
echo "HERMES_HOME: $HERMES_HOME"
echo "PORT: $PORT"
echo ""

# Run hermes gateway
exec hermes gateway run --accept-hooks
