# JARVIS Cloud — Agentic OS Monorepo

A 4-service monorepo for deploying **JARVIS** (Hermes AI agent) to Railway.

## Architecture

```
jarvis-cloud-v2/
├── api-server/          # FastAPI backend + Agentic OS dashboard (PORT)
│   ├── main.py          # All API routes — now supports PostgreSQL + SQLite
│   ├── Dockerfile       # Docker-based build for Railway
│   ├── Procfile         # Process runner
│   ├── railway.json     # Railway deployment config
│   ├── requirements.txt
│   └── static/
│       └── index.html   # React dashboard (pixel-art office)
├── telegram-bot/        # Telegram bot (TELEGRAM_TOKEN)
│   ├── bot.py
│   ├── requirements.txt
│   └── railway.json
├── belditalk-worker/    # Daily FB poster (FB_PAGE_TOKEN, cron 10AM)
│   ├── belditalk_post.py
│   ├── requirements.txt
│   └── railway.json
├── obsidian-vault/      # Git-synced knowledge base (empty stub)
│   └── README.md
├── .gitignore
└── README.md
```

## Services

- **api-server** — FastAPI + PostgreSQL/SQLite + React dashboard (Always on)
- **telegram-bot** — Telegram message relay (Always on)
- **belditalk-worker** — Facebook daily post (Daily 10 AM)
- **obsidian-vault** — Knowledge base stub (Manual sync)

## API Routes (api-server)

| Route              | Method | Description                |
|--------------------|--------|----------------------------|
| `/`                | GET    | Serves React dashboard     |
| `/api/health`      | GET    | System health check        |
| `/api/agents`      | GET    | List all agents            |
| `/api/agents/:id`  | GET    | Get single agent           |
| `/api/agents/:id`  | PATCH  | Update agent state         |
| `/api/tasks`       | GET    | List all tasks             |
| `/api/tasks`       | POST   | Create new task            |
| `/api/tasks/:id`   | PATCH  | Update task progress/status|
| `/api/tasks/:id`   | DELETE | Delete task                |
| `/api/logs`        | GET    | Get system logs            |
| `/api/goals`       | GET    | List strategic goals       |
| `/api/goals`       | POST   | Create new goal            |
| `/api/chat`        | POST   | Chat with Hermes           |

## Database

- **PostgreSQL** — used when `DATABASE_URL` env var is set (Railway PG service)
- **SQLite** — fallback when no `DATABASE_URL`, uses `DATA_DIR` (default: `/data/`)

## Deployment (Railway)

Each service deploys separately within the same Railway project:

```bash
railway login
cd api-server && railway up
cd ../telegram-bot && railway up
cd ../belditalk-worker && railway up
```

## Local Development

```bash
# API server (SQLite mode — no DATABASE_URL)
cd api-server
pip install -r requirements.txt
python main.py

# API server (PostgreSQL mode)
cd api-server
DATABASE_URL=postgresql://user:pass@host:5432/db python main.py

# Telegram bot
cd telegram-bot
TELEGRAM_TOKEN=xxx python bot.py

# BeldiTalk poster
cd belditalk-worker
FB_PAGE_TOKEN=xxx python belditalk_post.py
```

## Tech Stack

- **Backend**: Python 3.13, FastAPI, PostgreSQL / SQLite
- **Frontend**: React 18 (CDN), Babel standalone, Canvas 2D
- **Infra**: Railway (Docker build, health checks, cron)
