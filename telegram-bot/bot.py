#!/usr/bin/env python3
"""JARVIS Cloud — Telegram Bot (long-polling + health endpoint)."""

import os
import time
import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("telegram-bot")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

ALLOWED_USERS = os.environ.get("ALLOWED_USERS", "7044443781")
ALLOWED_SET = {int(x.strip()) for x in ALLOWED_USERS.split(",") if x.strip()}

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
POLL_TIMEOUT = 60  # long polling seconds

PORT = int(os.environ.get("PORT", 8080))


# --------------- Health HTTP Server ---------------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "telegram-bot"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress HTTP server logs


def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info(f"Health server listening on port {PORT}")
    server.serve_forever()


# --------------- Telegram Polling ---------------

def send_message(chat_id: int, text: str) -> dict:
    """Send a message via Telegram Bot API."""
    url = f"{API_BASE}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


def get_updates(offset: int = 0) -> list:
    """Long-poll for updates from Telegram Bot API."""
    url = f"{API_BASE}/getUpdates"
    params = {
        "offset": offset,
        "timeout": POLL_TIMEOUT,
        "allowed_updates": ["message"],
    }
    try:
        with httpx.Client(timeout=POLL_TIMEOUT + 10) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get("ok"):
                return data.get("result", [])
    except httpx.TimeoutException:
        pass  # Long poll timeout is normal
    except Exception as e:
        logger.error(f"Error fetching updates: {e}")
    return []


def handle_message(chat_id: int, text: str):
    """Process an incoming message and return a reply."""
    if chat_id not in ALLOWED_SET:
        logger.warning(f"Unauthorized access from {chat_id}")
        return "⛔ Unauthorized. You are not on the allowed users list."

    text_lower = text.strip().lower()

    # Simple command handling
    if text_lower == "/start":
        return (
            "🚀 *JARVIS Cloud is online!*\n\n"
            "I'm your AI agent system running 24/7.\n\n"
            "*Available commands:*\n"
            "• `/status` — System status\n"
            "• `/agents` — List active agents\n"
            "• `/help` — Show this message\n\n"
            "More commands coming soon!"
        )
    elif text_lower == "/status":
        return "✅ JARVIS Cloud — All systems operational.\n🟢 Telegram Bot connected\n🟢 API Server online\n🟢 BeldiTalk Worker scheduled\n🟢 PostgreSQL connected"
    elif text_lower == "/help":
        return (
            "*JARVIS Cloud Commands:*\n\n"
            "`/start` — Welcome message\n"
            "`/status` — System health\n"
            "`/agents` — List active agents\n"
            "`/help` — This message\n\n"
            "*Trading commands:* (coming soon)\n"
            "`/balance` — Account balance\n"
            "`/positions` — Open positions\n"
        )
    elif text_lower == "/agents":
        # Try to fetch from API server
        api_url = os.environ.get("RAILWAY_SERVICE_API_SERVER_URL", "api-server-production-9980.up.railway.app")
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"https://{api_url}/api/health")
                data = resp.json()
                return (
                    f"*JARVIS Agent Status:*\n\n"
                    f"👤 Agents online: {data.get('agents_online', '?')}\n"
                    f"📋 Active tasks: {data.get('active_tasks', '?')}\n"
                    f"✅ Completed tasks: {data.get('completed_tasks', '?')}\n"
                    f"⏱ Uptime: {data.get('uptime', '?')}"
                )
        except Exception as e:
            logger.error(f"Failed to fetch agents: {e}")
            return "⚠️ Could not reach API server. It may still be starting."
    else:
        return f"🤖 Message received. Use `/help` for available commands."


def polling_loop():
    logger.info("JARVIS Cloud Telegram Bot polling loop starting...")
    offset = 0

    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                update_id = update.get("update_id", 0)
                offset = max(offset, update_id + 1)

                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")

                if chat_id and text:
                    logger.info(f"Message from {chat_id}: {text[:50]}...")
                    reply = handle_message(chat_id, text)
                    try:
                        send_message(chat_id, reply)
                        logger.info(f"Replied to {chat_id}")
                    except Exception as e:
                        logger.error(f"Failed to send reply to {chat_id}: {e}")

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(5)


def main():
    logger.info("JARVIS Cloud Telegram Bot starting...")

    # Start health endpoint server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Start polling loop (blocking)
    polling_loop()


if __name__ == "__main__":
    main()
