# BeldiTalk Stack Reference

## Live Sites

### Production (Next.js 16 — ACTIVE)
- **URL:** https://belditalk.vercel.app
- **Source:** `/mnt/c/Users/USER/belditalk-site/`
- **GitHub:** LamseyahElias/belditalk (private)
- **Stack:** Next.js 16, Tailwind CSS v4, Framer Motion
- **Deploy:** `cd /mnt/c/Users/USER/belditalk-site && npx vercel --token '$VERCEL_TOKEN' --prod --yes`
- **Status:** LIVE ✅

### Legacy (static HTML — deprecated)
- **URL:** https://belditalk.vercel.app (redirects to prod)
- **Source:** `/mnt/c/Users/USER/belditalk.com/`

## Daily Facebook Post (NOW ON RAILWAY)

The daily FB posting script has moved from local cron to Railway cloud:

- **Railway service:** `belditalk-worker` in `jarvis-cloud` project
- **Schedule:** 10:00 AM daily (cronSchedule: "0 10 * * *")
- **Script:** `~/jarvis-cloud-v2/belditalk-worker/belditalk_post.py`
- **Env var needed:** `FB_PAGE_TOKEN` (must be set via Railway CLI)
- **Status:** Deployed but inactive until FB_PAGE_TOKEN is provided

## Services & APIs

| Service | Status | Notes |
|---------|--------|-------|
| Gumroad | ✅ Active | $12 one-time, embedded buy-gate |
| Meta Graph API | ⚠️ Token expired | Needs re-auth |
| SendGrid | ✅ Verified | Email delivery |
| Mailchimp | ✅ Ready | us10 datacenter |
| Lemon Squeezy | ✅ Ready | MAD pricing configured |
| ElevenLabs TTS | ✅ Ready | Voice synthesis |
| Railway | ✅ Active | Jarvis-cloud project |

## Ebook Files

- **Source PDF:** `/mnt/c/Users/USER/Desktop/peace-corps-dariya/Peace Corps Moroccan Arabic Textbook.pdf`
- **Build script:** `~/belditalk-ebook/build_ebook.py`
- **Output:** Built with ReportLab cover + PyPDF2 merge
- **Licensing:** Public domain (Peace Corps publication, pre-1989)
