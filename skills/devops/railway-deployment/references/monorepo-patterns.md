# JARVIS Cloud Monorepo Structure

Deployed to Railway project `jarvis-cloud` (ID: 9311ab1b).

## Services

```
jarvis-cloud-v2/
├── api-server/          # FastAPI + Agentic OS Dashboard (WEB)
│   ├── main.py          # Self-contained FastAPI app
│   ├── Dockerfile       # python:3.13-slim → uvicorn
│   ├── Procfile         # web: uvicorn main:app...
│   ├── requirements.txt # fastapi, uvicorn, psycopg2-binary, sqlalchemy
│   ├── railway.json     # DOCKERFILE builder, /api/health healthcheck
│   └── static/
│       └── index.html   # React dashboard
├── telegram-bot/        # Telegram long-poll worker (BACKGROUND)
│   ├── bot.py           # httpx-based Telegram polling + health HTTP server
│   ├── Dockerfile       # python:3.13-slim → python bot.py
│   ├── requirements.txt # httpx
│   ├── railway.json     # DOCKERFILE, ON_FAILURE restart
│   └── README.md
├── belditalk-worker/    # Daily FB poster (CRON @ 10AM)
│   ├── belditalk_post.py # 8 Moroccan culture templates
│   ├── Dockerfile
│   ├── requirements.txt # requests
│   └── railway.json     # cronSchedule: "0 10 * * *"
├── hermes-agent/        # Full Hermes AI agent (BACKGROUND)
│   ├── Dockerfile       # python:3.11-slim + pip install hermes-agent==0.14.0
│   ├── entrypoint.sh    # Generates .env + config.yaml from env vars
│   ├── config.template.yaml  # Uses {{PORT}} substitution
│   ├── railway.json     # DOCKERFILE builder
│   └── .gitignore
├── obsidian-vault/      # Git-sync target (README only)
├── .gitignore
└── README.md
```

## Key Design Decisions

1. **Dockerfile per service** — avoids Railpack monorepo detection issues. Each service builds from its own subdirectory via `rootDirectory`.
2. **`main.py` at root** (not in `app/`) — simplifies path handling. `Path(__file__).parent` resolves to `/app/`, not a subdirectory.
3. **PostgreSQL via Docker image** — `railway add --image postgres:16 --service postgres-db`.
4. **DATABASE_URL env var** — app checks this at startup. If set → PostgreSQL. If unset → SQLite fallback.
5. **rootDirectory on ServiceInstance** — The preferred approach for monorepos. Each service linked to the same repo must have `rootDirectory` set (e.g. `/telegram-bot`) on its ServiceInstance via the `serviceInstanceUpdate` mutation.
6. **API > CLI** — The Railway CLI is unreliable in WSL. Use the GraphQL API directly with the Bearer token from `~/.railway/config.json`.
7. **env var naming** — Must match exactly between code and Railway dashboard. Common mismatch: `TELEGRAM_TOKEN` in code vs `TELEGRAM_BOT_TOKEN` on Railway.
8. **Telegram bot architecture** — The cloud bot uses a threaded HTTP health server on `$PORT` alongside the long-polling Telegram loop. Health endpoint at `/health`.
9. **Cron worker pattern** — The belditalk-worker is a Docker container that runs once and exits. Railway's `cronSchedule` in railway.json handles restart at the scheduled interval.
10. **Service creation order matters** — (1) `serviceCreate` (name only), (2) `serviceConnect` (link GitHub repo + branch), (3) `serviceInstanceUpdate` (set rootDirectory), (4) `variableUpsert` for each env var, (5) push to GitHub or `serviceInstanceDeployV2` to trigger first deploy.
11. **Hermes agent uses entrypoint.sh** — The full Hermes agent generates its `config.yaml` and `.env` at startup from Railway env vars using an entrypoint script with config template. This avoids hardcoding secrets in the Docker image.

## URLs

- API Server: `https://api-server-production-9980.up.railway.app`
- Telegram Bot: `https://telegram-bot-production-2ecc.up.railway.app`
- BeldiTalk Worker: (cron, no public URL)
- Hermes Agent: (deployment pending — token expired during session)
