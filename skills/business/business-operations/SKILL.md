---
name: business-operations
description: "Business launch ops: API integrations, SaaS stack wiring, deployment, and launch checklists for Elias's businesses."
tags: [business, integrations, api, launch, deployment, belditalk, irm, pipeline]
---

# Business Operations

Use this skill when onboarding new API keys/services for a business, deploying websites, wiring up SaaS stacks, or preparing launch checklists.

## Trigger Conditions

- User provides API keys/tokens to store
- User asks to set up a new service integration
- User asks what's needed to launch a business/site
- User asks to deploy to Vercel/hosting
- User asks about payment, email, or social media setup
- User asks for a business pipeline check, status report, or audit across ventures
- Running as a cron job that needs to report on business health

## API Key Onboarding Workflow

1. **Store the key** in `~/.hermes/.env` with a clear comment block:
   ```
   # <Service Name> (<Purpose> - <Business>)
   SERVICE_API_KEY=<value>
   ```
2. **Verify the key works** immediately via API call — don't just store blindly:
   - Meta Graph API: `GET /me?access_token=TOKEN`
   - Meta Page: `GET /me/accounts?access_token=TOKEN` → returns page name, ID, tasks
   - Lemon Squeezy: `GET /v1/users/me` with `Authorization: Bearer TOKEN`
   - Mailchimp: `GET https://<dc>.api.mailchimp.com/3.0/` with basic auth `anystring:API_KEY` (dc = last part of key after `-`)
   - ElevenLabs: `GET /v1/user` with `xi-api-key` header
   - Canva/TikTok: OAuth flow needed, keys alone won't verify
3. **Update the vault registry** at `Business/API Keys & Integrations.md` — add service block with purpose, env var name, status, and use cases. Never put actual keys in the vault.
4. **Update memory** with service status (ready vs needs OAuth vs needs config)

## Business Pipeline Check

Use this when running periodic business health audits across Elias's ventures (IRM, BeldiTalk, Agency, Trading). Follow this data source discovery order.

### Data Source Locations (Elias's Obsidian Vault)

All business data lives in the Obsidian vault at `/mnt/c/Users/USER/Documents/Obsidian Vault/`. The vault has two organizational schemes — check both:

**Per-venture directories** (under `Business/{Venture Name}/`):
- `Pipeline.md` — leads, stages, outreach log, follow-up queue, pricing reference
- `Revenue.md` — closed deals, monthly actuals vs targets, payment tracking

**Agentic OS hub** (under `agentic-os/`):
- `GOALS.md` — all venture targets, progress checkboxes, monthly P&L targets, weekly review status
- `MEMORY/session.md` — current trading balance, active engine version, today's summary
- `Revenue.md` — aggregate revenue across all streams (trading, BeldiTalk, IRM, Agency)
- `Pipeline.md` — high-level lead counts per sector
- `Business/{Venture-Name}.md` — per-venture business status (e.g. `Business/IRM-Pipeline.md`)

### Standard Pipeline Check Workflow

1. **Read GOALS.md** — establish targets and milestone completion status for each venture
2. **Read MEMORY/session.md** — get current operational state (trading balance, engine version, session summary)
3. **Read each venture's Pipeline.md** — count active leads by stage, check outreach log, identify stale items in follow-up queue
4. **Read each venture's Revenue.md** — revenue this month vs target, verified closed deals
5. **Verify digital infrastructure** — curl website/domain URLs to confirm they return HTTP 200
6. **Synthesize report** — active leads (count + names), proposals out (count + targets), revenue this month (amount vs target), single most important action

### IRM-Specific Knowledge

- Business: Infinite Reflection Maroc — luxury infinity LED mirrors for Moroccan premium venues (hotels, nightclubs, riads, bars)
- SARL registration: NOT done (first step before banking)
- Prototype: NOT built (gating factor — 1m×1m, ~3,000 MAD materials, BOM ~2,434 MAD)
- Pricing: 25k–250k MAD per installation depending on scope (wall/ceiling/full room)
- Music-reactive upgrade: +15k–25k MAD upsell
- Annual maintenance: 5k–10k MAD per installation (recurring revenue)
- Website: `https://irm-site.vercel.app` (3 languages, product tiers, WhatsApp CTA)

### BeldiTalk-Specific Knowledge

- Business: Moroccan Darija language learning
- **New site** (Next.js 16, live): `/mnt/c/Users/USER/belditalk-site/` → deployed to `https://belditalk.vercel.app`
  - Navigation: Home, About, Course Preview, Pricing, Contact, Blog
  - Payment: Gumroad ($12 one-time, embedded buy-gate modal)
  - Stack: Next.js 16, Tailwind CSS v4, Framer Motion, Vercel
  - Nav links to `/course-preview` (not `/courses` — `/courses` redirects there)
  - Deploy: `cd /mnt/c/Users/USER/belditalk-site && npx vercel --token '$VERCEL_TOKEN' --prod`
- **Old site** (static HTML, deprecated): `/mnt/c/Users/USER/belditalk.com/`
  - Lemon Squeezy pricing (MAD 50 / 290 / 490), daily FB posting script
  - See `references/belditalk-stack.md` for full details
- **Daily FB poster now lives on Railway** (cloud, not local cron). Service: `belditalk-worker` in `jarvis-cloud` Railway project. Runs daily at 10 AM via Railway cronSchedule. Needs FB_PAGE_TOKEN set as Railway env var.
- Social: Instagram + Facebook pages connected (Meta API)
- Email: SendGrid verified (API key tested 200 OK)

### Report Format (cron pipeline checks)

When running as a cron job, output in this structure:

```
# {Venture Name} — Pipeline Report
**Date:** {date}

## Active Leads: {count}
{bulleted list of leads with stage and est. value}

## Proposals Out: {count}
{bulleted list of proposals sent and to whom}

## Revenue This Month: {amount}
{month vs target table}

## Most Important Action Today
{one clear action, step-by-step}
```

## Verification Endpoints Quick Reference

See `references/api-verification.md` for curl commands per service.
See `references/belditalk-stack.md` for Belditalk-specific services, scripts, deployment, pricing, and Meta posting workflow.
See `references/peace-corps-public-domain.md` for legal status of the Darija ebook source material.
See `references/mobile-responsiveness-audit.md` for systematic horizontal overflow / mobile layout fixes on Next.js sites.

## Launch Checklist (SaaS/Course Business)

Essential stack for an online business like Belditalk:

### Must-Have (blocks launch)
- [ ] Domain name purchased & DNS configured
- [ ] Hosting deployed (Vercel: `vercel login` → `vercel --prod`)
- [ ] SSL certificate (auto with Vercel/Netlify)
- [ ] Payment processor configured with products (Lemon Squeezy / Stripe)
- [ ] Landing page with value proposition + CTA

### Should-Have (launch week)
- [ ] Email capture (Mailchimp signup form embedded)
- [ ] Social media pages connected (Meta Graph API with publish permissions)
- [ ] Analytics (Vercel Analytics or Google Analytics)
- [ ] At least 3-5 content pieces live

### Nice-to-Have (month 1)
- [ ] Email drip campaign for new signups
- [ ] Social media auto-posting via API
- [ ] SEO basics (meta tags, sitemap, robots.txt)
- [ ] Community channel (Discord)

## Meta Business API Notes

- App Token format: `APP_ID|APP_SECRET` — used for app-level calls
- Page Token: long JWT-like string — used for page-level actions
- **Page token exchange (PROVEN):** User tokens stored in .env must be exchanged for page tokens before posting. Call `GET /v21.0/{PAGE_ID}?fields=access_token&access_token={USER_TOKEN}` to get the page token. Do NOT rely on `/me/accounts` — it may return empty `data` even when the token is valid.
- Page ID is NOT the user ID — get it from `/me/accounts` response or from the Facebook page About section
- Permissions must be requested via App Review for production:
  - `pages_manage_posts` — required for auto-posting
  - `instagram_basic` + `instagram_content_publish` — required for IG
  - `pages_read_engagement` — analytics
- Instagram must be linked to FB Page in IG app settings first
- **Token redaction in scripts:** Hermes redacts tokens from output. When using `execute_code`, write tokens to a temp file and read them back rather than passing through stdout.
- **Shell `&` trap:** URLs and data strings containing `&` (like `access_token=X&field=Y`) will be interpreted as shell backgrounding. Use Python `urllib.parse.urlencode()` or curl `-F` multipart flags instead.

### Token Renewal Flow (when expired)

FB page tokens expire ~60 days. When a `GET /v21.0/{PAGE_ID}?fields=access_token&access_token={TOKEN}` returns error code 190/subcode 463 ("Session has expired"), follow this workflow:

1. **Create an auth callback page** on the website to capture the new token. OAuth returns tokens in the URL hash fragment (#access_token=...):
   - Simple HTML page with JS that reads `window.location.hash` and displays the token
   - Deploy before generating the OAuth link
2. **Generate the OAuth URL:**
   ```
   https://www.facebook.com/v21.0/dialog/oauth
     ?client_id={APP_ID}
     &redirect_uri=https://yoursite.com/auth-callback
     &scope=pages_manage_posts,pages_read_engagement,pages_show_list
     &response_type=token
     &auth_type=rerequest
   ```
3. **User visits the URL**, authorizes, and is redirected to the callback page with the token in the URL
4. **User copies the full URL** (or token) and sends it to you
5. **Exchange user token for page token** if needed: `GET /v21.0/{PAGE_ID}?fields=access_token&access_token={NEW_USER_TOKEN}`
6. **Update `~/.hermes/.env`** with new token value
7. **Verify:** `GET /v21.0/{PAGE_ID}?fields=name,fan_count&access_token={NEW_TOKEN}`
8. **Resume social posting cron job**

**Pitfalls:**
- The callback page must exist and be deployed BEFORE the user clicks the OAuth link — the redirect URL must resolve
- For static sites on Vercel: add a `builds` entry for `*.html` glob so new .html files get deployed (not just `index.html`)
- The token appears in the URL hash — it's NOT sent to the server, so client-side JS is needed to capture it
- If the callback page 404s, the user can still copy the URL from the address bar (token is in the hash)
- **App ID extraction:** The META_APP_TOKEN in `.env` has format `APP_ID|APP_SECRET`. Parse with `app_token.split('|')[0]` to get the App ID for OAuth URLs — do NOT hardcode it
- **Vercel GitHub auto-deploy may be broken when the Vercel API token is expired.** If pushing to GitHub doesn't trigger a new deployment, the GitHub integration's auth token has expired. The user needs to re-login Vercel via browser or deploy with a fresh token manually.

## Vercel Deployment

- Install: `sudo npm install -g vercel`
- Login options:
  - Interactive: `vercel login` (needs browser)
  - Token: get from vercel.com/account/tokens, use `--token=<TOKEN>` flag
- Deploy: `cd /path/to/project && vercel deploy --prod --yes --token=<TOKEN>`
- Token deploy: pass `--token=` with `=` (not space) — `--token <val>` throws ARG_MISSING_REQUIRED_LONGARG
- Custom domain: `vercel domains add example.com`
- Env vars: `vercel env add SECRET_NAME`
- The `name` property in vercel.json is deprecated — Vercel warns but deploys fine

## Lemon Squeezy API Quirks

- **Products AND Variants APIs are READ-ONLY.** PATCH/POST to `/v1/products/{id}` or `/v1/variants/{id}` returns 405 Method Not Allowed. Products and prices MUST be managed in the dashboard at app.lemonsqueezy.com. Use GET to retrieve IDs afterward. Tell the user immediately when price changes are needed — don't waste time trying the API.
- **Discounts CAN be created via API.** POST `/v1/discounts` works. JSON:API format with store relationship.
- **Files API is also READ-ONLY.** POST to `/v1/files` returns 405. Digital product files (ebooks, PDFs) must be uploaded in the dashboard under each product. Inform the user immediately.
- **URL brackets must be percent-encoded.** `filter[store_id]` causes curl "bad range" error. Use `filter%5Bstore_id%5D=<id>` instead.
- **All requests need both headers:** `Accept: application/vnd.api+json` and `Authorization: Bearer <key>`.
- **Checkout overlay:** Add `<script src="https://assets.lemonsqueezy.com/lemon.js" defer></script>` and use `class="lemonsqueezy-button"` on buy links for in-page checkout.
- **Prices in API are in cents.** MAD 290.00 = 29000 in the API. MAD 49.00 = 4900.

## Mailchimp Integration Details

- **Signup form action URL format:** `https://gmail.<dc>.list-manage.com/subscribe/post?u=<uid>&id=<list_id>`

## Social Media Image Generation (Pillow)

When automated branded image generation is needed (daily posts, marketing graphics), use Python Pillow — NOT Canva API (requires interactive OAuth, impractical for headless automation).

**Working pipeline:**
1. Script: `~/.hermes/scripts/belditalk_image_gen.py`
2. Generates 1080x1080 branded PNGs with 6 templates (word, culture, lesson, phrase, promo, quiz)
3. Uses DejaVu Sans fonts (system-installed, supports Latin + Arabic)
4. CLI: `python3 belditalk_image_gen.py --type word --text "Zwin" --subtitle "Beautiful|zwee-n|Example" --output post.png`
5. Daily auto: `python3 belditalk_image_gen.py --generate-daily --output-dir ./posts/`
6. Samples: `python3 belditalk_image_gen.py --generate-samples --output-dir ./samples/`

**For better Arabic typography:** `apt install fonts-arabeyes` or download Google Fonts Cairo/Amiri.

## PDF Ebook Pipeline (ReportLab + PyPDF2)

To create branded ebooks from public domain content:
1. Generate cover/attribution pages with ReportLab (canvas API, programmatic PDF creation)
2. Merge with source PDF using PyPDF2 PdfWriter
3. Set metadata: `/Title`, `/Author`, `/Subject`, `/Creator`
4. Script: `~/belditalk-ebook/build_ebook.py`
5. Install: `pip install reportlab PyPDF2 pikepdf`

## Mailchimp Additional Details
- **Honeypot field** (required for bot prevention): `<input type="text" name="b_<uid>_<list_id>" tabindex="-1" value="" style="position:absolute;left:-5000px">`
- **Tags via API:** POST `/lists/{list_id}/segments` with `{name, static_segment: []}` to create tags.
- **AJAX submission:** Use `fetch()` to the form action URL to avoid page redirect. Show success/error inline.

## Pitfalls

1. **Always verify keys immediately.** A stored-but-broken key wastes future debugging time.
2. **Pipe character in .env values breaks `source`.** Tokens like `APP_ID|SECRET` must be quoted: `META_APP_TOKEN='123|abc'`. Otherwise bash interprets `|` as a pipe operator. Use `sed` to wrap in quotes if needed.
3. **Mailchimp datacenter matters.** The `-usXX` suffix on the API key determines the API subdomain. Wrong dc = 401.
4. **Meta Page Token vs User Token.** The token from `/me/accounts` is the real page token with page-scoped permissions. The initial user token may lack page permissions.
5. **Lemon Squeezy JWT expiry.** Check the `exp` claim — keys expire. Current key expires ~2027-01.
6. **npm global install on WSL needs sudo.** `npm install -g` without sudo fails with EACCES.
7. **Vault tracks WHAT, not secrets.** The Obsidian note records service name, env var, status, use cases. Actual keys stay in .env only.
8. **Lemon Squeezy product, price, AND file management is dashboard-only.** Products, variants, prices, and file uploads cannot be created or updated via API (405 on POST/PATCH). Inform the user immediately to make changes in the dashboard.
9. **Canva API requires OAuth2 authorization_code flow** — impractical for headless/automated use. Use Python Pillow instead for automated branded image generation (social media posts, banners). Script at `~/.hermes/scripts/belditalk_image_gen.py` generates 1080x1080 branded images with 6 templates (word, culture, lesson, phrase, promo, quiz).
10. **Claude Code `--max-turns 30` may not be enough for large HTML rebuilds.** A 3000-line single-file website rebuild hit the 30-turn limit. Use 40-50 for big rewrites, or split the prompt into sequential runs with `--continue`.
11. **Meta page "tasks" ≠ API permissions.** A page token from `/me/accounts` may show tasks like ADVERTISE, CREATE_CONTENT, MANAGE — but this does NOT mean the API-level permissions (like `pages_manage_posts`) are granted. Tasks are page-role permissions; API permissions must be requested separately in the Meta App Dashboard under App Review. Always check `/me/permissions` to verify actual API access before attempting to post.
12. **Vercel `--token` syntax.** Use `--token "$VERCEL_TOKEN"` (with quotes). The `--token=VALUE` form and `--token VALUE` both work, but if the env var is empty, `--token` alone throws "missing a value". Always `source ~/.hermes/.env` first to ensure the var is loaded.
13. **Vercel `--yes` flag for CI.** Include `--yes` to skip interactive project setup prompts. Without it, Vercel asks for project linking confirmation.
14. **Full business audit before launch.** When the user asks "can you handle this," do a systematic readiness check: website live + returning 200, checkout links returning 302 (redirect to checkout), e-book PDF exists and has correct page count, email list has subscribers, API permissions actually work (not just stored). Don't rely on stored status — verify live.
15. **GitHub as Vercel source.** When `vercel login` fails (expired token, no browser), push to GitHub and use `vercel --prod --yes --token` from a linked project. The `.vercel/project.json` file preserves the project link. Create the repo with `gh repo create` if it doesn't exist.
17. **Vercel static builds require explicit glob for new .html files.** When using `@vercel/static`, the `builds` config must match all HTML files, not just `index.html`. If you set `"src": "index.html"`, only that one file gets deployed — adding `auth-callback.html` or any other `.html` file produces a 404. Fix: use `"src": "*.html"` to catch all static HTML pages. If using a 404 handler, keep `index.html` as a specific match if it has special build settings, otherwise the glob covers everything.
18. **Business files live in Obsidian vault, not ~/.** Elias's business data (GOALS.md, Pipeline.md, Revenue.md, session.md) is in `/mnt/c/Users/USER/Documents/Obsidian Vault/` — not directly under `~/`. Always check there first when doing pipeline reports or status audits. The vault has two organizational schemes: per-venture dirs under `Business/{Name}/` and the agentic-os hub under `agentic-os/`.
