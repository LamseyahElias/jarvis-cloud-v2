#!/usr/bin/env python3
"""JARVIS Cloud — Telegram Bot (long-polling)."""

import os
import time
import json
import logging
from http import HTTPStatus

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("telegram-bot")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is required")

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
POLL_TIMEOUT = 60  # long polling seconds


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


def main():
    logger.info("JARVIS Cloud Telegram Bot starting...")
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
                    reply = "🤖 JARVIS Cloud is live. Message received."
                    if text.startswith("/start"):
                        reply = (
                            "🚀 *JARVIS Cloud is online!*\n\n"
                            "I'm the Telegram interface for your JARVIS AI agent system.\n"
                            "I relay messages to the command center.\n\n"
                            "Try sending any message — I'll echo it back.\n"
                            "Integration with the full agent suite coming soon!"
                        )
                    send_message(chat_id, reply)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
