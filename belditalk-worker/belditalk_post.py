#!/usr/bin/env python3
"""BeldiTalk Daily Post — Posts to Facebook Page daily at 10 AM.

Reads FB_PAGE_TOKEN from environment variables.
Posts about BeldiTalk content (Moroccan cultural platform).
"""

import os
import sys
import json
import logging
import random
from datetime import datetime

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("belditalk-worker")

FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")
if not FB_PAGE_TOKEN:
    logger.error("FB_PAGE_TOKEN environment variable is required")
    sys.exit(1)

# Facebook Graph API endpoint for posting to a page
GRAPH_API = "https://graph.facebook.com/v18.0"

# BeldiTalk content templates — Moroccan culture / language / heritage
CONTENT_TEMPLATES = [
    # Darija lessons
    {
        "message": "🇲🇦 *Darija Word of the Day* 🇲🇦\n\n"
                   "📖 *\"Sbah el Kher\"* — صباح الخير\n"
                   "Meaning: Good morning 🌅\n"
                   "Usage: Used from dawn until noon.\n\n"
                   "Example:\n"
                   "A: Sbah el kher, kifash nti? 🌞\n"
                   "B: Sbah el noor, labas? 😊\n\n"
                   "👉 Learn more at belditalk.com\n"
                   "#Darija #Morocco #LearnArabic #BeldiTalk",
        "link": "https://belditalk.com/blog/darija-word-of-the-day",
    },
    {
        "message": "🇲🇦 *Moroccan Idiom of the Week* 🇲🇦\n\n"
                   "🗣️ *\"Hna Hna, Hna Hna\"* — هنا هنا، هنا هنا\n"
                   "Literal meaning: Here here, there there\n"
                   "Actual meaning: Taking things step by step, poco a poco.\n\n"
                   "Life lesson: Don't rush, everything in its time 🫶\n\n"
                   "#MoroccanIdioms #Darija #BeldiTalk #Morocco",
    },
    {
        "message": "🍽️ *Taste of Morocco — Recipe Highlight* 🍽️\n\n"
                   "Today's dish: *Couscous with Seven Vegetables* 🥕🥔🧅🌶️🍅\n\n"
                   "The Friday staple of every Moroccan household.\n"
                   "Steamed semolina topped with zucchini, carrots, turnips,\n"
                   "pumpkin, onions, chickpeas, and lamb or chicken.\n\n"
                   "Served with a spiced broth — *marqa* — infused with\n"
                   "saffron, ginger, turmeric, and ras el hanout.\n\n"
                   "👉 Full recipe: belditalk.com/recipes/couscous\n"
                   "#MoroccanFood #Couscous #BeldiTalk #Morocco #Recipe",
        "link": "https://belditalk.com/recipes/couscous",
    },
    {
        "message": "🎵 *Moroccan Music Discovery* 🎵\n\n"
                   "🎧 Artist: *Nass El Ghiwane*\n"
                   "Genre: التراث — Moroccan folk / chaabi\n\n"
                   "Known as \"The Rolling Stones of Africa,\" this legendary\n"
                   "group revolutionized Moroccan music in the 1970s with\n"
                   "poetic lyrics addressing social issues.\n\n"
                   "Must-listen tracks:\n"
                   "🔹 \"Ya Sahra\"\n"
                   "🔹 \"El Hamel\"\n"
                   "🔹 \"Mana Moumen Moulana\"\n\n"
                   "🎵 Listen at belditalk.com/music\n"
                   "#MoroccanMusic #NassElGhiwane #BeldiTalk #Morocco",
        "link": "https://belditalk.com/music/nass-el-ghiwane",
    },
    {
        "message": "🏛️ *Moroccan Heritage Spotlight* 🏛️\n\n"
                   "📍 *Medina of Fes* — فاس البالي\n\n"
                   "Founded in 789 AD, Fes el-Bali is the oldest of Fes's\n"
                   "medinas and a UNESCO World Heritage Site.\n\n"
                   "✨ Highlights:\n"
                   "• Al-Qarawiyyin Mosque & University (859 AD) — oldest\n"
                   "  continually operating university in the world 🎓\n"
                   "• Chouara Tannery — vibrant dye pits since the 11th C.\n"
                   "• 9,400+ narrow alleyways — only donkeys and foot traffic\n\n"
                   "🌐 Explore more: belditalk.com/heritage\n"
                   "#Fes #Morocco #UNESCO #BeldiTalk #Heritage",
        "link": "https://belditalk.com/heritage/fes-medina",
    },
    {
        "message": "💼 *BeldiTalk Community Update* 💼\n\n"
                   "📊 This week on BeldiTalk:\n\n"
                   "✅ New Darija lessons: Greetings & Introductions\n"
                   "✅ Moroccan recipe collection growing\n"
                   "✅ Community discussion: \"Saving amaziɣ language\"\n"
                   "✅ New video: Moroccan tea ceremony tutorial 🫖\n\n"
                   "Be part of the conversation! 🌐 belditalk.com\n\n"
                   "#BeldiTalk #Community #Morocco #Darija #Amazigh",
        "link": "https://belditalk.com",
    },
    {
        "message": "🫖 *Moroccan Tea — More Than a Drink* 🫖\n\n"
                   "Atay (الته) is the soul of Moroccan hospitality.\n\n"
                   "Did you know?\n"
                   "🍃 Moroccans consume ~2kg of tea per person annually\n"
                   "🍃 The pouring ritual — pour from height to create foam\n"
                   "🍃 Three glasses = life, love, death (proverb)\n"
                   "🍃 Always offered to guests, even in shops\n\n"
                   "\"The first glass is as gentle as life,\n"
                   " the second as strong as love,\n"
                   " and the third as bitter as death.\"\n\n"
                   "👉 belditalk.com/culture/moroccan-tea\n"
                   "#MoroccanTea #Atay #Culture #BeldiTalk #Morocco",
        "link": "https://belditalk.com/culture/moroccan-tea",
    },
    {
        "message": "🗣️ *Darija Phrase: How Was Your Day?* 🗣️\n\n"
                   "🔸 *\"Kifash daz nharek?\"* — كيفاش داز نهارك؟\n"
                   "🔹 Response: \"Daz bikhir, hamdullah\" — داز بيكير حمدالله\n\n"
                   "Breakdown:\n"
                   "• Kifash = How\n"
                   "• Daz = Passed\n"
                   "• Nhar = Day\n"
                   "• -ek = Your (masculine)\n\n"
                   "🇲🇦 Practice this with your Moroccan friends today!\n\n"
                   "#Darija #LearnWithBeldiTalk #Morocco #BeldiTalk",
    },
]


def post_to_facebook(message: str, link: str = None) -> dict:
    """Post a message to the Facebook page."""
    url = f"{GRAPH_API}/me/feed"
    params = {
        "access_token": FB_PAGE_TOKEN,
        "message": message,
        "published": True,
    }
    if link:
        params["link"] = link

    try:
        resp = requests.post(url, params=params, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        logger.info(f"Posted successfully: {result.get('id', 'unknown')}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Facebook API error: {e}")
        if hasattr(e, "response") and e.response:
            logger.error(f"Response: {e.response.text}")
        raise


def main():
    """Select a random template and post it."""
    logger.info("BeldiTalk Daily Post Worker starting...")

    # Pick random template
    template = random.choice(CONTENT_TEMPLATES)
    message = template["message"]
    link = template.get("link")

    today = datetime.now().strftime("%Y-%m-%d")
    header = f"📅 *BeldiTalk Daily — {today}*\n\n"
    full_message = header + message

    logger.info(f"Posting: {full_message[:80]}...")
    result = post_to_facebook(full_message, link)

    logger.info(f"✅ Daily post successful. Post ID: {result.get('id')}")
    return result


if __name__ == "__main__":
    main()
