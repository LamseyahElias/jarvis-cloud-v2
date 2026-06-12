---
name: railway-cloud-migration
description: JARVIS Hermes agent Railway deployment — full migration checklist from local WSL to Railway cloud
---

# Railway Cloud Migration — Playbook

## Architecture

```
┌─ RAILWAY (24/7) ──────────────────────────────────────┐
│                                                        │
│  api-server   → Dashboard, agent management, health    │
│  telegram-bot → Simple command bot (Phase 1 / backup)  │
│  hermes-agent → Full AI agent (Phase 2 — target)       │
│  belditalk-worker → Daily FB post cron                 │
│  postgres-db  → PostgreSQL database                    │
│                                                        │
│  Internal network: .railway.internal DNS               │
└────────────────────────────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────────────────┐
│  LOCAL (WSL)                                           │
│  MT5 Bridge (Windows) — trades stay local               │
│  Hermes gateway (will be deprecated)                    │
│  Local cron jobs (will migrate to Railway)              │
└────────────────────────────────────────────────────────┘
```

## Repos

- `LamseyahElias/jarvis-cloud-v2` — monorepo with all services
- Services use `rootDirectory` per service (e.g. `/hermes-agent`, `/telegram-bot`)

## Services & Config

### api-server (DEPLOYED ✅)
- **Type**: FastAPI + uvicorn
- **Build**: Dockerfile (DOCKERFILE builder)
- **Port**: 8080
- **URL**: https://api-server-production-9980.up.railway.app
- **Health**: `/api/health` — returns 8 agents, operational
- **Dashboard**: serves full Agentic OS HTML at `/`
- **DB**: PostgreSQL linked via `DATABASE_URL`
- **Env vars**: DEEPSEEK_API_KEY, DATABASE_URL

### telegram-bot (DEPLOYED ✅ — simple only)
- **Type**: Python long-poll bot (basic commands)
- **Build**: Dockerfile (DOCKERFILE builder)
- **URL**: https://telegram-bot-production-2ecc.up.railway.app
- **Health**: `/health` — returns `{"status": "ok"}`
- **Commands**: /start, /status, /help, /agents
- **No AI** — just a status bot.
- **Env vars**: TELEGRAM_BOT_TOKEN, ALLOWED_USERS

### hermes-agent (CREATED — needs first deploy)
- **Type**: Full Hermes AI agent
- **Build**: Dockerfile (DOCKERFILE builder)
- **Root directory**: `/hermes-agent`
- **Port**: Railway $PORT (dynamic)
- **Phase 1**: API-only (no Telegram)
- **Phase 2**: Enable Telegram after API tests pass
- **Entrypoint**: `entrypoint.sh` — generates `.env` from Railway env vars, starts gateway
- **Env vars needed**: DEEPSEEK_API_KEY, TELEGRAM_BOT_TOKEN (for later), TELEGRAM_HOME_CHANNEL

### belditalk-worker (DEPLOYED ✅)
- **Type**: Cron job (daily 10AM)
- **Build**: Dockerfile (DOCKERFILE builder)
- **Root directory**: `/belditalk-worker`
- **Cron**: `0 10 * * *`
- **Env vars**: FB_PAGE_TOKEN needed

### postgres-db (CREATED ✅)
- **Type**: Railway PostgreSQL add-on
- **Auto-linked** to api-server

## Deployment Command Reference

### Railway CLI (after `railway login`)
```bash
cd ~/jarvis-cloud-v2
# Check services
railway service list

# Deploy a specific service (triggers from GitHub)
railway service redeploy --service hermes-agent

# Get deployment logs
railway logs --service hermes-agent

# Set env vars
railway variables set KEY=VALUE --service hermes-agent

# Create domain
railway domain
```

### GitHub push (auto-deploys services)
```bash
cd ~/jarvis-cloud-v2
git add -A
git commit -m "message"
git push origin main
```

## Migration Steps (order matters)

### Step 1: Deploy hermes-agent (API-only) ⬅️ CURRENT
- [ ] Ensure Dockerfile, entrypoint.sh, config.template.yaml are in `hermes-agent/`
- [ ] Config has `telegram.enabled: false` (Phase 1)
- [ ] Set env vars: DEEPSEEK_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_HOME_CHANNEL
- [ ] Trigger deploy via Railway CLI: `railway service redeploy --service hermes-agent`
- [ ] Wait for BUILDING → SUCCESS

### Step 2: Test hermes-agent API
- [ ] Get domain: `railway domain` or check dashboard
- [ ] Test health endpoint: `curl https://<domain>/api/health`
- [ ] Test conversation via API: POST to Hermes API
- [ ] Test memory access
- [ ] Test database connection (PostgreSQL)
- [ ] Test agent status (8 agents)
- [ ] Verify skills loaded (84 builtin)
- [ ] Verify cron jobs functional

### Step 3: Enable Telegram (after tests pass)
- [ ] Edit config.template.yaml: set `telegram.enabled: true`
- [ ] Ensure `allowed_chats: "7044443781"`
- [ ] Push to GitHub → auto-deploy
- [ ] Wait for deploy → SUCCESS

### Step 4: Verify Telegram on cloud
- [ ] Send a message to @lamseyahbot via Telegram
- [ ] Verify cloud Hermes responds (not local)
- [ ] If both respond → fix: kill local gateway

### Step 5: Kill local gateway
- [ ] Kill local Hermes: `pkill -f "hermes gateway run"` or `kill <PID>`
- [ ] Remove @reboot cron: `crontab -e` → remove `@reboot ... hermes gateway run`
- [ ] Verify: `ps aux | grep hermes | grep gateway` → empty
- [ ] Verify: Telegram message → only cloud responds

### Step 6: Post-migration
- [ ] Update README.md in cloud repo with all URLs
- [ ] Add custom skills: `hermes skills install <name>` (post-deployment)
- [ ] Move local cron jobs to Railway workers:
  - Trading cron jobs → keep local (needs MT5)
  - BeldiTalk post → already on Railway ✅
  - Morning brief → migrate
  - Daily note → migrate
- [ ] Set up Obsidian vault git-sync for cloud read/write

## Safety Rules

1. **Never expose secrets** — token values never in chat
2. **Don't enable Telegram until API tests pass** — avoids token conflicts
3. **Don't kill local Hermes until cloud Telegram confirmed working**
4. **Ask user before switching Telegram control** — this is a breaking change
5. **All trading stays local** — MT5 needs Windows
6. **After Railway re-auth, use CLI (`railway ...`) not GraphQL API**

## Common Pitfalls

- **Token expiry**: Railway OAuth tokens expire hourly. Run `railway login` to refresh.
- **Empty config**: Hermes first run creates skeleton dirs. Skills populate via curator (168h interval). Run `hermes skills update` on first start.
- **Port conflict**: Both api-server (8080) and hermes-agent ($PORT) run separate API servers. They don't conflict on Railway.
- **Root directory**: Must match the subdirectory name EXACTLY (e.g., `/hermes-agent` not `/hermes-agent/`).
- **Docker caching**: If changes don't appear, Railway might use cached build. Trigger fresh deploy or set `RAILWAY_DEPLOY_NO_CACHE=true`.
- **Telegram token**: Same bot token used by both local AND cloud. Enabling cloud Telegram will cause conflicts until local is killed.

## Verification Checklist

```
□ api-server health:   curl https://api-server-production-9980.up.railway.app/api/health
□ Dashboard loads:     curl https://api-server-production-9980.up.railway.app/
□ Telegram bot health: curl https://telegram-bot-production-2ecc.up.railway.app/health
□ Hermes agent health: curl https://hermes-agent-production-XXXX.up.railway.app/health
□ PostgreSQL linked:   checked via api-server
□ BeldiTalk cron:      runs at 10AM daily
□ GitHub webhook:      pushes auto-deploy
```
